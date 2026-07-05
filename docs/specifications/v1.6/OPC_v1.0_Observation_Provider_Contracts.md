# Observation Provider Contracts (OPC) v1.0

**Specification:** OPC v1.0  
**MIIE Version:** 1.6  
**Status:** Draft  
**Author:** MIIE Engineering  
**Last Updated:** 2026-07-03  

---

## 1. Purpose and Scope

### 1.1 Purpose

This document specifies the typed Protocol interfaces (contracts) that every observation provider must implement to participate in the MIIE v1.6 observation pipeline. The Observation Provider Contracts (OPC) define the boundary between external metric sources and the internal Observation Source Management System (OSMS).

### 1.2 Scope

The OPC covers:

- **IObservationProvider** — core contract for producing observations from external sources
- **IObservationValidator** — contract for validating observations against OSMS rules
- **IObservationTransformer** — contract for transforming raw observations into detector-consumable format
- **IProviderHealthReporter** — contract for reporting provider health status and telemetry
- **IProviderRegistry** — contract for registering, discovering, and managing provider lifecycle
- **Error handling contracts** — typed error hierarchy for provider failures
- **Backward compatibility** — relationship to existing interfaces (INT-01 through INT-18)

### 1.3 Non-Goals

This document does not define:

- Internal observation storage or persistence (see OPA v1.0)
- Observation routing or scheduling (see OPR v1.0)
- The OSMS configuration schema (see OSMS v1.0)
- Specific provider implementations

---

## 2. Interface Hierarchy and Relationships

### 2.1 Dependency Graph

```
IProviderRegistry
  ├── registers IObservationProvider instances
  ├── queries IProviderHealthReporter for status
  └── coordinates IObservationValidator and IObservationTransformer

IObservationProvider
  ├── produces ObservationCollection
  ├── implements IProviderHealthReporter
  └── consumes RepositoryContext

IObservationValidator
  ├── consumes Observation (single)
  ├── produces ValidationResult
  └── composable with other validators

IObservationTransformer
  ├── consumes Observation (raw)
  ├── produces Observation (transformed)
  └── preserves provenance chain

IProviderHealthReporter
  ├── produces HealthStatus
  ├── produces LatencyMetrics
  └── produces ConfidenceMetrics
```

### 2.2 Relationship to Existing Interfaces

The OPC interfaces extend the existing MIIE contract system (INT-01 through INT-18) without breaking backward compatibility. The existing interfaces are consumed downstream of the observation pipeline:

```
External Source
  ↓
IObservationProvider  ← OPC v1.0
  ↓
IObservationValidator  ← OPC v1.0
  ↓
IObservationTransformer  ← OPC v1.0
  ↓
IExtractor (INT-01)
  ↓
IDetector (INT-02)
  ↓
IScorer (INT-03)
  ↓
... (remaining INT interfaces)
```

### 2.3 Type Dependencies

All OPC interfaces depend on the following types defined in `src/miie/contracts/types.py`:

| Type | Source | Description |
|------|--------|-------------|
| `Observation` | OSMS v1.0 | Single metric observation with value, quality, and provenance |
| `ObservationCollection` | OSMS v1.0 | Ordered collection of observations with metadata |
| `RepositoryContext` | INT-XX | Context providing repository access and configuration |
| `MetricId` | OSMS v1.0 | Unique metric identifier (e.g., `"commit_frequency"`) |
| `QualityState` | OSMS v1.0 | Quality classification: `VALID`, `ESTIMATED`, `MISSING`, `STALE` |
| `Provenance` | OSMS v1.0 | Source attribution chain for an observation |
| `WindowDefinition` | INT-06 | Temporal or event-based window specification |

---

## 3. IObservationProvider — Core Contract

### 3.1 Overview

`IObservationProvider` is the primary interface for the observation pipeline. Every external metric source (version control, CI/CD, issue tracker, etc.) must implement this interface to provide observations to MIIE.

### 3.2 Protocol Definition

