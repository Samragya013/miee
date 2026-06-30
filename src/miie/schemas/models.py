"""
Data schemas for MIIE v1.0 core entities.

Implements the four core schemas needed for Day 10 dry-run slice:
- RepositoryContext
- MetricDataFrame
- DetectorResult
- EvidencePackage
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RepositoryContext:
    """
    Repository context extracted during ingestion (M-01).

    Source: BSD-Engineering Section 5.3
    """

    repo_id: str
    local_path: Path
    is_remote: bool
    remote_url: Optional[str] = None
    total_commits: int = 0
    first_commit_date: Optional[datetime.datetime] = None
    last_commit_date: Optional[datetime.datetime] = None
    contributor_count: int = 0
    is_shallow: bool = False
    is_fork: bool = False
    language_distribution: Optional[Dict[str, int]] = None

    def __post_init__(self):
        """Validate RepositoryContext constraints."""
        if self.total_commits < 10:
            raise ValueError(f"total_commits must be >= 10, got {self.total_commits}")
        if self.contributor_count < 1:
            raise ValueError(f"contributor_count must be >= 1, got {self.contributor_count}")


@dataclass
class MetricDataFrame:
    """
    Container for extracted metrics (M-02 output).

    Source: BSD-Engineering Section 6
    Represents metric data as defined in BSD Section 6.3 JSON serialization.
    """

    repo_id: str
    run_id: str
    timestamp: datetime.datetime
    metrics: Dict[str, Dict[str, List[Optional[float]]]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate that only frozen metrics are present."""
        allowed_metrics = {f"M-{i:02d}" for i in range(1, 8)}  # M-01 through M-07
        for metric_id in self.metrics:
            if metric_id not in allowed_metrics:
                raise ValueError(f"Invalid metric ID: {metric_id}. Must be one of {allowed_metrics}")


@dataclass
class D01Output:
    """
    Output from D-01: Distributional Drift Detector.

    Source: BSD-Engineering Section 8.2
    """

    ks_statistic: float
    ks_p_value: float
    psi_value: float
    direction: str  # mean_shift, variance_collapse, shape_change
    severity: float
    flagged: bool

    def __post_init__(self):
        if self.direction not in {"mean_shift", "variance_collapse", "shape_change"}:
            raise ValueError(
                f"direction must be one of mean_shift, variance_collapse, shape_change; got {self.direction}"
            )
        if not (0.0 <= self.severity <= 1.0):
            raise ValueError(f"severity must be between 0.0 and 1.0, got {self.severity}")


@dataclass
class D02Output:
    """
    Output from D-02: Correlation Breakdown Detector.

    Source: BSD-Engineering Section 8.3
    """

    pearson_r: float
    spearman_r: float
    fisher_z_ci: tuple  # (lower, upper)
    breakdown_type: Optional[str]  # sudden_drop, sign_reversal, gradual_erosion, confidence_exclusion
    delta_r: float
    severity: float
    flagged: bool

    def __post_init__(self):
        allowed_types = {
            "sudden_drop",
            "sign_reversal",
            "gradual_erosion",
            "confidence_exclusion",
        }
        if self.breakdown_type is not None and self.breakdown_type not in allowed_types:
            raise ValueError(f"breakdown_type must be one of {allowed_types} or None; got {self.breakdown_type}")
        if not (0.0 <= self.severity <= 1.0):
            raise ValueError(f"severity must be between 0.0 and 1.0, got {self.severity}")


@dataclass
class D03Output:
    """
    Output from D-03: Threshold Compression Detector.

    Source: BSD-Engineering Section 8.4
    """

    excess_mass_z: float
    excess_mass_flag: bool
    dip_test_p_value: float
    multimodal_flag: bool
    compression_index: float
    threshold: float
    severity: float
    flagged: bool

    def __post_init__(self):
        if not (0.0 <= self.severity <= 1.0):
            raise ValueError(f"severity must be between 0.0 and 1.0, got {self.severity}")


