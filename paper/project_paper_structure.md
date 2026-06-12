# Project Paper Structure

**Document Version:** 1.0  
**Date:** 2026-06-08  
**Target Venue:** ICSE / MSR  
**Paper Title:**测量完整性：评估软件工程指标持续有效性的工具

---

## Abstract

[TO BE WRITTEN]

---

## 1. Introduction

[TO BE WRITTEN]

### 1.1. Background

- Software engineering metrics as proxies for complex constructs
- The validity problem in SE metrics research
- Current practice: metrics used without validity assessment

### 1.2. Problem Statement

- Metrics can lose construct validity over time
- Pathologies: distributional drift, correlation breakdown, threshold compression
- Existing tools do not assess metric validity systematically

### 1.3. Solution Overview

- Measurement Integrity Intelligence Engine (MIIE)
- Automated detection of integrity violations
- Deterministic, transparent, and benchmark-validated

### 1.4. Contributions

- First open-source tool dedicated to measurement integrity
- Three statistical detectors with published benchmarks
- Integrity and Confidence Score formulas
- Reproducible research artifact with ICSE/MSR-ready packaging

### 1.5. Paper Organization

---

## 2. Motivation

[TO BE WRITTEN]

### 2.1. Real-World Examples

- Coverage inflation案例研究
- Review metric distortion案例研究
- Threshold compression案例研究

### 2.2. Impact on Research

- False research conclusions
- Wasted engineering effort
- Reproducibility crises

### 2.3. Current Gaps

- No existing tools for integrity assessment
- Benchmark validation missing
- Non-transparent detector logic

---

## 3. Problem Statement

[TO BE WRITTEN]

### 3.1. Construct Validity

- Metrics as proxies for underlying constructs
- Validity erosion over time
- Goodhart's law in software engineering

### 3.2. Integrity Assessment Requirements

- Detection: distributional drift, correlation breakdown, threshold compression
- Quantification: Integrity Score and Confidence Score
- Explanation: rule-based, traceable narratives

---

## 4. Related Work

[TO BE WRITTEN]

### 4.1. Software Engineering Metrics

- Code coverage effectiveness
- Commit frequency as velocity proxy
- Review metrics and collaboration
- Issue resolution time and responsiveness

### 4.2. Metric Validity Research

- Construct validity in SE research
- Goodhart effects in metrics usage
- Validity threats in software analytics

### 4.3. Benchmark Validation

- Benchmark suites for ML/SE
- Ground truth annotation methods
- Detector evaluation frameworks

### 4.4. Open Challenges

- Automated integrity assessment
- Benchmark-driven detector development
- Transparent explanation generation

---

## 5. Methodology

[TO BE WRITTEN]

### 5.1. System Architecture

- Processing pipeline: ingestion → extraction → segmentation → detection → scoring → evidence → explanation → export
- Benchmark subsystem: dataset generation → ground truth → runner → evaluation
- Storage layer: filesystem-only (no database)

### 5.2. Detector Algorithms

#### 5.2.1. Distributional Drift Detector (D-01)

- Kolmogorov-Smirnov test
- Population Stability Index (PSI)
- Direction classification: mean_shift, variance_collapse, shape_change

#### 5.2.2. Correlation Breakdown Detector (D-02)

- Pearson correlation analysis
- Spearman correlation analysis
- Breakdown types: sudden_drop, sign_reversal, gradual_erosion, confidence_exclusion

#### 5.2.3. Threshold Compression Detector (D-03)

- Excess mass test
- Hartigans' dip test
- Auto-threshold detection

### 5.3. Scoring Formulas

#### 5.3.1. Integrity Score (IS)

- Per-metric: IS_metric = 1.0 - (w₁×d₁ + w₂×d₂ + w₃×d₃)
- Repository-level: mean of available metric scores
- Default weights: D-01=0.40, D-02=0.35, D-03=0.25

#### 5.3.2. Confidence Score (CS)

- Multiplicative factors: CS = f₁ × f₂ × f₃ × f₄ × f₅
- Factors: sample_size, variance, missing_data, window_balance, detector_success

### 5.4. Benchmark Methodology

- Synthetic dataset generation with controlled pathologies
- Multiple annotators with Cohen's Kappa ≥0.80 target
- Benchmark suites: metric-drift-v1.0.0, correlation-breakdown-v1.0.0, threshold-compression-v1.0.0

---

## 6. Benchmark Design

[TO BE WRITTEN]

### 6.1. Dataset Generation

- Repository profiles: small_active, medium_active, large_active, seasonal, monotonic_growth, declining, stable
- Pathology injection: MDE-01, MDE-02, MDE-03
- Seed control: deterministic generation (seed=42)

### 6.2. Ground Truth Annotation

- Annotation workflow: injected → candidate → reviewed → resolved
- Multiple annotators (≥3)
- Cohen's Kappa for inter-rater agreement

### 6.3. Evaluation Metrics

- Accuracy, Precision, Recall, F1
- AUC-ROC, AUC-PR
- FPR, FNR

