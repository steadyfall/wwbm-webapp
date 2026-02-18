import pytest
from game.models import Lifeline


@pytest.mark.django_db
def test_db_write():
    """Smoke test: verify django_db_setup allows model creation."""
    obj = Lifeline.objects.create(name="Test", description="Smoke test lifeline")
    assert obj.pk is not None