@dataclass
class DetectorResult:
    """
    Container for detector results (D-01 through D-03 output).

    Source: BSD-Engineering Section 8 and class DetectorResults
    Extended: IMS Phase 6 (Evidence Refactor) for observation-level metadata

    Accepts both the legacy dict-based detector_outputs format and the
    new typed d_01/d_02/d_03 fields for backward compatibility.

    Observation metadata fields provide structured access to observation-level
    evidence that was previously buried in untyped detector_outputs dicts.
    """

    # Legacy fields (backward compatible)
    detector_outputs: Dict[str, Dict] = field(default_factory=dict)
    d_01: Dict[str, Dict[str, D01Output]] = field(default_factory=dict)
    d_02: Dict[str, Dict[str, D02Output]] = field(default_factory=dict)
    d_03: Dict[str, Dict[str, Dict[str, D03Output]]] = field(default_factory=dict)

    # Observation-level metadata fields (IMS Phase 6)
    observation_counts: Dict[str, int] = field(default_factory=dict)
    """Per-metric observation counts: metric_id -> count of observations used."""

    window_ids: List[str] = field(default_factory=list)
    """Ordered list of window IDs used in detection."""

    sample_sizes: Dict[str, int] = field(default_factory=dict)
    """Per-metric sample sizes: metric_id -> number of data points."""

    statistical_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    """Per-metric statistical summaries: metric_id -> {mean, std, min, max, median, count}."""

    threshold_metadata: Dict[str, Any] = field(default_factory=dict)
    """Threshold configuration used: {alpha, psi_threshold, compression_threshold, etc.}."""

    execution_timing: Dict[str, float] = field(default_factory=dict)
    """Per-detector execution times in seconds: detector_id -> seconds."""

    scientific_provenance: Dict[str, Any] = field(default_factory=dict)
    """Scientific configuration: {method, version, parameters, reference, etc.}."""

    def __post_init__(self):
        """Validate that only frozen detectors are present."""
        allowed_detectors = {f"D-{i:02d}" for i in range(1, 4)}  # D-01 through D-03
        for detector_id in self.detector_outputs:
            if detector_id not in allowed_detectors:
                raise ValueError(f"Invalid detector ID: {detector_id}. Must be one of {allowed_detectors}")

    def get_observation_metadata(self, detector_id: str) -> Dict[str, Any]:
        """
        Extract observation-level metadata from a specific detector's output.

        Args:
            detector_id: Detector identifier (e.g., 'D-01', 'D-02', 'D-03')

        Returns:
            Dictionary containing observation-level metadata or empty dict if not found.
        """
        if detector_id not in self.detector_outputs:
            return {}

        output = self.detector_outputs[detector_id]
        metadata: Dict[str, Any] = {}

        # Extract observation counts
        if "observation_counts" in output:
            metadata["observation_counts"] = output["observation_counts"]

        # Extract window pairs analyzed
        if "window_pairs_analyzed" in output:
            metadata["window_pairs"] = output["window_pairs_analyzed"]

        # Extract per-window statistics
        for key in ["ks_statistics", "psi_values", "drift_directions", "correlation_changes"]:
            if key in output:
                metadata[key] = output[key]

        # Extract drift events (contain detailed observation-level info)
        if "drift_events" in output:
            metadata["drift_events"] = output["drift_events"]

        # Extract confidence intervals
        if "confidence_intervals" in output:
            metadata["confidence_intervals"] = output["confidence_intervals"]

        return metadata

    def get_all_observation_counts(self) -> Dict[str, int]:
        """
        Get combined observation counts from all detectors.

        Returns:
            Dictionary mapping metric_id to total observation count.
        """
        combined: Dict[str, int] = {}

        for detector_id, output in self.detector_outputs.items():
            if "observation_counts" in output:
                for metric_id, count in output["observation_counts"].items():
                    combined[metric_id] = max(combined.get(metric_id, 0), count)

        return combined

    def get_execution_timing_summary(self) -> Dict[str, float]:
        """
        Get execution timing summary.

        Returns:
            Dictionary with total_time and per-detector times.
        """
        summary: Dict[str, float] = {
            "total_time": sum(self.execution_timing.values()),
            "detectors": dict(self.execution_timing),
        }
        return summary


@dataclass
class Provenance:
    """
    Container for provenance information.

    Source: ACS v1.0 Section 10.1 (Evidence Generation)
    """

    miie_version: str
    config_hash: str
    timestamp: str  # ISO 8601 UTC
    seed: Optional[int]
    platform: Optional[str]
    python_version: Optional[str]
    dependency_hash: Optional[str]

    def __post_init__(self):
        """Validate Provenance constraints."""
        # Basic validation - timestamp should be a string
        if not isinstance(self.timestamp, str):
            raise ValueError(f"provenance.timestamp must be a string, got {type(self.timestamp)}")
        # TODO: Add proper ISO 8601 UTC validation


@dataclass
class WarningItem:
    """
    Container for warning information.

    Source: ACS v1.0 Section 10.1 (Evidence Generation)
    """

    stage: str
    message: str
    metric_id: Optional[str]
    detector_id: Optional[str]


