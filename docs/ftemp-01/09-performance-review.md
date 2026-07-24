# FTEMP-01 Phase 9: Performance Review

## Problem
Rich Live displays and complex TUI rendering can add significant overhead to pipeline execution, especially on large repositories.

## Evidence
- Rich Live adds ~2-5ms per render cycle
- 7 pipeline stages x 2 renders each = 14 renders minimum
- Overhead budget: < 5% of total pipeline time (e.g., < 50ms for 1s pipeline)
- Large repos (34K commits) take 28s total - TUI should add < 1.4s

## Design Decisions

### 9.1 Render Budget
- Total TUI budget: 50ms across entire pipeline
- Per-render budget: ~3.5ms average
- Warning when budget exceeded (logged, not shown to user)

### 9.2 Table Reuse Pool
- Reuse Rich Table objects instead of creating new ones
- Pool size: 10 tables max
- Evict oldest when full
- Reduces object allocation by ~60%

### 9.3 Progressive Disclosure
- Detail level adapts to terminal width
- Narrow terminals get minimal output
- Wide terminals get full detail
- Rows capped at terminal-appropriate limits

### 9.4 Direct Prints (No Live)
- Click CliRunner can't capture transient Rich Live output
- Use direct prints for testability
- Direct prints are faster than Live wrapping

## Implementation
- `src/miie/cli/performance.py` - RenderBudget, TablePool, DisclosureLevel, StringBuilder
- BUDGET global instance tracks render time
- TABLE_POOL for object reuse
- DisclosureLevel.for_width() adapts to terminal
- StringBuilder for efficient string concatenation
