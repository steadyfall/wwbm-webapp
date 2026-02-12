# Testing for Authentication

## Summary
Parent issue for all test coverage in the `auth` app. Covers validation functions, registration/login/logout flows, and admin login.

## Motivation
`auth/validate.py`, `auth/views.py`, and the corresponding templates have zero test coverage. Auth is the entry point for every user and admin — validation and flow bugs here affect all users.

## Scope
**Project:** Backend (Testing)

Blocked by: TEST-INFRA-01

### Sub-issue A — Auth validation unit tests (`auth/validate.py`)
Test every condition of each validator:

**`usernameValidator`:**
- Valid username → `True`
- Username with allowed special chars (`.@+-`) → `True`
- Username with disallowed chars (space, `!`) → `False`
- Empty string → `False`
- Username > 149 chars → `False`

**`emailValidator`:**
- Valid email (`user@example.com`) → `True`
- Missing `@` → `False`
- Missing domain → `False`
- Local part with invalid chars → `False`

**`passwordValidator`:**
- Valid password (≥8 chars, 1 non-digit, username not in password) → `True`
- Password < 8 chars → `False`
- All-numeric password → `False`
- Password containing username (case-insensitive) → `False`
- Empty username → `False`

**`confirmPassword`:**
- Matching passwords, both valid → `True`
- Mismatched passwords → `False`
- Second password fails `passwordValidator` → `False`

### Sub-issue B — Registration flow tests (`auth/views.py:register`)
- POST with valid data → user created, redirect to login, success message
- POST with duplicate username → redirect to login, warning message
- POST with invalid email → redirect to register, error message
- POST with mismatched passwords → redirect to register, error message
- POST with password containing username → redirect to register, error message
- POST missing a required field (KeyError path) → redirect to register, error message
- GET → 200, renders registration template

### Sub-issue C — Login flow tests (`auth/views.py:login`)
- POST with valid credentials → user authenticated, redirect to mainpage
- POST with non-existent username → redirect to register, warning message
- POST with wrong password → redirect to login, error message
- POST with invalid username format → redirect to login, error message
- GET → 200, renders login template
- Already-authenticated user → (test current behaviour)

### Sub-issue D — Admin login flow tests (`auth/views.py:adminlogin`)
- POST with valid superuser credentials → redirect to admin panel
- POST with valid non-superuser credentials → redirect to mainpage
- POST with invalid credentials → redirect to admin login, error message
- Authenticated superuser GET → redirect to admin panel (after BUG-02 fix)
- Authenticated non-superuser GET → redirect to mainpage

## Acceptance Criteria
- All validator functions have 100% branch coverage
- All view flows have at least one test per branch
- `pytest tests/unit/test_auth_validation.py` and `pytest tests/unit/test_auth_views.py` pass

## Tests
File structure:
- `tests/unit/test_auth_validation.py` — Sub-issue A
- `tests/unit/test_auth_views.py` — Sub-issues B, C, D
