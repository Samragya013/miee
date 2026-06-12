> **MIIE** **Technical** **Freeze** **Sheet** **(TFS** **v1.0)**
> **Document** **Version:** 1.0
>
> **Status:** Technical Freeze — Pre-TRD Authority **Date:** 2026-06-07
>
> **Aligned** **With:** IPD v1.1 FINAL \| PRD v1.0
>
> **Objective:** Eliminate all implementation ambiguity. Three
> independent engineering teams using only IPD + PRD + TFS must produce
> functionally equivalent systems.
>
> **SECTION** **1** **—** **Product** **Freeze** **Summary**
>
> **1.1** **Frozen** **Product** **Name**
>
> **Measurement** **Integrity** **Intelligence** **Engine** **(MIIE)**
> *Frozen.* *No* *aliases* *permitted* *in* *V1* *documentation* *or*
> *code.*
>
> **1.2** **Frozen** **Mission**
>
> Evaluate whether software engineering metrics remain trustworthy
> representations of the constructs they claim to measure.
>
> *Frozen.* *V1* *does* *not* *measure* *productivity,* *code*
> *quality,* *or* *team* *performance.* *V1* *measures* *the*
> *integrity* *of* *metrics* *themselves.*
>
> **1.3** **Frozen** **Scope**
>
> V1 is frozen to exactly eight capabilities:

||
||
||
||
||
||
||
||
||
||
||

||
||
||
||

> **1.4** **Frozen** **Version** **1** **Objectives**
>
> 1\. **Repository** **Analysis:** Ingest any public Git repository;
> extract V1 metrics; segment into windows; run all detectors; produce
> scores, evidence, and explanations.
>
> 2\. **Detector** **Validation:** Execute benchmark suites to report
> precision, recall, F1, AUC-ROC, AUC-PR per detector.
>
> 3\. **Reproducibility:** Any analysis must be bitwise-identical when
> re-run with identical inputs, configuration, and random seed.
>
> 4\. **Transparency:** Every detector decision must be traceable to a
> specific statistical test, threshold, and data window.
>
> 5\. **Publication** **Support:** All outputs must be suitable for
> direct inclusion in peer-reviewed software engineering research.
>
> **1.5** **Frozen** **Out-of-Scope** **List**
>
> The following are **permanently** **excluded** from V1. No engineering
> team may implement them, regardless of user request:

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **SECTION** **2** **—** **Version** **1** **Metric** **Inventory**
>
> **2.1** **Supported** **Metrics** **(Frozen)**
>
> V1 officially supports exactly **7** **metrics**. No additional
> metrics may be included in V1 releases.
>
> ***M-01:*** ***Code*** ***Coverage***

||
||
||
||
||
||
||
||
||
||
||
||

> ***M-02:*** ***Commit*** ***Frequency***

||
||
||
||
||
||
||
||

||
||
||
||
||
||
||

> ***M-03:*** ***Review*** ***Participation***

||
||
||
||
||
||
||
||
||
||
||
||

> ***M-04:*** ***Review*** ***Latency***

||
||
||
||

||
||
||
||
||
||
||
||
||
||
||

> ***M-05:*** ***Issue*** ***Resolution*** ***Time***

||
||
||
||
||
||
||
||
||
||
||

||
||
||
||

> ***M-06:*** ***Code*** ***Churn***

||
||
||
||
||
||
||
||
||
||
||
||

> ***M-07:*** ***Cyclomatic*** ***Complexity***

||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

> **2.2** **Metric** **Extraction** **Priority** **Rules** **(Frozen)**
>
> 1\. **Git-derived** **metrics** (M-02, M-06) are always attempted.
>
> 2\. **Static** **analysis** **metrics** (M-07) are attempted if
> supported files exist; if tool missing, metric is unavailable.
>
> 3\. **Coverage** **metrics** (M-01) are attempted if artifacts exist;
> if absent, metric is unavailable.
>
> 4\. **External** **data** **metrics** (M-03, M-04, M-05) are attempted
> only if user provides PR/MR/issue export; if absent, metric is
> unavailable.
>
> 5\. **Unavailable** **metrics** do not fail the analysis; they are
> excluded from scoring with a warning in the confidence score.
>
> **SECTION** **3** **—** **Unsupported** **Metrics**
>
> **3.1** **Excluded** **Metrics** **Table**

||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||

> **3.2** **Exclusion** **Governance** **Rule**
>
> No engineering team may add any metric not in Section 2.1 to V1, even
> as an "experimental" or "hidden" feature. All metric additions require
> IPD/PRD amendment and TFS v2.0.
>
> **SECTION** **4** **—** **Detector** **Freeze**
>
> **4.1** **V1** **Detector** **Inventory** **(Frozen)**
>
> V1 contains exactly **3** **detectors**. No additional detectors may
> be implemented in V1.
>
> ***D-01:*** ***Distributional*** ***Drift*** ***Detector***

||
||
||
||
||
||
||
||
||
||
||
||
||

> ***D-02:*** ***Correlation*** ***Breakdown*** ***Detector***

||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

> ***D-03:*** ***Threshold*** ***Compression*** ***Detector***

||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||

> **4.2** **Detector** **Activation** **Rules** **(Frozen)**
>
> 1\. All 3 detectors are **enabled** **by** **default** for every
> analysis.
>
> 2\. Users may disable individual detectors via --detectors CLI flag or
> API parameter.
>
> 3\. Disabled detectors do not contribute to Integrity Score.
>
> 4\. A detector that fails on a specific metric (e.g., insufficient
> data) does not abort the analysis; it logs a warning and excludes that
> metric-detector pair from scoring.
>
> **SECTION** **5** **—** **Detector** **Algorithms**
>
> **5.1** **D-01:** **Distributional** **Drift** **Detector**
> **Algorithm**
>
> ***Formal*** ***Definition***
>
> Given two windows W₁ and W₂ with metric values X₁ = {x₁₁, x₁₂, ...,
> x₁ₙ} and X₂ = {x₂₁, x₂₂, ..., x₂ₘ}, the detector tests:
>
> **H₀:** F₁(x) = F₂(x) for all x (the distributions are identical)
> **H₁:** F₁(x) ≠ F₂(x) for some x (the distributions differ)
>
> ***Mathematical*** ***Basis*** **Kolmogorov-Smirnov** **Test:** Dₙ,ₘ =
> supₓ \|F₁,ₙ(x) - F₂,ₘ(x)\|
>
> where F₁,ₙ and F₂,ₘ are empirical CDFs. Under H₀, the asymptotic
> distribution of Dₙ,ₘ is known; p-value computed via standard
> approximation.
>
> **Population** **Stability** **Index** **(PSI):**
>
> PSI = Σᵢ (Pᵢ - Qᵢ) × ln(Pᵢ / Qᵢ)
>
> where Pᵢ and Qᵢ are proportions in bin i for W₁ and W₂ respectively.
> Bins: 10 equal-width bins over \[min(X₁ ∪ X₂), max(X₁ ∪ X₂)\].
>
> ***Detection*** ***Logic***
>
> FOR each metric M in {M-01..M-07}:
>
> FOR each consecutive window pair (Wᵢ, Wᵢ₊₁): IF \|Wᵢ\| \< 10 OR
> \|Wᵢ₊₁\| \< 10:
>
> SKIP with warning "Insufficient sample size" CONTINUE
>
> \# KS Test
>
> D, p_value = ks_2samp(Wᵢ\[M\], Wᵢ₊₁\[M\]) IF p_value \< 0.05:
>
> drift_detected = TRUE
>
> ELSE:
>
> drift_detected = FALSE
>
> \# PSI Test
>
> PSI = compute_psi(Wᵢ\[M\], Wᵢ₊₁\[M\], bins=10) IF PSI \> 0.25:
>
> psi_drift = TRUE ELSE:
>
> psi_drift = FALSE
>
> \# Final flag: TRUE if KS OR PSI fires IF drift_detected OR psi_drift:
>
> FLAG drift for M between Wᵢ and Wᵢ₊₁
>
> \# Direction classification mean_diff = mean(Wᵢ₊₁) - mean(Wᵢ)
>
> var_ratio = var(Wᵢ₊₁) / var(Wᵢ) if var(Wᵢ) \> 0 else INF
>
> IF \|mean_diff\| \> 0.5 \* std(Wᵢ): direction = "mean_shift"
>
> IF var_ratio \< 0.5:
>
> direction = "variance_collapse"
>
> IF drift_detected AND NOT (mean_shift OR variance_collapse): direction
> = "shape_change"
>
> ***Threshold*** ***Logic***

