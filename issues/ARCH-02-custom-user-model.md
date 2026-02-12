# Create a Custom User Model

## Summary
The project uses Django's built-in `User` model with no `AUTH_USER_MODEL` override. Adding profile data, per-user game settings, or custom auth behaviour later will require a painful data migration that rewrites all FK references across the schema.

## Motivation
Django's own documentation warns: *"If you're starting a new project, set up a custom user model even if the default User model is sufficient."* Every `ForeignKey(get_user_model(), ...)` in `game/models.py` is a hard dependency on the default model. A retroactive migration with real data in place is expensive and error-prone.

## Scope
**Project:** Backend

- Create a minimal `AbstractUser` subclass (no new fields needed at this stage) in `auth/models.py`
- Set `AUTH_USER_MODEL = "auth.User"` (or whichever app name is chosen after ARCH-01) in `kbc/settings.py`
- Generate and apply the migration
- Update all `get_user_model()` imports to resolve to the new model
- Verify admin, DRF token auth, and login flows still work

## Acceptance Criteria
- `settings.AUTH_USER_MODEL` points to the custom model
- `python manage.py migrate` completes without error
- Login, registration, and admin login flows work
- `python manage.py check` reports no issues

## Tests
- Existing login and registration flows should continue to pass (once test coverage is added per TEST-01)

## Notes
Blocked by ARCH-01: the `auth` app must be registered before its model can be the auth user model.

Use `AbstractUser` (not `AbstractBaseUser`) — it keeps all existing fields and permissions and requires zero additional implementation. The migration will squash all existing references automatically.

Keep the class minimal for now:
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Meta:
        verbose_name = "user"
```