@dataclass
class EvidencePackage:
    """
    Container for traceable evidence (M-09 Evidence Aggregator output).

    Source: ACS v1.0 Section 10.1 (Evidence Generation)
    Extended: IMS Phase 6 (Evidence Refactor) for observation-level provenance

    Observation provenance fields provide complete traceability from evidence
    back to the raw observations, detector executions, and statistical artifacts
    that produced the evidence.
    """

    # Core evidence fields (backward compatible)
    provenance: Provenance
    windows: List[WindowDefinition]
    metrics: Dict[str, Any]  # Summary of metric data
    detector_outputs: DetectorResults
    scores: ScorePackage
    warnings: List[WarningItem] = field(default_factory=list)

    # Observation-level provenance fields (IMS Phase 6)
    observation_summary: Dict[str, Any] = field(default_factory=dict)
    """
    Summary of observations used in evidence generation:
    {
        "total_observations": int,
        "per_metric": {
            "M-02": {"count": int, "window_count": int, "value_range": [min, max]},
            ...
        },
        "observation_quality": {"complete": int, "partial": int, "estimated": int}
    }
    """

    detector_execution_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    """
    Per-detector execution metadata:
    {
        "D-01": {
            "method": "kolmogorov_smirnov",
            "parameters": {"alpha": 0.05, "psi_threshold": 0.2},
            "execution_time_seconds": float,
            "windows_analyzed": int,
            "observations_consumed": int,
            "scientific_reference": "..."
        },
        ...
    }
    """

    statistical_artifacts: Dict[str, Any] = field(default_factory=dict)
    """
    Intermediate statistical calculations and artifacts:
    {
        "drift_statistics": {
            "D-01": {
                "ks_statistics": Dict[str, float],
                "psi_values": Dict[str, float],
                "drift_events": List[Dict]
            }
        },
        "correlation_artifacts": {
            "D-02": {
                "correlation_matrices": Dict[str, List[List[float]]],
                "fisher_z_scores": Dict[str, float]
            }
        },
        "compression_artifacts": {
            "D-03": {
                "dip_statistics": Dict[str, float],
                "excess_mass_statistics": Dict[str, float]
            }
        }
    }
    """

    configuration_snapshot: Dict[str, Any] = field(default_factory=dict)
    """
    Snapshot of configuration used for this evidence generation:
    {
        "metric_list": List[str],
        "segmentation_strategy": str,
        "segmentation_size": int,
        "detector_config": Dict[str, Any],
        "enabled_detectors": List[str],
        "extraction_params": {
            "since": Optional[str],
            "until": Optional[str],
            "exclude_bots": bool
        }
    }
    """

    def __post_init__(self):
        """Validate EvidencePackage structure."""
        # Validate provenance
        if not isinstance(self.provenance, Provenance):
            raise ValueError("provenance must be a Provenance instance")

        # Validate windows are WindowDefinition instances
        for i, window in enumerate(self.windows):
            if not isinstance(window, WindowDefinition):
                raise ValueError(f"windows[{i}] must be a WindowDefinition instance")

        # Validate scores is a ScorePackage instance
        if not isinstance(self.scores, ScorePackage):
            raise ValueError("scores must be a ScorePackage instance")

        # Validate detector_outputs is a DetectorResults instance
        if not isinstance(self.detector_outputs, DetectorResults):
            raise ValueError("detector_outputs must be a DetectorResults instance")

        # Validate warnings are WarningItem instances
        for i, warning in enumerate(self.warnings):
            if not isinstance(warning, WarningItem):
                raise ValueError(f"warnings[{i}] must be a WarningItem instance")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert EvidencePackage to a deterministic dictionary for serialization.

        Returns:
            Dictionary representation with all fields in consistent order.
        """
        return {
            "provenance": {
                "miie_version": self.provenance.miie_version,
                "config_hash": self.provenance.config_hash,
                "timestamp": self.provenance.timestamp,
                "seed": self.provenance.seed,
                "platform": self.provenance.platform,
                "python_version": self.provenance.python_version,
                "dependency_hash": self.provenance.dependency_hash,
            },
            "windows": [
                {
                    "window_id": w.window_id,
                    "start_date": w.start_date.isoformat(),
                    "end_date": w.end_date.isoformat(),
                    "commits": w.commits,
                    "strategy": w.strategy,
                    "size_config": w.size_config if hasattr(w, "size_config") else {},
                }
                for w in self.windows
            ],
            "metrics": self.metrics,
            "detector_outputs": self.detector_outputs.detector_outputs,
            "scores": {
                "integrity": {
                    "overall": self.scores.integrity.overall,
                    "per_metric": self.scores.integrity.per_metric,
                    "formula_version": self.scores.integrity.formula_version,
                },
                "confidence": {
                    "overall": self.scores.confidence.overall,
                    "factors": self.scores.confidence.factors,
                    "band": self.scores.confidence.band,
                },
                "timestamp": self.scores.timestamp.isoformat(),
                "config_hash": self.scores.config_hash,
                "formula_version": self.scores.formula_version,
            },
            "warnings": [
                {
                    "stage": w.stage,
                    "message": w.message,
                    "metric_id": w.metric_id,
                    "detector_id": w.detector_id,
                }
                for w in self.warnings
            ],
            # Observation-level provenance fields (IMS Phase 6)
            "observation_summary": self.observation_summary,
            "detector_execution_metadata": self.detector_execution_metadata,
            "statistical_artifacts": self.statistical_artifacts,
            "configuration_snapshot": self.configuration_snapshot,
        }

    def get_observation_trace(self, metric_id: str) -> Dict[str, Any]:
        """
        Get complete observation trace for a specific metric.

        Args:
            metric_id: Metric identifier (e.g., 'M-02')

        Returns:
            Dictionary containing complete observation trace or empty dict if not found.
        """
        trace: Dict[str, Any] = {
            "metric_id": metric_id,
            "windows": [],
            "detectors": {},
            "summary": {},
        }

        # Extract metric-specific data from windows
        for window in self.windows:
            if hasattr(window, "metric_values") and metric_id in window.metric_values:
                trace["windows"].append(
                    {
                        "window_id": window.window_id,
                        "value": window.metric_values[metric_id],
                        "start_date": window.start_date.isoformat(),
                        "end_date": window.end_date.isoformat(),
                    }
                )

        # Extract detector outputs for this metric
        for detector_id, output in self.detector_outputs.detector_outputs.items():
            if metric_id in str(output):
                trace["detectors"][detector_id] = output

        # Extract observation summary
        if "per_metric" in self.observation_summary and metric_id in self.observation_summary["per_metric"]:
            trace["summary"] = self.observation_summary["per_metric"][metric_id]

        return trace

    def get_evidence_completeness(self) -> Dict[str, Any]:
        """
        Get evidence completeness assessment.

        Returns:
            Dictionary with completeness metrics and gaps.
        """
        completeness: Dict[str, Any] = {
            "has_provenance": bool(self.provenance),
            "has_windows": bool(self.windows),
            "has_metrics": bool(self.metrics),
            "has_detector_outputs": bool(self.detector_outputs.detector_outputs),
            "has_scores": bool(self.scores),
            "has_observation_summary": bool(self.observation_summary),
            "has_detector_execution_metadata": bool(self.detector_execution_metadata),
            "has_statistical_artifacts": bool(self.statistical_artifacts),
            "has_configuration_snapshot": bool(self.configuration_snapshot),
            "window_count": len(self.windows),
            "detector_count": len(self.detector_outputs.detector_outputs),
            "warning_count": len(self.warnings),
        }

        # Calculate completeness score
        required_fields = [
            "has_provenance",
            "has_windows",
            "has_metrics",
            "has_detector_outputs",
            "has_scores",
        ]
        optional_fields = [
            "has_observation_summary",
            "has_detector_execution_metadata",
            "has_statistical_artifacts",
            "has_configuration_snapshot",
        ]

        required_count = sum(1 for f in required_fields if completeness[f])
        optional_count = sum(1 for f in optional_fields if completeness[f])

        completeness["required_completeness"] = required_count / len(required_fields)
        completeness["optional_completeness"] = optional_count / len(optional_fields)
        completeness["overall_completeness"] = (required_count + optional_count) / (
            len(required_fields) + len(optional_fields)
        )

        return completeness


# TODO: These are placeholder implementations for deferred schema classes.
# According to the operating plan, these schemas are deferred with reasons documented.
# They are implemented here as minimal placeholders to allow contracts layer development.
# In a full implementation, these would be replaced with the complete ACS v1.0 schema definitions.


@dataclass
class WindowDefinition:
    """
    Definition of an analysis window.

    Source: ACS v1.0 Section 6.2 (Window Definition)
    """

    window_id: str
    start_date: datetime.date
    end_date: datetime.date
    commits: int
    strategy: str
    size_config: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate WindowDefinition constraints."""
        if not self.window_id or not re.match(r"^w[0-9]+$", self.window_id):
            raise ValueError(f"window_id must match pattern ^w[0-9]+$, got {self.window_id}")
        if self.start_date >= self.end_date:
            raise ValueError(
                f"start_date must be before end_date, got start_date={self.start_date}, end_date={self.end_date}"
            )
        if self.commits < 1:
            raise ValueError(f"commits must be >= 1, got {self.commits}")