||
||
||
||
||
||
||

> ***Example*** ***Input***
>
> {
>
> "metric": "coverage",
>
> "window_1": \[0.82, 0.85, 0.88, 0.90, 0.91, 0.93, 0.95, 0.97, 0.98,
> 0.99\], "window_2": \[0.98, 0.99, 0.99, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
> 1.0\]
>
> }
>
> ***Example*** ***Output***
>
> {
>
> "detector": "D-01", "metric": "coverage",
>
> "window_pair": \["2025-Q1", "2025-Q2"\], "drift_detected": true,
> "ks_statistic": 0.65,
>
> "ks_p_value": 0.002, "psi_value": 0.42,
>
> "direction": "variance_collapse", "mean_shift": -0.05,
> "variance_ratio": 0.02, "sample_sizes": \[10, 10\]
>
> }

***Expected*** ***Precision*** ***Range***

0.80 – 0.90 (on metric-drift-v1 benchmark)

***Expected*** ***Recall*** ***Range***

0.75 – 0.85 (on metric-drift-v1 benchmark)

***False*** ***Positive*** ***Sources***

> 1\. Natural seasonal variation in development activity.
>
> 2\. Small sample sizes causing KS test sensitivity.
>
> 3\. Legitimate process improvements that genuinely change
> distributions.

***False*** ***Negative*** ***Sources***

> 1\. Gradual drift below per-window-pair sensitivity.
>
> 2\. Drift masked by high variance in both windows.
>
> 3\. PSI insensitivity to shifts that preserve bin proportions.

***Publication*** ***References***

> Massey, F.J. (1951). "The Kolmogorov-Smirnov Test for Goodness of
> Fit." *Journal* *of* *the* *American* *Statistical* *Association*,
> 46(253), 68-78.
>
> Siddiqi, N. (2012). *Credit* *Risk* *Scorecards:* *Developing* *and*
> *Implementing* *Intelligent* *Credit* *Scoring*. Wiley. (PSI standard
> reference)

**5.2** **D-02:** **Correlation** **Breakdown** **Detector**
**Algorithm**

***Formal*** ***Definition***

Given two metrics A and B with paired observations in window W: {(a₁,
b₁), ..., (aₙ, bₙ)}, the detector tests whether the correlation between
A and B is stable across windows.

**H₀:** ρ(Wᵢ) = ρ(Wᵢ₊₁) (correlation is stable)

**H₁:** \|ρ(Wᵢ) - ρ(Wᵢ₊₁)\| \> δ (correlation has changed significantly)

***Mathematical*** ***Basis*** **Pearson** **Correlation:**

r = Σᵢ(aᵢ - ā)(bᵢ - b) / √\[Σᵢ(aᵢ - ā)² Σᵢ(bᵢ - b)²\]

**Spearman** **Rank** **Correlation:**

ρₛ = 1 - 6Σdᵢ² / n(n² - 1)

where dᵢ = rank(aᵢ) - rank(bᵢ).

**Fisher** **z-transformation** **for** **confidence** **intervals:**

z = 0.5 × ln((1 + r) / (1 - r))

> SE = 1 / √(n - 3)
>
> CI₉₅ = \[tanh(z - 1.96×SE), tanh(z + 1.96×SE)\]
>
> ***Detection*** ***Logic***
>
> FOR each metric pair (Mᵢ, Mⱼ) where i \< j: FOR each window Wₖ:
>
> IF paired_observations \< 10: SKIP with warning CONTINUE
>
> r_pearson\[Wₖ\] = pearsonr(Wₖ\[Mᵢ\], Wₖ\[Mⱼ\]) r_spearman\[Wₖ\] =
> spearmanr(Wₖ\[Mᵢ\], Wₖ\[Mⱼ\])
>
> \# Trajectory analysis requires ≥3 windows IF number_of_windows \< 3:
>
> breakdown = FALSE \# Cannot assess trajectory CONTINUE
>
> \# Breakdown Type 1: Sudden drop FOR k = 1 to K-1:
>
> delta = \|r_pearson\[Wₖ₊₁\] - r_pearson\[Wₖ\]\| IF delta \> 0.3:
>
> FLAG breakdown for (Mᵢ, Mⱼ) between Wₖ and Wₖ₊₁ type = "sudden_drop"
>
> \# Breakdown Type 2: Sign reversal FOR k = 1 to K-1:
>
> IF sign(r_pearson\[Wₖ\]) ≠ sign(r_pearson\[Wₖ₊₁\]) AND
> \|r_pearson\[Wₖ\]\| \> 0.2 AND \|r_pearson\[Wₖ₊₁\]\| \> 0.2:
>
> FLAG breakdown for (Mᵢ, Mⱼ) between Wₖ and Wₖ₊₁ type = "sign_reversal"
>
> \# Breakdown Type 3: Gradual erosion IF K ≥ 4:
>
> slope = linear_regression_slope(r_pearson over window indices)
>
> IF slope \< -0.1 per window AND r_pearson\[W₁\] \> 0.3 AND
> r_pearson\[Wₖ\] \< 0.1: FLAG breakdown for (Mᵢ, Mⱼ)
>
> type = "gradual_erosion"
>
> \# Breakdown Type 4: Confidence interval exclusion FOR k = 1 to K-1:
>
> IF NOT (CI₉₅(Wₖ₊₁) overlaps CI₉₅(Wₖ)):
>
> FLAG breakdown for (Mᵢ, Mⱼ) between Wₖ and Wₖ₊₁ type =
> "confidence_exclusion"
>
> ***Threshold*** ***Logic***

||
||
||
||
||
||
||

***Example*** ***Input***

{

> "metric_a": "complexity", "metric_b": "churn", "windows": {
>
> "2025-Q1": \[\[15, 120\], \[18, 150\], \[12, 80\], \[20, 200\], \[14,
> 110\]\], "2025-Q2": \[\[16, 125\], \[19, 140\], \[13, 90\], \[21,
> 180\], \[15, 100\]\], "2025-Q3": \[\[50, 20\], \[55, 25\], \[48, 18\],
> \[60, 30\], \[52, 22\]\]

} }

***Example*** ***Output***

{

> "detector": "D-02",
>
> "metric_pair": \["complexity", "churn"\], "breakdown_detected": true,
> "breakdown_type": "sign_reversal", "pearson_trajectory": \[0.72, 0.68,
> -0.45\], "spearman_trajectory": \[0.70, 0.65, -0.42\],
>
> "window_pairs_flagged": \[\["2025-Q2", "2025-Q3"\]\],
> "confidence_intervals": \[
>
> \[0.45, 0.89\], \[0.40, 0.86\], \[-0.78, -0.12\]

\] }

***Expected*** ***Precision*** ***Range***

0.75 – 0.85 (on correlation-breakdown-v1 benchmark)

***Expected*** ***Recall*** ***Range***

0.70 – 0.80 (on correlation-breakdown-v1 benchmark)

***False*** ***Positive*** ***Sources***

> 1\. Small sample sizes producing unstable correlation estimates.
>
> 2\. Confounding variables affecting one metric but not the other.
>
> 3\. Non-linear relationships misdetected by Pearson threshold.

