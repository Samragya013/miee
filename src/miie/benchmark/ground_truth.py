"""
MIIE v1.6 — Ground Truth Dataset Framework

Defines the core data models for ground truth datasets used in benchmark
validation. These models formalise the dataset schema, lifecycle, and
metadata structure required for scientific reproducibility.

Resolves SDV Critical Finding CF-03 (G-09: No ground truth datasets).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DatasetType(str, Enum):
    """Classification of ground truth datasets."""

    SYNTHETIC = "synthetic"
    REAL = "real"
    ADVERSARIAL = "adversarial"


class DatasetStatus(str, Enum):
    """Lifecycle status of a ground truth dataset."""

    DRAFT = "draft"
    VALIDATED = "validated"
    CERTIFIED = "certified"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class RepositoryClassification(str, Enum):
    """Canonical repository classification categories."""

    HEALTHY = "healthy"
    ARCHIVED = "archived"
    FAST_GROWTH = "fast-growth"
    ENTERPRISE = "enterprise"
    EXPERIMENTAL = "experimental"
    FORK = "fork"
    HIGH_RISK = "high-risk"
    SYNTHETIC = "synthetic"
    DETECTOR_CHALLENGE = "detector-challenge"
    METRIC_VALIDATION = "metric-validation"


class AnomalyType(str, Enum):
    """Types of anomalies that can be present in datasets."""

    METRIC_DRIFT = "metric-drift"
    CORRELATION_BREAKDOWN = "correlation-breakdown"
    THRESHOLD_COMPRESSION = "threshold-compression"
    SEASONAL = "seasonal"
    GAMING = "gaming"
    PROCESS_DECAY = "process-decay"


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DetectorID(str, Enum):
    """Detector identifiers."""

    D01 = "D-01"
    D02 = "D-02"
    D03 = "D-03"


class MetricID(str, Enum):
    """Metric identifiers."""

    M01 = "M-01"
    M02 = "M-02"
    M03 = "M-03"
    M04 = "M-04"
    M05 = "M-05"
    M06 = "M-06"
    M07 = "M-07"


class TrendType(str, Enum):
    """Expected trend types for metric values."""

    STABLE = "stable"
    INCREASING = "increasing"
    DECREASING = "decreasing"
    SHIFT = "shift"
    PERIODIC = "periodic"


@dataclass(frozen=True)
class Provenance:
    """Dataset provenance information."""

    source: str
    methodology: str
    reproducibility: str
    tools: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    parent_dataset: Optional[str] = None


@dataclass(frozen=True)
class DetectorOutput:
    """Expected output for a single detector."""

    detected: bool
    severity: AnomalySeverity = AnomalySeverity.NONE
    p_value_max: Optional[float] = None
    confidence_min: Optional[float] = None


@dataclass(frozen=True)
class ExpectedScores:
    """Expected scoring outputs."""

    integrity_score_range: Optional[tuple[float, float]] = None
    confidence_score_range: Optional[tuple[float, float]] = None


@dataclass(frozen=True)
class GroundTruth:
    """Complete ground truth specification for a dataset."""

    anomaly_present: bool
    expected_detector_outputs: Dict[DetectorID, DetectorOutput]
    expected_metric_values: Dict[MetricID, Dict[str, Any]]
    expected_scores: ExpectedScores
    anomaly_type: Optional[AnomalyType] = None
    anomaly_severity: AnomalySeverity = AnomalySeverity.NONE
    anomaly_window_start: Optional[int] = None
    anomaly_window_end: Optional[int] = None


@dataclass(frozen=True)
class AcceptanceCriteria:
    """Acceptance criteria for benchmark validation."""

    d01_sensitivity_min: Optional[float] = None
    d01_specificity_min: Optional[float] = None
    d02_sensitivity_min: Optional[float] = None
    d02_specificity_min: Optional[float] = None
    d03_sensitivity_min: Optional[float] = None
    d03_specificity_min: Optional[float] = None
    metric_computation_tolerance: float = 0.01
    determinism_required: bool = True


@dataclass(frozen=True)
class Versioning:
    """Dataset versioning information."""

    changelog: List[str]
    compatibility: str = "backward-compatible"
    supersedes: Optional[str] = None


@dataclass(frozen=True)
class Certification:
    """Dataset certification information."""

    certified_by: str
    criteria: str
    certified_at: Optional[datetime] = None
    certificate_id: Optional[str] = None


@dataclass(frozen=True)
class Licensing:
    """Dataset licensing information."""

    license: str = "MIT"
    attribution: Optional[str] = None
    usage_restrictions: Optional[str] = None


@dataclass(frozen=True)
class GroundTruthDataset:
    """Complete ground truth dataset model.

    This is the primary data structure for MIIE ground truth datasets.
    It encapsulates all metadata, provenance, ground truth labels,
    acceptance criteria, versioning, certification, and licensing.

    Attributes:
        dataset_id: Unique identifier (e.g., 'GT-SYN-DRIFT-001')
        dataset_name: Human-readable name
        dataset_version: Semantic version (e.g., '1.0.0')
        dataset_type: Dataset type classification
        status: Lifecycle status
        created_by: Creator identifier
        created_at: Creation timestamp
        description: Dataset description
        repository_classification: Repository classification category
        provenance: Dataset provenance
        ground_truth: Ground truth specification
        acceptance_criteria: Acceptance criteria
        versioning: Versioning information
        certification: Certification information
        licensing: Licensing information
        language: Primary programming language
        commit_count: Number of commits
        contributor_count: Number of contributors
        time_span_days: Time span in days
        tags: Searchable tags
    """

    dataset_id: str
    dataset_name: str
    dataset_version: str
    dataset_type: DatasetType
    status: DatasetStatus
    created_by: str
    created_at: datetime
    description: str
    repository_classification: RepositoryClassification
    provenance: Provenance
    ground_truth: GroundTruth
    acceptance_criteria: AcceptanceCriteria
    versioning: Versioning
    certification: Certification
    licensing: Licensing
    language: str = "python"
    commit_count: int = 0
    contributor_count: int = 0
    time_span_days: int = 0
    tags: List[str] = field(default_factory=list)

    def is_certified(self) -> bool:
        """Check if dataset is certified for benchmarking."""
        return self.status in (
            DatasetStatus.CERTIFIED,
            DatasetStatus.PUBLISHED,
        )

    def is_usable(self) -> bool:
        """Check if dataset can be used for benchmarking."""
        return self.status != DatasetStatus.DEPRECATED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialisation."""
        return {
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "dataset_version": self.dataset_version,
            "dataset_type": self.dataset_type.value,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "repository_classification": self.repository_classification.value,
            "language": self.language,
            "commit_count": self.commit_count,
            "contributor_count": self.contributor_count,
            "time_span_days": self.time_span_days,
            "tags": self.tags,
            "provenance": {
                "source": self.provenance.source,
                "methodology": self.provenance.methodology,
                "tools": self.provenance.tools,
                "parameters": self.provenance.parameters,
                "reproducibility": self.provenance.reproducibility,
                "parent_dataset": self.provenance.parent_dataset,
            },
            "ground_truth": {
                "anomaly_present": self.ground_truth.anomaly_present,
                "anomaly_type": (
                    self.ground_truth.anomaly_type.value
                    if self.ground_truth.anomaly_type
                    else None
                ),
                "anomaly_severity": self.ground_truth.anomaly_severity.value,
                "anomaly_window_start": self.ground_truth.anomaly_window_start,
                "anomaly_window_end": self.ground_truth.anomaly_window_end,
                "expected_detector_outputs": {
                    det_id.value: {
                        "detected": out.detected,
                        "severity": out.severity.value,
                        "p_value_max": out.p_value_max,
                        "confidence_min": out.confidence_min,
                    }
                    for det_id, out in self.ground_truth.expected_detector_outputs.items()
                },
                "expected_metric_values": {
                    met_id.value: vals
                    for met_id, vals in self.ground_truth.expected_metric_values.items()
                },
                "expected_scores": {
                    "integrity_score_range": (
                        list(self.ground_truth.expected_scores.integrity_score_range)
                        if self.ground_truth.expected_scores.integrity_score_range
                        else None
                    ),
                    "confidence_score_range": (
                        list(self.ground_truth.expected_scores.confidence_score_range)
                        if self.ground_truth.expected_scores.confidence_score_range
                        else None
                    ),
                },
            },
            "acceptance_criteria": {
                "d01_sensitivity_min": self.acceptance_criteria.d01_sensitivity_min,
                "d01_specificity_min": self.acceptance_criteria.d01_specificity_min,
                "d02_sensitivity_min": self.acceptance_criteria.d02_sensitivity_min,
                "d02_specificity_min": self.acceptance_criteria.d02_specificity_min,
                "d03_sensitivity_min": self.acceptance_criteria.d03_sensitivity_min,
                "d03_specificity_min": self.acceptance_criteria.d03_specificity_min,
                "metric_computation_tolerance": self.acceptance_criteria.metric_computation_tolerance,
                "determinism_required": self.acceptance_criteria.determinism_required,
            },
            "versioning": {
                "changelog": self.versioning.changelog,
                "compatibility": self.versioning.compatibility,
                "supersedes": self.versioning.supersedes,
            },
            "certification": {
                "certified_by": self.certification.certified_by,
                "certified_at": (
                    self.certification.certified_at.isoformat()
                    if self.certification.certified_at
                    else None
                ),
                "criteria": self.certification.criteria,
                "certificate_id": self.certification.certificate_id,
            },
            "licensing": {
                "license": self.licensing.license,
                "attribution": self.licensing.attribution,
                "usage_restrictions": self.licensing.usage_restrictions,
            },
        }


@dataclass(frozen=True)
class GroundTruthEntry:
    """Individual ground truth entry for a specific window.

    Used to provide per-window ground truth labels within a dataset.

    Attributes:
        entry_id: Unique entry identifier
        dataset_id: Parent dataset identifier
        window_index: Window index
        expected_values: Expected metric/detector/score values
        annotations: Expert annotations
        confidence: Confidence in ground truth
        source: Source of ground truth
    """

    entry_id: str
    dataset_id: str
    window_index: int
    expected_values: Dict[str, Any]
    annotations: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    source: str = "automated"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialisation."""
        return {
            "entry_id": self.entry_id,
            "dataset_id": self.dataset_id,
            "window_index": self.window_index,
            "expected_values": self.expected_values,
            "annotations": self.annotations,
            "confidence": self.confidence,
            "source": self.source,
        }
