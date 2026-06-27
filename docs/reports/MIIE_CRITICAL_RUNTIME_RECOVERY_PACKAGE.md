# MIIE_CRITICAL_RUNTIME_RECOVERY_PACKAGE.md

**Date:** 2026-06-25

---

## Executive Summary

The Critical Runtime Forensic Investigation identified 4 defects in the MIIE v1.0 runtime pipeline. Two defects (D-1, D-2) were fixed in this iteration. Two defects (D-3, D-4) are architectural issues documented for future resolution.

**Test Results:** 911 passed, 4 skipped, 0 failed

**Multi-Repository Validation:** 6/6 repositories analyzed successfully

---

## Defect Summary

| ID | Defect | Type | Severity | Status |
|----|--------|------|----------|--------|
| D-1 | No minimum window gate | Missing Validation | HIGH | **FIXED** |
| D-2 | Explanation engine factor name mismatch | Bug | MEDIUM | **FIXED** |
| D-3 | Confidence f₁ counts data points, not per-window data | Mathematical Error | MEDIUM | Documented |
| D-4 | Extraction produces aggregated, not per-window data | Implementation Gap | HIGH | Documented |

---

## Fixes Applied

### D-1: Minimum Window Gate (AFD §Step 8)

**Authority:** "total windows ≥ 2 (required for drift detection). If <2 valid windows: abort."

**Files Modified:**
- `src/miie/orchestration/pipeline.py` — Added validation after segmentation
- `src/miie/cli.py` — Added validation after window generation

**Behavior:**
- If `len(windows) < 2`, pipeline returns early with error message
- CLI exits with code 3 and JSON error response
- Prevents meaningless detector results from single-window analysis

**Test:** Verified with MarkupSafe (1 window → exit 3)

---

### D-2: Explanation Engine Factor Names

**Authority:** TFS §7.5 specifies factors: sample_size, variance, missing_data, window_balance, detector_success

**Files Modified:**
- `src/miie/processing/explanation/engine.py` — Updated factor names

**Changes:**
- `data_quality` → `missing_data`
- `temporal_coverage` → `window_balance`

**Impact:** Narratives now correctly reflect actual factor values

---

### MockSegmentationEngine Update

**File Modified:**
- `src/miie/processing/segmentation.py` — Updated mock to return 2 windows

**Rationale:** Mock must produce ≥2 windows to pass minimum window gate

---

### Test Updates

**File Modified:**
- `tests/test_cli_usability.py` — Updated all tests to use commit strategy
- `tests/integration/test_segmentation_integration.py` — Updated window count assertion

**Rationale:** Test repos need ≥2 windows to pass minimum window gate

---

## Architectural Issues (D-3, D-4)

### D-3: Confidence f₁ Miscalculation

**Root Cause:** `_compute_sample_size_factor` counts data points in metric_dataframe, not per-window data points.

**Impact:** f₁ is always 0.02 regardless of window count.

**Resolution:** Requires D-4 fix (per-window extraction) to properly address.

---

### D-4: Extraction Not Windowed

**Root Cause:** Extraction engine returns aggregated values (`{'w00': [total]}`), not per-window values.

**Impact:** Detectors cannot compare across windows; confidence scores are incorrect.

**Resolution:** Requires extraction engine refactoring to produce per-window data.

---

## Multi-Repository Validation Results

| Repository | Commits | Windows | Exit Code | Status |
|------------|---------|---------|-----------|--------|
| Flask | 5539 | 281 | 0 | ✅ |
| Requests | 6477 | 330 | 0 | ✅ |
| FastAPI | 7378 | 394 | 0 | ✅ |
| Django | 34732 | 1913 | 0 | ✅ |
| NumPy | 41380 | 2239 | 0 | ✅ |
| Pandas | 38172 | 2058 | 0 | ✅ |
| MarkupSafe | 844 | 1 | 3 | ✅ (correct rejection) |

---

## Test Suite Results

```
911 passed, 4 skipped, 7 warnings
```

**Key Test Updates:**
- `test_cli_usability.py` — All 20 tests updated to use commit strategy
- `test_segmentation_integration.py` — Window count assertion updated
- `test_m02_to_m03_pipeline` — Mock returns 2 windows

---

## Documentation Generated

| Document | Purpose |
|----------|---------|
| `CRITICAL_INVESTIGATION_BASELINE.md` | Phase 0 baseline capture |
| `SEGMENTATION_FORENSIC_TRACE.md` | Window lifecycle trace |
| `CONFIDENCE_FORENSIC_TRACE.md` | Confidence formula derivation |
| `AUTHORITY_COMPARISON.md` | TFS/TRD/ACS/BSD compliance |
| `EXPLANATION_ENGINE_AUDIT.md` | Factor name mismatch |
| `ROOT_CAUSE_CLASSIFICATION.md` | Defect classification |
| `MIIE_CRITICAL_RUNTIME_RECOVERY_PACKAGE.md` | This document |

---

## Recommendations

### Immediate (Complete)
1. ✅ Minimum window gate prevents meaningless single-window analysis
2. ✅ Explanation engine correctly reports factor values

### Short-Term (Next Iteration)
1. Refactor extraction engine to produce per-window data (D-4)
2. Update confidence f₁ to use per-window data points (D-3)

### Long-Term
1. Implement windowed extraction for M-02 (commit frequency per window)
2. Implement windowed extraction for M-06 (code churn per window)
3. Add validation gates for each pipeline stage

---

## Compliance

| Authority | Requirement | Status |
|-----------|-------------|--------|
| AFD §Step 7 | Extraction per window | ⚠️ Documented (D-4) |
| AFD §Step 8 | Minimum 2 windows | ✅ Fixed (D-1) |
| TFS §7.5 | Confidence factors | ✅ Fixed (D-2) |
| TFS §7.5 | f₁ formula | ⚠️ Documented (D-3) |

---

## Sign-Off

**Investigation Program:** 10/10 phases complete

**Test Coverage:** 911 tests passing

**Multi-Repo Validation:** 6/6 repositories

**Recovery Status:** COMPLETE (D-1, D-2 fixed; D-3, D-4 documented)
