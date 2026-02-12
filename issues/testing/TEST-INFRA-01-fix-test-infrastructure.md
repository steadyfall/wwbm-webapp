# Fix Test Infrastructure — conftest.py DB Setup

## Summary
The `django_db_setup` fixture in `conftest.py` uses the wrong signature and scope for overriding the test database. This can cause test isolation failures and is not the pytest-django recommended pattern.

## Motivation
```python
# conftest.py:16 — incorrect pattern
@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
```

pytest-django's `django_db_setup` fixture requires specific parameters (`django_test_environment`, `django_db_blocker`) to properly manage the test database lifecycle. The current override mutates `settings` directly, which may not take effect correctly for all test ordering and can leak state between test sessions.

## Scope
**Project:** Backend (Testing Infrastructure)

- Update `conftest.py` to use the correct pytest-django `django_db_setup` override pattern:
  ```python
  @pytest.fixture(scope="session")
  def django_db_setup(django_test_environment, django_db_blocker):
      with django_db_blocker.unblock():
          # in-memory SQLite is already default via settings
          pass
  ```
- Alternatively, simply configure the test database in `kbc/settings.py` `Dev` class directly (pytest-django will use it):
  ```python
  # In pytest.ini or conftest.py:
  # DJANGO_SETTINGS_MODULE=kbc.settings
  # DJANGO_CONFIGURATION=Dev
  # Dev class already uses sqlite3
  ```
- Add a `pytest.ini` or `pyproject.toml` `[tool.pytest.ini_options]` section with `DJANGO_SETTINGS_MODULE` and `DJANGO_CONFIGURATION` so the `conftest.py` `os.environ.setdefault` calls are not needed
- Verify `pytest --co` (collect only) runs without error

## Acceptance Criteria
- `pytest --co` shows collectible test items without errors
- Writing a trivial `@pytest.mark.django_db` test that creates a model instance passes
- No `settings` mutations in `conftest.py` at fixture call time

## Tests
- Smoke test: `pytest tests/` with at least one real `@pytest.mark.django_db` test passes