@dataclass
class DetectorResults:
    """
    Container for results from multiple detectors.

    Source: BSD-Engineering Section 8.5 (DetectorResults dataclass)
    """

    d_01: Dict[str, Dict[str, D01Output]] = field(default_factory=dict)
    d_02: Dict[str, Dict[str, D02Output]] = field(default_factory=dict)
    d_03: Dict[str, Dict[str, Dict[str, D03Output]]] = field(default_factory=dict)
    detector_outputs: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        """Validate DetectorResults constraints."""
        # d_01 keys are metric_ids, d_02 keys are metric_pairs, d_03 keys are metric_ids
        # No detector-level validation needed here; detector identity is implicit by field name.


@dataclass
class IntegrityScore:
    """
    Container for integrity scores.

    Source: ACS v1.0 Section 9.2 (Score Package)
    """

    overall: float  # [0.0, 1.0]
    per_metric: Dict[str, float]  # metric_id -> [0.0, 1.0]
    formula_version: str

    def __post_init__(self):
        """Validate IntegrityScore constraints."""
        if not (0.0 <= self.overall <= 1.0):
            raise ValueError(f"integrity.overall must be between 0.0 and 1.0, got {self.overall}")
        for metric_id, score in self.per_metric.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"integrity.per_metric['{metric_id}'] must be between 0.0 and 1.0, got {score}")


@dataclass
class ConfidenceScore:
    """
    Container for confidence scores.

    Source: ACS v1.0 Section 9.2 (Score Package)
    """

    overall: float  # [0.0, 1.0]
    factors: Dict[str, float]  # sample_size, variance, missing_data, window_balance, detector_success
    band: Optional[str]  # "high" | "medium" | "low" | "critical"

    def __post_init__(self):
        """Validate ConfidenceScore constraints."""
        if not (0.0 <= self.overall <= 1.0):
            raise ValueError(f"confidence.overall must be between 0.0 and 1.0, got {self.overall}")
        for factor_name, value in self.factors.items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"confidence.factors['{factor_name}'] must be between 0.0 and 1.0, got {value}")
        if self.band is not None and self.band not in {
            "high",
            "medium",
            "low",
            "critical",
        }:
            raise ValueError(f"confidence.band must be one of 'high', 'medium', 'low', 'critical', got {self.band}")


@dataclass
class ScorePackage:
    """
    Container for computed integrity and confidence scores.

    Source: ACS v1.0 Section 9.2 (Score Package)
    """

    integrity: IntegrityScore
    confidence: ConfidenceScore
    timestamp: datetime.datetime
    config_hash: str
    formula_version: str = "1.0.0"

    def __post_init__(self):
        """Validate ScorePackage constraints."""
        # Validate that timestamp is timezone-aware (UTC)
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (UTC)")