```python
from __future__ import annotations
from abc import abstractmethod
from typing import Protocol, runtime_checkable
from datetime import datetime
from enum import Enum


class ProviderCapability(Enum):
    """Capabilities a provider can declare."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    HISTORICAL = "historical"
    STREAMING = "streaming"


class ProviderPriority(Enum):
    """Priority levels for provider selection."""
    PRIMARY = "primary"
    FALLBACK = "fallback"
    AUXILIARY = "auxiliary"


@runtime_checkable
class IObservationProvider(Protocol):
    """
    Core contract for producing observations from external sources.

    Every observation provider must implement this interface to participate
    in the MIIE observation pipeline. Providers are registered with the
    IProviderRegistry and invoked by the OSMS scheduler.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """
        Unique identifier for this provider.

        Must be stable across restarts. Used as the key in the
        IProviderRegistry. Format: "{source_type}.{source_name}",
        e.g., "git.github", "jira.cloud", "jenkins.primary".
        """
        ...

    @property
    @abstractmethod
    def metric_ids(self) -> frozenset[MetricId]:
        """
        Set of metric IDs this provider can supply.

        Used by IProviderRegistry to resolve which provider(s) to invoke
        for a given metric request. Must not be empty.
        """
        ...

    @property
    @abstractmethod
    def capabilities(self) -> frozenset[ProviderCapability]:
        """
        Declared capabilities of this provider.

        Determines how the OSMS scheduler interacts with this provider
        (e.g., whether it supports real-time queries or only batch).
        """
        ...

    @property
    @abstractmethod
    def priority(self) -> ProviderPriority:
        """
        Provider priority for metric resolution.

        When multiple providers supply the same metric, PRIMARY providers
        are preferred. FALLBACK providers are used when PRIMARY fails.
        AUXILIARY providers supplement but never replace.
        """
        ...

    @abstractmethod
    async def collect(
        self,
        metric_id: MetricId,
        context: RepositoryContext,
        window: WindowDefinition,
        options: ObservationOptions | None = None,
    ) -> ObservationCollection:
        """
        Collect observations for a given metric within a time window.

        Args:
            metric_id: The metric to collect.
            context: Repository context providing access to data sources.
            window: Temporal or event-based window for the observation.
            options: Optional collection parameters (timeout, retries, etc.).

        Returns:
            ObservationCollection containing zero or more observations.

        Raises:
            ProviderError: On unrecoverable failure.
            ProviderTimeoutError: If collection exceeds timeout.
            ProviderAuthError: If authentication fails.
            MetricNotSupportedError: If metric_id is not in self.metric_ids.

        The provider MUST NOT raise uncaught exceptions. All errors must be
        typed and recoverable. The pipeline continues with degraded data
        on provider failure.
        """
        ...

    @abstractmethod
    def can_provide(self, metric_id: MetricId) -> bool:
        """
        Check if this provider can supply a given metric.

        Used for fast-path resolution in IProviderRegistry. Must return
        the same answer as `metric_id in self.metric_ids` but avoids
        materializing the full set for large providers.
        """
        ...

    @abstractmethod
    async def initialize(self, config: ProviderConfig) -> None:
        """
        Initialize the provider with configuration.

        Called once after registration, before any collect() calls.
        Must not make external network calls during initialization.
        Use a lazy-init pattern for connections.
        """
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Gracefully shut down the provider.

        Release any held resources (connections, file handles, caches).
        The pipeline calls this during shutdown or when a provider is
        deregistered. Must complete within 5 seconds.
        """
        ...
```

### 3.3 Supporting Types

```python
@dataclass(frozen=True)
class ObservationOptions:
    """
    Options controlling provider collection behavior.
    """
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    include_estimated: bool = True
    quality_threshold: float = 0.0
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderConfig:
    """
    Configuration for provider initialization.

    Providers receive this during initialize() and must validate
    all required fields. Unknown fields are ignored (forward-compatible).
    """
    provider_id: str
    source_url: str
    auth_token: str | None = None
    auth_token_env_var: str | None = None
    api_version: str = "v1"
    rate_limit_rpm: int = 60
    cache_ttl_seconds: int = 300
    extra: dict[str, Any] | None = None
```

### 3.4 Behavioral Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| OPC-PROV-01 | `provider_id` must be unique across all registered providers | Prevents registry collisions |
| OPC-PROV-02 | `metric_ids` must be non-empty | A provider with no metrics is useless |
| OPC-PROV-03 | `collect()` must complete within `timeout_seconds` or raise `ProviderTimeoutError` | Prevents pipeline stalls |
| OPC-PROV-04 | `collect()` must return `ObservationCollection` even on partial failure | Pipeline continues with degraded data |
| OPC-PROV-05 | `collect()` must populate `Observation.provenance` with provider attribution | Enables traceability |
| OPC-PROV-06 | `initialize()` must not make network calls | Prevents slow startup |
| OPC-PROV-07 | `shutdown()` must complete within 5 seconds | Prevents pipeline hang on teardown |
| OPC-PROV-08 | `can_provide()` must be pure (no side effects) | Called frequently for routing decisions |
| OPC-PROV-09 | Provider must not raise uncaught exceptions from `collect()` | Pipeline stability |

---

## 4. IObservationValidator — Validation Contract

### 4.1 Overview

`IObservationValidator` validates individual observations against OSMS rules. Validators are composable — multiple validators can run on the same observation, and each produces an independent `ValidationResult`.

