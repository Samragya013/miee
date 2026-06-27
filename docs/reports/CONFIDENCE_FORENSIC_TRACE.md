# CONFIDENCE_FORENSIC_TRACE.md

**Date:** 2026-06-25

---

## Confidence Score Formula (TFS §7.4-7.5)

```
CS = f₁ × f₂ × f₃ × f₄ × f₅
```

| Factor | Formula | Description |
|--------|---------|-------------|
| f₁ | min(1.0, mean_n / 50.0) | Sample size |
| f₂ | 1.0 - min(1.0, mean_CV / 0.5) | Variance |
| f₃ | 1.0 - (missing_pairs / total_pairs) | Missing data |
| f₄ | 1.0 - min(1.0, std_size / mean_size) | Window balance |
| f₅ | successful_runs / total_attempts | Detector success |

---

## Runtime Trace — MIEE Repo (1 window, time, size=7)

### f₁: Sample Size Factor

```
metric_dataframe.metrics = {
    'M-02': {'w00': [137.0]},
    'M-06': {'w00': [110568.0]}
}

M-02: 1 window × 1 value = 1 point
M-06: 1 window × 1 value = 1 point

total_points = 2
metric_count = 2
mean_n = 2 / 2 = 1.0

f1 = min(1.0, 1.0 / 50.0) = 0.02
```

### f₂: Variance Factor

```
M-02: 1 value → cannot compute CV (need ≥2 values)
M-06: 1 value → cannot compute CV

cv_values = []
mean_CV = 0 (empty list)
f2 = 1.0 - min(1.0, 0.0 / 0.5) = 1.0
```

### f₃: Missing Data Factor

```
All metrics have data for all windows
missing_pairs = 0
total_pairs = 2
f3 = 1.0 - (0 / 2) = 1.0
```

### f₄: Window Balance Factor

```
1 window → std_size = 0, mean_size = 1.0
f4 = 1.0 - min(1.0, 0.0 / 1.0) = 1.0
```

### f₅: Detector Success Factor

```
3 detectors attempted, 3 succeeded
f5 = 3 / 3 = 1.0
```

### Final Score

```
CS = 0.02 × 1.0 × 1.0 × 1.0 × 1.0 = 0.02
```

---

## Runtime Trace — MIEE Repo (12 windows, commit, size=20)

### f₁: Sample Size Factor

```
metric_dataframe.metrics = {
    'M-02': {'w00': [137.0]},  ← SAME as 1 window
    'M-06': {'w00': [110568.0]}  ← SAME as 1 window
}

M-02: 1 window × 1 value = 1 point
M-06: 1 window × 1 value = 1 point

total_points = 2
metric_count = 2
mean_n = 2 / 2 = 1.0

f1 = min(1.0, 1.0 / 50.0) = 0.02  ← SAME
```

### Result

```
CS = 0.02 × 1.0 × 1.0 × 1.0 × 1.0 = 0.02  ← SAME
```

---

## Root Cause

**The metric_dataframe is created ONCE during extraction, BEFORE segmentation.**

```
Stage 3: Extraction → {'w00': [total_value]}  (aggregated)
Stage 4: Segmentation → creates 12 WindowDefinitions
         BUT metric_dataframe is NOT updated
Stage 6: Scoring reads metric_dataframe → still {'w00': [total_value]}
```

The `_compute_sample_size_factor` counts data points in `metric_dataframe.metrics`, not the number of `WindowDefinition` objects.

### Mathematical Impact

| Scenario | metric_dataframe | WindowDefinitions | f₁ | CS |
|----------|------------------|-------------------|----|----|
| 1 window | {'w00': [137.0]} | 1 | 0.02 | 0.02 |
| 12 windows | {'w00': [137.0]} | 12 | 0.02 | 0.02 |
| 276 windows | {'w00': [137.0]} | 276 | 0.02 | 0.02 |

**f₁ is constant regardless of window count because it reads from metric_dataframe, not WindowDefinitions.**
