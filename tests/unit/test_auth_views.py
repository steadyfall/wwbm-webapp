import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse


REGISTER_URL = "/auth/register/"
ADMINLOGIN_URL = "/auth/admin-login/"
LOGIN_URL = "/auth/login/"


def _valid_post_data(**overrides):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securePass1",
        "password2": "securePass1",
    }
    data.update(overrides)
    return data


def _valid_admin_data(**overrides):
    data = {
        "username": "superuser",
        "password": "superPass1",
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


@pytest.mark.django_db
class TestAdminLoginView:
    def test_unauthenticated_get_renders_form(self, client):
        response = client.get(ADMINLOGIN_URL)
        assert response.status_code == 200
        assert "authentication/adminlogin.html" in [t.name for t in response.templates]

    def test_authenticated_superuser_get_redirects_to_admin(self, client):
        # Documents TRI-27: currently broken (missing return on line 85 of auth/views.py)
        user = User.objects.create_superuser(**_valid_admin_data())
        client.force_login(user)
        response = client.get(ADMINLOGIN_URL)
        assert response.status_code == 302
        assert response.url == reverse("adminMainPage")

    def test_authenticated_non_superuser_get_redirects_to_mainpage(self, client):
        user = User.objects.create_user(**_valid_admin_data(username="regularuser", password="userPass1"))
        client.force_login(user)
        response = client.get(ADMINLOGIN_URL)
        assert response.status_code == 302
        assert response.url == reverse("mainpage")

    def test_post_valid_superuser_credentials_redirects_to_admin(self, client):
        User.objects.create_superuser(**_valid_admin_data())
        response = client.post(ADMINLOGIN_URL, _valid_admin_data())
        assert response.status_code == 302
        assert response.url == reverse("adminMainPage")

    def test_post_valid_non_superuser_credentials_redirects_to_mainpage(self, client):
        User.objects.create_user(**_valid_admin_data(username="regularuser", password="userPass1"))
        response = client.post(ADMINLOGIN_URL, _valid_admin_data(username="regularuser", password="userPass1"))
        assert response.status_code == 302
        assert response.url == reverse("mainpage")

    def test_post_invalid_credentials_redirects_with_error(self, client):
        User.objects.create_user(**_valid_admin_data(username="regularuser", password="userPass1"))
        response = client.post(ADMINLOGIN_URL, _valid_admin_data(username="regularuser", password="wrongpass"))
        assert response.status_code == 302
        assert response.url == reverse("adminLogin")
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)


def _valid_login_data(**overrides):
    data = {
        "username": "testuser",
        "password": "securePass1",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestLoginView:
    def test_get_renders_login_template(self, client):
        response = client.get(LOGIN_URL)
        assert response.status_code == 200
        assert "authentication/signin.html" in [t.name for t in response.templates]

    def test_valid_credentials(self, client):
        data = _valid_login_data()
        User.objects.create_user(username=data["username"], password=data["password"])
        response = client.post(LOGIN_URL, data)
        assert response.status_code == 302
        assert response.url == reverse("mainpage")

    def test_nonexistent_username(self, client):
        response = client.post(LOGIN_URL, _valid_login_data())
        assert response.status_code == 302
        assert response.url == "/auth/register/"
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "warning" for m in msgs)

    def test_wrong_password(self, client):
        data = _valid_login_data()
        User.objects.create_user(username=data["username"], password=data["password"])
        response = client.post(LOGIN_URL, _valid_login_data(password="wrongPass1"))
        assert response.status_code == 302
        assert response.url == LOGIN_URL
        msgs = list(get_messages(response.wsgi_request))
        assert any("Wrong password" in str(m) for m in msgs)

    def test_invalid_username_format(self, client):
        response = client.post(LOGIN_URL, _valid_login_data(username="bad user!"))
        assert response.status_code == 302
        assert response.url == LOGIN_URL
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)

    def test_invalid_password_format(self, client):
        response = client.post(LOGIN_URL, _valid_login_data(password="short"))
        assert response.status_code == 302
        assert response.url == LOGIN_URL
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)

    def test_missing_field(self, client):
        data = _valid_login_data()
        del data["password"]
        response = client.post(LOGIN_URL, data)
        assert response.status_code == 302
        assert response.url == LOGIN_URL
        msgs = list(get_messages(response.wsgi_request))
        assert any(m.level_tag == "error" for m in msgs)

    def test_already_authenticated_get(self, client):
        data = _valid_login_data()
        user = User.objects.create_user(username=data["username"], password=data["password"])
        client.force_login(user)
        response = client.get(LOGIN_URL)
        assert response.status_code == 200
        assert "authentication/signin.html" in [t.name for t in response.templates]
