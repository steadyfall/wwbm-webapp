# Design System Consolidation — Unify to Tailwind CSS

## Summary
Three completely different CSS frameworks and visual themes are used across the three major surfaces of the app. A user logging in experiences a dark Bootstrap starfield, then a Tailwind animated game grid, then a white Bootstrap admin panel — with different fonts, colour systems, and component patterns on each surface. There are no shared design tokens.

## Motivation
- **Brand inconsistency**: Login page uses Montserrat/Manrope/Open Sans; game uses Tailwind defaults; admin uses system font.
- **Maintenance cost**: A colour or typography change must be made in three separate places (Bootstrap variables, inline Tailwind classes, `auth.css` hardcoded values).
- **Auth page mobile collapse**: `signin.html:49` has `style="width:25%"` — renders ~50px wide on mobile. This is a direct result of the Bootstrap-era layout not being replaced when the rest of the app moved to Tailwind.
- **Dead CSS**: `base.css` still contains Bootstrap-era utility classes (`.blurr`, `.unblurr`, `.button-64`, `.bttn`) alongside Tailwind classes. `auth.css` has magic layout classes (`.ml-25percent`, `.ml-27percent`, `.ml-32percent`).

## Scope
**Project:** Platform (Frontend)

### Phase 1 — Auth pages (highest priority, simplest templates)
- Migrate `templates/authentication/signin.html` from Bootstrap 5 + inline styles to Tailwind
- Migrate `templates/authentication/register.html` from Bootstrap 5 + inline styles to Tailwind
- Remove `static/css/auth.css` magic layout classes; replace with Tailwind responsive classes
- Fix mobile collapse: replace `style="width:25%"` with responsive Tailwind classes (e.g. `w-full max-w-sm mx-auto`)
- Combine three separate Google Fonts `<link>` requests into one combined URL
- Remove the footer JS on auth pages that crashes because `<footer>` doesn't exist (`signin.html:14-27`)

### Phase 2 — Base template cleanup
- Remove duplicate jQuery load from `tailwind_theme/templates/base.html` (keep 3.7.1 only)
- Remove dead Bootstrap-era CSS classes from `static/css/base.css`
- Define Tailwind design tokens in `tailwind_theme/static_src/tailwind.config.js` `extend` block (brand colours, font families) so colour changes require one edit

### Phase 3 — Admin panel (lower priority)
- Assess whether the custom Bootstrap admin panel should be migrated to Tailwind or extended from Django admin
- (See also CODE-QUALITY notes on `adminpanel/views.py` 985-line file)

## Acceptance Criteria
- Phase 1: Auth pages render correctly on mobile (390px width) with no horizontal scroll
- Phase 1: No `auth.css` magic layout classes remain
- Phase 1: Single combined Google Fonts URL request per page
- Phase 2: jQuery loaded exactly once per page (3.7.1)
- Phase 2: `tailwind.config.js` `extend` block has at least brand primary and accent colours defined
- Phase 3: Decision documented in issue comment (migrate vs extend-Django-admin)

## Tests
- Visual regression test (or Playwright screenshot) for auth pages at 390px and 1280px widths
- JS console error check: no `TypeError` on auth page load

## Notes
The footer JS crash (`signin.html:14-27`) is a quick fix independent of the migration — it can be fixed in Phase 1 or separately as a hotfix (see BUG-06 in the existing frontend review).

`tailwind.config.js:36` currently scans `../../**/*.js` which includes `node_modules/` — fix this scope issue in Phase 2 to reduce Tailwind build time.