***False*** ***Negative*** ***Sources***

> 1\. Breakdowns below the 0.3 magnitude threshold.
>
> 2\. Breakdowns in Spearman but not Pearson (or vice versa) if only one
> is monitored.
>
> 3\. Missing data creating artificial correlation stability.

***Publication*** ***References***

> Cohen, J. (1988). *Statistical* *Power* *Analysis* *for* *the*
> *Behavioral* *Sciences* (2nd ed.). Lawrence Erlbaum. (Effect size
> thresholds)
>
> Fisher, R.A. (1915). "Frequency Distribution of the Values of the
> Correlation Coefficient in Samples from an Indefinitely Large
> Population." *Biometrika*, 10(4), 507-521.

**5.3** **D-03:** **Threshold** **Compression** **Detector**
**Algorithm**

***Formal*** ***Definition***

Given a metric M with values X = {x₁, ..., xₙ} in window W, and a
threshold T, the detector tests whether values cluster within margin ε
of T at a rate significantly higher than expected under a uniform or
baseline distribution.

**H₀:** Values near T are consistent with the overall distribution (no
artificial clustering) **H₁:** Values near T are significantly
overrepresented (threshold compression detected)

***Mathematical*** ***Basis*** **Excess** **Mass** **Test:**

Let B(T, ε) = {x : \|x - T\| ≤ ε} (the "band" around threshold).

Expected proportion under uniform assumption: p₀ = 2ε / (max(X) -
min(X)) Observed proportion: p = \|B(T, ε)\| / n

Test statistic: z = (p - p₀) / √(p₀(1 - p₀) / n) Reject H₀ if z \> z₀.₉₅
(one-tailed, α = 0.05)

**Hartigans'** **Dip** **Test** **(supporting):**

D = inf_F supₓ \|Fₙ(x) - F(x)\|

where Fₙ is empirical CDF and F ranges over unimodal distributions.
p-value computed via bootstrap (n_boot = 1000, seed = 42).

***Detection*** ***Logic***

FOR each metric M in {M-01..M-07}: FOR each window W:

> IF \|W\| \< 20:
>
> SKIP with warning CONTINUE
>
> \# Determine thresholds explicit_thresholds = config.get(M, \[\])
>
> auto_thresholds = detect_round_numbers(W\[M\]) thresholds =
> explicit_thresholds + auto_thresholds
>
> FOR each threshold T in thresholds: IF T \< min(W\[M\]) OR T \>
> max(W\[M\]):
>
> CONTINUE
>
> ε = max(0.02 × T, 0.01 × (max(W\[M\]) - min(W\[M\])))
>
> \# Excess mass test
>
> in_band = count(\|x - T\| ≤ ε for x in W\[M\]) p_hat = in_band / \|W\|
>
> p_0 = 2 \* ε / (max(W\[M\]) - min(W\[M\]))
>
> IF p_0 \> 0.5:
>
> CONTINUE \# Band too wide; test meaningless
>
> z_score = (p_hat - p_0) / sqrt(p_0 \* (1 - p_0) / \|W\|)
>
> IF z_score \> 1.645: \# One-tailed, α = 0.05 excess_mass_flag = TRUE
>
> ELSE:
>
> excess_mass_flag = FALSE
>
> \# Dip test (supporting)
>
> dip_stat, dip_p = diptest(W\[M\], n_boot=1000, seed=42) IF dip_p \<
> 0.05:
>
> multimodal_flag = TRUE ELSE:
>
> multimodal_flag = FALSE
>
> \# Final flag: TRUE if excess_mass_flag AND (multimodal_flag OR p_hat
> \> 0.5)
>
> IF excess_mass_flag AND (multimodal_flag OR p_hat \> 0.5): FLAG
> compression for M at threshold T in window W compression_index = p_hat
>
> hypothesized_cause = infer_cause(M, T) \# Rule-based: see FR-010
>
> ***Threshold*** ***Logic***

||
||
||
||
||
||
||
||
||
||

> ***Auto-Threshold*** ***Detection***
>
> FOR each candidate T in \[1, 5, 10, 20, 25, 50, 75, 80, 90, 95, 100,
> 1000\]: IF T is within \[min(X), max(X)\]:
>
> ADD T to auto_thresholds
>
> FOR each percentile in \[10, 25, 50, 75, 90\]: T = percentile(X,
> percentile)
>
> IF T is a "round number" (ends in 0 or 5): ADD T to auto_thresholds
>
> REMOVE duplicates
>
> ***Example*** ***Input***
>
> {
>
> "metric": "coverage",
>
> "window": \[0.98, 0.99, 1.0, 1.0, 0.99, 1.0, 0.98, 1.0, 0.99, 1.0,
> 0.97, 0.98, 0.99, 1.0, 1.0, 0.99, 1.0, 0.98, 0.99, 1.0\],
>
> "thresholds": \[1.0, 0.95, 0.80\] }
>
> ***Example*** ***Output*** {
>
> "detector": "D-03", "metric": "coverage", "window": "2025-Q2",
> "compression_detected": true, "threshold": 1.0,
>
> "margin": 0.02, "compression_index": 0.75, "excess_mass_z_score": 4.2,
> "dip_test_statistic": 0.08, "dip_test_p_value": 0.003,
>
> "hypothesized_cause": "THRESHOLD_GAMING", "sample_size": 20

}

***Expected*** ***Precision*** ***Range***

0.85 – 0.95 (on threshold-compression-v1 benchmark)

***Expected*** ***Recall*** ***Range***

0.80 – 0.90 (on threshold-compression-v1 benchmark)

***False*** ***Positive*** ***Sources***

> 1\. Natural clustering at round numbers (e.g., file sizes at 1024
> bytes).
>
> 2\. Metrics with inherently bounded domains (e.g., percentages
> naturally cluster at extremes).
>
> 3\. Small windows with stochastic clustering.

***False*** ***Negative*** ***Sources***

> 1\. Compression below the 2% margin threshold.
>
> 2\. Compression at non-round thresholds not in auto-detection list.
>
> 3\. Uniform drift toward threshold that doesn't create sharp
> clustering.

***Publication*** ***References***

> Hartigan, J.A., & Hartigan, P.M. (1985). "The Dip Test of
> Unimodality." *The* *Annals* *of* *Statistics*, 13(1), 70-84.
>
> Ultsch, A. (2005). "Pareto Density Estimation: A Density Estimation
> for Knowledge Discovery." *Innovations* *in* *Classification,* *Data*
> *Science,* *and* *Information* *Systems*, 91-100.

**SECTION** **6** **—** **Integrity** **Score** **Freeze**

**6.1** **Purpose**

The Integrity Score (IS) quantifies the overall construct validity of a
metric or metric set by aggregating detector outputs. It answers:
*"Based* *on* *the* *statistical* *evidence,* *how* *likely* *is* *it*
*that* *this* *metric* *still* *measures* *what* *it* *claims* *to*
*measure?"*

**6.2** **Scale** **and** **Range**

> **Scale:** Continuous float
>
> **Range:** \[0.0, 1.0\]
>
> **Interpretation:**
>
> 1.0 = No detectors fired; metric appears fully valid.
>
> 0.0 = All detectors fired at maximum severity; metric appears
> completely invalid.
>
> \<0.5 = Serious validity concerns; metric should not be used without
> investigation.

**6.3** **Formula** **(Frozen)**

***Per-Metric*** ***Integrity*** ***Score*** For a single metric M, let:

> d₁ = D-01 severity (0 or 1, or 0–1 for magnitude if drift detected)
>
> d₂ = D-02 severity (0 or 1, or 0–1 for magnitude if breakdown
> detected)
>
> d₃ = D-03 severity (0 or 1, or 0–1 for magnitude if compression
> detected)
>
> w₁, w₂, w₃ = detector weights (default: w₁=0.40, w₂=0.35, w₃=0.25)

