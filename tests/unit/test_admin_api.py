import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token

from game.models import Category, Option, Question


@pytest.fixture
def api_user():
    return User.objects.create_user(username="apiuser", password="apiPass123")


@pytest.fixture
def auth_header(api_user):
    token = Token.objects.create(user=api_user)
    return {"HTTP_AUTHORIZATION": f"Token {token.key}"}


@pytest.fixture
def payload():
    return {
        "category": "Science",
        "difficulty": "Easy",
        "question": "What planet is known as the Red Planet?",
        "correct_answer": "Mars",
        "incorrect_answers": ["Venus", "Jupiter", "Mercury"],
    }


@pytest.fixture(autouse=True)
def default_category():
    Category.objects.get_or_create(name="None")


def _post(client, data, headers):
    return client.post(
        reverse("addQuestionAPI"),
        data=data,
        content_type="application/json",
        **headers,
    )


def _error_codes(response):
    errors = response.json()["errors"]
    if isinstance(errors, dict):
        return {errors["status_code"]}
    return {error["status_code"] for error in errors}


@pytest.mark.django_db
class TestAddQuestionAPI:
    def test_valid_single_question_creates_question_and_relationships(
        self, client, auth_header, api_user, payload
    ):
        science = Category.objects.create(name="Science")

        response = _post(client, [payload], auth_header)

        assert response.status_code == 201
        assert response.json()["success"] == 1

        question = Question.objects.get(text=payload["question"])
        assert question.who_added == api_user
        assert question.difficulty == Question.EASY
        assert question.correct_option.text == "Mars"
        assert list(question.falls_under.all()) == [science]
        assert {option.text for option in question.incorrect_options.all()} == {
            "Venus",
            "Jupiter",
            "Mercury",
        }

    def test_valid_multi_question_payload_creates_all_questions(
        self, client, auth_header, payload
    ):
        questions = [
            payload | {"question": f"Question {index}?", "correct_answer": f"A{index}"}
            for index in range(3)
        ]

        response = _post(client, questions, auth_header)

        assert response.status_code == 201
        assert Question.objects.count() == 3

    def test_non_list_payload_returns_400(self, client, auth_header, payload):
        response = _post(client, payload, auth_header)

        assert response.status_code == 400
        assert response.json()["success"] == 0
        assert response.json()["errors"]["status_code"] == 3

    def test_empty_list_returns_400(self, client, auth_header):
        response = _post(client, [], auth_header)

        assert response.status_code == 400
        assert response.json()["success"] == 0
        assert response.json()["errors"]["status_code"] == 3

    @pytest.mark.parametrize("missing_key", ["question", "difficulty"])
    def test_missing_required_parameter_returns_status_4(
        self, client, auth_header, payload, missing_key
    ):
        del payload[missing_key]

        response = _post(client, [payload], auth_header)

        assert response.status_code == 409
        assert _error_codes(response) == {4}
        assert Question.objects.count() == 0

    def test_non_dict_question_returns_status_3(self, client, auth_header):
        response = _post(client, ["not a dict"], auth_header)

        assert response.status_code == 409
        assert _error_codes(response) == {3}

    def test_incorrect_answers_must_have_three_values(
        self, client, auth_header, payload
    ):
        payload["incorrect_answers"] = ["Only one"]

        response = _post(client, [payload], auth_header)

        assert response.status_code == 409
        assert _error_codes(response) == {5}

    def test_duplicate_question_text_returns_status_5(
        self, client, auth_header, api_user, payload
    ):
        Question.objects.create(
            who_added=api_user,
            text=payload["question"],
            difficulty=Question.EASY,
            correct_option=Option.objects.create(text="Mars"),
        )

        response = _post(client, [payload], auth_header)

        assert response.status_code == 409
        assert _error_codes(response) == {5}

    def test_invalid_difficulty_returns_status_5(self, client, auth_header, payload):
        payload["difficulty"] = "Impossible"

        response = _post(client, [payload], auth_header)

        assert response.status_code == 409
        assert _error_codes(response) == {5}

    def test_invalid_option_returns_status_5(self, client, auth_header, payload):
        payload["correct_answer"] = {"text": "Mars"}

        response = _post(client, [payload], auth_header)

        assert response.status_code == 409
        assert _error_codes(response) == {5}

    def test_unknown_category_uses_default_none_category(
        self, client, auth_header, payload
    ):
        payload["category"] = "Unknown category"

        response = _post(client, [payload], auth_header)

        assert response.status_code == 201
        question = Question.objects.get(text=payload["question"])
        assert [category.name for category in question.falls_under.all()] == ["None"]

    def test_category_list_deduplicates_and_falls_back_to_default(
        self, client, auth_header, payload
    ):
        Category.objects.create(name="Science")
        payload["category"] = ["Science", "Science", "Missing category"]

        response = _post(client, [payload], auth_header)

        assert response.status_code == 201
        question = Question.objects.get(text=payload["question"])
        assert {category.name for category in question.falls_under.all()} == {
            "None",
            "Science",
        }

    def test_missing_authorization_token_returns_401(self, client, payload):
        response = _post(client, [payload], {})

        assert response.status_code == 401
        assert Question.objects.count() == 0


@pytest.fixture
def api_admin_user():
    return User.objects.create_superuser(
        username="apiadmin", email="apiadmin@example.com", password="adminPass123"
    )


@pytest.fixture
def api_admin_client(client, api_admin_user):
    client.force_login(api_admin_user)
    return client


@pytest.fixture
def api_questions(api_admin_user):
    questions = []
    for index in range(3):
        question = Question.objects.create(
            who_added=api_admin_user,
            text=f"Random question {index}?",
            difficulty=Question.EASY,
            correct_option=Option.objects.create(text=f"Answer {index}"),
        )
        question.incorrect_options.set(
            [
                Option.objects.create(text=f"Wrong {index} a"),
                Option.objects.create(text=f"Wrong {index} b"),
                Option.objects.create(text=f"Wrong {index} c"),
            ]
        )
        questions.append(question)
    return questions


@pytest.mark.django_db
class TestGetQuestionAPI:
    def test_count_param_returns_that_many_questions(
        self, api_admin_client, api_questions
    ):
        response = api_admin_client.get(reverse("getQuestionAPI") + "?count=3")

        assert response.status_code == 200
        assert len(response.json()["data"]) == 3

    def test_missing_count_defaults_to_one(self, api_admin_client, api_questions):
        response = api_admin_client.get(reverse("getQuestionAPI"))

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_non_numeric_count_defaults_to_one(self, api_admin_client, api_questions):
        response = api_admin_client.get(reverse("getQuestionAPI") + "?count=abc")

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_count_above_limit_returns_error(self, api_admin_client, api_questions):
        response = api_admin_client.get(reverse("getQuestionAPI") + "?count=10")

        assert response.status_code == 200
        assert response.json()["error"] == "Cannot request more than 5 objects."
