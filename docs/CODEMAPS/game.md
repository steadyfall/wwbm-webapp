# Game App Codemap

**Last Updated:** 2026-02-12
**App:** `game/`
**Entry Point:** `game/urls.py`

## Architecture

```
User Authentication (Django Auth)
    ↓
MainPage (session creation on POST)
    ↓
Rules Page (T&C agreement) → Session object created
    ↓
QuestionInGame (game loop)
    ├── Lifelines System (fifty50, audiencePoll, expertAnswer)
    ├── Question Selection (difficulty-based by level)
    └── Answer Validation
    ↓
BetweenQuestion (result page)
    ├── Correct → Next Level
    ├── Wrong   → Game Over
    └── Quit    → Game Over
    ↓
Leaderboard / ScoreBoard
```

## Models

| Model | Key Fields | Relationships |
|-------|-----------|---------------|
| `Lifeline` | name, description, date_created | M2M ← Session (left_lifelines, used_lifelines) |
| `Level` | level_number (-1–16), money | FK ← Session (current_level, prev_level) |
| `Category` | name, date_created | M2M ← Question (falls_under) |
| `Option` | text, date_added, hits | FK ← Question (correct_option); M2M ← Question (incorrect_options); M2M → User (through ChosenOption) |
| `ChosenOption` | user, option, date_chosen | Through table: User → Option selection history |
| `Question` | text, difficulty, question_type, date_added | FK → User (who_added), Option (correct_option); M2M → Category, Option, User (asked_to) |
| `Session` | session_id (8-char), score, gameOver, agreedToRules | FK → User, Level; M2M → Lifeline, Question |
| `QuestionOrder` | question, session, date_chosen | Through table: tracks question order per session |

## Views

| View | Type | URL Name | Purpose |
|------|------|----------|---------|
| `MainPage` | CBV | `mainpage` | Game entry; creates new session on POST |
| `About` | CBV | `about` | Game rules and lifeline info |
| `Rules` | CBV (LoginRequired) | `rules` | T&C agreement; validates session ownership |
| `QuestionInGame` | CBV (LoginRequired) | `question` | Main game loop: question display + answer submission |
| `BetweenQuestion` | CBV (LoginRequired) | `statusAfterQn` | Shows correct/incorrect/quit result between levels |
| `Leaderboard` | CBV | `leaderboard` | All-users scores ranked by score (paginated) |
| `ScoreBoard` | CBV (LoginRequired) | `scores` | User-specific session history (paginated) |
| `pageChecker` | Function | `tester` | Dev/test page (renders gameover.html) |

## URL Patterns

| Pattern | Name | View |
|---------|------|------|
| `` | `mainpage` | MainPage |
| `about/` | `about` | About |
| `leaderboard/` | `leaderboard` | Leaderboard |
| `scores/` | `scores` | ScoreBoard |
| `game/<session>/rules/` | `rules` | Rules |
| `game/<session>/question/<level>/` | `question` | QuestionInGame |
| `game/<session>/question/<level>/<status>/` | `statusAfterQn` | BetweenQuestion |
| `tester/` | `tester` | pageChecker |

## Management Commands

| Command | Purpose |
|---------|---------|
| `createlevels` | Initialise 17 levels with prize money ($0 → $1 M) |
| `createlifelines` | Initialise 3 lifelines (Fifty-50, Audience Poll, Expert Answer) |
| `createcategories` | Fetch trivia categories from OpenTriviaDB API |
| `fetchqns` | Fetch questions from OpenTriviaDB and write to JSON |
| `extractoptions` | Parse answer options from fetched JSON |
| `addquestions` | Load parsed questions + options into the database |

**Seed sequence:**
```
createlevels → createlifelines → createcategories → fetchqns → extractoptions → addquestions
```

## Lifelines

Defined in `game/lifelines.py`. Each lifeline calls `general_procedure()` which:
1. Adds the question to `session.lifeline_qns`
2. Moves the lifeline from `session.left_lifelines` → `session.used_lifelines`

| Lifeline | Function | Effect |
|----------|----------|--------|
| Fifty-50 | `fifty50(question_id, session_id)` | Eliminates one random wrong option; returns 2 options (correct + 1 wrong) |
| Audience Poll | `audiencePoll(question_id, session_id)` | Correct answer gets 50–100 %; remaining % split across wrong options |
| Expert Answer | `expertAnswer(question_id, session_id)` | Reveals correct answer text directly |

**Name → ID mapping** (`mappedLifelines`): `{"Fifty-50": 2, "Audience Poll": 3, "Expert Answer": 4}`

## Custom Template Tags

Registered in `game/templatetags/utility.py`:

| Filter | Purpose |
|--------|---------|
| `slicer(value, arg)` | `value[arg]` — slice string/list at index |
| `titLe(value)` | Title-case a string |
| `getListFromQueryDict(qd, key)` | Extract multiple values for a key from a QueryDict |
| `querysetToPrimaryKey(qs)` | Return list of PKs from a queryset |
| `user_check(ct)` | True if content_type refers to the User model |
| `obj_exists(ct)` | True if the object referenced by content_type exists |
| `model_name(ct)` | Title-cased model name from a content_type |
| `multiply(value, arg)` | `value * arg` |

## Data Flow

### Gameplay
```
POST /  (startPlay=yes)
  → Session.get_unused_sessionId() → create Session + set left_lifelines
  → redirect rules?session=<id>

POST /game/<session>/rules/  (agreed=yes)
  → current_level=1, prev_level=-1, agreedToRules=True
  → redirect question?session=<id>&level=1

GET /game/<session>/question/<level>/
  → Session.set_question() → Session.get_next_question() (difficulty by level)
  → render question.html (4 shuffled options)

POST /game/<session>/question/<level>/  (userAnswer=<text>)
  → Option.hits.add(user)           ← track selection
  → Correct: score += level.money, level += 1, correct_qns.add(question)
  → Wrong:   gameOver=True, wrong_qn=question, score //= 100
  → redirect statusAfterQn
```

### Lifeline Usage
```
POST lifelineSubmit=yes, lifeline=<name>
  → look up lifeline in mappedLifelines
  → call fifty50 / audiencePoll / expertAnswer
  → general_procedure(): update lifeline_qns, left_lifelines, used_lifelines
  → re-render question.html with modified options/message
```

### Leaderboard
```
GET /leaderboard/
  → Session.objects.order_by("-score", "-date_created")
  → Paginator(sessions, 12)
  → render leaderboard.html
```

## Related Apps

- [auth.md](auth.md) — user authentication
- [adminpanel.md](adminpanel.md) — CRUD management of game models
- [database.md](database.md) — full model schema
