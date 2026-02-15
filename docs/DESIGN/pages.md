# Client-Facing Pages

**Last Updated:** 2026-02-12

## Template Hierarchy

```
templates/base.html                          ← global layout (dark theme, Tailwind)
├── templates/navbar.html                    ← header: logo, username, auth links
├── templates/footer.html                    ← footer: nav links, copyright
├── templates/mainPage.html                  ← game entry
├── templates/about.html                     ← about page
├── templates/rules.html                     ← T&C (includes gamerules.html)
│   └── templates/gamerules.html             ← reusable rule cards
├── templates/question.html                  ← game question + lifeline modal
│   ├── templates/lifelineSVG/fifty50.html
│   ├── templates/lifelineSVG/audiencePoll.html
│   ├── templates/lifelineSVG/expertAnswer.html
│   ├── templates/optionSVG/optionA.html
│   ├── templates/optionSVG/optionB.html
│   ├── templates/optionSVG/optionC.html
│   └── templates/optionSVG/optionD.html
├── templates/gameover.html                  ← between-question result
├── templates/leaderboard.html               ← all-users scores
└── templates/scoreboard.html               ← user session history

templates/authentication/                    ← standalone auth pages (no base.html)
├── signin.html
├── register.html
├── signout.html
├── adminlogin.html
├── adminlogout.html
└── icons/
    ├── userCircle.html
    ├── password.html
    ├── at.html
    └── squareAsterick.html

templates/adminpanel/                        ← admin-only (extends adminpanel/base.html)
├── base.html                               ← Tabler framework layout
├── index.html
├── listdb.html
├── listlog.html
├── objectCreate.html
├── objectView.html
├── objectDelete.html
├── objectHistory.html
├── apiaccess.html
├── apidocs.html
└── formTemplates/
    ├── question.html
    ├── option.html
    ├── lifeline.html
    └── category.html
```

## Page Inventory

| Page | Template | URL Name | Auth | Purpose | Key UI Elements |
|------|----------|----------|------|---------|-----------------|
| Main Page | `mainPage.html` | `mainpage` | No | Game entry | Logo, "Play" button |
| About | `about.html` | `about` | No | Project info | Info cards |
| Rules | `rules.html` | `rules` | Yes | T&C agreement | Rule cards, Start button |
| Question | `question.html` | `question` | Yes | Active game loop | Timer, question text, 2×2 option grid, lifeline modal |
| Between Question | `gameover.html` | `statusAfterQn` | Yes | Correct/wrong result | Colour banner (green/red), confetti (correct) |
| Leaderboard | `leaderboard.html` | `leaderboard` | No | All-time high scores | Paginated table (12/page), score, user, date |
| ScoreBoard | `scoreboard.html` | `scores` | Yes | Personal session history | Paginated session list |
| Login | `authentication/signin.html` | `login` | No | User login | Username, password, submit |
| Register | `authentication/register.html` | `register` | No | New user registration | Username, email, password ×2 |
| Logout | `authentication/signout.html` | `logout` | Yes | Confirm logout | Message + redirect |
| Admin Login | `authentication/adminlogin.html` | `adminLogin` | No | Admin login | Username, password |
| Admin Logout | `authentication/adminlogout.html` | `adminLogout` | Yes (admin) | Admin logout | Message + redirect |
| Admin Home | `adminpanel/index.html` | `adminMainPage` | Superuser | Dashboard + stats | Sidebar nav, charts, counts |
| DB List | `adminpanel/listdb.html` | `adminListDB` | Superuser | List model records | Table, CRUD links, pagination |
| DB Object | `adminpanel/objectView.html` | `adminDBObject` | Superuser | Edit object | Form, update/delete buttons |
| DB Create | `adminpanel/objectCreate.html` | `adminDBObjectCreate` | Superuser | Create object | Form, submit button |
| DB Delete | `adminpanel/objectDelete.html` | `adminDBObjectDelete` | Superuser | Confirm deletion | Confirm button |
| DB History | `adminpanel/objectHistory.html` | `adminDBObjectHistory` | Superuser | Change audit log | Timeline of changes |
| Logs | `adminpanel/listlog.html` | `adminListLogs` | Superuser | System audit logs | Paginated log table |
| API Access | `adminpanel/apiaccess.html` | `APIAccess` | Superuser | Manage API tokens | Token display, regenerate |
| API Docs | `adminpanel/apidocs.html` | `APIDocs` | Superuser | API reference | Endpoint specs, examples |

## URL → View → Template Map

### Game (`/`)

| URL | View | Template |
|-----|------|----------|
| `/` | `MainPage` | `mainPage.html` |
| `/about/` | `About` | `about.html` |
| `/leaderboard/` | `Leaderboard` | `leaderboard.html` |
| `/scores/` | `ScoreBoard` | `scoreboard.html` |
| `/game/<s>/rules/` | `Rules` | `rules.html` |
| `/game/<s>/question/<l>/` | `QuestionInGame` | `question.html` |
| `/game/<s>/question/<l>/<status>/` | `BetweenQuestion` | `gameover.html` |

### Auth (`/auth/`)

| URL | View | Template |
|-----|------|----------|
| `/auth/login/` | `login()` | `authentication/signin.html` |
| `/auth/logout/` | `logout()` | `authentication/signout.html` |
| `/auth/register/` | `register()` | `authentication/register.html` |
| `/auth/admin-login/` | `adminlogin()` | `authentication/adminlogin.html` |
| `/auth/admin-logout/` | `adminlogout()` | `authentication/adminlogout.html` |

### Admin (`/admin/`)

| URL | View | Template |
|-----|------|----------|
| `/admin/` | `AdminMainPage` | `adminpanel/index.html` |
| `/admin/apps/<db>/` | `AdminListDB` | `adminpanel/listdb.html` |
| `/admin/apps/<db>/object/<pk>/` | `AdminDBObjectChange` | `adminpanel/objectView.html` |
| `/admin/apps/<db>/create/` | `AdminDBObjectCreate` | `adminpanel/objectCreate.html` |
| `/admin/apps/<db>/object/<pk>/delete/` | `AdminDBObjectDelete` | `adminpanel/objectDelete.html` |
| `/admin/apps/<db>/object/<pk>/history/` | `AdminDBObjectHistory` | `adminpanel/objectHistory.html` |
| `/admin/logs/` | `ShowLogDB` | `adminpanel/listlog.html` |
| `/admin/api-access/` | `APIAccess` | `adminpanel/apiaccess.html` |
| `/admin/api-docs/` | `APIDocs` | `adminpanel/apidocs.html` |
