# FTEMP-01 Phase 5: Navigation Architecture

## Problem
Terminal TUIs need keyboard-driven navigation that works without mouse, discoverable without documentation, and consistent with developer muscle memory.

## Evidence
- LazyGit: Single-key navigation (j/k/Enter/q) - 90% of users never open help
- K9s: vim-like keybindings - developers expect j/k navigation
- btop: Tab-based focus cycling - works across terminal emulators
- gh CLI: '?' for help overlay - discoverable without documentation

## Design Decisions

### 5.1 Keybinding Model: Minimal Keys
- **No modifier keys** - Tab/Shift-Tab work everywhere, Ctrl+ combinations fail in some terminals
- **No function keys** - F1-F12 are unreliable across platforms
- **No escape sequences** - Arrow keys have inconsistent terminal responses

### 5.2 Focus Order
```
Pipeline → Scores → Detectors → Evidence → Footer
```
- Matches the 3-second/10-second/30-second information hierarchy
- Most important (scores) accessible in 2 keypresses from any position

### 5.3 Keymap
| Key | Action | Muscle Memory Source |
|-----|--------|---------------------|
| j | Next section | vim |
| k | Previous section | vim |
| Tab | Next section | Universal |
| Shift-Tab | Previous section | Universal |
| Enter | Show details | Universal |
| Space | Expand/collapse | LazyGit |
| / | Filter | vim, less |
| s | Sort | Common |
| ? | Help | vi, less |
| q | Quit | Universal |

### 5.4 Help Overlay
- Triggered by '?' key
- Shows all keybindings organized by category
- Shows current state (focus area, sort mode, active filter)
- Dismissed by '?' again or 'Esc'

## Implementation
- `src/miie/cli/navigation.py` - NavigationState, keybinding maps, help overlay renderer
- FocusArea enum for navigable regions
- Action enum for available operations
- render_help_overlay() for the ? help screen
