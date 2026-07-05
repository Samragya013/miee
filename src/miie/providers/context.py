"""
MIIE v1.6 Observation Provider Framework — Core type definitions.

All observation provider contracts reference these types.
Implements OPC-v1.0 §2 and OPA-v1.0 §9.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Enums — Provider States (OPA §11.1)
# ---------------------------------------------------------------------------


class ProviderState(str, Enum):
    """OPA §11.1 — Provider lifecycle states."""

    UNINITIALIZED = "uninitialized"
    READY = "ready"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    DISPOSED = "disposed"


# ---------------------------------------------------------------------------
# Enums — Quality States (OVR §8)
# ---------------------------------------------------------------------------


class QualityState(str, Enum):
    """OVR §8 — Quality state machine states."""

    COMPLETE = "complete"
    DEGRADED = "degraded"
    UNCERTAIN = "uncertain"
    STALE = "stale"
    RECOVERING = "recovering"
    MISSING = "missing"


# ---------------------------------------------------------------------------
# Enums — Observation States (OPC §2.3)
# ---------------------------------------------------------------------------


class ObservationState(str, Enum):
    """OPC §2.3 — Observation lifecycle states."""

    EXTRACTED = "extracted"
    VALIDATED = "validated"
    TRANSFORMED = "transformed"
    STORED = "stored"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Enums — Priority Levels (OPR §9.4)
# ---------------------------------------------------------------------------


class PriorityLevel(int, Enum):
    """OPR §9.4 — Provider priority levels (lower = higher priority)."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


# ---------------------------------------------------------------------------
# Enums — Health Status (OPR §9.5)
# ---------------------------------------------------------------------------


class HealthStatus(str, Enum):
    """OPR §9.5 — Provider health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Enums — Extraction Phase (OPA §17.2)
# ---------------------------------------------------------------------------


class ExtractionPhase(str, Enum):
    """OPA §17.2 — Error context extraction phases."""

    HEALTH_CHECK = "health_check"
    EXTRACT = "extract"
    TRANSFORM = "transform"


# ---------------------------------------------------------------------------
# Constants — Metric IDs (ODSS §9)
# ---------------------------------------------------------------------------

VALID_METRIC_IDS: FrozenSet[str] = frozenset(f"M-{i:02d}" for i in range(1, 8))

METRIC_ID_M01: str = "M-01"
METRIC_ID_M02: str = "M-02"
METRIC_ID_M03: str = "M-03"
METRIC_ID_M04: str = "M-04"
METRIC_ID_M05: str = "M-05"
METRIC_ID_M06: str = "M-06"
METRIC_ID_M07: str = "M-07"


# ---------------------------------------------------------------------------
# Constants — Provider Capabilities (OPR §6.2)
# ---------------------------------------------------------------------------

CAPABILITY_GIT_NATIVE: str = "git-native"
CAPABILITY_API_REQUIRED: str = "api-required"
CAPABILITY_LOCAL_ONLY: str = "local-only"
CAPABILITY_REMOTE_ONLY: str = "remote-only"
CAPABILITY_REAL_TIME: str = "real-time"
CAPABILITY_BATCH: str = "batch"


# ---------------------------------------------------------------------------
# Dataclasses — Provider Context (OPA §10.1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderContext:
    """OPA §10.1 — Typed context passed to a provider during extraction.

    Derived from RepositoryContext but scoped to a single provider invocation.
    """

    repo_path: str
    repository_id: str
    analysis_id: str
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    exclude_bots: bool = False
    config: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if not self.repo_path:
            raise ValueError("repo_path must not be empty")
        if not self.repository_id:
            raise ValueError("repository_id must not be empty")
        if not self.analysis_id:
            raise ValueError("analysis_id must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


# ---------------------------------------------------------------------------
# Dataclasses — Provider Capability (OPR §6.2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderCapability:
    """OPR §6.2 — What a provider can produce.

    Declares supported metrics, source types, and optional capabilities.
    """

    supported_metrics: FrozenSet[str]
    supported_source_types: FrozenSet[str]
    capabilities: FrozenSet[str] = field(default_factory=frozenset)
    requires_network: bool = False
    requires_api_token: bool = False
    max_observations_per_batch: int = 10000

    def supports_metric(self, metric_id: str) -> bool:
        """Check if this provider supports a given metric."""
        return metric_id in self.supported_metrics

    def supports_source_type(self, source_type: str) -> bool:
        """Check if this provider supports a given source type."""
        return source_type in self.supported_source_types


# ---------------------------------------------------------------------------
# Dataclasses — Provider Health (OPR §9.5)
# ---------------------------------------------------------------------------


@dataclass
class ProviderHealth:
    """OPR §9.5 — Health snapshot reflecting a provider's current status.

    Includes health score, status, latency metrics, and error tracking.
    """

    status: HealthStatus = HealthStatus.UNKNOWN
    health_score: float = 1.0
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    total_extractions: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_message: Optional[str] = None
    last_error: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate extraction success rate."""
        if self.total_extractions == 0:
            return 1.0
        return self.successful_extractions / self.total_extractions

    @property
    def is_healthy(self) -> bool:
        """Check if provider is in a healthy state."""
        return self.status in (HealthStatus.HEALTHY, HealthStatus.DRAINING)

    @property
    def is_usable(self) -> bool:
        """Check if provider can be used for extraction."""
        return self.status in (
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNKNOWN,
        )


