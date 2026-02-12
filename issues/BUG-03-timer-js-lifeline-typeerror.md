# timer.js — TypeError on Lifeline Confirm Click

## Summary
`timer.js:105` calls `.attr()` on a jQuery Event object instead of an element. Every lifeline confirmation click throws `TypeError: e.attr is not a function`, the confirm button is never disabled, and the timer time is not correctly captured.

## Motivation
```js
// Broken (timer.js:103-106):
$('#confirmLifeline').on("click", function (e) {
    $('#timeLeftAfterLifeline').val(parseInt(timeLeft.textContent));
    e.attr('disabled', true);  // e is the Event, not the element
});

// Fix:
$('#confirmLifeline').on("click", function (e) {
    $('#timeLeftAfterLifeline').val(parseInt(timeLeft.textContent));
    $(this).prop('disabled', true);  // 'this' is the clicked element
});
```

The `.val()` call on line 104 (capturing timer value) likely still executes before the error, but the error prevents the button from being disabled. Re-clicking the confirm button can re-submit the lifeline form.

## Scope
**Project:** Platform (Frontend)

- Fix `e.attr('disabled', true)` → `$(this).prop('disabled', true)` at `timer.js:105`
- Verify the fix by clicking "Use Lifeline" → selecting a lifeline → confirming — button should become disabled and form should submit once

## Acceptance Criteria
- Lifeline confirmation click does not throw a JS error in console
- After confirmation, the confirm button is disabled and cannot be clicked again
- Timer value is correctly captured in the `timeLeftAfterLifeline` hidden input

## Tests
- JS console: zero errors after lifeline confirm click
- E2E: use a lifeline, confirm — button becomes disabled, form POSTs with correct `timeLeftAfterLifeline` value
