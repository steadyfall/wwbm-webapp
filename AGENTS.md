# AGENTS.md

Guidance for coding agents working in this repository.

## Project Shape

Trivivo is a Django 5 trivia game. The Django project is `kbc`; apps are:

- `game`: quiz flow, scoring, lifelines, levels, and question management commands.
- `auth`: user/admin authentication and validation.
- `adminpanel`: custom admin UI and REST API surface.
- `tailwind_theme`: django-tailwind theme and Tailwind build inputs.

Shared HTML lives in `templates/`, static assets in `static/`, and tests in `tests/` plus app-level `tests.py` files. Architecture notes are in `docs/CODEMAPS/`.

## Setup And Commands

Prefer Make targets over raw commands when a target exists.

```bash
cp .env.example .env
make setup
make bootstrap
make run
```

Common checks:

```bash
make check
make test
make test-failed
make test-functional
```

Tests require the local environment file because the Makefile sources `.env` before pytest. The pytest config is in `pyproject.toml` and uses `kbc.settings` with `DJANGO_CONFIGURATION=Dev`.

## Coding Conventions

- Python target is 3.11; dependencies are managed with `uv`.
- Formatting and linting are handled by Ruff through `make check`.
- Keep line length and imports aligned with `pyproject.toml`.
- Use `@pytest.mark.django_db` for tests that touch the database.
- Read the existing view/model/form code before asserting redirects, messages, or template behavior.
- For frontend changes, follow the existing templates/static structure and the design docs in `docs/DESIGN/`.

## Files To Treat Carefully

- Do not edit generated caches or reports such as `htmlcov/`, `.pytest_cache/`, `__pycache__/`, or `.ruff_cache/`.
- Do not hand-edit `db.sqlite3` for code changes.
- Do not hand-edit Tailwind output in `tailwind_theme/static/css/dist/`; change `tailwind_theme/static_src/src/styles.css` or Tailwind config and rebuild instead.
- Do not run destructive Make targets (`make nuke-db`, `make restart`) unless the user explicitly asks.

## Reference Docs

- `README.md`: high-level project overview and issue labels.
- `docs/CONTRIB.md`: setup, workflow, commands, and style.
- `docs/RUNBOOK.md`: environment variables, management commands, and operations.
- `CLAUDE.md`: branch, commit, PR, and testing conventions.

TODO: Add deployment host/platform-specific commands if they become part of routine agent work.
