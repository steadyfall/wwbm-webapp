# Trivivo Architecture Overview

**Last Updated:** 2026-02-12
**Framework:** Django 5.1.2
**Python:** 3.11+

## App Overview

| App | Purpose | Key Models | Entry Point |
|-----|---------|------------|-------------|
| `game` | Main trivia game logic and gameplay views | Session, Question, Level, Category, Option, Lifeline, ChosenOption, QuestionOrder | `game/urls.py` |
| `auth` | User authentication (login/register) | Django User (built-in) | `auth/urls.py` |
| `adminpanel` | Custom admin interface for managing questions and game data | (uses game models) | `adminpanel/urls.py` |
| `kbc` | Project configuration and root URL routing | — | `kbc/settings.py`, `kbc/urls.py` |

## Request Lifecycle

```
Browser
  → Django Middleware Stack
  → URL Router (kbc/urls.py)
      ├── /djadmin/     → Django Admin
      ├── /admin/       → adminpanel.urls
      ├── /             → game.urls
      ├── /auth/        → auth.urls
      └── /__reload__/  → django_browser_reload (dev)
  → View (CBV or FBV)
  → Model Query / Update
  → Template Rendering (templates/)
  → HTTP Response
```

## Middleware Stack

Order defined in `kbc/settings.py`:

1. `SecurityMiddleware` — HTTPS enforcement, security headers
2. `SessionMiddleware` — Session management
3. `CommonMiddleware` — MIME types, URL normalisation
4. `CsrfViewMiddleware` — CSRF protection
5. `AuthenticationMiddleware` — User auth context
6. `MessageMiddleware` — Django messages framework
7. `XFrameOptionsMiddleware` — Clickjacking protection
8. `BrowserReloadMiddleware` — Live reload (dev only)

## URL Structure

```
kbc/urls.py
├── /djadmin/                               → Django Admin Interface
├── /admin/                                 → adminpanel.urls
│   ├── /                                   → AdminMainPage
│   ├── /test/                              → testSite
│   ├── /apps/<db>/                         → AdminListDB
│   ├── /logs/                              → ShowLogDB
│   ├── /apps/<db>/object/<pk>/             → AdminDBObjectChange
│   ├── /apps/<db>/create/                  → AdminDBObjectCreate
│   ├── /apps/<db>/object/<pk>/delete/      → AdminDBObjectDelete
│   ├── /apps/<db>/object/<pk>/history/     → AdminDBObjectHistory
│   ├── /api-access/                        → APIAccess
│   ├── /api-docs/                          → APIDocs
│   ├── /random-question/                   → GetQuestion (API)
│   └── /add-questions/                     → AddQuestion (API)
├── /                                       → game.urls
│   ├── /tester/                            → pageChecker
│   ├── /                                   → MainPage
│   ├── /about/                             → About
│   ├── /leaderboard/                       → Leaderboard
│   ├── /scores/                            → ScoreBoard
│   ├── /game/<session>/rules/              → Rules
│   ├── /game/<session>/question/<level>/   → QuestionInGame
│   └── /game/<session>/question/<level>/<status>/  → BetweenQuestion
└── /auth/                                  → auth.urls
    ├── /login/                             → login()
    ├── /logout/                            → logout()
    ├── /register/                          → register()
    ├── /admin-login/                       → adminlogin()
    └── /admin-logout/                      → adminlogout()
```

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | >=5.1.2 | Web framework |
| djangorestframework | >=3.14.0 | REST API layer |
| django-configurations | >=2.5.1 | Env-based config classes |
| django-crispy-forms | >=2.0 | Form rendering |
| crispy-bootstrap5 | >=0.7 | Bootstrap 5 integration |
| django-tailwind | >=3.8.0 | Tailwind CSS integration |
| django-browser-reload | >=1.12.0 | Live reload (dev) |
| dj-database-url | >=2.2.0 | Database URL parsing |
| aiohttp | >=3.11.11 | Async HTTP client (question fetch) |
| requests | >=2.31.0 | HTTP library |

## Authentication

- Web views: Django session cookies
- API endpoints: DRF Token authentication (`rest_framework.authtoken`)
- `LOGIN_REDIRECT_URL = "mainpage"`
- `LOGIN_URL = "login"`

## Documentation

- [CONTRIB.md](../CONTRIB.md) — developer setup and workflow
- [RUNBOOK.md](../RUNBOOK.md) — deployment and operations
- [game.md](game.md) — game app codemap
- [auth.md](auth.md) — auth app codemap
- [adminpanel.md](adminpanel.md) — admin panel codemap
- [database.md](database.md) — all models and relationships
