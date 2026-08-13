import uuid
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from game.lifelines import AUDIENCE_POLL, EXPERT_ANSWER, FIFTY50
from game.models import Level, Lifeline, Option, Question, Session


@pytest.fixture
def player():
    return get_user_model().objects.create_user(
        username="game-model-player",
        password="playerPass123",
    )


@pytest.fixture
def lifelines():
    return {
        name: Lifeline.objects.create(name=name, description=f"{name} description")
        for name in (FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER)
    }


def create_question(*, text, difficulty, player):
    correct_option = Option.objects.create(text=f"{text} correct")
    question = Question.objects.create(
        who_added=player,
        text=text,
        difficulty=difficulty,
        correct_option=correct_option,
    )
    question.incorrect_options.add(Option.objects.create(text=f"{text} incorrect"))
    return question


@pytest.mark.django_db
class TestSessionCreation:
    def test_new_sessions_receive_distinct_uuid_ids(self, player):
        first_session = Session.objects.create(session_user=player)
        second_session = Session.objects.create(session_user=player)

        assert isinstance(first_session.session_id, uuid.UUID)
        assert isinstance(second_session.session_id, uuid.UUID)
        assert first_session.session_id != second_session.session_id

    def test_starting_game_assigns_all_available_lifelines(
        self, client, player, lifelines
    ):
        client.force_login(player)

        response = client.post(reverse("mainpage"), {"startPlay": "yes"})

        session = Session.objects.get(session_user=player)
        assert response.status_code == 301
        assert set(session.left_lifelines.all()) == set(lifelines.values())


@pytest.mark.django_db
class TestSetQuestion:
    def test_sets_and_tracks_next_question(self, player):
        level = Level.objects.create(level_number=1, money=100)
        next_question = create_question(
            text="An easy question",
            difficulty=Question.EASY,
            player=player,
        )
        session = Session.objects.create(session_user=player, current_level=level)

        with patch.object(
            Session,
            "get_next_question",
            return_value=next_question,
        ) as get_next_question:
            selected = Session.set_question(session.session_id)

        session.refresh_from_db()
        assert selected == next_question
        assert session.current_question == next_question
        assert list(session.questions_asked.all()) == [next_question]
        assert list(player.questions_asked.all()) == [next_question]
        get_next_question.assert_called_once_with(session.session_id)
