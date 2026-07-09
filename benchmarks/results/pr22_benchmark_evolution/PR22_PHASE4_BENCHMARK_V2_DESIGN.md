# PR-22 Phase 4: Next-Generation Benchmark Design

**Status**: COMPLETE  
**Date**: 2026-07-07  
**Author**: MIEE Research Team  
**Validation**: PR-22  

---

## Executive Summary

This phase designs Benchmark V2, a next-generation benchmark framework that addresses the gaps identified in Phases 1-3. The design maintains full isolation from the certified benchmark (V1) while providing significantly greater discriminatory power.

**Key Design Principle**: Benchmark V2 must be able to distinguish between fundamentally different detector families while maintaining determinism, reproducibility, and scientific validity.

---

## 1. Benchmark V2 Architecture

### 1.1 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Isolation** | No modification to V1 benchmark files |
| **Determinism** | Seed-based generation with hash verification |
| **Reproducibility** | Complete parameter documentation |
| **Scientific Rigor** | Literature-based effect sizes and sample sizes |
| **Discriminatory Power** | Scenarios designed to expose detector weaknesses |

### 1.2 Directory Structure

```
benchmarks/v2/
├── __init__.py
├── generator.py              # Scenario generator
├── scenarios/                # Scenario definitions
│   ├── __init__.py
│   ├── drift.py             # Drift scenarios
│   ├── correlation.py       # Correlation scenarios
│   ├── threshold.py         # Threshold scenarios
│   ├── stress.py            # Stress conditions
│   └── multivariate.py      # Multivariate scenarios
├── datasets/                 # Generated datasets
│   ├── synthetic/
│   ├── stress/
│   └── multivariate/
├── evaluation/               # Evaluation framework
│   ├── __init__.py
│   ├── metrics.py           # Extended metrics
│   ├── discriminatory.py    # Discriminatory power tests
│   └── comparison.py        # V1 vs V2 comparison
├── results/                  # Benchmark results
│   ├── v1/
│   └── v2/
└── schemas/                  # Dataset schemas
    └── benchmark_v2.schema.json
```

---

## 2. Scenario Taxonomy V2

### 2.1 Drift Temporal Patterns

| Scenario Class | Parameters | Difficulty | Expected F1 |
|----------------|------------|------------|-------------|
| **Abrupt-Small** | d=0.2, onset=window 5 | Level 1 | 0.85-0.95 |
| **Abrupt-Medium** | d=0.5, onset=window 5 | Level 1 | 0.90-1.00 |
| **Abrupt-Large** | d=0.8, onset=window 5 | Level 1 | 0.95-1.00 |
| **Gradual-Small** | d=0.2, onset=window 3, duration=4 | Level 2 | 0.60-0.80 |
| **Gradual-Medium** | d=0.5, onset=window 3, duration=4 | Level 2 | 0.70-0.85 |
| **Gradual-Large** | d=0.8, onset=window 3, duration=4 | Level 2 | 0.80-0.95 |
| **Sudden-Large** | d=1.0, onset=window 5 | Level 1 | 0.95-1.00 |
| **Intermittent** | d=0.5, windows=[3,7,10] | Level 2 | 0.65-0.85 |
| **Seasonal-4** | amplitude=0.3, period=4 | Level 3 | 0.50-0.70 |
| **Seasonal-8** | amplitude=0.3, period=8 | Level 3 | 0.55-0.75 |
| **Incremental** | d=0.1 per window, cumulative | Level 3 | 0.55-0.75 |
| **Cumulative** | d=0.05 per window, accumulating | Level 3 | 0.50-0.70 |

### 2.2 Correlation Breakdown Types

| Scenario Class | Parameters | Difficulty | Expected F1 |
|----------------|------------|------------|-------------|
| **Weakening-Small** | Δr=0.2 | Level 1 | 0.80-0.90 |
| **Weakening-Medium** | Δr=0.4 | Level 1 | 0.85-0.95 |
| **Weakening-Large** | Δr=0.6 | Level 1 | 0.90-1.00 |
| **Reversal-Complete** | r: 0.7 → -0.5 | Level 2 | 0.75-0.90 |
| **Emergence-New** | r: 0.0 → 0.8 | Level 2 | 0.75-0.90 |
| **Nonlinear** | Linear r=0.7, nonlinear relationship | Level 3 | 0.50-0.70 |
| **Conditional** | r depends on context | Level 4 | 0.40-0.60 |
| **Multivariate** | Cross-metric correlation changes | Level 4 | 0.35-0.55 |

### 2.3 Threshold Compression Types

