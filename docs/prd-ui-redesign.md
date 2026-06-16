# PRD: Calculator UI Redesign

## Problem Statement

Users of the math calculator app have a functional but bare-bones interface: a text input, a submit button, and a history table. There is no visual hierarchy, no dark mode, and no way to interact with the calculator without typing — making it friction-heavy and visually unappealing, especially for quick use or on mobile.

## Solution

Redesign the frontend of the math calculator app with a full numeric keypad, dark mode (default), a light mode toggle persisted across sessions, a curated set of suggested-equation preset buttons, and a polished dark-charcoal/indigo visual style. The backend remains unchanged.

## User Stories

1. As a user, I want to see a full numeric keypad (0–9, operators, decimal, clear, equals), so that I can enter equations without typing.
2. As a user, I want to see the equation I'm building on a display area above the keypad, so that I know what I've entered before evaluating.
3. As a user, I want to press `=` to evaluate the equation, so that I control when calculation happens.
4. As a user, I want to press `C` to clear the current display, so that I can start over without refreshing the page.
5. As a user, I want operators (`+`, `-`, `*`, `/`) on the right column of the keypad, so that I can find them where I expect them.
6. As a user, I want digits arranged in standard calculator layout (7-8-9 top, 4-5-6 middle, 1-2-3 bottom, 0 and `.` last row), so that I can use muscle memory.
7. As a user, I want to see preset suggested-equation buttons (e.g. `12 * 3`, `100 / 4`, `7 + 8`, `50 - 13`), so that I can try the app immediately without thinking of an equation.
8. As a user, I want clicking a preset to populate the display and evaluate it immediately, so that presets feel like a one-tap shortcut.
9. As a user, I want the app to open in dark mode by default, so that it looks polished and is easy on the eyes.
10. As a user, I want a toggle to switch between dark and light mode, so that I can use the app in bright environments.
11. As a user, I want my mode preference remembered across page loads via localStorage, so that I don't have to re-toggle every visit.
12. As a user, I want the history table to update immediately after each calculation, so that I can see my result in context.
13. As a user, I want the history displayed most-recent-first, so that my latest result is always at the top.
14. As a user, I want error feedback (e.g. division by zero, incomplete equation) displayed near the keypad, so that I understand why an equation was rejected.
15. As a user, I want the interface to look clean and minimal with consistent spacing and typography, so that the app feels professional.
16. As a user, I want the keypad buttons to have hover and active states, so that the UI feels responsive to my input.
17. As a user, I want the layout to work reasonably on mobile screen widths, so that I can use it on my phone.

## Implementation Decisions

- All changes are **frontend-only** — `app.py`, the Flask routes, the DB schema, and `requirements.txt` are unchanged.
- The HTML/CSS/JS embedded in the `HTML` constant in `app.py` is fully replaced.
- The keypad is a CSS grid — standard calculator arrangement: 7-8-9, 4-5-6, 1-2-3, 0/./= in the digit area; `+`, `-`, `*`, `/`, `C` in the operator column.
- The display area sits above the keypad and renders the equation string as it is built (e.g. `12 *`), then shows the result after `=`.
- Equation evaluation is build-then-evaluate: digits and one operator are accumulated into a string; `=` submits to `POST /calculate`.
- Single-operation constraint is preserved: the keypad enforces `number → operator → number → =` sequencing. A second operator press replaces the first (or starts a new equation after a result).
- Suggested presets are 4–6 hard-coded buttons rendered above or beside the keypad. Clicking a preset populates the full equation string and immediately evaluates it.
- Dark mode uses CSS custom properties (`--bg`, `--surface`, `--text`, `--accent`) toggled by a class on `<body>`. Dark is the default class; toggling swaps to a light-mode class.
- The dark/light preference is read from `localStorage` on page load and written on toggle.
- Color palette: dark charcoal background (`#1a1a2e` / `#16213e`), indigo accent (`#6366f1`), white/light-grey text. Light mode inverts to near-white background with dark text, same accent.

## Testing Decisions

- The backend has no changes and requires no new tests.
- Frontend behavior is best verified by running the app and exercising the golden path manually: build an equation via keypad → press `=` → confirm result appears in history.
- Key edge cases to verify manually: division by zero shows error message; pressing `=` with an incomplete equation shows error; pressing a preset populates and evaluates correctly; dark/light toggle persists after page reload.
- There is no existing automated frontend test suite; no new test infrastructure is proposed for this change.

## Out of Scope

- Chained / multi-operation expressions (e.g. `5 + 3 * 2`) — single-operation only.
- Scientific calculator functions (trig, exponents, log, etc.).
- Server-side changes of any kind.
- User accounts or per-user history.
- Keyboard input support (not removed, but not a focus of this redesign).

## Further Notes

- This is a v1 UI polish pass. A full scientific calculator mode was discussed and deferred to a future iteration.
- The backend regex (`^\s*(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)\s*$`) already validates the single-operation format — the frontend keypad sequencing should produce strings that always match it.