**Severity** **Calculation:**

IF D-01 fires on M:

> d_1 = min(1.0, mean(drift_magnitude across all window pairs))

where drift_magnitude = ks_statistic (normalized to \[0,1\] by capping
at 0.5) ELSE:

> d_1 = 0.0

IF D-02 fires on M:

d_2 = min(1.0, mean(breakdown_magnitude across all metric pairs and
window pairs))

where breakdown_magnitude = \|delta_r\| / 0.3 (capped at 1.0) ELSE:

> d_2 = 0.0

IF D-03 fires on M:

> d_3 = min(1.0, mean(compression_index across all thresholds and
> windows)) where compression_index is already in \[0,1\]

ELSE:

> d_3 = 0.0

**Per-Metric** **Score:**

IS_metric = 1.0 - (w₁ × d₁ + w₂ × d₂ + w₃ × d₃)

***Repository-Level*** ***Integrity*** ***Score***

IS_repo = mean(IS_metric for all available metrics M)

If a metric is unavailable (missing data), it is excluded from the mean.
The number of metrics included is reported.

> **6.4** **Weighting** **Logic** **(Frozen)**

||
||
||
||
||
||

> Weights are **configurable** via configuration file but must default
> to the above values. Any deviation must be logged in the evidence
> package.
>
> **6.5** **Normalization** **Logic**
>
> All severity values are normalized to \[0, 1\] before weighting.
>
> The final score is clamped to \[0, 1\].
>
> No non-linear transformations (sigmoid, log) are applied.
>
> **6.6** **Edge** **Cases**

||
||
||
||
||
||
||
||

> **6.7** **Confidence** **Intervals**
>
> V1 does **not** compute confidence intervals for the Integrity Score.
> The Confidence Score (Section 7) serves this purpose.
>
> **6.8** **Example** **Calculations** **Example** **1:** **Clean**
> **metric**
>
> D-01: no drift → d₁ = 0.0
>
> D-02: no breakdown → d₂ = 0.0
>
> D-03: no compression → d₃ = 0.0
>
> IS = 1.0 - (0.40×0 + 0.35×0 + 0.25×0) = **1.00**
>
> **Example** **2:** **Drift** **+** **compression**
>
> D-01: drift detected, ks_stat = 0.30 → d₁ = 0.30/0.50 = 0.60
>
> D-02: no breakdown → d₂ = 0.0
>
> D-03: compression detected, index = 0.75 → d₃ = 0.75
>
> IS = 1.0 - (0.40×0.60 + 0.35×0 + 0.25×0.75) = 1.0 - (0.24 + 0 +
> 0.1875) = **0.5725**
>
> **Example** **3:** **All** **pathologies**
>
> D-01: d₁ = 1.0
>
> D-02: d₂ = 1.0
>
> D-03: d₃ = 1.0
>
> IS = 1.0 - (0.40 + 0.35 + 0.25) = **0.00**
>
> **6.9** **Inter-Engineer** **Consistency** **Requirement**
>
> Given identical inputs, configurations, and detector outputs, three
> independent engineers must calculate identical Integrity Scores to
> within floating-point precision (\| ΔIS\| \< 1e-9). The formula above
> is deterministic and unambiguous.
>
> **SECTION** **7** **—** **Confidence** **Score** **Freeze**
>
> **7.1** **Purpose**
>
> The Confidence Score (CS) measures the **reliability** **of** **the**
> **Integrity** **Score** **assessment**, not the quality of the
> repository. It answers: *"How* *much* *should* *we* *trust* *the*
> *Integrity* *Score* *given* *the* *data* *we* *had?"*
>
> **7.2** **Scale** **and** **Range**
>
> **Scale:** Continuous float
>
> **Range:** \[0.0, 1.0\]
>
> **Interpretation:**
>
> 1.0 = Maximum confidence; data volume and quality are excellent.
>
> 0.0 = No confidence; assessment is unreliable.
>
> \<0.5 = Low confidence; results are speculative and should not be used
> for decisions.
>
> **7.3** **Inputs** **(Frozen)**

||
||
||
||
||

||
||
||
||
||
||
||

> **7.4** **Formula** **(Frozen)**
>
> CS = f₁ × f₂ × f₃ × f₄ × f₅
>
> All factors are in \[0, 1\]. The product ensures that any weak factor
> degrades confidence multiplicatively.
>
> **7.5** **Factor** **Details**
>
> ***f₁:*** ***Sample*** ***Size*** ***Factor***
>
> mean_n = mean(\|Wₖ\| for all k and all metrics with data) f₁ =
> min(1.0, mean_n / 50.0)
>
> If average sample size = 50 → f₁ = 1.0
>
> If average sample size = 25 → f₁ = 0.5
>
> If average sample size = 10 → f₁ = 0.2
>
> ***f₂:*** ***Variance*** ***Factor***
>
> FOR each metric M and window W with data: IF mean(W\[M\]) ≠ 0:
>
> CV = std(W\[M\]) / \|mean(W\[M\])\| ELSE:
>
> CV = 0 if std(W\[M\]) = 0 else INF → cap at 1.0 mean_CV = mean(CV for
> all valid windows)
>
> f₂ = 1.0 - min(1.0, mean_CV / 0.5)
>
> If mean CV = 0.0 → f₂ = 1.0 (perfect variance)
>
> If mean CV = 0.5 → f₂ = 0.0 (too noisy)
>
> If mean CV = 0.25 → f₂ = 0.5
>
> ***f₃:*** ***Missing*** ***Data*** ***Factor***
>
> total_pairs = num_metrics × num_windows
>
> missing_pairs = count of (metric, window) pairs with no data f₃ =
> 1.0 - (missing_pairs / total_pairs)
>
> ***f₄:*** ***Window*** ***Balance*** ***Factor***
>
> window_sizes = \[sum(\|Wₖ\| across all metrics) for each window k\]
> mean_size = mean(window_sizes)
>
> std_size = std(window_sizes) IF mean_size \> 0:
>
> f₄ = 1.0 - min(1.0, std_size / mean_size) ELSE:
>
> f₄ = 0.0
>
> ***f₅:*** ***Detector*** ***Success*** ***Factor***
>
> total_attempts = num_metrics × num_detectors (adjusted for metric
> availability) successful_runs = count of detector executions that
> completed (not skipped)
>
> f₅ = successful_runs / total_attempts
>
> **7.6** **Interpretation** **Bands** **(Frozen)**

||
||
||
||
||
||
||

> **7.7** **Example** **Calculations** **Example** **1:** **Excellent**
> **data**
>
> f₁ = 80/50 = 1.0 (capped)
>
> f₂ = 1.0 - 0.1/0.5 = 0.8
>
> f₃ = 1.0 (no missing data)
>
> f₄ = 1.0 - 5/50 = 0.9
>
> f₅ = 1.0 (all detectors succeeded)
>
> CS = 1.0 × 0.8 × 1.0 × 0.9 × 1.0 = **0.72** (Medium-High)
>
> **Example** **2:** **Sparse** **data**
>
> f₁ = 15/50 = 0.3
>
> f₂ = 1.0 - 0.6/0.5 = 0.0 (capped at 0)
>
> f₃ = 0.7
>
> f₄ = 0.8
>
> f₅ = 0.9
>
> CS = 0.3 × 0.0 × 0.7 × 0.8 × 0.9 = **0.00** (Critical)
>
> **Example** **3:** **Moderate** **data**
>
> f₁ = 40/50 = 0.8
>
> f₂ = 1.0 - 0.2/0.5 = 0.6
>
> f₃ = 0.9
>
> f₄ = 0.85
>
> f₅ = 1.0
>
> CS = 0.8 × 0.6 × 0.9 × 0.85 × 1.0 = **0.3672** (Low)
>
> **7.8** **Inter-Engineer** **Consistency** **Requirement**
>
> Given identical inputs and window definitions, three independent
> engineers must calculate identical Confidence Scores to within
> floating-point precision (\|ΔCS\| \< 1e-9). The product formula is
> deterministic and unambiguous.
>
> **SECTION** **8** **—** **Benchmark** **Freeze**
>
> **8.1** **Benchmark** **Assumptions** **(Frozen)**
>
> 1\. Benchmarks are the **sole** **mechanism** for validating detector
> performance in V1.
>
> 2\. Benchmarks are **versioned** **independently** of MIIE releases.
>
> 3\. Benchmarks are **self-contained**: all data, labels, and metadata
> are in the benchmark directory.
>
> 4\. Benchmarks are **immutable**: once published, a benchmark version
> cannot be modified.
>
> 5\. Benchmarks are **deterministic**: given a detector and seed,
> results must be identical across runs.
>
> **8.2** **Benchmark** **Suites** **(Frozen)** V1 ships with exactly
> **3** **benchmark** **suites**:

