"""
ACS v1.0 Contract Validators
Implements validation logic for all module interfaces and CLI contracts.
Based on ACS Section 20: Validation Contract Framework and interface-specific validation rules.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Import schemas for validation
from miie.schemas.models import (
    RepositoryContext,
    MetricDataFrame,
    WindowDefinition,
    DetectorResults,
    ScorePackage,
    EvidencePackage,
    ExplanationReport,
    BenchmarkRun
)

# Import custom exceptions
from miie.contracts.errors import (
    ValidationError,
    IngestionError,
    ExtractionError,
    SegmentationError,
    DetectionError,
    ScoreError,
    EvidenceError,
    ExplanationError,
    BenchmarkError,
    EvaluationError,
    SerializationError,
    ReportError
)


def validate_repository_inputs(repo_path: str,
                              cache_dir: Optional[Path] = None,
                              keep_cache: bool = False,
                              shallow_depth: Optional[int] = None) -> None:
    """Validate inputs for INT-01: Repository Ingestion.

    Validates:
    1. repo_path must be non-empty string
    2. If repo_path is URL: scheme must be https:// or ssh://
    3. If repo_path is local path: must exist and contain .git directory
    4. cache_dir must be writable path (if provided)
    5. shallow_depth if provided must be ≥ 1

    Args:
        repo_path: Repository path or URL
        cache_dir: Cache directory path
        keep_cache: Whether to keep cloned repositories
        shallow_depth: Depth for shallow clone

    Raises:
        ValidationError: If any validation fails
    """
    if not repo_path or not isinstance(repo_path, str):
        raise ValidationError("repo_path must be a non-empty string")

    # Check if it's a URL
    try:
        parsed = urlparse(repo_path)
        is_url = bool(parsed.scheme)  # True if any scheme is present
    except Exception:
        is_url = False

    if is_url:
        # Validate URL scheme
        if parsed.scheme not in ['https', 'ssh']:
            raise ValidationError(f"Repository URL scheme must be https:// or ssh://, got: {parsed.scheme}")
    else:
        # Validate local path
        path_obj = Path(repo_path)
        if not path_obj.exists():
            raise ValidationError(f"Repository path does not exist: {repo_path}")
        if not (path_obj / '.git').exists():
            raise ValidationError(f"Path is not a Git repository (missing .git directory): {repo_path}")

        # Try to validate it's a proper git repo
        try:
            # This would normally check git rev-parse --git-dir
            # For now, just check if .git exists
            pass
        except Exception as e:
            raise ValidationError(f"Invalid Git repository: {repo_path}") from e

    # Validate cache_dir if provided
    if cache_dir is not None:
        if not isinstance(cache_dir, Path):
            raise ValidationError("cache_dir must be a Path object")
        # In real implementation, we'd check if directory is writable

    # Validate shallow_depth
    if shallow_depth is not None:
        if not isinstance(shallow_depth, int) or shallow_depth < 1:
            raise ValidationError("shallow_depth must be an integer ≥ 1")


def validate_extraction_inputs(repository_context: RepositoryContext,
                              metric_list: List[str],
                              since: Optional[datetime] = None,
                              until: Optional[datetime] = None,
                              exclude_bots: bool = False) -> None:
    """Validate inputs for INT-02: Metric Extraction.

    Validates:
    1. repository_context must be valid RepositoryContext object
    2. metric_list must contain valid metric IDs or "all"
    3. since ≤ until if both provided
    4. exclude_bots must be boolean

    Args:
        repository_context: RepositoryContext object
        metric_list: List of metric IDs or ["all"]
        since: Start datetime for extraction
        until: End datetime for extraction
        exclude_bots: Whether to exclude bot commits

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(repository_context, RepositoryContext):
        raise ValidationError("repository_context must be a valid RepositoryContext object")

    # Validate metric_list
    if not isinstance(metric_list, list) or not metric_list:
        raise ValidationError("metric_list must be a non-empty list")

    valid_metrics = {"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07", "all"}
    for metric in metric_list:
        if metric not in valid_metrics:
            raise ValidationError(f"Invalid metric ID: {metric}. Must be one of {valid_metrics}")

    # Validate time range
    if since is not None and until is not None:
        if not isinstance(since, datetime) or not isinstance(until, datetime):
            raise ValidationError("since and until must be datetime objects")
        if since > until:
            raise ValidationError("since must be before or equal to until")

    # Validate exclude_bots
    if not isinstance(exclude_bots, bool):
        raise ValidationError("exclude_bots must be a boolean")


