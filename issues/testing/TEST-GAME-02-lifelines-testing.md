# Testing for Lifelines

## Summary
Sub-issue of TEST-GAME-01. Covers unit and integration tests for all three lifeline implementations (`fifty50`, `audiencePoll`, `expertAnswer`) and the shared `general_procedure`.

## Motivation
Lifeline logic has three distinct failure modes that are currently untested:
1. `general_procedure` silently uses hardcoded PKs (ARCH-04) — tests will catch regressions after the fix
2. `fifty50` uses `secrets.choice()` while `audiencePoll` uses `random.randint()` — inconsistency is inconsistent with security expectations
3. No test verifies that a used lifeline is actually moved from `left_lifelines` to `used_lifelines`

## Scope
**Project:** Backend (Testing)

Blocked by: TEST-INFRA-01, ARCH-04 (dynamic lifeline lookup)

### Tests to write

**`general_procedure(lifeline_id, question_id, session_id)`:**
- Adds question to `session.lifeline_qns`
- Removes the lifeline from `session.left_lifelines`
- Adds the lifeline to `session.used_lifelines`
- After: `left_lifelines` count decreases by 1, `used_lifelines` count increases by 1

**`expertAnswer(question_id, session_id)`:**
- Returns a string containing the correct option text
- Calls `general_procedure` (verify side effects above)
- Returned string format: `"The expert says that the answer would be <b>{correct_text}</b>."`

**`fifty50(question_id, session_id)`:**
- Returns a list of exactly 2 option texts
- The list always contains the correct option text
- The list contains exactly 1 of the incorrect option texts (not both, not neither)
- Calls `general_procedure` (verify side effects)

**`audiencePoll(question_id, session_id)`:**
- Returns a non-empty string (HTML list items)
- The correct answer is present in the output
- All incorrect options are present in the output
- Percentages are numeric and between 1 and 100
- Calls `general_procedure` (verify side effects)

**Integration: lifeline in game flow:**
- Use a lifeline during a question → next page render shows lifeline removed from `left_lifelines`
- Use all three lifelines → "Use Lifeline" button is hidden/absent from the question page

## Acceptance Criteria
- All tests pass for all three lifeline functions
- After a lifeline is used, `left_lifelines` and `used_lifelines` reflect the change

## Tests
File: `tests/unit/test_lifelines.py`