### 4.2 Protocol Definition

```python
@runtime_checkable
class IObservationValidator(Protocol):
    """
    Contract for validating observations against OSMS rules.

    Validators are composable. Multiple validators may run on the same
    observation, and the IProviderRegistry aggregates their results.
    A validation failure does not necessarily reject an observation;
    it downgrades the QualityState based on OSMS policy.
    """

    @property
    @abstractmethod
    def validator_id(self) -> str:
        """Unique identifier for this validator."""
        ...

    @property
    @abstractmethod
    def validation_rules(self) -> frozenset[str]:
        """
        Set of rule IDs this validator enforces.

        Used for observability and debugging. E.g., {"RANGE_CHECK",
        "TEMPORAL_CONSISTENCY", "SCHEMA_VALIDITY"}.
        """
        ...

    @abstractmethod
    def validate(
        self,
        observation: Observation,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """
        Validate a single observation.

        Args:
            observation: The observation to validate.
            context: Optional context (e.g., historical observations for
                     temporal checks, metric schema for range checks).

        Returns:
            ValidationResult indicating pass/fail with reasons.

        This is a synchronous operation. Validation must not make network
        calls or perform I/O. It operates on data already collected.
        """
        ...

    @abstractmethod
    def validate_batch(
        self,
        observations: Sequence[Observation],
        context: ValidationContext | None = None,
    ) -> list[ValidationResult]:
        """
        Validate a batch of observations.

        Default implementation calls validate() per observation. Override
        for batch-optimized validation (e.g., temporal consistency checks
        across a sequence).

        Args:
            observations: Sequence of observations to validate.
            context: Optional validation context.

        Returns:
            List of ValidationResult, one per input observation.
        """
        ...

    def validate_batch_default(
        self,
        observations: Sequence[Observation],
        context: ValidationContext | None = None,
    ) -> list[ValidationResult]:
        """Default batch validation: delegates to validate() per item."""
        return [self.validate(obs, context) for obs in observations]
```

### 4.3 Supporting Types

```python
class ValidationSeverity(Enum):
    """Severity levels for validation failures."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationFailure(Enum):
    """Typed validation failure reasons."""
    VALUE_OUT_OF_RANGE = "value_out_of_range"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    TEMPORAL_GAP = "temporal_gap"
    DUPLICATE_TIMESTAMP = "duplicate_timestamp"
    SCHEMA_VIOLATION = "schema_violation"
    PROVENANCE_MISSING = "provenance_missing"
    QUALITY_STATE_INCONSISTENT = "quality_state_inconsistent"
    DEPENDENCY_MISSING = "dependency_missing"


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating a single observation.
    """
    observation_id: str
    is_valid: bool
    severity: ValidationSeverity
    failures: tuple[ValidationFailure, ...]
    messages: tuple[str, ...]
    suggested_quality_state: QualityState
    validator_id: str
    rule_ids: frozenset[str]


@dataclass(frozen=True)
class ValidationContext:
    """
    Context for validation operations.
    """
    metric_schema: dict[str, Any] | None = None
    historical_observations: Sequence[Observation] | None = None
    quality_policy: QualityPolicy | None = None
    timestamp_tolerance_seconds: float = 60.0
```

### 4.4 Behavioral Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| OPC-VAL-01 | `validate()` must be synchronous (no I/O) | Validation is fast-path |
| OPC-VAL-02 | `validate()` must never raise exceptions | All outcomes encoded in ValidationResult |
| OPC-VAL-03 | `validate_batch()` must produce results in input order | Simplifies aggregation |
| OPC-VAL-04 | Validator must not mutate the input Observation | Immutable data contract |
| OPC-VAL-05 | `suggested_quality_state` must be one of the QualityState enum values | Deterministic state transitions |
| OPC-VAL-06 | Composing validators must not produce conflicting `suggested_quality_state` | IProviderRegistry resolves conflicts |

---

## 5. IObservationTransformer — Transformation Contract

### 5.1 Overview

`IObservationTransformer` converts raw observations from external sources into the internal `Observation` format consumed by detectors (INT-02). Transformers handle quality state transitions (e.g., MISSING → ESTIMATED when interpolation is applicable) and must preserve the full provenance chain.

### 5.2 Protocol Definition