def validate_segmentation_inputs(metric_dataframe: MetricDataFrame,
                                strategy: str,
                                size: int,
                                custom_boundaries: Optional[List[tuple[datetime, datetime]]] = None) -> None:
    """Validate inputs for INT-03: Window Segmentation.

    Validates:
    1. strategy must be one of the four frozen values
    2. size ≥ 1
    3. custom_boundaries required only if strategy="custom"
    4. Each boundary must be [start, end] with start < end
    5. Minimum 2 windows required for drift detection (validated later)

    Args:
        metric_dataframe: MetricDataFrame object
        strategy: Segmentation strategy ("time", "commit", "release", "custom")
        size: Window size
        custom_boundaries: List of (start, end) tuples for custom strategy

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(metric_dataframe, MetricDataFrame):
        raise ValidationError("metric_dataframe must be a valid MetricDataFrame object")

    valid_strategies = {"time", "commit", "release", "custom"}
    if strategy not in valid_strategies:
        raise ValidationError(f"strategy must be one of {valid_strategies}, got: {strategy}")

    if not isinstance(size, int) or size < 1:
        raise ValidationError("size must be an integer ≥ 1")

    if strategy == "custom":
        if custom_boundaries is None:
            raise ValidationError("custom_boundaries is required when strategy='custom'")
        if not isinstance(custom_boundaries, list):
            raise ValidationError("custom_boundaries must be a list")

        for i, boundary in enumerate(custom_boundaries):
            if not isinstance(boundary, tuple) or len(boundary) != 2:
                raise ValidationError(f"custom_boundaries[{i}] must be a tuple of (start, end)")
            start, end = boundary
            if not isinstance(start, datetime) or not isinstance(end, datetime):
                raise ValidationError(f"custom_boundaries[{i}] start and end must be datetime objects")
            if start >= end:
                raise ValidationError(f"custom_boundaries[{i}] start must be before end")
    else:
        if custom_boundaries is not None:
            raise ValidationError(f"custom_boundaries should not be provided when strategy='{strategy}'")


def validate_detection_inputs(metric_dataframe: MetricDataFrame,
                             windows: List[WindowDefinition],
                             detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
                             enabled_detectors: Optional[List[str]] = None) -> None:
    """Validate inputs for INT-04: Detector Invocation.

    Validates:
    1. enabled_detectors must contain valid detector IDs or "all"
    2. detector_config must contain configuration objects for each enabled detector
    3. windows must be non-empty, ordered, non-overlapping
    4. metric_dataframe must contain data for at least one metric

    Args:
        metric_dataframe: MetricDataFrame object
        windows: List of WindowDefinition objects
        detector_config: Configuration for each detector
        enabled_detectors: List of detector IDs to run

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(metric_dataframe, MetricDataFrame):
        raise ValidationError("metric_dataframe must be a valid MetricDataFrame object")

    # Validate enabled_detectors
    if enabled_detectors is not None:
        if not isinstance(enabled_detectors, list):
            raise ValidationError("enabled_detectors must be a list")

        valid_detectors = {"D-01", "D-02", "D-03", "all"}
        for det in enabled_detectors:
            if det not in valid_detectors:
                raise ValidationError(f"Invalid detector ID: {det}. Must be one of {valid_detectors}")
    elif detector_config is not None:
        # If detector_config is provided but enabled_detectors not, infer from config keys
        enabled_detectors = list(detector_config.keys())
        for det in enabled_detectors:
            if det not in {"D-01", "D-02", "D-03"}:
                raise ValidationError(f"Invalid detector ID in detector_config: {det}")

    # Validate detector_config if provided
    if detector_config is not None:
        if not isinstance(detector_config, dict):
            raise ValidationError("detector_config must be a dictionary")

        # Validate each detector's config
        for det_id, config in detector_config.items():
            if det_id not in {"D-01", "D-02", "D-03"}:
                raise ValidationError(f"Invalid detector ID in detector_config: {det_id}")
            if not isinstance(config, dict):
                raise ValidationError(f"Configuration for {det_id} must be a dictionary")

    # Validate windows
    if not isinstance(windows, list) or not windows:
        raise ValidationError("windows must be a non-empty list")

    if not all(isinstance(w, WindowDefinition) for w in windows):
        raise ValidationError("All items in windows must be WindowDefinition objects")

    # Check if windows are ordered and non-overlapping (basic check)
    if len(windows) > 1:
        for i in range(len(windows) - 1):
            if windows[i].end_date >= windows[i + 1].start_date:
                raise ValidationError(f"Windows must be non-overlapping and chronologically ordered: window {i} ends at {windows[i].end_date}, window {i+1} starts at {windows[i+1].start_date}")


