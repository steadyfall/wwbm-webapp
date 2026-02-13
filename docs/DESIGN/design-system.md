# Design System

**Last Updated:** 2026-02-12
**Styling:** Tailwind CSS (django-tailwind) + `static/css/`
**Forms:** django-crispy-forms + crispy-bootstrap5

## Colour Palette

| Role | Tailwind Class | Context |
|------|---------------|---------|
| Page background | `bg-black` | Global (`base.html` body) |
| Primary text | `text-white` | Body text, headings |
| Accent green | `text-emerald-500/600` | Buttons, hover states, success messages |
| Error red | `bg-[#ff7792]` | Game over / wrong answer banner |
| Success green | `bg-[#38fa5f]` | Correct answer banner |
| Info blue | `bg-blue-700` | Django info messages |
| Warning yellow | `bg-yellow-700` | Django warning messages |
| Debug gray | `bg-gray-700` | Django debug messages |
| Default neutral | `bg-neutral-700` | Untagged Django messages |
| Input background | `bg-gray-800` (`#222121`) | Form fields |
| Gradient purple | `bg-gradient-to-r from-[#AF40FF] to-[#5B42F3]` | CTA buttons |
| Question box | `bg-blue-900` | Question text container |
| Option buttons | `bg-blue-800` | Answer option buttons |
| Option hover | `bg-blue-700` | Hover state on options |
| Option labels | `text-cyan-400` | A / B / C / D labels |
| Night sky | (background image) | `static/img/nightsky.jpg` |

## Django Message Banner Colour Map

Defined in `base.html`:

| Tag | Tailwind Class |
|-----|---------------|
| `debug` | `bg-gray-700` |
| `info` | `bg-blue-700` |
| `success` | `bg-green-700` |
| `warning` | `bg-yellow-700` |
| `error` | `bg-red-700` |
| *(default)* | `bg-neutral-700` |

Banner wrapper: `mx-5 my-2 md:mx-auto md:w-[50rem] p-4 rounded flex justify-between items-center text-white`

## Typography

| Font | Source | Usage |
|------|--------|-------|
| Montserrat | Google Fonts | `.font-sans`, primary body text |
| Open Sans | Google Fonts | Auth form labels / placeholders |
| Manrope | Google Fonts | CTA buttons |
| Inter | Bootstrap/Tabler | Admin panel |

### Sizes

| Class | Context |
|-------|---------|
| `text-4xl` | Page headings (About, Leaderboard) |
| `text-3xl` | Main page greeting |
| `text-2xl` | Question text |
| `text-lg` | Option buttons, game info |
| `text-sm` | Nav links, form helpers |
| `text-xs` | Fine print |

## Layout Conventions

| Pattern | Classes | Usage |
|---------|---------|-------|
| Page container | `w-full max-w-4xl mx-auto p-4` | Game pages |
| Blur overlay | `.blur-bg` (`backdrop-filter: blur(15px)`) | Navbar, footer |
| Option grid | `grid grid-cols-1 sm:grid-cols-2 gap-4` | Answer options |
| Flex row | `flex flex-row justify-between items-center` | Horizontal layouts |
| Modal | `fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50` | Lifeline dialog |
| Message banner | `mx-5 my-2 md:mx-auto md:w-[50rem] p-4 rounded` | System messages |
| Flickering grid | `#smooth-grid` (fixed, full viewport) | Animated background (`flickeringGrid.js`) |

## Form Conventions

- Rendered with `crispy_forms` using the `bootstrap5` pack
- Input background: `#222121`, white text, placeholder colour `#c9b0f5` italic
- Validation icons injected via `templates/authentication/icons/` partials (right.png / wrong.png)
- Submit buttons styled via crispy `FormHelper`

### Button Styles

| Class | Purpose |
|-------|---------|
| `.button-64` | Primary CTA gradient button |
| `.signinButton` | Login form submit |
| `.registerButton` | Register form submit |
| `.signBackInButton` | Secondary auth button |

## Animations & Effects

| Effect | Implementation | Usage |
|--------|---------------|-------|
| Blur glass | CSS `backdrop-filter: blur(15px)` | Navbar, footer |
| Fade in | `@keyframes fadein` (3 s linear) | Element entry |
| Confetti | `confetti-fall` + `confetti.js` | Victory screen |
| Hover transition | `transition-colors` | Buttons |
| Grid animation | `flickeringGrid.js` | Background (all pages) |

## Responsive Breakpoints

| Prefix | Min-width | Key pattern |
|--------|-----------|-------------|
| *(none)* | 0 | Mobile first |
| `sm:` | 640 px | `grid-cols-1 sm:grid-cols-2` |
| `md:` | 768 px | `mx-5 md:mx-auto` |
| `lg:` | 1024 px | Extended layouts |

## Admin Panel Design

- **Framework:** Tabler 1.0.0-beta17 (Bootstrap-based)
- **Theme:** Dark sidebar + white content area
- **Components:** Navbar, sidebar nav (Apps ▸ Lifelines / Categories / Options / Questions / Sessions; Logs; API ▸ Token / Docs)
