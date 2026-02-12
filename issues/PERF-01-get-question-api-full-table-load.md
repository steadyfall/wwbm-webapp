# GetQuestion API Loads Full Question Table for Random Sample

## Summary
`adminpanel/views.py:763` uses `random.sample(list(Question.objects.all()), count)` to retrieve up to 5 random questions. This loads the entire `Question` table into Python memory on every request to the `/admin/api/get-question/` endpoint.

## Motivation
```python
# adminpanel/views.py:763
data = random.sample(list(Question.objects.all()), count)
```

With 10,000 questions this deserializes 10,000 ORM objects, returns 5, and discards the rest. The memory spike is proportional to the total question count.

## Scope
**Project:** Backend

- Replace with a DB-level random sample:
  ```python
  data = list(Question.objects.order_by("?")[:count])
  ```
- Note: `ORDER BY RANDOM()` on SQLite is acceptable at this scale; on PostgreSQL consider `TABLESAMPLE` for very large tables
- Also fix: `count = int(count) if count.isdigit() else 1` — `count.isdigit()` returns `False` for `None` (when `?count=` param is missing), which would raise `AttributeError`. Guard against `count` being `None`.

## Acceptance Criteria
- `/admin/api/get-question/?count=5` returns 5 random questions without loading the full table
- Missing or non-numeric `count` parameter defaults to 1 without raising an error
- `count > 5` still returns the `"Cannot request more than 5 objects."` error

## Tests
- Unit test: `GetQuestion` with `count=3` returns exactly 3 questions
- Unit test: `GetQuestion` with no `count` param returns 1 question (default)
- Unit test: `GetQuestion` with `count=10` returns error response
