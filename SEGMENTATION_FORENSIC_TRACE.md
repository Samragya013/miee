# SEGMENTATION_FORENSIC_TRACE.md

**Date:** 2026-06-25

---

## Window Lifecycle Trace

### Pipeline Flow
```
CLI Input
  ↓
Configuration Resolution (strategy=time, size=7)
  ↓
Stage 1: Ingestion → RepositoryContext (137 commits, 12-day span)
  ↓
Stage 3: Extraction → MetricDataFrame {'w00': [137.0]}
  ↓                                         ↑
Stage 4: Segmentation → 1 WindowDefinition  AGGREGATED, not per-window
  ↓
Stage 5: Detection → D-01 skips (needs ≥2 windows)
  ↓
Stage 6: Scoring → sample_size = 0.02
  ↓
Stage 7: Reporting → Confidence = Low
```

### Critical Finding

**Extraction produces AGGREGATED data, not per-window data.**

| Stage | Input | Output | Issue |
|-------|-------|--------|-------|
| Extraction | repo (137 commits) | `{'w00': [137.0]}` | Single window, total value |
| Segmentation | metric_dataframe | 12 WindowDefinitions | Windows created, but metric_dataframe unchanged |
| Detection | metric_dataframe | Skips (needs ≥2 windows in metric data) | Only sees 1 window in metric data |
| Scoring | metric_dataframe | sample_size = 0.02 | Counts data points, not windows |

### Answer to Questions

**A. How many windows should Flask produce under default settings?**
- Default: time, size=7 → 1 window (7-day window ending at run date)
- This is **correct** for the time strategy

**B. How many windows are generated?**
- Segmentation generates 1 WindowDefinition
- But metric_dataframe still has `{'w00': [total]}`

**C. How many reach detectors?**
- D-01 sees 1 window in metric_dataframe → skips drift detection
- D-02 sees 1 window → skips correlation breakdown
- D-03 sees 1 window → skips threshold compression
- **All detectors effectively skip when metric_dataframe has 1 window**

**D. How many reach scoring?**
- All 3 reach scoring, but produce no findings

**E. How many reach evidence?**
- All 3 reach evidence

**F. How many reach reporting?**
- All 3 reach reporting

**G. If 281 windows are generated, why is the user seeing 1?**
- Segmentation creates WindowDefinitions, but metric_dataframe is not re-extracted per window
- The metric_dataframe is created ONCE before segmentation
- Segmentation creates windows, but doesn't modify metric_dataframe
- Detectors read from metric_dataframe, not from WindowDefinitions
- **This is the fundamental architecture gap**

### Root Cause

The extraction engine is designed for "Day 7 foundation" and returns aggregated values:

```python
# extraction.py line 143-151
# For Day 7 foundation, we extract total commit count as a single value
# In future versions, this would be windowed
commit_count = self._get_commit_count_since_until(...)
return {"w00": [float(commit_count)]}
```

The segmentation engine creates WindowDefinitions, but these are NOT used to re-extract metrics per window.

### Impact

1. D-01 (distribution drift) cannot compare distributions across windows
2. D-02 (correlation breakdown) cannot compare correlations across windows
3. D-03 (threshold compression) cannot detect compression patterns
4. Confidence sample_size factor counts data points (always 1 per metric), not windows
5. **All detectors produce PASS by default, not by actual detection**
