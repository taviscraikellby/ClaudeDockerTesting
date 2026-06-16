# Full keypad calculator: input, evaluate, history

## Parent

#1 — Calculator UI Redesign: keypad, dark mode, presets, polish

## What to build

Replace the text input with a full numeric keypad and display area. The keypad uses standard calculator layout (7-8-9, 4-5-6, 1-2-3, 0/./= in the digit area; +, -, *, /, C in the operator column). A display area above the keypad shows the equation as it is being built.

The JS state machine enforces single-operation sequencing: number → operator → number → =. Pressing = submits to POST /calculate, updates the history table (most-recent-first), and clears the display. Errors (division by zero, incomplete equation) display inline near the keypad. The layout is mobile-responsive. Hover and active states are styled on all buttons.

## Acceptance criteria

- [ ] Full numeric keypad renders in standard calculator layout
- [ ] Display area shows the equation string as digits and operator are pressed
- [ ] Pressing = evaluates the equation and shows the result in history
- [ ] Pressing C clears the display
- [ ] A second operator press replaces the first; pressing an operator after a result starts a new equation
- [ ] Errors display inline near the keypad (division by zero, incomplete equation)
- [ ] History table updates immediately after each calculation, most-recent-first
- [ ] Buttons have hover and active states
- [ ] Layout is usable on mobile screen widths
- [ ] All buttons are correctly styled in both dark and light themes (from #2)

## Blocked by

#2 — Dark mode with light mode toggle
