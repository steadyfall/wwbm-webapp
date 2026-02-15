# Contributing to Trivivo

**Last Updated:** 2026-02-12

Developer setup, workflow, and project conventions.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | [python.org](https://www.python.org/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js / npm | latest LTS | [nodejs.org](https://nodejs.org/) |

## Quick Start

```bash
cp .env.example .env        # add SECRET_KEY
make setup                  # venv + deps + tailwind + migrate
make bootstrap              # seed categories, levels, lifelines
make seed                   # fetch 10 questions from OpenTriviaDB
make run                    # http://127.0.0.1:8000
```

`make setup` performs: `uv venv --seed`, `uv pip install -e ".[dev]"`, `npm install` (tailwind), `make migrate`.

## Make Commands

### Primary

| Command | Description |
|---------|-------------|
| `make setup` | One-time setup: venv, deps, tailwind, migrate |
| `make run` | Start Django dev server **with** Tailwind watcher |
| `make run-server` | Start Django dev server only (no Tailwind) |
| `make run-tailwind` | Start Tailwind CSS watcher only |
| `make check` | Format + lint + Django system check |
| `make test` | Run pytest with coverage (HTML report → `htmlcov/`) |
| `make test-failed` | Re-run only the last failed tests |
| `make test-functional` | Run tests in `tests/functional/` only |
| `make test-pipeline` | Tests with `--cov-fail-under=100` (CI mode) |
| `make format` | Auto-format with `ruff format` |
| `make lint` | Lint with `ruff check --fix` |
| `make migrations` | `manage.py makemigrations` |
| `make migrate` | `manage.py migrate` |
| `make bootstrap` | Load categories, levels, lifelines (idempotent) |
| `make seed` | Fetch 10 questions from OpenTriviaDB and load them |
| `make shell` | `manage.py shell` |
| `make dbshell` | `manage.py dbshell` (SQLite) |
| `make superuser` | `manage.py createsuperuser` |
| `make collectstatic` | Collect static files to `staticfiles/` |
| `make clean` | Remove `__pycache__`, `.pyc`, `.coverage`, caches |

### Destructive (prompt for confirmation)

| Command | Description |
|---------|-------------|
| `make nuke-db` | Delete `db.sqlite3` + all migration files |
| `make restart` | `nuke-db` + `migrate` + `bootstrap` |

## Project Structure

```
trivivo/
├── kbc/               # Project config (settings, root URLs, WSGI/ASGI)
├── game/              # Main game app (models, views, URLs, lifelines, management cmds)
├── auth/              # Authentication app (login, register, validation)
├── adminpanel/        # Custom admin interface + REST API
├── templates/         # HTML templates (base, navbar, footer, per-app)
├── static/            # CSS, JS, images, audio
├── tailwind_theme/    # django-tailwind theme (npm / Tailwind build)
├── tests/             # Test suite
├── docs/              # Documentation
│   ├── CODEMAPS/      # Architecture codemaps per app
│   └── DESIGN/        # UI/UX design system docs
├── Makefile
├── pyproject.toml
└── manage.py
```

See [docs/CODEMAPS/INDEX.md](CODEMAPS/INDEX.md) for full architecture.

## Code Style

Enforced via **ruff** (config in `pyproject.toml`):

- Line length: 88
- Target: Python 3.11
- Rule sets: `E`, `W`, `F` (pyflakes), `I` (isort), `B` (bugbear), `C4` (comprehensions), `UP` (pyupgrade)
- Excludes: migrations, `__pycache__`, `.venv`, `node_modules`

Run before every commit:

```bash
make check
```

## Testing

```bash
make test               # all tests + coverage
make test-failed        # re-run failures only
make test-functional    # tests/functional/ only
make test-pipeline      # CI — fails below 100% coverage
```

Test config in `pyproject.toml` (`[tool.pytest.ini_options]`):

- Settings: `kbc.settings` / `Dev` configuration
- Paths: `tests/`, `game/`, `adminpanel/`, `auth/`
- Coverage excludes: migrations, `__pycache__`, `.venv`, `manage.py`, `conftest.py`, `tailwind_theme/`

## Environment

The project uses `django-configurations`. Set these in `.env` or your shell:

```bash
DJANGO_SETTINGS_MODULE=kbc.settings
DJANGO_CONFIGURATION=Dev    # or Prod
SECRET_KEY=<your-secret-key>
```

See [docs/RUNBOOK.md](RUNBOOK.md) for full env var reference.

## Pre-commit Hooks

Pre-commit is listed as a dev dependency. To install:

```bash
uv run pre-commit install
```

## Workflow

1. Branch off `main`
2. Make changes
3. `make check` — format + lint
4. `make test` — all tests green
5. Open PR targeting `main`

PRs intended for production are labelled `release`.

## Related Docs

- [RUNBOOK.md](RUNBOOK.md) — deployment and operations
- [CODEMAPS/INDEX.md](CODEMAPS/INDEX.md) — architecture overview
- [CODEMAPS/game.md](CODEMAPS/game.md) — game app codemap
- [CODEMAPS/auth.md](CODEMAPS/auth.md) — auth app codemap
- [CODEMAPS/adminpanel.md](CODEMAPS/adminpanel.md) — admin panel codemap
- [CODEMAPS/database.md](CODEMAPS/database.md) — all models
- [DESIGN/design-system.md](DESIGN/design-system.md) — design tokens