```python
@runtime_checkable
class IObservationTransformer(Protocol):
    """
    Contract for transforming raw observations into detector-consumable format.

    Transformers handle:
    - Unit conversion (e.g., hours → seconds)
    - Quality state transitions (MISSING → ESTIMATED)
    - Provenance chain preservation
    - Derived metric computation
    - Schema normalization
    """

    @property
    @abstractmethod
    def transformer_id(self) -> str:
        """Unique identifier for this transformer."""
        ...

    @property
    @abstractmethod
    def source_metric_ids(self) -> frozenset[MetricId]:
        """
        Metric IDs this transformer accepts as input.

        The transformer only processes observations whose metric_id
        is in this set.
        """
        ...

    @property
    @abstractmethod
    def target_metric_ids(self) -> frozenset[MetricId]:
        """
        Metric IDs this transformer produces as output.

        After transformation, observations have their metric_id
        replaced with a value from this set.
        """
        ...

    @abstractmethod
    def transform(
        self,
        observation: Observation,
        context: TransformationContext | None = None,
    ) -> Observation:
        """
        Transform a single raw observation into detector format.

        Args:
            observation: The raw observation to transform.
            context: Optional context (e.g., schema definitions,
                     transformation parameters).

        Returns:
            Transformed Observation with updated quality_state,
            provenance, and metric_id as needed.

        The transformed observation MUST:
        - Preserve the original Observation.id in provenance.source_id
        - Append this transformer's identity to provenance.chain
        - Set quality_state appropriately (see Quality State Transitions)
        - Not produce an observation with QualityState.MISSING unless
          the input was already MISSING and no estimation is possible

        Raises:
            TransformationError: If transformation is not possible.
            The caller must catch this and pass the observation through
            unchanged (graceful degradation).
        """
        ...

    @abstractmethod
    def transform_batch(
        self,
        observations: Sequence[Observation],
        context: TransformationContext | None = None,
    ) -> list[Observation]:
        """
        Transform a batch of observations.

        Default implementation calls transform() per observation.
        Override for batch-optimized transformations (e.g., interpolation
        across a time series).

        Args:
            observations: Sequence of raw observations.
            context: Optional transformation context.

        Returns:
            List of transformed observations. Length matches input length.
        """
        ...

    @abstractmethod
    def can_transform(self, metric_id: MetricId) -> bool:
        """
        Check if this transformer handles a given metric.

        Must be pure and fast. Called frequently for routing.
        """
        ...

    def transform_batch_default(
        self,
        observations: Sequence[Observation],
        context: TransformationContext | None = None,
    ) -> list[Observation]:
        """Default batch transformation: delegates to transform() per item."""
        return [self.transform(obs, context) for obs in observations]
```

### 5.3 Supporting Types

```python
@dataclass(frozen=True)
class TransformationContext:
    """
    Context for transformation operations.
    """
    source_schema: dict[str, Any] | None = None
    target_schema: dict[str, Any] | None = None
    interpolation_method: str | None = None
    estimation_confidence_threshold: float = 0.7
    extra: dict[str, Any] | None = None
```

### 5.4 Quality State Transitions

Transformers may trigger the following quality state transitions:

| Current State | Transition To | Condition |
|---------------|---------------|-----------|
| `VALID` | `VALID` | Transformation preserves validity |
| `VALID` | `ESTIMATED` | Transformation requires interpolation |
| `MISSING` | `ESTIMATED` | Interpolation available and confidence ≥ threshold |
| `MISSING` | `MISSING` | No interpolation available |
| `STALE` | `ESTIMATED` | Fresh data available after transformation |
| `STALE` | `STALE` | No fresh data available |

Transformers MUST NOT transition `VALID` → `MISSING`. If a transformation cannot preserve validity, it must produce `ESTIMATED` with appropriate confidence metadata.

### 5.5 Provenance Preservation

Every transformed observation must maintain an unbroken provenance chain:

```python
@dataclass(frozen=True)
class ProvenanceChain:
    """
    Immutable provenance chain for an observation.
    """
    source_id: str                          # Original observation ID
    chain: tuple[ProvenanceStep, ...]       # Ordered transformation steps


@dataclass(frozen=True)
class ProvenanceStep:
    """
    A single step in the provenance chain.
    """
    transformer_id: str
    timestamp: datetime
    input_metric_id: MetricId
    output_metric_id: MetricId
    quality_state_before: QualityState
    quality_state_after: QualityState
```

### 5.6 Behavioral Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| OPC-XFR-01 | `transform()` must preserve original observation ID in provenance | Traceability |
| OPC-XFR-02 | `transform()` must append to provenance.chain, not replace | Complete transformation history |
| OPC-XFR-03 | `transform()` must not produce `MISSING` from non-`MISSING` input | Degrades data quality unnecessarily |
| OPC-XFR-04 | `transform_batch()` must return observations in input order | Simplifies downstream processing |
| OPC-XFR-05 | Transformation must be deterministic for same input + context | Reproducibility |
| OPC-XFR-06 | Transformer must not mutate the input Observation | Immutable data contract |
| OPC-XFR-07 | `TransformationError` must include the original observation | Enables pass-through fallback |

---