||
||
||
||
||
||

||
||
||
||

> **8.3** **Benchmark** **Versioning** **Strategy**
>
> **Format:** metric-drift-v1.0.0 where: First segment = suite name
>
> Second segment = major version (breaking changes to schema or labels)
>
> Third segment = minor version (non-breaking additions)
>
> **Bump** **rules:**
>
> Major bump: change to ground truth labels, schema changes, removal of
> datasets.
>
> Minor bump: additional datasets, metadata corrections, documentation
> updates.
>
> **8.4** **Benchmark** **Folder** **Structure** **(Frozen)**
>
> ~/.miie/benchmarks/
>
> ├── metric-drift-v1.0.0/ │ ├── manifest.json
>
> │ ├── schema.json
>
> │ ├── ground_truth.json │ ├── data/
>
> │ │ ├── repo_001/
>
> │ │ │ ├── metrics.json │ │ │ └── windows.json │ │ ├── repo_002/
>
> │ │ └── ... │ └── README.md
>
> ├── correlation-breakdown-v1.0.0/ │ └── ...
>
> └── threshold-compression-v1.0.0/ └── ...
>
> **8.5** **Benchmark** **Metadata** **Schema** **(Frozen)**
>
> {
>
> "suite_id": "metric-drift-v1", "version": "1.0.0",
>
> "description": "Synthetic repositories with known distributional
> drift", "created_at": "2026-01-15",
>
> "author": "MIIE Benchmark Team", "license": "CC-BY-4.0",
> "num_datasets": 50, "detector_target": "D-01",
>
> "metrics_included": \["M-01", "M-02", "M-06", "M-07"\],
> "window_strategy": "time",
>
> "window_size_days": 30, "random_seed": 42
>
> }
>
> **8.6** **Ground** **Truth** **Schema** **(Frozen)**
>
> {
>
> "ground_truth_version": "1.0.0", "labels": \[
>
> {
>
> "dataset_id": "repo_001", "metric": "coverage", "window_pair":
> \["w03", "w04"\], "label": true,
>
> "label_type": "drift", "confidence": "high", "annotator": "expert_01",
> "annotation_date": "2026-01-10",
>
> "evidence": "Visual inspection of CDFs; KS statistic = 0.48" }
>
> \] }
>
> **8.7** **Label** **Schema** **(Frozen)**

||
||
||
||
||
||
||
||
||
||
||
||

> **8.8** **Evaluation** **Schema** **(Frozen)**
>
> {
>
> "evaluation_version": "1.0.0", "suite_id": "metric-drift-v1",
> "detector_id": "D-01", "detector_config": {"alpha": 0.05}, "seed": 42,
>
> "metrics": { "accuracy": 0.91, "precision": 0.88, "recall": 0.85,
> "f1": 0.86, "auc_roc": 0.94, "auc_pr": 0.89, "fpr": 0.12, "fnr": 0.15
>
> }, "confusion_matrix": {
>
> "tp": 85, "fp": 12, "tn": 90, "fn": 15
>
> }, "per_dataset_results": \[
>
> {
>
> "dataset_id": "repo_001", "predicted": true, "actual": true,
> "correct": true
>
> } \]
>
> }
>
> **8.9** **Output** **Schema** **(Frozen)**
>
> Benchmark output must conform to the Evaluation Schema above. All
> fields are mandatory. Per-dataset results must include every dataset
> in the suite.
>
> **SECTION** **9** **—** **Repository** **Selection** **Criteria**
>
> **9.1** **Inclusion** **Criteria** **(Frozen)**
>
> A repository is **valid** **for** **V1** **analysis** if and only if:

||
||
||
||
||
||
||
||
||

> **9.2** **Exclusion** **Criteria** **(Frozen)**
>
> A repository is **excluded** **from** **V1** **analysis** if any of
> the following apply:

||
||
||
||
||
||
||
||

