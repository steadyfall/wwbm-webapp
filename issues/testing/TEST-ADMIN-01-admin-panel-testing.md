# Testing for Admin Panel

## Summary
Parent issue for all test coverage of the custom admin panel: the `AddQuestion` API endpoint, access control on all admin views, and model CRUD operations.

## Motivation
The admin panel's `AddQuestion` API is the primary data ingestion path for questions. It has complex validation logic (8 nested functions) with zero test coverage. A bad payload could silently create malformed data. Access control tests verify that the `SuperuserRequiredMixin` is correctly applied across all admin views.

## Scope
**Project:** Backend (Testing)

Blocked by: TEST-INFRA-01

### Sub-issue A — AddQuestion API (`adminpanel/views.py:AddQuestion`)
- Valid single-question payload → 200, question created, M2M fields set correctly
- Valid multi-question payload (3 questions) → 200, all 3 created
- Non-list payload → 400 error response
- Empty list payload → 400 error response
- Payload with missing `question` key → status_code 4 in response
- Payload with missing `difficulty` key → status_code 4 in response
- Payload with incorrect `incorrect_answers` count (not 3) → status_code 5 in response
- Payload with duplicate question text (already in DB) → status_code 5 in response
- Payload with valid category string → question assigned to matching category
- Payload with unknown category string → question assigned to default "None" category
- Request without Authorization token → 401

### Sub-issue B — Access control on admin views
For each admin view (`AdminMainPage`, `AdminListDB`, `AdminDBObjectCreate`, `AdminDBObjectChange`, `AdminDBObjectDelete`, `AdminDBObjectHistory`, `ShowLogDB`, `APIAccess`, `APIDocs`, `GetQuestion`):
- Unauthenticated request → redirect to admin login
- Authenticated non-superuser → 403
- Authenticated superuser → 200 (or expected redirect)

### Sub-issue C — Admin CRUD operations
- `AdminListDB` GET for each model type → 200, correct records listed
- `AdminDBObjectCreate` POST with valid form → object created, log entry added
- `AdminDBObjectChange` POST with valid form → object updated, log entry added
- `AdminDBObjectDelete` POST with `yes` → object deleted, log entry added
- `AdminDBObjectDelete` POST with `no` → no deletion, redirect to list

## Acceptance Criteria
- All `AddQuestion` validation branches are tested
- Every admin view has a 401/403 test for unauthenticated/non-superuser access
- `pytest tests/unit/test_admin_api.py` and `pytest tests/unit/test_admin_views.py` pass

## Tests
File structure:
- `tests/unit/test_admin_api.py` — Sub-issue A
- `tests/unit/test_admin_views.py` — Sub-issues B, C