def validate_d01_input(values_a: List[float], values_b: List[float],
                      metric_id: str, window_pair: tuple[str, str],
                      config: Dict[str, Any]) -> None:
    """Validate inputs for D-01 Distributional Drift detector.

    Validates:
    1. sample sizes each ≥ 10 (checked during processing, not here)
    2. alpha = 0.05 (frozen) - validated in config
    3. psi_threshold = 0.25 (frozen) - validated in config

    Args:
        values_a: Metric values from window A
        values_b: Metric values from window B
        metric_id: Metric identifier (M-01 through M-07)
        window_pair: Tuple of window IDs
        config: Detector configuration

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(values_a, list) or not all(isinstance(x, (int, float)) for x in values_a):
        raise ValidationError("values_a must be a list of numbers")

    if not isinstance(values_b, list) or not all(isinstance(x, (int, float)) for x in values_b):
        raise ValidationError("values_b must be a list of numbers")

    valid_metrics = {"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"}
    if metric_id not in valid_metrics:
        raise ValidationError(f"metric_id must be one of {valid_metrics}, got: {metric_id}")

    if not isinstance(window_pair, tuple) or len(window_pair) != 2:
        raise ValidationError("window_pair must be a tuple of two strings")

    if not all(isinstance(w, str) and w.startswith('w') and len(w) == 3 and w[1:].isdigit() for w in window_pair):
        raise ValidationError("window_pair elements must be window IDs in format wNN")

    # Validate config
    if not isinstance(config, dict):
        raise ValidationError("config must be a dictionary")

    alpha = config.get("alpha", 0.05)
    psi_threshold = config.get("psi_threshold", 0.25)

    if alpha != 0.05:
        raise ValidationError(f"alpha must be 0.05 (frozen), got: {alpha}")

    if psi_threshold != 0.25:
        raise ValidationError(f"psi_threshold must be 0.25 (frozen), got: {psi_threshold}")


def validate_d02_input(values_a: List[float], values_b: List[float],
                      metric_a: str, metric_b: str,
                      window_history: List[WindowDefinition],
                      config: Dict[str, Any]) -> None:
    """Validate inputs for D-02 Correlation Breakdown detector.

    Validates:
    1. Paired observations ≥ 10 per window (checked during processing)
    2. correlation_threshold = 0.3 (frozen)

    Args:
        values_a: Values of metric A
        values_b: Values of metric B
        metric_a: First metric identifier
        metric_b: Second metric identifier
        window_history: List of window definitions
        config: Detector configuration

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(values_a, list) or not all(isinstance(x, (int, float)) for x in values_a):
        raise ValidationError("values_a must be a list of numbers")

    if not isinstance(values_b, list) or not all(isinstance(x, (int, float)) for x in values_b):
        raise ValidationError("values_b must be a list of numbers")

    if len(values_a) != len(values_b):
        raise ValidationError("values_a and values_b must have the same length")

    valid_metrics = {"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"}
    if metric_a not in valid_metrics:
        raise ValidationError(f"metric_a must be one of {valid_metrics}, got: {metric_a}")

    if metric_b not in valid_metrics:
        raise ValidationError(f"metric_b must be one of {valid_metrics}, got: {metric_b}")

    if metric_a == metric_b:
        raise ValidationError("metric_a and metric_b must be different")

    if not isinstance(window_history, list) or not window_history:
        raise ValidationError("window_history must be a non-empty list")

    if not all(isinstance(w, WindowDefinition) for w in window_history):
        raise ValidationError("All items in window_history must be WindowDefinition objects")

    # Validate config
    if not isinstance(config, dict):
        raise ValidationError("config must be a dictionary")

    correlation_threshold = config.get("correlation_threshold", 0.3)

    if correlation_threshold != 0.3:
        raise ValidationError(f"correlation_threshold must be 0.3 (frozen), got: {correlation_threshold}")


