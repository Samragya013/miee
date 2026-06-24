# AUTHORITY_COMPARISON.md

**Date:** 2026-06-25

---

## Extraction: Authority vs. Implementation

### AFD §Step 7 (Extraction)

| Metric | AFD Specification | Current Implementation | Gap |
|--------|-------------------|----------------------|-----|
| M-02 | `Count per day` | `{'w00': [total_count]}` | Aggregated, not per-day |
| M-06 | `mean per window` | `{'w00': [total_churn]}` | Aggregated, not per-window |
| M-01..M-07 | Per-window values | Single window `w00` | No windowed extraction |

### AFD §Step 8 (Segmentation)

| Requirement | Specification | Implementation | Status |
|-------------|---------------|----------------|--------|
| Windows non-overlapping | Yes | Yes | ✅ |
| Ordered | Yes | Yes | ✅ |
| Each window ≥1 commit | Yes | Guard exists | ✅ |
| Total windows ≥ 2 | **ABORT if <2** | **No abort** | ❌ DEFECT |
| Validation gate | Abort on <2 windows | Continues silently | ❌ DEFECT |

### AFD §Step 9 (Detection)

| Detector | Requirement | Current State | Impact |
|----------|-------------|---------------|--------|
| D-01 | Per window pair (Wi, Wi+1) | Skips (needs ≥2 windows in metric data) | No drift detection |
| D-02 | Per window pair | Skips (needs ≥2 windows) | No correlation analysis |
| D-03 | Per window, sample ≥20 | Skips (needs ≥2 windows) | No compression detection |

---

## Confidence: Authority vs. Implementation

### TFS §7.5 f₁ Specification

```
mean_n = mean(|Wₖ| for all k and all metrics with data)
f₁ = min(1.0, mean_n / 50.0)
```

**Where `|Wₖ|` = count of data points in window k**

### Current Implementation

```python
# _compute_sample_size_factor (engine.py:364-396)
total_points = 0
metric_count = 0
for metric_id, metric_series in metric_dataframe.metrics.items():
    for value_list in metric_series.values():
        for val in value_list:
            if val is not None:
                total_points += 1
if metric_count > 0:
    mean_n = total_points / metric_count
f1 = min(1.0, mean_n / 50.0)
```

**This counts data points in metric_dataframe, not per-window data points.**

### Mathematical Proof

| Scenario | metric_dataframe | |Wₖ| per window | mean_n | f₁ |
|----------|------------------|----------------|--------|-----|
| 1 window | {'w00': [137.0]} | 1 | 1.0 | 0.02 |
| 12 windows | {'w00': [137.0]} | 1 (same!) | 1.0 | 0.02 |
| 276 windows | {'w00': [137.0]} | 1 (same!) | 1.0 | 0.02 |

**f₁ is constant because metric_dataframe is not updated per window.**

---

## Root Cause Summary

### Defect 1: Extraction Not Windowed (AFD §Step 7)

- **Authority:** M-02 `Count per day`, M-06 `mean per window`
- **Implementation:** `{'w00': [total_value]}` — aggregated
- **Impact:** Detectors cannot compare across windows

### Defect 2: No Minimum Window Gate (AFD §Step 8)

- **Authority:** "total windows ≥ 2 (required for drift detection). If <2 valid windows: abort."
- **Implementation:** No abort on <2 windows
- **Impact:** System continues with 1 window, producing meaningless results

### Defect 3: Confidence Factor Miscalculation

- **Authority:** f₁ uses `|Wₖ|` (data points per window)
- **Implementation:** f₁ uses total data points in metric_dataframe
- **Impact:** f₁ is always 0.02 regardless of window count

---

## Classification

| Defect | Type | Severity |
|--------|------|----------|
| Extraction not windowed | Implementation Gap | HIGH — detectors non-functional |
| No minimum window gate | Missing Validation | HIGH — violates AFD contract |
| Confidence factor miscalculation | Mathematical Error | MEDIUM — wrong confidence score |

---

## Recommended Fixes

### Fix 1: Minimum Window Gate (AFD §Step 8)

```python
# In pipeline.py, after segmentation
if len(windows) < 2:
    # AFD §Step 8: Abort if <2 windows
    raise PipelineError(
        f"Insufficient windows: {len(windows)} (need ≥2). "
        "Adjust window_size or time range."
    )
```

### Fix 2: Windowed Extraction (AFD §Step 7)

Extract metrics per window, not aggregated:

```python
# For each window in segmentation output:
for window in windows:
    metric_value = extract_metric(context, window.start, window.end)
    metric_dataframe.metrics['M-02'][window.window_id] = [metric_value]
```

### Fix 3: Confidence f₁ from Window Count

```python
# Use len(windows) for sample_size
mean_n = len(windows)  # or mean data points per window
f1 = min(1.0, mean_n / 50.0)
```
