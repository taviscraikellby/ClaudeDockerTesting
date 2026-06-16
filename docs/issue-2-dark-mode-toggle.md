# Dark mode with light mode toggle

## Parent

#1 — Calculator UI Redesign: keypad, dark mode, presets, polish

## What to build

Add dark mode as the default theme with a light mode toggle. The app should open in dark mode on first visit. A toggle button switches between dark and light. The user's preference is written to `localStorage` on toggle and read back on page load so it persists across sessions.

This slice installs the full CSS custom property system (`--bg`, `--surface`, `--text`, `--accent`) that subsequent slices will build on. Both themes are fully styled — the existing text-input UI looks correct in both modes.

## Acceptance criteria

- [ ] App opens in dark mode by default (dark charcoal background, indigo accent)
- [ ] A visible toggle button switches between dark and light mode
- [ ] Light mode uses a near-white background with dark text and the same indigo accent
- [ ] Theme preference is saved to `localStorage` and restored on page reload
- [ ] All existing UI elements (input, button, history table) are legible and styled correctly in both themes

## Blocked by

None - can start immediately
