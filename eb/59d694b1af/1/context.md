# Session Context

## User Prompts

### Prompt 1

Give me a high level frontend code and design review of the project and use typescript-lsp plugin, frontend-design plugin, Playwright MCP and subagents to analyze further.

### Prompt 2

Non-admin credentials - Username: johnDoe | Password: jdvance1 ; Admin credentials - Username: hdave | Password: manuosos1 -- this is for login.

### Prompt 3

<task-notification>
<task-id>a19f640</task-id>
<status>completed</status>
<summary>Agent "Explore project structure" completed</summary>
<result>Perfect! Now I have enough information to provide a comprehensive overview. Let me compile all my findings:

## Comprehensive Project Overview - Trivivo

### 1. PROJECT STRUCTURE

**Directory Layout:**
```
trivivo/
├── adminpanel/          # Admin management app
├── auth/                # Authentication app
├── game/                # C...

### Prompt 4

Encapsulate all of this findings into a Markdown file without losing any detail and doing it in minimum tokens possible + make sure it is very structured for both humans & agents to understand.

### Prompt 5

Clear up files created by Playwright MCP.

### Prompt 6

· `game/views.py:72` — FOREIGN KEY crash on game start · **FIXED**
```python
# Before (hardcoded IDs that didn't match DB records 1,2,3):
new_session.left_lifelines.set([2, 3, 4])
# After:
new_session.left_lifelines.set(Lifeline.objects.values_list("id", flat=True))
```
- **Symptom**: `IntegrityError: FOREIGN KEY constraint failed` on every game start
- **Root cause**: Same hardcoded-ID pattern as BUG-07/BUG-08; a `TODO` comment acknowledged it
- **Status**: Fixed in this review session

### Prompt 7

[Request interrupted by user]

### Prompt 8

Commit this change.

