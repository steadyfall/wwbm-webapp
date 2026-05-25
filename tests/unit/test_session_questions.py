import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from game.models import Level, Lifeline, Option, Question, Session
from game.views import PAGINATE_NO, ScoreBoard


@pytest.fixture
def player():
    return User.objects.create_user(username="player", password="playerPass123")


@pytest.fixture
def easy_level():
    return Level.objects.create(level_number=1, money=100)


@pytest.fixture
def medium_level():
    return Level.objects.create(level_number=6, money=2000)


@pytest.fixture
def option():
    return Option.objects.create(text="Correct")


def create_question(text, difficulty, option, user):
    return Question.objects.create(
        who_added=user,
        text=text,
        difficulty=difficulty,
        correct_option=option,
    )


@pytest.mark.django_db
class TestSessionQuestionSelection:
    def test_get_next_question_returns_none_when_no_matching_difficulty_exists(
        self, player, easy_level, option
    ):
        session = Session.objects.create(
            session_user=player,
            current_level=easy_level,
        )
        create_question("Medium only?", Question.MEDIUM, option, player)

        assert Session.get_next_question(session.session_id) is None

    def test_get_next_question_returns_unasked_question_for_level_difficulty(
        self, player, easy_level, option
    ):
        session = Session.objects.create(
            session_user=player,
            current_level=easy_level,
        )
        asked = create_question("Already asked?", Question.EASY, option, player)
        available = create_question("Fresh question?", Question.EASY, option, player)
        asked.asked_to.add(player)

        assert Session.get_next_question(session.session_id) == available

    def test_get_next_question_excludes_question_seen_in_prior_session(
        self, player, easy_level, option
    ):
        prior_session = Session.objects.create(
            session_user=player,
            current_level=easy_level,
        )
        current_session = Session.objects.create(
            session_user=player,
            current_level=easy_level,
        )
        prior_question = create_question("Asked before?", Question.EASY, option, player)
        available = create_question("Still unseen?", Question.EASY, option, player)
        prior_session.questions_asked.add(prior_question)
        prior_question.asked_to.add(player)

        assert Session.get_next_question(current_session.session_id) == available

    def test_get_next_question_selects_a_random_offset_without_random_sort(
        self, player, easy_level, option, monkeypatch
    ):
        session = Session.objects.create(
            session_user=player,
            current_level=easy_level,
        )
        first = create_question("First?", Question.EASY, option, player)
        create_question("Second?", Question.EASY, option, player)
        offset_bounds = []

        def choose_first(bound):
            offset_bounds.append(bound)
            return 0

        monkeypatch.setattr("game.models.random.randrange", choose_first)

        with CaptureQueriesContext(connection) as queries:
            selected = Session.get_next_question(session.session_id)

        sql = " ".join(query["sql"].upper() for query in queries)
        assert selected == first
        assert offset_bounds == [2]
        assert "ORDER BY RAND" not in sql
        assert "RANDOM()" not in sql

    def test_set_question_returns_none_without_changing_current_question(
        self, player, medium_level
    ):
        session = Session.objects.create(
            session_user=player,
            current_level=medium_level,
        )
        original_question = session.current_question

        assert Session.set_question(session.session_id) is None

        session.refresh_from_db()
        assert session.current_question == original_question


@pytest.mark.django_db
class TestScoreBoardPerformance:
    def test_scoreboard_does_not_treat_matching_text_as_default_wrong_question(
        self, player, easy_level, option
    ):
        lookalike = create_question("None", Question.EASY, option, player)
        Session.objects.create(
            session_user=player,
            current_level=easy_level,
            wrong_qn=lookalike,
        )

        request = RequestFactory().get(reverse("scores"))
        request.user = player
        view = ScoreBoard()
        view.request = request

        result = list(view.context_creator()["allSessions"])[0]

        assert result[4] is False

    def test_scoreboard_context_stays_under_query_budget(
        self, player, easy_level, option
    ):
        lifeline = Lifeline.objects.create(name="Fifty fifty", description="Help")
        correct_question = create_question("Correct?", Question.EASY, option, player)
        for index in range(20):
            session = Session.objects.create(
                session_user=player,
                current_level=easy_level,
                score=index,
            )
            session.correct_qns.add(correct_question)
            session.used_lifelines.add(lifeline)

        request = RequestFactory().get(reverse("scores"))
        request.user = player
        view = ScoreBoard()
        view.request = request

        with CaptureQueriesContext(connection) as queries:
            context = view.context_creator()

        assert len(queries) <= 5
        assert len(context["allSessions"]) == PAGINATE_NO
