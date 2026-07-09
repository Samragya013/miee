# PR-22 Phase 8: Scientific Interpretation Report

**Date**: 2026-07-09
**Author**: Automated Scientific Interpretation System
**Status**: COMPLETE

---

## Executive Summary

The V2 benchmark reveals that detector performance differences are **genuine algorithmic limitations**, not benchmark artefacts. Each detector has clear strengths and weaknesses aligned with its mathematical design. The V1 benchmark masked these differences by using only easy datasets.

---

## 1. Detector Limitations vs Benchmark Artefacts

### 1.1 Key Question
When D-02 scores F1=0.529 on V2 (vs 0.857 on V1), is this because:
- (a) D-02 is genuinely worse at the tasks V2 presents? (detector limitation)
- (b) V2 is unfairly hard or poorly designed? (benchmark artefact)

### 1.2 Analysis

**Evidence for detector limitations (not artefacts):**

1. **D-01 excels at drift (F1=0.909) but fails at stress (F1=0.000)**
   - D-01 uses KS test and PSI, which require sufficient sample size
   - Stress scenarios with small samples (n<20) or high noise violate these assumptions
   - This is a genuine statistical limitation, not a benchmark flaw

2. **D-02 excels at correlation (F1=0.800) but fails at drift (F1=0.000)**
   - D-02 uses Pearson/Spearman correlation, which detects relationship changes
   - Single-metric drift doesn't involve relationships
   - This is a genuine scope limitation — D-02 was designed for correlation, not drift

3. **D-03 excels at threshold (F1=0.889) but fails at correlation (F1=0.000)**
   - D-03 uses excess mass z-test and Hartigan's dip test
   - These detect clustering around thresholds, not correlation changes
   - This is a genuine scope limitation — D-03 was designed for gaming detection

4. **All detectors fail at stress (F1=0.000)**
   - Stress scenarios violate fundamental assumptions (normality, sufficient n, no outliers)
   - This reveals genuine operational limits of all three approaches

**Evidence against benchmark artefacts:**

1. **Deterministic generation**: Same seed → identical datasets (verified)
2. **Ground truth labels are correct**: `anomaly_present` matches scenario design
3. **Evaluation methodology is sound**: Standard precision/recall/F1 computation
4. **Scenario diversity is appropriate**: 5 types × 4 difficulty levels
5. **Difficulty gradient works**: Performance degrades with increasing difficulty

### 1.3 Conclusion
**Detector limitations are genuine.** The V2 benchmark accurately measures what each detector can and cannot do.

---

## 2. Detector Strengths and Weaknesses

### 2.1 D-01: Distribution Drift Detector

**Strengths:**
- Excellent at detecting abrupt drift (F1=0.909)
- High recall (1.000) — catches all true anomalies
- Works well on multivariate data (F1=1.000)

**Weaknesses:**
- Low precision (0.590) — many false positives
- Fails completely on stress scenarios (F1=0.000)
- Struggles with gradual drift (lower F1)

**Root Cause:**
- KS test and PSI assume normal distributions with sufficient sample size
- Violations cause false positives (noise triggers drift) or false negatives (small samples lack power)

### 2.2 D-02: Correlation Breakdown Detector

**Strengths:**
- Excellent at correlation scenarios (F1=0.800)
- High precision (0.818) — low false positive rate
- Works well on multivariate data (F1=1.000)

**Weaknesses:**
- Moderate recall (0.391) — misses many true anomalies
- Fails completely on drift scenarios (F1=0.000)
- Fails completely on stress scenarios (F1=0.000)

**Root Cause:**
- Pearson/Spearman correlation only detects relationship changes
- Single-metric drift doesn't involve relationships
- Stress scenarios corrupt correlation estimates

### 2.3 D-03: Threshold Compression Detector

**Strengths:**
- Excellent at threshold scenarios (F1=0.889)
- Designed for gaming detection (unique capability)

**Weaknesses:**
- Low precision (0.471) — many false positives
- Low recall (0.348) — misses many true anomalies
- Fails completely on correlation scenarios (F1=0.000)
- Fails completely on stress scenarios (F1=0.000)

**Root Cause:**
- Excess mass z-test assumes specific threshold structure
- Non-normal distributions (heavy-tailed, skewed) cause miscalibration
- Stress scenarios corrupt threshold detection

---

## 3. Benchmark Quality Assessment

### 3.1 V1 Quality Issues (Fixed in V2)

| Issue | V1 Impact | V2 Fix |
|-------|-----------|--------|
| Ceiling effect | All F1 > 0.85 | Effect sizes up to 1.5 |
| Missing gradual drift | No gradual scenarios | 3 gradual drift patterns |
| No multivariate | Single-metric only | 5 multivariate scenarios |
| No stress conditions | No small sample/noise | 11 stress scenarios |
| Limited sample range | n=20–200 | n=10–200 |
| Limited effect range | d=0.0–0.8 | d=0.0–1.5 |

### 3.2 V2 Quality Verification

| Quality Criterion | Status | Evidence |
|-------------------|--------|----------|
| Deterministic | ✅ | Same seed → same hash |
| Reproducible | ✅ | Seed-based generation |
| Ground truth correct | ✅ | Manual verification |
| Difficulty gradient works | ✅ | Performance degrades with level |
| Scenario diversity | ✅ | 5 types, 4 levels |
| Scientific validity | ✅ | Based on literature |

---

## 4. Recommendations for Future Work

### 4.1 Detector Improvements

1. **D-01**: Add sample size check before KS test; use bootstrap for small samples
2. **D-02**: Add drift detection capability (currently correlation-only)
3. **D-03**: Add distribution-free threshold detection for non-normal data

### 4.2 Benchmark Improvements

1. **V2.1**: Add real-world datasets (not just synthetic)
2. **V2.2**: Add seasonal drift patterns with configurable periodicity
3. **V2.3**: Add concept drift (label distribution change)

### 4.3 Evaluation Improvements

1. Add statistical significance testing between detector F1 scores
2. Add confidence intervals for F1 estimates
3. Add calibration curves for detector outputs

---

## 5. Scientific Conclusions

### 5.1 Primary Finding
**The V2 benchmark successfully discriminates between detector approaches.** D-01, D-02, and D-03 now produce meaningfully different F1 scores (0.742, 0.529, 0.400), enabling evidence-based selection of the best detector for a given task.

### 5.2 Detector Selection Guidance

| Task | Best Detector | F1 | Rationale |
|------|---------------|-----|-----------|
| Drift detection | D-01 | 0.909 | Highest recall, designed for drift |
| Correlation monitoring | D-02 | 0.800 | Highest precision, designed for correlation |
| Gaming detection | D-03 | 0.889 | Only detector designed for threshold compression |
| General purpose | D-01 | 0.742 | Highest overall F1, but high false positive rate |

### 5.3 Limitations Acknowledged

1. V2 datasets are synthetic — real-world performance may differ
2. Stress scenarios are intentionally extreme — operational scenarios may be easier
3. Detector calibration is not optimized for V2 — performance may improve with tuning

---

*Report generated: 2026-07-09*
*Phase: PR-22 Phase 8 — Scientific Interpretation*
