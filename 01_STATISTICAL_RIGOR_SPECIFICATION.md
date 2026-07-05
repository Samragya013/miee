# MIIE v1.6 — Statistical Rigor Specification

**Scientific Statistical Framework & Measurement Integrity Specification**

| Field | Value |
|-------|-------|
| Document Type | Scientific Statistical Constitution |
| Version | 1.6.0 |
| Status | Canonical |
| Scope | All statistical algorithms, confidence estimation, detector mathematics, validation methodology |
| Audience | Statisticians, scientific software engineers, AI agents performing statistical work |
| Last Updated | 2026-07-05 |

---

## Table of Contents

1. [Purpose of Statistical Rigor](#1-purpose-of-statistical-rigor)
2. [Statistical Design Principles](#2-statistical-design-principles)
3. [Population vs Sample](#3-population-vs-sample)
4. [Observation Model](#4-observation-model)
5. [Confidence Theory](#5-confidence-theory)
6. [Statistical Algorithms](#6-statistical-algorithms)
7. [Statistical Assumptions](#7-statistical-assumptions)
8. [Multiple Testing](#8-multiple-testing)
9. [Adaptive Statistics](#9-adaptive-statistics)
10. [Scientific Limitations](#10-scientific-limitations)
11. [Threats to Statistical Validity](#11-threats-to-statistical-validity)
12. [Statistical Validation Strategy](#12-statistical-validation-strategy)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [Future Statistical Evolution](#14-future-statistical-evolution)
15. [Statistical Glossary](#15-statistical-glossary)
16. [Appendices](#16-appendices)

---

## 1. Purpose of Statistical Rigor

### 1.1 Why Statistical Rigor is Central to MIIE

MIIE exists to evaluate the validity of software engineering metrics. This evaluation is itself a statistical enterprise. Every detection finding, every integrity score, every confidence estimate is a statistical statement about the behaviour of metric time series. If the statistics are wrong, the conclusions are wrong, and any downstream decisions based on those conclusions are unfounded.

Statistical rigor in MIIE means more than correct formulae. It means:

- Every algorithm has a clearly stated purpose, mathematical formulation, and set of assumptions
- Every threshold is derived from a significance level or established convention, not arbitrary selection
- Every score carries a confidence estimate that honestly reflects the limitations of the underlying data
- Every result is reproducible: identical inputs produce identical outputs, always

### 1.2 Engineering Correctness vs Scientific Correctness

**Engineering correctness** means the code runs without errors, produces output in the expected format, and passes its test suite. A detector can be engineering-correct while being scientifically meaningless — it may execute the KS test correctly but apply it to data that violates every assumption the test requires.

**Scientific correctness** means the statistical conclusions are valid given the data and assumptions. A scientifically correct implementation:

- Applies the right test to the right data
- Respects the assumptions of the test
- Reports the correct p-value, effect size, and confidence interval
- Acknowledges when assumptions are violated
- Does not over-interpret results from small samples
- Does not conflate statistical significance with practical significance

MIIE requires both. Engineering correctness is necessary but not sufficient.

### 1.3 Measurement Integrity

Measurement integrity is the degree to which a metric time series faithfully represents the underlying phenomenon it claims to measure. A metric with high integrity exhibits natural variation consistent with the development process. A metric with low integrity may show distribution drift (sudden shifts), correlation breakdown (decoupling from related metrics), or threshold compression (artificial clustering around specific values).

MIIE's statistical framework is designed to detect these three categories of integrity violation. The framework does not determine whether a metric is "good" or "bad" — it determines whether the metric's statistical behaviour is consistent with natural development processes.

### 1.4 Construct Validity

Construct validity asks: does MIIE measure what it claims to measure? MIIE claims to detect integrity violations in metric time series. The construct validity of MIIE depends on:

- Whether the three detector categories (drift, breakdown, compression) capture the meaningful forms of integrity violation
- Whether the statistical tests employed are appropriate for the data types involved
- Whether the confidence scores accurately reflect the reliability of the detection

Construct validity is established through the benchmark validation framework (DSVP), which evaluates detection accuracy against synthetic datasets with known ground truth.

### 1.5 Reproducibility

Every statistical computation in MIIE must be reproducible. Given the same observations, configuration, and random seed, every algorithm must produce identical numerical results. This is enforced through:

- Pure functions with no side effects
- Centralized seed management for any stochastic procedures (bootstrap)
- Deterministic floating-point operations (sorted inputs, fixed bin edges)
- Frozen dataclass models that prevent mutation

Reproducibility is not merely a convenience — it is a scientific requirement. Unreproducible results cannot be verified, and unverifiable results cannot be trusted.

### 1.6 Epistemic Reliability

Epistemic reliability is the degree to which MIIE's conclusions can be trusted as knowledge. A system with high epistemic reliability:

- Reports what it knows and what it does not know
- Quantifies uncertainty rather than hiding it
- Degrades gracefully when data is insufficient
- Never presents a guess as a certainty

MIIE's confidence scoring system is the primary mechanism for epistemic reliability. When data is sparse, noisy, or incomplete, the confidence score decreases, signaling that the integrity assessment should be interpreted with caution.

---

## 2. Statistical Design Principles

### 2.1 Evidence Before Inference

MIIE collects observations, computes metrics, and only then applies detectors. The detectors never operate on raw data without passing through the metric computation layer. This ordering ensures that:

- Every detection finding is traceable to specific observations
- The metric computation layer validates data quality before statistical tests consume it
- Evidence packages capture the complete chain from observation to detection

### 2.2 Deterministic Execution

Statistical algorithms must produce identical results across runs. This principle eliminates a class of scientific errors where different runs produce different conclusions from identical data. Determinism is enforced through:

- Fixed random seeds for bootstrap procedures
- Sorted inputs to any procedure that depends on ordering
- Deterministic binning (linspace with fixed endpoints)
- No dependence on system time, process ID, or other non-reproducible sources

### 2.3 Reproducibility

Reproducibility extends determinism to the full analysis pipeline. Two analysts running MIIE on the same repository with the same configuration must obtain identical evidence packages. The evidence package records all parameters necessary for reproduction: the seed, the configuration hash, the dependency hash, and the platform metadata.

### 2.4 Confidence Quantification

Every statistical conclusion must be accompanied by a confidence estimate. MIIE never reports a detection without indicating how confident it is in that detection. Confidence is not optional — it is a mandatory component of every output.

The confidence system distinguishes between:

- **Metric confidence**: How reliable is the computed metric value?
- **Detection confidence**: How reliable is the detector's finding?
- **Score confidence**: How reliable is the overall integrity assessment?

### 2.5 Measurement Uncertainty

Every measurement carries uncertainty. MIIE quantifies uncertainty as the population standard deviation of observation values within a metric. Uncertainty propagates through the system: high uncertainty in observations leads to low metric confidence, which reduces detection sensitivity, which reduces the weight of that metric in the overall integrity score.

### 2.6 Transparency

Every statistical decision must be documented. The thresholds, weights, and algorithms used by MIIE are not hidden parameters — they are published in this specification, enforced in code, and recorded in every evidence package. A user can trace any finding back to the exact statistical test and threshold that produced it.

### 2.7 Minimal Assumptions

MIIE uses non-parametric tests wherever possible. The KS test does not assume normality. The Spearman correlation does not assume linearity. The PSI does not assume any particular distribution. When parametric tests are used (Pearson correlation), the assumptions are documented and the limitations acknowledged.

### 2.8 Graceful Degradation

When data is insufficient for a statistical test, MIIE degrades gracefully rather than producing a misleading result:

- Fewer than 2 windows: analysis aborts with exit code 3
- Fewer than 10 observations per window (D-01): drift detection skipped for that window pair
- Fewer than 20 observations per window (D-03): compression detection skipped
- Fewer than 4 observations for Fisher z CI: CI returns (0.0, 0.0)
- Empty observation set: metric computation raises ValueError

### 2.9 Statistical Conservatism

When in doubt, MIIE errs toward conservatism:

- The integrity score defaults to 1.0 (no violation) when no detectors find anomalies
- The confidence score defaults to 0.0 (no confidence) when data is insufficient
- The severity multiplier reduces impact when observation coverage is low
- The observation-aware adjustment prevents over-penalizing sparse data

---

## 3. Population vs Sample

### 3.1 Definitions

**Repository**: A version control repository containing a history of commits, pull requests, and associated metadata. The repository is the **population** of interest — the complete set of development activity.

**Observation**: A single data point extracted from the repository, associated with a metric, source, and timestamp. An observation is a **sample** from the repository's development activity.

**Sample**: A subset of observations selected for analysis. In MIIE, the sample consists of all observations extracted by the provider layer for a given analysis window.

**Population**: The theoretical complete set of all possible observations from the repository. In practice, the population is unobservable — we only see the sample that the providers extract.

**Window**: A temporal or commit-count segment of the observation series. Windows partition the sample into contiguous subsets for sequential analysis.

**Metric**: A derived quantity computed from observations within a window. Metrics transform raw observations into interpretable values (entropy ratio, commit count, churn ratio, etc.).

**Detector Input**: The set of metric values across windows, consumed by a detector to identify anomalies.

### 3.2 Sampling Assumptions

MIIE makes the following assumptions about the relationship between sample and population:

**SA-1: Temporal Representativeness**: Observations within a window are assumed to be representative of the development activity during that period. This assumption holds when commits occur at approximately regular intervals and the window is long enough to capture meaningful variation.

**SA-2: Provider Completeness**: The provider layer is assumed to extract all observations that the metric requires. When providers are missing or incomplete, the observation quality is downgraded (estimated or derived rather than complete).

**SA-3: Independence of Windows**: Observations in different windows are assumed to be independent. This assumption is violated when development activity is bursty (e.g., a single large refactoring spanning multiple windows).

**SA-4: Exchangeability Within Windows**: Within a window, observations are assumed to be exchangeable — their order does not affect the metric computation. This assumption holds for mean and sum aggregations but may be violated for time-dependent statistics.

### 3.3 Window Assumptions

Windows are the fundamental unit of analysis. MIIE's windowing assumptions include:

**WA-1: Minimum Window Size**: Each window must contain sufficient observations for the detectors to operate. D-01 requires ≥10 observations per window. D-02 requires ≥10 observations per window and ≥2 windows. D-03 requires ≥20 observations per window.

**WA-2: Non-Overlapping**: Windows do not overlap. Each observation belongs to exactly one window.

**WA-3: Temporal Ordering**: Windows are ordered by time (or commit sequence). The detector algorithms depend on this ordering to detect changes between consecutive windows.

**WA-4: Adequate Number**: At least 2 windows are required for drift and correlation analysis. A single window is sufficient for compression analysis.

### 3.4 Independent Observations

The independence assumption is critical for the validity of statistical tests. MIIE assumes:

- Each commit is an independent observation of development activity
- Each pull request is an independent observation of review activity
- Observations from different contributors are independent
- Observations from different time periods are independent

**Known violations**: In practice, commits are not fully independent. A single feature may span multiple commits. A code review may influence subsequent reviews. These dependencies are acknowledged as a limitation (see §10).

### 3.5 Potential Violations

| Assumption | Potential Violation | Impact | Mitigation |
|-----------|-------------------|--------|------------|
| Temporal representativeness | Bursty development activity | Windows may not capture representative samples | Adaptive window sizing (§9.3) |
| Provider completeness | Missing provider data | Metrics computed from incomplete data | Quality scoring, confidence adjustment |
| Independence of windows | Cross-window dependencies | Spurious drift detections | Minimum window size requirements |
| Exchangeability within windows | Temporal autocorrelation | Biased variance estimates | Non-parametric tests |
| Independent observations | Related commits/PRs | Inflated effective sample size | acknowledged limitation |

---

## 4. Observation Model

### 4.1 The Observation Pipeline

The observation model describes how raw repository data transforms into detection findings:

```
Repository
    ↓ (Provider extraction)
Observations
    ↓ (Quality assessment)
ObservationCollection
    ↓ (Graph construction)
RepositoryObservationGraph
    ↓ (Windowing)
ObservationWindows
    ↓ (Metric computation)
Metrics
    ↓ (Detector execution)
Detections
    ↓ (Scoring)
IntegrityScore + ConfidenceScore
    ↓ (Evidence packaging)
EvidencePackage
```

### 4.2 Sample Adequacy

Sample adequacy is the degree to which the observed sample is sufficient for reliable statistical inference. MIIE assesses sample adequacy through:

**Observation count**: More observations provide more reliable estimates. The sample size factor in the confidence score asymptotes to 1.0 at 20 observations per metric (metric-level) and 50 observations per window (score-level).

**Coverage ratio**: The fraction of expected metric-window pairs that have actual observations. Missing pairs reduce the missing data factor in the confidence score.

**Provider diversity**: Observations from multiple providers are more reliable than observations from a single provider. The provider diversity factor in the metric confidence score increases with the number of distinct providers.

### 4.3 Coverage

Coverage measures the completeness of the observation set across metrics and windows:

```
coverage = observed_pairs / (num_metrics × num_windows)
```

Low coverage indicates that the analysis is based on partial information. The confidence score penalizes low coverage through the missing data factor (f₃).

### 4.4 Missing Observations

Missing observations occur when:

- A provider fails to extract data for a metric
- A metric has minimum observation requirements that are not met
- A window contains no observations for a metric

MIIE handles missing observations through:

- **Quality tagging**: Missing observations are tagged with quality="missing"
- **Confidence reduction**: Missing observations reduce the confidence score
- **Graceful degradation**: Detectors skip windows with insufficient observations
- **Severity reduction**: The observation-aware multiplier reduces severity for sparse metrics

### 4.5 Observation Quality

Each observation carries a quality tag:

| Quality | Meaning | Confidence Weight |
|---------|---------|-------------------|
| complete | Directly extracted from source | 1.0 |
| estimated | Derived from partial data | 0.5 |
| derived | Computed from other observations | 0.7 |
| missing | Not available | 0.0 |

The observation quality factor in the confidence score is:

```
quality_factor = (complete + 0.5 × partial) / (complete + partial + estimated)
```

### 4.6 Provider Diversity

Provider diversity measures the number of independent data sources contributing to a metric. More sources provide greater confidence that the observation reflects reality rather than an artifact of a single extraction method.

The provider diversity factor in the metric-level confidence score is:

```
diversity_factor = min(1.0, num_providers / 2.0)
```

This factor reaches its maximum at 2 providers, reflecting the principle that two independent sources provide substantially more confidence than one, while additional sources provide diminishing returns.

---

## 5. Confidence Theory

### 5.1 Formal Definition

Confidence in MIIE is a [0, 1] value quantifying the reliability of a statistical conclusion. It is not a probability in the frequentist sense — it does not answer "what is the probability that this conclusion is correct?" Rather, it answers "how much should this conclusion be trusted given the available evidence?"

### 5.2 Uncertainty

Uncertainty is the population standard deviation of observation values:

```
σ = √(Σ(xᵢ - μ)² / n)
```

where xᵢ are the observation values and μ is the mean. Uncertainty captures the spread of observations within a metric. High uncertainty indicates that observations vary widely, making the metric value less reliable.

### 5.3 Coverage

Coverage in the confidence context refers to the completeness of the observation set across all metric-window pairs. It is distinct from the statistical concept of confidence interval coverage. Low coverage means the analysis is based on partial information.

### 5.4 Quality

Quality reflects the provenance of observations. Complete observations (directly extracted from the source) carry more weight than estimated observations (derived from partial data) or derived observations (computed from other observations).

### 5.5 Confidence Composition

MIIE uses two distinct confidence formulas:

**Metric-level confidence** (BaseMetricComputer):

```
confidence = 0.3 × f₁ + 0.3 × f₂ + 0.2 × f₃ + 0.2 × f₄
```

where:
- f₁ = min(1.0, n / 20) — sample size factor
- f₂ = mean(quality_scores) — quality factor
- f₃ = max(0, 1 - |σ/μ|) — relative uncertainty factor
- f₄ = min(1.0, num_providers / 2) — provider diversity factor

**Score-level confidence** (ScoringEngine):

```
confidence = f₁ × f₂ × f₃ × f₄ × f₅ × f₆
```

where:
- f₁ = min(1.0, mean_n / 50) — sample size factor (target: 50)
- f₂ = 1 - min(1, mean_CV / 0.5) — variance factor
- f₃ = 1 - (missing_pairs / total_pairs) — missing data factor
- f₄ = 1 - min(1, std_size / mean_size) — window balance factor
- f₅ = successful_runs / total_attempts — detector success factor
- f₆ = (complete + 0.5 × partial) / (complete + partial + estimated) — observation quality factor

### 5.6 Sample Size Effects

Small samples produce unreliable estimates. The sample size factor captures this:

- At n=1: f₁ = 0.05 (very low confidence)
- At n=10: f₁ = 0.50 (moderate confidence)
- At n=20: f₁ = 1.00 (full confidence at metric level)
- At n=50: f₁ = 1.00 (full confidence at score level)

The difference in targets (20 vs 50) reflects the different requirements: metric computation can produce a reasonable estimate with fewer observations, while the overall score requires a more robust foundation.

### 5.7 Measurement Quality

Measurement quality affects confidence through two mechanisms:

1. **Direct effect**: The quality factor (f₂ at metric level, f₆ at score level) weights observations by their provenance
2. **Indirect effect**: Low-quality observations reduce the effective sample size, which reduces the sample size factor

### 5.8 Provider Diversity

Multiple providers provide greater confidence because:

- A single provider may have systematic biases
- Provider failures are independent — if one fails, others may succeed
- Cross-provider validation increases confidence in observation accuracy

### 5.9 Variance

High variance within a metric reduces confidence. The variance factor at the score level uses the coefficient of variation (CV):

```
CV = σ / |μ|
```

The variance factor is:

```
f₂ = 1 - min(1, CV / 0.5)
```

At CV=0 (no variance): f₂ = 1.0 (full confidence)
At CV=0.5 (moderate variance): f₂ = 0.0 (no confidence contribution)
At CV>0.5 (high variance): f₂ = 0.0 (clamped)

**Special case**: When the mean is 0, if all values are 0 (perfect consistency), CV=0. If values vary around 0, CV is set to 1.0 (maximum penalty), reflecting the high uncertainty of measurements near zero.

### 5.10 Missing Information

Missing information reduces confidence proportionally to the fraction of missing metric-window pairs:

```
f₃ = 1 - (missing_pairs / total_pairs)
```

At 0% missing: f₃ = 1.0
At 50% missing: f₃ = 0.5
At 100% missing: f₃ = 0.0

---

## 6. Statistical Algorithms

### 6.1 Kolmogorov–Smirnov Two-Sample Test

#### Purpose

The Kolmogorov–Smirnov (KS) two-sample test determines whether two samples are drawn from the same underlying distribution. In MIIE, it detects distribution drift between consecutive analysis windows.

#### Mathematical Formulation

Given two samples X = {x₁, ..., xₙ₁} and Y = {y₁, ..., yₙ₂}, the KS statistic is:

```
D = sup_x |F̂₁(x) - F̂₂(x)|
```

where F̂₁ and F̂₂ are the empirical cumulative distribution functions (ECDFs) of X and Y respectively. The supremum is taken over all values x in the combined support of both samples.

The ECDF of a sample is:

```
F̂(x) = (1/n) Σᵢ I(xᵢ ≤ x)
```

where I(·) is the indicator function.

The asymptotic p-value is approximated by:

```
p = 2 × exp(-2 × D² × n_eff)
```

where n_eff = (n₁ × n₂) / (n₁ + n₂) is the effective sample size.

#### Interpretation

- D ∈ [0, 1]: The KS statistic. Values near 0 indicate similar distributions; values near 1 indicate dissimilar distributions.
- p ∈ [0, 1]: The p-value. Small p-values (p < 0.05) indicate statistically significant difference between distributions.
- **Threshold**: p < 0.05 indicates distribution drift.

#### Assumptions

- Samples are independent
- Observations are continuous (or treated as such)
- The test is non-parametric — no distributional assumptions about the underlying populations
- The asymptotic approximation for the p-value is accurate for moderate sample sizes (n₁, n₂ ≥ 10)

#### Failure Modes

- **Small samples** (n < 10): The asymptotic p-value approximation becomes unreliable. MIIE skips detection for window pairs with fewer than 10 observations.
- **Discrete data**: The KS test is designed for continuous data. Discrete data (e.g., integer commit counts) may produce conservative p-values.
- **Tied values**: Large numbers of tied values reduce the test's power.
- **Multiple modes**: The KS test detects any difference in distribution, not specifically drift. Bimodal distributions may produce significant results without meaningful drift.

#### Scientific Justification

The KS test is a standard non-parametric test for distribution comparison. It is distribution-free, making it suitable for MIIE's diverse metric types. The test has well-understood power characteristics and is widely used in change-point detection applications.

#### Alternative Methods

- Anderson-Darling test: More powerful against tail differences, but less common
- Cramér-von Mises test: More powerful against location shifts, but less sensitive to scale changes
- Mann-Whitney U test: Tests for location shift only, not distributional difference

#### Validation Requirements

- D-01 precision ≥ 0.80, recall ≥ 0.75 (DSVP targets)
- FPR ≤ 0.05 on synthetic datasets with no drift
- TPR ≥ 0.80 on synthetic datasets with known drift
- Reproducibility: 100% identical across 100 runs

---

### 6.2 Population Stability Index (PSI)

#### Purpose

The Population Stability Index quantifies the magnitude of distribution shift between two samples. It is used alongside the KS test in D-01 to detect distribution drift.

#### Mathematical Formulation

Given expected distribution P and actual distribution Q, with n_bins equal-width bins:

```
PSI = Σᵢ (qᵢ - pᵢ) × ln(qᵢ / pᵢ)
```

where pᵢ is the proportion of expected observations in bin i, and qᵢ is the proportion of actual observations in bin i.

MIIE uses equal-width bins over the combined range of both samples:

```
bins = linspace(min(X ∪ Y), max(X ∪ Y), n_bins + 1)
```

where n_bins = 10 (per DES §21.2).

To avoid division by zero, a floor of ε = 10⁻¹⁰ is applied to zero-proportion bins.

#### Interpretation

- PSI ≈ 0: No distribution shift
- PSI < 0.10: Minor shift (not significant)
- 0.10 ≤ PSI < 0.25: Moderate shift (notable but not alarming)
- PSI ≥ 0.25: Significant shift (drift detected)

**Threshold**: PSI > 0.25 indicates distribution drift.

#### Assumptions

- Both samples are drawn from the same measurement scale
- The binning strategy captures meaningful distributional differences
- The logarithmic transformation is appropriate for the data range
- Proportions are well-defined (non-zero after epsilon floor)

#### Failure Modes

- **Very small samples**: Bin proportions are noisy, producing unreliable PSI values
- **Zero-proportion bins**: Without the epsilon floor, ln(0) is undefined
- **Fixed bin count**: 10 bins may not be appropriate for all distributions (see §9.1)
- **Extreme values**: Outliers can distort bin edges and proportions
- **Identical distributions**: PSI = 0 exactly, which is correct but provides no information about the sensitivity of the test

#### Scientific Justification

PSI is widely used in financial risk management for monitoring distribution stability. It provides a complementary measure to the KS test: the KS test detects whether distributions differ, while PSI quantifies how much they differ.

#### Alternative Methods

- Jensen-Shannon divergence: Symmetric, bounded alternative to KL divergence
- Wasserstein distance: Measures the "earth mover's distance" between distributions
- Hellinger distance: Another divergence measure with better mathematical properties

#### Validation Requirements

- PSI > 0.25 on datasets with known drift
- PSI ≈ 0 on identical distributions
- PSI is symmetric: PSI(P, Q) ≈ PSI(Q, P) for large samples

---

### 6.3 Pearson Product-Moment Correlation Coefficient

#### Purpose

The Pearson correlation coefficient measures the strength and direction of the linear relationship between two continuous variables. In MIIE, it is used in D-02 to detect correlation breakdown between metric pairs across windows.

#### Mathematical Formulation

For samples X = {x₁, ..., xₙ} and Y = {y₁, ..., yₙ}:

```
r = Σᵢ(xᵢ - x̄)(yᵢ - ȳ) / √(Σᵢ(xᵢ - x̄)² × Σᵢ(yᵢ - ȳ)²)
```

where x̄ and ȳ are the sample means.

Equivalently:

```
r = Cov(X, Y) / (σ_X × σ_Y)
```

#### Interpretation

- r = +1: Perfect positive linear relationship
- r = 0: No linear relationship
- r = -1: Perfect negative linear relationship
- |r| > 0.3: Moderate to strong relationship (MIIE threshold for sign reversal)
- |r| > 0.5: Strong relationship

#### Assumptions

- Both variables are continuous
- The relationship is linear (non-linear relationships may produce r ≈ 0)
- Both variables are approximately normally distributed (for significance testing)
- Observations are independent
- No significant outliers (Pearson r is sensitive to outliers)

#### Failure Modes

- **Non-linear relationships**: Pearson r measures linear association only. A perfect quadratic relationship may produce r ≈ 0.
- **Outliers**: A single outlier can dramatically change r.
- **Small samples**: r is unreliable with fewer than 10 observations.
- **Restricted range**: If both variables have limited range, r is attenuated.
- **Ecological fallacy**: Aggregate-level correlations may not hold at the individual level.

#### Scientific Justification

Pearson r is the standard measure of linear association. It is computationally simple, well-understood, and widely reported. For MIIE's purpose of detecting correlation breakdown, it provides a clear, interpretable measure of how the linear relationship between metric pairs changes across windows.

#### Alternative Methods

- Spearman ρ: Rank-based, robust to non-linearity and outliers (MIIE also computes this)
- Kendall τ: Another rank correlation, more robust with small samples
- Distance correlation: Detects non-linear dependencies

#### Validation Requirements

- r = 1.0 on perfectly correlated synthetic data
- r ≈ 0 on independent synthetic data
- |r| < 0.1 on datasets with no linear relationship

---

### 6.4 Spearman Rank-Order Correlation Coefficient

#### Purpose

Spearman ρ measures the strength and direction of the monotonic relationship between two variables. It is more robust than Pearson r to non-linear relationships and outliers. MIIE computes both Pearson r and Spearman ρ in D-02 to detect correlation breakdown.

#### Mathematical Formulation

Spearman ρ is the Pearson correlation applied to rank-transformed data:

```
ρ = Pearson(ranked(X), ranked(Y))
```

where ranked(·) assigns average ranks to handle ties:

```
rank(xᵢ) = (number of values ≤ xᵢ + number of values ≥ xᵢ) / 2n
```

#### Interpretation

- ρ = +1: Perfect monotonic increasing relationship
- ρ = 0: No monotonic relationship
- ρ = -1: Perfect monotonic decreasing relationship
- Agreement between Pearson r and Spearman ρ indicates a linear relationship
- Disagreement (|ρ| >> |r|) indicates a non-linear but monotonic relationship

#### Assumptions

- At least ordinal data (rankable)
- Observations are independent
- The relationship is monotonic (for meaningful interpretation)

#### Failure Modes

- **Small samples**: Rank correlations are unreliable with fewer than 10 observations
- **Many ties**: Large numbers of tied values reduce the effective information
- **Non-monotonic relationships**: Spearman ρ does not detect non-monotonic associations

#### Scientific Justification

Spearman ρ provides robustness against the non-normality and outliers common in software engineering metrics. By computing both Pearson r and Spearman ρ, MIIE can distinguish between linear and non-linear association breakdown.

#### Alternative Methods

- Kendall τ: More robust with small samples, but less powerful
- Goodman-Kruskal gamma: Handles ordinal data with ties

#### Validation Requirements

- ρ = 1.0 on perfectly monotonically related data
- ρ ≈ 0 on independent data
- Agreement with Pearson r on linear synthetic data

---

### 6.5 Fisher z-Transformation

#### Purpose

The Fisher z-transformation converts a correlation coefficient to a value approximately normally distributed, enabling the construction of confidence intervals for correlation coefficients. MIIE uses Fisher z in D-02 to compute confidence intervals for per-window correlations.

#### Mathematical Formulation

**Forward transformation:**

```
z = 0.5 × ln((1 + r) / (1 - r)) = arctanh(r)
```

**Inverse transformation:**

```
r = tanh(z)
```

**Standard error:**

```
SE = 1 / √(n - 3)
```

**Confidence interval (z-scale):**

```
z_lower = z - z_crit × SE
z_upper = z + z_crit × SE
```

where z_crit = Φ⁻¹(1 - α/2) for a (1-α) confidence level.

**Confidence interval (r-scale):**

```
CI = (tanh(z_lower), tanh(z_upper))
```

#### Interpretation

- The Fisher z-transformation maps r ∈ (-1, 1) to z ∈ (-∞, +∞)
- The SE decreases with sample size: larger samples produce narrower CIs
- Non-overlapping CIs between consecutive windows indicate correlation breakdown

#### Assumptions

- The sample size is moderate to large (n ≥ 4)
- The population correlation is not exactly ±1
- The sampling distribution of r is approximately bivariate normal

#### Failure Modes

- **Small samples** (n < 4): The SE becomes very large, producing uninformative CIs. MIIE returns (0.0, 0.0) for n < 4.
- **r = ±1**: The transformation is undefined (arctanh diverges). MIIE clamps r to (-1 + 10⁻¹⁰, 1 - 10⁻¹⁰).
- **Non-normal data**: The normality assumption for the sampling distribution may not hold.

#### Scientific Justification

The Fisher z-transformation is the standard method for constructing confidence intervals for correlation coefficients. It is well-established in the statistical literature and widely used in meta-analysis.

#### Alternative Methods

- Bootstrap confidence intervals: Non-parametric, no normality assumption
- Bayesian credible intervals: Provide posterior probability statements
- Bootstrapped percentile intervals: Simple to implement, distribution-free

#### Validation Requirements

- CI width decreases with increasing sample size
- CI covers the true correlation at the nominal rate (95% CI covers ~95% of the time)
- Non-overlapping CIs correctly identify correlation changes

---

### 6.6 Hartigan's Dip Test (Approximation)

#### Purpose

The dip test assesses whether a distribution is unimodal (single-peaked) or multimodal (multiple peaks). Multimodality around a threshold may indicate threshold compression. MIIE uses an approximation based on the KS statistic against the uniform CDF.

#### Mathematical Formulation

The true Hartigan dip statistic is the maximum difference between the empirical distribution function and the least-majorant concave function. MIIE approximates this using:

```
dip_statistic = max_x |F̂(x) - U(x)|
```

where F̂(x) is the ECDF of the data and U(x) is the uniform CDF over the data range:

```
U(x) = (x - min(X)) / (max(X) - min(X))
```

The p-value is computed via bootstrap:

1. Generate B = 1000 samples from Uniform(min(X), max(X))
2. For each bootstrap sample, compute the same KS statistic
3. p_value = (number of bootstrap stats ≥ observed stat) / B

#### Interpretation

- dip_statistic ∈ [0, 1]: The maximum deviation from uniformity
- p_value ∈ [0, 1]: The probability of observing this deviation under uniformity
- **Threshold**: p < 0.05 indicates multimodality (distribution is not unimodal)

#### Assumptions

- The data is continuous
- The data range is meaningful (uniform reference is appropriate)
- 1000 bootstrap samples provide adequate precision for the p-value
- The random seed is fixed for reproducibility

#### Failure Modes

- **Approximation**: This is not the true Hartigan dip test. It uses KS against uniform CDF as an approximation (documented in DSVP §15.4). The approximation may differ from the true dip test in power and size.
- **Small samples** (n < 2): The test is undefined. MIIE returns (0.0, 1.0).
- **Constant data**: If all values are identical, the test is undefined. MIIE returns (0.0, 1.0).
- **Computational cost**: 1000 bootstrap iterations per threshold per window may be slow for large datasets.

#### Scientific Justification

The dip test is the standard test for unimodality. MIIE's approximation captures the essential idea (deviation from a reference distribution) while being computationally tractable. The approximation is documented as a known limitation.

#### Alternative Methods

- True Hartigan dip test: Available in R's `diptest` package, but not in Python's standard libraries
- Silverman's bandwidth test: Tests for multimodality using kernel density estimation
- Gaussian mixture model comparison: Tests for multiple components

#### Validation Requirements

- dip_statistic ≈ 0 on uniform data
- dip_statistic > 0 on bimodal data
- p_value < 0.05 on clearly bimodal synthetic data
- Reproducibility: identical results with fixed seed

---

### 6.7 Excess Mass Test

#### Purpose

The excess mass test detects whether observations cluster around a specific threshold more than expected under a uniform distribution. It is used in D-03 to detect threshold compression — the artificial concentration of metric values near specific thresholds.

#### Mathematical Formulation

For a threshold T and band half-width ε:

**Expected proportion under uniformity:**

```
p₀ = 2ε / range(X)
```

**Observed proportion in band:**

```
p = |{x : |x - T| ≤ ε}| / n
```

**Z-statistic:**

```
z = (p - p₀) / √(p₀(1 - p₀) / n)
```

**Epsilon computation (DES §22.3):**

```
ε = max(0.02 × |T|, 0.01 × range(X))
```

#### Interpretation

- z ∈ (-∞, +∞): The excess mass z-score
- z > 0: More observations near T than expected
- z < 0: Fewer observations near T than expected
- **Threshold**: z > 1.645 (one-tailed, α = 0.05) indicates threshold compression

#### Assumptions

- The data is continuous (or approximately so)
- The uniform distribution is an appropriate null model
- The sample size is large enough for the normal approximation to the binomial
- The threshold and band width are meaningful for the data

#### Failure Modes

- **Very small samples**: The normal approximation is unreliable. MIIE requires ≥20 observations.
- **Zero variance**: If all values are identical and equal to the threshold, z → ∞ (correct but extreme).
- **Band width sensitivity**: The choice of ε affects the test. Too narrow: miss compression. Too wide: detect natural clustering.
- **Multiple thresholds**: Testing many thresholds inflates the family-wise error rate (see §8).

#### Scientific Justification

The excess mass test is a natural approach for detecting concentration around thresholds. The z-test provides a familiar significance framework. The epsilon formula (DES §22.3) balances sensitivity to local concentration against robustness to small fluctuations.

#### Alternative Methods

- Kernel density estimation: More flexible, but requires bandwidth selection
- Ripley's K-function: Detects spatial clustering, applicable to 1D data
- Bayesian change-point detection: More principled, but computationally expensive

#### Validation Requirements

- z > 1.645 on synthetic data with artificial threshold compression
- z ≈ 0 on uniformly distributed data
- z < 0 on data avoiding the threshold

---

### 6.8 Bootstrap

#### Purpose

Bootstrap resampling provides a non-parametric method for estimating the sampling distribution of a statistic. MIIE uses bootstrap in the dip test approximation to estimate the p-value under the null hypothesis of uniformity.

#### Mathematical Formulation

Given a sample X = {x₁, ..., xₙ} and a statistic T(X):

1. Draw B bootstrap samples X*₁, ..., X*_B, each of size n, with replacement from X
2. Compute T(X*₁), ..., T(X*_B)
3. The bootstrap distribution of T is approximated by {T(X*₁), ..., T(X*_B)}
4. The p-value is: p = (1/B) Σᵢ I(T(X*ᵢ) ≥ T_obs)

#### Interpretation

- The bootstrap distribution approximates the true sampling distribution
- More bootstrap samples produce more precise p-value estimates
- The bootstrap is valid for any statistic with finite variance

#### Assumptions

- The sample is representative of the population
- Bootstrap samples are drawn with replacement
- The number of bootstrap samples B is large enough for stable estimates
- The statistic is pivotal (or approximately so) for good bootstrap performance

#### Failure Modes

- **Small samples**: The bootstrap distribution may not approximate the true sampling distribution
- **Discrete data**: Bootstrap resampling may not capture the true variability
- **Extreme statistics**: Statistics with infinite variance (e.g., maximum) may not bootstrap well
- **Computational cost**: Large B (e.g., 1000) is computationally expensive for complex statistics

#### Scientific Justification

The bootstrap is a well-established non-parametric method that requires minimal assumptions. It is particularly valuable when the sampling distribution of a statistic is unknown or difficult to derive analytically.

#### Alternative Methods

- Permutation tests: Exact tests for exchangeable data
- Jackknife: Leave-one-out resampling, less variable but more biased
- Bayesian posterior simulation: Provides full posterior distributions

#### Validation Requirements

- Bootstrap p-value converges to the true p-value as B → ∞
- Bootstrap distribution is approximately symmetric for symmetric statistics
- Coverage of bootstrap confidence intervals matches nominal level

---

### 6.9 Effect Size

#### Purpose

Effect size quantifies the magnitude of a statistical effect, independent of sample size. MIIE uses effect sizes (KS statistic, correlation change, compression index) to assess the practical significance of detections.

#### Mathematical Formulation

MIIE uses several effect size measures:

**KS statistic (D)**: The maximum CDF difference. Ranges from 0 (identical) to 1 (maximally different).

**Drift magnitude**: `min(1.0, KS / 0.5)`. Normalized to [0, 1] by capping at KS = 0.5.

**Breakdown magnitude**: `min(1.0, |Δr| / 0.3)`. Normalized to [0, 1] by capping at |Δr| = 0.3.

**Compression index**: `|{x : |x - T| ≤ ε}| / n`. The fraction of observations in the threshold band.

#### Interpretation

- Effect sizes in [0, 0.2]: Small effect
- Effect sizes in [0.2, 0.5]: Medium effect
- Effect sizes in [0.5, 0.8]: Large effect
- Effect sizes > 0.8: Very large effect

#### Assumptions

- The effect size measure is appropriate for the type of data
- The normalization constants (0.5 for KS, 0.3 for Δr) are meaningful
- Effect sizes are comparable across metrics and detectors

#### Failure Modes

- **Normalization sensitivity**: Different normalization constants would produce different effect sizes
- **Non-comparability**: Effect sizes from different detectors may not be directly comparable
- **Threshold dependence**: Some effect size measures depend on the choice of threshold

#### Scientific Justification

Effect sizes complement p-values by indicating practical significance. A statistically significant result with a tiny effect size may not be practically meaningful. MIIE's effect sizes are used in the severity calculations that feed into the integrity score.

#### Alternative Methods

- Cohen's d: Standardized mean difference, applicable to location shifts
- η² (eta-squared): Proportion of variance explained
- Common language effect size: Probability that a random observation from one group exceeds a random observation from the other

#### Validation Requirements

- Effect sizes are bounded in [0, 1] after normalization
- Effect sizes increase with the magnitude of the underlying effect
- Effect sizes are reproducible

---

### 6.10 Confidence Interval

#### Purpose

A confidence interval provides a range of plausible values for a population parameter. MIIE uses Fisher z-based confidence intervals for correlation coefficients in D-02 to assess the reliability of per-window correlations.

#### Mathematical Formulation

For a correlation coefficient r with sample size n, at confidence level (1 - α):

```
z_r = arctanh(r)
SE = 1 / √(n - 3)
z_crit = Φ⁻¹(1 - α/2)
CI_r = (tanh(z_r - z_crit × SE), tanh(z_r + z_crit × SE))
```

#### Interpretation

- A 95% CI means: if we repeated the analysis many times, approximately 95% of the CIs would contain the true correlation
- **Non-overlapping CIs**: If CIs for two windows do not overlap, the correlations are significantly different
- **Wide CIs**: Indicate low precision (small sample or high variability)
- **Narrow CIs**: Indicate high precision (large sample or low variability)

#### Assumptions

- The sampling distribution of r is approximately normal after Fisher z-transformation
- The sample is representative
- Observations are independent

#### Failure Modes

- **Small samples** (n < 4): CIs are uninformative. MIIE returns (0.0, 0.0).
- **r = ±1**: The transformation diverges. MIIE clamps to avoid this.
- **Non-normal data**: The normality assumption may not hold.

#### Scientific Justification

Confidence intervals are the standard method for quantifying estimation uncertainty. The Fisher z-transformation is the standard method for correlation CIs.

#### Alternative Methods

- Bootstrap CI: Non-parametric, no normality assumption
- Bayesian credible interval: Provides posterior probability
- Jackknife CI: Simpler but less accurate

#### Validation Requirements

- CI width decreases with increasing sample size
- CI covers the true parameter at the nominal rate
- Non-overlapping CIs correctly identify significant differences

---

### 6.11 Coefficient of Variation

#### Purpose

The coefficient of variation (CV) measures relative variability — the standard deviation relative to the mean. MIIE uses CV in the confidence score to penalize metrics with high relative variability.

#### Mathematical Formulation

```
CV = σ / |μ|
```

where σ is the population standard deviation and μ is the mean.

**Special cases:**

- If μ = 0 and all values are 0: CV = 0 (perfect consistency)
- If μ = 0 but values vary: CV = 1.0 (maximum penalty)

#### Interpretation

- CV < 0.1: Low variability (reliable measurements)
- CV ∈ [0.1, 0.5): Moderate variability
- CV ≥ 0.5: High variability (unreliable measurements)

The variance factor in the confidence score is:

```
f₂ = 1 - min(1, CV / 0.5)
```

At CV = 0: f₂ = 1.0 (full confidence)
At CV = 0.5: f₂ = 0.0 (no confidence)

#### Assumptions

- The mean is not zero (or the special case handling applies)
- The standard deviation is a meaningful measure of spread
- The data is on a ratio scale (meaningful zero point)

#### Failure Modes

- **Mean near zero**: Small changes in the mean produce large changes in CV
- **Negative values**: CV is defined but may be misleading for data that can be negative
- **Skewed distributions**: CV may not capture the relevant variability

#### Scientific Justification

CV is the standard measure of relative variability. It is unitless, making it comparable across metrics with different scales.

#### Alternative Methods

- Interquartile range: Robust to outliers, but less commonly used
- Median absolute deviation: Robust alternative to standard deviation
- Signal-to-noise ratio: Related concept in engineering contexts

#### Validation Requirements

- CV ≥ 0 for all data
- CV = 0 for constant data
- CV increases with increasing variability

---

### 6.12 Adaptive Binning

#### Purpose

Adaptive binning adjusts the number and width of bins based on the data characteristics. MI currently uses fixed 10-bin equal-width binning for PSI. Adaptive binning is identified as a future improvement.

#### Mathematical Formulation

Potential approaches:

**Sturges' rule**: `k = ⌈log₂(n) + 1⌉`
**Freedman-Diaconis**: `width = 2 × IQR × n⁻¹/³`
**Scott's rule**: `width = 3.49 × σ × n⁻¹/³`

#### Interpretation

Adaptive binning would:

- Use fewer bins for small samples (reducing noise)
- Use more bins for large samples (increasing resolution)
- Adjust bin width based on data spread

#### Assumptions

- The data is continuous
- The sample size is large enough for the binning rule to be meaningful
- The chosen rule is appropriate for the data distribution

#### Failure Modes

- **Very small samples**: Even adaptive rules produce unreliable bins
- **Heavy-tailed distributions**: Equal-width bins may miss structure in the tails
- **Multimodal distributions**: Adaptive bins may split or merge modes

#### Scientific Justification

Adaptive binning is a well-established improvement over fixed binning. It balances resolution against noise in a data-dependent way.

#### Alternative Methods

- Variable-width bins: Different widths for different regions
- Optimal binning: Minimize some loss function
- Bayesian binning: Let the data determine the number of bins

#### Validation Requirements

- Adaptive bins produce more stable PSI values than fixed bins
- Adaptive bins adapt appropriately to sample size and data spread

---

### 6.13 Multiple Comparison Correction

#### Purpose

When multiple statistical tests are performed simultaneously, the probability of at least one false positive increases. Multiple comparison correction controls this inflation. MIIE currently does not apply correction, which is identified as a limitation (see §8).

#### Mathematical Formulation

**Bonferroni correction**: `α_adjusted = α / m` where m is the number of tests

**Holm correction**: Sequential Bonferroni, less conservative

**Benjamini-Hochberg**: Controls false discovery rate rather than family-wise error

#### Interpretation

- Without correction: Each test uses α = 0.05, but the family-wise error rate may be much higher
- With Bonferroni: Each test uses α/m, controlling family-wise error at α
- With BH: The expected fraction of false discoveries is controlled at α

#### Assumptions

- Tests are independent (Bonferroni) or have known dependency structure
- The number of tests is known in advance
- Each test has the same significance level

#### Failure Modes

- **Over-correction**: Bonferroni is very conservative, especially with many tests
- **Under-correction**: BH is less conservative but allows more false discoveries
- **Dependent tests**: Standard corrections assume independence

#### Scientific Justification

Multiple comparison correction is a fundamental requirement for valid statistical inference when performing multiple tests. Its absence in MIIE is a known limitation.

#### Alternative Methods

- Permutation-based correction: Exact, but computationally expensive
- Bayesian model comparison: Naturally handles multiple hypotheses
- False coverage rate control: For confidence intervals rather than tests

#### Validation Requirements

- Correction reduces false positive rate without excessive power loss
- Applied to all statistical tests in the detector pipeline

---

## 7. Statistical Assumptions

### 7.1 D-01 Distribution Drift Detector

| Assumption | Description | Status |
|-----------|-------------|--------|
| A1: Independent samples | Observations in consecutive windows are independent | Generally holds for well-windowed data |
| A2: Continuous data | The KS test assumes continuous distributions | Violated for integer metrics (commit count); impact is conservative p-values |
| A3: Adequate sample size | ≥10 observations per window for reliable KS test | Enforced by MIIE |
| A4: Stable measurement scale | The metric meaning does not change across windows | May be violated during refactoring or tool changes |
| A5: Representative windows | Each window captures a representative period | May be violated for bursty development |

### 7.2 D-02 Correlation Breakdown Detector

| Assumption | Description | Status |
|-----------|-------------|--------|
| B1: Bivariate normality | Pearson r assumes bivariate normal data for CI validity | May be violated for skewed metrics |
| B2: Monotonic relationship | Spearman ρ assumes monotonic association | Holds for many metric pairs |
| B3: Adequate sample size | ≥10 observations per window, ≥2 windows | Enforced by MIIE |
| B4: Paired observations | Each observation must have values for both metrics in a pair | May not hold if providers extract different metrics |
| B5: Temporal alignment | Paired observations must be from the same time period | Enforced by source_id matching |

### 7.3 D-03 Threshold Compression Detector

| Assumption | Description | Status |
|-----------|-------------|--------|
| C1: Uniform null | The excess mass test assumes uniformity under H₀ | May not be appropriate for all metric distributions |
| C2: Adequate sample size | ≥20 observations per window | Enforced by MIIE |
| C3: Meaningful thresholds | The auto-generated thresholds are meaningful for the data | Depends on data characteristics |
| C4: Continuous data | The dip test approximation assumes continuous data | May be violated for integer metrics |
| C5: Unimodal null | The dip test assumes unimodality under H₀ | Alternative: uniformity assumption |

### 7.4 Metric Computation

| Assumption | Description | Status |
|-----------|-------------|--------|
| D1: Exchangeability | Observations within a window are exchangeable | Holds for sum/mean aggregation |
| D2: Valid units | All observations for a metric have the same unit | Enforced by validation |
| D3: Finite values | No NaN or infinite values in observations | Enforced by validation |
| D4: Range compliance | Observation values within the metric's valid range | Enforced by validation (warning) |

### 7.5 Sampling Framework

| Assumption | Description | Status |
|-----------|-------------|--------|
| E1: Temporal continuity | The repository has continuous development activity | May be violated for inactive repos |
| E2: Sufficient history | The repository has enough history for meaningful windows | May be violated for new repos |
| E3: Provider availability | Required providers are available and functional | May be violated for GitHub API rate limits |

### 7.6 Confidence Estimation

| Assumption | Description | Status |
|-----------|-------------|--------|
| F1: Linear quality scaling | Quality weights (complete=1.0, estimated=0.5, etc.) are appropriate | Simplification; actual quality may not be linear |
| F2: Monotonic sample size | More observations always increase confidence | May not hold for very large samples with high variance |
| F3: Independence of factors | The six confidence factors are independent | May be correlated in practice |

### 7.7 Evidence

| Assumption | Description | Status |
|-----------|-------------|--------|
| G1: Deterministic hashing | SHA-256 produces deterministic, collision-resistant hashes | Well-established cryptographic property |
| G2: Canonical serialization | JSON with sort_keys produces identical output | Enforced by implementation |

### 7.8 Scoring

| Assumption | Description | Status |
|-----------|-------------|--------|
| H1: Additive severity | Detector severities combine additively | Simplification; interactions may exist |
| H2: Fixed weights | The detector weights (0.40, 0.35, 0.25) are appropriate | May need adjustment for different domains |
| H3: Linear observation scaling | The severity multiplier scales linearly with coverage | Simplification; actual relationship may be non-linear |

---

## 8. Multiple Testing

### 8.1 The Problem

When MIIE performs k statistical tests at significance level α, the probability of at least one false positive (family-wise error rate, FWER) is:

```
FWER = 1 - (1 - α)ᵏ
```

For example, with k = 20 tests at α = 0.05:

```
FWER = 1 - (0.95)²⁰ ≈ 0.64
```

This means there is a 64% chance of at least one false positive detection.

### 8.2 Current State

MIIE currently does not apply multiple comparison correction. Each detector operates independently, and each statistical test uses the nominal α level. This is a known limitation.

### 8.3 Bonferroni Correction

The Bonferroni correction is the simplest and most conservative approach:

```
α_adjusted = α / k
```

where k is the number of tests. For k = 20 tests at α = 0.05:

```
α_adjusted = 0.05 / 20 = 0.0025
```

**Advantages:**
- Controls FWER at exactly α
- Simple to implement
- No assumptions about test dependencies

**Disadvantages:**
- Very conservative — reduces power substantially
- Assumes tests are independent
- Does not account for correlations between tests

### 8.4 Holm Correction

The Holm (step-down) procedure is uniformly more powerful than Bonferroni:

1. Order p-values: p₁ ≤ p₂ ≤ ... ≤ pₖ
2. For each i, compare pᵢ to α / (k - i + 1)
3. Reject all hypotheses where pᵢ ≤ α / (k - i + 1)

**Advantages:**
- More powerful than Bonferroni
- Controls FWER at exactly α
- Valid for dependent tests

**Disadvantages:**
- Still conservative for large k
- Does not control false discovery rate

### 8.5 Benjamini-Hochberg

The Benjamini-Hochberg procedure controls the false discovery rate (FDR) rather than FWER:

1. Order p-values: p₁ ≤ p₂ ≤ ... ≤ pₖ
2. Find the largest i such that pᵢ ≤ (i/k) × α
3. Reject all hypotheses with pⱼ ≤ pᵢ for j ≤ i

**Advantages:**
- More powerful than FWER control methods
- Controls the expected fraction of false discoveries
- Suitable when many tests are expected to be significant

**Disadvantages:**
- Does not control FWER
- Assumes tests are independent or positively correlated
- Less conservative — may allow more false positives

### 8.6 Recommendation for Future Versions

The recommended approach for MIIE is:

1. **D-01**: Apply Bonferroni correction across metrics within each window pair. Each metric-window pair is an independent test.
2. **D-02**: Apply Benjamini-Hochberg across metric pairs. Correlation tests are often positively correlated, making BH appropriate.
3. **D-03**: Apply Bonferroni correction across thresholds within each window. Thresholds are tested independently.
4. **Cross-detector**: Do not apply correction across detectors (D-01, D-02, D-03), as they test different hypotheses.

### 8.7 Impact Assessment

Implementing multiple comparison correction would:

- Reduce false positive rate (currently unknown, expected to be > 0.05)
- Reduce true positive rate (power loss)
- Increase the minimum sample size needed for significant detections
- Require recalibration of benchmark precision/recall targets

---

## 9. Adaptive Statistics

### 9.1 Adaptive PSI Bins

The current PSI implementation uses fixed 10-bin equal-width binning. Adaptive binning would:

- Use Sturges' rule: `k = ⌈log₂(n) + 1⌉` for small samples
- Use Freedman-Diaconis rule: `width = 2 × IQR × n⁻¹/³` for moderate samples
- Cap maximum bins at 20 to prevent overfitting

**Expected impact**: More stable PSI values for small samples, more sensitive detection for large samples.

### 9.2 Adaptive Thresholds

The current D-03 auto-threshold system uses a fixed set of candidates. Adaptive thresholds would:

- Compute thresholds based on the data distribution (e.g., local modes, quantiles)
- Use kernel density estimation to identify peaks
- Adapt the number of thresholds to the data complexity

**Expected impact**: Better detection of compression at non-standard thresholds.

### 9.3 Dynamic Confidence

The current confidence formula uses fixed factor weights. Dynamic confidence would:

- Weight factors based on the specific metric and detector context
- Use Bayesian updating to incorporate prior knowledge
- Adjust the sample size target based on the metric's inherent variability

**Expected impact**: More accurate confidence estimates for different metric types.

### 9.4 Adaptive Window Sizing

The sampling framework already supports adaptive window sizing. Future improvements would:

- Use changepoint detection to identify natural window boundaries
- Adapt window sizes to the metric's autocorrelation structure
- Balance window size against the detector's minimum requirements

**Expected impact**: Better alignment between window boundaries and development activity changes.

---

## 10. Scientific Limitations

### 10.1 Approximate Dip Test

**Limitation**: MIIE uses a KS-based approximation of Hartigan's dip test, not the true dip statistic. The approximation may differ from the true test in power and size characteristics.

**Scientific impact**: Compression detections may be less reliable than they would be with the true dip test. The approximation may miss subtle multimodality or detect spurious multimodality.

**Mitigation**: The approximation is documented in DSVP §15.4. Benchmark targets account for the approximation's limitations.

### 10.2 Fixed PSI Bins

**Limitation**: PSI uses fixed 10-bin equal-width binning. This may not be appropriate for all data distributions.

**Scientific impact**: Small samples may produce noisy PSI values. Large samples may benefit from more bins. Heavy-tailed distributions may be poorly represented.

**Mitigation**: The 10-bin choice follows DES §21.2 convention. The epsilon floor prevents zero-proportion issues.

### 10.3 Small Sample Behaviour

**Limitation**: Many statistical tests have poor power or unreliable p-values with small samples. MIIE enforces minimum sample sizes, but these minima are themselves compromises.

**Scientific impact**: Small repositories may produce unreliable detections. Very small samples (n < 20) may produce either false positives or false negatives.

**Mitigation**: Minimum sample sizes are enforced. Confidence scores decrease for small samples. The severity multiplier reduces impact for sparse data.

### 10.4 Window Dependence

**Limitation**: The validity of drift and correlation detections depends on the windowing strategy. Different window sizes and boundaries may produce different results.

**Scientific impact**: Results may not be comparable across different windowing configurations. Optimal windowing depends on the development activity pattern.

**Mitigation**: The sampling framework provides adaptive window sizing. Configuration documents the windowing strategy.

### 10.5 Provider Limitations

**Limitation**: MIIE currently supports only Git and GitHub providers. Repositories hosted on other platforms cannot be fully analyzed.

**Scientific impact**: Analyses are limited to what the available providers can extract. Missing providers reduce coverage and confidence.

**Mitigation**: The provider framework supports additional providers. Quality scoring reflects provider availability.

### 10.6 Missing Observations

**Limitation**: Some metric-window pairs may have no observations. This reduces coverage and may bias the analysis.

**Scientific impact**: Missing observations reduce confidence and may mask real integrity violations.

**Mitigation**: The missing data factor in the confidence score penalizes missing observations. The severity multiplier reduces impact for sparse metrics.

### 10.7 Multiple Testing

**Limitation**: MIIE does not currently apply multiple comparison correction. The false positive rate may exceed the nominal 0.05 level.

**Scientific impact**: Some detections may be false positives. The integrity score may be lower than warranted.

**Mitigation**: The effect size normalization and severity multiplier provide some protection against false positives. Multiple comparison correction is recommended for future versions (§8.6).

### 10.8 Effect Size Interpretation

**Limitation**: The normalization constants for effect sizes (0.5 for KS, 0.3 for Δr) are based on convention, not theory. Different constants would produce different severity assessments.

**Scientific impact**: The severity of detections may be over- or under-estimated depending on the normalization.

**Mitigation**: The normalization constants are documented and frozen. Sensitivity analysis would be needed to assess the impact of different constants.

### 10.9 Non-Parametric Limitations

**Limitation**: Non-parametric tests (KS, Spearman) are less powerful than their parametric counterparts when assumptions are met.

**Scientific impact**: MIIE may miss real effects that a parametric test would detect.

**Mitigation**: Non-parametric tests are used because their assumptions are more likely to hold for diverse software engineering metrics.

### 10.10 Temporal Assumptions

**Limitation**: MIIE assumes that observations within a window are exchangeable and that windows are independent. In reality, development activity has temporal structure (autocorrelation, trend, seasonality).

**Scientific impact**: Temporal structure may produce spurious drift detections or mask real drift.

**Mitigation**: The minimum window size requirements and the sampling framework's adaptive windowing partially address this limitation.

---

## 11. Threats to Statistical Validity

### 11.1 Internal Validity

Internal validity asks: are the causal conclusions warranted given the study design?

**Threats:**

- **Confounding**: Changes in development practices, tooling, or team composition may produce metric changes that are not integrity violations
- **Selection bias**: The choice of analysis window may selectively include or exclude relevant data
- **Maturation**: Natural evolution of the codebase may produce legitimate metric changes that detectors flag as violations

**Mitigations:**

- The evidence package records all parameters for audit
- Multiple detectors reduce the risk of a single confounding factor
- The confidence score indicates the reliability of the analysis

### 11.2 Construct Validity

Construct validity asks: does MIIE measure what it claims to measure?

**Threats:**

- **Incomplete construct coverage**: MIIE detects three types of integrity violations but may miss others (e.g., synthetic commits, AI-generated code patterns)
- **Measurement error**: Provider extraction may introduce noise or bias into observations
- **Face validity**: The statistical tests may not align with human intuition about integrity violations

**Mitigations:**

- The benchmark framework evaluates detection accuracy against ground truth
- The observation quality system tracks measurement reliability
- The evidence package enables human review of detection findings

### 11.3 External Validity

External validity asks: do the results generalize beyond the specific study?

**Threats:**

- **Repository bias**: Results from open-source repositories may not generalize to proprietary codebases
- **Language bias**: Results from Python-heavy repositories may not generalize to other languages
- **Provider bias**: Results from GitHub-hosted repositories may not generalize to other platforms
- **Temporal bias**: Results from a specific time period may not generalize to other periods

**Mitigations:**

- The benchmark suite includes diverse repository types
- The provider framework supports multiple platforms
- The configuration allows analysis of arbitrary time ranges

### 11.4 Conclusion Validity

Conclusion validity asks: are the statistical conclusions warranted given the data?

**Threats:**

- **Small sample size**: Limited observations reduce the power of statistical tests
- **Multiple testing**: Inflated false positive rate without correction
- **Effect size ambiguity**: Normalization constants affect severity interpretation
- **p-value misinterpretation**: Small p-values indicate statistical significance, not practical significance

**Mitigations:**

- Minimum sample size requirements are enforced
- The confidence score reflects the reliability of conclusions
- Effect sizes are reported alongside p-values
- The evidence package enables independent verification

### 11.5 Measurement Validity

Measurement validity asks: are the measurements accurate and meaningful?

**Threats:**

- **Construct irrelevant variance**: Noise in observations that is unrelated to the metric construct
- **Construct underrepresentation**: Observations that fail to capture the full metric construct
- **Method variance**: Differences in measurement method (Git vs GitHub) that affect values

**Mitigations:**

- Quality tagging distinguishes complete, estimated, and derived observations
- Provider diversity factor rewards multi-source validation
- The evidence package records the measurement method for each observation

### 11.6 Sampling Bias

Sampling bias occurs when the observed sample is not representative of the population.

**Sources:**

- Provider extraction may miss certain types of commits or PRs
- The analysis window may not cover the full development history
- Repository activity patterns may not be representative

**Mitigations:**

- The sampling framework attempts to select representative windows
- Quality scoring reflects the completeness of the sample
- The confidence score penalizes low coverage

### 11.7 Repository Bias

Different repositories have different characteristics that may affect analysis results.

**Sources:**

- Repository size (small vs large)
- Development activity (active vs dormant)
- Team structure (solo vs distributed)
- Tooling (CI/CD, code review, testing)

**Mitigations:**

- The configuration allows customization of analysis parameters
- The confidence score reflects the adequacy of the data
- The evidence package enables repository-specific interpretation

### 11.8 Provider Bias

Different providers may extract different observations from the same repository.

**Sources:**

- Git provider may extract different metrics than GitHub provider
- API rate limits may cause incomplete extraction
- Authentication differences may affect data access

**Mitigations:**

- Provider diversity factor rewards multi-source validation
- The evidence package records the provider for each observation
- Quality scoring reflects provider availability

### 11.9 Observation Bias

Individual observations may be biased or inaccurate.

**Sources:**

- Commit messages may not accurately reflect code changes
- PR metadata may be influenced by process rather than quality
- Timestamps may not accurately reflect when work occurred

**Mitigations:**

- Quality tagging identifies estimated and derived observations
- The confidence score penalizes low-quality observations
- The evidence package enables observation-level audit

---

## 12. Statistical Validation Strategy

### 12.1 Unit Validation

**Purpose**: Verify that each statistical function produces correct results for known inputs.

**Approach**:
- Test each function with hand-computed examples
- Test edge cases (empty input, single value, identical values, extreme values)
- Test numerical stability (very large/small values, near-zero denominators)

**Coverage**: Every function in `statistics.py` and `scoring/utils.py`.

### 12.2 Synthetic Validation

**Purpose**: Verify that detectors correctly identify known patterns in synthetic data.

**Approach**:
- Generate synthetic time series with known drift, correlation breakdown, and compression
- Run detectors and compare findings against ground truth
- Compute precision, recall, and F1 scores

**Coverage**: D-01, D-02, D-03 with controlled synthetic datasets.

### 12.3 Benchmark Validation

**Purpose**: Evaluate detection accuracy against ground truth on realistic datasets.

**Approach**:
- Use the benchmark framework (DES-v1.0) with synthetic and real repository data
- Compute confusion matrices for each detector
- Compare against hard targets (precision ≥ 0.80, recall ≥ 0.75)

**Coverage**: All three detectors across multiple dataset categories.

### 12.4 Real Repository Validation

**Purpose**: Verify that MIIE produces meaningful results on real repositories.

**Approach**:
- Run the full pipeline against public GitHub repositories
- Review detection findings for face validity
- Compare across repositories with different characteristics

**Coverage**: Multiple repositories across different languages, sizes, and activity levels.

### 12.5 Cross-Platform Validation

**Purpose**: Verify that results are consistent across platforms.

**Approach**:
- Run the same analysis on Windows, macOS, and Linux
- Compare numerical results for consistency
- Verify deterministic output across platforms

**Coverage**: Full test suite on all supported platforms.

### 12.6 Reproducibility Validation

**Purpose**: Verify that results are reproducible across runs.

**Approach**:
- Run the same analysis 100 times with identical inputs
- Compare all numerical results for exact equality
- Verify evidence package determinism

**Coverage**: All statistical functions and detector algorithms.

### 12.7 Determinism Validation

**Purpose**: Verify that no non-deterministic operations affect results.

**Approach**:
- Run analyses with different random seeds
- Verify that results change only when expected (bootstrap procedures)
- Verify that non-random components are identical across seeds

**Coverage**: All code paths that use random number generation.

### 12.8 Performance Validation

**Purpose**: Verify that statistical computations complete within acceptable time bounds.

**Approach**:
- Profile detector execution time
- Verify bootstrap procedures complete within 10s per threshold
- Verify full pipeline completes within 60s for typical repositories

**Coverage**: All computational bottlenecks.

---

## 13. Acceptance Criteria

### 13.1 Minimum Sample Sizes

| Component | Minimum | Justification |
|-----------|---------|---------------|
| D-01 per window pair | 10 observations | KS test asymptotic approximation reliability |
| D-02 per window pair | 10 observations | Correlation estimation reliability |
| D-02 across windows | 2 windows | Correlation comparison requires ≥2 time points |
| D-03 per window | 20 observations | Excess mass z-test normal approximation |
| Fisher z CI | 4 observations | SE = 1/√(n-3), requires n > 3 |
| Metric computation | 1 observation | Minimum for aggregation |
| M-03 Churn Ratio | 5 observations | Dependency on M-07, reliability threshold |
| M-05 Review Latency | 2 observations | Mean requires ≥2 for meaningful uncertainty |

### 13.2 Confidence Thresholds

| Metric | Low | Medium | High |
|--------|-----|--------|------|
| Metric confidence | < 0.3 | 0.3 – 0.7 | > 0.7 |
| Score confidence | < 0.5 | 0.5 – 0.8 | > 0.8 |

### 13.3 Effect Sizes

| Effect | Small | Medium | Large |
|--------|-------|--------|-------|
| KS statistic | < 0.1 | 0.1 – 0.3 | > 0.3 |
| Correlation change | < 0.1 | 0.1 – 0.3 | > 0.3 |
| Compression index | < 0.1 | 0.1 – 0.3 | > 0.3 |

### 13.4 Acceptable Uncertainty

| Metric | Maximum CV | Justification |
|--------|-----------|---------------|
| Confidence score | 0.5 | CV > 0.5 → variance factor = 0 |
| Metric value | Dependent on metric | Range-specific |

### 13.5 Reproducibility

- 100 identical runs must produce byte-identical outputs
- Evidence package hash must be identical across runs
- Detection findings must be identical across runs

### 13.6 Numerical Stability

- No NaN values in outputs (except explicitly handled)
- No infinite values in outputs (except explicitly handled)
- Floating-point operations must be within 1e-10 of analytical values
- Clamped values must be exactly at the boundary when clamped

### 13.7 Deterministic Ordering

- JSON output must use `sort_keys=True`
- Window iteration must follow temporal order
- Metric computation must follow dependency order (topological sort)
- Graph construction must follow deduplication policy order

---

## 14. Future Statistical Evolution

### 14.1 True Hartigan Dip Test

**Current state**: MIIE uses a KS-based approximation of the dip test.

**Future state**: Implement the true Hartigan dip statistic using the consecutive convex minorant algorithm.

**Why future**: The true dip test requires a specialized algorithm not available in standard Python libraries. The approximation captures the essential idea while being computationally tractable. The true test would improve power and accuracy for compression detection.

**Impact**: More reliable compression detections, better discrimination between unimodal and multimodal distributions.

### 14.2 Adaptive PSI

**Current state**: Fixed 10-bin equal-width binning.

**Future state**: Adaptive binning using Sturges' rule, Freedman-Diaconis, or Scott's rule.

**Why future**: The fixed binning follows established convention (DES §21.2). Adaptive binning requires additional complexity and validation. The current approach is a conservative baseline.

**Impact**: More stable PSI values for small samples, more sensitive detection for large samples.

### 14.3 Bayesian Confidence

**Current state**: Frequentist confidence factors with fixed weights.

**Future state**: Bayesian confidence using posterior distributions.

**Why future**: Bayesian methods require prior specification, which adds complexity and subjective choices. The current frequentist approach is simpler and more widely understood. Bayesian methods would provide more natural uncertainty quantification.

**Impact**: More principled uncertainty quantification, ability to incorporate prior knowledge.

### 14.4 Robust Estimators

**Current state**: Mean and standard deviation for aggregation and uncertainty.

**Future state**: Median and median absolute deviation (MAD) as robust alternatives.

**Why future**: Robust estimators are less affected by outliers but less efficient for normal data. The current estimators are standard and well-understood. Robust estimators would improve performance on skewed distributions.

**Impact**: Better handling of outliers and skewed distributions.

### 14.5 Multivariate Detectors

**Current state**: Univariate detectors operating on individual metrics or metric pairs.

**Future state**: Multivariate detectors operating on the full metric vector simultaneously.

**Why future**: Multivariate methods (PCA, Mahalanobis distance, multivariate EWMA) can detect anomalies that univariate methods miss. They require more complex implementation and interpretation. The current univariate approach is simpler and more interpretable.

**Impact**: Detection of complex anomalies involving multiple metrics simultaneously.

### 14.6 Causal Inference

**Current state**: Associational analysis (correlation, not causation).

**Future state**: Causal inference methods (Granger causality, instrumental variables, difference-in-differences).

**Why future**: Causal inference requires stronger assumptions and more complex methodology. The current associational approach is sufficient for detecting integrity violations. Causal methods would enable understanding of why violations occur.

**Impact**: Understanding of causal mechanisms behind integrity violations, not just their detection.

---

## 15. Statistical Glossary

| Term | Definition |
|------|-----------|
| **Alpha (α)** | The significance level of a statistical test. The probability of rejecting the null hypothesis when it is true (Type I error). MIIE uses α = 0.05. |
| **Asymptotic** | A property that holds as the sample size approaches infinity. The KS p-value approximation is asymptotic. |
| **Bias** | The systematic difference between an estimator and the true population parameter. An unbiased estimator has zero expected bias. |
| **Bootstrap** | A resampling method that estimates the sampling distribution of a statistic by repeatedly sampling with replacement from the observed data. |
| **Bonferroni correction** | A method for controlling the family-wise error rate by dividing α by the number of tests. |
| **Coefficient of Variation (CV)** | The ratio of the standard deviation to the absolute mean. Measures relative variability. |
| **Confidence Interval (CI)** | A range of values that is likely to contain the true population parameter with a specified probability. |
| **Confidence Score** | A [0, 1] value quantifying the reliability of a statistical conclusion in MIIE. |
| **Construct validity** | The degree to which a measurement instrument measures what it claims to measure. |
| **Deterministic** | A property of a function or algorithm that produces identical outputs for identical inputs, with no random variation. |
| **Effect size** | A quantitative measure of the magnitude of a statistical effect. MIIE uses KS statistic, correlation change, and compression index. |
| **Empirical CDF (ECDF)** | The cumulative distribution function constructed from observed data. F̂(x) = (count of values ≤ x) / n. |
| **Epsilon (ε)** | A small positive constant used to avoid division by zero or logarithm of zero. MIIE uses ε = 10⁻¹⁰. |
| **Excess Mass** | The difference between the observed proportion of observations near a threshold and the expected proportion under uniformity. |
| **Family-Wise Error Rate (FWER)** | The probability of making at least one false positive error among a set of statistical tests. |
| **Fisher z-transformation** | A transformation that maps the correlation coefficient r to a normally distributed variable z = arctanh(r). |
| **Freedman-Diaconis rule** | A method for determining bin width: width = 2 × IQR × n⁻¹/³. |
| **Hartigan's Dip Test** | A test for unimodality. The dip statistic is the maximum difference between the ECDF and the closest unimodal distribution. |
| **Kolmogorov-Smirnov (KS) test** | A non-parametric test comparing two distributions based on the maximum CDF difference. |
| **Null Hypothesis (H₀)** | The hypothesis that there is no effect or no difference. MIIE tests H₀ of no distribution change, no correlation breakdown, no compression. |
| **P-value** | The probability of observing results at least as extreme as the data, assuming the null hypothesis is true. |
| **Pearson correlation (r)** | A measure of linear association between two variables, ranging from -1 to +1. |
| **Population Stability Index (PSI)** | A measure of distribution shift: PSI = Σ(qᵢ - pᵢ) × ln(qᵢ/pᵢ). Values > 0.25 indicate significant drift. |
| **Power** | The probability of correctly rejecting a false null hypothesis. Power = 1 - β (Type II error rate). |
| **Precision** | The fraction of positive detections that are true positives. Precision = TP / (TP + FP). |
| **Provenance** | The origin and history of a data point or result. MIIE records full provenance in evidence packages. |
| **Recall** | The fraction of true positives that are detected. Recall = TP / (TP + FN). |
| **Reproducibility** | The ability to produce identical results from identical inputs, with no random variation. |
| **Spearman ρ** | A rank-based measure of monotonic association, ranging from -1 to +1. |
| **Standard Error (SE)** | The standard deviation of the sampling distribution of a statistic. SE = 1/√(n-3) for Fisher z. |
| **Statistical significance** | A result is statistically significant if the p-value is less than the significance level α. |
| **Supremum (sup)** | The least upper bound of a set. The KS statistic is the supremum of the absolute CDF difference. |
| **Type I Error** | Rejecting the null hypothesis when it is true (false positive). |
| **Type II Error** | Failing to reject the null hypothesis when it is false (false negative). |
| **Unimodal** | Having a single mode (peak). The dip test tests for unimodality. |
| **Variance** | The expected squared deviation from the mean. σ² = Σ(xᵢ - μ)² / n. |

---

## 16. Appendices

### Appendix A: Statistical Notation

| Symbol | Meaning |
|--------|---------|
| X, Y | Samples (random variables) |
| xᵢ, yᵢ | Individual observations |
| x̄, ȳ | Sample means |
| σ, s | Population/sample standard deviation |
| σ², s² | Population/sample variance |
| n, n₁, n₂ | Sample sizes |
| r | Pearson correlation coefficient |
| ρ | Spearman rank correlation coefficient |
| D | KS statistic |
| p | p-value |
| α | Significance level |
| β | Type II error rate |
| F̂(x) | Empirical CDF |
| U(x) | Uniform CDF |
| SE | Standard error |
| CI | Confidence interval |
| CV | Coefficient of variation |
| PSI | Population Stability Index |
| ε | Epsilon (small constant) |
| B | Number of bootstrap samples |
| k | Number of tests / bins |
| z | Fisher z-transformed value |
| Φ | Standard normal CDF |

### Appendix B: Formula Summary

| Formula | Expression | Reference |
|---------|-----------|-----------|
| KS statistic | D = sup_x \|F̂₁(x) - F̂₂(x)\| | §6.1 |
| KS p-value | p = 2 × exp(-2D²n_eff) | §6.1 |
| PSI | PSI = Σ(qᵢ - pᵢ) × ln(qᵢ/pᵢ) | §6.2 |
| Pearson r | r = Σ(xᵢ-x̄)(yᵢ-ȳ) / √(Σ(xᵢ-x̄)²Σ(yᵢ-ȳ)²) | §6.3 |
| Spearman ρ | ρ = Pearson(ranked(X), ranked(Y)) | §6.4 |
| Fisher z | z = 0.5 × ln((1+r)/(1-r)) | §6.5 |
| Fisher z CI | CI = (tanh(z - z_crit×SE), tanh(z + z_crit×SE)) | §6.5 |
| Fisher z SE | SE = 1/√(n-3) | §6.5 |
| Excess mass z | z = (p - p₀)/√(p₀(1-p₀)/n) | §6.7 |
| Epsilon | ε = max(0.02\|T\|, 0.01×range(X)) | §6.7 |
| Dip statistic | dip = max_x \|F̂(x) - U(x)\| | §6.6 |
| CV | CV = σ/\|μ\| | §6.11 |
| Metric confidence | c = 0.3f₁ + 0.3f₂ + 0.2f₃ + 0.2f₄ | §5.5 |
| Score confidence | CS = f₁×f₂×f₃×f₄×f₅×f₆ | §5.5 |
| Integrity score | IS = 1.0 - (w₁d₁ + w₂d₂ + w₃d₃) | §6.9 |
| Drift magnitude | min(1.0, KS/0.5) | §6.9 |
| Breakdown magnitude | min(1.0, \|Δr\|/0.3) | §6.9 |
| Severity multiplier | 0.5 + 0.5 × coverage | §6.9 |

### Appendix C: Detector-to-Statistic Mapping

| Detector | Statistics Used | Thresholds |
|----------|----------------|------------|
| D-01 Distribution Drift | KS two-sample test, PSI | p < 0.05, PSI > 0.25 |
| D-02 Correlation Breakdown | Pearson r, Spearman ρ, Fisher z CI | \|Δr\| > 0.3, sign reversal \|r\| > 0.2, slope < -0.1 |
| D-03 Threshold Compression | Excess mass z-test, Dip test (KS approx) | z > 1.645, dip p < 0.05 |

### Appendix D: Metric-to-Statistic Mapping

| Metric | Aggregation | Uncertainty | Confidence Factors |
|--------|------------|-------------|-------------------|
| M-01 Entropy Ratio | mean | σ | sample size, quality, uncertainty, diversity |
| M-02 Commit Count | sum | σ | sample size, quality, uncertainty, diversity |
| M-03 Churn Ratio | mean | σ | sample size, quality, uncertainty, diversity |
| M-04 Test Coverage | mean | σ | sample size, quality, uncertainty, diversity |
| M-05 Review Latency | mean | σ | sample size, quality, uncertainty, diversity |
| M-06 File Change Count | sum | σ | sample size, quality, uncertainty, diversity |
| M-07 Branch Freshness | mean | σ | sample size, quality, uncertainty, diversity |

### Appendix E: Validation Checklist

| Check | Method | Target |
|-------|--------|--------|
| D-01 precision | Benchmark evaluation | ≥ 0.80 |
| D-01 recall | Benchmark evaluation | ≥ 0.75 |
| D-02 precision | Benchmark evaluation | ≥ 0.75 |
| D-02 recall | Benchmark evaluation | ≥ 0.70 |
| D-03 precision | Benchmark evaluation | ≥ 0.85 |
| D-03 recall | Benchmark evaluation | ≥ 0.80 |
| KS test correctness | Hand-computed examples | Exact match |
| PSI correctness | Hand-computed examples | Exact match |
| Pearson r correctness | Hand-computed examples | Exact match |
| Fisher z correctness | Hand-computed examples | Exact match |
| Excess mass correctness | Hand-computed examples | Exact match |
| Dip test correctness | Synthetic bimodal data | p < 0.05 |
| Confidence score range | All analyses | [0, 1] |
| Integrity score range | All analyses | [0, 1] |
| Reproducibility | 100 identical runs | 100% identical |
| Determinism | Multi-platform runs | Byte-identical |
| Numerical stability | Edge cases | No NaN/Inf |

---

*This document is the scientific statistical constitution of the MIIE repository. Every statistical implementation must conform to this specification.*
