# FTEMP-01 Phase 6: Scientific Dashboard

## Problem
The current TUI shows scores as plain numbers without statistical context, making it hard to interpret what the scores mean scientifically.

## Evidence
- btop: Dense metric display with color-coded values and trend arrows
- K9s: Minimal decoration, maximum signal density
- Scientific plotting: Every number accompanied by confidence interval
- Academic papers: Results always show p-values alongside effect sizes

## Design Decisions

### 6.1 Confidence Factor Breakdown
The 6-factor confidence model (beta_1 through beta_6) needs visual representation:

| Factor | Name | Visual |
|--------|------|--------|
| beta_1 | Data Completeness | Bar + numeric |
| beta_2 | Statistical Power | Bar + numeric |
| beta_3 | Missing Data | Bar + numeric |
| beta_4 | Methodological | Bar + numeric |
| beta_5 | Temporal Coverage | Bar + numeric |
| beta_6 | Cross-Validation | Bar + numeric |
| OVERALL | Total Confidence | Bar + label |

### 6.2 Detector Detail Cards
Each detector gets a card showing:
- Status icon (V CLEAR / X TRIGGERED)
- Description (what it tests)
- Key statistics (PSI value, dip statistic, p-value)
- Significance indicator (p < 0.05 highlighted)

### 6.3 Metric Cards
Individual metric display:
- Metric ID + source (git/proxy/github)
- Current value with trend arrow
- Delta from previous window

### 6.4 Layout Rules
- Width >= 90: Detector cards side-by-side (Columns)
- Width < 90: Detector cards stacked vertically
- Compact mode: Status only, no descriptions
- Detail mode: Full statistics with bars

## Implementation
- `src/miie/cli/scientific_dashboard.py` - render_confidence_breakdown(), render_detector_detail(), render_metric_card(), render_scientific_dashboard()
- Uses semantic_colors for all color assignments
- Uses responsive layout for adaptive column count
- Panel-per-detector for visual separation
