import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from game.models import ChosenOption, Level, Option, Question, Session


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
    correct = Option.objects.create(text="Correct answer")
    incorrect_options = [
        Option.objects.create(text=f"Wrong answer {number}") for number in range(1, 4)
    ]
    question = Question.objects.create(
        text="What is the answer?",
        correct_option=correct,
        difficulty=Question.EASY,
    )
    question.incorrect_options.set(incorrect_options)
    return question


@pytest.fixture
def game_session(player, levels, question):
    return Session.objects.create(
        session_user=player,
        agreedToRules=True,
        prev_level=levels[-1],
        current_level=levels[1],
        current_question=question,
    )


def question_url(game_session):
    return reverse("question", kwargs={"session": game_session.session_id, "level": 1})


def assert_unchanged_session(game_session, question):
    game_session.refresh_from_db()
    assert game_session.score == 0
    assert game_session.current_level.level_number == 1
    assert game_session.gameOver is False
    assert game_session.wrong_qn_id == Question.get_default_pk()
    assert not game_session.correct_qns.exists()
    assert ChosenOption.objects.count() == 0
    assert question.asked_to.count() == 0


@pytest.mark.django_db
class TestQuestionAnswerValidation:
    def test_missing_answer_redirects_with_warning_without_writes(
        self, client, player, game_session, question
    ):
        client.force_login(player)

        response = client.post(question_url(game_session), {"submitBtn": "yes"})

        assert response.status_code == 302
        assert response.url == question_url(game_session)
        assert [str(message) for message in get_messages(response.wsgi_request)] == [
            "Choose an option!"
        ]
        assert_unchanged_session(game_session, question)

    def test_unknown_answer_redirects_with_warning_without_writes(
        self, client, player, game_session, question
    ):
        client.force_login(player)

        response = client.post(
            question_url(game_session),
            {"submitBtn": "yes", "userAnswer": "Tampered answer"},
        )

        assert response.status_code == 302
        assert response.url == question_url(game_session)
        assert [str(message) for message in get_messages(response.wsgi_request)] == [
            "Invalid answer!"
        ]
        assert_unchanged_session(game_session, question)

    def test_other_question_option_redirects_with_warning_without_writes(
        self, client, player, game_session, question
    ):
        other_correct = Option.objects.create(text="Other question answer")
        Question.objects.create(
            text="Another question",
            correct_option=other_correct,
            difficulty=Question.EASY,
        )
        client.force_login(player)

        response = client.post(
            question_url(game_session),
            {"submitBtn": "yes", "userAnswer": other_correct.text},
        )

        assert response.status_code == 302
        assert response.url == question_url(game_session)
        assert [str(message) for message in get_messages(response.wsgi_request)] == [
            "Invalid answer!"
        ]
        assert_unchanged_session(game_session, question)

    def test_correct_answer_updates_score_and_redirects_to_next_question(
        self, client, player, game_session, question
    ):
        client.force_login(player)

        response = client.post(
            question_url(game_session),
            {"submitBtn": "yes", "userAnswer": question.correct_option.text},
        )

        game_session.refresh_from_db()
        assert response.status_code == 301
        assert response.url == reverse(
            "question", kwargs={"session": game_session.session_id, "level": 2}
        )
        assert game_session.score == 100
        assert game_session.current_level.level_number == 2
        assert question in game_session.correct_qns.all()
        assert question.correct_option.hits.get() == player

    def test_incorrect_answer_ends_game_and_redirects_to_status(
        self, client, player, game_session, question
    ):
        incorrect_option = question.incorrect_options.first()
        client.force_login(player)

        response = client.post(
            question_url(game_session),
            {"submitBtn": "yes", "userAnswer": incorrect_option.text},
        )

        game_session.refresh_from_db()
        assert response.status_code == 301
        assert response.url == reverse(
            "statusAfterQn",
            kwargs={
                "session": game_session.session_id,
                "level": 1,
                "status": "incorrect",
            },
        )
        assert game_session.gameOver is True
        assert game_session.wrong_qn == question
        assert game_session.score == 0
        assert incorrect_option.hits.get() == player

    def test_duplicate_option_text_is_rejected_without_writes(
        self, client, player, game_session, question
    ):
        duplicate = Option.objects.create(text=question.correct_option.text)
        question.incorrect_options.add(duplicate)
        client.force_login(player)

        response = client.post(
            question_url(game_session),
            {"submitBtn": "yes", "userAnswer": question.correct_option.text},
        )

        assert response.status_code == 302
        assert response.url == question_url(game_session)
        assert_unchanged_session(game_session, question)
