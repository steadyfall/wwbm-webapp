# Testing for Frontend JavaScript

## Summary
Parent issue for JS-level tests covering `timer.js` behaviour, answer button interaction, and lifeline modal flow. These are the highest-impact client-side paths where bugs BUG-03, BUG-04, and BUG-05 all live.

## Motivation
The three critical frontend bugs (TypeError on lifeline confirm, cancel permanently disables button, answer cards submit empty form) are all testable in isolation with a JS unit testing framework or via Playwright E2E tests. Without tests, these bugs will silently regress.

## Scope
**Project:** Platform (Testing)

Blocked by: BUG-03, BUG-04, BUG-05 (bugs must be fixed before tests can be written to verify the fixes)

### Sub-issue A — Answer button interaction (`question.html`, `timer.js`)
- Clicking an answer card does NOT submit the form (`type="button"` test)
- Clicking card A checks `#option_a` radio
- Clicking card B after card A: `#option_b` is checked, `#option_a` is unchecked
- Clicking Submit with a card selected sends the correct `userAnswer` value
- Clicking Submit without any card selected does not POST (or shows validation)

### Sub-issue B — Timer behaviour (`timer.js`)
- Timer counts down from the server-provided value
- Timer turns red at ≤ 10 seconds
- Timer auto-submits at 0 (calls `$('#sendAnswer').click()`)
- `pause()` stops the countdown
- `pause()` called again resumes the countdown
- Opening lifeline modal calls `pause()`
- Cancelling lifeline modal calls `pause()` (resumes timer)
- Timer DOM displays `NaN` only if intentionally testing that guard — normal flow never shows NaN

### Sub-issue C — Lifeline modal flow
- Cancel button does NOT disable the "Use Lifeline" button (after BUG-04 fix)
- Confirm button IS disabled after clicking it (after BUG-03 fix)
- `timeLeftAfterLifeline` hidden input value is set to current timer value on confirm
- Confirm POSTs the lifeline form with `lifelineSubmit=yes` and correct `lifeline` value

## Acceptance Criteria
- All sub-issue A tests pass (Playwright E2E against a running dev server, or JS unit tests with jsdom)
- Timer tests verify countdown, auto-submit, pause/resume
- No JS console errors during any tested flow

## Tests
Recommended tool: Playwright (already in the project's `.env.mcp`)

File structure:
- `tests/functional/test_question_page.py` — Sub-issues A, B, C (Playwright E2E)
- Or: `static/js/__tests__/timer.test.js` (Jest/vitest if JS unit tests are preferred)

## Notes
E2E Playwright tests require a running Django dev server with seed data. The test setup should use `pytest-django` live server or a separate fixture that starts the server and seeds the DB.
