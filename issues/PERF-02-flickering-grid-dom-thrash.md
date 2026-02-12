# Low Priority: Replace flickeringGrid.js DOM Mutations with CSS Animation

## Summary
The main page background animation (`flickeringGrid.js`) creates ~2,200 `<div>` elements and mutates all their opacity values every 1,000ms via `setInterval`, causing a full layout/paint cycle once per second.

## Motivation
At 1280×800 resolution, the grid creates approximately 2,200 cells. Each `setInterval` tick modifies `opacity` on a random subset of cells, triggering browser reflow/repaint for all of them. This keeps the main thread busy even when the user is idle on the main page.

## Scope
**Project:** Platform (Frontend) — Low Priority

Two approaches:

**Option A — CSS keyframes (recommended):**
- Generate the grid cells once with JS
- Assign a random `animation-delay` to each cell at init time
- Define a CSS `@keyframes` rule for the flicker
- The browser compositor handles animation without JS involvement after init

**Option B — requestAnimationFrame:**
- Replace `setInterval(checker, 1000)` with `requestAnimationFrame`
- Batch DOM mutations using a `DocumentFragment`
- Provides more control over timing but keeps animation on the main thread

## Acceptance Criteria
- Main page background animation is visually equivalent to the current implementation
- No `setInterval` call for DOM mutations in `flickeringGrid.js`
- Browser DevTools Performance panel shows no layout thrash from the grid after page load

## Tests
- Visual regression: screenshot of main page at 1280×800 is visually equivalent before/after

## Notes
Low priority — this is a cosmetic animation and has no functional impact. Address after critical bugs and performance issues affecting gameplay are resolved.