@dataclass
class Explanation:
    """
    Individual explanation for a detector finding.

    Source: BSD-Engineering Section 11.1
    """

    metric_id: str
    detector_id: str
    narrative: str
    severity: str  # mild, moderate, severe
    evidence_refs: List[str]
    confidence: str  # high, medium, low
    rule_fired: str

    def __post_init__(self):
        if self.severity not in {"mild", "moderate", "severe"}:
            raise ValueError(f"severity must be one of mild, moderate, severe; got {self.severity}")
        if self.confidence not in {"high", "medium", "low"}:
            raise ValueError(f"confidence must be one of high, medium, low; got {self.confidence}")


@dataclass
class ExplanationReport:
    """
    Container for explanation narratives and recommendations.

    Source: BSD-Engineering Section 11.1 (ExplanationReport schema)
    """

    explanations: List[Explanation] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    narratives: List[str] = field(default_factory=list)  # legacy compat

    def __post_init__(self):
        """Validate ExplanationReport constraints."""
        for i, exp in enumerate(self.explanations):
            if not isinstance(exp, Explanation):
                raise ValueError(f"explanations[{i}] must be an Explanation instance")


@dataclass
class BenchmarkRun:
    """
    Container for benchmark execution results.

    Source: BSD-Engineering Section 15.1 (BenchmarkRun schema)
    """

    run_id: str = ""
    suite_id: str = ""
    detector_id: str = ""
    detector_version: str = ""
    seed: int = 0
    started_at: str = ""
    completed_at: str = ""
    predictions: Dict[str, Any] = field(default_factory=dict)
    timing: Dict[str, float] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)  # legacy compat

    def __post_init__(self):
        """Validate BenchmarkRun constraints."""
        if self.detector_id and self.detector_id not in {"D-01", "D-02", "D-03"}:
            raise ValueError(f"detector_id must be one of D-01, D-02, D-03; got {self.detector_id}")


@dataclass
class ConfusionMatrix:
    """
    Confusion matrix for binary classification evaluation.

    Source: BSD-Engineering Section 16.1 (EvaluationResult confusion_matrix)
    """

    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    def __post_init__(self):
        for field_name in ("tp", "fp", "tn", "fn"):
            val = getattr(self, field_name)
            if val < 0:
                raise ValueError(f"confusion_matrix.{field_name} must be >= 0, got {val}")


@dataclass
class EvaluationResult:
    """
    Container for evaluation metrics.

    Source: BSD-Engineering Section 16.1 (EvaluationResult schema)
    """

    suite_id: str = ""
    detector_id: str = ""
    detector_version: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    confusion_matrix: Optional[ConfusionMatrix] = None
    per_dataset_results: Optional[Dict[str, Dict[str, float]]] = None
    # Legacy fields for backward compatibility
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0

    def __post_init__(self):
        """Validate EvaluationResult constraints."""
        for field_name in ("accuracy", "precision", "recall", "f1_score"):
            val = getattr(self, field_name)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{field_name} must be between 0.0 and 1.0, got {val}")
        for metric_name, val in self.metrics.items():
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"metrics['{metric_name}'] must be between 0.0 and 1.0, got {val}")


@dataclass
class ReportOutput:
    """
    Container for generated report output paths (deferred schema placeholder).

    Source: ACS v1.0 Section 13.2 (Report Output)
    TODO: Implement full ReportOutput schema per ACS v1.0 specification
    """

    report_paths: Dict[str, Path] = field(default_factory=dict)
    manifest_path: Optional[Path] = None
    checksums: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate ReportOutput constraints."""
        # Placeholder validation - full validation TBD


@dataclass
class GroundTruthLabel:
    """
    Individual ground truth label for a metric/detector combination.

    Source: BSD-Engineering Section 14.1 (GroundTruth labels items)
    """

    repo_id: str  # ^repo_[0-9]{3}$
    metric_id: str
    label: bool
    event_type: str  # MDE-01, MDE-02, MDE-03, MDE-04
    window_id: Optional[str] = None
    window_pair: Optional[List[str]] = None
    metric_pair: Optional[List[str]] = None
    threshold: Optional[float] = None
    severity: Optional[str] = None  # mild, moderate, severe
    confidence: Optional[str] = None  # high, medium, low
    evidence_refs: List[str] = field(default_factory=list)
    annotator_agreement: Optional[float] = None

    def __post_init__(self):
        if not re.match(r"^repo_[0-9]{3}$", self.repo_id):
            raise ValueError(f"repo_id must match pattern ^repo_[0-9]{{3}}$; got {self.repo_id}")
        if self.event_type not in {"MDE-01", "MDE-02", "MDE-03", "MDE-04"}:
            raise ValueError(f"event_type must be one of MDE-01, MDE-02, MDE-03, MDE-04; got {self.event_type}")
        if self.severity is not None and self.severity not in {
            "mild",
            "moderate",
            "severe",
        }:
            raise ValueError(f"severity must be one of mild, moderate, severe; got {self.severity}")
        if self.confidence is not None and self.confidence not in {
            "high",
            "medium",
            "low",
        }:
            raise ValueError(f"confidence must be one of high, medium, low; got {self.confidence}")
        if self.annotator_agreement is not None and not (0.0 <= self.annotator_agreement <= 1.0):
            raise ValueError(f"annotator_agreement must be between 0.0 and 1.0, got {self.annotator_agreement}")


@dataclass
class GroundTruthInput:
    """
    Container for ground truth input data.

    Source: BSD-Engineering Section 14.1 (GroundTruth schema)
    """

    suite_id: str = ""
    version: str = ""
    labels: List[GroundTruthLabel] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)  # legacy compat

    def __post_init__(self):
        """Validate GroundTruthInput constraints."""
        for i, label in enumerate(self.labels):
            if not isinstance(label, GroundTruthLabel):
                raise ValueError(f"labels[{i}] must be a GroundTruthLabel instance")


@dataclass
class Annotation:
    """
    Container for individual annotations (deferred schema placeholder).

    Source: ACS v1.0 Section 15.2 (Annotation)
    TODO: Implement full Annotation schema per ACS v1.0 specification
    """

    label: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate Annotation constraints."""
        # Placeholder validation - full validation TBD
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")


