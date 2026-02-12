# Harden Production Settings Class

## Summary
The `Prod` configuration class in `kbc/settings.py` contains only `DEBUG = False`. This makes any production deployment either broken (Django rejects all requests due to `ALLOWED_HOSTS = []`) or insecure (missing HTTPS enforcement, no cookie security flags, no logging).

## Motivation
- `ALLOWED_HOSTS` defaults to `[]` — Django raises `DisallowedHost` for every request in production
- No `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, or `CSRF_COOKIE_SECURE` — session and CSRF tokens transmitted in plaintext over HTTP
- No server-side logging — errors in production are invisible
- SQLite hardcoded for all environments; `dj-database-url` is installed but unused — production should be able to point at PostgreSQL via env variable

## Scope
**Project:** Infra

- Add `ALLOWED_HOSTS = values.ListValue(environ_name="ALLOWED_HOSTS")` (or read from env) to `Prod`
- Add HTTPS security settings:
  - `SECURE_SSL_REDIRECT = True`
  - `SESSION_COOKIE_SECURE = True`
  - `CSRF_COOKIE_SECURE = True`
  - `SECURE_HSTS_SECONDS = 31536000` (1 year)
  - `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- Add `LOGGING` config with at least a file or stderr handler for `ERROR` level
- Replace hardcoded SQLite `DATABASES` with `dj-database-url` env-variable driven config (already installed as a dependency)
- Add `CONN_MAX_AGE` (can be done here or in ARCH-03)
- Remove `django_browser_reload` from `MIDDLEWARE` in `Prod` (dev-only middleware)

## Acceptance Criteria
- `python manage.py check --deploy` passes (or all warnings are explicitly acknowledged)
- Setting `DJANGO_CONFIGURATION=Prod` + valid `ALLOWED_HOSTS` env var starts the server and accepts requests
- HTTPS headers present when run behind a TLS-terminating proxy (or with a self-signed cert in staging)
- A `500` error produces a log entry, not a silent failure

## Tests
- Deployment readiness check: `manage.py check --deploy --settings=kbc.settings` in CI with `DJANGO_CONFIGURATION=Prod`

## Notes
Lower visual priority than ARCH-05 (design system) but a hard prerequisite for any real deployment. Should be done before any public launch.

`dj-database-url` is already in `pyproject.toml` — just unused. The `Prod` class can read `DATABASE_URL` from the environment with:
```python
import dj_database_url
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}
```
