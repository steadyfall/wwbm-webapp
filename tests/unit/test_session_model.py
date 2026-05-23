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