# ---------------------------------------------------------------------------
# BSD §12: AnalysisResult
# ---------------------------------------------------------------------------


@dataclass
class RunMetadata:
    """
    Runtime metadata captured during analysis execution.

    Source: BSD-Engineering Section 12 (AnalysisResult)
    """

    duration_seconds: float
    memory_peak_mb: float
    cpu_time_seconds: float
    stage_timings: Dict[str, float]

    def __post_init__(self):
        """Validate RunMetadata constraints."""
        if self.duration_seconds < 0:
            raise ValueError(f"duration_seconds must be >= 0, got {self.duration_seconds}")
        if self.memory_peak_mb < 0:
            raise ValueError(f"memory_peak_mb must be >= 0, got {self.memory_peak_mb}")
        if self.cpu_time_seconds < 0:
            raise ValueError(f"cpu_time_seconds must be >= 0, got {self.cpu_time_seconds}")
        for stage, timing in self.stage_timings.items():
            if timing < 0:
                raise ValueError(f"stage_timings['{stage}'] must be >= 0, got {timing}")


@dataclass
class AnalysisResult:
    """
    Top-level output of a complete MIIE analysis run.

    Source: BSD-Engineering Section 12 (AnalysisResult)
    """

    miie_version: str
    generated_at: str  # ISO 8601 UTC
    config_hash: str
    repository: RepositoryContext
    windows: List[WindowDefinition]
    metrics: MetricDataFrame
    detector_results: DetectorResults
    scores: ScorePackage
    evidence: EvidencePackage
    explanations: ExplanationReport
    run_metadata: RunMetadata

    def __post_init__(self):
        """Validate AnalysisResult structure."""
        if not self.miie_version:
            raise ValueError("miie_version must not be empty")
        if not self.generated_at:
            raise ValueError("generated_at must not be empty")
        if not self.config_hash:
            raise ValueError("config_hash must not be empty")
        if not isinstance(self.repository, RepositoryContext):
            raise ValueError("repository must be a RepositoryContext instance")
        for i, window in enumerate(self.windows):
            if not isinstance(window, WindowDefinition):
                raise ValueError(f"windows[{i}] must be a WindowDefinition instance")
        if not isinstance(self.metrics, MetricDataFrame):
            raise ValueError("metrics must be a MetricDataFrame instance")
        if not isinstance(self.detector_results, DetectorResults):
            raise ValueError("detector_results must be a DetectorResults instance")
        if not isinstance(self.scores, ScorePackage):
            raise ValueError("scores must be a ScorePackage instance")
        if not isinstance(self.evidence, EvidencePackage):
            raise ValueError("evidence must be an EvidencePackage instance")
        if not isinstance(self.explanations, ExplanationReport):
            raise ValueError("explanations must be an ExplanationReport instance")
        if not isinstance(self.run_metadata, RunMetadata):
            raise ValueError("run_metadata must be a RunMetadata instance")


# ---------------------------------------------------------------------------
# BSD §13: BenchmarkDataset
# ---------------------------------------------------------------------------


@dataclass
class SyntheticRepositoryMetadata:
    """
    Metadata for a single synthetic repository in a benchmark dataset.

    Source: BSD-Engineering Section 13 (BenchmarkDataset)
    """

    repo_id: str  # pattern ^repo_[0-9]{3}$
    category: str  # enum: real_world, synthetic_healthy, synthetic_pathological
    language: str
    parameters: Dict[str, Any]  # duration_days, total_commits, contributors, etc.

    def __post_init__(self):
        """Validate SyntheticRepositoryMetadata constraints."""
        if not re.match(r"^repo_[0-9]{3}$", self.repo_id):
            raise ValueError(f"repo_id must match pattern ^repo_[0-9]{{3}}$, got {self.repo_id}")
        allowed_categories = {
            "real_world",
            "synthetic_healthy",
            "synthetic_pathological",
        }
        if self.category not in allowed_categories:
            raise ValueError(f"category must be one of {allowed_categories}, got {self.category}")
        if not self.language:
            raise ValueError("language must not be empty")


