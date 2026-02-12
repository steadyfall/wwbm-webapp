# Eliminate Double-Query Pattern in Views

## Summary
Every view in `game/views.py` uses `filter(...).exists()` followed immediately by `.get(...)` on the same object — two database round-trips for what should be one.

## Motivation
The pattern appears ~8 times:
```python
# game/views.py:94-96 (and repeated in test_func, get, post of every view)
check = Session.objects.filter(session_id=sessionId).exists()  # query 1
if check:
    sessionObj = Session.objects.get(session_id=sessionId)     # query 2
```

Each occurrence wastes one DB query. In `QuestionInGame`, this pattern runs in `test_func()`, `get()`, and `post()` — potentially 6 wasted queries for a single page load.

The correct approach is `get_object_or_404()` (for user-facing views) or a `try/except ObjectDoesNotExist` block (for views that need custom error handling):

```python
# Option A (preferred for most views):
from django.shortcuts import get_object_or_404
sessionObj = get_object_or_404(Session, session_id=sessionId)

# Option B (when custom error handling is needed):
try:
    sessionObj = Session.objects.get(session_id=sessionId)
except Session.DoesNotExist:
    return redirect("mainpage")
```

## Scope
**Project:** Backend

- Replace all `filter(...).exists()` + `get(...)` pairs in `game/views.py` with a single query
- Applies to: `Rules.test_func`, `Rules.get`, `Rules.post`, `QuestionInGame.test_func`, `QuestionInGame.get`, `QuestionInGame.post`, `BetweenQuestion.test_func`, `BetweenQuestion.get`, `BetweenQuestion.post`
- Also fix in `adminpanel/views.py` where the same pattern appears for `pk_checker` lookups

## Acceptance Criteria
- No `filter(...).exists()` + `.get(...)` pair on the same model and conditions exists
- All views return the same HTTP responses as before
- `python manage.py check` passes

## Tests
- Existing view unit tests (once written, TEST-01) should still pass
- Query count assertions: each view should perform ≤ 1 query to retrieve a session object
