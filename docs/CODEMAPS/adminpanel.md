# Admin Panel Codemap

**Last Updated:** 2026-02-12
**App:** `adminpanel/`
**Entry Point:** `adminpanel/urls.py`

## Architecture

```
Browser → kbc/urls.py (admin/ prefix) → adminpanel/urls.py
  → SuperuserRequiredMixin + LoginRequiredMixin
  → views.py / viewsExtra.py
  → game.models (Session, Lifeline, Category, Question, Option)
  → templates/adminpanel/
  → Django LogEntry (audit trail)

REST API layer:
  → GetQuestion  (GET  admin/random-question/)
  → AddQuestion  (POST admin/add-questions/) — TokenAuthentication
```

## Views

| View | Type | URL Name | Purpose | Auth |
|------|------|----------|---------|------|
| `testSite()` | Function | `test` | Debug page | None |
| `AdminMainPage` | CBV | `adminMainPage` | Dashboard with stats & charts | Superuser |
| `AdminListDB` | CBV | `adminListDB` | Paginated list + bulk delete | Superuser |
| `AdminDBObjectCreate` | CBV | `adminDBObjectCreate` | Create new object | Superuser |
| `AdminDBObjectChange` | CBV | `adminDBObject` | View/edit object with change tracking | Superuser |
| `AdminDBObjectDelete` | CBV | `adminDBObjectDelete` | Deletion confirmation | Superuser |
| `AdminDBObjectHistory` | CBV | `adminDBObjectHistory` | Audit log for one object | Superuser |
| `ShowLogDB` | CBV | `adminListLogs` | All system audit logs | Superuser |
| `APIAccess` | CBV | `APIAccess` | Manage API tokens | Superuser |
| `APIDocs` | CBV | `APIDocs` | API documentation | Superuser |
| `GetQuestion` | CBV | `getQuestionAPI` | Return random questions (max 5) | Superuser |
| `AddQuestion` | APIView | `addQuestionAPI` | Bulk add questions via REST API | Token Auth |

## URL Patterns

| Pattern | Name | View | Methods |
|---------|------|------|---------|
| `` | `adminMainPage` | AdminMainPage | GET |
| `test/` | `test` | testSite | GET |
| `apps/<str:db>/` | `adminListDB` | AdminListDB | GET, POST |
| `logs/` | `adminListLogs` | ShowLogDB | GET |
| `apps/<str:db>/object/<pk>/` | `adminDBObject` | AdminDBObjectChange | GET, POST |
| `apps/<str:db>/create/` | `adminDBObjectCreate` | AdminDBObjectCreate | GET, POST |
| `apps/<str:db>/object/<pk>/delete/` | `adminDBObjectDelete` | AdminDBObjectDelete | GET, POST |
| `apps/<str:db>/object/<pk>/history/` | `adminDBObjectHistory` | AdminDBObjectHistory | GET |
| `api-access/` | `APIAccess` | APIAccess | GET |
| `api-docs/` | `APIDocs` | APIDocs | GET |
| `random-question/` | `getQuestionAPI` | GetQuestion | GET |
| `add-questions/` | `addQuestionAPI` | AddQuestion | POST |

## Supported Models

| Model | Create | Edit | Delete | List |
|-------|--------|------|--------|------|
| Session | — | — | Yes | Yes |
| Lifeline | — | Yes | Yes | Yes |
| Category | Yes | Yes | Yes | Yes |
| Question | Yes | Yes | Yes | Yes |
| Option | Yes | Yes | Yes | Yes |

## Forms

| Form | Model | Purpose |
|------|-------|---------|
| `QuestionForm` | Question | Create/edit questions |
| `OptionForm` | Option | Create/edit options |
| `LifelineForm` | Lifeline | Create/edit lifelines |
| `CategoryForm` | Category | Create/edit categories |
| `ModifiedModelForm` | Base | M2M handling + change tracking |

## Serializers

| Serializer | Model | Purpose |
|-----------|-------|---------|
| `QuestionEncoder` | Question | API JSON output: category names, difficulty display, correct/incorrect answers |

## Helper Functions (`viewsExtra.py`)

| Function | Purpose |
|----------|---------|
| `pk_checker()` | Validate pk format (prevents injection) |
| `safe_pk_list_converter()` | Safely convert pk list from POST |
| `safe_object_delete()` | Delete object safely |
| `safe_object_delete_log()` | Delete + write LogEntry |
| `log_addition()` | Log object creation |
| `log_change()` | Log object modification |
| `log_deletion()` | Log object deletion |
| `pretty_change_message()` | Format change message for display |
| `daterange()` | Generate a date range |
| `widget_list_generator()` | Build form widget dict |

## Mixins

| Mixin | Behaviour |
|-------|-----------|
| `SuperuserRequiredMixin` | Redirects non-superusers |
| `LoginRequiredMixin` | Redirects unauthenticated users |

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `PAGINATE_NO` | 12 | Items per page |
| `SITE_NAME` | `"AdminPanel"` | Page title prefix |
| `modelDict` | session, lifeline, category, question, option | Model registry |
| `modelFormDict` | same keys | Form class registry |
| `allowedModelNames` | tuple of modelDict keys | URL param whitelist |

## Data Flow

### Dashboard
```
GET /admin/
  → context_creator() builds:
    last 12 logs, question counts, session counts,
    user counts, category stats, 15-day chart data
  → render adminpanel/index.html
```

### Bulk Delete
```
POST /admin/apps/<db>/
  → validate pk_checker for each id
  → safe_object_delete_log() → LogEntry
  → success message → redirect
```

### Create Object
```
GET  /admin/apps/<db>/create/  → render form
POST /admin/apps/<db>/create/
  → form.save() → log_addition() → redirect detail
```

### Edit Object
```
GET  /admin/apps/<db>/object/<pk>/  → render pre-filled form
POST /admin/apps/<db>/object/<pk>/
  → form.changed_data → save + log_change()
  → redirect list
```

### API Add Questions
```
POST /admin/add-questions/
  Body: [{difficulty, question, correct_answer, incorrect_answers, category}, ...]
  → TokenAuthentication
  → checkQuestion, checkCategory, checkQuestionText, checkDifficulty, checkOption
  → bulk create Question objects
  → updateM2Mfields() (categories + incorrect_options)
  → JSON response
```

## Related Apps

- [auth.md](auth.md) — authentication for admin users
- [game.md](game.md) — source of all managed models
- [database.md](database.md) — all model schemas