@dataclass
class PathologyMetadata:
    """
    Metadata describing an injected pathology event in a benchmark dataset.

    Source: BSD-Engineering Section 13 (BenchmarkDataset)
    """

    event_type: str  # MDE-01, MDE-02, MDE-03
    metric_id: str
    target_window: str
    severity: float
    drift_direction: Optional[str] = None
    drift_magnitude: Optional[float] = None
    metric_pair: Optional[List[str]] = None
    breakdown_type: Optional[str] = None
    correlation_change: Optional[float] = None
    threshold: Optional[float] = None
    compression_ratio: Optional[float] = None

    def __post_init__(self):
        """Validate PathologyMetadata constraints."""
        allowed_event_types = {"MDE-01", "MDE-02", "MDE-03"}
        if self.event_type not in allowed_event_types:
            raise ValueError(f"event_type must be one of {allowed_event_types}, got {self.event_type}")
        if not self.metric_id:
            raise ValueError("metric_id must not be empty")
        if not self.target_window:
            raise ValueError("target_window must not be empty")
        if not (0.0 <= self.severity <= 1.0):
            raise ValueError(f"severity must be between 0.0 and 1.0, got {self.severity}")
        if self.drift_magnitude is not None and self.drift_magnitude < 0:
            raise ValueError(f"drift_magnitude must be >= 0, got {self.drift_magnitude}")
        if self.correlation_change is not None and not (-1.0 <= self.correlation_change <= 1.0):
            raise ValueError(f"correlation_change must be between -1.0 and 1.0, got {self.correlation_change}")
        if self.threshold is not None and self.threshold < 0:
            raise ValueError(f"threshold must be >= 0, got {self.threshold}")
        if self.compression_ratio is not None and self.compression_ratio < 0:
            raise ValueError(f"compression_ratio must be >= 0, got {self.compression_ratio}")


@dataclass
class BenchmarkDataset:
    """
    Complete benchmark dataset definition for detector evaluation.

    Source: BSD-Engineering Section 13 (BenchmarkDataset)
    """

    suite_id: str
    version: str
    description: str
    num_datasets: int
    metrics_included: List[str]
    detector_target: str
    window_strategy: str
    window_size_days: int
    random_seed: int
    pathology_ratio: float
    annotation_kappa: Optional[float] = None
    datasets: List[SyntheticRepositoryMetadata] = field(default_factory=list)
    pathologies: List[PathologyMetadata] = field(default_factory=list)

    def __post_init__(self):
        """Validate BenchmarkDataset constraints."""
        if not self.suite_id:
            raise ValueError("suite_id must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")
        if not self.description:
            raise ValueError("description must not be empty")
        if self.num_datasets < 1:
            raise ValueError(f"num_datasets must be >= 1, got {self.num_datasets}")
        if not self.metrics_included:
            raise ValueError("metrics_included must not be empty")
        if not self.detector_target:
            raise ValueError("detector_target must not be empty")
        if not self.window_strategy:
            raise ValueError("window_strategy must not be empty")
        if self.window_size_days < 1:
            raise ValueError(f"window_size_days must be >= 1, got {self.window_size_days}")
        if not (0.0 <= self.pathology_ratio <= 1.0):
            raise ValueError(f"pathology_ratio must be between 0.0 and 1.0, got {self.pathology_ratio}")
        if self.annotation_kappa is not None and not (0.0 <= self.annotation_kappa <= 1.0):
            raise ValueError(f"annotation_kappa must be between 0.0 and 1.0, got {self.annotation_kappa}")
        for i, ds in enumerate(self.datasets):
            if not isinstance(ds, SyntheticRepositoryMetadata):
                raise ValueError(f"datasets[{i}] must be a SyntheticRepositoryMetadata instance")
        for i, path in enumerate(self.pathologies):
            if not isinstance(path, PathologyMetadata):
                raise ValueError(f"pathologies[{i}] must be a PathologyMetadata instance")


# ---------------------------------------------------------------------------
# BSD §17: Configuration
# ---------------------------------------------------------------------------


@dataclass
class DetectorConfig:
    """
    Tunable parameters for individual detectors.

    Source: BSD-Engineering Section 17 (Configuration)
    """

    alpha: float = 0.05
    psi_threshold: float = 0.25
    correlation_threshold: float = 0.3
    margin: float = 0.02
    bootstrap_iterations: int = 1000
    bootstrap_seed: int = 42

    def __post_init__(self):
        """Validate DetectorConfig constraints."""
        if not (0.0 < self.alpha < 1.0):
            raise ValueError(f"alpha must be between 0.0 and 1.0 exclusive, got {self.alpha}")
        if self.psi_threshold < 0:
            raise ValueError(f"psi_threshold must be >= 0, got {self.psi_threshold}")
        if not (0.0 <= self.correlation_threshold <= 1.0):
            raise ValueError(f"correlation_threshold must be between 0.0 and 1.0, got {self.correlation_threshold}")
        if self.margin < 0:
            raise ValueError(f"margin must be >= 0, got {self.margin}")
        if self.bootstrap_iterations < 1:
            raise ValueError(f"bootstrap_iterations must be >= 1, got {self.bootstrap_iterations}")


