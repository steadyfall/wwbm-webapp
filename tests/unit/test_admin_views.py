import pytest
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import User
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from adminpanel.views import AdminMainPage
from game.models import Category, Lifeline, Option, Question, Session


@pytest.fixture
def superuser():
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminPass123"
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(username="player", password="playerPass123")


@pytest.fixture(autouse=True)
def admin_data(superuser):
    category = Category.objects.create(name="General")
    none_category = Category.objects.get_or_create(name="None")[0]
    correct = Option.objects.create(text="Correct")
    wrong_options = [
        Option.objects.create(text="Wrong 1"),
        Option.objects.create(text="Wrong 2"),
        Option.objects.create(text="Wrong 3"),
    ]
    question = Question.objects.create(
        who_added=superuser,
        text="Existing question?",
        difficulty=Question.EASY,
        correct_option=correct,
    )
    question.falls_under.set([category, none_category])
    question.incorrect_options.set(wrong_options)
    Lifeline.objects.create(name="Ask an expert", description="Expert help")
    Session.objects.create(session_id="ADMIN001", session_user=superuser, score=100)
    return {
        "category": category,
        "correct": correct,
        "wrong_options": wrong_options,
        "question": question,
    }


@pytest.fixture
def admin_client(client, superuser):
    client.force_login(superuser)
    return client


def _admin_urls(admin_data):
    category = admin_data["category"]
    question = admin_data["question"]
    return [
        reverse("adminMainPage"),
        reverse("adminListDB", kwargs={"db": "session"}),
        reverse("adminListDB", kwargs={"db": "lifeline"}),
        reverse("adminListDB", kwargs={"db": "category"}),
        reverse("adminListDB", kwargs={"db": "question"}),
        reverse("adminListDB", kwargs={"db": "option"}),
        reverse("adminDBObjectCreate", kwargs={"db": "category"}),
        reverse("adminDBObject", kwargs={"db": "category", "pk": category.pk}),
        reverse("adminDBObjectDelete", kwargs={"db": "category", "pk": category.pk}),
        reverse("adminDBObjectHistory", kwargs={"db": "question", "pk": question.pk}),
        reverse("adminListLogs"),
        reverse("APIAccess"),
        reverse("APIDocs"),
        reverse("getQuestionAPI") + "?count=1",
    ]


@pytest.mark.django_db
class TestAdminAccessControl:
    @pytest.mark.parametrize("url_index", range(14))
    def test_unauthenticated_requests_redirect_to_admin_login(
        self, client, admin_data, url_index
    ):
        url = _admin_urls(admin_data)[url_index]

        response = client.get(url)

        assert response.status_code == 302
        assert response.url.startswith(reverse("adminLogin"))

    @pytest.mark.parametrize("url_index", range(14))
    def test_non_superuser_requests_return_403(
        self, client, regular_user, admin_data, url_index
    ):
        client.force_login(regular_user)
        url = _admin_urls(admin_data)[url_index]

        response = client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("url_index", range(14))
    def test_superuser_requests_return_success_or_expected_redirect(
        self, admin_client, admin_data, url_index
    ):
        url = _admin_urls(admin_data)[url_index]

        response = admin_client.get(url)

        assert response.status_code in {200, 302}


@pytest.mark.django_db
class TestAdminDashboardPerformance:
    def test_dashboard_context_stays_under_query_budget(self, admin_data):
        view = AdminMainPage()
        view.request = RequestFactory().get(reverse("adminMainPage"))
        view.kwargs = {}

        with CaptureQueriesContext(connection) as queries:
            context = view.context_creater()

        assert len(queries) <= 20
        assert context["total_question_count"] >= 1
        assert context["category_with_most_qs"]


@pytest.mark.django_db
class TestAdminCRUDViews:
    @pytest.mark.parametrize(
        ("model_name", "expected_text"),
        [
            ("session", "ADMIN001"),
            ("lifeline", "Ask an expert"),
            ("category", "General"),
            ("question", "Existing question?"),
            ("option", "Correct"),
        ],
    )
    def test_admin_list_db_shows_records(self, admin_client, model_name, expected_text):
        response = admin_client.get(reverse("adminListDB", kwargs={"db": model_name}))

        assert response.status_code == 200
        assert expected_text in response.content.decode()

    def test_create_category_adds_object_and_log_entry(self, admin_client, superuser):
        response = admin_client.post(
            reverse("adminDBObjectCreate", kwargs={"db": "category"}),
            {
                "name": "History",
                "date_created": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "create": "Create",
            },
        )

        category = Category.objects.get(name="History")
        assert response.status_code == 302
        assert response.url == reverse(
            "adminDBObject", kwargs={"db": "category", "pk": category.pk}
        )
        log = LogEntry.objects.get(object_id=str(category.pk), action_flag=ADDITION)
        assert log.user == superuser
        assert log.object_repr == str(category)

    def test_change_category_updates_object_and_log_entry(
        self, admin_client, admin_data, superuser
    ):
        category = admin_data["category"]

        response = admin_client.post(
            reverse("adminDBObject", kwargs={"db": "category", "pk": category.pk}),
            {
                "name": "Updated General",
                "date_created": category.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                "save_continue": "Save and continue",
            },
        )

        category.refresh_from_db()
        assert response.status_code == 302
        assert response.url == reverse(
            "adminDBObject", kwargs={"db": "category", "pk": category.pk}
        )
        assert category.name == "Updated General"
        log = LogEntry.objects.get(object_id=str(category.pk), action_flag=CHANGE)
        assert log.user == superuser

    def test_delete_category_yes_deletes_object_and_adds_log_entry(
        self, admin_client, superuser
    ):
        category = Category.objects.create(name="Temporary")

        response = admin_client.post(
            reverse(
                "adminDBObjectDelete", kwargs={"db": "category", "pk": category.pk}
            ),
            {"yes": "Yes"},
        )

        assert response.status_code == 302
        assert response.url == reverse("adminListDB", kwargs={"db": "category"})
        assert not Category.objects.filter(pk=category.pk).exists()
        log = LogEntry.objects.get(object_id=str(category.pk), action_flag=DELETION)
        assert log.user == superuser
        assert log.object_repr == "Temporary"

    def test_delete_category_no_keeps_object_and_redirects_to_list(self, admin_client):
        category = Category.objects.create(name="Keep me")

        response = admin_client.post(
            reverse(
                "adminDBObjectDelete", kwargs={"db": "category", "pk": category.pk}
            ),
            {"no": "No"},
        )

        assert response.status_code == 302
        assert response.url == reverse("adminListDB", kwargs={"db": "category"})
        assert Category.objects.filter(pk=category.pk).exists()
        assert not LogEntry.objects.filter(
            object_id=str(category.pk), action_flag=DELETION
        ).exists()
