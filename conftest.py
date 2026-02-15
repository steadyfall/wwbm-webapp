import os

# Configure Django settings before pytest runs
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kbc.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")

# Initialize django-configurations
import configurations

configurations.setup()

import pytest
from django.conf import settings


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure database for testing."""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture
def api_client():
    """Return a DRF API client."""
    from rest_framework.test import APIClient

    return APIClient()
