"""
MIIE v1.6 Observation Provider Framework — Health Monitoring.

Tracks execution metrics, latency, availability, errors, and capability
coverage for every registered provider.  The ``ProviderHealthMonitor``
is the single source of truth for provider health within the system.

Implements OPR §9.5.
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Dict, FrozenSet, List, Optional, Set

from miie.providers.context import (
    HealthStatus,
    ProviderHealth,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_LATENCY_HISTORY_SIZE: int = 1000
_DEFAULT_ERROR_HISTORY_SIZE: int = 200
_DEFAULT_MAX_CONSECUTIVE_FAILURES: int = 5
_DEFAULT_LATENCY_DEGRADED_MS: float = 5000.0
_DEFAULT_LATENCY_UNHEALTHY_MS: float = 10000.0


# ---------------------------------------------------------------------------
# Dataclass — Execution Metrics (OPR §9.5.1)
# ---------------------------------------------------------------------------


@dataclass
class ExecutionMetrics:
    """Tracks aggregate execution statistics for a single provider.

    Maintains a bounded deque of recent latencies so that p95/p99 can be
    computed without unbounded memory growth.
    """

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    latency_history: Deque[float] = field(default_factory=lambda: deque(maxlen=_DEFAULT_LATENCY_HISTORY_SIZE))

    # -- derived helpers ----------------------------------------------------

    @property
    def success_rate(self) -> float:
        """Ratio of successful executions to total (1.0 when no executions)."""
        if self.total_executions == 0:
            return 1.0
        return self.successful_executions / self.total_executions

    @property
    def failure_rate(self) -> float:
        """Ratio of failed executions to total."""
        if self.total_executions == 0:
            return 0.0
        return self.failed_executions / self.total_executions

    def record_latency(self, latency_ms: float) -> None:
        """Append a latency sample to the bounded history."""
        self.latency_history.append(latency_ms)

    def p95_latency(self) -> float:
        """Return the 95th-percentile latency (0.0 if empty)."""
        return _percentile(self.latency_history, 0.95)

    def p99_latency(self) -> float:
        """Return the 99th-percentile latency (0.0 if empty)."""
        return _percentile(self.latency_history, 0.99)

    def average_latency(self) -> float:
        """Return the arithmetic mean of recorded latencies (0.0 if empty)."""
        if not self.latency_history:
            return 0.0
        return sum(self.latency_history) / len(self.latency_history)


# ---------------------------------------------------------------------------
# Dataclass — Last Execution (OPR §9.5.2)
# ---------------------------------------------------------------------------


@dataclass
class LastExecution:
    """Snapshot of the most recent execution for a provider."""

    timestamp: Optional[datetime] = None
    success: bool = False
    latency_ms: float = 0.0
    error: Optional[str] = None
    observation_count: int = 0


# ---------------------------------------------------------------------------
# Dataclass — Availability (OPR §9.5.3)
# ---------------------------------------------------------------------------


@dataclass
class Availability:
    """Tracks the rolling availability state of a provider.

    ``availability_score`` is a float in [0.0, 1.0] that decays when the
    provider becomes unavailable and recovers on successful executions.
    """

    state: HealthStatus = HealthStatus.UNKNOWN
    consecutive_unavailable: int = 0
    availability_score: float = 1.0

    def mark_available(self) -> None:
        """Record a successful availability check."""
        self.consecutive_unavailable = 0
        self.state = HealthStatus.HEALTHY

    def mark_unavailable(self) -> None:
        """Record a failed availability check."""
        self.consecutive_unavailable += 1
        if self.consecutive_unavailable >= _DEFAULT_MAX_CONSECUTIVE_FAILURES:
            self.state = HealthStatus.UNHEALTHY
        else:
            self.state = HealthStatus.DEGRADED

    def recalculate_score(self, total_checks: int) -> None:
        """Recompute the availability score from historical data.

        Args:
            total_checks: Total number of availability checks performed.
        """
        if total_checks == 0:
            self.availability_score = 1.0
        else:
            successful = total_checks - self.consecutive_unavailable
            self.availability_score = max(0.0, successful / total_checks)


# ---------------------------------------------------------------------------
# Dataclass — Error Record (OPR §9.5.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ErrorRecord:
    """Single error record with timestamp, type, message, and context."""

    timestamp: datetime
    error_type: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Dataclass — Error History (OPR §9.5.4)
# ---------------------------------------------------------------------------


@dataclass
class ErrorHistory:
    """Bounded deque of ``ErrorRecord`` instances for a single provider.

    Provides query helpers for recent errors and errors filtered by type.
    """

    records: Deque[ErrorRecord] = field(default_factory=lambda: deque(maxlen=_DEFAULT_ERROR_HISTORY_SIZE))

    def record_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ErrorRecord:
        """Append a new error record and return it.

        Args:
            error_type: Category of the error (e.g. ``"TimeoutError"``).
            message: Human-readable description.
            context: Arbitrary metadata about the error.

        Returns:
            The newly created ``ErrorRecord``.
        """
        record = ErrorRecord(
            timestamp=datetime.now(timezone.utc),
            error_type=error_type,
            message=message,
            context=context or {},
        )
        self.records.append(record)
        return record

    def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
        """Return the most recent *count* error records (newest last)."""
        snapshot = list(self.records)
        return snapshot[-count:]

    def get_errors_by_type(self, error_type: str) -> List[ErrorRecord]:
        """Return all records whose ``error_type`` matches exactly."""
        return [r for r in self.records if r.error_type == error_type]

    def clear(self) -> None:
        """Discard all stored records."""
        self.records.clear()


# ---------------------------------------------------------------------------
# Class — Latency Tracker (OPR §9.5.5)
# ---------------------------------------------------------------------------


class LatencyTracker:
    """Thread-safe latency tracker with percentile queries.

    Stores up to ``max_history`` recent latency samples (milliseconds) in a
    bounded deque and provides O(n log n) percentile computation.
    """

    def __init__(self, max_history: int = _DEFAULT_LATENCY_HISTORY_SIZE) -> None:
        self._lock = threading.Lock()
        self._samples: Deque[float] = deque(maxlen=max_history)

    def record(self, latency_ms: float) -> None:
        """Record a latency sample."""
        with self._lock:
            self._samples.append(latency_ms)

    def average(self) -> float:
        """Return the arithmetic mean of all stored samples."""
        with self._lock:
            if not self._samples:
                return 0.0
            return sum(self._samples) / len(self._samples)

    def p50(self) -> float:
        """Return the 50th-percentile (median) latency."""
        with self._lock:
            return _percentile(self._samples, 0.50)

    def p95(self) -> float:
        """Return the 95th-percentile latency."""
        with self._lock:
            return _percentile(self._samples, 0.95)

    def p99(self) -> float:
        """Return the 99th-percentile latency."""
        with self._lock:
            return _percentile(self._samples, 0.99)

    def reset(self) -> None:
        """Discard all stored samples."""
        with self._lock:
            self._samples.clear()

    @property
    def sample_count(self) -> int:
        """Number of latency samples currently stored."""
        with self._lock:
            return len(self._samples)


# ---------------------------------------------------------------------------
# Dataclass — Capability Coverage (OPR §9.5.6)
# ---------------------------------------------------------------------------


@dataclass
class CapabilityCoverage:
    """Tracks how much of a provider's declared capability is exercised.

    Coverage is expressed as a float in [0.0, 1.0] for each dimension.
    """

    metric_coverage: float = 0.0
    source_type_coverage: float = 0.0
    overall_coverage: float = 0.0

    def recalculate(
        self,
        used_metrics: Set[str],
        declared_metrics: FrozenSet[str],
        used_source_types: Set[str],
        declared_source_types: FrozenSet[str],
    ) -> None:
        """Recompute all coverage scores from declared and exercised sets.

        ``overall_coverage`` is the weighted mean of metric (70 %) and
        source-type (30 %) coverage, matching the weights used in
        ``CapabilityNegotiator``.
        """
        self.metric_coverage = _set_coverage(used_metrics, declared_metrics)
        self.source_type_coverage = _set_coverage(used_source_types, declared_source_types)
        self.overall_coverage = self.metric_coverage * 0.7 + self.source_type_coverage * 0.3


# ---------------------------------------------------------------------------
# Per-provider internal state bundle (used by ProviderHealthMonitor)
# ---------------------------------------------------------------------------


@dataclass
class _ProviderHealthState:
    """Mutable container for all health-tracking data of one provider."""

    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    last_execution: LastExecution = field(default_factory=LastExecution)
    availability: Availability = field(default_factory=Availability)
    error_history: ErrorHistory = field(default_factory=ErrorHistory)
    latency_tracker: LatencyTracker = field(default_factory=LatencyTracker)
    capability_coverage: CapabilityCoverage = field(default_factory=CapabilityCoverage)
    health: ProviderHealth = field(default_factory=ProviderHealth)
    used_metrics: Set[str] = field(default_factory=set)
    used_source_types: Set[str] = field(default_factory=set)
    declared_metrics: FrozenSet[str] = field(default_factory=frozenset)
    declared_source_types: FrozenSet[str] = field(default_factory=frozenset)


# ---------------------------------------------------------------------------
# Class — Provider Health Monitor (OPR §9.5)
# ---------------------------------------------------------------------------


class ProviderHealthMonitor:
    """Thread-safe central health monitor for all observation providers.

    Every public method acquires the provider-level lock before mutating
    state, so callers may invoke methods from any thread without external
    synchronisation.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._providers: Dict[str, _ProviderHealthState] = {}

    # -- registration -------------------------------------------------------

    def register_provider(
        self,
        provider_id: str,
        declared_metrics: Optional[FrozenSet[str]] = None,
        declared_source_types: Optional[FrozenSet[str]] = None,
    ) -> None:
        """Register a new provider for health tracking.

        Args:
            provider_id: Unique provider identifier.
            declared_metrics: Metric IDs the provider declares support for.
            declared_source_types: Source types the provider declares support for.

        Raises:
            ValueError: If *provider_id* is already registered.
        """
        with self._lock:
            if provider_id in self._providers:
                raise ValueError(f"Provider '{provider_id}' is already registered")
            state = _ProviderHealthState()
            state.declared_metrics = declared_metrics or frozenset()
            state.declared_source_types = declared_source_types or frozenset()
            state.health.status = HealthStatus.UNKNOWN
            state.health.health_score = 1.0
            self._providers[provider_id] = state

    def unregister_provider(self, provider_id: str) -> None:
        """Remove a provider from health tracking.

        Args:
            provider_id: Unique provider identifier.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            if provider_id not in self._providers:
                raise KeyError(f"Provider '{provider_id}' is not registered")
            del self._providers[provider_id]

    # -- direct health reporting -------------------------------------------

    def report_health(self, provider_id: str, health: ProviderHealth) -> None:
        """Store an externally-reported health snapshot.

        Args:
            provider_id: Unique provider identifier.
            health: Health snapshot to store.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            state = self._get_state(provider_id)
            state.health = health

    def get_health(self, provider_id: str) -> ProviderHealth:
        """Return the current health snapshot for a provider.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            state = self._get_state(provider_id)
            return state.health

    def reset_health(self, provider_id: str) -> None:
        """Reset all health-tracking data for a provider to initial values.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            state = self._get_state(provider_id)
            state.metrics = ExecutionMetrics()
            state.last_execution = LastExecution()
            state.availability = Availability()
            state.error_history.clear()
            state.latency_tracker.reset()
            state.used_metrics.clear()
            state.used_source_types.clear()
            state.health = ProviderHealth(status=HealthStatus.UNKNOWN, health_score=1.0)

    # -- execution recording -----------------------------------------------

    def record_execution(
        self,
        provider_id: str,
        latency_ms: float,
        success: bool,
        observation_count: int = 0,
        metric_ids: Optional[List[str]] = None,
    ) -> None:
        """Record a single execution result for a provider.

        This updates execution metrics, latency tracking, availability,
        last-execution snapshot, capability coverage, and triggers a
        health-status re-evaluation.

        Args:
            provider_id: Unique provider identifier.
            latency_ms: Wall-clock latency of the execution in milliseconds.
            success: Whether the execution completed successfully.
            observation_count: Number of observations produced.
            metric_ids: Metric IDs exercised during this execution.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        now = datetime.now(timezone.utc)
        with self._lock:
            state = self._get_state(provider_id)

            # Execution metrics
            state.metrics.total_executions += 1
            if success:
                state.metrics.successful_executions += 1
            else:
                state.metrics.failed_executions += 1
            state.metrics.record_latency(latency_ms)

            # Latency tracker
            state.latency_tracker.record(latency_ms)

            # Last execution
            state.last_execution = LastExecution(
                timestamp=now,
                success=success,
                latency_ms=latency_ms,
                observation_count=observation_count,
            )

            # Availability
            if success:
                state.availability.mark_available()
            else:
                state.availability.mark_unavailable()
            state.availability.recalculate_score(state.metrics.total_executions)

            # Capability coverage
            if metric_ids:
                state.used_metrics.update(metric_ids)
            state.capability_coverage.recalculate(
                used_metrics=state.used_metrics,
                declared_metrics=state.declared_metrics,
                used_source_types=state.used_source_types,
                declared_source_types=state.declared_source_types,
            )

            # Derive health status
            self._update_health_status(provider_id)

    def record_error(
        self,
        provider_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ErrorRecord:
        """Append an error record and re-evaluate provider health.

        Args:
            provider_id: Unique provider identifier.
            error_type: Category of the error.
            error_message: Human-readable description.
            context: Arbitrary metadata about the error.

        Returns:
            The newly created ``ErrorRecord``.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            state = self._get_state(provider_id)
            record = state.error_history.record_error(error_type, error_message, context)
            state.last_execution.error = error_message
            self._update_health_status(provider_id)
            return record

    # -- read accessors -----------------------------------------------------

    def get_execution_metrics(self, provider_id: str) -> ExecutionMetrics:
        """Return the aggregate execution metrics for a provider.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            return self._get_state(provider_id).metrics

    def get_last_execution(self, provider_id: str) -> LastExecution:
        """Return the last-execution snapshot for a provider.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            return self._get_state(provider_id).last_execution

    def get_availability(self, provider_id: str) -> Availability:
        """Return the availability state for a provider.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            return self._get_state(provider_id).availability

    def get_error_history(self, provider_id: str) -> ErrorHistory:
        """Return the error history for a provider.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            return self._get_state(provider_id).error_history

    def get_latency_tracker(self, provider_id: str) -> LatencyTracker:
        """Return the latency tracker for a provider.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            return self._get_state(provider_id).latency_tracker

    def get_capability_coverage(self, provider_id: str) -> CapabilityCoverage:
        """Return the capability coverage state for a provider.

        Raises:
            KeyError: If *provider_id* is not registered.
        """
        with self._lock:
            return self._get_state(provider_id).capability_coverage

    def get_registered_providers(self) -> List[str]:
        """Return a snapshot of all registered provider IDs."""
        with self._lock:
            return list(self._providers.keys())

    # -- internal helpers ---------------------------------------------------

    def _get_state(self, provider_id: str) -> _ProviderHealthState:
        """Return the internal state bundle, raising ``KeyError`` if absent.

        Caller **must** hold ``self._lock``.
        """
        try:
            return self._providers[provider_id]
        except KeyError:
            raise KeyError(f"Provider '{provider_id}' is not registered")

    def _update_health_status(self, provider_id: str) -> None:
        """Derive the ``ProviderHealth`` snapshot from current metrics.

        Caller **must** hold ``self._lock``.

        Status derivation rules (OPR §9.5):
        - ``HEALTHY``     — success rate >= 90 %, consecutive failures < 3,
          average latency < 5 000 ms.
        - ``DEGRADED``    — success rate >= 70 %, consecutive failures < 5,
          average latency < 10 000 ms.
        - ``UNHEALTHY``   — any of: success rate < 70 %, consecutive
          failures >= 5, average latency >= 10 000 ms.
        - ``DRAINING``    — same as HEALTHY but provider state is DISPOSED
          (checked externally by the caller; we never set DRAINING here).
        - ``UNKNOWN``     — no executions recorded yet.
        """
        state = self._get_state(provider_id)
        metrics = state.metrics

        # No data yet
        if metrics.total_executions == 0:
            state.health = ProviderHealth(status=HealthStatus.UNKNOWN, health_score=1.0)
            return

        success_rate = metrics.success_rate
        avg_latency = metrics.average_latency()
        consecutive_failures = state.availability.consecutive_unavailable
        p95 = metrics.p95_latency()
        p99 = metrics.p99_latency()

        # Compute a blended health score in [0.0, 1.0].
        # Components: success_rate (50 %), availability (30 %), latency (20 %).
        latency_ratio = 1.0 - min(avg_latency / _DEFAULT_LATENCY_UNHEALTHY_MS, 1.0)
        availability_ratio = state.availability.availability_score
        health_score = success_rate * 0.5 + availability_ratio * 0.3 + latency_ratio * 0.2
        health_score = max(0.0, min(1.0, health_score))

        # Determine status
        if success_rate >= 0.90 and consecutive_failures < 3 and avg_latency < _DEFAULT_LATENCY_DEGRADED_MS:
            status = HealthStatus.HEALTHY
        elif (
            success_rate >= 0.70
            and consecutive_failures < _DEFAULT_MAX_CONSECUTIVE_FAILURES
            and avg_latency < _DEFAULT_LATENCY_UNHEALTHY_MS
        ):
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY

        # Build the health snapshot
        last_err_ts: Optional[datetime] = None
        last_err_msg: Optional[str] = None
        if state.error_history.records:
            last_record = state.error_history.records[-1]
            last_err_ts = last_record.timestamp
            last_err_msg = last_record.message

        state.health = ProviderHealth(
            status=status,
            health_score=health_score,
            last_check=datetime.now(timezone.utc),
            consecutive_failures=consecutive_failures,
            total_extractions=metrics.total_executions,
            successful_extractions=metrics.successful_executions,
            failed_extractions=metrics.failed_executions,
            average_latency_ms=avg_latency,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            error_message=last_err_msg,
            last_error=last_err_ts,
        )


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _percentile(values: Deque[float], pct: float) -> float:
    """Compute the *pct* percentile of *values* (0.0 – 1.0).

    Returns 0.0 when *values* is empty.  Uses linear interpolation between
    ranks (scipy ``method='linear'`` equivalent).
    """
    if not values:
        return 0.0
    data = sorted(values)
    n = len(data)
    if n == 1:
        return data[0]
    # Index in [0, n-1]
    k = pct * (n - 1)
    lo = int(k)
    hi = min(lo + 1, n - 1)
    frac = k - lo
    return data[lo] + frac * (data[hi] - data[lo])


def _set_coverage(used: Set[str], declared: FrozenSet[str]) -> float:
    """Fraction of *declared* items that appear in *used* (0.0 if empty)."""
    if not declared:
        return 0.0
    return len(used & declared) / len(declared)