@dataclass
class Configuration:
    """
    Top-level MIIE analysis configuration.

    Source: BSD-Engineering Section 17 (Configuration)
    """

    repo: str
    since: Optional[str] = None
    until: Optional[str] = None
    metrics: List[str] = field(default_factory=lambda: ["all"])
    window_strategy: str = "time"
    window_size: int = 90
    detectors: List[str] = field(default_factory=lambda: ["all"])
    output_formats: List[str] = field(default_factory=lambda: ["json"])
    exclude_bots: bool = False
    thresholds: Dict[str, Any] = field(default_factory=dict)
    detector_weights: Dict[str, float] = field(default_factory=lambda: {"D-01": 0.40, "D-02": 0.35, "D-03": 0.25})
    seed: int = 42
    output_dir: str = "./output"
    verbose: bool = False
    keep_cache: bool = False
    shallow_depth: int = 1
    detector_config: DetectorConfig = field(default_factory=DetectorConfig)

    def __post_init__(self):
        """Validate Configuration constraints."""
        if not self.repo:
            raise ValueError("repo must not be empty")
        if self.window_size < 1:
            raise ValueError(f"window_size must be >= 1, got {self.window_size}")
        if not self.output_formats:
            raise ValueError("output_formats must not be empty")
        # Validate detector_weights sum to 1.0 (within floating point tolerance)
        weight_sum = sum(self.detector_weights.values())
        if abs(weight_sum - 1.0) > 1e-6:
            raise ValueError(f"detector_weights must sum to 1.0, got {weight_sum}")
        if self.shallow_depth < 1:
            raise ValueError(f"shallow_depth must be >= 1, got {self.shallow_depth}")
        if not isinstance(self.detector_config, DetectorConfig):
            raise ValueError("detector_config must be a DetectorConfig instance")


# ---------------------------------------------------------------------------
# BSD §18: JobManifest
# ---------------------------------------------------------------------------


@dataclass
class JobManifest:
    """
    Manifest describing a queued or completed MIIE job.

    Source: BSD-Engineering Section 18 (JobManifest)
    """

    job_id: str  # UUID4
    job_type: str  # enum: analyze, benchmark, explain, export, generate
    job_params: Dict[str, Any]
    output_dir: str
    created_at: str  # ISO 8601 UTC
    status: str  # enum: created, queued, running, completed, failed, cancelled
    progress: float = 0.0
    current_stage: Optional[str] = None
    result_paths: Dict[str, str] = field(default_factory=dict)
    error_metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate JobManifest constraints."""
        if not self.job_id:
            raise ValueError("job_id must not be empty")
        allowed_job_types = {"analyze", "benchmark", "explain", "export", "generate"}
        if self.job_type not in allowed_job_types:
            raise ValueError(f"job_type must be one of {allowed_job_types}, got {self.job_type}")
        if not self.created_at:
            raise ValueError("created_at must not be empty")
        allowed_statuses = {
            "created",
            "queued",
            "running",
            "completed",
            "failed",
            "cancelled",
        }
        if self.status not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}, got {self.status}")
        if not (0.0 <= self.progress <= 1.0):
            raise ValueError(f"progress must be between 0.0 and 1.0, got {self.progress}")


# ---------------------------------------------------------------------------
# BSD §19: StateObject
# ---------------------------------------------------------------------------


@dataclass
class StateTransition:
    """
    A single state transition in a job's lifecycle.

    Source: BSD-Engineering Section 19 (StateObject)
    """

    status: str
    timestamp: str  # ISO 8601 UTC
    stage: Optional[str] = None
    progress: float = 0.0

    def __post_init__(self):
        """Validate StateTransition constraints."""
        allowed_statuses = {
            "created",
            "queued",
            "running",
            "completed",
            "failed",
            "cancelled",
        }
        if self.status not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}, got {self.status}")
        if not self.timestamp:
            raise ValueError("timestamp must not be empty")
        if not (0.0 <= self.progress <= 1.0):
            raise ValueError(f"progress must be between 0.0 and 1.0, got {self.progress}")


@dataclass
class RecoveryMetadata:
    """
    Metadata for job recovery after failure or interruption.

    Source: BSD-Engineering Section 19 (StateObject)
    """

    last_completed_stage: Optional[str] = None
    checkpoint_path: Optional[str] = None
    retry_count: int = 0

    def __post_init__(self):
        """Validate RecoveryMetadata constraints."""
        if self.retry_count < 0:
            raise ValueError(f"retry_count must be >= 0, got {self.retry_count}")


@dataclass
class StateObject:
    """
    Persistent state object for tracking job lifecycle.

    Source: BSD-Engineering Section 19 (StateObject)
    """

    job_id: str
    current_status: str
    history: List[StateTransition]
    recovery_metadata: Optional[RecoveryMetadata] = None

    def __post_init__(self):
        """Validate StateObject constraints."""
        if not self.job_id:
            raise ValueError("job_id must not be empty")
        allowed_statuses = {
            "created",
            "queued",
            "running",
            "completed",
            "failed",
            "cancelled",
        }
        if self.current_status not in allowed_statuses:
            raise ValueError(f"current_status must be one of {allowed_statuses}, got {self.current_status}")
        for i, transition in enumerate(self.history):
            if not isinstance(transition, StateTransition):
                raise ValueError(f"history[{i}] must be a StateTransition instance")
        if self.recovery_metadata is not None and not isinstance(self.recovery_metadata, RecoveryMetadata):
            raise ValueError("recovery_metadata must be a RecoveryMetadata instance or None")


# ---------------------------------------------------------------------------
# Observation Engine v1.5 — Re-exports
# ---------------------------------------------------------------------------
# These re-exports make observation models importable from schemas.models
# for backward compatibility. The canonical definitions live in
# miie.processing.observation.models.

from miie.processing.observation.models import (  # noqa: E402, F401
    ODSS_SCHEMA_VERSION,
    Observation,
    ObservationCollection,
    ObservationProvenance,
    ObservationQuality,
    ObservationRelationship,
    ObservationStatistics,
    ObservationWindow,
    RelationshipType,
    SourceType,
    create_observation,
    generate_observation_id,
)
