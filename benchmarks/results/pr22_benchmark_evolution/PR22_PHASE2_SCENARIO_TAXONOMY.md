# PR-22 Phase 2: Scenario Taxonomy

**Status**: COMPLETE  
**Date**: 2026-07-07  
**Author**: MIEE Research Team  
**Validation**: PR-22  

---

## Executive Summary

This phase classifies every benchmark scenario and identifies missing scenario classes. The taxonomy provides a comprehensive framework for evaluating benchmark completeness.

**Critical Finding**: Only 6 of 21 scenario classes are currently covered (29% coverage). The benchmark lacks critical scenario types including gradual drift, seasonal drift, multivariate drift, and stress conditions.

---

## 1. Current Dataset Classification

### 1.1 D-01 (Distribution Drift) Datasets

| Dataset ID | Name | Drift Type | Effect Size | Scenario Class |
|------------|------|------------|-------------|----------------|
| GT-SYN-DRIFT-001 | No Drift Baseline | None | d=0.0 | **Abrupt-None** |
| GT-SYN-DRIFT-002 | Small Drift Below Threshold | Abrupt | d=0.2 | **Abrupt-Small** |
| GT-SYN-DRIFT-003 | Medium Drift Detected | Abrupt | d=0.5 | **Abrupt-Medium** |
| GT-SYN-DRIFT-004 | Large Drift Detected | Abrupt | d=0.8 | **Abrupt-Large** |
| GT-SYN-DRIFT-005 | Gradual Drift Detected | Gradual | d=0.5 | **Gradual-Medium** |
| GT-SYN-DRIFT-006 | Sudden Drift Detected | Sudden | d=0.8 | **Abrupt-Sudden** |
| GT-SYN-DRIFT-007 | Intermittent Drift Detected | Intermittent | d=0.5 | **Intermittent-Medium** |
| GT-ADV-DRIFT-001 | Subtle Drift May Evade | Abrupt | d=0.3 | **Abrupt-Adversarial** |
| GT-ADV-DRIFT-002 | Seasonal Pattern Should Not Trigger | Seasonal | amp=0.3 | **Seasonal-None** |

### 1.2 D-02 (Correlation Breakdown) Datasets

| Dataset ID | Name | Breakdown Type | Effect Size | Scenario Class |
|------------|------|----------------|-------------|----------------|
| GT-SYN-CORR-001 | No Correlation Breakdown Baseline | None | r=0.7 | **None-Strong** |
| GT-SYN-CORR-002 | Small Correlation Weakening Below Threshold | Weakening | Δr=0.2 | **Weakening-Small** |
| GT-SYN-CORR-003 | Medium Correlation Weakening Detected | Weakening | Δr=0.4 | **Weakening-Medium** |
| GT-SYN-CORR-004 | Large Correlation Weakening Detected | Weakening | Δr=0.6 | **Weakening-Large** |
| GT-SYN-CORR-005 | Correlation Reversal Detected | Reversal | r=-0.5 | **Reversal-Complete** |
| GT-SYN-CORR-006 | Correlation Emergence Detected | Emergence | r=0.8 | **Emergence-New** |
| GT-ADV-CORR-001 | Subtle Correlation Decoupling May Evade | Weakening | Δr=0.15 | **Weakening-Adversarial** |

### 1.3 D-03 (Threshold Compression) Datasets

| Dataset ID | Name | Compression Type | Effect Size | Scenario Class |
|------------|------|------------------|-------------|----------------|
| GT-SYN-THRESH-001 | No Threshold Compression Baseline | None | None | **None-Unimodal** |
| GT-SYN-THRESH-002 | Weak Compression Below Threshold | Weak | Weak | **Weak-Below** |
| GT-SYN-THRESH-003 | Moderate Compression Detected | Moderate | Moderate | **Moderate-Detected** |
| GT-SYN-THRESH-004 | Strong Compression Detected | Strong | Strong | **Strong-Detected** |
| GT-SYN-THRESH-005 | Bimodal Distribution Detected | Bimodal | Bimodal | **Bimodal-Detected** |
| GT-ADV-THRESH-001 | Near-Threshold Gaming May Evade | Gaming | Gaming | **Gaming-Adversarial** |