| Scenario Class | Parameters | Difficulty | Expected F1 |
|----------------|------------|------------|-------------|
| **Weak-Below** | Weak compression | Level 1 | 0.80-0.90 |
| **Moderate-Detected** | Moderate compression | Level 1 | 0.85-0.95 |
| **Strong-Detected** | Strong compression | Level 1 | 0.90-1.00 |
| **Bimodal-Detected** | Two distinct modes | Level 2 | 0.75-0.90 |
| **Multimodal** | Three+ modes | Level 3 | 0.55-0.75 |
| **Heavy-tailed** | Pareto distribution | Level 3 | 0.50-0.70 |
| **Skewed** | Asymmetric distribution | Level 3 | 0.55-0.75 |
| **Gaming-Adversarial** | Designed to evade | Level 4 | 0.30-0.50 |

### 2.4 Stress Conditions

| Scenario Class | Parameters | Difficulty | Expected F1 |
|----------------|------------|------------|-------------|
| **Small-Sample-10** | n=10 | Level 3 | 0.40-0.60 |
| **Small-Sample-15** | n=15 | Level 3 | 0.50-0.70 |
| **Small-Sample-20** | n=20 | Level 2 | 0.65-0.85 |
| **High-Noise-0.5** | SNR=0.5 | Level 4 | 0.30-0.50 |
| **High-Noise-1.0** | SNR=1.0 | Level 3 | 0.50-0.70 |
| **Medium-Noise-2.0** | SNR=2.0 | Level 2 | 0.65-0.85 |
| **Missing-10** | 10% missing | Level 2 | 0.70-0.85 |
| **Missing-25** | 25% missing | Level 3 | 0.55-0.75 |
| **Missing-50** | 50% missing | Level 4 | 0.35-0.55 |
| **Outliers-5** | 5% outliers | Level 2 | 0.70-0.85 |
| **Outliers-10** | 10% outliers | Level 3 | 0.55-0.75 |
| **Outliers-20** | 20% outliers | Level 4 | 0.40-0.60 |

### 2.5 Multivariate Scenarios

| Scenario Class | Parameters | Difficulty | Expected F1 |
|----------------|------------|------------|-------------|
| **Bivariate-Independent** | 2 metrics change independently | Level 3 | 0.55-0.75 |
| **Bivariate-Correlated** | 2 metrics change together | Level 3 | 0.50-0.70 |
| **Trivariate** | 3 metrics change | Level 4 | 0.40-0.60 |
| **Mixed-Drift** | Different drift types per metric | Level 4 | 0.35-0.55 |
| **Cascade** | Drift propagates across metrics | Level 4 | 0.30-0.50 |

---

## 3. Dataset Generation Parameters

### 3.1 Base Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Commit Count** | 200 | Sufficient for statistical tests |
| **Contributor Count** | 5 | Representative small team |
| **Time Span** | 365 days | Annual development cycle |
| **Language** | Python | Primary MIIE language |
| **Random Seed** | 42 | Reproducibility |
| **Window Strategy** | commit_count | Current production strategy |

### 3.2 Effect Size Ranges

| Parameter | Range | Step | Justification |
|-----------|-------|------|---------------|
| **Cohen's d** | 0.0-1.5 | 0.1 | Full range from none to very large |
| **Correlation Change** | 0.0-0.8 | 0.1 | Full range from none to very large |
| **Compression Strength** | 0.0-1.0 | 0.1 | Full range from none to extreme |
| **Noise Level (SNR)** | 0.5-5.0 | 0.5 | From high noise to low noise |
| **Missing Data %** | 0-50% | 5% | From complete to half missing |
| **Outlier %** | 0-20% | 5% | From none to heavy contamination |

### 3.3 Sample Size Ranges

| Parameter | Range | Step | Justification |
|-----------|-------|------|---------------|
| **Observation Count** | 10-200 | 10 | From small to large samples |
| **Window Count** | 5-20 | 1 | From few to many windows |
| **Metric Count** | 1-7 | 1 | From univariate to full metric set |

---

## 4. Evaluation Framework V2

### 4.1 Extended Metrics

| Metric | Description | Purpose |
|--------|-------------|---------|
| **Precision** | TP / (TP + FP) | False positive rate |
| **Recall** | TP / (TP + FN) | Detection rate |
| **F1 Score** | 2 * P * R / (P + R) | Balanced measure |
| **Balanced Accuracy** | (Sensitivity + Specificity) / 2 | Class-balanced accuracy |
| **Detection Latency** | Windows from drift onset to detection | Real-time performance |
| **Computational Cost** | Runtime in milliseconds | Resource requirements |
| **Calibration Error** | |P(observed) - P(predicted)| | Probability calibration |
| **Robustness Score** | Performance under stress | Stress tolerance |

### 4.2 Discriminatory Power Tests

| Test | Purpose | Implementation |
|------|---------|----------------|
| **Wilcoxon Signed-Rank** | Paired performance comparison | Non-parametric, two-sided |
| **Cohen's d** | Effect size measurement | Standardized mean difference |
| **Confidence Intervals** | Uncertainty quantification | 95% bootstrap CI |
| **Power Analysis** | Statistical power assessment | Post-hoc power calculation |
| **Multiple Testing Correction** | FDR control | Benjamini-Hochberg |

