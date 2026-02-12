# Testing for Game Logic

## Summary
Parent issue for all test coverage of core game mechanics: session creation, question selection, answer flow, scoring, level progression, and game-over states.

## Motivation
`game/views.py`, `game/models.py`, and `game/lifelines.py` have zero tests. Critical paths — including session creation, score calculation, and level progression — are exercised only via manual testing. Bugs BUG-01 through BUG-06 were all found by code reading, not by tests.

## Scope
**Project:** Backend (Testing)

Blocked by: TEST-INFRA-01

### Sub-issue A — Session creation and management (`game/models.py`)
- `Session.get_unused_sessionId()` returns a string not already in use
- `Session.get_unused_sessionId()` called twice in quick succession returns two different IDs
- `Session.set_question()` sets `current_question` and adds to `questions_asked`
- `Session.set_question()` calls `get_next_question()` with correct difficulty for the current level
- Session is created with all three lifelines in `left_lifelines`

### Sub-issue B — Question selection (`game/models.py:234`)
- `get_next_question()` returns a question of the correct difficulty for levels 1-5 (Easy), 6-10 (Medium), 11-15 (Hard)
- `get_next_question()` does not return a question already asked to the user
- `get_next_question()` returns `None` (not `IndexError`) when no questions of the required difficulty exist (after ARCH-03 fix)
- `get_next_question()` queries the DB, not Python memory (assertNumQueries: ≤ 2)

### Sub-issue C — Answer flow and scoring (`game/views.py:QuestionInGame.post`)
- Correct answer: score increases by `current_level.money`, level advances, redirect to next question
- Wrong answer: `game_over=True`, `wrong_qn` set, score reduced (KBC rules), redirect to game over
- Exit (submitBtn=exit): `game_over=True`, redirect to quit status
- Level 15 correct answer: `game_over=True`, redirect to "finished" status
- Answer with invalid `userAnswer` (not one of current question's options): redirect with warning, no state change (after BUG-06 fix)

### Sub-issue D — Rules flow (`game/views.py:Rules`)
- GET with valid session, rules not yet agreed: 200, rules template
- GET with already-agreed session: redirect to mainpage
- POST with `agreed=yes`: session updated, redirect to question/1
- POST without `agreed` key: session deleted, redirect to mainpage — no NameError (after BUG-01 fix)
- POST with non-existent session ID: redirect to mainpage

### Sub-issue E — Model default PK methods
- `Level.get_default_pk()` returns the PK of the Level with `level_number=0`
- `Question.get_default_pk()` returns the PK of the sentinel "None" question
- `Option.get_default_pk()` returns the PK of the sentinel "None" option
- `get_sentinel_user()` returns the PK of the "deleted" user, creating it if absent

## Acceptance Criteria
- All sub-issues pass with `pytest tests/unit/test_game_*.py`
- No test relies on hardcoded PKs

## Tests
File structure:
- `tests/unit/test_game_models.py` — Sub-issues A, B, E
- `tests/unit/test_game_views.py` — Sub-issues C, D