## 6. IProviderHealthReporter — Health Reporting Contract

### 6.1 Overview

`IProviderHealthReporter` provides health status, latency metrics, and confidence metrics for a provider. This is a mixin interface — `IObservationProvider` instances also implement `IProviderHealthReporter`.

### 6.2 Protocol Definition

```python
class ProviderHealthStatus(Enum):
    """Provider health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@runtime_checkable
class IProviderHealthReporter(Protocol):
    """
    Contract for reporting provider health and telemetry.

    Providers implement this to expose operational metrics. The
    IProviderRegistry queries health status during provider resolution
    to avoid routing to unhealthy providers.
    """

    @property
    @abstractmethod
    def health_status(self) -> ProviderHealthStatus:
        """
        Current health status of this provider.

        Status transitions:
        - HEALTHY → DEGRADED: when error rate > 10% or p99 latency > threshold
        - DEGRADED → UNHEALTHY: when error rate > 50% or consecutive failures > 5
        - Any → HEALTHY: when error rate < 5% and consecutive successes > 10
        - UNHEALTHY → UNKNOWN: when provider is restarted

        The provider tracks these internally; the registry polls this property.
        """
        ...

    @property
    @abstractmethod
    def latency_metrics(self) -> LatencyMetrics:
        """
        Latency metrics for this provider.

        Updated after each collect() call. The registry uses these for
        timeout calibration and provider selection.
        """
        ...

    @property
    @abstractmethod
    def confidence_metrics(self) -> ConfidenceMetrics:
        """
        Confidence metrics for this provider's observations.

        Tracks how confident the provider is in its data quality.
        Used by the scoring pipeline (INT-03) for weighting.
        """
        ...

    @abstractmethod
    def record_success(self, latency_ms: float, observation_count: int) -> None:
        """
        Record a successful collection.

        Called by the pipeline after a successful collect(). Updates
        internal health state and metrics.

        Args:
            latency_ms: Collection latency in milliseconds.
            observation_count: Number of observations collected.
        """
        ...

    @abstractmethod
    def record_failure(self, error: ProviderError, latency_ms: float) -> None:
        """
        Record a failed collection attempt.

        Called by the pipeline after a failed collect(). Updates
        internal health state and metrics.

        Args:
            error: The typed error that caused the failure.
            latency_ms: Time elapsed before failure, in milliseconds.
        """
        ...

    @abstractmethod
    def register_health_check(
        self,
        callback: HealthCheckCallback,
        interval_seconds: float = 60.0,
    ) -> str:
        """
        Register a health check callback.

        The provider calls registered callbacks at the specified interval.
        Used for external health monitoring integration (e.g., Kubernetes
        liveness probes).

        Args:
            callback: Function to call on health check.
            interval_seconds: Minimum interval between checks.

        Returns:
            Registration ID for deregistration.
        """
        ...

    @abstractmethod
    def deregister_health_check(self, registration_id: str) -> None:
        """
        Deregister a previously registered health check callback.
        """
        ...
```

### 6.3 Supporting Types

```python
@dataclass(frozen=True)
class LatencyMetrics:
    """
    Latency metrics for a provider, updated after each collection.
    """
    p50_ms: float
    p90_ms: float
    p99_ms: float
    max_ms: float
    total_collections: int
    last_collection_timestamp: datetime | None = None


@dataclass(frozen=True)
class ConfidenceMetrics:
    """
    Confidence metrics for provider data quality.
    """
    mean_confidence: float           # [0.0, 1.0]
    min_confidence: float            # [0.0, 1.0]
    confidence_distribution: dict[str, float]  # histogram buckets
    estimated_observation_ratio: float  # fraction of ESTIMATED observations
    total_observations: int


@dataclass(frozen=True)
class HealthCheckCallback:
    """
    Callback signature for health checks.
    """
    __call__: Callable[[ProviderHealthStatus, LatencyMetrics], None]
```

### 6.4 Behavioral Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| OPC-HLT-01 | `health_status` must be computed from recent metrics, not cached stale | Accurate health picture |
| OPC-HLT-02 | `record_success()` and `record_failure()` must be thread-safe | Pipeline may call concurrently |
| OPC-HLT-03 | Latency metrics must use exponential moving average for smoothing | Prevents metric oscillation |
| OPC-HLT-04 | `register_health_check()` must not fail | Health monitoring is critical |
| OPC-HLT-05 | Provider must transition to UNHEALTHY after 5 consecutive failures | Prevents routing to broken providers |

---

## 7. IProviderRegistry — Registry Contract

### 7.1 Overview

`IProviderRegistry` manages the lifecycle and resolution of observation providers. It is the single source of truth for which providers are available, their health status, and their metric coverage.

