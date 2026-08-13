import pytest
from django.contrib.auth import get_user_model
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


def create_game_session(player, levels, question, **overrides):
    values = {
        "session_user": player,
        "agreed_to_rules": True,
        "prev_level": levels[-1],
        "current_level": levels[1],
        "current_question": question,
    }
    values.update(overrides)
    return Session.objects.create(**values)


def assert_temporary_redirect(response, expected_url):
    assert response.status_code == 302
    assert response.url == expected_url


@pytest.mark.django_db
class TestGameFlowRedirects:
    def test_start_redirects_to_rules_temporarily(self, client, player):
        client.force_login(player)

        response = client.post(reverse("mainpage"), {"startPlay": "yes"})

        game_session = Session.objects.get(session_user=player)
        assert_temporary_redirect(
            response,
            reverse("rules", kwargs={"session": game_session.session_id}),
        )

    def test_rules_acceptance_redirects_to_question_temporarily(
        self, client, player, levels
    ):
        game_session = Session.objects.create(
            session_user=player,
            prev_level=levels[0],
            current_level=levels[0],
        )
        client.force_login(player)

        response = client.post(
            reverse("rules", kwargs={"session": game_session.session_id}),
            {"agreed": "yes"},
        )

        assert_temporary_redirect(
            response,
            reverse(
                "question", kwargs={"session": game_session.session_id, "level": 1}
            ),
        )

    def test_rules_rejection_redirects_to_main_page_temporarily(
        self, client, player, levels
    ):
        game_session = Session.objects.create(
            session_user=player,
            prev_level=levels[0],
            current_level=levels[0],
        )
        client.force_login(player)

        response = client.post(
            reverse("rules", kwargs={"session": game_session.session_id}),
            {"agreed": "no"},
        )

        assert_temporary_redirect(response, reverse("mainpage"))

    def test_correct_answer_redirects_to_next_question_temporarily(
        self, client, player, levels, question
    ):
        game_session = create_game_session(player, levels, question)
        client.force_login(player)

        response = client.post(
            reverse(
                "question", kwargs={"session": game_session.session_id, "level": 1}
            ),
            {"submitBtn": "yes", "userAnswer": question.correct_option.text},
        )

        assert_temporary_redirect(
            response,
            reverse(
                "question", kwargs={"session": game_session.session_id, "level": 2}
            ),
        )

    def test_incorrect_answer_redirects_to_status_temporarily(
        self, client, player, levels, question
    ):
        game_session = create_game_session(player, levels, question)
        client.force_login(player)

        response = client.post(
            reverse(
                "question", kwargs={"session": game_session.session_id, "level": 1}
            ),
            {
                "submitBtn": "yes",
                "userAnswer": question.incorrect_options.first().text,
            },
        )

        assert_temporary_redirect(
            response,
            reverse(
                "statusAfterQn",
                kwargs={
                    "session": game_session.session_id,
                    "level": 1,
                    "status": "incorrect",
                },
            ),
        )

    def test_invalid_question_state_redirects_to_main_page_temporarily(
        self, client, player, levels, question
    ):
        game_session = create_game_session(
            player, levels, question, agreed_to_rules=False
        )
        client.force_login(player)

        response = client.post(
            reverse(
                "question", kwargs={"session": game_session.session_id, "level": 1}
            ),
            {"submitBtn": "yes", "userAnswer": question.correct_option.text},
        )

        assert_temporary_redirect(response, reverse("mainpage"))

    def test_between_question_continue_redirects_to_question_temporarily(
        self, client, player, levels, question
    ):
        game_session = create_game_session(
            player,
            levels,
            question,
            current_level=levels[2],
            prev_level=levels[1],
        )
        client.force_login(player)
        status_url = reverse(
            "statusAfterQn",
            kwargs={
                "session": game_session.session_id,
                "level": 1,
                "status": "correct",
            },
        )

        response = client.post(status_url, {"nextQ": "yes"})

        assert_temporary_redirect(
            response,
            reverse(
                "question", kwargs={"session": game_session.session_id, "level": 2}
            ),
        )

    def test_between_question_quit_redirects_to_status_temporarily(
        self, client, player, levels, question
    ):
        game_session = create_game_session(
            player,
            levels,
            question,
            current_level=levels[2],
            prev_level=levels[1],
        )
        client.force_login(player)
        status_url = reverse(
            "statusAfterQn",
            kwargs={
                "session": game_session.session_id,
                "level": 1,
                "status": "correct",
            },
        )

        response = client.post(status_url, {"nextQ": "no"})

        assert_temporary_redirect(
            response,
            reverse(
                "statusAfterQn",
                kwargs={
                    "session": game_session.session_id,
                    "level": 1,
                    "status": "quit",
                },
            ),
        )

    def test_between_question_non_correct_status_redirects_to_main_page_temporarily(
        self, client, player, levels, question
    ):
        game_session = create_game_session(player, levels, question)
        client.force_login(player)

        response = client.post(
            reverse(
                "statusAfterQn",
                kwargs={
                    "session": game_session.session_id,
                    "level": 1,
                    "status": "incorrect",
                },
            ),
            {"nextQ": "yes"},
        )

        assert_temporary_redirect(response, reverse("mainpage"))
