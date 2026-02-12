# Register `auth` and `adminpanel` in INSTALLED_APPS

## Summary
`auth` and `adminpanel` are both functional Django apps but neither is listed in `INSTALLED_APPS`. Django's migration runner, signal dispatch, and management command autodiscovery all depend on app registration.

## Motivation
Running `manage.py migrate` silently skips any future migrations added to these apps. If either app ever defines its own model or signal, it will not be detected. This is a latent correctness bug that grows more dangerous as the codebase evolves.

## Scope
**Project:** Backend

- Add `auth.apps.AuthConfig` to `INSTALLED_APPS` in `kbc/settings.py`
- Add `adminpanel.apps.AdminpanelConfig` to `INSTALLED_APPS` in `kbc/settings.py`
- Verify `python manage.py migrate --check` passes after the change
- Verify `python manage.py check` passes

## Acceptance Criteria
- Both apps appear in `INSTALLED_APPS` in `Base` configuration
- `manage.py migrate` applies all existing migrations without error
- `manage.py check` reports no issues

## Tests
- No new tests required for this change; existing migration smoke test (run `migrate` in CI) covers it

## Notes
The app appears to work currently because `game` imports the models that `auth` and `adminpanel` depend on, so the tables exist. This is a hidden dependency that will silently break on any fresh DB or environment where `game` migrations have not run first.

`auth` conflicts with Django's built-in `django.contrib.auth` — confirm that `auth.apps.AuthConfig` uses a unique `name` (e.g. `"trivivo_auth"` or `"player_auth"`) to avoid namespace collision in the app registry.
