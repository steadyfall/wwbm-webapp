from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth"
    label = "trivivo_auth"  # avoids collision with django.contrib.auth's label
