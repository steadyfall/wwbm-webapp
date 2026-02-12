# Answer Option Buttons Submit Empty Form Instead of Selecting Answer

## Summary
The A/B/C/D answer card buttons are `<button>` elements with no `type="button"` attribute inside a `<form>`. They default to `type="submit"`, so clicking any card submits the form with no radio selected, triggering an error redirect. The visual cards and the actual radio inputs are two separate disconnected UX elements.

## Motivation
```html
<!-- question.html:95-113 — all four have this pattern: -->
<button class="bg-blue-800 hover:bg-blue-700 ...">
    <span class="text-cyan-400 font-bold mr-2">A.</span> {{ option1 }}
</button>
<!-- ...then separately, far below the cards: -->
<input type="radio" name="userAnswer" id="option_a" value="{{ option1 }}">
```

A user naturally clicks the card. The browser submits the form without a `userAnswer` value selected. The server returns "Choose an option!" and redirects. On reload, `timer.js` reads `NaN` from the timer DOM element and displays "Time Left: NaNs" (cascade bug).

The fix merges the two UX elements: clicking a card should visually select it AND set the corresponding radio input.

## Scope
**Project:** Platform (Frontend)

- Add `type="button"` to all four `<button>` answer cards in `question.html:95-113`
- Add a JS click handler that, when a card is clicked:
  1. Checks the corresponding radio input (`#option_a` for A, etc.)
  2. Adds a visual "selected" style to the clicked card (and removes it from others)
- The existing radio inputs below the fold can remain (for form submission) but should update in sync with card clicks
- Remove the separate "Your option is: ○A ○B ○C ○D" radio section if it becomes redundant after the cards handle selection visually
- Test that the Submit button correctly sends `userAnswer` after card selection

## Acceptance Criteria
- Clicking a card does NOT submit the form
- Clicking a card checks the corresponding radio input
- Clicking Submit after selecting a card sends the correct `userAnswer` value
- The "Time Left: NaNs" timer display does not occur
- Only one card can be selected at a time (clicking B deselects A)

## Tests
- E2E: click card A → submit → server receives `userAnswer` matching option A text
- E2E: click card B then card C → submit → server receives option C
- Unit JS: card click handler checks correct radio input
- JS console: no errors during normal answer flow

## Notes
This fix also resolves the cascade NaN timer bug (timer.js reads NaN after the redirect-on-empty-submit cycle).
