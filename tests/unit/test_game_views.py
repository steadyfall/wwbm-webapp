import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from game.models import Level, Option, Question, Session


@pytest.fixture
def player():
    return get_user_model().objects.create_user(
        username="game-view-player",
        password="playerPass123",
    )


@pytest.fixture
def levels():
    return {
        level_number: Level.objects.create(
            level_number=level_number,
            money=max(level_number, 0) * 100,
        )
        for level_number in (-1, 1, 2, 14, 15, 16)
    }


@pytest.fixture
def question(player):
    correct_option = Option.objects.create(text="The correct answer")
    incorrect_options = [
        Option.objects.create(text=f"Wrong answer {number}") for number in range(1, 4)
    ]
    question = Question.objects.create(
        who_added=player,
        text="Which answer is correct?",
        difficulty=Question.EASY,
        correct_option=correct_option,
    )
    question.incorrect_options.set(incorrect_options)
    return question


@pytest.fixture
def session_factory(player, levels, question):
    def create_session(*, level_number=1, previous_level=-1, score=0):
        return Session.objects.create(
            session_user=player,
            agreedToRules=True,
            prev_level=levels[previous_level],
            current_level=levels[level_number],
            current_question=question,
            score=score,
        )

    return create_session


def question_url(session, level_number):
    return reverse(
        "question",
        kwargs={"session": session.session_id, "level": level_number},
    )


@pytest.mark.django_db
class TestQuestionInGameAnswers:
    def test_correct_answer_increases_score_and_advances_level(
        self, client, player, levels, question, session_factory
    ):
        session = session_factory(score=500)
        client.force_login(player)

        response = client.post(
            question_url(session, 1),
            {"submitBtn": "yes", "userAnswer": question.correct_option.text},
        )

        session.refresh_from_db()
        assert response.status_code == 301
        assert response.url == question_url(session, 2)
        assert session.score == 500 + levels[1].money
        assert session.current_level == levels[2]
        assert list(session.correct_qns.all()) == [question]
        assert list(question.correct_option.hits.all()) == [player]

    def test_wrong_answer_ends_game_and_reduces_score(
        self, client, player, question, session_factory
    ):
        session = session_factory(score=10_000)
        client.force_login(player)

        response = client.post(
            question_url(session, 1),
            {
                "submitBtn": "yes",
                "userAnswer": question.incorrect_options.first().text,
            },
        )

        session.refresh_from_db()
        assert response.status_code == 301
        assert response.url == reverse(
            "statusAfterQn",
            kwargs={
                "session": session.session_id,
                "level": 1,
                "status": "incorrect",
            },
        )
        assert session.gameOver is True
        assert session.wrong_qn == question
        assert session.score == 100

    def test_exit_ends_game_and_redirects_to_quit_status(
        self, client, player, session_factory
    ):
        session = session_factory(score=500)
        client.force_login(player)

        response = client.post(question_url(session, 1), {"submitBtn": "exit"})

        session.refresh_from_db()
        assert response.status_code == 301
        assert response.url == reverse(
            "statusAfterQn",
            kwargs={
                "session": session.session_id,
                "level": 1,
                "status": "quit",
            },
        )
        assert session.gameOver is True
        assert session.score == 500

    def test_correct_answer_at_level_fifteen_finishes_game(
        self, client, player, levels, question, session_factory
    ):
        session = session_factory(level_number=15, previous_level=14, score=1_000)
        client.force_login(player)

        response = client.post(
            question_url(session, 15),
            {"submitBtn": "yes", "userAnswer": question.correct_option.text},
        )

        session.refresh_from_db()
        assert response.status_code == 301
        assert response.url == reverse(
            "statusAfterQn",
            kwargs={
                "session": session.session_id,
                "level": 15,
                "status": "correct",
            },
        )
        assert session.current_level == levels[16]
        assert session.gameOver is True

        finished_response = client.get(response.url)
        assert finished_response.status_code == 200
        assert finished_response.context["mode"] == "finished"

    @pytest.mark.parametrize(
        "invalid_answer", ["Tampered answer", "Other question answer"]
    )
    def test_invalid_answer_warns_without_changing_session(
        self, client, player, question, session_factory, invalid_answer
    ):
        if invalid_answer == "Other question answer":
            Option.objects.create(text=invalid_answer)
        session = session_factory(score=500)
        original_level = session.current_level
        client.force_login(player)

        response = client.post(
            question_url(session, 1),
            {"submitBtn": "yes", "userAnswer": invalid_answer},
        )

        session.refresh_from_db()
        message_texts = [
            str(message) for message in get_messages(response.wsgi_request)
        ]
        assert response.status_code == 302
        assert response.url == question_url(session, 1)
        assert message_texts == ["Invalid answer!"]
        assert session.score == 500
        assert session.current_level == original_level
        assert session.gameOver is False
        assert not Option.hits.through.objects.filter(user=player).exists()