# ---------------------------------------------------------------------------
# Dataclasses — Metric Bounds (OVR §9.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MetricBounds:
    """OVR §9.3 — Validation bounds for a metric."""

    metric_id: str
    min_value: float
    max_value: float
    unit: str
    description: str = ""

    def validate(self, value: float) -> bool:
        """Check if a value is within bounds."""
        return self.min_value <= value <= self.max_value


# Per-metric validation bounds (OVR §9.3)
METRIC_BOUNDS: Dict[str, MetricBounds] = {
    "M-01": MetricBounds("M-01", 0.0, 1.0, "ratio", "Commit entropy ratio"),
    "M-02": MetricBounds("M-02", 0.0, float("inf"), "count", "Commit count"),
    "M-03": MetricBounds("M-03", 0.0, 1.0, "ratio", "Code churn ratio"),
    "M-04": MetricBounds("M-04", 0.0, 1.0, "ratio", "Test coverage ratio"),
    "M-05": MetricBounds("M-05", 0.0, float("inf"), "hours", "Review latency"),
    "M-06": MetricBounds("M-06", 0.0, float("inf"), "count", "File change count"),
    "M-07": MetricBounds("M-07", 0.0, 1.0, "ratio", "Branch freshness ratio"),
}


# ---------------------------------------------------------------------------
# Dataclasses — Validation Result (OPC §3.2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidationResult:
    """OPC §3.2 — Result of observation validation."""

    is_valid: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(cls) -> ValidationResult:
        """Create a successful validation result."""
        return cls(is_valid=True)

    @classmethod
    def failure(cls, violations: List[str], rule_id: Optional[str] = None) -> ValidationResult:
        """Create a failed validation result."""
        return cls(is_valid=False, violations=violations, rule_id=rule_id)

    @classmethod
    def with_warnings(cls, warnings: List[str]) -> ValidationResult:
        """Create a successful result with warnings."""
        return cls(is_valid=True, warnings=warnings)


# ---------------------------------------------------------------------------
# Dataclasses — Observation Metrics (OPC §2.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObservationMetrics:
    """OPC §2.4 — Metrics associated with an observation."""

    metric_id: str
    value: float
    unit: str
    confidence: float = 1.0
    is_estimated: bool = False

    def __post_init__(self) -> None:
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    @property
    def is_valid(self) -> bool:
        """Check if value is within metric bounds."""
        bounds = METRIC_BOUNDS.get(self.metric_id)
        if bounds is None:
            return False
        return bounds.validate(self.value)


