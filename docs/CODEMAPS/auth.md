# Auth App Codemap

**Last Updated:** 2026-02-12
**App:** `auth/`
**Entry Point:** `auth/urls.py`

## Architecture

```
Browser → auth/urls.py → views.py → Django auth backend → templates/authentication/

Validation Module (auth/validate.py):
  ├─ usernameValidator()     - Regex: [\w.@+-]{1,149}
  ├─ emailValidator()        - Standard email regex
  ├─ passwordValidator()     - Min 8 chars, non-numeric, not username
  └─ confirmPassword()       - Match + validate second password
```

## Models

Auth app does not define custom models. Uses Django's built-in `django.contrib.auth.models.User`.

| Field | Type | Notes |
|-------|------|-------|
| `username` | CharField | 1–150 chars |
| `email` | EmailField | Optional |
| `password` | CharField | Hashed |
| `is_superuser` | BooleanField | Admin status flag |

## Views

| View | Type | URL Name | Purpose | Auth Required |
|------|------|----------|---------|---------------|
| `register()` | Function | `register` | User registration with validation | No |
| `login()` | Function | `login` | Standard user login | No |
| `logout()` | Function | `logout` | User logout with redirect | Yes |
| `adminlogin()` | Function | `adminLogin` | Admin-only login with superuser check | No |
| `adminlogout()` | Function | `adminLogout` | Admin logout with superuser check | Yes |

## URL Patterns

| Pattern | Name | View | Methods |
|---------|------|------|---------|
| `login/` | `login` | `login()` | GET, POST |
| `logout/` | `logout` | `logout()` | GET |
| `register/` | `register` | `register()` | GET, POST |
| `admin-login/` | `adminLogin` | `adminlogin()` | GET, POST |
| `admin-logout/` | `adminLogout` | `adminlogout()` | GET |

## Validation Rules

| Field | Rule |
|-------|------|
| Username | `^[\w.@+-]{1,149}$` |
| Email | `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$` |
| Password | Min 8 chars, at least one non-numeric char, cannot contain username |
| Password confirm | Must match password and pass passwordValidator |

## Data Flow

### Registration
```
POST /register/
  → validate username, email, password, password2
  → User already exists? → Warning → redirect login
  → Create User → Success → redirect login
```

### Login
```
POST /login/
  → validate username + password
  → User not found? → Warning → redirect register
  → authenticate()
    → Failed  → Error → redirect login
    → Success → login() → redirect mainpage
```

### Admin Login
```
POST /admin-login/
  → already authenticated?
    → is_superuser → redirect adminMainPage
    → not superuser → redirect mainpage
  → validate username
  → User not found? → Warning → redirect adminLogin
  → authenticate()
    → Failed  → Error → redirect adminLogin
    → Success → login()
      → is_superuser → redirect adminMainPage
      → not superuser → redirect mainpage
```

## Related Apps

- [adminpanel.md](adminpanel.md) — uses admin login views
- [game.md](game.md) — authenticated users access game content
- [database.md](database.md) — Django auth tables
