# Day 16 Authority Specification
## D03 Threshold Compression Detector

## Sources Consulted
- `src/miie/processing/detection/threshold_compression_detector.py` (implementation)
- `src/miie/processing/detection/base.py` (BaseDetector contract)
- `src/miie/schemas/models.py` (MetricDataFrame, DetectorResult schemas)
- `src/miie/cli.py` (detector registration)

## Technical Foundation Specification (TFS) v1.0
### Section 5.3: Threshold Compression Detector

#### 5.3.1 Detector Purpose
- Detect artificial clustering of values around thresholds using Excess Mass test and Hartigans' Dip test (supporting).
- Implements D-03 detector per TFS Section 5.3.

#### 5.3.2 Supported Metrics
- M-01 through M-07 (7 metrics)
- Implemented as: `supported_metrics=[f"M-{i:02d}" for i in range(1, 8)]`

#### 5.3.3 Input Format
- Accepts `MetricDataFrame` with:
  - `repo_id`: string
  - `run_id`: string
  - `timestamp`: ISO 8601 UTC string (YYYY-MM-DDTHH:MM:SSZ)
  - `metrics`: dictionary mapping metric ID to dictionary of window ID to list of float values
- Validation: 
  - At least one supported metric must be present (`validate_input` returns True if ≥1 supported metric)
  - Timestamp must be in ISO 8601 UTC format (validated in `MetricDataFrame.__post_init__`)

#### 5.3.4 Detection Algorithms
##### Excess Mass Test (Primary)
- For each metric, threshold, and window:
  - Compute excess mass test statistic (z-score)
  - Formula: 
    - Let B(T, ε) = {x : |x - T| ≤ ε} (the "band" around threshold)
    - Expected proportion under uniform assumption: p₀ = 2ε / (max(X) - min(X))
    - Observed proportion: p = |B(T, ε)| / n
    - Test statistic: z = (p - p₀) / √(p₀(1 - p₀) / n)
  - Implemented in `_excess_mass_test` method
  - Threshold: z > 1.645 (one-tailed, α = 0.05)

##### Hartigan's Dip Test (Supporting)
- For each metric, threshold, and window:
  - Compute Hartigans' Dip test statistic and p-value via bootstrap
  - Implemented in `_dip_test` method
  - Uses bootstrap samples (n_boot = 1000, seed = 42)
  - Approximated via KS test against uniform distribution (as exact dip test is complex)
  - Threshold: p < 0.05

##### Threshold Selection
- Auto-threshold detection from TFS Section 5.3:
  - Candidate thresholds: [1, 5, 10, 20, 25, 50, 75, 80, 90, 95, 100, 1000]
  - Percentile-based thresholds: [10, 25, 50, 75, 90] of metric values
  - Only thresholds that are "round numbers" (end in 0 or 5) from percentiles are used
  - Thresholds must be within [min(X), max(X)] of the metric values
- Implemented in `_get_thresholds_for_metric` method

##### Epsilon Calculation
- Per TFS Section 5.3: ε = max(0.02 × |T|, 0.01 × (max(X) - min(X)))
- Implemented in `_compute_epsilon` method

#### 5.3.5 Detection Logic
- For each metric:
  - Determine thresholds to test (auto-thresholds)
  - For each threshold and window:
    - Skip if insufficient sample size (n < 20)
    - Compute excess mass z-score
    - Compute dip test statistic and p-value
    - Determine if compression is detected:
      - excess_mass_flag = (z_score > 1.645)
      - multimodal_flag = (dip_p < 0.05)
      - p_hat = proportion of values in band [T-ε, T+ε]
      - Compression detected if: excess_mass_flag AND (multimodal_flag OR p_hat > 0.5)
- Implemented in `execute` method

#### 5.3.6 Output Format
- Returns `DetectorResult` with `detector_outputs` containing key "D-03"
- Value is a dictionary with:
  - `compression_detected`: boolean (True if any compression event detected)
  - `compression_index`: float (average compression_index across all events, where compression_index = p_hat)
  - `metrics_analyzed`: list of metric IDs that were processed
  - `compression_events`: list of dictionaries, each containing:
    - "metric": metric ID
    - "threshold": threshold value
    - "window": window ID
    - "compression_detected": True
    - "compression_index": float (p_hat for this event)
    - "excess_mass_z_score": float
    - "dip_test_statistic": float
    - "dip_test_p_value": float
    - "epsilon": float
    - "sample_size": int (n)
    - "hypothesized_cause": string (rule-based, e.g., "THRESHOLD_GAMING")
  - `thresholds_used`: dictionary mapping metric ID to list of thresholds tested
  - `excess_mass_z_scores`: dictionary mapping (metric, threshold, window) to z-score
  - `dip_test_statistics`: dictionary mapping (metric, threshold, window) to dip statistic
  - `dip_test_p_values`: dictionary mapping (metric, threshold, window) to dip p-value
  - `windows_analyzed`: list of window IDs processed

