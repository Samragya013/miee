"""
MIIE v1.6 Scientific Metric Completion Framework — Data Models.

Defines the core data structures for metric computation, aggregation,
and result representation.

Reference: PR-12 specification.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Metric Definition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MetricDefinition:
    """Defines a metric's identity, constraints, and computation requirements.

    Attributes:
        metric_id: Canonical metric identifier (e.g. "M-01").
        name: Human-readable metric name.
        unit: Measurement unit (ratio, count, hours).
        min_value: Minimum valid value (inclusive).
        max_value: Maximum valid value (inclusive).
        description: What this metric measures.
        aggregation: How to aggregate observations ("sum" or "mean").
        required_observations: Minimum observations needed for valid computation.
        dependencies: Metric IDs this metric depends on for cross-validation.
    """

    metric_id: str
    name: str
    unit: str
    min_value: float
    max_value: float
    description: str
    aggregation: str  # "sum" or "mean"
    required_observations: int = 1
    dependencies: Tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Observation Input
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObservationInput:
    """A validated observation ready for metric computation.

    Wraps the raw Observation with pre-computed fields for efficiency.

    Attributes:
        observation_id: Unique observation identifier.
        metric_id: Which metric this observation measures.
        value: Numeric measurement value.
        unit: Unit of measurement.
        quality: Data quality level.
        source_type: Origin source type.
        source_id: Origin source identifier.
        timestamp: ISO-8601 extraction timestamp.
        provider_id: Which provider produced this observation.
        metadata: Additional context from the provider.
    """

    observation_id: str
    metric_id: str
    value: float
    unit: str
    quality: str
    source_type: str
    source_id: str
    timestamp: str
    provider_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Metric Result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MetricResult:
    """The computed result for a single metric.

    Attributes:
        metric_id: Which metric was computed.
        value: Aggregated numeric value.
        unit: Unit of the result.
        confidence: Confidence score in [0.0, 1.0].
        uncertainty: Standard deviation of contributing observations (0.0 if single).
        observation_count: Number of observations used.
        provider_count: Number of distinct providers contributing.
        quality_distribution: Count per quality level.
        computation_method: How the value was derived.
        warnings: Any warnings during computation.
        source_observation_ids: IDs of observations used.
    """

    metric_id: str
    value: float
    unit: str
    confidence: float
    uncertainty: float
    observation_count: int
    provider_count: int
    quality_distribution: Dict[str, int]
    computation_method: str
    warnings: List[str] = field(default_factory=list)
    source_observation_ids: Tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Metric Collection
# ---------------------------------------------------------------------------


@dataclass
class MetricCollection:
    """Collection of computed metric results for a repository analysis.

    Attributes:
        collection_id: Deterministic identifier.
        repository_id: Repository being analyzed.
        analysis_id: Analysis run identifier.
        results: Mapping from metric_id to MetricResult.
        overall_confidence: Weighted mean confidence across all metrics.
        coverage: Fraction of expected metrics that have results.
        computation_timestamp: When computation completed.
        warnings: Global warnings.
    """

    collection_id: str
    repository_id: str
    analysis_id: str
    results: Dict[str, MetricResult] = field(default_factory=dict)
    overall_confidence: float = 0.0
    coverage: float = 0.0
    computation_timestamp: str = ""
    warnings: List[str] = field(default_factory=list)

    @property
    def metric_ids(self) -> List[str]:
        """Sorted list of computed metric IDs."""
        return sorted(self.results.keys())

    @property
    def metric_count(self) -> int:
        """Number of computed metrics."""
        return len(self.results)

    def get_result(self, metric_id: str) -> Optional[MetricResult]:
        """Get result for a specific metric."""
        return self.results.get(metric_id)

    def has_metric(self, metric_id: str) -> bool:
        """Check if a metric has been computed."""
        return metric_id in self.results

    def confidence_by_metric(self) -> Dict[str, float]:
        """Return confidence scores per metric."""
        return {mid: r.confidence for mid, r in self.results.items()}


# ---------------------------------------------------------------------------
# Computation Diagnostics
# ---------------------------------------------------------------------------


@dataclass
class ComputationDiagnostics:
    """Diagnostics produced during metric computation.

    Attributes:
        total_observations_processed: Total input observations.
        observations_by_metric: Per-metric observation counts.
        observations_by_provider: Per-provider observation counts.
        validation_failures: Observations that failed validation.
        computation_times_ms: Per-metric computation time in milliseconds.
        dependency_graph: Metric dependency edges.
        overall_confidence: Aggregate confidence.
        warnings: All warnings generated.
    """

    total_observations_processed: int = 0
    observations_by_metric: Dict[str, int] = field(default_factory=dict)
    observations_by_provider: Dict[str, int] = field(default_factory=dict)
    validation_failures: List[str] = field(default_factory=list)
    computation_times_ms: Dict[str, float] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    overall_confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating observations or metric results.

    Attributes:
        is_valid: Whether validation passed.
        errors: List of validation error messages.
        warnings: List of validation warnings.
        checked_count: Number of items validated.
        passed_count: Number of items that passed.
    """

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checked_count: int = 0
    passed_count: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EXPECTED_METRIC_IDS = tuple(f"M-{i:02d}" for i in range(1, 8))


def generate_metric_collection_id(
    repository_id: str,
    analysis_id: str,
) -> str:
    """Generate a deterministic metric collection ID.

    Args:
        repository_id: Repository identifier.
        analysis_id: Analysis run identifier.

    Returns:
        16-character hex string.
    """
    raw = f"metric-collection:{repository_id}:{analysis_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
