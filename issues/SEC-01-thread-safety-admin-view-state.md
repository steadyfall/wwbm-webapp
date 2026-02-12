# Security: Thread-Unsafe Class-Level Mutable State in Admin Views

## Summary
`AdminDBObjectCreate` and `AdminDBObjectChange` store `form_class` and `instance` as class-level attributes via `setattr()`. Under any multi-threaded WSGI server, concurrent requests will overwrite each other's state, leading to silent data corruption — one user's save operation targets another user's record.

## Motivation
```python
# adminpanel/views.py:477-483 (in get/post methods)
setattr(AdminDBObjectCreate, "form_class", modelFormDict[smallcaseDB])  # class-level write
setattr(AdminDBObjectChange, "instance",
        model.objects.get(pk=int(pk) if pk.isnumeric() else pk))         # class-level write
```

These writes are on the **class** itself. Django creates one view instance per request, but the class is shared across all requests. Sequence:
1. Thread A sets `AdminDBObjectChange.instance = question_X`
2. Thread B sets `AdminDBObjectChange.instance = question_Y`
3. Thread A calls `self.get_instance()` → returns `question_Y` (Thread B's object)
4. Thread A saves form data into `question_Y`'s record instead of `question_X`

This is silent data corruption: no error, wrong record modified.

## Scope
**Project:** Backend (treat as security severity due to data integrity impact)

- Move `form_class` and `instance` from class attributes to instance attributes
  - Set them in `get()` and `post()` on `self` (not `cls` or the class itself)
  - Remove all `setattr(AdminDBObjectCreate, ...)` and `setattr(AdminDBObjectChange, ...)` calls
- `get_form_class()` should return from `self.form_class` (instance attribute)
- `get_instance()` should return from `self.instance` (instance attribute)

Example pattern:
```python
def get(self, request, *args, **kwargs):
    ...
    self.form_class = modelFormDict[smallcaseDB]
    self.instance = model.objects.get(pk=...)
    return render(request, ..., self.context_creator())
```

## Acceptance Criteria
- `AdminDBObjectChange.form_class` and `AdminDBObjectChange.instance` are never written as class-level attributes
- Concurrent requests to the admin change view operate on independent state
- Admin CRUD operations (view, edit, save) work correctly in single-threaded tests

## Tests
- Unit test: two sequential requests to `AdminDBObjectChange` with different PKs each operate on their respective objects
- (Thread-safety is hard to test deterministically; the unit test verifies the data path is instance-scoped)

## Notes
The root cause is reimplementing Django's `UpdateView`/`CreateView` CBVs manually. Long-term, consider using Django's built-in generic editing views which handle this correctly by design. The instance-level fix is the right immediate action for the existing custom implementation.