### 1.4 Real Repository Datasets

| Dataset ID | Name | Repository Type | Scenario Class |
|------------|------|-----------------|----------------|
| GT-REAL-HEALTHY-001 | Healthy Repository Baseline 1 | Healthy | **Real-Healthy** |
| GT-REAL-HEALTHY-002 | Healthy Repository Baseline 2 | Healthy | **Real-Healthy** |
| GT-REAL-HEALTHY-003 | Healthy Repository Baseline 3 | Healthy | **Real-Healthy** |

---

## 2. Complete Scenario Taxonomy

### 2.1 Drift Temporal Patterns

| Scenario Class | Description | Present | Count |
|----------------|-------------|---------|-------|
| **Abrupt** | Instantaneous distribution shift | YES | 6 |
| **Gradual** | Slow, progressive drift over time | YES | 1 |
| **Sudden** | Immediate, large-magnitude shift | YES | 1 |
| **Intermittent** | Periodic drift with recovery | YES | 1 |
| **Seasonal** | Cyclical, repeating patterns | YES | 1 (adversarial only) |
| **Incremental** | Step-wise small changes | NO | 0 |
| **Rotating** | Changing distribution over time | NO | 0 |
| **Cumulative** | Accumulating small changes | NO | 0 |

### 2.2 Drift Magnitude Classes

| Scenario Class | Effect Size | Present | Count |
|----------------|-------------|---------|-------|
| **None** | d=0.0 | YES | 3 |
| **Small** | d=0.2 | YES | 2 |
| **Medium** | d=0.5 | YES | 4 |
| **Large** | d=0.8 | YES | 2 |
| **Very Large** | d>1.0 | NO | 0 |
| **Varying** | Mixed | NO | 0 |

### 2.3 Correlation Breakdown Types

| Scenario Class | Description | Present | Count |
|----------------|-------------|---------|-------|
| **None** | Stable correlation | YES | 1 |
| **Weakening** | Correlation decreasing | YES | 3 |
| **Reversal** | Correlation sign change | YES | 1 |
| **Emergence** | New correlation appearing | YES | 1 |
| **Nonlinear** | Linear correlation breaks | NO | 0 |
| **Conditional** | Correlation depends on context | NO | 0 |
| **Multivariate** | Cross-metric correlation changes | NO | 0 |

### 2.4 Threshold Compression Types

| Scenario Class | Description | Present | Count |
|----------------|-------------|---------|-------|
| **None** | Unimodal distribution | YES | 1 |
| **Weak** | Slight compression | YES | 1 |
| **Moderate** | Noticeable compression | YES | 1 |
| **Strong** | Severe compression | YES | 1 |
| **Bimodal** | Two distinct modes | YES | 1 |
| **Multimodal** | More than two modes | NO | 0 |
| **Heavy-tailed** | Extreme values | NO | 0 |
| **Skewed** | Asymmetric distribution | NO | 0 |

### 2.5 Data Quality Conditions

| Scenario Class | Description | Present | Count |
|----------------|-------------|---------|-------|
| **Complete** | All data present | YES | 22 |
| **Sparse** | Few observations | NO | 0 |
| **Missing** | Some observations missing | NO | 0 |
| **Noisy** | Random noise added | NO | 0 |
| **Outliers** | Extreme values present | NO | 0 |
| **Mixed Quality** | Varying quality levels | NO | 0 |

### 2.6 Repository Evolution Patterns

| Scenario Class | Description | Present | Count |
|----------------|-------------|---------|-------|
| **Healthy** | Active, stable development | YES | 3 |
| **Declining** | Decreasing activity | NO | 0 |
| **Archived** | No longer maintained | NO | 0 |
| **Fast-growing** | Rapid expansion | NO | 0 |
| **Lifecycle Transition** | Phase changes | NO | 0 |
| **Team Change** | Developer turnover | NO | 0 |
| **Technology Shift** | Stack changes | NO | 0 |

