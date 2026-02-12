# Session Model — Query Optimization and Missing Indexes

## Summary
The `Session` model and its related views execute hundreds of redundant queries per page load due to N+1 patterns and missing database indexes. This is the single highest-impact performance issue in the codebase.

## Motivation
`ScoreBoard.context_creator()` (`game/views.py:558`) calls `.correct_qns.all().count()` and `.used_lifelines.all().count()` inside a Python loop — one query per field per session row. With 100 sessions this is 200+ queries for one page. The same pattern exists in `AdminMainPage.context_creater()` for categories and users. Additionally, `Question.difficulty`, `Session.date_created`, `Session.session_user`, and `QuestionOrder.date_chosen` have no `db_index=True`, meaning every filtered query does a full table scan.

## Scope
**Project:** Backend

### Part A — Fix N+1 queries
- `game/views.py:558` ScoreBoard: replace Python-loop `.count()` calls with a single `.annotate(correct_count=Count("correct_qns"), lifeline_count=Count("used_lifelines"))` queryset
- `adminpanel/views.py:125` AdminMainPage: replace `x.all_questions.all().count()` inside `map()` with `.annotate(question_count=Count("all_questions"))` on the Category queryset
- `adminpanel/views.py:172` AdminMainPage: replace double `User.objects.all()` with a single annotated queryset

### Part B — Add missing indexes
Add `db_index=True` to:
- `Question.difficulty` (`game/models.py:147`)
- `Session.date_created` (`game/models.py:173`)
- `Session.session_user` (`game/models.py:174`)
- `QuestionOrder.date_chosen` (`game/models.py:271`)

Generate and apply migrations for the index additions.

### Part C — DB connection pool
- Add `"CONN_MAX_AGE": 600` to `DATABASES["default"]` in `kbc/settings.py`

### Part D — Fix `get_next_question()` memory and crash
`game/models.py:234-248` loads the full `Question` table and all questions asked to the user into Python memory, then performs an in-memory set difference — O(n) memory, O(n²) worst-case computation. It also raises an uncaught `IndexError` if no questions of the required difficulty exist.

- Replace the Python set-difference with a single filtered query:
  ```python
  asked_pks = sessionObj.questions_asked.values_list("pk", flat=True)
  qn = (
      Question.objects
      .filter(difficulty=mode)
      .exclude(pk__in=asked_pks)
      .order_by("?")
      .first()
  )
  if qn is None:
      # Handle gracefully: fall back to any difficulty, or end the game
      raise ValueError(f"No {mode} questions available")
  ```
- Handle the `None` result explicitly at the call site in `Session.set_question()` and the view

## Acceptance Criteria
- ScoreBoard page triggers ≤ 5 queries (verifiable via `django-debug-toolbar` or `assertNumQueries` in tests)
- AdminMainPage dashboard triggers ≤ 20 queries
- All four model fields have `db_index=True` and corresponding migrations
- `CONN_MAX_AGE` is set
- `get_next_question()` does not load any full table into Python memory
- `get_next_question()` returns `None` (not `IndexError`) when no questions of the required difficulty exist

## Tests
- Add `assertNumQueries` bounds test for `ScoreBoard` view once test infrastructure is established
- Unit test: `get_next_question()` with no questions of the required difficulty returns `None` without raising
- Unit test: `get_next_question()` returns a question of the correct difficulty not already asked

## Notes
Model split (GameSession / GameState / GameScore) is intentionally deferred — address structural concerns after test coverage exists. This issue is scoped to the minimal performance fixes that don't require structural changes.
