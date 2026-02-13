# Trivivo Operations Runbook

**Last Updated:** 2026-02-12

Complete operational guide for deploying, managing, and maintaining the Trivivo trivia game application.

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django secret key. Generate: `python -c "import secrets; print(secrets.token_urlsafe(50))"` | `Qw_K9xL2mP...` |
| `DJANGO_CONFIGURATION` | No | Config class to load | `Dev` |
| `DJANGO_SETTINGS_MODULE` | No | Settings module (rarely changed) | `kbc.settings` |

### Configuration Classes (`kbc/settings.py`)

| Class | `DEBUG` | `ALLOWED_HOSTS` | Notes |
|-------|---------|-----------------|-------|
| `Dev` | `True` | `localhost`, `127.0.0.1` | Browser reload, Tailwind compilation |
| `Prod` | `False` | Your domain(s) | Static files must be collected |

## Database Setup

```bash
# Apply migrations
make migrate

# Bootstrap base game data (levels, lifelines, categories)
make bootstrap

# Seed with questions from OpenTriviaDB
make seed
```

## Management Commands

### Bootstrap (run once, in order)

| Command | Purpose |
|---------|---------|
| `createlevels [--enable-logging]` | Create 17 levels (−1 to 16) with prize money |
| `createlifelines [--enable-logging]` | Create 3 lifelines (Fifty-50, Audience Poll, Expert Answer) |
| `createcategories [--enable-logging] [--force]` | Fetch categories from OpenTriviaDB API |

### Question Seeding

| Command | Purpose |
|---------|---------|
| `fetchqns [N] [--category ID] [--difficulty e\|m\|h] [--enable-logging]` | Fetch N questions from OpenTriviaDB, write to JSON |
| `extractoptions <file.json> [--enable-logging]` | Extract unique answer options from JSON → Option model |
| `addquestions <file.json> [--enable-logging] [--force-update]` | Add questions from JSON → database |

**Full seed pipeline:**
```bash
make seed
# or manually:
uv run python manage.py createcategories
uv run python manage.py fetchqns 50
uv run python manage.py extractoptions fetched_questions_*.json
uv run python manage.py addquestions fetched_questions_*.json
```

### Utilities

```bash
uv run python manage.py createsuperuser   # Create admin user
uv run python manage.py showmigrations    # Show migration status
uv run python manage.py shell             # Interactive Django shell
uv run python manage.py dbshell          # SQLite direct shell
```

## Deployment

### Pre-deployment Checklist

- [ ] Tests pass: `make test-pipeline`
- [ ] Linting passes: `make check`
- [ ] `DJANGO_CONFIGURATION=Prod`
- [ ] `SECRET_KEY` is unique and not committed
- [ ] `ALLOWED_HOSTS` updated for your domain
- [ ] Static files collected: `make collectstatic`
- [ ] Migrations applied: `make migrate`

### Production Steps

```bash
export DJANGO_CONFIGURATION=Prod

# Collect static files
make collectstatic

# Apply migrations
make migrate

# Create admin user
make superuser

# Start (example with gunicorn)
uv run gunicorn kbc.wsgi:application --bind 0.0.0.0:8000
```

## Common Operational Tasks

### Reset Dev Database

```bash
make nuke-db       # Wipes database with confirmation
make restart       # nuke-db + migrate + bootstrap
```

### Backup Database

```bash
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

### Clean Build Artefacts

```bash
make clean   # Removes __pycache__, .pyc, .coverage, htmlcov, pytest/mypy/ruff caches
```

## Troubleshooting

| Symptom | Command |
|---------|---------|
| App won't start | `make check` — check for syntax / config errors |
| Missing static files | `make collectstatic` |
| Migration errors | `uv run python manage.py showmigrations` |
| DB queries | `make dbshell` |

### Complete Data Reconstruction

```bash
rm db.sqlite3
make migrate
make bootstrap
make seed
make superuser
```

## Related

- [CONTRIB.md](CONTRIB.md) — developer setup and workflow
- [CODEMAPS/INDEX.md](CODEMAPS/INDEX.md) — architecture overview
