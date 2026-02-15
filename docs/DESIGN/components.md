# UI Components & Assets

**Last Updated:** 2026-02-12

## Shared Partials

| Partial | Path | Used In |
|---------|------|---------|
| Navbar | `templates/navbar.html` | All `base.html` pages |
| Footer | `templates/footer.html` | All `base.html` pages |
| Game Rules | `templates/gamerules.html` | `rules.html` |
| Lifeline — Fifty-50 | `templates/lifelineSVG/fifty50.html` | `question.html` |
| Lifeline — Audience Poll | `templates/lifelineSVG/audiencePoll.html` | `question.html` |
| Lifeline — Expert Answer | `templates/lifelineSVG/expertAnswer.html` | `question.html` |
| Option label A | `templates/optionSVG/optionA.html` | `question.html` |
| Option label B | `templates/optionSVG/optionB.html` | `question.html` |
| Option label C | `templates/optionSVG/optionC.html` | `question.html` |
| Option label D | `templates/optionSVG/optionD.html` | `question.html` |
| Icon — user circle | `templates/authentication/icons/userCircle.html` | `signin.html`, `register.html` |
| Icon — password | `templates/authentication/icons/password.html` | `register.html` |
| Icon — @ | `templates/authentication/icons/at.html` | `register.html` |
| Icon — asterisk | `templates/authentication/icons/squareAsterick.html` | `signin.html`, `register.html` |
| Icon — check | `templates/icons/check.html` | (available for use) |
| Icon — cross | `templates/icons/cross.html` | (available for use) |
| Icon — plus | `templates/icons/plus.html` | (available for use) |

## CSS Files

| File | Purpose | Key Classes |
|------|---------|-------------|
| `static/css/base.css` | Global layout, game UI, buttons | `.button-64`, `.bttn`, `.question`, `.options`, `.logo-div`, `.footer-nav-link`, `.blur-bg` |
| `static/css/auth.css` | Login/register form styling | `.signinButton`, `.registerButton`, `.signBackInButton`, `.valid`, `.invalid` |
| `static/css/confetti.css` | Victory animation | `.confetti`, `.confetti-item`, `@keyframes confetti-fall` |
| `static/css/bannerCorrectQ.css` | Correct answer banner theme | (game-over green state) |
| `static/css/bannerwrongQ.css` | Wrong answer banner theme | (game-over red state) |

## JavaScript Behaviours

| File | Behaviour | Trigger |
|------|-----------|---------|
| `static/js/timer.js` | Countdown timer; auto-submits `#sendAnswer` at 0 s; turns red < 10 s; pauses during lifeline modal | Page load on `question.html` |
| `static/js/confetti.js` | Generates 350 falling confetti pieces (blue, yellow, cyan, orange) for 2–5 s each | Document ready on win `gameover.html` |
| `static/js/flickeringGrid.js` | Animated grid pattern on `#smooth-grid` (fixed, full viewport) | Deferred load, all `base.html` pages |
| `static/js/validator.js` | Real-time field validation (password strength, username rules, email format); visual icons | Input/blur events on `register.html` |
| `static/js/signin.js` | Login form presence validation; error display | Form submit on `signin.html` |
| `static/js/charting.js` | Chart/graph rendering | Leaderboard / admin dashboard |
| `static/js/adminpanelForms/` | Dynamic admin CRUD form handling | Admin pages |

## Image Assets

| File | Usage |
|------|-------|
| `static/img/wwbmicon.ico` | Favicon + navbar brand logo |
| `static/img/nightsky.jpg` | Main page background |
| `static/img/qn2.png` | Question container background |
| `static/img/options.png` | Option buttons background |
| `static/img/right.png` | Valid field indicator (auth forms) |
| `static/img/wrong.png` | Invalid field indicator (auth forms) |
| `static/img/wwbm.jpg` | Game-related imagery |
| `static/img/wwbm2.jpg` | Game-related imagery |
| `static/img/cURL_API_usage.png` | API docs screenshot |
| `static/img/Python_API_usage.png` | API docs screenshot |
| `static/img/levels.png` | Prize levels reference screenshot |

## Audio

| File | Usage |
|------|-------|
| `static/audio/introduction.mp3` | Game introduction audio |

## External CDN Dependencies

| Library | Purpose | Used In |
|---------|---------|---------|
| Tailwind CSS (django-tailwind) | Primary CSS framework | All `base.html` pages |
| Bootstrap 5.3.0 | Admin panel theme base | `adminpanel/` |
| Tabler 1.0.0-beta17 | Admin panel theme | `adminpanel/base.html` |
| Tom Select | Searchable select dropdowns | Admin forms |
| Flatpickr | Date picker | Admin forms |
| jQuery 3.7.1 | DOM + event handling | Auth pages, base.html |
| Google Fonts | Montserrat, Open Sans, Manrope | All pages |
