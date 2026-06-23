# D-02 Correlation Breakdown Detector Specification

## Overview
This document specifies the implementation of the D-02 Correlation Breakdown Detector for MIIE v1.0, following the requirements outlined in TFS Section 5.2.

## Purpose
The D-02 detector identifies significant changes in correlation between metric pairs across time windows, implementing four specific breakdown detection algorithms:
1. Sudden drop detection
2. Sign reversal detection  
3. Gradual erosion detection
4. Confidence interval exclusion detection

## Algorithm Details

### Input Requirements
- At least two metrics from the supported set (M-01 through M-07)
- Time-series data organized by window identifiers
- Minimum of 10 paired observations per window for correlation computation

### Correlation Computation
#### Pearson Correlation
For metric pair (X, Y) with n paired observations:
```
r = Σ((xᵢ - x̄)(yᵢ - ȳ)) / √[Σ(xᵢ - x̄)² Σ(yᵢ - ȳ)²]
```

#### Spearman Rank Correlation
1. Convert X and Y to rank variables Xᵣ and Yᵣ
2. Compute Pearson correlation on the rank variables

### Breakdown Detection Types

#### 1. Sudden Drop
Triggered when |rₜ₊₁ - rₜ| > 0.3 between consecutive windows

#### 2. Sign Reversal
Triggered when:
- sign(rₜ) ≠ sign(rₜ₊₁)  
- |rₜ| > 0.2 and |rₜ₊₁| > 0.2

#### 3. Gradual Erosion
Triggered when:
- K ≥ 4 windows available
- r₀ > 0.3 and rₖ₋₁ < 0.1
- Linear regression slope of r over window indices < -0.1

#### 4. Confidence Interval Exclusion
Triggered when:
- K ≥ 2 windows available
- 95% confidence intervals for consecutive windows do not overlap
- Computed using Fisher z-transformation:
  - z = 0.5 × ln((1+r)/(1-r))
  - SE = 1/√(n-3)
  - CI = [tanh(z - 1.96×SE), tanh(z + 1.96×SE)]

## Output Structure
The detector outputs a structured result containing:
- `breakdown_detected`: Boolean indicating if any breakdown was found
- `breakdown_type`: String indicating highest priority breakdown type (None if no breakdown)
- `metric_pairs_analyzed`: List of metric pairs evaluated
- `breakdown_events`: List of detailed breakdown event objects
- `pearson_trajectories`: Dictionary mapping metric pairs to Pearson correlation values per window
- `spearman_trajectories`: Dictionary mapping metric pairs to Spearman correlation values per window
- `confidence_intervals`: Dictionary mapping (metric_i, metric_j, window_id) to [lower, upper] CI bounds
- `window_pairs_flagged`: List of window pairs where breakdowns were detected

## Priority System
When multiple breakdown types are detected, the following priority is used (highest to lowest):
1. sign_reversal
2. sudden_drop  
3. gradual_erosion
4. confidence_exclusion

## Implementation Notes
- Deterministic output guaranteed for identical inputs, seed, and configuration
- Handles edge cases including insufficient data, NaN values, and missing windows
- All numeric computations use numpy for consistency and performance
- Threshold values are configurable via class attributes but default to TFS Section 5.2 values

## References
- TFS Section 5.2: Correlation Breakdown Detector
- ACS v1.0: Detector Interface Specification
- BSD-Engineering v1.0: Statistical Computing Guidelines