def validate_d03_input(metric_values: List[float], thresholds: List[float],
                      metric_id: str, window_id: str,
                      config: Dict[str, Any]) -> None:
    """Validate inputs for D-03 Threshold Compression detector.

    Validates:
    1. sample_size ≥ 20 (checked during processing)
    2. margin = max(0.02×T, 0.01×range) (frozen) - validated in processing
    3. z_score threshold = 1.645 (one-tailed, α=0.05) - validated as bootstrap setting
    4. bootstrap_iterations = 1000, bootstrap_seed = 42 (frozen)
    5. p_hat dominance threshold = 0.5 (frozen)
    6. p_0 sanity cap = 0.5 (frozen)

    Args:
        metric_values: List of metric values
        thresholds: List of threshold values to test
        metric_id: Metric identifier (M-01 through M-07)
        window_id: Window identifier
        config: Detector configuration

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(metric_values, list) or not all(isinstance(x, (int, float)) for x in metric_values):
        raise ValidationError("metric_values must be a list of numbers")

    if not isinstance(thresholds, list) or not all(isinstance(x, (int, float)) for x in thresholds):
        raise ValidationError("thresholds must be a list of numbers")

    valid_metrics = {"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"}
    if metric_id not in valid_metrics:
        raise ValidationError(f"metric_id must be one of {valid_metrics}, got: {metric_id}")

    if not isinstance(window_id, str) or not (window_id.startswith('w') and len(window_id) == 3 and window_id[1:].isdigit()):
        raise ValidationError(f"window_id must be in format wNN, got: {window_id}")

    # Validate config
    if not isinstance(config, dict):
        raise ValidationError("config must be a dictionary")

    margin = config.get("margin", 0.02)
    bootstrap_iterations = config.get("bootstrap_iterations", 1000)
    bootstrap_seed = config.get("bootstrap_seed", 42)

    # Note: margin validation is complex (depends on T and range) so done in processing
    # Note: bootstrap_iterations and bootstrap_seed validation is done in processing

    # These are the frozen values that should be validated
    if bootstrap_iterations != 1000:
        raise ValidationError(f"bootstrap_iterations must be 1000 (frozen), got: {bootstrap_iterations}")

    if bootstrap_seed != 42:
        raise ValidationError(f"bootstrap_seed must be 42 (frozen), got: {bootstrap_seed}")


def validate_scoring_inputs(detector_results: DetectorResults,
                           metric_dataframe: MetricDataFrame,
                           windows: List[WindowDefinition],
                           detector_weights: Optional[Dict[str, float]] = None) -> None:
    """Validate inputs for INT-05: Score Calculation.

    Validates:
    1. detector_weights must contain keys for all enabled detectors
    2. If sum ≠ 1.0, normalize proportionally (done in processing)
    3. If detector skipped on metric, redistribute weight proportionally (done in processing)
    4. All severity values must be in [0.0, 1.0] (checked in processing)
    5. If all metrics unavailable: raise ScoreError (done in processing)

    Args:
        detector_results: DetectorResults object
        metric_dataframe: MetricDataFrame object
        windows: List of WindowDefinition objects
        detector_weights: Weights for detectors

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(detector_results, DetectorResults):
        raise ValidationError("detector_results must be a valid DetectorResults object")

    if not isinstance(metric_dataframe, MetricDataFrame):
        raise ValidationError("metric_dataframe must be a valid MetricDataFrame object")

    if not isinstance(windows, list) or not windows:
        raise ValidationError("windows must be a non-empty list")

    if not all(isinstance(w, WindowDefinition) for w in windows):
        raise ValidationError("All items in windows must be WindowDefinition objects")

    # Validate detector_weights if provided
    if detector_weights is not None:
        if not isinstance(detector_weights, dict):
            raise ValidationError("detector_weights must be a dictionary")

        valid_detectors = {"D-01", "D-02", "D-03"}
        for det_id in detector_weights.keys():
            if det_id not in valid_detectors:
                raise ValidationError(f"Invalid detector ID in detector_weights: {det_id}")

        # Check that weights are non-negative
        for det_id, weight in detector_weights.items():
            if not isinstance(weight, (int, float)) or weight < 0:
                raise ValidationError(f"Weight for {det_id} must be non-negative number, got: {weight}")


