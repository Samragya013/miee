# FTEMP-01 Phase 7: Evidence-Based Color System (COMPLETED)

## Problem
Colors were assigned by aesthetic preference rather than scientific meaning.

## Evidence
- Traffic light paradigm: Green=good, Red=bad is universal (WCAG, ISO 3864)
- Weber-Fechner law: Just-noticeable difference in color ~0.2 on 0-1 scale
- Nielsen (1994): Consistent color mapping across all contexts
- Wong (2011): Color-blind safe palettes for scientific visualization

## Implementation
- `src/miie/cli/semantic_colors.py` - 14 color categories with HCI citations
- Traffic light scoring: >=0.9 green, >=0.7 cyan, >=0.5 yellow, <0.5 red
- Binary detector status: CLEAR=green, TRIGGERED=red everywhere
- Data provenance: git=blue, proxy=yellow, github=green (cool-to-warm)
- Score bars with labeled thresholds
- Verdict messages and action messages

## Evidence Base
- Color assignments backed by HCI research
- Every color category has a citation
- Consistent mapping: same color = same meaning across entire TUI