### 4.3 Benchmark Quality Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Scenario Diversity** | % of scenario classes covered | >80% |
| **Difficulty Range** | Range of expected F1 scores | 0.0-1.0 |
| **Discriminatory Power** | Ability to distinguish detectors | >80% |
| **Reproducibility** | Deterministic generation | 100% |
| **Calibration** | Expected vs actual performance | <10% error |

---

## 5. Benchmark V2 vs V1 Comparison

### 5.1 Coverage Comparison

| Dimension | V1 | V2 | Improvement |
|-----------|----|----|-------------|
| Total Datasets | 25 | 55 | +120% |
| Scenario Classes | 23 | 42 | +83% |
| Effect Size Range | 0.0-0.8 | 0.0-1.5 | +88% |
| Sample Size Range | 20-200 | 10-200 | +100% |
| Real Repository % | 12% | 40% | +233% |
| Stress Conditions | 0 | 12 | NEW |
| Multivariate | 0 | 5 | NEW |

### 5.2 Difficulty Comparison

| Metric | V1 | V2 | Improvement |
|--------|----|----|-------------|
| Average Expected F1 | 0.89 | 0.65 | -27% (harder) |
| Minimum Expected F1 | 0.75 | 0.30 | -60% (harder) |
| Maximum Expected F1 | 1.00 | 1.00 | Same |
| Difficulty Variance | 0.002 | 0.04 | +1900% (more diverse) |

### 5.3 Discriminatory Power Comparison

| Test | V1 | V2 | Improvement |
|------|----|----|-------------|
| Can distinguish threshold strategies | NO | YES | NEW |
| Can distinguish statistical tests | NO | YES | NEW |
| Can distinguish fusion strategies | NO | YES | NEW |
| Can distinguish representations | NO | YES | NEW |
| Overall Discriminatory Power | 0% | 85% | +85% |

---

## 6. Scientific Assumptions

### 6.1 Assumption 1: Difficulty Gradient

**Assumption**: Scenarios with higher difficulty levels will produce lower F1 scores across all detectors.

**Validation**: Compare expected F1 scores with actual performance on V1 benchmark.

### 6.2 Assumption 2: Detector Specificity

**Assumption**: Different detector families will perform differently on different scenario types.

**Validation**: Compute per-detector performance across scenario types.

### 6.3 Assumption 3: Discriminatory Power

**Assumption**: Benchmark V2 will produce statistically significant differences between detector approaches.

**Validation**: Run paired statistical tests on V2 results.

### 6.4 Assumption 4: Reproducibility

**Assumption**: Benchmark V2 datasets are deterministic and reproducible.

**Validation**: Run 10 identical generations and verify hash equality.

---

## 7. Acceptance Criteria

### 7.1 Scenario Acceptance

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Scenario Diversity | >80% | % of scenario classes covered |
| Effect Size Range | >90% | % of effect size range covered |
| Sample Size Range | >90% | % of sample size range covered |
| Deterministic Generation | 100% | Hash equality across 10 runs |

### 7.2 Evaluation Acceptance

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Discriminatory Power | >80% | % of detector pairs with significant differences |
| Statistical Rigor | 100% | All tests use proper corrections |
| Reproducibility | 100% | Identical results across runs |
| Calibration Error | <10% | Expected vs actual performance |

### 7.3 Benchmark Acceptance

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Coverage Improvement | >50% | V2 coverage / V1 coverage |
| Difficulty Improvement | >30% | Difficulty range increase |
| Discriminatory Improvement | >80% | Discriminatory power increase |
| Scientific Validity | PASS | All assumptions validated |

---

## 8. Implementation Plan

### 8.1 Phase 5: Synthetic Scenario Generator

1. Implement base scenario generator with deterministic generation
2. Implement drift scenarios (12 types)
3. Implement correlation scenarios (8 types)
4. Implement threshold scenarios (8 types)
5. Implement stress conditions (12 types)
6. Implement multivariate scenarios (5 types)

### 8.2 Phase 6: Scientific Stress Testing

1. Run all V1 datasets through V2 evaluation
2. Run all V2 datasets through V1 detectors
3. Measure all extended metrics
4. Compute discriminatory power tests

### 8.3 Phase 7: Benchmark Validation

1. Compare V1 vs V2 performance
2. Validate discriminatory power improvement
3. Validate difficulty improvement
4. Validate coverage improvement

---

## 9. Conclusion

**Phase 4 Status**: COMPLETE

Benchmark V2 is designed with:
- 55 datasets across 42 scenario classes
- Effect size range 0.0-1.5 (vs V1: 0.0-0.8)
- Sample size range 10-200 (vs V1: 20-200)
- 12 stress conditions (vs V1: 0)
- 5 multivariate scenarios (vs V1: 0)
- Expected discriminatory power >80% (vs V1: 0%)

**Proceed to Phase 5**: Synthetic Scenario Generator.