> **9.3** **Fork** **Handling** **Rules** **(Frozen)**
>
> 1\. **Fork** **detection:** If repository is a GitHub/GitLab fork
> (detected via git remote or API metadata), log a warning.
>
> 2\. **Fork** **analysis:** Analysis proceeds on the fork's own commit
> history.
>
> 3\. **Confidence** **impact:** If fork has \<10 unique commits, f₃
> (missing data factor) is reduced by 0.1.
>
> 4\. **No** **special** **exclusion:** Forks are not banned unless they
> fail general inclusion criteria.
>
> **9.4** **Archival** **Rules** **(Frozen)**
>
> 1\. **Archival** **status:** MIIE does not check archival status;
> archived repositories are analyzed if accessible.
>
> 2\. **Read-only** **repositories:** No special handling; analysis
> proceeds as normal.
>
> **9.5** **Bot** **Handling** **Rules** **(Frozen)**
>
> 1\. **Bot** **detection:** Use commit author email heuristic: emails
> containing bot, ci, github-actions, dependabot, renovate are flagged
> as bots.
>
> 2\. **Bot** **commit** **handling:** Bot commits are **included** in
> metric extraction by default (to detect bot-induced drift).
>
> 3\. **Bot** **exclusion** **option:** User may specify --exclude-bots
> to remove bot commits from M-02 (commit frequency) and M-06 (churn).
> Other metrics are unaffected.
>
> 4\. **Bot** **impact** **logging:** If bot commits \> 20% of total
> commits, a warning is issued in the explanation report.
>
> **SECTION** **10** **—** **Ground** **Truth** **Freeze**
>
> **10.1** **Ground** **Truth** **Strategy** **(Frozen)**
>
> 1\. **Source:** Ground truth for V1 benchmarks is generated through
> **expert** **annotation** of synthetic repositories.
>
> 2\. **Synthetic** **data:** Repositories are generated with known
> statistical properties and injected pathologies at controlled points.
>
> 3\. **Verification:** Every label is verified by at least 2
> independent annotators.
>
> 4\. **Transparency:** Ground truth generation scripts and random seeds
> are published alongside benchmarks.
>
> **10.2** **Annotation** **Workflow** **(Frozen)**
>
> Step 1: Generate synthetic repository with known parameters
>
> Step 2: Inject pathology at specified window (drift, breakdown, or
> compression) Step 3: Run automated statistical tests to generate
> candidate labels
>
> Step 4: Expert annotator reviews candidate labels + visualizations
> (CDFs, scatter plots, histograms)
>
> Step 5: Annotator confirms, rejects, or modifies label Step 6: Second
> expert annotator independently reviews
>
> Step 7: Discrepancies resolved via conflict resolution (Section 10.3)
> Step 8: Final label written to ground_truth.json
>
> **10.3** **Reviewer** **Workflow** **(Frozen)**
>
> Each benchmark suite has a **primary** **reviewer** and **secondary**
> **reviewer**.
>
> Primary reviewer annotates first; secondary reviewer annotates blind
> (no access to primary's labels).
>
> Reviewers are software analytics researchers with graduate-level
> statistics training.
>
> Reviewers document evidence for every label in the evidence field.
>
> **10.4** **Conflict** **Resolution** **Process** **(Frozen)**

||
||
||
||
||
||
||

> **10.5** **Label** **Categories** **(Frozen)**

||
||
||
||
||
||
||

> **10.6** **Evidence** **Requirements** **(Frozen)** Every true label
> must include evidence:
>
> For drift: KS statistic or PSI value, visual CDF comparison.
>
> For breakdown: Correlation values before/after, scatter plot
> inspection.
>
> For compression: Histogram showing clustering, excess mass
> calculation.
>
> **10.7** **Quality** **Control** **Rules** **(Frozen)** 1. No label
> without documented evidence.
>
> 2\. No synthetic repository with \>1 pathology type (to avoid
> confounding).
>
> 3\. Minimum 20% clean (negative) labels per suite.
>
> 4\. Pathology injection must be verifiable by independent script.
>
> **10.8** **Inter-Rater** **Agreement** **Requirements** **(Frozen)**

||
||
||
||
||

> **10.9** **Termination** **Threshold** **(Frozen)**
>
> If Cohen's Kappa \< 0.65 after conflict resolution and third-expert
> adjudication:
>
> The benchmark suite is **rejected**.
>
> Ground truth generation must restart with revised synthetic data or
> clearer annotation guidelines.
>
> No suite may be published with κ \< 0.65.

**SECTION** **11** **—** **Benchmark** **Evaluation** **Freeze**

**11.1** **Train/Test** **Split** **(Frozen)**

V1 benchmarks do **not** use train/test splits. Benchmarks are
**evaluation-only** datasets:

> Detectors are not trained on benchmark data.
>
> All benchmark datasets are used for evaluation.
>
> "Train/test split" is not applicable to V1 detectors (they are
> rule-based, not machine-learned).

**11.2** **Cross-Project** **Validation** **(Frozen)**

> Each dataset in a benchmark suite represents a distinct synthetic
> repository.
>
> Evaluation is performed **per-dataset** and then aggregated.
>
> No cross-project training occurs.

**11.3** **Temporal** **Validation** **(Frozen)**

> Benchmark datasets include temporal windows.
>
> Detectors must process windows in chronological order.
>
> No future data may be used to predict past windows (no leakage).

**11.4** **Holdout** **Strategy** **(Frozen)** V1 does not use holdout
sets.

> All labeled datasets are evaluated.
>
> Future benchmark versions (v1.1, v1.2) may add new datasets as holdout
> for detector generalization testing.

**11.5** **Leakage** **Prevention** **Rules** **(Frozen)**

> 1\. **No** **ground** **truth** **access** **during** **detection:**
> Detector algorithms must not access ground_truth.json.
>
> 2\. **No** **cross-dataset** **information:** Detection on dataset N
> must not use metric values from dataset M.
>
> 3\. **No** **future** **window** **access:** When evaluating window
> pair (Wᵢ, Wᵢ₊₁), detector must not access Wᵢ₊₂ or later.
>
> 4\. **No** **label-dependent** **thresholds:** Detector thresholds are
> fixed by TFS Section 5; they may not be tuned post-hoc based on
> benchmark labels.

**11.6** **Random** **Seed** **Policy** **(Frozen)** **Default**
**seed:** 42

> **Seed** **usage:**
>
> D-03 dip test bootstrap: seed=42
>
> Synthetic data generation: seed=42
>
> Any stochastic detector component: seed=42
>
> **Seed** **override:** User may specify --seed N in CLI or API.
>
> **Seed** **reporting:** Seed value must be included in every benchmark
> export.
>
> **11.7** **Reproducibility** **Policy** **(Frozen)**
>
> Given identical detector version, configuration, benchmark suite
> version, and seed, three independent runs must produce
> bitwise-identical evaluation JSON.
>
> Reproducibility is verified in CI before every release.
>
> **11.8** **Evaluation** **Metrics** **(Frozen)**
>
> Every benchmark evaluation must report exactly these metrics:

||
||
||
||
||
||
||
||
||
||
||

> **Confusion** **Matrix** **Definition:**
>
> TP: Detector fired, ground truth = TRUE
>
> FP: Detector fired, ground truth = FALSE
>
> TN: Detector did not fire, ground truth = FALSE
>
> FN: Detector did not fire, ground truth = TRUE
>
> **SECTION** **12** **—** **Data** **Freeze**
>
> **12.1** **Supported** **Inputs** **(Frozen)**

||
||
||
||
||
||
||
||
||

> **12.2** **Supported** **Formats** **(Frozen)**

||
||
||
||
||
||
||
||
||

> **12.3** **Required** **Fields** **(Frozen)**
>
> ***Git*** ***Repository***
>
> .git directory present
>
> git log returns ≥ 10 commits
>
> At least one commit with timestamp
>
> ***PR/MR*** ***Export*** ***(JSON)*** {
>
> "id": "string", "created_at": "ISO-8601",
>
> "first_review_at": "ISO-8601 or null", "reviewers": \["string"\]
>
> }
>
> ***Issue*** ***Export*** ***(JSON)***
>
> {
>
> "id": "string", "created_at": "ISO-8601",
>
> "closed_at": "ISO-8601 or null", "state": "open or closed"
>
> }
>
> ***Configuration*** ***File***
>
> repo: "string"
>
> metrics: \["M-01", "M-02", ...\] window_strategy:
> "time\|commit\|release\|custom" window_size: "integer"
>
> detectors: \["D-01", "D-02", "D-03"\] output_formats: \["json", "md",
> "csv"\]
>
> **12.4** **Optional** **Fields** **(Frozen)**

||
||
||
||
||
||
||
||
||
||
||

> **12.5** **Missing** **Data** **Policy** **(Frozen)**

||
||
||
||
||
||
||
||

||
||
||
||
||

> **12.6** **Data** **Validation** **Rules** **(Frozen)**
>
> 1\. **Repository** **validation:** git rev-parse --git-dir must
> succeed.
>
> 2\. **Metric** **value** **validation:** Must be numeric or null;
> non-numeric values are coerced to null with warning.
>
> 3\. **Timestamp** **validation:** Must parse as ISO 8601; invalid
> timestamps are coerced to null.
>
> 4\. **Configuration** **validation:** Strict schema; unknown fields
> rejected; required fields enforced.
>
> 5\. **Benchmark** **validation:** Ground truth labels must match
> schema; dataset IDs must match data directories.
>
> **12.7** **Data** **Retention** **Policy** **(Frozen)**
>
> MIIE does not maintain a database or persistent store.
>
> All outputs are written to user-specified output directory.
>
> Temporary clone directories are deleted after analysis unless
> --keep-cache is set.
>
> Cache directory (~/.miie/cache/) may retain cloned repositories for 7
> days; user may clear at any time.
>
> No telemetry or usage data is transmitted.
>
> **12.8** **Export** **Formats** **(Frozen)**

||
||
||
||
||
||

> **SECTION** **13** **—** **CLI** **Freeze**
>
> **13.1** **Entry** **Point** **(Frozen)**
>
> miie \[global-options\] \<command\> \[command-options\]
>
> **13.2** **Global** **Options** **(Frozen)**

||
||
||
||
||
||
||
||

> **13.3** **miie** **analyze(Frozen)**
>
> **Purpose:** Analyze a repository for metric integrity.
>
> **Arguments:**

||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **Output:**
>
> Exit code 0: No integrity failures (IS = 1.0 for all metrics)
>
> Exit code 1: Analysis completed with integrity failures
>
> Exit code 2: System error
>
> Exit code 3: Invalid arguments
>
> Files written to --output directory
>
> **Error** **Cases:**
>
> Repository inaccessible → Exit 3, stderr: \[INVALID-REPO\] Cannot
> access repository at \<path\>. Suggestion: verify URL or permissions.
>
> No commits in range → Exit 1, stdout warning: No commits found in
> range \<since\> to \<until\>.
>
> Metric extraction fails → Continue with warning; metric unavailable.
>
> Out of memory → Exit 2, partial results saved if possible.
>
> **Example:**
>
> miie analyze --repo https://github.com/org/repo.git \\ --since
> 2025-01-01 --until 2025-12-31 \\
>
> --metrics M-01,M-02,M-07 \\
>
> --window-strategy time --window-size 90 \\ --output ./analysis-2025/
>
> **13.4** **miie** **benchmark(Frozen)**
>
> **Purpose:** Run a benchmark suite against one or more detectors.
>
> **Arguments:**

||
||
||
||
||
||
||
||

> **Output:**
>
> Exit code 0: Benchmark completed successfully
>
> Exit code 4: Benchmark failure
>
> Files written to --output directory
>
> **Error** **Cases:**
>
> Suite not found → Exit 4, stderr: \[BENCHMARK-NOT-FOUND\] Suite
> \<name\> not found in ~/.miie/benchmarks/. Suggestion: list available
> suites with 'miie benchmark --list'.
>
> Detector incompatible → Exit 4, stderr: \[INCOMPATIBLE-DETECTOR\]
> Detector \<id\> does not support benchmark schema version \<version\>.
>
> Ground truth missing → Exit 4, stderr: \[INVALID-BENCHMARK\] Ground
> truth file missing or malformed.
>
> **Example:**
>
> miie benchmark --suite metric-drift-v1 \\ --detectors D-01 \\
>
> --seed 42 \\
>
> --output ./benchmark-results/
>
> **13.5** **miie** **explain(Frozen)**
>
> **Purpose:** Generate or re-generate explanations from an existing
> analysis.
>
> **Arguments:**

||
||
||
||
||
||
||

> **Output:**
>
> Exit code 0: Explanations generated
>
> Exit code 3: Invalid input directory
>
> Files written to --input directory (overwrites) or --output if
> specified
>
> **Error** **Cases:**
>
> Input directory missing → Exit 3, stderr: \[MISSING-INPUT\] Analysis
> directory \<path\> not found. Suggestion: run 'miie analyze' first.
>
> Evidence package missing → Exit 3, stderr: \[MISSING-EVIDENCE\]
> evidence.json not found in \<path\>.
>
> Metric not found → Exit 3, stderr: \[UNKNOWN-METRIC\] Metric \<id\>
> not found in evidence package.
>
> **Example:**
>
> miie explain --input ./analysis-2025/ --metric M-01 --format md
>
> **13.6** **miie** **export(Frozen)**
>
> **Purpose:** Export results from an existing analysis in specified
> formats.
>
> **Arguments:**

||
||
||
||
||
||
||

> **Output:**
>
> Exit code 0: Export completed
>
> Exit code 3: Invalid input or format
>
> **Error** **Cases:**
>
> Input directory missing → Exit 3
>
> Format unsupported → Exit 3, stderr: \[UNSUPPORTED-FORMAT\] Format
> \<fmt\> not supported. Supported: json, md, csv.
>
> **Example:**
>
> miie export --input ./analysis-2025/ --format csv --filter
> failures_only
>
> **13.7** **Exit** **Codes** **(Frozen)**

||
||
||
||
||
||
||

||
||
||
||
||

> **13.8** **Error** **Message** **Format** **(Frozen)**
>
> \[ERROR-CODE\] Human-readable description. Suggestion: actionable fix.
>
> Error codes are uppercase with hyphens.
>
> Description is one sentence.
>
> Suggestion starts with "Suggestion:" and provides a concrete fix.
>
> Traceback included only if --verbose is enabled.
>
> **SECTION** **14** **—** **API** **Freeze**
>
> **14.1** **Base** **Configuration** **(Frozen)**
>
> **Base** **URL:** http://localhost:8000 (default, configurable via
> --port)
>
> **Version** **prefix:** /v1/
>
> **Content-Type:** application/json for requests and responses
>
> **Health** **endpoint:** GET /v1/health
>
> **14.2** **Authentication** **(Frozen)**
>
> **Local** **mode:** No authentication. API binds to 127.0.0.1 only.
>
> **Networked** **mode:** Optional API key via header Authorization:
> Bearer \<token\>.
>
> MIIE does not implement user management, sessions, or RBAC.
>
> **14.3** **Endpoints** **(Frozen)**
>
> ***POST*** ***/v1/analyze*** **Input** **Schema:**
>
> {
>
> "repo": "string (required)",
>
> "since": "string (ISO 8601, optional)", "until": "string (ISO 8601,
> optional)", "metrics": \["string"\] or \["all"\], "window_strategy":
> "time\|commit\|release\|custom", "window_size": "integer",
>
> "detectors": \["string"\] or \["all"\],
>
> "output_formats": \["json", "md", "csv"\], "exclude_bots": "boolean",
> "thresholds": {"M-01": \[1.0, 0.95\]},