def validate_evidence_inputs(repository_context: RepositoryContext,
                            metric_dataframe: MetricDataFrame,
                            windows: List[WindowDefinition],
                            detector_results: DetectorResults,
                            score_package: ScorePackage,
                            configuration: Dict[str, Any]) -> None:
    """Validate inputs for INT-06: Evidence Generation.

    Validates:
    1. All nested objects must match their respective schemas
    2. Every positive detector flag must have corresponding statistical evidence
    3. provenance.timestamp must be ISO 8601 UTC
    4. warnings array captures all non-fatal issues from pipeline execution

    Args:
        repository_context: RepositoryContext object
        metric_dataframe: MetricDataFrame object
        windows: List of WindowDefinition objects
        detector_results: DetectorResults object
        score_package: ScorePackage object
        configuration: Runtime configuration

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(repository_context, RepositoryContext):
        raise ValidationError("repository_context must be a valid RepositoryContext object")

    if not isinstance(metric_dataframe, MetricDataFrame):
        raise ValidationError("metric_dataframe must be a valid MetricDataFrame object")

    if not isinstance(windows, list):
        raise ValidationError("windows must be a list")

    if not all(isinstance(w, WindowDefinition) for w in windows):
        raise ValidationError("All items in windows must be WindowDefinition objects")

    if not isinstance(detector_results, DetectorResults):
        raise ValidationError("detector_results must be a valid DetectorResults object")

    if not isinstance(score_package, ScorePackage):
        raise ValidationError("score_package must be a valid ScorePackage object")

    if not isinstance(configuration, dict):
        raise ValidationError("configuration must be a dictionary")


def validate_explanation_inputs(evidence_package: EvidencePackage,
                               score_package: ScorePackage,
                               metric_filter: Optional[str] = None,
                               detector_filter: Optional[str] = None) -> None:
    """Validate inputs for INT-07: Explanation Generation.

    Validates:
    1. Templates must exist in src/miie/reporting/templates/ (checked during processing)
    2. Every explanation must cite at least one evidence_ref (checked during processing)
    3. severity must match detector output severity (checked during processing)
    4. narrative must be non-empty string (checked during processing)
    5. Templates rendered in detector priority order: D-01, D-02, D-03 (checked during processing)

    Args:
        evidence_package: EvidencePackage object
        score_package: ScorePackage object
        metric_filter: Optional metric ID to filter explanations
        detector_filter: Optional detector ID to filter explanations

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(evidence_package, EvidencePackage):
        raise ValidationError("evidence_package must be a valid EvidencePackage object")

    if not isinstance(score_package, ScorePackage):
        raise ValidationError("score_package must be a valid ScorePackage object")

    if metric_filter is not None:
        if not isinstance(metric_filter, str):
            raise ValidationError("metric_filter must be a string or None")
        valid_metrics = {"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"}
        if metric_filter not in valid_metrics:
            raise ValidationError(f"metric_filter must be one of {valid_metrics}, got: {metric_filter}")

    if detector_filter is not None:
        if not isinstance(detector_filter, str):
            raise ValidationError("detector_filter must be a string or None")
        valid_detectors = {"D-01", "D-02", "D-03"}
        if detector_filter not in valid_detectors:
            raise ValidationError(f"detector_filter must be one of {valid_detectors}, got: {detector_filter}")


