# Remove Dead Test View with Hardcoded Question Index

## Summary
`game/views.py:38-50` contains a `question()` view function that accesses `Question.objects.all()[345]` — a hardcoded array index that crashes with `IndexError` if the DB has fewer than 346 questions. This is clearly leftover test/dev code.

## Motivation
```python
# game/views.py:38 — never called from production URLs, but still present
def question(request):
    allOptions = [i.text for i in Question.objects.all()[345].incorrect_options.all()]
    # ↑ IndexError if len(Question.objects.all()) < 346
```

Additionally, `game/views.py:17-30` contains `pageChecker` which also appears to be a test stub (`print(request.POST)`, hardcoded context values). Both functions are unprotected by auth and pollute the codebase.

## Scope
**Project:** Backend

- Remove the `question()` function from `game/views.py:38-50`
- Remove the `pageChecker()` function from `game/views.py:17-30`
- Remove any URL patterns that reference these functions in `game/urls.py`
- Remove the `print(request.POST)` statement at `game/views.py:20` (see also BUG-15)

## Acceptance Criteria
- Neither `question` nor `pageChecker` appear in `game/views.py`
- `game/urls.py` has no dangling URL patterns pointing to removed functions
- `python manage.py check` passes

## Tests
- N/A — these are deletions