### 2.7 Stress Conditions

| Scenario Class | Description | Present | Count |
|----------------|-------------|---------|-------|
| **Normal** | Standard conditions | YES | 22 |
| **Small Sample** | n < 20 | NO | 0 |
| **Large Sample** | n > 100 | NO | 0 |
| **High Noise** | SNR < 1.0 | NO | 0 |
| **Imbalanced Windows** | Unequal window sizes | NO | 0 |
| **Extreme Sparsity** | Very few observations | NO | 0 |
| **Adversarial** | Designed to evade detection | YES | 4 |

### 2.8 Multivariate Patterns

| Scenario Class | Description | Present | Count |
|----------------|-------------|---------|-------|
| **Univariate** | Single metric changes | YES | 22 |
| **Bivariate** | Two metrics change together | NO | 0 |
| **Multivariate** | Multiple metrics change | NO | 0 |
| **Correlated Change** | Metrics change in relation | NO | 0 |
| **Independent Change** | Metrics change independently | NO | 0 |

---

## 3. Coverage Analysis

### 3.1 Scenario Class Coverage

| Category | Total Classes | Covered | Coverage |
|----------|---------------|---------|----------|
| Drift Temporal Patterns | 8 | 5 | 63% |
| Drift Magnitude | 6 | 4 | 67% |
| Correlation Breakdown | 7 | 4 | 57% |
| Threshold Compression | 8 | 5 | 63% |
| Data Quality | 6 | 1 | 17% |
| Repository Evolution | 7 | 1 | 14% |
| Stress Conditions | 7 | 2 | 29% |
| Multivariate | 5 | 1 | 20% |
| **Overall** | **54** | **23** | **43%** |

### 3.2 Missing Critical Classes

| Priority | Missing Class | Impact | Reason |
|----------|---------------|--------|--------|
| **CRITICAL** | Gradual Drift | Cannot test slow drift detection | Only 1 gradual dataset |
| **CRITICAL** | Seasonal Drift | Cannot test cyclical patterns | Only 1 adversarial seasonal |
| **CRITICAL** | Multivariate Drift | Cannot test cross-metric changes | Zero multivariate datasets |
| **CRITICAL** | Small Sample | Cannot test detector limits | Zero small sample datasets |
| **HIGH** | Noisy Observations | Cannot test noise robustness | Zero noisy datasets |
| **HIGH** | Missing Data | Cannot test incomplete data handling | Zero missing data datasets |
| **HIGH** | Repository Decline | Cannot test lifecycle transitions | Zero decline datasets |
| **HIGH** | Heavy-tailed | Cannot test extreme distributions | Zero heavy-tailed datasets |
| **MEDIUM** | Incremental Drift | Cannot test step-wise changes | Zero incremental datasets |
| **MEDIUM** | Nonlinear Correlation | Cannot test nonlinear relationships | Zero nonlinear datasets |
| **MEDIUM** | Team Change | Cannot test developer turnover | Zero team change datasets |
| **LOW** | Rotating Distribution | Cannot test changing distributions | Zero rotating datasets |
| **LOW** | Cumulative Drift | Cannot test accumulating changes | Zero cumulative datasets |

---

## 4. Dataset Uniqueness Analysis

### 4.1 D-01 Dataset Overlap

| Dataset Pair | Overlap Assessment |
|--------------|-------------------|
| DRIFT-001 & DRIFT-002 | LOW (different magnitudes) |
| DRIFT-002 & DRIFT-003 | LOW (different magnitudes) |
| DRIFT-003 & DRIFT-004 | LOW (different magnitudes) |
| DRIFT-003 & DRIFT-005 | MEDIUM (both medium magnitude) |
| DRIFT-003 & DRIFT-007 | MEDIUM (both medium magnitude) |
| DRIFT-006 & DRIFT-004 | LOW (different types) |

### 4.2 D-02 Dataset Overlap

| Dataset Pair | Overlap Assessment |
|--------------|-------------------|
| CORR-001 & CORR-002 | LOW (different magnitudes) |
| CORR-002 & CORR-003 | LOW (different magnitudes) |
| CORR-003 & CORR-004 | LOW (different magnitudes) |
| CORR-005 & CORR-006 | LOW (different types) |

