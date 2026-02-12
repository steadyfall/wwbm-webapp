# Fix camelCase Field Names on Django Models

## Summary
`Session.agreedToRules` and `Session.gameOver` use camelCase naming, violating Django and PEP 8 conventions. This makes ORM filter calls error-prone and breaks any tooling that enforces snake_case naming.

## Motivation
```python
# game/models.py:191,193
agreedToRules = models.BooleanField(verbose_name="Agreed to T&C", default=False)
gameOver = models.BooleanField(verbose_name="Game over?", default=False)
```

Django silently normalises these to lowercase column names (`agreedtorules`, `gameover`) in SQLite. Referencing them with the wrong case in filters — e.g. `filter(agreed_to_rules=True)` — raises no error but returns incorrect results. Any developer unfamiliar with the codebase will use the expected `snake_case` form and get silent bugs.

## Scope
**Project:** Backend

- Rename `agreedToRules` → `agreed_to_rules` on `Session` model (`game/models.py:191`)
- Rename `gameOver` → `game_over` on `Session` model (`game/models.py:193`)
- Update all references in `game/views.py` (`sessionObj.agreedToRules`, `sessionObj.gameOver`)
- Update all references in `adminpanel/views.py` if present
- Update all template references if present
- Generate and apply a migration (column rename)

## Acceptance Criteria
- `Session.agreed_to_rules` and `Session.game_over` are the field names in models
- All views, templates, and tests use the snake_case names
- Migration applies cleanly
- `python manage.py check` passes
- Ruff `N815` (mixed-case variable in class scope) rule passes

## Tests
- All existing game flow tests continue to pass after the rename
- Unit test: `Session.objects.filter(agreed_to_rules=True)` returns sessions where the field is True

## Notes
This requires a schema migration. On SQLite, `ALTER TABLE RENAME COLUMN` is supported since SQLite 3.25. Django will generate the correct migration automatically with `makemigrations`.
