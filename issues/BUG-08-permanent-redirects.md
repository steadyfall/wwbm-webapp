# Remove `permanent=True` from Game-Flow Redirects

## Summary
Nearly every `redirect()` call in `game/views.py` uses `permanent=True`, issuing HTTP 301 redirects. Browsers cache 301 responses indefinitely — fixing a redirect target or changing a URL pattern will have no visible effect until users manually clear their browser cache.

## Motivation
HTTP 301 is designed for permanent URL moves (e.g., a domain migration). Game flow navigation — "after answering correctly, go to the next question" — is dynamic and should use HTTP 302. The current code means:
- Any fix to a redirect URL won't reach users who have cached the old 301
- Bookmarking `/game/session/question/1/` then clearing the session could redirect to a cached stale URL

Affected locations (non-exhaustive):
- `game/views.py:72` — rules redirect after session creation
- `game/views.py:113` — mainpage redirect
- `game/views.py:130` — question redirect after agreeing to rules
- `game/views.py:347`, `367`, etc. — all post-answer redirects

## Scope
**Project:** Backend

- Remove `permanent=True` from all `redirect()` calls in `game/views.py` that represent dynamic game-flow navigation
- `permanent=True` may be retained only for truly permanent URL structure changes (none currently apply in game logic)

## Acceptance Criteria
- All redirects in game flow return HTTP 302
- `python manage.py check` passes
- Game flow (start → rules → question → answer → next question) works end to end

## Tests
- Unit tests for each view: verify redirect status code is 302
