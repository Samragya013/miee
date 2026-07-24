# FTEMP-01 Phase 13: Flagship Blueprint

## Vision
MIIE TUI as the reference implementation for scientific tool terminal interfaces - combining rigor of academic visualization with UX of modern terminal apps.

## Blueprint Architecture

### Layer 1: Design Tokens (Foundation)
```
src/miie/cli/design_tokens.py
  MIIEDesignTokens (singleton)
  ├── TypographyTokens (fonts, sizes, weights)
  ├── SpacingTokens (padding, margins, gaps)
  ├── BorderTokens (styles, radii)
  ├── LayoutTokens (columns, rows, max widths)
  └── AnimationTokens (speeds, easing)
```

### Layer 2: Color System (Semantics)
```
src/miie/cli/semantic_colors.py
  ├── Traffic light scoring (green/cyan/yellow/red)
  ├── Binary detector status (clear/triggered)
  ├── Data provenance (git/proxy/github)
  ├── Verdict messages (healthy/stable/partial/critical)
  ├── Action messages (no-action/monitor/review/investigate)
  └── Score bars with thresholds
```

### Layer 3: Responsive Layout (Adaptation)
```
src/miie/cli/responsive.py
  ├── WidthCategory enum (5 tiers)
  ├── LayoutConfig dataclass (per-tier settings)
  ├── LAYOUTS dict (preset configurations)
  ├── get_layout() (terminal width -> config)
  └── Adaptation functions (columns, truncation)
```

### Layer 4: Brand Identity (Permanence)
```
src/miie/cli/brand_header.py
  ├── LOGO_WIDE / LOGO_COMPACT / LOGO_MINIMAL
  ├── render_brand_header() (adaptive variant)
  ├── render_status_bar() (live metrics)
  └── render_section_divider() (visual separation)
```

### Layer 5: Navigation (Interaction)
```
src/miie/cli/navigation.py
  ├── NavigationState (focus, sort, filter)
  ├── KEYBINDINGS map (minimal keys)
  ├── render_help_overlay() (? help screen)
  └── Focus indicators
```

### Layer 6: Scientific Dashboard (Data)
```
src/miie/cli/scientific_dashboard.py
  ├── render_confidence_breakdown() (6 factors)
  ├── render_detector_detail() (per-detector card)
  ├── render_metric_card() (individual metrics)
  └── render_scientific_dashboard() (assembled view)
```

### Layer 7: Accessibility (Inclusion)
```
src/miie/cli/accessibility.py
  ├── AccessibilityConfig (from env vars)
  ├── Color-blind palettes (4 modes)
  ├── Dual-coded status markers (icon + text)
  └── Screen reader support
```

### Layer 8: Performance (Budget)
```
src/miie/cli/performance.py
  ├── RenderBudget (50ms total)
  ├── TablePool (object reuse)
  ├── DisclosureLevel (adaptive detail)
  └── StringBuilder (efficient strings)
```

### Layer 9: Premium TUI (Orchestration)
```
src/miie/cli/premium_tui.py
  ├── PremiumPipelineProgress (stage tracking)
  ├── display_executive_summary() (results panel)
  ├── display_metric_sources() (data provenance)
  ├── display_premium_footer() (completion)
  └── create_pipeline_progress() (factory)
```

## Design Principles
1. **Evidence-first**: Every design choice backed by research
2. **Color = meaning**: Not decoration
3. **Adaptive**: Works at any terminal width
4. **Accessible**: Usable by everyone
5. **Testable**: All output capturable by CliRunner
6. **Performant**: < 50ms total overhead