### 7.2 Protocol Definition

```python
@runtime_checkable
class IProviderRegistry(Protocol):
    """
    Contract for managing observation provider lifecycle and resolution.

    The registry:
    - Registers and deregisters providers
    - Resolves providers for metric requests
    - Manages provider lifecycle (start/stop/restart)
    - Coordinates validators and transformers
    - Handles provider prioritization and fallback
    """

    @abstractmethod
    async def register(
        self,
        provider: IObservationProvider,
        validators: Sequence[IObservationValidator] | None = None,
        transformers: Sequence[IObservationTransformer] | None = None,
    ) -> RegistrationResult:
        """
        Register a provider with optional validators and transformers.

        Args:
            provider: The provider to register.
            validators: Optional validators to apply to this provider's output.
            transformers: Optional transformers to apply before validation.

        Returns:
            RegistrationResult with registration status and assigned ID.

        Raises:
            ProviderAlreadyRegisteredError: If provider_id already registered.
            ValidationError: If provider fails validation checks.
        """
        ...

    @abstractmethod
    async def deregister(self, provider_id: str) -> None:
        """
        Deregister a provider and release its resources.

        Calls provider.shutdown() before deregistration.
        """
        ...

    @abstractmethod
    async def resolve(
        self,
        metric_id: MetricId,
        context: RepositoryContext,
        window: WindowDefinition,
    ) -> ProviderResolution:
        """
        Resolve which provider(s) to use for a metric request.

        Resolution order:
        1. Filter by can_provide(metric_id)
        2. Filter by health_status != UNHEALTHY
        3. Sort by priority (PRIMARY > FALLBACK > AUXILIARY)
        4. Filter by window compatibility
        5. Select best provider

        Args:
            metric_id: The metric to resolve.
            context: Repository context for provider filtering.
            window: Window definition for compatibility check.

        Returns:
            ProviderResolution with selected provider(s) and fallback chain.
        """
        ...

    @abstractmethod
    async def collect(
        self,
        metric_id: MetricId,
        context: RepositoryContext,
        window: WindowDefinition,
        options: ObservationOptions | None = None,
    ) -> ObservationCollection:
        """
        Collect observations using the resolved provider.

        This is the high-level entry point. It:
        1. Resolves the provider via resolve()
        2. Runs transformers on raw output
        3. Runs validators on transformed output
        4. Returns validated ObservationCollection

        On primary provider failure, automatically falls back to
        fallback providers. Never raises on partial failure.
        """
        ...

    @abstractmethod
    def list_providers(
        self,
        metric_id: MetricId | None = None,
        status_filter: ProviderHealthStatus | None = None,
    ) -> list[ProviderInfo]:
        """
        List registered providers with optional filters.

        Args:
            metric_id: Filter to providers that can supply this metric.
            status_filter: Filter to providers with this health status.

        Returns:
            List of ProviderInfo for matching providers.
        """
        ...

    @abstractmethod
    async def get_provider(self, provider_id: str) -> IObservationProvider:
        """
        Get a specific provider by ID.

        Raises:
            ProviderNotFoundError: If no provider with this ID is registered.
        """
        ...

    @abstractmethod
    async def restart_provider(self, provider_id: str) -> None:
        """
        Restart a provider (shutdown then re-initialize).

        Used for recovery from UNHEALTHY state. Calls shutdown(),
        then re-initializes with stored config.
        """
        ...

    @abstractmethod
    def get_health_summary(self) -> RegistryHealthSummary:
        """
        Get aggregate health summary for all registered providers.
        """
        ...
```

### 7.3 Supporting Types

```python
@dataclass(frozen=True)
class RegistrationResult:
    """Result of provider registration."""
    provider_id: str
    registration_id: str
    registered_at: datetime
    validators_applied: frozenset[str]
    transformers_applied: frozenset[str]


@dataclass(frozen=True)
class ProviderResolution:
    """Result of provider resolution."""
    primary: IObservationProvider | None
    fallbacks: list[IObservationProvider]
    validators: Sequence[IObservationValidator]
    transformers: Sequence[IObservationTransformer]
    resolution_reason: str


@dataclass(frozen=True)
class ProviderInfo:
    """Public information about a registered provider."""
    provider_id: str
    metric_ids: frozenset[MetricId]
    priority: ProviderPriority
    health_status: ProviderHealthStatus
    capabilities: frozenset[ProviderCapability]
    registered_at: datetime
    last_collection_timestamp: datetime | None = None


@dataclass(frozen=True)
class RegistryHealthSummary:
    """Aggregate health summary for the registry."""
    total_providers: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    unknown_count: int
    metric_coverage: dict[MetricId, int]  # metric_id → number of providers
```

### 7.4 Behavioral Requirements

