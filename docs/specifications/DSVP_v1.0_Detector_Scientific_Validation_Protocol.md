# Detector Scientific Validation Protocol (DSVP) v1.0

**MIIE v1.5 — Detector Subsystem Scientific Validation Methodology**

| Field | Value |
|-------|-------|
| Document ID | DSVP-v1.0 |
| Version | 1.0.0 |
| Status | Canonical |
| Date | 2026-06-29 |
| Authors | MIIE Engineering |
| Approved By | Repository Governance |
| Derived From | PRD-v1.5-OE, OEAS-v1.5, ODSS-v1.0, DES-v2.0 |
| Supersedes | None (new) |
| Scope | Scientific validation methodology for all MIIE detectors |
| Classification | Methodology specification (no implementation code) |

---

## Table of Contents

1. [Document Metadata](#1-document-metadata)
2. [Purpose](#2-purpose)
3. [Scope](#3-scope)
4. [Objectives](#4-objectives)
5. [Non-Objectives](#5-non-objectives)
6. [Scientific Validation Philosophy](#6-scientific-validation-philosophy)
7. [Research Questions](#7-research-questions)
8. [Hypotheses](#8-hypotheses)
9. [Detector Assumptions](#9-detector-assumptions)
10. [Dataset Taxonomy](#10-dataset-taxonomy)
11. [Validation Dataset Design](#11-validation-dataset-design)
12. [Experimental Methodology](#12-experimental-methodology)
13. [D-01 Validation Protocol](#13-d-01-validation-protocol)
14. [D-02 Validation Protocol](#14-d-02-validation-protocol)
15. [D-03 Validation Protocol](#15-d-03-validation-protocol)
16. [Statistical Evaluation Metrics](#16-statistical-evaluation-metrics)
17. [Acceptance Criteria](#17-acceptance-criteria)
18. [False Positive Analysis](#18-false-positive-analysis)
19. [False Negative Analysis](#19-false-negative-analysis)
20. [Stress Testing Methodology](#20-stress-testing-methodology)
21. [Adversarial Validation](#21-adversarial-validation)
22. [Regression Validation](#22-regression-validation)
23. [Reproducibility Requirements](#23-reproducibility-requirements)
24. [Threats to Validity](#24-threats-to-validity)
25. [Bias Analysis](#25-bias-analysis)
26. [Statistical Power Considerations](#26-statistical-power-considerations)
27. [Reporting Requirements](#27-reporting-requirements)
28. [Validation Artifacts](#28-validation-artifacts)
29. [Risk Register](#29-risk-register)
30. [Future Detector Validation Strategy](#30-future-detector-validation-strategy)
31. [Glossary](#31-glossary)
32. [Appendix](#32-appendix)

---

## 1. Document Metadata

| Field | Value |
|-------|-------|
| Document ID | DSVP-v1.0 |
| Version | 1.0.0 |
| Date | 2026-06-29 |
| Classification | Internal Scientific Validation Methodology |
| Status | Canonical |
| Baseline | v1.0.1 (tag `4c4d5e6`) |
| Dependencies | PRD-v1.5-OE, OEAS-v1.5, ODSS-v1.0, DES-v2.0 |
| Related Documents | RELEASE_BASELINE.md, BASELINE_CHANGE_POLICY.md |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-29 | MIIE Engineering | Initial scientific validation protocol |

---

## 2. Purpose

This document defines the **scientific validation methodology** for the MIIE detector subsystem. It specifies how every detector — D-01 (Distributional Drift), D-02 (Correlation Breakdown), D-03 (Threshold Compression) — will be evaluated for correctness, robustness, statistical validity, and reproducibility.

The DSVP exists because detector execution over aggregated single values (v1.0) produces degenerate or skipped results that cannot be meaningfully validated. The v1.5 Observation Engine provides per-commit observation-level data, enabling statistically rigorous validation for the first time.

This document is a methodology specification. It does not implement tests, modify code, or redesign detector mathematics. It defines *what* must be validated, *how* it must be validated, and *what* constitutes acceptable evidence of correctness.

---

## 3. Scope

### 3.1 In Scope

| Component | Scope |
|-----------|-------|
| Detector correctness | Statistical validity of each detector's outputs |
| Reproducibility | Deterministic results across runs |
| Robustness | Behavior under edge cases and adversarial inputs |
| False positive analysis | Type I error characterization |
| False negative analysis | Type II error characterization |
| Stress testing | Behavior under extreme conditions |
| Regression testing | Stability across versions |
| Confidence calibration | Reliability of confidence estimates |
| Dataset design | Validation dataset taxonomy and construction |

### 3.2 Out of Scope

| Component | Reason | Target |
|-----------|--------|--------|
| Detector algorithm changes | Algorithms are frozen | v1.5 unchanged |
| Scoring formula validation | Frozen per baseline | Separate protocol |
| Evidence engine validation | Separate specification | Separate protocol |
| Explanation engine validation | Separate specification | Separate protocol |
| CLI validation | Frozen per baseline | Separate protocol |
| Performance benchmarking | Covered in DES | DES scope |

---

## 4. Objectives

| ID | Objective | Priority | Verification |
|----|-----------|----------|-------------|
| OBJ-1 | Demonstrate detector statistical validity | HIGH | Hypothesis tests on synthetic data |
| OBJ-2 | Characterize false positive rates | HIGH | Controlled no-drift/no-break datasets |
| OBJ-3 | Characterize false negative rates | HIGH | Controlled known-shift datasets |
| OBJ-4 | Demonstrate reproducibility | HIGH | Identical results across 100 runs |
| OBJ-5 | Validate confidence calibration | MEDIUM | Confidence vs. actual correctness |
| OBJ-6 | Validate robustness to edge cases | MEDIUM | Edge-case dataset battery |
| OBJ-7 | Validate adversarial resilience | MEDIUM | Adversarial dataset battery |
| OBJ-8 | Demonstrate regression stability | HIGH | Cross-version comparison |
| OBJ-9 | Characterize detection latency | LOW | Timing measurements |
| OBJ-10 | Document known limitations | MEDIUM | Threats to validity section |

---

## 5. Non-Objectives

| ID | Non-Objective | Reason |
|----|--------------|--------|
| NO-1 | Validate detector algorithms | Algorithms are scientifically validated in published literature |
| NO-2 | Redesign detection mathematics | Scope is validation, not redesign |
| NO-3 | Validate scoring formulas | Scoring is frozen per baseline |
| NO-4 | Validate explanation engine | Separate specification |
| NO-5 | Implement production tests | This is methodology, not implementation |
| NO-6 | Validate across all possible repositories | Representative sample is sufficient |

---

## 6. Scientific Validation Philosophy

### 6.1 Why Detector Validation Matters

Detector validation is the process of demonstrating that a detector's outputs are statistically meaningful, reproducible, and trustworthy. Without validation, detector outputs are unverified claims about repository integrity.

The consequences of unvalidated detectors include:

| Consequence | Description |
|------------|-------------|
| False alarms | Reporting integrity problems that do not exist |
| Missed detections | Failing to report real integrity problems |
| Misleading confidence | Providing confidence estimates that do not reflect actual reliability |
| Non-reproducibility | Different runs producing different results for the same repository |

### 6.2 Four Dimensions of Validation

Detector validation operates along four independent dimensions:

```
┌─────────────────────────────────────────────────────────────────┐
│                  FOUR DIMENSIONS OF VALIDATION                   │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  Implementation  │  │   Scientific    │  │  Statistical   │  │
│  │   Correctness    │  │   Correctness   │  │  Significance  │  │
│  │                  │  │                 │  │                │  │
│  │ Does the code    │  │ Does the        │  │ Are the        │  │
│  │ correctly        │  │ algorithm       │  │ results        │  │
│  │ implement the    │  │ produce valid   │  │ unlikely under │  │
│  │ specified        │  │ statistical     │  │ the null       │  │
│  │ algorithm?       │  │ inferences?     │  │ hypothesis?    │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Operational Reliability                     ││
│  │                                                             ││
│  │ Does the detector behave predictably across diverse inputs, ││
│  │ edge cases, adversarial inputs, and over time?              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Dimension Definitions

| Dimension | Definition | Validation Method |
|-----------|-----------|-------------------|
| Implementation correctness | Code faithfully implements the specified algorithm | Unit tests, property-based tests, cross-implementation comparison |
| Scientific correctness | Algorithm produces valid statistical inferences | Synthetic data with known ground truth |
| Statistical significance | Results are unlikely under the null hypothesis | Hypothesis testing, p-value analysis |
| Operational reliability | Behavior is predictable and robust | Edge-case testing, stress testing, adversarial testing |

### 6.4 Validation vs. Verification

| Concept | Definition | Scope |
|---------|-----------|-------|
| Verification | "Are we building the product right?" | Implementation matches specification |
| Validation | "Are we building the right product?" | Product meets user needs |
| Scientific validation | "Does the product produce valid scientific results?" | Statistical correctness, reproducibility |

This document addresses scientific validation — demonstrating that detector outputs are statistically meaningful and reproducible.

---

## 7. Research Questions

The DSVP addresses the following research questions:

| ID | Research Question | Detector | Priority |
|----|------------------|----------|----------|
| RQ-1 | Does D-01 correctly detect distributional shifts with statistical significance? | D-01 | HIGH |
| RQ-2 | What is D-01's false positive rate under no-shift conditions? | D-01 | HIGH |
| RQ-3 | What is D-01's false negative rate under known-shift conditions? | D-01 | HIGH |
| RQ-4 | Does D-01 correctly classify drift direction (mean_shift, variance_collapse, shape_change)? | D-01 | MEDIUM |
| RQ-5 | Does D-02 correctly detect correlation breakdown between metric pairs? | D-02 | HIGH |
| RQ-6 | What is D-02's false positive rate under stable-correlation conditions? | D-02 | HIGH |
| RQ-7 | Does D-02 correctly classify breakdown types (sudden_drop, sign_reversal, gradual_erosion, confidence_exclusion)? | D-02 | MEDIUM |
| RQ-8 | Does D-03 correctly detect artificial clustering around thresholds? | D-03 | HIGH |
| RQ-9 | What is D-03's false positive rate under natural distributions? | D-03 | HIGH |
| RQ-10 | Are all detector outputs deterministic across runs with identical inputs? | All | HIGH |
| RQ-11 | Do confidence estimates accurately reflect actual detection reliability? | All | MEDIUM |
| RQ-12 | Do detectors maintain performance under extreme conditions? | All | MEDIUM |

---

## 8. Hypotheses

### 8.1 D-01 Hypotheses

| ID | Null Hypothesis (H₀) | Alternative Hypothesis (H₁) | Test |
|----|----------------------|---------------------------|------|
| H-D01-1 | D-01 does not detect drift when distributions are identical | D-01 detects drift when distributions differ | Two-proportion z-test on detection rate |
| H-D01-2 | D-01's KS p-values are uniformly distributed under H₀ | D-01's KS p-values are stochastically smaller under H₁ | Kolmogorov-Smirnov test on p-value distribution |
| H-D01-3 | D-01's PSI values are below threshold under no-drift | D-01's PSI values are above threshold under drift | One-sided t-test on PSI values |
| H-D01-4 | D-01 correctly classifies drift direction > 50% of the time | D-01 correctly classifies drift direction > 80% of the time | Binomial test on classification accuracy |

### 8.2 D-02 Hypotheses

| ID | Null Hypothesis (H₀) | Alternative Hypothesis (H₁) | Test |
|----|----------------------|---------------------------|------|
| H-D02-1 | D-02 does not detect breakdown when correlations are stable | D-02 detects breakdown when correlations change | Two-proportion z-test on detection rate |
| H-D02-2 | D-02's Pearson r values are stable across windows under H₀ | D-02's Pearson r values change significantly under H₁ | ANOVA on per-window correlations |
| H-D02-3 | D-02's Fisher z CIs overlap across windows under H₀ | D-02's Fisher z CIs do not overlap under H₁ | CI overlap test |
| H-D02-4 | D-02 correctly classifies breakdown type > 50% of the time | D-02 correctly classifies breakdown type > 70% of the time | Binomial test on classification accuracy |

### 8.3 D-03 Hypotheses

| ID | Null Hypothesis (H₀) | Alternative Hypothesis (H₁) | Test |
|----|----------------------|---------------------------|------|
| H-D03-1 | D-03 does not detect compression under natural distributions | D-03 detects compression under artificial clustering | Two-proportion z-test on detection rate |
| H-D03-2 | D-03's excess mass z-scores are below threshold under H₀ | D-03's excess mass z-scores are above threshold under H₁ | One-sided t-test on z-scores |
| H-D03-3 | D-03's dip p-values are above threshold under unimodal distributions | D-03's dip p-values are below threshold under multimodal distributions | One-sided t-test on p-values |
| H-D03-4 | D-03's compression index reflects true clustering proportion | D-03's compression index is calibrated to ground truth | Correlation test between index and ground truth |

---

## 9. Detector Assumptions

### 9.1 Shared Assumptions

| Assumption | Description | Validation |
|-----------|-------------|-----------|
| A-SH-1 | Observations are independent | Verify no autocorrelation in extraction |
| A-SH-2 | Observations are identically distributed within windows | Verify stationarity within windows |
| A-SH-3 | Missing observations are missing at random | Verify no systematic missingness |
| A-SH-4 | Seed-controlled operations are deterministic | Verify across 100 runs |
| A-SH-5 | The observation schema is stable | Verify schema version compatibility |

### 9.2 D-01 Assumptions

| Assumption | Description | Validation |
|-----------|-------------|-----------|
| A-D01-1 | Samples are drawn from continuous distributions | Verify metric values are continuous |
| A-D01-2 | Samples within each window are i.i.d. | Verify independence within windows |
| A-D01-3 | The KS test is appropriate for the metric distributions | Verify with known distributions |
| A-D01-4 | PSI bins adequately represent the distribution | Verify bin count sensitivity |
| A-D01-5 | Consecutive windows are the correct comparison unit | Verify window pair strategy |

### 9.3 D-02 Assumptions

| Assumption | Description | Validation |
|-----------|-------------|-----------|
| A-D02-1 | Paired observations are aligned by source_id | Verify alignment correctness |
| A-D02-2 | Pearson correlation is appropriate for the metric pairs | Verify linearity assumption |
| A-D02-3 | Spearman correlation is appropriate for non-linear relationships | Verify monotonicity assumption |
| A-D02-4 | Fisher z-transform is valid for sample sizes ≥ 10 | Verify CI coverage |
| A-D02-5 | The number of metric pairs is manageable | Verify computational feasibility |

### 9.4 D-03 Assumptions

| Assumption | Description | Validation |
|-----------|-------------|-----------|
| A-D03-1 | Threshold candidates are representative of potential gaming | Verify auto-threshold detection |
| A-D03-2 | The excess mass test correctly identifies clustering | Verify with known clustering |
| A-D03-3 | The dip test approximation is valid | Verify against known multimodal distributions |
| A-D03-4 | Bootstrap p-values are reliable for n ≥ 20 | Verify bootstrap calibration |
| A-D03-5 | Epsilon computation is appropriate | Verify epsilon sensitivity |

---

## 10. Dataset Taxonomy

### 10.1 Taxonomy Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION DATASET TAXONOMY                    │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │    Synthetic      │  │    Real OSS      │  │  Edge-Case    │ │
│  │  (ground truth    │  │  (ecological     │  │  (boundary    │ │
│  │   known)          │  │   validity)      │  │   conditions) │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬────────┘ │
│           │                     │                    │          │
│  ┌────────▼─────────┐  ┌───────▼──────────┐  ┌─────▼────────┐ │
│  │   Adversarial     │  │     Stress       │  │  Temporal    │ │
│  │  (robustness)     │  │  (scalability)   │  │  Evolution   │ │
│  └────────┬─────────┘  └───────┬──────────┘  └─────┬────────┘ │
│           │                     │                    │          │
│           └─────────────────────┼────────────────────┘          │
│                                 │                               │
│                        ┌────────▼────────┐                      │
│                        │  Industrial     │                      │
│                        │  (future)       │                      │
│                        └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Dataset Categories

| Category | Purpose | Ground Truth | Example |
|----------|---------|-------------|---------|
| Synthetic | Controlled experiments with known outcomes | Explicit | Gaussian shift, uniform no-shift |
| Real OSS | Ecological validity in real repositories | Expert-labeled | Django, Flask, NumPy |
| Edge-Case | Boundary conditions and extreme inputs | Explicit | Single observation, identical values |
| Adversarial | Robustness to adversarial manipulation | Explicit | Crafted gaming patterns |
| Stress | Scalability and performance limits | Implicit | 100K observations, 1000 windows |
| Temporal | Evolution over time | Implicit | Repository at different stages |
| Industrial | Future enterprise repositories | TBD | Proprietary repositories |

---

## 11. Validation Dataset Design

### 11.1 Synthetic Datasets

#### 11.1.1 D-01 Synthetic Datasets

| Dataset | Distribution A | Distribution B | Expected Outcome | Purpose |
|---------|---------------|---------------|-----------------|---------|
| SYN-D01-01 | N(0,1) | N(0,1) | No drift | False positive baseline |
| SYN-D01-02 | N(0,1) | N(0.5,1) | Drift (mean_shift) | Mean shift detection |
| SYN-D01-03 | N(0,1) | N(0,0.5) | Drift (variance_collapse) | Variance collapse detection |
| SYN-D01-04 | N(0,1) | Uniform(0,1) | Drift (shape_change) | Shape change detection |
| SYN-D01-05 | N(0,1) | N(0,1) | No drift | Large sample (n=1000) |
| SYN-D01-06 | N(0,1) | N(0.1,1) | No drift | Small shift below threshold |
| SYN-D01-07 | N(0,1) | N(1,1) | Drift | Large shift above threshold |
| SYN-D01-08 | Uniform(0,1) | Bimodal(0,0.5,1) | Drift (shape_change) | Multimodal shift |
| SYN-D01-09 | N(0,1) | N(0,1) | No drift | n=10 (minimum sample) |
| SYN-D01-10 | N(0,1) | N(0,2) | Drift (variance_collapse) | Variance expansion |

#### 11.1.2 D-02 Synthetic Datasets

| Dataset | Pair Relationship | Expected Outcome | Purpose |
|---------|------------------|-----------------|---------|
| SYN-D02-01 | r=0.8 stable | No breakdown | False positive baseline |
| SYN-D02-02 | r=0.8 → r=0.2 | Breakdown (sudden_drop) | Sudden drop detection |
| SYN-D02-03 | r=0.5 → r=-0.5 | Breakdown (sign_reversal) | Sign reversal detection |
| SYN-D02-04 | r=0.8 → r=0.1 over 5 windows | Breakdown (gradual_erosion) | Gradual erosion detection |
| SYN-D02-05 | r=0.5 stable | No breakdown | Moderate correlation stability |
| SYN-D02-06 | r=0.0 stable | No breakdown | Zero correlation stability |
| SYN-D02-07 | r=0.8 → CI non-overlap | Breakdown (confidence_exclusion) | CI exclusion detection |
| SYN-D02-08 | Independent pairs | No breakdown | Noise resilience |
| SYN-D02-09 | r=0.9 → r=0.7 | No breakdown | Below threshold change |
| SYN-D02-10 | r=0.3 → r=-0.3 | Breakdown (sign_reversal) | Weak-to-weak sign reversal |

#### 11.1.3 D-03 Synthetic Datasets

| Dataset | Distribution | Threshold Clustering | Expected Outcome | Purpose |
|---------|-------------|---------------------|-----------------|---------|
| SYN-D03-01 | Uniform(0,100) | None | No compression | False positive baseline |
| SYN-D03-02 | 70% at 50, 30% Uniform | Strong at 50 | Compression detected | Gaming detection |
| SYN-D03-03 | 60% at 100, 40% Uniform | Strong at 100 | Compression detected | Round number gaming |
| SYN-D03-04 | Normal(50,10) | None | No compression | Natural distribution |
| SYN-D03-05 | Bimodal(25,75) | Weak at 50 | Possible compression | Borderline case |
| SYN-D03-06 | 80% at 10, 20% Uniform | Very strong at 10 | Compression detected | Extreme gaming |
| SYN-D03-07 | Uniform(0,100) | None | No compression | Large sample (n=1000) |
| SYN-D03-08 | Mixture(0.5, N(50,1), 0.5, Uniform(0,100)) | Moderate at 50 | Compression detected | Mixed distribution |
| SYN-D03-09 | Uniform(0,100) | None | No compression | Small sample (n=20) |
| SYN-D03-10 | 55% at 75, 45% Uniform | Weak at 75 | Borderline | Sensitivity test |

### 11.2 Real OSS Datasets

| Dataset | Repository | Version | Expected Outcome | Purpose |
|---------|-----------|---------|-----------------|---------|
| OSS-01 | Django/django | Latest | Natural behavior | Ecological validity |
| OSS-02 | pallets/flask | Latest | Natural behavior | Ecological validity |
| OSS-03 | numpy/numpy | Latest | Natural behavior | Ecological validity |
| OSS-04 | scikit-learn/scikit-learn | Latest | Natural behavior | Ecological validity |
| OSS-05 | pandas-dev/pandas | Latest | Natural behavior | Ecological validity |
| OSS-06 | Samragya013/miee | v1.0.1 | Natural behavior | Self-validation |
| OSS-07 | torvalds/linux | Latest | Natural behavior | Large-scale validation |
| OSS-08 | rust-lang/rust | Latest | Natural behavior | Different ecosystem |
| OSS-09 | golang/go | Latest | Natural behavior | Different ecosystem |
| OSS-10 | nodejs/node | Latest | Natural behavior | Different ecosystem |

### 11.3 Edge-Case Datasets

| Dataset | Condition | Expected Outcome | Purpose |
|---------|-----------|-----------------|---------|
| EDGE-01 | n=1 per window | Skip (insufficient) | Minimum sample gate |
| EDGE-02 | n=9 per window | Skip (below threshold) | D-01 sample gate |
| EDGE-03 | n=19 per window | Skip (below threshold) | D-03 sample gate |
| EDGE-04 | All values identical | KS=0, PSI=0 | Degenerate distribution |
| EDGE-05 | Two distinct values only | Bimodal detection | Minimal bimodality |
| EDGE-06 | Single window | Skip (need pairs) | D-01/D-02 window gate |
| EDGE-07 | 100 windows | Full execution | Large window count |
| EDGE-08 | 7 metrics, all present | Full execution | Maximum metric count |
| EDGE-09 | 1 metric only | D-01/D-03 only | Minimum metric count |
| EDGE-10 | Mixed quality observations | Quality filtering | Quality gate behavior |

### 11.4 Adversarial Datasets

| Dataset | Adversarial Pattern | Expected Outcome | Purpose |
|---------|-------------------|-----------------|---------|
| ADV-01 | Gaussian with spike at threshold | D-03 detects compression | Gaming with spike |
| ADV-02 | Correlated pairs with injected noise | D-02 detects breakdown | Noise injection attack |
| ADV-03 | Gradual drift disguised as stable | D-01 detects drift | Camouflaged drift |
| ADV-04 | Two metrics with artificial correlation | D-02 detects breakdown | Artificial correlation |
| ADV-05 | Threshold gaming with offset | D-03 may or may not detect | Offset gaming |
| ADV-06 | Perfect gaming (all values at threshold) | D-03 detects compression | Perfect gaming |

### 11.5 Stress Datasets

| Dataset | Scale | Expected Outcome | Purpose |
|---------|-------|-----------------|---------|
| STRESS-01 | 100K observations | Execution completes | Scalability |
| STRESS-02 | 1000 windows | Execution completes | Window scalability |
| STRESS-03 | 7 metrics × 1000 windows | Execution completes | Metric-window scalability |
| STRESS-04 | 100 thresholds × 7 metrics | Execution completes | Threshold scalability |
| STRESS-05 | 10K bootstrap samples | Execution completes | Bootstrap scalability |

---

## 12. Experimental Methodology

### 12.1 Experiment Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPERIMENT LIFECYCLE                           │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │ 1. Design│──▶│2.Prepare │──▶│3.Execute │──▶│4.Analyze │   │
│  │ Protocol │   │ Datasets │   │Detector  │   │ Results  │   │
│  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘   │
│                                                      │          │
│                                         ┌────────────▼────────┐ │
│                                         │ 5. Report Findings  │ │
│                                         └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 Repository Preparation

| Step | Description | Output |
|------|-------------|--------|
| 1 | Clone repository at specified commit | Local repository |
| 2 | Extract commit metadata | Commit list with timestamps |
| 3 | Extract file metadata | File-level observations |
| 4 | Compute ground truth labels | Labeled anomalies |

### 12.3 Observation Extraction

| Step | Description | Output |
|------|-------------|--------|
| 1 | Configure extraction parameters | ExtractionConfig |
| 2 | Extract observations using Observation Engine | ObservationCollection |
| 3 | Validate observation schema conformance | ValidationReport |
| 4 | Record extraction provenance | Provenance |

### 12.4 Window Generation

| Step | Description | Output |
|------|-------------|--------|
| 1 | Configure windowing strategy | WindowConfig |
| 2 | Generate windows | list<ObservationWindow> |
| 3 | Validate minimum sample sizes | WindowValidationReport |
| 4 | Record window boundaries | WindowBoundaries |

### 12.5 Detector Execution

| Step | Description | Output |
|------|-------------|--------|
| 1 | Configure detector parameters | DetectorConfig |
| 2 | Execute detector | DetectorResult |
| 3 | Collect evidence | EvidencePackage |
| 4 | Record execution timing | TimingReport |

### 12.6 Result Comparison

| Step | Description | Output |
|------|-------------|--------|
| 1 | Compare detector output to ground truth | ComparisonReport |
| 2 | Compute evaluation metrics | MetricsReport |
| 3 | Compute confidence intervals | CIReport |
| 4 | Generate statistical summary | StatisticalSummary |

### 12.7 Acceptance Analysis

| Step | Description | Output |
|------|-------------|--------|
| 1 | Evaluate against acceptance criteria | AcceptanceReport |
| 2 | Identify failures | FailureList |
| 3 | Classify failures by severity | SeverityReport |
| 4 | Generate go/no-go recommendation | Recommendation |

---

## 13. D-01 Validation Protocol

### 13.1 Scientific Objective

D-01 detects distributional drift — significant changes in the distribution of metric values between consecutive windows. The scientific objective is to demonstrate that D-01 correctly identifies distributional shifts while maintaining a controlled false positive rate.

### 13.2 Validation Experiments

| Experiment | Dataset | Procedure | Acceptance Criterion |
|-----------|---------|-----------|---------------------|
| D01-EXP-01 | SYN-D01-01 (no drift) | Run D-01 on identical distributions | FPR ≤ 0.05 |
| D01-EXP-02 | SYN-D01-02 (mean shift) | Run D-01 on shifted distributions | TPR ≥ 0.80 |
| D01-EXP-03 | SYN-D01-03 (variance collapse) | Run D-01 on variance-changed distributions | TPR ≥ 0.80 |
| D01-EXP-04 | SYN-D01-04 (shape change) | Run D-01 on shape-changed distributions | TPR ≥ 0.80 |
| D01-EXP-05 | SYN-D01-05 (large sample) | Run D-01 on large samples | Correct detection |
| D01-EXP-06 | SYN-D01-06 (small shift) | Run D-01 on sub-threshold shift | FPR ≤ 0.05 |
| D01-EXP-07 | SYN-D01-07 (large shift) | Run D-01 on supra-threshold shift | TPR ≥ 0.95 |
| D01-EXP-08 | SYN-D01-08 (bimodal) | Run D-01 on multimodal shift | TPR ≥ 0.80 |
| D01-EXP-09 | SYN-D01-09 (minimum sample) | Run D-01 on minimum samples | Correct behavior |
| D01-EXP-10 | SYN-D01-10 (variance expansion) | Run D-01 on variance expansion | TPR ≥ 0.80 |
| D01-EXP-11 | OSS-01 through OSS-10 | Run D-01 on real repositories | No crashes, valid output |
| D01-EXP-12 | EDGE-01 through EDGE-10 | Run D-01 on edge cases | Correct handling |
| D01-EXP-13 | ADV-01 through ADV-06 | Run D-01 on adversarial data | Robust behavior |

### 13.3 Evaluation Procedure

```
D-01 EVALUATION PROCEDURE:

FOR each experiment:
  1. Generate or load dataset
  2. Configure detector with seed=42
  3. Execute D-01
  4. Record: drift_detected, drift_magnitude, drift_direction
  5. Compare to ground truth
  6. Compute: TP, FP, TN, FN
  7. Compute: precision, recall, F1, FPR, TNR
  8. Record timing

AGGREGATE across experiments:
  9. Compute mean and CI for each metric
  10. Compare to acceptance thresholds
  11. Generate acceptance report
```

### 13.4 Drift Direction Validation

| Direction | Ground Truth Definition | Validation Method |
|-----------|----------------------|-------------------|
| mean_shift | |mean_B - mean_A| > 0.5 × std_A | Classification accuracy |
| variance_collapse | var_B / var_A < 0.5 | Classification accuracy |
| shape_change | Neither mean_shift nor variance_collapse | Classification accuracy |

### 13.5 Known Limitations

| Limitation | Description | Impact | Mitigation |
|-----------|-------------|--------|-----------|
| Minimum sample | KS test requires ≥10 per window | Cannot detect drift in small windows | Document as constraint |
| Unimodal assumption | KS test assumes continuous distributions | May miss discrete distribution changes | Not applicable for MIIE metrics |
| Consecutive windows | Only compares adjacent windows | May miss non-consecutive drift | Document as design choice |
| No magnitude threshold | Any statistically significant change is flagged | May flag trivial changes | Use PSI as secondary criterion |

---

## 14. D-02 Validation Protocol

### 14.1 Scientific Objective

D-02 detects correlation breakdown — significant changes in correlation between metric pairs across windows. The scientific objective is to demonstrate that D-02 correctly identifies correlation changes while maintaining a controlled false positive rate.

### 14.2 Validation Experiments

| Experiment | Dataset | Procedure | Acceptance Criterion |
|-----------|---------|-----------|---------------------|
| D02-EXP-01 | SYN-D02-01 (stable r=0.8) | Run D-02 on stable correlation | FPR ≤ 0.05 |
| D02-EXP-02 | SYN-D02-02 (r=0.8→0.2) | Run D-02 on sudden drop | TPR ≥ 0.80 |
| D02-EXP-03 | SYN-D02-03 (r=0.5→-0.5) | Run D-02 on sign reversal | TPR ≥ 0.80 |
| D02-EXP-04 | SYN-D02-04 (gradual erosion) | Run D-02 on gradual decline | TPR ≥ 0.70 |
| D02-EXP-05 | SYN-D02-05 (stable r=0.5) | Run D-02 on moderate stability | FPR ≤ 0.05 |
| D02-EXP-06 | SYN-D02-06 (stable r=0.0) | Run D-02 on zero correlation | FPR ≤ 0.05 |
| D02-EXP-07 | SYN-D02-07 (CI non-overlap) | Run D-02 on CI exclusion | TPR ≥ 0.80 |
| D02-EXP-08 | SYN-D02-08 (independent) | Run D-02 on noise | FPR ≤ 0.05 |
| D02-EXP-09 | SYN-D02-09 (below threshold) | Run D-02 on sub-threshold change | FPR ≤ 0.05 |
| D02-EXP-10 | SYN-D02-10 (weak sign reversal) | Run D-02 on weak reversal | TPR ≥ 0.70 |
| D02-EXP-11 | OSS-01 through OSS-10 | Run D-02 on real repositories | No crashes, valid output |
| D02-EXP-12 | EDGE-01 through EDGE-10 | Run D-02 on edge cases | Correct handling |

### 14.3 Breakdown Type Validation

| Type | Ground Truth Definition | Validation Method |
|------|----------------------|-------------------|
| sudden_drop | |r_{k+1} - r_k| > 0.3 | Classification accuracy |
| sign_reversal | sign(r_k) ≠ sign(r_{k+1}), |r_k| > 0.2, |r_{k+1}| > 0.2 | Classification accuracy |
| gradual_erosion | slope < -0.1 over ≥4 windows | Classification accuracy |
| confidence_exclusion | CI_k ∩ CI_{k+1} = ∅ | Classification accuracy |

### 14.4 Known Limitations

| Limitation | Description | Impact | Mitigation |
|-----------|-------------|--------|-----------|
| Paired observations | Requires same source for both metrics | Cannot analyze metrics from different sources | Document as constraint |
| Minimum pairs | Requires ≥10 paired observations | Cannot detect in small windows | Document as constraint |
| No multiple comparison | Does not correct for O(K²) tests | May have elevated FPR for many pairs | Document as limitation |
| Pearson linearity | Assumes linear relationship | May miss non-linear breakdowns | Spearman as complementary |

---

## 15. D-03 Validation Protocol

### 15.1 Scientific Objective

D-03 detects threshold compression — artificial clustering of values around specific thresholds. The scientific objective is to demonstrate that D-03 correctly identifies gaming patterns while maintaining a controlled false positive rate.

### 15.2 Validation Experiments

| Experiment | Dataset | Procedure | Acceptance Criterion |
|-----------|---------|-----------|---------------------|
| D03-EXP-01 | SYN-D03-01 (uniform) | Run D-03 on natural distribution | FPR ≤ 0.05 |
| D03-EXP-02 | SYN-D03-02 (strong clustering) | Run D-03 on artificial clustering | TPR ≥ 0.80 |
| D03-EXP-03 | SYN-D03-03 (round number) | Run D-03 on round number gaming | TPR ≥ 0.80 |
| D03-EXP-04 | SYN-D03-04 (normal) | Run D-03 on natural normal | FPR ≤ 0.05 |
| D03-EXP-05 | SYN-D03-05 (bimodal) | Run D-03 on borderline case | Correct behavior |
| D03-EXP-06 | SYN-D03-06 (extreme gaming) | Run D-03 on extreme clustering | TPR ≥ 0.95 |
| D03-EXP-07 | SYN-D03-07 (large sample) | Run D-03 on large uniform | FPR ≤ 0.05 |
| D03-EXP-08 | SYN-D03-08 (mixture) | Run D-03 on mixed distribution | TPR ≥ 0.70 |
| D03-EXP-09 | SYN-D03-09 (small sample) | Run D-03 on minimum sample | Correct handling |
| D03-EXP-10 | SYN-D03-10 (borderline) | Run D-03 on borderline clustering | Correct behavior |
| D03-EXP-11 | OSS-01 through OSS-10 | Run D-03 on real repositories | No crashes, valid output |
| D03-EXP-12 | EDGE-01 through EDGE-10 | Run D-03 on edge cases | Correct handling |
| D03-EXP-13 | ADV-01 through ADV-06 | Run D-03 on adversarial data | Robust behavior |

### 15.3 Compression Index Calibration

| Metric | Ground Truth | Expected D-03 Output | Calibration Test |
|--------|-------------|---------------------|-----------------|
| 0% clustering | p_hat = 0.0 | compression_index ≈ 0.0 | Correlation test |
| 50% clustering | p_hat = 0.5 | compression_index ≈ 0.5 | Correlation test |
| 70% clustering | p_hat = 0.7 | compression_index ≈ 0.7 | Correlation test |
| 90% clustering | p_hat = 0.9 | compression_index ≈ 0.9 | Correlation test |

### 15.4 Known Limitations

| Limitation | Description | Impact | Mitigation |
|-----------|-------------|--------|-----------|
| Threshold candidates | Auto-detection may miss thresholds | May miss gaming at non-standard thresholds | Document as constraint |
| Minimum sample | Excess Mass requires ≥20 | Cannot detect in small windows | Document as constraint |
| Bootstrap approximation | Dip test uses KS approximation | Not exact dip test | Document as approximation |
| Epsilon sensitivity | Epsilon computation affects band width | Results sensitive to epsilon | Sensitivity analysis |
| Round number bias | Auto-thresholds favor round numbers | May miss non-round gaming | Document as design choice |

---

## 16. Statistical Evaluation Metrics

### 16.1 Classification Metrics

| Metric | Definition | Formula | Appropriate For |
|--------|-----------|---------|-----------------|
| Precision | Proportion of positive predictions that are correct | TP / (TP + FP) | When false positives are costly |
| Recall (Sensitivity) | Proportion of actual positives that are detected | TP / (TP + FN) | When false negatives are costly |
| F1 Score | Harmonic mean of precision and recall | 2 × P × R / (P + R) | Balanced evaluation |
| Specificity | Proportion of actual negatives that are correctly identified | TN / (TN + FP) | When false positives must be controlled |
| False Positive Rate | Proportion of actual negatives incorrectly identified as positive | FP / (FP + TN) = 1 - Specificity | Type I error characterization |
| False Negative Rate | Proportion of actual positives incorrectly identified as negative | FN / (FN + TP) = 1 - Recall | Type II error characterization |

### 16.2 Statistical Metrics

| Metric | Definition | Appropriate For |
|--------|-----------|-----------------|
| KS statistic | Maximum difference between empirical CDFs | D-01 drift magnitude |
| PSI | Population stability index | D-01 drift magnitude |
| Pearson r | Linear correlation coefficient | D-02 correlation strength |
| Spearman rho | Rank correlation coefficient | D-02 monotonic correlation |
| Fisher z | Fisher z-transform of Pearson r | D-02 CI computation |
| Excess Mass z | Z-score for threshold clustering | D-03 compression strength |
| Dip statistic | Measure of multimodality | D-03 multimodality evidence |
| Compression index | Proportion of values in threshold band | D-03 compression magnitude |

### 16.3 Quality Metrics

| Metric | Definition | Appropriate For |
|--------|-----------|-----------------|
| Detection latency | Time from observation to detection | Performance evaluation |
| Confidence calibration | Agreement between confidence and correctness | Reliability evaluation |
| Reproducibility score | Proportion of identical results across runs | Determinism evaluation |
| Robustness score | Performance under adversarial/edge conditions | Robustness evaluation |

### 16.4 Why Each Metric Is Appropriate

| Metric | Justification |
|--------|--------------|
| Precision | Controls the proportion of false alarms; critical for user trust |
| Recall | Controls the proportion of missed detections; critical for integrity |
| F1 | Balances precision and recall; appropriate when both errors are important |
| FPR | Directly measures Type I error; required for hypothesis testing |
| FNR | Directly measures Type II error; required for power analysis |
| Specificity | Measures the ability to correctly identify non-anomalies |
| Confidence calibration | Ensures that reported confidence reflects actual reliability |
| Reproducibility score | Ensures deterministic behavior; scientific requirement |

---

## 17. Acceptance Criteria

### 17.1 D-01 Acceptance Criteria

| ID | Criterion | Threshold | Measurement |
|----|-----------|-----------|-------------|
| AC-D01-01 | False Positive Rate (no drift) | FPR ≤ 0.05 | SYN-D01-01 |
| AC-D01-02 | True Positive Rate (mean shift) | TPR ≥ 0.80 | SYN-D01-02 |
| AC-D01-03 | True Positive Rate (variance collapse) | TPR ≥ 0.80 | SYN-D01-03 |
| AC-D01-04 | True Positive Rate (shape change) | TPR ≥ 0.80 | SYN-D01-04 |
| AC-D01-05 | Direction classification accuracy | ≥ 70% | SYN-D01-02,03,04 |
| AC-D01-06 | Reproducibility | 100% identical | 100 runs |
| AC-D01-07 | Edge case handling | No crashes | EDGE-01 through EDGE-10 |
| AC-D01-08 | Real repository execution | No crashes | OSS-01 through OSS-10 |

### 17.2 D-02 Acceptance Criteria

| ID | Criterion | Threshold | Measurement |
|----|-----------|-----------|-------------|
| AC-D02-01 | False Positive Rate (stable correlation) | FPR ≤ 0.05 | SYN-D02-01 |
| AC-D02-02 | True Positive Rate (sudden drop) | TPR ≥ 0.80 | SYN-D02-02 |
| AC-D02-03 | True Positive Rate (sign reversal) | TPR ≥ 0.80 | SYN-D02-03 |
| AC-D02-04 | True Positive Rate (gradual erosion) | TPR ≥ 0.70 | SYN-D02-04 |
| AC-D02-05 | Breakdown type classification accuracy | ≥ 60% | SYN-D02-02,03,04,07 |
| AC-D02-06 | Reproducibility | 100% identical | 100 runs |
| AC-D02-07 | Edge case handling | No crashes | EDGE-01 through EDGE-10 |
| AC-D02-08 | Real repository execution | No crashes | OSS-01 through OSS-10 |

### 17.3 D-03 Acceptance Criteria

| ID | Criterion | Threshold | Measurement |
|----|-----------|-----------|-------------|
| AC-D03-01 | False Positive Rate (natural distribution) | FPR ≤ 0.05 | SYN-D03-01 |
| AC-D03-02 | True Positive Rate (strong clustering) | TPR ≥ 0.80 | SYN-D03-02 |
| AC-D03-03 | True Positive Rate (round number gaming) | TPR ≥ 0.80 | SYN-D03-03 |
| AC-D03-04 | True Positive Rate (extreme gaming) | TPR ≥ 0.95 | SYN-D03-06 |
| AC-D03-05 | Compression index calibration | r ≥ 0.80 | SYN-D03-02,03,06,08 |
| AC-D03-06 | Reproducibility | 100% identical | 100 runs |
| AC-D03-07 | Edge case handling | No crashes | EDGE-01 through EDGE-10 |
| AC-D03-08 | Real repository execution | No crashes | OSS-01 through OSS-10 |

### 17.4 Cross-Detector Acceptance Criteria

| ID | Criterion | Threshold | Measurement |
|----|-----------|-----------|-------------|
| AC-XD-01 | Deterministic execution | 100% identical outputs | 100 runs with seed=42 |
| AC-XD-02 | No cross-detector interference | Independent results | Parallel vs. sequential execution |
| AC-XD-03 | Evidence traceability | 100% of results have evidence | Evidence audit |
| AC-XD-04 | Confidence calibration | 90% CI contains true value ≥85% of time | Calibration test |

---

## 18. False Positive Analysis

### 18.1 Purpose

False positive analysis characterizes the rate at which detectors incorrectly report anomalies when none exist. This is critical for user trust — excessive false positives cause alarm fatigue.

### 18.2 D-01 False Positive Scenarios

| Scenario | Description | Expected FPR |
|----------|-------------|-------------|
| Identical distributions | Same distribution in both windows | ≤ 0.05 |
| Same mean, different variance | Only variance changes (below threshold) | ≤ 0.05 |
| Random fluctuations | Small random differences between windows | ≤ 0.05 |
| Small sample noise | Natural variation with small n | ≤ 0.10 |
| Different seeds | Same data, different random seeds | ≤ 0.05 |

### 18.3 D-02 False Positive Scenarios

| Scenario | Description | Expected FPR |
|----------|-------------|-------------|
| Stable correlation | Same r across all windows | ≤ 0.05 |
| Zero correlation | r=0 stable across windows | ≤ 0.05 |
| Weak correlation | r=0.3 stable across windows | ≤ 0.05 |
| Different seeds | Same data, different random seeds | ≤ 0.05 |

### 18.4 D-03 False Positive Scenarios

| Scenario | Description | Expected FPR |
|----------|-------------|-------------|
| Uniform distribution | No clustering | ≤ 0.05 |
| Normal distribution | Natural bell curve | ≤ 0.05 |
| Bimodal (natural) | Natural bimodality without gaming | ≤ 0.10 |
| Different seeds | Same data, different random seeds | ≤ 0.05 |

### 18.5 False Positive Mitigation

| Strategy | Description | Detector |
|----------|-------------|----------|
| Threshold tuning | Adjust significance thresholds | All |
| Multiple comparison correction | Bonferroni or FDR correction | D-02 |
| Minimum sample enforcement | Skip when sample too small | All |
| Dual-criterion detection | Require both KS and PSI to agree | D-01 |

---

## 19. False Negative Analysis

### 19.1 Purpose

False negative analysis characterizes the rate at which detectors fail to report anomalies that exist. This is critical for integrity — missed detections leave problems undetected.

### 19.2 D-01 False Negative Scenarios

| Scenario | Description | Expected FNR |
|----------|-------------|-------------|
| Very small shift | Mean shift of 0.1σ | High (expected) |
| Gradual drift | Slow, monotonic shift | Moderate |
| Variance-only change | Same mean, different variance | Moderate |
| Small sample | n=10 per window | High (expected) |
| Multimodal → unimodal | Shape change without mean change | Moderate |

### 19.3 D-02 False Negative Scenarios

| Scenario | Description | Expected FNR |
|----------|-------------|-------------|
| Very small change | r changes by 0.05 | High (expected) |
| Gradual erosion over few windows | K=3 windows | Moderate |
| Non-linear breakdown | Non-linear relationship change | High (Pearson misses) |
| Small paired sample | n=10 pairs | Moderate |

### 19.4 D-03 False Negative Scenarios

| Scenario | Description | Expected FNR |
|----------|-------------|-------------|
| Weak clustering | 55% at threshold | High (expected) |
| Non-round threshold | Gaming at non-standard values | Moderate |
| Small sample | n=20 | Moderate |
| Distributed gaming | Values spread across multiple thresholds | High |

### 19.5 False Negative Mitigation

| Strategy | Description | Detector |
|----------|-------------|----------|
| Lower thresholds | More sensitive detection | All |
| Larger samples | More observations per window | All |
| Multiple tests | Combine KS + PSI | D-01 |
| Multiple correlations | Combine Pearson + Spearman | D-02 |
| Multiple criteria | Combine Excess Mass + Dip | D-03 |

---

## 20. Stress Testing Methodology

### 20.1 Purpose

Stress testing evaluates detector behavior under extreme conditions — large datasets, many windows, many metrics, and high computational load.

### 20.2 Stress Test Matrix

| Test | Scale | Resource Limit | Expected Behavior |
|------|-------|---------------|-------------------|
| ST-01 | 100K observations | < 100MB memory | Completes within memory |
| ST-02 | 1000 windows | < 5s per detector | Completes within time |
| ST-03 | 7 metrics × 1000 windows | < 500MB memory | Completes within memory |
| ST-04 | 100 thresholds × 7 metrics | < 10s per detector | Completes within time |
| ST-05 | 10K bootstrap samples | < 60s per detector | Completes within time |
| ST-06 | All datasets combined | < 300s total | Completes within time |

### 20.3 Stress Test Evaluation

| Metric | Target | Measurement |
|--------|--------|-------------|
| Peak memory | < 100MB for 100K obs | Memory profiling |
| Execution time | < 5s per detector for 1000 windows | Timing measurement |
| Bootstrap time | < 60s for 10K samples | Timing measurement |
| No crashes | 0 crashes across all tests | Crash count |

---

## 21. Adversarial Validation

### 21.1 Purpose

Adversarial validation evaluates detector robustness against crafted inputs designed to evade detection or produce misleading results.

### 21.2 Adversarial Patterns

| Pattern | Description | Expected Detector Behavior |
|---------|-------------|--------------------------|
| Spike at threshold | Values clustered at threshold with offset | D-03 detects if excess mass is sufficient |
| Noise injection | Random noise added to correlated data | D-02 detects if correlation drops sufficiently |
| Camouflaged drift | Gradual drift within natural variation | D-01 detects if drift exceeds KS threshold |
| Artificial correlation | Two metrics with injected linear relationship | D-02 detects correlation change |
| Offset gaming | Values at threshold ± small offset | D-03 may or may not detect (epsilon dependent) |
| Perfect gaming | All values exactly at threshold | D-03 detects strong compression |

### 21.3 Adversarial Evaluation Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Detection of obvious gaming | ≥ 90% | ADV-01, ADV-06 |
| Robustness to noise | FPR ≤ 0.10 | ADV-02 |
| Detection of camouflaged drift | ≥ 70% | ADV-03 |
| No misleading outputs | 100% | All adversarial datasets |

---

## 22. Regression Validation

### 22.1 Purpose

Regression validation ensures that detector outputs remain stable across versions. Changes in detector behavior must be intentional and documented.

### 22.2 Regression Test Types

| Type | Description | Frequency |
|------|-------------|-----------|
| Cross-version comparison | Compare v1.0.1 vs. v1.5 outputs | Every release |
| Seed reproducibility | Same seed, same output | Every commit |
| Benchmark stability | Benchmark results within tolerance | Every release |
| Configuration stability | Same config, same output | Every commit |

### 22.3 Regression Tolerance

| Metric | Tolerance | Measurement |
|--------|-----------|-------------|
| Drift detection | Identical boolean | Cross-version comparison |
| Drift magnitude | Δ ≤ 0.01 | Cross-version comparison |
| Breakdown detection | Identical boolean | Cross-version comparison |
| Breakdown type | Identical string | Cross-version comparison |
| Compression detection | Identical boolean | Cross-version comparison |
| Compression index | Δ ≤ 0.01 | Cross-version comparison |

### 22.4 Regression Investigation Triggers

| Trigger | Action |
|---------|--------|
| Detection result changes | Investigate root cause |
| Magnitude changes by > 0.01 | Investigate root cause |
| New failure modes appear | Investigate root cause |
| Performance regresses by > 20% | Investigate root cause |

---

## 23. Reproducibility Requirements

### 23.1 Determinism Requirements

| Requirement | Description | Verification |
|------------|-------------|-------------|
| Same seed → same output | Identical results for identical seed | 100-run test |
| Same data → same output | Identical results for identical data | Cross-run comparison |
| Same config → same output | Identical results for identical config | Config variation test |
| Platform independence | Same results across OS | Cross-platform comparison |

### 23.2 Reproducibility Test Protocol

```
REPRODUCIBILITY TEST:

1. Configure detector with seed=42
2. Execute on dataset D
3. Record output O₁
4. Reset detector state
5. Execute on dataset D with seed=42
6. Record output O₂
7. Assert O₁ == O₂ (byte-identical)
8. Repeat 100 times
9. Report: 100/100 identical (100%)
```

### 23.3 Reproducibility Failure Investigation

| Failure Type | Investigation | Resolution |
|-------------|--------------|-----------|
| Non-deterministic random | Check seed propagation | Fix seed management |
| Floating-point non-determinism | Check platform differences | Use deterministic operations |
| Ordering non-determinism | Check sort stability | Use stable sort |
| Hash non-determinism | Check hash randomization | Use deterministic hash |

---

## 24. Threats to Validity

### 24.1 Internal Validity

| Threat | Description | Mitigation |
|--------|-------------|-----------|
| Implementation bugs | Code may not match specification | Unit tests, code review |
| Test dataset bias | Synthetic data may not represent reality | Real OSS datasets |
| Parameter tuning bias | Thresholds may be overfit to test data | Cross-validation |
| Confirmation bias | Experimenter may interpret results favorably | Pre-registered hypotheses |

### 24.2 External Validity

| Threat | Description | Mitigation |
|--------|-------------|-----------|
| Dataset representativeness | Test datasets may not represent all repositories | Diverse dataset battery |
| Metric generality | Results may not generalize to all metrics | All 7 metrics tested |
| Repository diversity | Results may not generalize to all repositories | 10+ real repositories |
| Temporal stability | Results may change over time | Temporal validation |

### 24.3 Construct Validity

| Threat | Description | Mitigation |
|--------|-------------|-----------|
| Ground truth accuracy | Synthetic ground truth may not match reality | Expert validation |
| Metric appropriateness | Evaluation metrics may not capture desired properties | Multiple metrics |
| Statistical assumptions | Assumptions may not hold | Assumption validation |

### 24.4 Reliability Validity

| Threat | Description | Mitigation |
|--------|-------------|-----------|
| Platform dependence | Results may vary across platforms | Cross-platform testing |
| Version dependence | Results may depend on library versions | Pin versions |
| Random seed dependence | Results may depend on seed | Multiple seeds tested |

---

## 25. Bias Analysis

### 25.1 Selection Bias

| Source | Description | Mitigation |
|--------|-------------|-----------|
| Repository selection | Test repositories may not be representative | Diverse ecosystem coverage |
| Time period selection | Test period may not be representative | Multiple time periods |
| Metric selection | Test metrics may not be representative | All 7 metrics tested |

### 25.2 Measurement Bias

| Source | Description | Mitigation |
|--------|-------------|-----------|
| Ground truth labeling | Synthetic labels may not match reality | Expert validation |
| Threshold selection | Detection thresholds may be biased | Sensitivity analysis |
| Sample size bias | Small samples may produce unreliable results | Minimum sample gates |

### 25.3 Reporting Bias

| Source | Description | Mitigation |
|--------|-------------|-----------|
| Publication bias | Positive results may be overrepresented | Report all results |
| cherry-picking | Favorable datasets may be selected | Pre-registered protocol |
| Metric selection | Favorable metrics may be reported | Report all metrics |

---

## 26. Statistical Power Considerations

### 26.1 Power Analysis

| Detector | Effect Size | Sample Size | Power | Alpha |
|----------|------------|-------------|-------|-------|
| D-01 | Medium (d=0.5) | 10 per window | 0.80 | 0.05 |
| D-01 | Large (d=0.8) | 10 per window | 0.95 | 0.05 |
| D-01 | Small (d=0.2) | 10 per window | 0.30 | 0.05 |
| D-02 | Medium (r=0.3) | 10 paired | 0.80 | 0.05 |
| D-02 | Large (r=0.5) | 10 paired | 0.95 | 0.05 |
| D-03 | Medium (p_hat=0.6) | 20 | 0.80 | 0.05 |
| D-03 | Large (p_hat=0.8) | 20 | 0.95 | 0.05 |

### 26.2 Power Limitations

| Limitation | Description | Impact |
|-----------|-------------|--------|
| Small sample | n=10 for D-01/D-02 may have low power | May miss small effects |
| Multiple comparisons | O(K²) pairs in D-02 reduces effective power | May miss weak breakdowns |
| Bootstrap variability | D-03 bootstrap may have variable power | May miss weak clustering |

### 26.3 Power Recommendations

| Recommendation | Description |
|---------------|-------------|
| Increase sample size | Use ≥30 observations per window when possible |
| Reduce multiple comparisons | Limit to pre-specified metric pairs |
| Increase bootstrap samples | Use ≥1000 for D-03 |
| Use one-sided tests | Where directional hypothesis is appropriate |

---

## 27. Reporting Requirements

### 27.1 Required Report Sections

| Section | Content |
|---------|---------|
| Executive Summary | Key findings, go/no-go recommendation |
| Methodology | Dataset descriptions, experiment procedures |
| Results | Per-detector results with metrics and CIs |
| Discussion | Interpretation, limitations, implications |
| Appendix | Raw data, additional analyses |

### 27.2 Per-Detector Report Template

| Field | Description |
|-------|-------------|
| Detector ID | D-01, D-02, or D-03 |
| Dataset | Description of dataset used |
| Sample size | Number of observations |
| Windows | Number of windows |
| Detection result | Boolean: detected or not |
| Effect size | Magnitude of detected effect |
| Confidence | Confidence in detection |
| Timing | Execution time |
| Reproducibility | Whether result is reproducible |

### 27.3 Statistical Reporting Standards

| Standard | Description |
|----------|-------------|
| Effect sizes | Always report effect sizes, not just p-values |
| Confidence intervals | Always report 95% CIs for key metrics |
| Sample sizes | Always report sample sizes |
| Assumptions | Always state statistical assumptions |
| Limitations | Always acknowledge limitations |

---

## 28. Validation Artifacts

### 28.1 Required Artifacts

| Artifact | Description | Location |
|----------|-------------|----------|
| Validation datasets | Synthetic, real, edge-case, adversarial | benchmarks/datasets/validation/ |
| Ground truth labels | Known outcomes for each dataset | benchmarks/ground_truth/validation/ |
| Experiment scripts | Reproducible experiment execution | scripts/validation/ |
| Result reports | Per-experiment results | docs/reports/validation/ |
| Statistical analyses | Detailed statistical analyses | docs/reports/validation/ |
| Regression baselines | Cross-version comparison baselines | benchmarks/results/baseline/ |

### 28.2 Artifact Versioning

| Artifact | Versioning Strategy |
|----------|-------------------|
| Datasets | Semantic versioning (major.minor.patch) |
| Ground truth | Tied to dataset version |
| Experiment scripts | Tied to MIIE version |
| Results | Timestamped, tied to MIIE version |

---

## 29. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|------------|--------|-----------|
| R-1 | Synthetic data does not represent reality | Medium | High | Real OSS datasets |
| R-2 | Ground truth labels are inaccurate | Low | High | Expert validation |
| R-3 | Statistical assumptions violated | Medium | Medium | Assumption testing |
| R-4 | Power insufficient for small effects | High | Medium | Increase sample sizes |
| R-5 | Multiple comparison inflation | Medium | Medium | FDR correction |
| R-6 | Platform-dependent results | Low | Medium | Cross-platform testing |
| R-7 | Regression detection failure | Low | High | Comprehensive regression suite |
| R-8 | Adversarial evasion | Medium | Medium | Adversarial dataset battery |

---

## 30. Future Detector Validation Strategy

### 30.1 New Detector Validation

| Step | Description |
|------|-------------|
| 1 | Define scientific objectives for new detector |
| 2 | Define hypotheses and acceptance criteria |
| 3 | Design validation datasets |
| 4 | Execute validation protocol |
| 5 | Report results |
| 6 | Compare to existing detector baselines |

### 30.2 Validation Protocol Evolution

| Version | Planned Enhancements |
|---------|---------------------|
| v1.1 | Add cross-validation, expand real OSS datasets |
| v1.2 | Add temporal validation, industrial datasets |
| v2.0 | Add ML detector validation, streaming validation |

---

## 31. Glossary

| Term | Definition |
|------|-----------|
| False Positive | Detector reports anomaly when none exists (Type I error) |
| False Negative | Detector fails to report existing anomaly (Type II error) |
| Precision | Proportion of positive predictions that are correct |
| Recall | Proportion of actual positives that are detected |
| F1 Score | Harmonic mean of precision and recall |
| Specificity | Proportion of actual negatives correctly identified |
| Statistical Power | Probability of detecting a true effect (1 - β) |
| Effect Size | Magnitude of the difference between groups |
| Confidence Interval | Range of plausible values for a parameter |
| Ground Truth | Known correct answer for validation |
| Synthetic Data | Artificially generated data with known properties |
| Reproducibility | Ability to produce identical results across runs |
| Determinism | Property that same input always produces same output |
| Bootstrap | Resampling technique for estimating sampling distributions |

---

## 32. Appendix

### A. Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| PRD-v1.5-OE | docs/architecture/observation_engine/PRD_v1.5_Observation_Engine.md | Parent requirement |
| OEAS-v1.5 | docs/architecture/observation_engine/OEAS_v1.5_Observation_Engine.md | Architecture specification |
| ODSS-v1.0 | docs/architecture/observation_engine/ODSS_v1.0_Observation_Data_Schema_Specification.md | Data schema |
| DES-v2.0 | docs/architecture/detectors/DES_v2.0_Detector_Execution_Specification.md | Execution specification |

### B. Dataset Inventory

| Category | Count | Purpose |
|----------|-------|---------|
| Synthetic D-01 | 10 | D-01 controlled experiments |
| Synthetic D-02 | 10 | D-02 controlled experiments |
| Synthetic D-03 | 10 | D-03 controlled experiments |
| Real OSS | 10 | Ecological validity |
| Edge-Case | 10 | Boundary conditions |
| Adversarial | 6 | Robustness testing |
| Stress | 5 | Scalability testing |
| **Total** | **61** | **Comprehensive validation** |

### C. Acceptance Criteria Summary

| Detector | Total Criteria | Pass Threshold |
|----------|---------------|----------------|
| D-01 | 8 | All 8 pass |
| D-02 | 8 | All 8 pass |
| D-03 | 8 | All 8 pass |
| Cross-detector | 4 | All 4 pass |
| **Total** | **28** | **All 28 pass** |

### D. Validation Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                 VALIDATION WORKFLOW OVERVIEW                      │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │  Dataset  │──▶│ Extract  │──▶│  Detect  │──▶│ Evaluate │   │
│  │  Loading  │   │ Obs.     │   │          │   │          │   │
│  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘   │
│                                                      │          │
│                              ┌───────────────────────┼───────┐ │
│                              │                       │       │ │
│                        ┌─────▼─────┐  ┌─────────────▼─────┐ │ │
│                        │  D-01     │  │      D-02         │ │ │
│                        │  D-03     │  │                   │ │ │
│                        └─────┬─────┘  └─────────┬─────────┘ │ │
│                              │                   │           │ │
│                              └───────────┬───────┘           │ │
│                                          │                   │ │
│                                    ┌─────▼─────┐             │ │
│                                    │  Compare  │             │ │
│                                    │  to GT    │             │ │
│                                    └─────┬─────┘             │ │
│                                          │                   │ │
│                                    ┌─────▼─────┐             │ │
│                                    │  Report   │             │ │
│                                    │  Results  │             │ │
│                                    └───────────┘             │ │
│                                                              │ │
└─────────────────────────────────────────────────────────────────┘
```

---

*End of Document*

---

**Document History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-29 | MIIE Engineering | Initial scientific validation protocol |

**Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Research Lead | | | |
| Science Lead | | | |
| Governance | | | |