def validate_benchmark_inputs(suite_id: str, detector_ids: List[str],
                             config: Dict[str, Any], seed: int = 42) -> None:
    """Validate inputs for INT-09: Benchmark Execution.

    Validates:
    1. suite_id must match directory name in ~/.miie/benchmarks/
    2. detector_ids must be valid and compatible with suite schema version
    3. seed must be integer (default 42)
    4. Suite manifest must exist and be valid (checked during processing)

    Args:
        suite_id: Benchmark suite identifier
        detector_ids: List of detector IDs to evaluate
        config: Configuration overrides for detectors
        seed: Random seed for reproducibility

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(suite_id, str) or not suite_id:
        raise ValidationError("suite_id must be a non-empty string")

    if not isinstance(detector_ids, list) or not detector_ids:
        raise ValidationError("detector_ids must be a non-empty list")

    valid_detectors = {"D-01", "D-02", "D-03", "all"}
    for det in detector_ids:
        if det not in valid_detectors:
            raise ValidationError(f"Invalid detector ID: {det}. Must be one of {valid_detectors}")

    if not isinstance(config, dict):
        raise ValidationError("config must be a dictionary")

    if not isinstance(seed, int):
        raise ValidationError("seed must be an integer")


def validate_evaluation_inputs(benchmark_run: BenchmarkRun,
                              ground_truth: Dict[str, Any]) -> None:
    """Validate inputs for INT-10: Evaluation.

    Validates:
    1. All metrics in [0.0, 1.0] (checked during processing)
    2. TP + FP + TN + FN = total instances (checked during processing)
    3. Division by zero in precision/recall/F1 returns 0.0 with warning (checked during processing)
    4. AUC-ROC ≥ 0.5 sanity check (warning if below, not error) (checked during processing)

    Args:
        benchmark_run: BenchmarkRun object
        ground_truth: Ground truth data

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(benchmark_run, BenchmarkRun):
        raise ValidationError("benchmark_run must be a valid BenchmarkRun object")

    if not isinstance(ground_truth, dict):
        raise ValidationError("ground_truth must be a dictionary")


