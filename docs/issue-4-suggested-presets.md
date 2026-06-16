# Suggested equation presets

## Parent

#1 — Calculator UI Redesign: keypad, dark mode, presets, polish

## What to build

Add a row of 4–6 hard-coded preset buttons above the keypad (e.g. `12 * 3`, `100 / 4`, `7 + 8`, `50 - 13`). Clicking a preset populates the display with the full equation string and immediately evaluates it via POST /calculate, adding the result to the history table.

## Acceptance criteria

- [ ] 4–6 preset buttons are visible above the keypad
- [ ] Clicking a preset populates the display with the preset equation
- [ ] The equation is evaluated immediately on click (no need to press =)
- [ ] The result appears in the history table
- [ ] Preset buttons are styled consistently with the rest of the UI in both dark and light themes
- [ ] Preset buttons are usable on mobile screen widths

## Blocked by

#3 — Full keypad calculator: input, evaluate, history