| ID | Requirement | Rationale |
|----|-------------|-----------|
| OPC-REG-01 | `register()` must call `provider.initialize()` before adding to registry | Ensures provider is ready |
| OPC-REG-02 | `deregister()` must call `provider.shutdown()` before removal | Clean resource release |
| OPC-REG-03 | `resolve()` must never return an UNHEALTHY provider | Prevents known-bad routing |
| OPC-REG-04 | `collect()` must fall back automatically on primary failure | Pipeline resilience |
| OPC-REG-05 | `collect()` must run transformers before validators | Validates transformed output |
| OPC-REG-06 | `collect()` must never raise on partial failure | Returns degraded ObservationCollection |
| OPC-REG-07 | `restart_provider()` must not affect other providers | Isolated recovery |
| OPC-REG-08 | `list_providers()` must return results within 100ms | Used in health dashboards |
| OPC-REG-09 | Registry must be thread-safe for concurrent operations | Pipeline is async |

---

## 8. Error Handling Contracts

### 8.1 Error Hierarchy

All provider errors must inherit from `ProviderError`. The pipeline catches `ProviderError` (and its subclasses) and never encounters uncaught exceptions from provider code.

```python
class ProviderError(Exception):
    """
    Base class for all provider errors.

    All provider errors are recoverable. The pipeline continues with
    degraded data when a ProviderError occurs.
    """
    provider_id: str
    metric_id: MetricId | None
    provenance: Provenance | None
    timestamp: datetime
    retryable: bool


class ProviderTimeoutError(ProviderError):
    """Raised when a collection exceeds the configured timeout."""
    timeout_seconds: float
    elapsed_seconds: float


class ProviderAuthError(ProviderError):
    """Raised when authentication with the external source fails."""
    auth_method: str
    source_url: str


class ProviderRateLimitError(ProviderError):
    """Raised when the external source rate-limits the provider."""
    retry_after_seconds: float
    rate_limit_rpm: int


class ProviderConnectionError(ProviderError):
    """Raised when the external source is unreachable."""
    source_url: str
    connection_attempt: int


class ProviderDataError(ProviderError):
    """Raised when the external source returns invalid data."""
    raw_response: str | None = None
    expected_schema: str | None = None


class MetricNotSupportedError(ProviderError):
    """Raised when a provider cannot supply the requested metric."""
    supported_metrics: frozenset[MetricId]


class ProviderAlreadyRegisteredError(ProviderError):
    """Raised when attempting to register a duplicate provider."""
    existing_provider_id: str


class ProviderNotFoundError(ProviderError):
    """Raised when a requested provider is not in the registry."""
    requested_provider_id: str


class TransformationError(ProviderError):
    """Raised when transformation is not possible."""
    input_observation_id: str
    transformer_id: str
    reason: str
```

### 8.2 Error Recovery Rules

| Rule | Description |
|------|-------------|
| ERR-01 | All provider errors are caught at the `IProviderRegistry.collect()` level |
| ERR-02 | `ProviderTimeoutError` triggers automatic fallback to next provider in chain |
| ERR-03 | `ProviderAuthError` marks provider as DEGRADED, does not trigger fallback (auth issue is persistent) |
| ERR-04 | `ProviderRateLimitError` triggers fallback with `retry_after_seconds` hint |
| ERR-05 | `ProviderConnectionError` triggers fallback and marks provider as DEGRADED |
| ERR-06 | `ProviderDataError` triggers fallback for that metric; original data passed through if possible |
| ERR-07 | `TransformationError` causes transformer to be skipped; raw observation passed to validator |
| ERR-08 | All errors are logged with full provenance chain for debugging |
| ERR-09 | After 5 consecutive errors, provider transitions to UNHEALTHY |
| ERR-10 | `ProviderError` must never crash the pipeline; all errors are recoverable |

### 8.3 Error Logging Contract

Every provider error must produce a structured log entry:

```python
@dataclass(frozen=True)
class ProviderErrorLog:
    """Structured error log entry for provider failures."""
    error_type: str               # Class name of the error
    provider_id: str
    metric_id: str | None
    message: str
    provenance: dict[str, Any] | None
    timestamp: datetime
    retryable: bool
    context: dict[str, Any] | None  # Additional debugging context
```

---

## 9. Backward Compatibility

### 9.1 Relationship to INT-01 through INT-18

The OPC interfaces do not modify or replace any existing INT interfaces. They operate upstream of the existing pipeline:

```
External Source
  ↓
IObservationProvider (OPC-01)     ← NEW
IObservationValidator (OPC-02)    ← NEW
IObservationTransformer (OPC-03)  ← NEW
  ↓
IExtractor (INT-01)               ← EXISTING
IDetector (INT-02)                ← EXISTING
IScorer (INT-03)                  ← EXISTING
...                               ← EXISTING
```