"detector_weights": {"D-01": 0.4, "D-02": 0.35, "D-03": 0.25} }

**Response** **202** **Accepted:**

{

> "job_id": "uuid", "status": "queued",

"poll_url": "/v1/jobs/{job_id}" }

**Response** **400** **Bad** **Request:**

{

> "type": "https://miie.dev/errors/invalid-repo", "title": "Invalid
> Repository",
>
> "status": 400,
>
> "detail": "The provided URL is not a valid Git repository.",
> "instance": "/v1/analyze"

}

***GET*** ***/v1/jobs/{job_id}*** **Response** **200** **(completed):**

{

> "job_id": "uuid", "status": "completed", "created_at": "ISO-8601",
> "completed_at": "ISO-8601",
>
> "results_url": "/v1/jobs/{job_id}/results", "summary": {
>
> "overall_integrity_score": "float", "overall_confidence": "float",
> "failures_detected": "integer", "metrics_analyzed": "integer"

} }

**Response** **202** **(running):**

{

> "job_id": "uuid", "status": "running",
>
> "progress": "float (0.0-1.0)",

"stage":
"ingestion\|extraction\|segmentation\|detection\|scoring\|explanation\|
export"

}

**Response** **404:**

{

> "type": "https://miie.dev/errors/job-not-found", "title": "Job Not
> Found",
>
> "status": 404,
>
> "detail": "No job found with ID {job_id}.", "instance":
> "/v1/jobs/{job_id}"

}

***GET*** ***/v1/jobs/{job_id}/results***

**Response** **200:** Full JSON export identical to CLI JSON output.

***POST*** ***/v1/benchmark*** **Input** **Schema:**

{

> "suite": "string (required)", "detectors": \["string"\] or \["all"\],
>
> "config_overrides": {"D-01": {"alpha": 0.01}}, "seed": "integer",

"output_formats": \["json", "md"\] }

**Response** **202** **Accepted:** Same job structure as /v1/analyze.

***POST*** ***/v1/explain*** **Input** **Schema:**

{

> "job_id": "string (required)", "metric": "string (optional)",
> "detector": "string (optional)", "format": "md\|json"

}

**Response** **200:**

{

> "explanation": "string (Markdown)", "rule_fired": "string",
> "evidence_refs": \["string"\], "metric": "string",

"detector": "string" }

***POST*** ***/v1/export*** **Input** **Schema:**

{

> "job_id": "string (required)", "formats": \["json", "md", "csv"\],
> "filter": "string (optional)"

}

**Response** **200:**

{

> "download_urls": {
>
> "json": "/v1/jobs/{job_id}/export/json", "md":
> "/v1/jobs/{job_id}/export/md", "csv": "/v1/jobs/{job_id}/export/csv"

} }

