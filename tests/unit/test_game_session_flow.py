import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from game.lifelines import AUDIENCE_POLL, EXPERT_ANSWER, FIFTY50
from game.models import Level, Lifeline, Option, Question, Session


@pytest.fixture
def player():
    return get_user_model().objects.create_user(username="player", password="pass")


@pytest.fixture
def levels():
    Level.objects.filter(level_number__in=(-1, 0, 1)).delete()
    return {
        level_number: Level.objects.create(level_number=level_number, money=100)
        for level_number in (-1, 0, 1)
    }


@pytest.fixture
def lifelines():
    return {
        name: Lifeline.objects.create(name=name, description=f"{name} description")
        for name in (FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER)
    }


@pytest.fixture
def question():
    correct = Option.objects.create(text="Correct answer")
    incorrect_options = [
        Option.objects.create(text="Wrong answer 1"),
        Option.objects.create(text="Wrong answer 2"),
        Option.objects.create(text="Wrong answer 3"),
    ]
    qn = Question.objects.create(
        text="What is the answer?",
        correct_option=correct,
        difficulty=Question.EASY,
    )
    qn.incorrect_options.set(incorrect_options)
    return qn


@pytest.mark.django_db
def test_start_game_creates_uuid_session_and_redirects_to_rules(
    client, lifelines, levels, player
):
    client.force_login(player)

    response = client.post(reverse("mainpage"), {"startPlay": "yes"})

    assert response.status_code == 301
    session = Session.objects.get(session_user=player)
    assert isinstance(session.session_id, uuid.UUID)
    assert response.url == reverse("rules", kwargs={"session": session.session_id})
    assert set(session.left_lifelines.all()) == set(lifelines.values())


@pytest.mark.django_db
def test_question_lifeline_post_removes_lifeline_from_available_options(
    client, lifelines, levels, player, question
):
    session = Session.objects.create(
        session_user=player,
        agreed_to_rules=True,
        prev_level=levels[-1],
        current_level=levels[1],
        current_question=question,
    )
    session.left_lifelines.set(lifelines.values())
    client.force_login(player)

    response = client.post(
        reverse("question", kwargs={"session": session.session_id, "level": 1}),
        {
            "lifelineSubmit": "yes",
            "lifeline": FIFTY50,
            "timeLeftAfterLifeline": "10",
        },
    )

    session.refresh_from_db()
    assert response.status_code == 200
    assert lifelines[FIFTY50] not in session.left_lifelines.all()
    assert lifelines[FIFTY50] in session.used_lifelines.all()
