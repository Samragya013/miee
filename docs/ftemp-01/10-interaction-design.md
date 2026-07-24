# FTEMP-01 Phase 10: Interaction Design

## Problem
CLI interactions should follow predictable patterns - users should never wonder "what do I press next?"

## Evidence
- Nielsen (1994): Consistency and standards heuristic
- Shneiderman (1987): Golden rules - consistency, feedback, reversibility
- LazyGit: Every action has visible state change
- K9s: Status always visible, no hidden state

## Design Decisions

### 10.1 Feedback Principles
1. **Immediate feedback**: Every keypress produces visible state change
2. **Reversible actions**: All navigation is bidirectional (j/k)
3. **Progressive disclosure**: Details on demand, not overwhelming
4. **Consistent patterns**: Same key = same action everywhere

### 10.2 State Visibility
- Current focus area always indicated by `>` marker
- Expanded sections clearly show collapsed state
- Sort order visible in footer
- Filter active state shown in status bar

### 10.3 Error Prevention
- No destructive actions in navigation (no delete, no modify)
- Quit requires 'q' key (not accidental escape)
- Filter requires explicit '/' then text then Enter
- Help overlay is toggle, not mode change

### 10.4 Information Hierarchy
```
3-second rule: Scores (most important, first visible)
10-second rule: Detector status (secondary)
30-second rule: Evidence details (tertiary, on demand)
```

## Implementation
- Navigation state machine with clear transitions
- Focus indicator (`>`) rendered before focused section
- Sort/filter status in footer bar
- Help overlay as modal (dismissible with Esc or ?)
