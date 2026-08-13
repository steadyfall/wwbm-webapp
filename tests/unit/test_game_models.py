import uuid
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from game.lifelines import AUDIENCE_POLL, EXPERT_ANSWER, FIFTY50
from game.models import (
    Level,
    Lifeline,
    Option,
    Question,
    Session,
    get_sentinel_user,
)


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


@pytest.mark.django_db
class TestGetNextQuestion:
    @pytest.mark.parametrize(
        ("level_number", "expected_difficulty"),
        [
            (1, Question.EASY),
            (5, Question.EASY),
            (6, Question.MEDIUM),
            (10, Question.MEDIUM),
            (11, Question.HARD),
            (15, Question.HARD),
        ],
    )
    def test_selects_question_for_level_difficulty(
        self, player, level_number, expected_difficulty
    ):
        level = Level.objects.create(level_number=level_number, money=100)
        expected_question = create_question(
            text=f"Question for level {level_number}",
            difficulty=expected_difficulty,
            player=player,
        )
        session = Session.objects.create(session_user=player, current_level=level)

        assert Session.get_next_question(session.session_id) == expected_question

    def test_excludes_questions_already_asked_to_player(self, player):
        level = Level.objects.create(level_number=1, money=100)
        asked_question = create_question(
            text="Already asked",
            difficulty=Question.EASY,
            player=player,
        )
        available_question = create_question(
            text="Still available",
            difficulty=Question.EASY,
            player=player,
        )
        asked_question.asked_to.add(player)
        session = Session.objects.create(session_user=player, current_level=level)

        assert Session.get_next_question(session.session_id) == available_question

    def test_returns_none_when_difficulty_has_no_available_questions(self, player):
        level = Level.objects.create(level_number=11, money=100)
        create_question(
            text="Easy only",
            difficulty=Question.EASY,
            player=player,
        )
        session = Session.objects.create(session_user=player, current_level=level)

        assert Session.get_next_question(session.session_id) is None

    def test_stays_within_two_query_budget(self, player, django_assert_max_num_queries):
        level = Level.objects.create(level_number=6, money=100)
        create_question(
            text="Medium question",
            difficulty=Question.MEDIUM,
            player=player,
        )
        session = Session.objects.create(session_user=player, current_level=level)

        with django_assert_max_num_queries(2):
            Session.get_next_question(session.session_id)


@pytest.mark.django_db
class TestDefaultFactories:
    def test_level_default_pk_creates_level_zero(self):
        default_pk = Level.get_default_pk()

        default_level = Level.objects.get(pk=default_pk)
        assert default_level.level_number == 0
        assert Level.get_default_pk() == default_pk

    def test_option_default_pk_creates_none_option(self):
        default_pk = Option.get_default_pk()

        default_option = Option.objects.get(pk=default_pk)
        assert default_option.text == "None"
        assert Option.get_default_pk() == default_pk

    def test_question_default_pk_creates_complete_none_question(self):
        default_pk = Question.get_default_pk()

        default_question = Question.objects.get(pk=default_pk)
        assert default_question.text == "None"
        assert default_question.correct_option.text == "None"
        assert list(default_question.incorrect_options.all()) == [
            default_question.correct_option
        ]
        assert Question.get_default_pk() == default_pk

    def test_sentinel_user_factory_creates_deleted_user(self):
        default_pk = get_sentinel_user()

        sentinel_user = get_user_model().objects.get(pk=default_pk)
        assert sentinel_user.username == "deleted"
        assert get_sentinel_user() == default_pk
