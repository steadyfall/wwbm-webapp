import uuid

import pytest
from django.contrib.auth import get_user_model

from game.models import Session


@pytest.mark.django_db
def test_session_create_generates_uuid_primary_key():
    user = get_user_model().objects.create_user(username="player", password="pass")

    game_session = Session.objects.create(session_user=user)

    assert isinstance(game_session.session_id, uuid.UUID)


def test_session_model_does_not_expose_non_atomic_id_generator():
    assert not hasattr(Session, "get_unused_sessionId")


@pytest.mark.django_db
def test_session_state_fields_use_snake_case():
    user = get_user_model().objects.create_user(username="player", password="pass")
    game_session = Session.objects.create(
        session_user=user,
        agreed_to_rules=True,
        game_over=False,
    )

    assert Session._meta.get_field("agreed_to_rules").value_from_object(game_session)
    assert Session.objects.filter(agreed_to_rules=True).get() == game_session
