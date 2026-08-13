import re

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from game.lifelines import (
    AUDIENCE_POLL,
    EXPERT_ANSWER,
    FIFTY50,
    audiencePoll,
    expertAnswer,
    fifty50,
    general_procedure,
    get_lifeline_map,
)
from game.models import Level, Lifeline, Option, Question, Session


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


@pytest.fixture
def session(lifelines):
    user = get_user_model().objects.create_user(username="player", password="pass")
    game_session = Session.objects.create(session_user=user)
    game_session.left_lifelines.set(lifelines.values())
    return game_session


@pytest.mark.django_db
def test_get_lifeline_map_uses_database_primary_keys(lifelines):
    decoy = Lifeline.objects.create(name="Decoy", description="Not a real lifeline")

    mapped = get_lifeline_map()

    assert mapped == {
        FIFTY50: lifelines[FIFTY50].pk,
        AUDIENCE_POLL: lifelines[AUDIENCE_POLL].pk,
        EXPERT_ANSWER: lifelines[EXPERT_ANSWER].pk,
    }
    assert decoy.pk not in mapped.values()


@pytest.mark.django_db
def test_general_procedure_moves_lifeline_and_tracks_question(
    lifelines, question, session
):
    general_procedure(lifelines[FIFTY50].pk, question.pk, session.session_id)

    session.refresh_from_db()
    assert question in session.lifeline_qns.all()
    assert lifelines[FIFTY50] not in session.left_lifelines.all()
    assert lifelines[FIFTY50] in session.used_lifelines.all()


@pytest.mark.django_db
def test_expert_answer_returns_correct_option_and_uses_lifeline(
    lifelines, question, session
):
    answer = expertAnswer(question.pk, session.session_id)

    assert answer == "The expert says that the answer would be <b>Correct answer</b>."
    assert lifelines[EXPERT_ANSWER] in session.used_lifelines.all()
    assert lifelines[EXPERT_ANSWER] not in session.left_lifelines.all()


@pytest.mark.django_db
def test_fifty50_returns_two_options_with_correct_answer(lifelines, question, session):
    options = fifty50(question.pk, session.session_id)

    assert len(options) == 2
    assert "Correct answer" in options
    assert len(set(options)) == 2
    assert lifelines[FIFTY50] in session.used_lifelines.all()
    assert lifelines[FIFTY50] not in session.left_lifelines.all()


@pytest.mark.django_db
def test_audience_poll_returns_all_options_with_percentages(
    lifelines, question, session
):
    poll = audiencePoll(question.pk, session.session_id)

    assert poll
    for option in [
        "Correct answer",
        "Wrong answer 1",
        "Wrong answer 2",
        "Wrong answer 3",
    ]:
        assert option in poll

    percentages = [int(match) for match in re.findall(r"<i>(\d+)</i>%", poll)]
    assert len(percentages) == 4
    assert all(1 <= percent <= 100 for percent in percentages)
    assert lifelines[AUDIENCE_POLL] in session.used_lifelines.all()
    assert lifelines[AUDIENCE_POLL] not in session.left_lifelines.all()


@pytest.mark.django_db
def test_using_all_lifelines_hides_lifeline_button(
    client, lifelines, question, session
):
    level = Level.objects.create(level_number=1, money=100)
    session.agreedToRules = True
    session.current_level = level
    session.prev_level = level
    session.current_question = question
    session.save(
        update_fields=[
            "agreedToRules",
            "current_level",
            "prev_level",
            "current_question",
        ]
    )

    fifty50(question.pk, session.session_id)
    audiencePoll(question.pk, session.session_id)
    expertAnswer(question.pk, session.session_id)
    client.force_login(session.session_user)

    response = client.get(
        reverse(
            "question",
            kwargs={"session": session.session_id, "level": level.level_number},
        )
    )

    session.refresh_from_db()
    assert response.status_code == 200
    assert not session.left_lifelines.exists()
    assert set(session.used_lifelines.all()) == set(lifelines.values())
    assert b'id="lifelineButton"' not in response.content
