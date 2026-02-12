# Replace Wildcard Imports with Explicit Imports

## Summary
Three files use `from module import *`, pulling unknown names into scope and hiding dependencies. This makes it impossible to tell where a name comes from without running the code, breaks IDEs and static analysis, and makes refactoring unsafe.

## Motivation
```python
# game/views.py:9-10
from game.models import *    # imports: Lifeline, Level, Category, Option, ChosenOption,
                             # Question, Session, QuestionOrder, random, User, timezone...
from .lifelines import *     # imports: FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER, mappedLifelines
                             # + everything game.models imported (double import)

# auth/views.py:7
from .validate import *      # imports: usernameValidator, emailValidator, passwordValidator, confirmPassword, re
```

Specifically:
- `random` is imported into `game/views.py` namespace via `game.models` wildcard — any `random.X` call in views is using the module imported from models, not a clean import
- `re` is imported into `auth/views.py` namespace via `validate` wildcard

## Scope
**Project:** Backend

- Replace `from game.models import *` in `game/views.py` with explicit imports of every name actually used
- Replace `from .lifelines import *` in `game/views.py` with explicit imports (`FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER, mappedLifelines, expertAnswer, fifty50, audiencePoll`)
- Replace `from .validate import *` in `auth/views.py` with explicit imports (`usernameValidator, emailValidator, passwordValidator, confirmPassword`)
- Add explicit `import random` to `game/views.py` (currently pulled in indirectly via models wildcard)

## Acceptance Criteria
- No `import *` in `game/views.py` or `auth/views.py`
- All names used in each file are explicitly imported
- `python manage.py check` and Ruff linting pass

## Tests
- N/A — this is a pure refactor; existing behaviour is unchanged
- Ruff rule `F401` (unused imports) and `F403` (star imports) should be enabled and pass