# ---------------------------------------------------------------------------
# Dataclasses — Provider Error Context (OPA §17.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderErrorContext:
    """OPA §17.3 — Context attached to every provider error."""

    provider_id: str
    metric_id: str
    extraction_phase: ExtractionPhase
    repository_id: str
    analysis_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_type: str = ""
    error_message: str = ""


# ---------------------------------------------------------------------------
# Dataclasses — Quality State Transition (OVR §8.2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QualityStateTransition:
    """OVR §8.2 — Defines a valid quality state transition."""

    source: QualityState
    trigger: str
    target: QualityState
    description: str = ""


# Valid quality state transitions (OVR §8.2)
VALID_QUALITY_TRANSITIONS: List[QualityStateTransition] = [
    QualityStateTransition(
        QualityState.COMPLETE,
        "data_degradation",
        QualityState.DEGRADED,
        "Quality degraded due to data issues",
    ),
    QualityStateTransition(
        QualityState.DEGRADED,
        "further_degradation",
        QualityState.UNCERTAIN,
        "Quality further degraded to uncertain",
    ),
    QualityStateTransition(
        QualityState.UNCERTAIN,
        "continued_degradation",
        QualityState.STALE,
        "Quality degraded to stale",
    ),
    QualityStateTransition(
        QualityState.UNCERTAIN,
        "recovery_started",
        QualityState.RECOVERING,
        "Recovery process started",
    ),
    QualityStateTransition(
        QualityState.RECOVERING,
        "recovery_complete",
        QualityState.COMPLETE,
        "Recovery completed successfully",
    ),
    QualityStateTransition(
        QualityState.STALE,
        "data_lost",
        QualityState.MISSING,
        "Data no longer available",
    ),
    QualityStateTransition(
        QualityState.MISSING,
        "data_recovered",
        QualityState.RECOVERING,
        "Data recovered, starting recovery",
    ),
]


# ---------------------------------------------------------------------------
# Dataclasses — Provider Entry (OPR §6.3)
# ---------------------------------------------------------------------------


@dataclass
class ProviderEntry:
    """OPR §6.3 — Registry record for a provider."""

    provider_id: str
    provider: Any  # IObservationProvider instance
    capability: ProviderCapability
    priority: PriorityLevel = PriorityLevel.MEDIUM
    health: ProviderHealth = field(default_factory=ProviderHealth)
    registered_at: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id must not be empty")
        if self.registered_at is None:
            self.registered_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Dataclasses — Extraction Result (OPA §13)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExtractionResult:
    """OPA §13 — Result of provider extraction."""

    provider_id: str
    metric_id: str
    observations: Tuple[Any, ...]
    quality_state: QualityState = QualityState.COMPLETE
    confidence: float = 1.0
    extraction_time_ms: float = 0.0
    is_partial: bool = False
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def observation_count(self) -> int:
        """Return number of extracted observations."""
        return len(self.observations)

    @property
    def is_empty(self) -> bool:
        """Check if extraction produced no observations."""
        return self.observation_count == 0


# ---------------------------------------------------------------------------
# Dataclasses — Provider Registration Config (OPR §7.2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderRegistrationConfig:
    """OPR §7.2 — Configuration for provider registration."""

    provider_id: str
    provider_class: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    tags: FrozenSet[str] = field(default_factory=frozenset)
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id must not be empty")
        if not self.provider_class:
            raise ValueError("provider_class must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


# ---------------------------------------------------------------------------
# Dataclasses — Provider Factory Result (OPR §7.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderFactoryResult:
    """OPR §7.3 — Result of provider creation."""

    provider: Any  # IObservationProvider instance
    validation_result: ValidationResult
    config_warnings: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if provider was created successfully."""
        return self.validation_result.is_valid
