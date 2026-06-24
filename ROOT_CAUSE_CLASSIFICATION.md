# ROOT_CAUSE_CLASSIFICATION.md

**Date:** 2026-06-25

---

## Defect Registry

| ID | Defect | Type | Severity | Authority Reference | Fix Complexity |
|----|--------|------|----------|-------------------|----------------|
| D-1 | No minimum window gate | Missing Validation | HIGH | AFD §Step 8 | LOW |
| D-2 | Explanation engine factor name mismatch | Bug | MEDIUM | TFS §7.5 | LOW |
| D-3 | Confidence f₁ counts data points, not per-window data | Mathematical Error | MEDIUM | TFS §7.5 | MEDIUM |
| D-4 | Extraction produces aggregated, not per-window data | Implementation Gap | HIGH | AFD §Step 7 | HIGH |

---

## Classification Details

### D-1: No Minimum Window Gate

**Authority:** AFD §Step 8
> "total windows ≥ 2 (required for drift detection). If <2 valid windows: abort."

**Current State:** System continues with 1 window, producing meaningless detector results.

**Classification:** Missing Validation — the authority explicitly requires this gate, but it's not implemented.

**Fix:** Add validation after segmentation. If `len(windows) < 2`, raise error or return early with warning.

**Risk:** LOW — adds a guard, doesn't change existing behavior for valid cases.

---

### D-2: Explanation Engine Factor Name Mismatch

**Authority:** TFS §7.5 specifies factors: sample_size, variance, missing_data, window_balance, detector_success

**Current State:** Explanation engine checks for `data_quality` and `temporal_coverage`, which don't exist in confidence_factors dict.

**Classification:** Bug — wrong dictionary keys cause false narratives.

**Fix:** Update explanation/engine.py to use correct factor names.

**Risk:** LOW — changes narrative text only, doesn't affect scoring or detection.

---

### D-3: Confidence f₁ Counts Data Points, Not Per-Window Data

**Authority:** TFS §7.5
> "mean_n = mean(|Wₖ| for all k and all metrics with data)"
> "f₁ = min(1.0, mean_n / 50.0)"

**Current State:** `_compute_sample_size_factor` counts data points in metric_dataframe.metrics, not per-window data points.

**Classification:** Mathematical Error — the formula is implemented incorrectly.

**Fix:** Update `_compute_sample_size_factor` to count data points per window.

**Risk:** MEDIUM — changes confidence scores, but metric_dataframe doesn't have per-window data (see D-4).

---

### D-4: Extraction Produces Aggregated, Not Per-Window Data

**Authority:** AFD §Step 7
> M-02: "Count per day"
> M-06: "mean per window"

**Current State:** Extraction returns `{'w00': [total_value]}` — aggregated, not per-window.

**Classification:** Implementation Gap — the extraction engine was built for "Day 7 foundation" and returns aggregated values.

**Fix:** Refactor extraction to produce per-window data. This is a significant architectural change.

**Risk:** HIGH — changes the core data flow, affects all downstream components.

---

## Remediation Strategy

### Phase 7: Fix Verified Defects (D-1, D-2)

These are simple, verified defects that can be fixed without architectural changes:

1. **D-1:** Add minimum window gate after segmentation
2. **D-2:** Fix explanation engine factor names

### Phase 8: Document D-3, D-4 as Architectural Issues

These are deeper issues that require architectural changes:

1. **D-3:** Cannot fix without D-4 (per-window data)
2. **D-4:** Requires extraction engine refactoring — out of scope for this iteration

### Rationale

The investigation program says:
- "ONLY fix verified defects, NO speculative changes"
- "Phase 7: Remediation — ONLY fix verified defects, NO speculative changes"

D-1 and D-2 are verified defects with clear authority references and simple fixes.
D-3 and D-4 are architectural issues that require significant changes.
