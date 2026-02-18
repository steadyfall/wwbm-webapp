import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages


REGISTER_URL = "/auth/register/"


def _valid_post_data(**overrides):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securePass1",
        "password2": "securePass1",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestRegisterView:
    def test_get_renders_register_template(self, client):
        response = client.get(REGISTER_URL)
        assert response.status_code == 200
        assert "authentication/register.html" in [t.name for t in response.templates]

    def test_valid_registration(self, client):
        response = client.post(REGISTER_URL, _valid_post_data())
        assert response.status_code == 302
        assert response.url == "/auth/login/"
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "success" for m in msgs)

    def test_duplicate_username(self, client):
        User.objects.create_user(
            username="testuser", email="other@example.com", password="securePass1"
        )
        response = client.post(REGISTER_URL, _valid_post_data())
        assert response.status_code == 302
        assert response.url == "/auth/login/"
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "warning" for m in msgs)

    def test_invalid_email(self, client):
        response = client.post(REGISTER_URL, _valid_post_data(email="notanemail"))
        assert response.status_code == 302
        assert response.url == "/auth/register/"
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)

    def test_mismatched_passwords(self, client):
        response = client.post(REGISTER_URL, _valid_post_data(password2="differentPass1"))
        assert response.status_code == 302
        assert response.url == "/auth/register/"
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)

    def test_password_contains_username(self, client):
        response = client.post(
            REGISTER_URL,
            _valid_post_data(username="john", password="johnsmith1", password2="johnsmith1"),
        )
        assert response.status_code == 302
        assert response.url == "/auth/register/"
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)

    def test_missing_required_field(self, client):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securePass1",
        }
        response = client.post(REGISTER_URL, data)
        assert response.status_code == 302
        assert response.url == "/auth/register/"
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)