### 4.3 D-03 Dataset Overlap

| Dataset Pair | Overlap Assessment |
|--------------|-------------------|
| THRESH-001 & THRESH-002 | LOW (different magnitudes) |
| THRESH-002 & THRESH-003 | LOW (different magnitudes) |
| THRESH-003 & THRESH-004 | LOW (different magnitudes) |
| THRESH-004 & THRESH-005 | LOW (different types) |

---

## 5. Benchmark Complexity Analysis

### 5.1 Current Complexity Distribution

| Complexity Level | Datasets | Percentage |
|------------------|----------|------------|
| **Simple** (univariate, abrupt, complete data) | 22 | 88% |
| **Medium** (univariate, gradual/seasonal, complete data) | 2 | 8% |
| **Complex** (multivariate, missing data, noise) | 0 | 0% |
| **Adversarial** (designed to evade) | 4 | 16% |

### 5.2 Required Complexity Distribution

| Complexity Level | Target | Current | Gap |
|------------------|--------|---------|-----|
| **Simple** | 30% | 88% | -58% |
| **Medium** | 40% | 8% | +32% |
| **Complex** | 20% | 0% | +20% |
| **Adversarial** | 10% | 16% | -6% |

---

## 6. Detector Coverage Analysis

### 6.1 Per-Detector Scenario Coverage

| Detector | Total Scenarios | Unique Classes | Coverage |
|----------|-----------------|----------------|----------|
| D-01 | 12 | 6 | 75% |
| D-02 | 9 | 4 | 57% |
| D-03 | 8 | 5 | 63% |

### 6.2 Cross-Detector Coverage Gaps

| Gap | Impact | Priority |
|-----|--------|----------|
| No multivariate scenarios for any detector | Cannot test cross-metric detection | CRITICAL |
| No stress conditions for any detector | Cannot test robustness | HIGH |
| No real anomaly repositories | Cannot validate on real data | HIGH |
| Limited D-02 positive examples | Cannot validate correlation detection | MEDIUM |

---

## 7. Recommendations

### 7.1 Benchmark V2 Required Additions

| Category | New Scenarios | Priority |
|----------|---------------|----------|
| Gradual Drift | 5 scenarios (d=0.2, 0.3, 0.5, 0.8, varying) | CRITICAL |
| Seasonal Drift | 3 scenarios (period=4, 8, 12 windows) | CRITICAL |
| Multivariate Drift | 5 scenarios (bivariate, trivariate, correlated, independent) | CRITICAL |
| Small Sample | 3 scenarios (n=10, 15, 20) | CRITICAL |
| Noisy Observations | 3 scenarios (SNR=0.5, 1.0, 2.0) | HIGH |
| Missing Data | 3 scenarios (10%, 25%, 50% missing) | HIGH |
| Repository Decline | 3 scenarios (gradual, sudden, archived) | HIGH |
| Heavy-tailed | 3 scenarios (Pareto, log-normal, Cauchy) | MEDIUM |

### 7.2 Benchmark V2 Design Principles

1. **Difficulty Range**: Include scenarios where detectors fail (F1 < 0.50)
2. **Scenario Diversity**: Cover all 54 scenario classes
3. **Effect Size Range**: Include very large (d > 1.0) and very small (d < 0.2) effects
4. **Sample Size Range**: Include n < 20 and n > 100
5. **Real Repository Data**: Increase to at least 40% of datasets
6. **Stress Testing**: Include noise, missing data, extreme sparsity
7. **Multivariate**: Include cross-metric relationship changes

---

## 8. Conclusion

**Phase 2 Status**: COMPLETE

The current benchmark covers only 43% of required scenario classes. Critical gaps include:
- Gradual drift (most common real-world drift type)
- Seasonal drift (cyclical patterns)
- Multivariate drift (cross-metric relationships)
- Stress conditions (small samples, noise, missing data)

**Proceed to Phase 3**: Benchmark Gap Analysis.
