# Data Model Correctness — UUID Session IDs and Dynamic Lifeline Lookup

## Summary
Two data-model fragility issues with the same root cause: code that assumes a specific database state at initialisation time. Both will silently break on any fresh DB, `flush`, or re-seed.

## Motivation
1. **Hardcoded lifeline PKs** (`game/lifelines.py:8`): `mappedLifelines = [(2, FIFTY50), (3, AUDIENCE_POLL), (4, EXPERT_ANSWER)]` assumes lifelines were inserted with PKs 2, 3, and 4. A fresh DB seed yields different PKs and every lifeline call either fetches the wrong lifeline or raises `DoesNotExist`.
2. **String session IDs with a non-atomic collision check** (`game/models.py:226–231`): The uniqueness check reads all existing session IDs into a Python set, then generates a candidate. Between the read and the `Session.objects.create()`, a concurrent request can claim the same ID. `session_id` is the primary key — a duplicate will raise `IntegrityError`.

## Scope
**Project:** Backend

### Sub-issue A — Dynamic lifeline lookup
- Replace the hardcoded `[(2, FIFTY50), ...]` list in `game/lifelines.py:8` with a runtime lookup:
  ```python
  mappedLifelines = {
      lifeline.name: lifeline.pk
      for lifeline in Lifeline.objects.filter(name__in=[FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER])
  }
  ```
- This lookup should be lazy (called at first use, not at import time) to avoid import-time DB hits
- Update all three lifeline functions to use the new mapping

### Sub-issue B — UUID session IDs
- Replace `session_id = models.CharField(primary_key=True, max_length=8)` with `session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`
- Remove `Session.get_unused_sessionId()` entirely — UUID generation is collision-proof by design
- Update all URL patterns and view kwargs that reference `session` to handle UUID format
- Generate and apply the migration

## Acceptance Criteria
- Sub-issue A: Creating a fresh DB, running `createlifelines` management command, then starting a game uses lifelines correctly without hardcoding PKs
- Sub-issue B: `Session.objects.create()` never calls `get_unused_sessionId()` and the `session_id` field is a UUID
- `python manage.py migrate` completes without error
- Game start, lifeline use, and session lookup flows all work end-to-end

## Tests
- Unit test: `Session.objects.create()` generates a valid UUID primary key
- Unit test: Lifeline lookup with a fresh DB returns correct PK for each lifeline name
- Integration test: Full game flow (start → answer → lifeline → answer → end) completes without error

## Notes
Sub-issue B changes the URL shape from `/game/aBcD1234/question/1/` to `/game/xxxxxxxx-xxxx.../question/1/`. If short URLs are important for aesthetics, a separate `slug` field can be kept for display while the UUID remains the PK — but that is a separate concern.

Sub-issue A should be done before B; the lifeline fix is simpler and independently useful.
