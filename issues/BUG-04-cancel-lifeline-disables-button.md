# Cancel Lifeline Modal Permanently Disables Lifeline Button

## Summary
Clicking "Cancel" in the lifeline modal permanently disables the "Use Lifeline" button for the rest of the game session, losing all remaining lifelines without using any.

## Motivation
```js
// Broken (timer.js:108-111):
$('#closeLifeline').on("click", function () {
    $('#lifelineButton').attr('disabled', true);  // wrong: fires on Cancel too
    pause();
});
```

The cancel handler (`#closeLifeline`) permanently disables `#lifelineButton`. This means any player who opens the lifeline modal and changes their mind loses access to all lifelines immediately. The disable should only happen after a lifeline is actually submitted.

## Scope
**Project:** Platform (Frontend)

- Remove `$('#lifelineButton').attr('disabled', true)` from the `#closeLifeline` click handler in `timer.js:109`
- Verify the "Use Lifeline" button remains enabled after cancelling the modal
- Verify the button becomes disabled after actually using a lifeline (which is handled server-side via `{% if usedLifelineRecently %}disabled{% endif %}` in the template)
- The `pause()` call should remain — the timer should still unpause/resume when the modal is closed

## Acceptance Criteria
- Open lifeline modal → click Cancel → "Use Lifeline" button remains enabled
- Open lifeline modal → select lifeline → click "Use Lifeline" → button disabled on next page load
- Timer pauses when modal opens, resumes when modal closes (Cancel or Submit)

## Tests
- E2E: open modal → cancel → lifeline button is still enabled
- E2E: use a lifeline → subsequent question page shows lifeline button disabled
