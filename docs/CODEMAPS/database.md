# Database Codemap

**Last Updated:** 2026-02-12
**ORM:** Django ORM
**Default PK:** `BigAutoField`

## Entity Relationship Overview

```
User (django.contrib.auth.User)
  ├── 1→N  Session         (session_user FK)
  ├── 1→N  Question        (who_added FK)
  ├── M2M  Option.hits     (through ChosenOption)
  └── M2M  Question.asked_to

Session
  ├── FK→  User            (session_user)
  ├── FK→  Level           (prev_level, current_level)
  ├── FK→  Question        (current_question, wrong_qn)
  ├── M2M→ Question        (questions_asked, through QuestionOrder)
  ├── M2M→ Question        (correct_qns)
  ├── M2M→ Question        (lifeline_qns)
  └── M2M→ Lifeline        (left_lifelines, used_lifelines)

Question
  ├── FK→  User            (who_added)
  ├── M2M→ Category        (falls_under)
  ├── FK→  Option          (correct_option)
  └── M2M→ Option          (incorrect_options)

Option
  └── M2M→ User            (hits, through ChosenOption)

ChosenOption  [through: Option.hits]
  ├── FK→  User
  └── FK→  Option

QuestionOrder  [through: Session.questions_asked]
  ├── FK→  Question
  └── FK→  Session
```

## Models

### Lifeline

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `date_created` | DateTimeField | `default=timezone.now` |
| `name` | CharField | `max_length=81` |
| `description` | TextField | `max_length=1000`, not null |

**Relationships:** M2M ← Session (`left_lifelines`, `used_lifelines`)

---

### Level

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `level_number` | IntegerField | `min=-1`, `max=16` |
| `money` | IntegerField | `min=0`, `max=10_000_000` |

**Relationships:** FK ← Session (`prev_level`, `current_level`)

**Methods:** `get_default_pk()`, `print_money()`

---

### Category

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `date_created` | DateTimeField | `default=timezone.now` |
| `name` | CharField | `max_length=81` |

**Relationships:** M2M ← Question (`falls_under`)

**Methods:** `get_default_pk()` — gets/creates `"None"` category

---

### Option

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `date_added` | DateTimeField | `default=timezone.now` |
| `text` | CharField | `max_length=250` |
| `hits` | ManyToManyField | User, through=`ChosenOption` |

**Relationships:** FK ← Question (`correct_option`), M2M ← Question (`incorrect_options`)

**Methods:** `get_default_pk()` — gets/creates `"None"` option

---

### ChosenOption *(through)*

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `user` | ForeignKey | User, `on_delete=CASCADE` |
| `option` | ForeignKey | Option, `on_delete=CASCADE` |
| `date_chosen` | DateTimeField | `default=timezone.now` |

---

### Question

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `who_added` | ForeignKey | User, `on_delete=SET_DEFAULT`, default=sentinel |
| `date_added` | DateTimeField | `default=timezone.now` |
| `falls_under` | ManyToManyField | Category |
| `text` | TextField | `max_length=666`, not null |
| `correct_option` | ForeignKey | Option, `on_delete=SET_DEFAULT`, default=placeholder |
| `incorrect_options` | ManyToManyField | Option |
| `question_type` | CharField | choices: `MULTIPLE` \| `TRUEFALSE`, default=`MULTIPLE` |
| `difficulty` | CharField | choices: `UNASSIGNED` \| `EASY` \| `MEDIUM` \| `HARD`, default=`UNASSIGNED` |
| `asked_to` | ManyToManyField | User |

**Meta:** `ordering = ["-date_added"]`

**Methods:** `get_default_pk()`

---

### Session

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `session_id` | CharField | `max_length=8`, not PK, 8-char random ID |
| `date_created` | DateTimeField | `default=timezone.now` |
| `session_user` | ForeignKey | User, `on_delete=SET(sentinel)` |
| `prev_level` | ForeignKey | Level, `on_delete=SET_DEFAULT` |
| `current_level` | ForeignKey | Level, `on_delete=SET_DEFAULT` |
| `agreedToRules` | BooleanField | `default=False` |
| `gameOver` | BooleanField | `default=False` |
| `score` | IntegerField | `min=0`, `max=100_000_000`, `default=0` |
| `current_question` | ForeignKey | Question, `on_delete=SET_DEFAULT` |
| `questions_asked` | ManyToManyField | Question, through=`QuestionOrder` |
| `correct_qns` | ManyToManyField | Question |
| `wrong_qn` | ForeignKey | Question, `on_delete=SET_DEFAULT` |
| `lifeline_qns` | ManyToManyField | Question |
| `left_lifelines` | ManyToManyField | Lifeline |
| `used_lifelines` | ManyToManyField | Lifeline |

**Meta:** `ordering = ["-date_created"]`

**Methods:** `get_unused_sessionId()`, `get_next_question()`, `set_question()`

---

### QuestionOrder *(through)*

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | BigAutoField | PK, auto |
| `question` | ForeignKey | Question, `on_delete=CASCADE` |
| `session` | ForeignKey | Session, `on_delete=CASCADE` |
| `date_chosen` | DateTimeField | `default=timezone.now` |

---

## Sentinel User

```python
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="deleted")[0].pk
```

A `"deleted"` placeholder user is created to prevent cascade deletion of Sessions and Questions when a real user is removed. Used as `SET_DEFAULT` target for `Session.session_user` and `Question.who_added`.

## Related Apps

- [INDEX.md](INDEX.md) — architecture overview
- [game.md](game.md) — game views and data flow
- [adminpanel.md](adminpanel.md) — CRUD operations on these models