---

## 7. Detector Design

[TO BE WRITTEN]

### 7.1. Statistical Rigor

- KS test: Massey (1951)
- PSI: Siddiqi (2012)
- Pearson/Spearman: Cohen (1988)
- Hartigans' dip: Hartigan & Hartigan (1985)

### 7.2. Threshold Selection

- Alpha: 0.05 (two-tailed)
- PSI threshold: 0.25
- Correlation threshold: 0.3
- Margin: max(0.02×T, 0.01×range)

### 7.3. Implementation Constraints

- Deterministic: fixed random seeds
- Reproducible: bitwise-identical outputs
- Transparent: full statistical metadata

---

## 8. Implementation

[TO BE WRITTEN]

### 8.1. CLI Interface

- Commands: analyze, benchmark, explain, export, generate, ingest, validate, version
- Global options: --config, --output, --verbose

### 8.2. REST API

- Endpoints: /v1/analyze, /v1/benchmark, /v1/explain, /v1/export, /v1/jobs/{job_id}, /v1/health

### 8.3. Architecture

- Interface layer: CLI, API
- Orchestration layer: Job Manager, Pipeline Controller, State Manager, Workflow Engine
- Processing layer: M-01 through M-09
- Benchmark layer: M-03 GEN, M-04, M-06, M-07
- Output layer: JSON, Markdown, CSV

---

## 9. Results

[TO BE WRITTEN]

### 9.1. Detector Performance

| Detector | Precision | Recall | F1 | AUC-ROC | AUC-PR |
|----------|-----------|--------|----|---------|--------|
| D-01 | ≥0.80 | ≥0.75 | TODO | TODO | TODO |
| D-02 | ≥0.75 | ≥0.70 | TODO | TODO | TODO |
| D-03 | ≥0.85 | ≥0.80 | TODO | TODO | TODO |

### 9.2. Benchmark Results

- metric-drift-v1.0.0: 50 datasets
- correlation-breakdown-v1.0.0: 40 datasets
- threshold-compression-v1.0.0: 30 datasets

### 9.3. Reproducibility Validation

- Bitwise-identical outputs across runs
- Three independent implementations produce identical results

### 9.4. User Study Results

- [TO BE FILLED]

---

## 10. Threats To Validity

[TO BE WRITTEN]

### 10.1. Internal Validity

- Detector thresholds may not generalize
- Benchmark datasets may not represent real-world corruption
- Statistical assumptions may be violated

### 10.2. External Validity

- Benchmark dataset bias toward GitHub repositories
- English-language repositories only
- Western development practices

### 10.3. Construct Validity

- Integrity Score as proxy for construct validity
- Confidence Score interpretation limitations
- Pathology injection may not match real corruption patterns

### 10.4. Conclusion Validity

- Statistical test assumptions (independence, distribution)
- Multiple comparison problem
- Threshold selection bias

---

## 11. Future Work

[TO BE WRITTEN]

### 11.1. Short-Term

- Additional metrics beyond M-07
- Additional detectors beyond D-03
- Historical drift analysis
- Cross-repository comparison

### 11.2. Medium-Term

- Recommendation engine for intervention suggestions
- LLM-generated natural language explanations
- Continuous monitoring pipeline
- Organizational incentive modeling

### 11.3. Long-Term

- Cross-domain generalization (data science, product management)
- Predictive integrity scoring
- Enterprise SaaS platform
- Marketplace for detector contributions

---

## 12. References

[TO BE WRITTEN]

### Key References

1. Massey, F.J. (1951). "The Kolmogorov-Smirnov Test for Goodness of Fit." Journal of the American Statistical Association, 46(253), 68-78.
2. Siddiqi, N. (2012). Credit Risk Scorecards: Developing and Implementing Intelligent Credit Scoring. Wiley.
3. Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum.
4. Hartigan, J.A., & Hartigan, P.M. (1985). "The Dip Test of Unimodality." The Annals of Statistics, 13(1), 70-84.
5. Goodhart, C. (1975). "Problems of Monetary Management." In R. Sato and F. Brechling (eds.), The Theory of Monetary Policy. Macmillan.

---

## Appendix A: Artifact Information

### A.1. MIIE Package

- Package name: miie
- Version: 1.0.0
- Python: 3.10+
- Dependencies: pandas, scipy, numpy, fastapi, pydantic

### A.2. Benchmark Suites

- metric-drift-v1.0.0: 50 datasets, D-01 validation
- correlation-breakdown-v1.0.0: 40 datasets, D-02 validation
- threshold-compression-v1.0.0: 30 datasets, D-03 validation

### A.3. Reproducibility Package

- seeds: 42
- dependencies: poetry.lock
- platform: Linux, macOS, Windows (WSL)

---

## Appendix B: Source Code

- Repository: [TO BE FILLED]
- License: CC-BY-4.0
- DOI: [TO BE FILLED]

---

*This structure is a template. Fill in each section with research results and analysis.*