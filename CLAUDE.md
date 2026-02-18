# Trivivo

## Repository
- **Repo**: `steadyfall/wwbm-webapp`
- **Main branch**: `main`

## Git & Commits

**Branch naming**: `<username>/descriptive-name` (e.g. `steadyfall/tri-60-test-usernamevalidator-...`)
- Ticket IDs are allowed in branch names but **not** in PR titles
- Max 60 characters total

**Commit messages**: Conventional Commits format
```
<type>: short description
```
Types: `feat`, `fix`, `test`, `build`, `chore`, `style`, `refactor`

## Pull Requests

- **Always create PRs as drafts** (`--draft`) targeting `main`
- **Do not include ticket IDs in PR titles** (no `TRI-xx` or issue numbers)
- **Follow `.github/PULL_REQUEST_TEMPLATE.md`** for PR body structure
- Keep PR body ≤ 500 words
- Include screenshots/pictures for any frontend/visual changes

<!-- Linting: run `uv run ruff check . && uv run ruff format .` before committing (configured in pyproject.toml) -->

## Testing

**Framework**: `pytest` with `pytest-django`

**Config**: `pyproject.toml`
```
DJANGO_SETTINGS_MODULE=kbc.settings
DJANGO_CONFIGURATION=Dev
```

**Before running tests, source the env file**:
```bash
# Run a specific file:
source .env && uv run pytest tests/unit/<file>

# Run all tests:
source .env && uv run pytest
```

**Rules**:
- All tests must pass — no skips, no failures
- Use `@pytest.mark.django_db` for any test that touches the database
- Integration tests use `django.test.Client`
- Unit tests for validators/pure logic require no DB

**Test file location**: `tests/unit/` for unit tests; app-level tests go alongside their app (e.g. `game/tests/`)

## General Conventions

- **Read source code before writing tests** — never assume redirect URLs, message levels, or behavior; read the actual view/function first
- Use git worktrees when working on parallel feature branches to avoid interfering with `main`
- Run `make setup` when in freshly initialized git worktree
- Source `.env` in every worktree (it is not copied automatically)

## References

- See `docs/RUNBOOK.md` for deployment, database management, and operational commands
- Run `make help` to list all available commands; prefer `make` targets over raw `uv run python manage.py ...` invocations