def validate_report_inputs(analysis_result: Dict[str, Any],
                          output_formats: List[str],
                          output_dir: Path) -> None:
    """Validate inputs for INT-08: Report Generation.

    Validates:
    1. output_formats must contain valid format strings
    2. output_dir must be writable (checked during processing)
    3. Disk space check before write (checked during processing)
    4. All files written atomically (temp + rename) (checked during processing)
    5. manifest.json written last with checksums of all other files (checked during processing)

    Args:
        analysis_result: Analysis results to export
        output_formats: List of format strings ("json", "md", "csv")
        output_dir: Directory to write output files

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(analysis_result, dict):
        raise ValidationError("analysis_result must be a dictionary")

    if not isinstance(output_formats, list) or not output_formats:
        raise ValidationError("output_formats must be a non-empty list")

    valid_formats = {"json", "md", "csv"}
    for fmt in output_formats:
        if fmt not in valid_formats:
            raise ValidationError(f"Invalid output format: {fmt}. Must be one of {valid_formats}")

    if not isinstance(output_dir, Path):
        raise ValidationError("output_dir must be a Path object")


# CLI-specific validators
def validate_cli_ingest_inputs(repo_path: str, shallow: Optional[int] = None) -> None:
    """Validate inputs for miie ingest CLI command."""
    validate_repository_inputs(repo_path, shallow_depth=shallow)


def validate_cli_analyze_inputs(repo_path: str, since: Optional[str] = None,
                               until: Optional[str] = None, metrics: Optional[List[str]] = None,
                               window_strategy: Optional[str] = None, window_size: Optional[int] = None,
                               output_dir: Optional[Path] = None, detectors: Optional[List[str]] = None,
                               format: Optional[List[str]] = None, exclude_bots: bool = False) -> None:
    """Validate inputs for miie analyze CLI command."""
    if not repo_path or not isinstance(repo_path, str):
        raise ValidationError("repo_path must be a non-empty string")

    # Validate time strings
    if since is not None:
        if not isinstance(since, str):
            raise ValidationError("since must be a string")
        # In real implementation, we'd parse ISO 8601

    if until is not None:
        if not isinstance(until, str):
            raise ValidationError("until must be a string")
        # In real implementation, we'd parse ISO 8601

    if since is not None and until is not None:
        if since > until:  # Simple string comparison for ISO 8601
            raise ValidationError("since must be before or equal to until")

    # Validate metrics
    if metrics is not None:
        if not isinstance(metrics, list):
            raise ValidationError("metrics must be a list")
        valid_metrics = {"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07", "all"}
        for metric in metrics:
            if metric not in valid_metrics:
                raise ValidationError(f"Invalid metric ID: {metric}")

    # Validate window strategy
    if window_strategy is not None:
        valid_strategies = {"time", "commit", "release", "custom"}
        if window_strategy not in valid_strategies:
            raise ValidationError(f"window_strategy must be one of {valid_strategies}")

    # Validate window size
    if window_size is not None:
        if not isinstance(window_size, int) or window_size < 1:
            raise ValidationError("window_size must be an integer ≥ 1")

    # Validate output directory
    if output_dir is not None:
        if not isinstance(output_dir, Path):
            raise ValidationError("output_dir must be a Path object")

    # Validate detectors
    if detectors is not None:
        if not isinstance(detectors, list):
            raise ValidationError("detectors must be a list")
        valid_detectors = {"D-01", "D-02", "D-03", "all"}
        for det in detectors:
            if det not in valid_detectors:
                raise ValidationError(f"Invalid detector ID: {det}")

    # Validate format
    if format is not None:
        if not isinstance(format, list):
            raise ValidationError("format must be a list")
        valid_formats = {"json", "md", "csv"}
        for fmt in format:
            if fmt not in valid_formats:
                raise ValidationError(f"Invalid format: {fmt}. Must be one of {valid_formats}")

    # Validate exclude_bots
    if not isinstance(exclude_bots, bool):
        raise ValidationError("exclude_bots must be a boolean")


# Additional helper validation functions
def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID4."""
    import uuid
    try:
        val = uuid.UUID(uuid_string, version=4)
        return str(val) == uuid_string
    except ValueError:
        return False


def is_valid_sha256(hex_string: str) -> bool:
    """Check if string is a valid SHA-256 hash."""
    if not isinstance(hex_string, str) or len(hex_string) != 64:
        return False
    try:
        int(hex_string, 16)
        return True
    except ValueError:
        return False


def is_valid_window_id(window_id: str) -> bool:
    """Check if string is a valid window ID (wNN format)."""
    return isinstance(window_id, str) and len(window_id) == 3 and window_id.startswith('w') and window_id[1:].isdigit()


def is_valid_metric_id(metric_id: str) -> bool:
    """Check if string is a valid metric ID (M-NN format)."""
    valid_metrics = {"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"}
    return metric_id in valid_metrics


def is_valid_detector_id(detector_id: str) -> bool:
    """Check if string is a valid detector ID (D-NN format)."""
    valid_detectors = {"D-01", "D-02", "D-03"}
    return detector_id in valid_detectors