# NameError Crash on Rules Page POST

## Summary
Submitting the rules form without the `agreed` field (including browser back-button flow) causes an unhandled `NameError` and returns HTTP 500.

## Motivation
`game/views.py:119` calls `sessionObj.delete()` before `sessionObj` is ever assigned. The variable is only assigned on line 122, after the guard. Any POST request that is missing the `agreed` key hits this path and crashes.

```python
# Current (broken):
check = Session.objects.filter(session_id=sessionId).exists()
if "agreed" not in tuple(self.request.POST.keys()):
    sessionObj.delete()  # ← NameError: 'sessionObj' not defined
    return redirect("mainpage", permanent=True)
if check:
    sessionObj = Session.objects.get(session_id=sessionId)  # too late

# Fix: assign first, then guard
if check:
    sessionObj = Session.objects.get(session_id=sessionId)
    if "agreed" not in tuple(self.request.POST.keys()):
        sessionObj.delete()
        return redirect("mainpage", permanent=True)
```

## Scope
**Project:** Backend

- Fix variable assignment order in `Rules.post()` at `game/views.py:115-133`
- Ensure session is deleted (not leaked) when `agreed` is missing
- Handle the case where `check` is False (session doesn't exist) before the delete

## Acceptance Criteria
- POST to `/game/<session>/rules/` without `agreed` field: redirects to mainpage, no 500 error, session is cleaned up
- POST with `agreed=yes`: game proceeds normally
- POST with `agreed=no`: session deleted, redirected to mainpage

## Tests
- Unit test: `Rules.post()` without `agreed` key → 302 redirect to mainpage, session deleted
- Unit test: `Rules.post()` with non-existent session ID → 302 redirect to mainpage
- Unit test: `Rules.post()` with `agreed=yes` → redirects to question page

## Notes
The current code also has a double-query anti-pattern (see BUG-11) — fix both simultaneously.