> ***GET*** ***/v1/health*** **Response** **200:**
>
> {
>
> "status": "healthy", "version": "1.0.0", "uptime_seconds": "integer"
>
> }
>
> **14.4** **Status** **Codes** **(Frozen)**

||
||
||
||
||
||
||
||
||

> **14.5** **Error** **Response** **Schema** **(Frozen)** All errors
> follow RFC 7807 Problem Details:
>
> {
>
> "type": "string (URI identifying error type)", "title": "string (short
> human-readable summary)", "status": "integer (HTTP status code)",
> "detail": "string (human-readable explanation)", "instance": "string
> (request path)"
>
> }
>
> **14.6** **Versioning** **Rules** **(Frozen)**
>
> URL path versioning: /v1/, /v2/, etc.
>
> Breaking changes require new version prefix.
>
> Non-breaking additions (new optional fields, new endpoints) are
> backward-compatible within /v1/.
>
> Deprecation: Deprecation: true header + Sunset: \<date\> header on
> responses for deprecated endpoints.
>
> **SECTION** **15** **—** **Success** **Threshold** **Freeze**
>
> **15.1** **Numeric** **Targets** **(Frozen)**
>
> All targets are **hard** **commitments** for V1.0.0 release.

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **15.2** **Target** **Enforcement**
>
> Release is **blocked** if any detector fails its precision/recall/AUC
> target on published benchmarks.
>
> Release is **blocked** if test coverage \< 80%.
>
> Release is **blocked** if reproducibility check fails.
>
> Annotation quality target is **blocking** for benchmark suite
> publication.
>
> **SECTION** **16** **—** **Risk** **Freeze**
>
> **16.1** **Research** **Risks**

||
||
||
||
||
||
||

> **16.2** **Data** **Risks**

||
||
||
||
||
||

||
||
||
||
||

> **16.3** **Engineering** **Risks**

||
||
||
||
||
||
||

> **16.4** **Benchmark** **Risks**

||
||
||
||
||
||

||
||
||
||

> **16.5** **Publication** **Risks**

||
||
||
||
||
||

> **SECTION** **17** **—** **TRD** **Readiness** **Audit**
>
> **17.1** **Audit** **Results**

||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **17.2** **Residual** **Ambiguity** **Checklist**
>
> The following items are explicitly **not** **ambiguous** but require
> **engineering** **decisions** during TRD:

||
||
||
||
||
||
||
||
||

> These are **engineering** **decisions**, not **ambiguities**. The TFS
> has frozen the *what* and *why*; the TRD will specify the *how*.
>
> **FINAL** **QUESTION**
>
> **TRD** **Generation** **Approval** **Verdict**
>
> **Question:** *If* *three* *independent* *engineering* *teams* *built*
> *MIIE* *using* *only* *the* *IPD,* *PRD,* *and* *this* *TFS,* *would*
> *they* *produce* *functionally* *equivalent* *systems?*
>
> **Answer:** **YES**
>
> **Declaration**
>
> **TRD** **GENERATION** **APPROVED.**
>
> The Technical Freeze Sheet v1.0 eliminates all ambiguity that could
> cause divergent implementations. Three independent engineering teams
> using IPD v1.1 FINAL, PRD v1.0, and TFS v1.0 would produce systems
> that:
>
> 1\. Support exactly the same 7 metrics with identical extraction
> methods.
>
> 2\. Implement exactly the same 3 detectors with identical statistical
> tests, thresholds, and pseudocode.
>
> 3\. Compute identical Integrity Scores and Confidence Scores given
> identical inputs.
>
> 4\. Use identical CLI commands, flags, and exit codes.
>
> 5\. Expose identical REST API endpoints with identical schemas.
>
> 6\. Produce identical benchmark evaluation metrics on identical
> benchmark suites.
>
> 7\. Generate identical evidence packages and explanation reports.

The remaining work for TRD is to specify:

> Programming language and framework choices
>
> Module decomposition and class design
>
> Dependency graph and version pinning
>
> Testing strategy and CI/CD pipeline
>
> Packaging and distribution mechanics
>
> Performance optimization techniques
>
> Deployment architecture for API mode

These are engineering implementation details, not product ambiguities.

**APPENDIX** **A** **—** **JSON** **Schema** **Reference**

**A.1** **Evidence** **Package** **Schema** **(v1.0.0)**

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title": "MIIE
> Evidence Package",
>
> "type": "object",

"required": \["provenance", "windows", "metrics", "detector_outputs",
"scores"\],

> "properties": { "provenance": {
>
> "type": "object",
>
> "required": \["miie_version", "config_hash", "timestamp"\],
> "properties": {
>
> "miie_version": {"type": "string"}, "config_hash": {"type": "string"},
>
> "timestamp": {"type": "string", "format": "date-time"} }
>
> }, "windows": {
>
> "type": "array", "items": {
>
> "type": "object",
>
> "required": \["id", "start", "end", "commits"\], "properties": {
>
> "id": {"type": "string"},
>
> "start": {"type": "string", "format": "date-time"}, "end": {"type":
> "string", "format": "date-time"}, "commits": {"type": "integer"}
>
> } }
>
> }, "metrics": {
>
> "type": "object", "additionalProperties": {
>
> "type": "object",
>
> "description": "Map of window_id to array of metric values" }
>
> },
>
> "detector_outputs": { "type": "object", "properties": {
>
> "D-01": {"type": "object"}, "D-02": {"type": "object"}, "D-03":
> {"type": "object"}
>
> } },
>
> "scores": { "type": "object",
>
> "required": \["integrity", "confidence"\], "properties": {
>
> "integrity": { "type": "object",
>
> "required": \["overall", "per_metric"\], "properties": {
>
> "overall": {"type": "number", "minimum": 0, "maximum": 1},
> "per_metric": {
>
> "type": "object",

"additionalProperties": {"type": "number", "minimum": 0, "maximum": 1}

> } }
>
> }, "confidence": {
>
> "type": "object",
>
> "required": \["overall", "factors"\], "properties": {
>
> "overall": {"type": "number", "minimum": 0, "maximum": 1}, "factors":
> {
>
> "type": "object", "properties": {
>
> "sample_size": {"type": "number"}, "variance": {"type": "number"},
> "missing_data": {"type": "number"}, "window_balance": {"type":
> "number"}, "detector_success": {"type": "number"}
>
> } }
>
> } }
>
> } }

} }

**A.2** **Configuration** **Schema** **(v1.0.0)**

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title": "MIIE
> Configuration",
>
> "type": "object", "required": \["repo"\], "properties": {
>
> "repo": {"type": "string"},
>
> "since": {"type": "string", "format": "date-time"}, "until": {"type":
> "string", "format": "date-time"}, "metrics": {
>
> "type": "array",

"items": {"enum": \["M-01", "M-02", "M-03", "M-04", "M-05", "M-06",
"M-07", "all"\]}

> },
>
> "window_strategy": {"enum": \["time", "commit", "release",
> "custom"\]},
>
> "window_size": {"type": "integer", "minimum": 1}, "detectors": {
>
> "type": "array",
>
> "items": {"enum": \["D-01", "D-02", "D-03", "all"\]} },
>
> "output_formats": { "type": "array",
>
> "items": {"enum": \["json", "md", "csv"\]} },
>
> "exclude_bots": {"type": "boolean"}, "thresholds": {
>
> "type": "object",
>
> "additionalProperties": {"type": "array", "items": {"type": "number"}}
> },
>
> "detector_weights": { "type": "object", "properties": {
>
> "D-01": {"type": "number"}, "D-02": {"type": "number"}, "D-03":
> {"type": "number"}
>
> } },
>
> "seed": {"type": "integer"} }
>
> }
>
> **APPENDIX** **B** **—** **Glossary**

||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||

> **APPENDIX** **C** **—** **Document** **Control**

||
||
||
||

> **END** **OF** **TFS** **v1.0**