### 9.2 Adapter Pattern for Existing Providers

Existing providers that currently implement `IExtractor` (INT-01) directly can be adapted to `IObservationProvider` using the `ExtractorAdapter`:

```python
class ExtractorAdapter:
    """
    Wraps an existing IExtractor as an IObservationProvider.

    This enables incremental migration: existing extractors continue
    to work while new providers implement IObservationProvider directly.
    """

    def __init__(self, extractor: IExtractor, provider_id: str, metric_ids: frozenset[MetricId]):
        self._extractor = extractor
        self._provider_id = provider_id
        self._metric_ids = metric_ids

    async def collect(
        self,
        metric_id: MetricId,
        context: RepositoryContext,
        window: WindowDefinition,
        options: ObservationOptions | None = None,
    ) -> ObservationCollection:
        """Delegates to the wrapped extractor's extract() method."""
        ...
```

### 9.3 Migration Path

| Phase | Description | Timeline |
|-------|-------------|----------|
| Phase 1 | OPC interfaces defined and tested | MIIE v1.6 |
| Phase 2 | Existing providers wrapped with ExtractorAdapter | MIIE v1.6.x |
| Phase 3 | New providers implement IObservationProvider directly | MIIE v1.7 |
| Phase 4 | ExtractorAdapter deprecated; all providers native | MIIE v2.0 |

---

## 10. Cross-References

### 10.1 Related Specifications

| Document | Version | Relationship |
|----------|---------|--------------|
| Observation Source Management System (OSMS) | v1.0 | Defines Observation, QualityState, Provenance types consumed by OPC |
| Observation Processing Architecture (OPA) | v1.0 | Defines how OPC-validated observations flow to detectors |
| Observation Processing Runtime (OPR) | v1.0 | Defines scheduling and orchestration of IObservationProvider.collect() |
| IExtractor (INT-01) | v1.5 | Existing interface; OPC wraps via ExtractorAdapter |
| IDetector (INT-02) | v1.5 | Downstream consumer of OPC-validated observations |
| RepositoryContext (INT-XX) | v1.5 | Context type passed to provider.collect() |

### 10.2 Interface Mapping

| OPC Interface | INT Equivalent | Migration Status |
|---------------|----------------|------------------|
| IObservationProvider | IExtractor (INT-01) | New; adapter available |
| IObservationValidator | (none) | New; no predecessor |
| IObservationTransformer | (none) | New; no predecessor |
| IProviderHealthReporter | (none) | New; no predecessor |
| IProviderRegistry | (none) | New; no predecessor |

---

## Appendix A: Implementation Checklist

- [ ] Define all OPC Protocol classes in `src/miie/contracts/opc.py`
- [ ] Define supporting types in `src/miie/contracts/opc_types.py`
- [ ] Implement `ExtractorAdapter` for backward compatibility
- [ ] Add OPC interfaces to `src/miie/contracts/__init__.py` exports
- [ ] Write unit tests for each Protocol's behavioral requirements
- [ ] Write integration tests for IProviderRegistry flow
- [ ] Update existing INT-01 tests to verify adapter compatibility
- [ ] Add OPC interface documentation to developer guide
- [ ] Verify all OPC error types are caught at registry level
- [ ] Performance test: provider resolution < 10ms, validation < 5ms per observation

---

## Appendix B: Example Provider Implementation

```python
class GitCommitFrequencyProvider:
    """Example IObservationProvider implementation for git commit frequency."""

    @property
    def provider_id(self) -> str:
        return "git.github"

    @property
    def metric_ids(self) -> frozenset[MetricId]:
        return frozenset({"commit_frequency", "commit_author_diversity"})

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return frozenset({ProviderCapability.HISTORICAL, ProviderCapability.BATCH})

    @property
    def priority(self) -> ProviderPriority:
        return ProviderPriority.PRIMARY

    async def collect(
        self,
        metric_id: MetricId,
        context: RepositoryContext,
        window: WindowDefinition,
        options: ObservationOptions | None = None,
    ) -> ObservationCollection:
        try:
            raw_data = await self._fetch_commits(context, window)
            observations = self._parse_observations(raw_data, metric_id)
            return ObservationCollection(
                observations=observations,
                provider_id=self.provider_id,
                collected_at=datetime.utcnow(),
                window=window,
            )
        except ConnectionError as e:
            raise ProviderConnectionError(
                provider_id=self.provider_id,
                metric_id=metric_id,
                source_url=self._source_url,
                connection_attempt=1,
                message=str(e),
                retryable=True,
            ) from e
```

---

*End of OPC v1.0 Specification*
