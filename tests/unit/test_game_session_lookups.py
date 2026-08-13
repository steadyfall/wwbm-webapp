import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from game.models import Level, Option, Question, Session


@pytest.fixture
def player():
    return get_user_model().objects.create_user(username="player", password="pass")


@pytest.fixture
def levels():
    return {
        number: Level.objects.create(level_number=number, money=number * 100)
        for number in (-1, 0, 1, 2)
    }


@pytest.fixture
def question():
    correct = Option.objects.create(text="Correct")
    incorrect_options = [
        Option.objects.create(text=f"Incorrect {number}") for number in range(1, 4)
    ]
    question = Question.objects.create(
        text="What is the answer?",
        correct_option=correct,
        difficulty=Question.EASY,
    )
    question.incorrect_options.set(incorrect_options)
    return question


def session_retrieval_count(queries):
    return sum(
        query["sql"].upper().startswith("SELECT")
        and 'FROM "GAME_SESSION"' in query["sql"].upper()
        for query in queries
    )


@pytest.mark.django_db
class TestGameSessionLookups:
    def test_rules_post_retrieves_session_once(self, client, player, levels):
        game_session = Session.objects.create(
            session_user=player,
            prev_level=levels[0],
            current_level=levels[0],
        )
        client.force_login(player)

        with CaptureQueriesContext(connection) as queries:
            response = client.post(
                reverse("rules", kwargs={"session": game_session.session_id}),
                {"agreed": "no"},
            )

        assert response.status_code == 302
        assert session_retrieval_count(queries) == 1

    def test_question_post_retrieves_session_once(
        self, client, player, levels, question
    ):
        game_session = Session.objects.create(
            session_user=player,
            agreed_to_rules=True,
            prev_level=levels[-1],
            current_level=levels[1],
            current_question=question,
        )
        client.force_login(player)

        with CaptureQueriesContext(connection) as queries:
            response = client.post(
                reverse(
                    "question",
                    kwargs={"session": game_session.session_id, "level": 1},
                ),
                {"submitBtn": "unexpected"},
            )

        assert response.status_code == 302
        assert session_retrieval_count(queries) == 1

    def test_between_question_post_retrieves_session_once(
        self, client, player, levels, question
    ):
        game_session = Session.objects.create(
            session_user=player,
            agreed_to_rules=True,
            prev_level=levels[1],
            current_level=levels[2],
            current_question=question,
        )
        client.force_login(player)

        with CaptureQueriesContext(connection) as queries:
            response = client.post(
                reverse(
                    "statusAfterQn",
                    kwargs={
                        "session": game_session.session_id,
                        "level": 1,
                        "status": "correct",
                    },
                ),
                {"nextQ": "yes"},
            )

        assert response.status_code == 302
        assert session_retrieval_count(queries) == 1
