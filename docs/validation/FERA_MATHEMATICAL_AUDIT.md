# FERA Phase 7 — Mathematical Audit

**Audit ID:** FERA-P7-MATH  
**Date:** 2026-06-23  
**Auditor:** Independent Audit Authority  
**Scope:** Scoring engine mathematical correctness, detector correlation output, f₁ sample-size factor, autoresearch metric correlation  

---

## 1. Scoring Engine NameError Bugs (5 occurrences)

### Evidence
`src/miie/processing/scoring/engine.py` references undefined variable `detector_output` instead of loop variable `det_output` in five locations:

| Line | Method | Bug | Trigger Condition |
|------|--------|-----|-------------------|
| 175 | `_get_drift_severity` | `float(detector_output["ks_statistic"])` | D-01 fires with `drift_detected=True` AND `ks_statistic` key present |
| 188 | `_get_drift_severity` | `float(detector_output[score_field])` | D-01 fires via `score`/`severity`/`drift_score` fallback path |
| 228 | `_get_breakdown_severity` | `float(detector_output["delta_r"])` | D-02 fires with `correlation_breakdown=True` AND `delta_r` key present |
| 241 | `_get_breakdown_severity` | `float(detector_output[score_field])` | D-02 fires via `score`/`severity`/`breakdown_score` fallback path |
| 281 | `_get_compression_severity` | `float(detector_output["compression_index"])` | D-03 fires with `threshold_compressed=True` AND `compression_index` key present |
| 294 | `_get_compression_severity` | `float(detector_output[score_field])` | D-03 fires via `score`/`severity`/`compression_score` fallback path |

### Impact
- **All detector magnitude extraction paths crash with `NameError: name 'detector_output' is not defined`**
- Integrity score falls back to `d₁=d₂=d₃=0.0` (no detection), returning a false-perfect IS=1.0
- The scoring engine cannot correctly compute detector-weighted integrity scores when any detector fires with magnitude data

### Verdict
**CRITICAL BUG** — The scoring engine's severity extraction is entirely non-functional. All detector magnitude values are silently lost. The engine only works when detectors do NOT fire (returning 1.0 by default).

---

## 2. f₁ Sample-Size Factor Bug

### Evidence
`engine.py:363-397` — `_compute_sample_size_factor`:

```python
for value_list in metric_series.values():
    if isinstance(value_list, list):
        for val in value_list:
            if val is not None:
                points_sum += abs(val)  # ← BUG: sums absolute VALUES
```

TFS Section 7.4 specifies: **f₁ = min(1.0, mean_n / 50.0)** where `mean_n = mean(|Wₖ|)` — the **count of data points per window**, not the sum of their absolute magnitudes.

### Impact
- If metric values are large (e.g., commit counts of 100–500), `points_sum` inflates to thousands, making f₁ always clamp to 1.0
- If metric values are small (e.g., 0.01–0.10), `points_sum` deflates, making f₁ artificially low
- The factor no longer measures sample size; it measures **sum of absolute metric magnitudes** — a mathematically unrelated quantity

### Verdict
**WRONG FORMULA** — f₁ does not compute what TFS Section 7.4 specifies. `valid_points` (the count) is computed but never used; `points_sum` (the magnitude sum) is used instead. Should be `mean_n = total_points / metric_count` where `total_points` = count of non-None values, not their sum.

---

## 3. f₅ Detector Success Factor — Always 1.0

### Evidence
`engine.py:535-537`:
```python
# In mock scenario, assume all detectors ran successfully
successful_runs = num_detectors * num_metrics  # Assuming all combinations succeeded
```

### Impact
- f₅ is always 1.0 regardless of actual detector execution status
- This is explicitly documented as a "mock scenario" placeholder
- Confidence score never penalizes failed detector runs

### Verdict
**STUB** — Acknowledged placeholder. Not a bug per se, but means CS never reflects actual detector reliability.

---

## 4. D-02 Autoresearch Correlation Analysis

### Evidence
- **Source:** `.autoresearch/miie/validation/results.tsv`
- **Config:** `metric: success_rate`, `evaluate_cmd: python -m pytest tests/ -v --tb=short`
- **Results:** 4 logged iterations, all `success_rate=0.0`

| Timestamp | Description | success_rate |
|-----------|-------------|--------------|
| 2026-06-20T13:17:25Z | Initial validation run - test suite crashed | 0.0 |
| 2026-06-20T13:38:31Z | Validation run crashed (iteration 3) | 0.0 |
| 2026-06-20T13:53:10Z | Validation run crashed - API rate limits | 0.0 |

- **Correlation (autoresearch iterations vs. success_rate):** N/A — all values are 0.0; no variance to correlate
- The autoresearch experiment never produced a non-zero success rate
- `day15_loop.json` references "Day 15 D02 Correlation Breakdown Detector" — the detector exists (314 lines) but is out-of-authority and non-functional per scoring bugs

### Verdict
**NO SIGNAL** — Autoresearch produced zero successful iterations. The experiment is non-informative.

---

## 5. Integrity Score Formula Correctness (when detectors don't fire)

When no detectors fire, the formula `IS = 1.0 - (w₁×0 + w₂×0 + w₃×0) = 1.0` is trivially correct. The issue is that detectors DO fire (D-02 with correlation_breakdown=True in test data), but the magnitude extraction crashes, so severity defaults to 0.0.

**The formula itself (TFS Section 6.3) is correctly implemented** — the bug is in the severity extraction layer feeding it.

---

## Summary

| Check | Status | Severity |
|-------|--------|----------|
| Scoring engine NameError bugs (5x) | **FAIL** | CRITICAL |
| f₁ sample-size factor formula | **FAIL** | HIGH |
| f₅ detector success factor | **STUB** | MEDIUM |
| D-02 autoresearch correlation | **NO SIGNAL** | HIGH |
| IS formula (TFS 6.3) when no detectors fire | **PASS** | — |
| CS formula (TFS 7.4-7.5) correctness | **FAIL** (f₁ wrong) | HIGH |

**Overall Mathematical Audit: FAIL** — The scoring engine has critical bugs that make detector severity extraction non-functional and f₁ compute the wrong quantity.
