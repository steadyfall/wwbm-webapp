# Unguarded `Option.objects.get()` on User-Submitted Answer

## Summary
`game/views.py:315` calls `Option.objects.get(text=userAnswer)` where `userAnswer` comes directly from `request.POST`. A crafted POST request with a `userAnswer` value that doesn't match any option — or matches an option not belonging to the current question — raises an unhandled exception or allows invalid state writes.

## Motivation
```python
# game/views.py:313-316
if self.request.POST["submitBtn"] == "yes":
    userAnswer = self.request.POST["userAnswer"]
    optionText = sessionObj.current_question.correct_option.text
    option = Option.objects.get(text=userAnswer)  # ← DoesNotExist if tampered
    option.hits.add(sessionObj.session_user)       # ← records a hit for an unrelated option
```

Two issues:
1. If `userAnswer` doesn't match any `Option.text`, `DoesNotExist` is raised → HTTP 500
2. If `userAnswer` matches an option in the DB but not one of the four options for the current question, the hit is still recorded against that unrelated option — logic bypass

## Scope
**Project:** Backend

- Validate `userAnswer` against the current question's actual options (correct + 3 incorrect) before any DB operation
- If `userAnswer` is not one of the current question's options, treat as invalid input → redirect with warning
- This validation makes the subsequent `DoesNotExist` impossible for valid inputs; add try/except as a defensive fallback

## Acceptance Criteria
- Crafted POST with a non-existent `userAnswer` returns a redirect/warning, not HTTP 500
- Crafted POST with an `Option` text that exists in the DB but belongs to a different question is rejected
- Valid `userAnswer` (one of the four current question options) is processed normally

## Tests
- Unit test: POST with `userAnswer` not matching any `Option` → 302 redirect, no 500
- Unit test: POST with valid answer from a different question → rejected
- Unit test: POST with correct answer → session score increases, redirect to next question
- Unit test: POST with incorrect answer → game over, correct score reduction applied
