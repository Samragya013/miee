# EXPLANATION_ENGINE_AUDIT.md

**Date:** 2026-06-25

---

## Factor Name Mismatch

The explanation engine checks for factor names that don't exist in the confidence_factors dict.

### Scoring Engine Output

```python
# scoring/engine.py line 353-361
return {
    "overall": confidence_score,
    "factors": {
        "sample_size": f1,      # ← This exists
        "variance": f2,         # ← This exists
        "missing_data": f3,     # ← This exists
        "window_balance": f4,   # ← This exists
        "detector_success": f5  # ← This exists
    }
}
```

### Explanation Engine Input

```python
# explanation/engine.py line 61-63
sample_size = confidence_factors.get("sample_size", 0.0)      # ← Matches
data_quality = confidence_factors.get("data_quality", 0.0)    # ← WRONG KEY
temporal_coverage = confidence_factors.get("temporal_coverage", 0.0)  # ← WRONG KEY
```

### Impact

| Factor | Actual Value | Explanation Engine Reads | Result |
|--------|-------------|------------------------|--------|
| sample_size | 0.02 | `confidence_factors.get("sample_size")` | 0.02 ✅ |
| missing_data | 1.0 | `confidence_factors.get("data_quality")` | 0.0 ❌ |
| window_balance | 1.0 | `confidence_factors.get("temporal_coverage")` | 0.0 ❌ |

### Generated Output (Incorrect)

```
Confidence score is low (0.02), indicating limited data quality, sample size, or temporal coverage.
Sample size factor is low (0.02), indicating limited number of analysis windows.
Data quality factor is low (0.00), indicating missing or invalid data in metric-window pairs.
Temporal coverage factor is low (0.00), indicating limited temporal spread of analysis windows.
```

### Expected Output (Correct)

```
Confidence score is low (0.02), indicating limited sample size.
Sample size factor is low (0.02), indicating limited number of analysis windows.
(Note: missing_data=1.0 and window_balance=1.0 are actually fine)
```

---

## Root Cause

The explanation engine was written with different factor names than what the scoring engine produces:

| Scoring Engine Factor | Explanation Engine Check | Match? |
|----------------------|------------------------|--------|
| `sample_size` | `sample_size` | ✅ |
| `variance` | (not checked) | — |
| `missing_data` | `data_quality` | ❌ |
| `window_balance` | `temporal_coverage` | ❌ |
| `detector_success` | (not checked) | — |

---

## Fix

Update explanation/engine.py to use correct factor names:

```python
# Line 61-63: Change from
sample_size = confidence_factors.get("sample_size", 0.0)
data_quality = confidence_factors.get("data_quality", 0.0)
temporal_coverage = confidence_factors.get("temporal_coverage", 0.0)

# To
sample_size = confidence_factors.get("sample_size", 0.0)
missing_data = confidence_factors.get("missing_data", 0.0)
window_balance = confidence_factors.get("window_balance", 0.0)
```

And update the corresponding narrative generation (lines 65-75).
