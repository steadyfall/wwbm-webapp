<div align="center">

# Trivivo

</div>

"Trivivo" is a website developed by me that aims to test you with 15 questions of varying difficulty and topics, with staggering timeouts. The aim is to score the highest among the quiz-takers!

## Trello
The Trello board is [here](https://linear.app/trivivo/team/TRI/all).


## Project Structure
```text
.
├── adminpanel
├── auth
├── game
├── kbc
├── static
└── templates
```

- `adminpanel` app handles administrator actions of the app, allowing administrators to perform elevated actions such as CRUD operations, changing timeout speeds, etc.
- `auth` app handles authentication of users/admins to various sites.
- `game` app handles the game logic of the app, involving timeouts, progression to the next levels, score/leaderboard handling, etc.
- `kbc` is the project folder (for Django projects).
- `static` holds the staticfiles for the project & apps.
- `templates` holds the templates for all the apps that get rendered when called via the `views.py` in each app.

## Issue Labels

### Quality
| Label | Description |
|---|---|
| `accessibility` | Breaks keyboard or screen reader access |
| `design` | CSS inconsistency, unfinished migration, or design debt |

### Area
| Label | Description |
|---|---|
| `auth` | Authentication or authorization related |
| `backend` | Django / Python / view logic issue |
| `database` | Model, query, migration, or index issue |
| `frontend` | HTML / CSS / JavaScript issue |
| `performance` | Causes excess queries, memory, or latency |

### Type
| Label | Description |
|---|---|
| `bug` | Something is broken or behaving incorrectly |
| `critical` | Crash, data loss, or auth bypass risk |
| `security` | Vulnerability or exploitable behaviour |
| `refactor` | Restructure code without changing behaviour |
| `feature` | New feature or request |

### Dev
| Label | Description |
|---|---|
| `infra` | CI/CD, GitHub Actions, or deployment configs |
| `tests` | Missing, empty, or broken test coverage |
| `docs` | Improvements or additions to documentation |

### Flow
| Label | Description |
|---|---|
| `release` | Marks PRs intended to be merged into main (production) |


### Triage
| Label | Description |
|---|---|
| `duplicate` | This issue or pull request already exists |
| `good first issue` | Good for newcomers |
| `invalid` | This doesn't seem right |
