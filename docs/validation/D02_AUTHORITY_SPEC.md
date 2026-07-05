# D02 CORRELATION BREAKDOWN DETECTOR AUTHORITY SPECIFICATION
## Extracted from TFS v1.0 Section 5.2

### Formal Definition
Given two metrics A and B with paired observations in window W: {(a₁, b₁), ..., (aₙ, bₙ)}, the detector tests whether the correlation between A and B is stable across windows.

**H₀:** ρ(Wᵢ) = ρ(Wᵢ₊₁) (correlation is stable)
**H₁:** \|ρ(Wᵢ) - ρ(Wᵢ₊₁)\| \> δ (correlation has changed significantly)

### Mathematical Basis
#### Pearson Correlation:
r = Σᵢ(aᵢ - ā)(bᵢ - b) / √[Σᵢ(aᵢ - ā)² Σᵢ(bᵢ - b)²]

#### Spearman Rank Correlation:
ρₛ = 1 - 6Σdᵢ² / n(n² - 1)
where dᵢ = rank(aᵢ) - rank(bᵢ)

#### Fisher z-transformation for confidence intervals:
z = 0.5 × ln((1 + r) / (1 - r))
SE = 1 / √(n - 3)
CI₉₅ = [tanh(z - 1.96×SE), tanh(z + 1.96×SE)]

### Detection Logic
FOR each metric pair (Mᵢ, Mⱼ) where i < j:
  FOR each window Wₖ:
    IF paired_observations < 10: 
      SKIP with warning "Insufficient sample size"
      CONTINUE
    
    r_pearson[Wₖ] = pearsonr(Wₖ[Mᵢ], Wₖ[Mⱼ])
    r_spearman[Wₖ] = spearmanr(Wₖ[Mᵢ], Wₖ[Mⱼ])
    
    # Trajectory analysis requires ≥3 windows
    IF number_of_windows < 3:
      breakdown = FALSE  # Cannot assess trajectory
      CONTINUE
    
    # Breakdown Type 1: Sudden drop
    FOR k = 1 to K-1:
      delta = |r_pearson[Wₖ₊₁] - r_pearson[Wₖ]|
      IF delta > 0.3:
        FLAG breakdown for (Mᵢ, Mⱼ) between Wₖ and Wₖ₊₁
        type = "sudden_drop"
    
    # Breakdown Type 2: Sign reversal
    FOR k = 1 to K-1:
      IF sign(r_pearson[Wₖ]) ≠ sign(r_pearson[Wₖ₊₁]) AND
         |r_pearson[Wₖ]| > 0.2 AND |r_pearson[Wₖ₊₁]| > 0.2:
        FLAG breakdown for (Mᵢ, Mⱼ) between Wₖ and Wₖ₊₁
        type = "sign_reversal"
    
    # Breakdown Type 3: Gradual erosion
    IF K ≥ 4:
      slope = linear_regression_slope(r_pearson over window indices)
      IF slope < -0.1 per window AND 
         r_pearson[W₁] > 0.3 AND 
         r_pearson[Wₖ] < 0.1:
        FLAG breakdown for (Mᵢ, Mⱼ)
        type = "gradual_erosion"
    
    # Breakdown Type 4: Confidence interval exclusion
    FOR k = 1 to K-1:
      IF NOT (CI₉₅(Wₖ₊₁) overlaps CI₉₅(Wₖ)):
        FLAG breakdown for (Mᵢ, Mⱼ) between Wₖ and Wₖ₊₁
        type = "confidence_exclusion"

### Threshold Logic
- Sudden drop threshold: δ = 0.3 (minimum correlation change to flag)
- Sign reversal minimum correlation: |r| > 0.2 for both windows
- Gradual erosion slope threshold: < -0.1 per window
- Gradual erosion window requirements: K ≥ 4, r_pearson[W₁] > 0.3, r_pearson[Wₖ] < 0.1

### Input Requirements
- Paired observations of two metrics (Mᵢ, Mⱼ) across temporal windows
- Minimum 10 paired observations per window for correlation calculation
- Minimum 3 windows for trajectory analysis (sudden drop, sign reversal, confidence exclusion)
- Minimum 4 windows for gradual erosion detection
- Metrics must be numeric (M-01 through M-07)

### Output Specification
Per breakdown event, output shall include:
- detector: "D-02"
- metric_pair: [Mᵢ, Mⱼ] (array of two metric IDs)
- breakdown_detected: boolean
- breakdown_type: enum["sudden_drop", "sign_reversal", "gradual_erosion", "confidence_exclusion", null]
- pearson_trajectory: array of Pearson r values per window (for visualization)
- spearman_trajectory: array of Spearman ρ values per window (for visualization)
- window_pairs_flagged: array of [window_start, window_end] pairs where breakdown occurred
- confidence_intervals: array of [lower, upper] CI₉₅ bounds per window (for Pearson r)

### Evidence Requirements
Per TFS Section 10.6: Every true label must include evidence:
- For breakdown: Correlation values before/after, scatter plot inspection.

### Validation Rules
1. Input validation: Verify metric pair exists in MetricDataFrame
2. Sample size validation: Skip windows with <10 paired observations
3. Window count validation: 
   - <3 windows: only sudden drop and sign reversal possible (no trajectory)
   - <4 windows: gradual erosion not possible
4. Correlation bounds: All r values must be in [-1, 1]
5. Output validation: breakdown_type must be null if breakdown_detected=false
6. Determinism: Same input + seed must produce identical output

### Allowed Mathematics
- Pearson correlation calculation
- Spearman rank correlation calculation
- Linear regression (for slope in gradual erosion)
- Fisher z-transformation (for confidence intervals)
- Hyperbolic tangent (tanh) for CI conversion
- Absolute value, sign function, basic arithmetic

### Forbidden Mathematics
- Machine learning models
- Cross-window data leakage (using future windows to predict past)
- Non-parametric correlation methods beyond Pearson/Spearman
- Ad hoc thresholds not specified in TFS
- Modification of threshold values (0.3, 0.2, -0.1) without TFS amendment

### Expected Performance (from TFS)
- Precision Range: 0.75 – 0.85 (on correlation-breakdown-v1 benchmark)
- Recall Range: 0.70 – 0.80 (on correlation-breakdown-v1 benchmark)

### False Positive Sources
1. Small sample sizes producing unstable correlation estimates.
2. Confounding variables affecting one metric but not the other.
3. Non-linear relationships misdetected by Pearson threshold.

### False Negative Sources
1. Breakdowns below the 0.3 magnitude threshold.
2. Breakdowns in Spearman but not Pearson (or vice versa) if only one is monitored.
3. Missing data creating artificial correlation stability.

### Publication References
- Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum. (Effect size thresholds)
- Fisher, R.A. (1915). "Frequency Distribution of the Values of the Correlation Coefficient in Samples from an Indefinitely Large Population." Biometrika, 10(4), 507-521.

### Implementation Notes
- Must compute both Pearson and Spearman correlations for each window pair
- Must flag breakdown if ANY of the four detection logic paths triggers
- Breakdown priority: If multiple types detected in same window pair, output breakdown_type shall be:
  1. sign_reversal (highest priority)
  2. sudden_drop
  3. gradual_erosion
  4. confidence_exclusion (lowest priority)
  (This priority ensures deterministic output when multiple conditions met)
- Window pairs are consecutive (Wₖ, Wₖ₊₁)
- All calculations must use the same random seed (42) for any stochastic components (though D-02 has none)
- Output trajectories must be in chronological window order