#### 5.3.7 Error Handling
- If no metrics available for compression analysis:
  - Returns structured output with:
    - `compression_detected`: False
    - `compression_index`: 0.0
    - `metrics_analyzed`: empty list
    - `compression_events`: empty list
    - `thresholds_used`: empty dict
    - `excess_mass_z_scores`: empty dict
    - `dip_test_statistics`: empty dict
    - `dip_test_p_values`: empty dict
    - `windows_analyzed`: empty list
- If insufficient data (n < 20) for a metric-threshold-window combination:
  - Skips that combination (continues to next)

#### 5.3.8 Determinism
- Identical inputs, seed, and configuration → identical outputs
- Achieved by:
  - Fixed random seed for dip test bootstrap (seed = 42)
  - No external dependencies or non-deterministic sources
  - Pure computation with numpy and standard library

## Technical Requirements Document (TRD) v1.0
### Section 4.3: Detection Components

#### 4.3.1 Detector Interface
- Implement `BaseDetector` interface:
  - `detector_id`, `detector_name`, `supported_metrics` properties
  - `validate_input(MetricDataFrame) -> bool` method
  - `execute(MetricDataFrame) -> DetectorResult` method

#### 4.3.2 Input Validation
- Validate `MetricDataFrame` format (inherited from `MetricDataFrame` validation)
- Check for presence of at least one supported metric

#### 4.3.3 Deterministic Computation
- Same inputs → same outputs (see TFS 5.3.8)

#### 4.3.4 Error Handling
- Graceful degradation on invalid input (returns structured `DetectorResult` with safe defaults)

#### 4.3.5 Performance Monitoring
- Component-level timing metrics (handled by pipeline)

#### 4.3.6 Resource Constraints
- Bounded memory and CPU usage (O(w × t × m) where w=windows, t=thresholds, m=metrics)

#### 4.3.7 Configuration Management
- Thresholds are standards-based (hardcoded to TFS Section 5.3 values)

#### 4.3.8 Audit Trail
- Deterministic outputs enable reproducibility

#### 4.3.9 Security Considerations
- No injection vulnerabilities; input treated as numerical data only

## Architectural Component Specification (ACS) v1.0
### Section 3.2: Processing Components

#### 3.2.1 Component Independence
- No external dependencies beyond declared (standard library and numpy)

#### 3.2.2 Standardized Interfaces
- `MetricDataFrame` in, `DetectorResult` out (via method signatures)

#### 3.2.3 Lifecycle Management
- Stateless between invocations (no persistent state)

#### 3.2.4 Thread Safety
- Safe for concurrent invocation (no shared mutable state)

#### 3.2.5 Exception Safety
- No resource leaks on exception (no external resources allocated)

#### 3.2.6 Performance Characteristics
- Documented time/space complexity: O(w × t × m)

#### 3.2.7 Observability
- Exposes standard metrics via pipeline (execution time, success/failure)

#### 3.2.8 Testability
- Supports unit testing and mocking (deterministic output enables testing)

#### 3.2.9 Documentation
- Self-documenting code with clear API (docstrings, comments)

#### 3.2.10 Standards Compliance
- Adheres to TFS and TRD where specified

## BSD-Engineering v1.0
### Software Engineering Practices

- **Numerical Stability**: Uses numpy for statistical operations (Excess Mass test, Dip test approximation)
- **Algorithm Transparency**: Clear documentation of mathematical basis in code comments
- **Error Handling**: Graceful degradation and informative failure modes (input validation returns boolean, computation handles edge cases)
- **Code Maintainability**: Modular, readable, and maintainable structure (clear method separation, descriptive naming)
- **Performance Efficiency**: Appropriate algorithms for problem scale (O(w × t × m) is appropriate for detector)
- **Security Best Practices**: No injection, safe handling of external data (input validated and treated as numerical data only)
- **Reproducibility**: Deterministic with controlled randomness (seed-controlled where applicable; deterministic core algorithms)
- **Testing Sufficiency**: Adequate unit and integration testing (to be completed)
- **Documentation Completeness**: Architectural and usage documentation (this spec + implementation comments)
- **Dependency Management**: Clear, minimal, and version-appropriate dependencies (only numpy beyond standard library)

## AFD (Application Framework Definition)
- Not consulted as no specific AFD documents were provided in the initial state.
- Implementation follows the standard MIIE v1.0 plugin architecture via `DetectorRegistry`.

## Summary of Requirements
The D03 Threshold Compression Detector must:
1. Implement the `BaseDetector` interface with detector ID "D-03"
2. Detect threshold compression using Excess Mass test (primary) and Hartigans' Dip test (supporting)
3. Use auto-threshold detection as specified in TFS Section 5.3
4. Require at least one supported metric for validation
5. Process windowed metric data with minimum 20 observations per window for analysis
6. Return a `DetectorResult` with the specified output structure
7. Be deterministic for identical inputs, seed, and configuration
8. Handle edge cases gracefully (insufficient data, no metrics, etc.)
9. Be registered with the `DetectorRegistry` in the analysis pipeline
10. Comply with all BSD-Engineering v1.0 software engineering practices

## References
- src/miie/processing/detection/threshold_compression_detector.py
- src/miie/processing/detection/base.py
- src/miie/schemas/models.py
- src/miie/cli.py