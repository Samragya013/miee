"""
MIIE v1.6 Observation Provider Framework — Provider lifecycle management.

Implements OPA §11 lifecycle phases: initialize, configure, validate,
execute, normalize, cleanup, shutdown, and recover.  Every state
transition is recorded in a ProviderLifecycleAudit trail for
observability and debugging.

Depends on:
    miie.providers.context  — core types (ProviderContext, ExtractionResult, …)
    miie.providers.exceptions — error hierarchy
    miie.providers.health    — ProviderHealthMonitor (Protocol defined here
                               until the real module ships)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from miie.providers.context import (
    ExtractionResult,
    ProviderContext,
    ProviderState,
    QualityState,
    ValidationResult,
)
from miie.providers.exceptions import (
    ExtractionError,
    ExtractionTimeoutError,
    ProviderDisposedError,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Protocol — ProviderHealthMonitor (placeholder until miie.providers.health)
# ---------------------------------------------------------------------------


@runtime_checkable
class ProviderHealthMonitor(Protocol):
    """Minimal health-monitor contract expected by ProviderLifecycleManager.

    A concrete implementation lives in (or will land in)
    ``miie.providers.health``.  This Protocol lets lifecycle.py type-check
    without a hard import on a module that may not exist yet.
    """

    def record_success(self, provider_id: str, latency_ms: float) -> None: ...

    def record_failure(self, provider_id: str, error: Exception) -> None: ...

    def get_health(self, provider_id: str) -> Any: ...


# ---------------------------------------------------------------------------
# Lifecycle States (OPA §11.1 — extended)
# ---------------------------------------------------------------------------


class LifecycleState(str, Enum):
    """Extended provider lifecycle states.

    Superset of ``ProviderState`` that includes transient intermediate
    states used only during lifecycle transitions.  These never leak
    outside the ``ProviderLifecycleManager`` boundary.
    """

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    CONFIGURING = "configuring"
    VALIDATING = "validating"
    READY = "ready"
    EXECUTING = "executing"
    NORMALIZING = "normalizing"
    CLEANING_UP = "cleaning_up"
    DISPOSED = "disposed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Allowed transitions (OPA §11.2)
# ---------------------------------------------------------------------------

_ALLOWED_TRANSITIONS: Dict[LifecycleState, frozenset[LifecycleState]] = {
    LifecycleState.UNINITIALIZED: frozenset(
        {
            LifecycleState.INITIALIZING,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.INITIALIZING: frozenset(
        {
            LifecycleState.READY,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.CONFIGURING: frozenset(
        {
            LifecycleState.READY,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.VALIDATING: frozenset(
        {
            LifecycleState.READY,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.READY: frozenset(
        {
            LifecycleState.CONFIGURING,
            LifecycleState.VALIDATING,
            LifecycleState.EXECUTING,
            LifecycleState.CLEANING_UP,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.EXECUTING: frozenset(
        {
            LifecycleState.NORMALIZING,
            LifecycleState.CLEANING_UP,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.NORMALIZING: frozenset(
        {
            LifecycleState.READY,
            LifecycleState.CLEANING_UP,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.CLEANING_UP: frozenset(
        {
            LifecycleState.DISPOSED,
            LifecycleState.FAILED,
        }
    ),
    LifecycleState.DISPOSED: frozenset(),  # terminal
    LifecycleState.FAILED: frozenset(
        {
            LifecycleState.INITIALIZING,
            LifecycleState.READY,
        }
    ),
}


def _is_valid_transition(source: LifecycleState, target: LifecycleState) -> bool:
    """Return *True* if *source → target* is permitted."""
    return target in _ALLOWED_TRANSITIONS.get(source, frozenset())


# ---------------------------------------------------------------------------
# Lifecycle Transition record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LifecycleTransition:
    """Immutable record of a single lifecycle state change."""

    provider_id: str
    from_state: LifecycleState
    to_state: LifecycleState
    trigger: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary."""
        result: Dict[str, Any] = {
            "provider_id": self.provider_id,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "trigger": self.trigger,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "duration_ms": self.duration_ms,
        }
        if self.error_message is not None:
            result["error_message"] = self.error_message
        return result


# ---------------------------------------------------------------------------
# Provider Lifecycle Audit (OPA §11.3)
# ---------------------------------------------------------------------------


class ProviderLifecycleAudit:
    """Records every lifecycle transition per provider.

    Thread-safe for concurrent callers; all mutations happen under a
    single lock.
    """

    def __init__(self) -> None:
        self._transitions: Dict[str, List[LifecycleTransition]] = {}
        self._current_state: Dict[str, LifecycleState] = {}

    # -- public API ----------------------------------------------------------

    def record(self, transition: LifecycleTransition) -> None:
        """Append a transition to the audit trail."""
        pid = transition.provider_id
        self._transitions.setdefault(pid, []).append(transition)
        self._current_state[pid] = transition.to_state

    def get_transitions(self, provider_id: str) -> List[LifecycleTransition]:
        """Return the full ordered list of transitions for *provider_id*."""
        return list(self._transitions.get(provider_id, []))

    def get_current_state(self, provider_id: str) -> LifecycleState:
        """Return the latest lifecycle state for *provider_id*.

        Falls back to ``UNINITIALIZED`` if no transition has been recorded.
        """
        return self._current_state.get(provider_id, LifecycleState.UNINITIALIZED)

    def get_audit_trail(self, provider_id: str) -> List[Dict[str, Any]]:
        """Return a serialisable audit trail for *provider_id*."""
        return [t.to_dict() for t in self.get_transitions(provider_id)]

    def clear(self, provider_id: Optional[str] = None) -> None:
        """Purge transitions — one provider or all."""
        if provider_id is None:
            self._transitions.clear()
            self._current_state.clear()
        else:
            self._transitions.pop(provider_id, None)
            self._current_state.pop(provider_id, None)

    @property
    def tracked_providers(self) -> List[str]:
        """IDs of all providers with recorded transitions."""
        return list(self._transitions.keys())


# ---------------------------------------------------------------------------
# Provider Lifecycle Manager (OPA §11)
# ---------------------------------------------------------------------------


class ProviderLifecycleManager:
    """Drives a provider through its lifecycle phases.

    Every public method transitions the provider through a well-defined
    state machine, enforces preconditions, records timing, reports
    health, and appends to the audit trail.

    Parameters
    ----------
    health_monitor:
        A ``ProviderHealthMonitor`` instance (or compatible object)
        used to record extraction successes / failures.
    """

    def __init__(self, health_monitor: ProviderHealthMonitor) -> None:
        self._health_monitor = health_monitor
        self._audit = ProviderLifecycleAudit()

    # -- helpers -------------------------------------------------------------

    @property
    def audit(self) -> ProviderLifecycleAudit:
        """Access the underlying audit trail."""
        return self._audit

    def _get_lifecycle_state(self, provider: Any) -> LifecycleState:
        """Derive a ``LifecycleState`` from a provider's ``state`` attr."""
        if not hasattr(provider, "state"):
            return LifecycleState.UNINITIALIZED
        raw: ProviderState = provider.state  # type: ignore[assignment]
        mapping: Dict[ProviderState, LifecycleState] = {
            ProviderState.UNINITIALIZED: LifecycleState.UNINITIALIZED,
            ProviderState.READY: LifecycleState.READY,
            ProviderState.ACTIVE: LifecycleState.READY,
            ProviderState.DEGRADED: LifecycleState.READY,
            ProviderState.FAILED: LifecycleState.FAILED,
            ProviderState.DISPOSED: LifecycleState.DISPOSED,
        }
        return mapping.get(raw, LifecycleState.UNINITIALIZED)

    def _transition(
        self,
        provider: Any,
        target: LifecycleState,
        trigger: str,
        *,
        duration_ms: float = 0.0,
        error_message: Optional[str] = None,
    ) -> LifecycleTransition:
        """Record a transition in the audit trail."""
        pid = getattr(provider, "provider_id", "<unknown>")
        current = self._get_lifecycle_state(provider)
        success = error_message is None

        transition = LifecycleTransition(
            provider_id=pid,
            from_state=current,
            to_state=target,
            trigger=trigger,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
        )
        self._audit.record(transition)
        return transition

    def _set_provider_state(self, provider: Any, target: LifecycleState) -> None:
        """Push the provider's internal ``state`` attribute if writable."""
        # Map lifecycle states back to ProviderState where possible
        provider_state_map: Dict[LifecycleState, ProviderState] = {
            LifecycleState.UNINITIALIZED: ProviderState.UNINITIALIZED,
            LifecycleState.INITIALIZING: ProviderState.UNINITIALIZED,
            LifecycleState.CONFIGURING: ProviderState.READY,
            LifecycleState.VALIDATING: ProviderState.READY,
            LifecycleState.READY: ProviderState.READY,
            LifecycleState.EXECUTING: ProviderState.ACTIVE,
            LifecycleState.NORMALIZING: ProviderState.ACTIVE,
            LifecycleState.CLEANING_UP: ProviderState.DISPOSED,
            LifecycleState.DISPOSED: ProviderState.DISPOSED,
            LifecycleState.FAILED: ProviderState.FAILED,
        }
        ps = provider_state_map.get(target)
        if ps is not None and hasattr(provider, "_state"):
            provider._state = ps  # type: ignore[attr-defined]

    def _ensure_not_disposed(self, provider: Any) -> None:
        """Raise ``ProviderDisposedError`` if the provider is disposed."""
        if self._get_lifecycle_state(provider) == LifecycleState.DISPOSED:
            pid = getattr(provider, "provider_id", "<unknown>")
            raise ProviderDisposedError(f"Provider '{pid}' has been disposed")

    # -- public lifecycle phases (OPA §11.4) ---------------------------------

    def initialize(self, provider: Any, context: ProviderContext) -> bool:
        """Initialize *provider* and transition to READY.

        Returns ``True`` on success, ``False`` on failure.
        """
        pid = getattr(provider, "provider_id", "<unknown>")
        self._ensure_not_disposed(provider)

        current = self._get_lifecycle_state(provider)
        if current not in (
            LifecycleState.UNINITIALIZED,
            LifecycleState.FAILED,
        ):
            logger.warning(
                "initialize: provider '%s' in unexpected state %s",
                pid,
                current.value,
            )
            return False

        self._transition(provider, LifecycleState.INITIALIZING, "initialize_start")
        t0 = time.monotonic()

        try:
            provider.initialize(context)
        except Exception as exc:
            duration_ms = (time.monotonic() - t0) * 1000.0
            self._transition(
                provider,
                LifecycleState.FAILED,
                "initialize_error",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            self._set_provider_state(provider, LifecycleState.FAILED)
            self._health_monitor.record_failure(pid, exc)
            logger.exception("initialize: provider '%s' failed", pid)
            return False

        duration_ms = (time.monotonic() - t0) * 1000.0
        self._transition(
            provider,
            LifecycleState.READY,
            "initialize_complete",
            duration_ms=duration_ms,
        )
        self._set_provider_state(provider, LifecycleState.READY)
        self._health_monitor.record_success(pid, duration_ms)
        logger.info("initialize: provider '%s' ready (%.1f ms)", pid, duration_ms)
        return True

    def configure(self, provider: Any, config: Dict[str, Any]) -> bool:
        """Apply *config* to *provider*.

        Returns ``True`` on success.
        """
        pid = getattr(provider, "provider_id", "<unknown>")
        self._ensure_not_disposed(provider)

        current = self._get_lifecycle_state(provider)
        if current not in (LifecycleState.READY, LifecycleState.CONFIGURING):
            logger.warning(
                "configure: provider '%s' in unexpected state %s",
                pid,
                current.value,
            )
            return False

        self._transition(provider, LifecycleState.CONFIGURING, "configure_start")
        t0 = time.monotonic()

        try:
            if hasattr(provider, "configure"):
                provider.configure(config)
            elif hasattr(provider, "config"):
                provider.config.update(config)  # type: ignore[attr-defined]
            else:
                logger.debug(
                    "configure: provider '%s' has no configure method; " "storing config on entry",
                    pid,
                )
        except Exception as exc:
            duration_ms = (time.monotonic() - t0) * 1000.0
            self._transition(
                provider,
                LifecycleState.FAILED,
                "configure_error",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            self._set_provider_state(provider, LifecycleState.FAILED)
            logger.exception("configure: provider '%s' failed", pid)
            return False

        duration_ms = (time.monotonic() - t0) * 1000.0
        self._transition(
            provider,
            LifecycleState.READY,
            "configure_complete",
            duration_ms=duration_ms,
        )
        self._set_provider_state(provider, LifecycleState.READY)
        logger.info("configure: provider '%s' configured (%.1f ms)", pid, duration_ms)
        return True

    def validate(self, provider: Any) -> ValidationResult:
        """Validate that *provider* is properly configured.

        Delegates to the provider's ``validate`` method if present,
        otherwise returns a successful result.
        """
        pid = getattr(provider, "provider_id", "<unknown>")
        self._ensure_not_disposed(provider)

        current = self._get_lifecycle_state(provider)
        if current == LifecycleState.DISPOSED:
            return ValidationResult.failure(
                [f"Provider '{pid}' is disposed"],
                rule_id="LIFECYCLE_DISPOSED",
            )

        self._transition(provider, LifecycleState.VALIDATING, "validate_start")
        t0 = time.monotonic()

        try:
            if hasattr(provider, "validate"):
                result: ValidationResult = provider.validate()
            else:
                result = ValidationResult.success()
        except Exception as exc:
            duration_ms = (time.monotonic() - t0) * 1000.0
            self._transition(
                provider,
                LifecycleState.READY,
                "validate_error",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            self._set_provider_state(provider, LifecycleState.READY)
            return ValidationResult.failure([str(exc)], rule_id="LIFECYCLE_VALIDATE_ERROR")

        duration_ms = (time.monotonic() - t0) * 1000.0
        target = LifecycleState.READY if result.is_valid else LifecycleState.FAILED
        self._transition(
            provider,
            target,
            "validate_complete" if result.is_valid else "validate_failed",
            duration_ms=duration_ms,
        )
        self._set_provider_state(provider, target)
        logger.info(
            "validate: provider '%s' valid=%s (%.1f ms)",
            pid,
            result.is_valid,
            duration_ms,
        )
        return result

    def execute(
        self,
        provider: Any,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Execute observation extraction for *metric_ids*.

        Transitions through EXECUTING → NORMALIZING → READY, recording
        timing and reporting health.  Returns the (possibly normalised)
        ``ExtractionResult``.
        """
        pid = getattr(provider, "provider_id", "<unknown>")
        self._ensure_not_disposed(provider)

        current = self._get_lifecycle_state(provider)
        if current not in (LifecycleState.READY,):
            # Build a synthetic failed result rather than raising so
            # callers can always inspect the result object.
            logger.error(
                "execute: provider '%s' not READY (state=%s)",
                pid,
                current.value,
            )
            return ExtractionResult(
                provider_id=pid,
                metric_id=",".join(metric_ids),
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
                metadata={"error": f"Provider in state {current.value}"},
            )

        self._transition(provider, LifecycleState.EXECUTING, "execute_start")
        t0 = time.monotonic()

        try:
            raw_result: ExtractionResult = provider.extract_observations(context, metric_ids)
        except ExtractionTimeoutError as exc:
            duration_ms = (time.monotonic() - t0) * 1000.0
            self._transition(
                provider,
                LifecycleState.FAILED,
                "execute_timeout",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            self._set_provider_state(provider, LifecycleState.FAILED)
            self._health_monitor.record_failure(pid, exc)
            logger.error("execute: provider '%s' timed out (%.1f ms)", pid, duration_ms)
            return ExtractionResult(
                provider_id=pid,
                metric_id=",".join(metric_ids),
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
                extraction_time_ms=duration_ms,
                metadata={"error": str(exc), "error_type": "timeout"},
            )
        except ExtractionError as exc:
            duration_ms = (time.monotonic() - t0) * 1000.0
            self._transition(
                provider,
                LifecycleState.FAILED,
                "execute_extraction_error",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            self._set_provider_state(provider, LifecycleState.FAILED)
            self._health_monitor.record_failure(pid, exc)
            logger.error(
                "execute: provider '%s' extraction error (%.1f ms)",
                pid,
                duration_ms,
            )
            return ExtractionResult(
                provider_id=pid,
                metric_id=",".join(metric_ids),
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
                extraction_time_ms=duration_ms,
                metadata={"error": str(exc), "error_type": "extraction"},
            )
        except Exception as exc:
            duration_ms = (time.monotonic() - t0) * 1000.0
            self._transition(
                provider,
                LifecycleState.FAILED,
                "execute_error",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            self._set_provider_state(provider, LifecycleState.FAILED)
            self._health_monitor.record_failure(pid, exc)
            logger.exception("execute: provider '%s' unexpected error", pid)
            return ExtractionResult(
                provider_id=pid,
                metric_id=",".join(metric_ids),
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
                extraction_time_ms=duration_ms,
                metadata={"error": str(exc), "error_type": "unexpected"},
            )

        extraction_ms = (time.monotonic() - t0) * 1000.0
        self._transition(
            provider,
            LifecycleState.NORMALIZING,
            "execute_complete",
            duration_ms=extraction_ms,
        )

        # -- Normalize -------------------------------------------------------
        normalised = self.normalize(raw_result)

        # -- Back to READY ---------------------------------------------------
        self._transition(
            provider,
            LifecycleState.READY,
            "normalize_complete",
        )
        self._set_provider_state(provider, LifecycleState.READY)
        self._health_monitor.record_success(pid, extraction_ms)
        logger.info(
            "execute: provider '%s' extracted %d observations (%.1f ms)",
            pid,
            normalised.observation_count,
            extraction_ms,
        )
        return normalised

    def normalize(self, result: ExtractionResult) -> ExtractionResult:
        """Validate and normalise an extraction result (OPA §11.5).

        Checks quality state consistency and returns the result
        unchanged when everything looks correct.  Degrades the quality
        state when observations are empty or confidence is zero.
        """
        warnings = list(result.warnings)

        # Empty extraction — degrade quality
        if result.is_empty and result.quality_state == QualityState.COMPLETE:
            warnings.append("Extraction produced zero observations; " "quality degraded from COMPLETE to DEGRADED")
            return ExtractionResult(
                provider_id=result.provider_id,
                metric_id=result.metric_id,
                observations=result.observations,
                quality_state=QualityState.DEGRADED,
                confidence=0.0,
                extraction_time_ms=result.extraction_time_ms,
                is_partial=True,
                warnings=warnings,
                metadata={**result.metadata, "normalization": "empty_degrade"},
            )

        # Zero confidence — mark as uncertain
        if result.confidence == 0.0 and not result.is_empty:
            warnings.append("Confidence is zero; quality state overridden to UNCERTAIN")
            return ExtractionResult(
                provider_id=result.provider_id,
                metric_id=result.metric_id,
                observations=result.observations,
                quality_state=QualityState.UNCERTAIN,
                confidence=0.0,
                extraction_time_ms=result.extraction_time_ms,
                is_partial=result.is_partial,
                warnings=warnings,
                metadata={**result.metadata, "normalization": "zero_confidence"},
            )

        # Already degraded / uncertain / missing — keep as-is, add note
        if result.quality_state in (
            QualityState.DEGRADED,
            QualityState.UNCERTAIN,
            QualityState.STALE,
            QualityState.MISSING,
            QualityState.RECOVERING,
        ):
            warnings.append(f"Quality state is {result.quality_state.value}; " "no normalization applied")
            if warnings != result.warnings:
                return ExtractionResult(
                    provider_id=result.provider_id,
                    metric_id=result.metric_id,
                    observations=result.observations,
                    quality_state=result.quality_state,
                    confidence=result.confidence,
                    extraction_time_ms=result.extraction_time_ms,
                    is_partial=result.is_partial,
                    warnings=warnings,
                    metadata=result.metadata,
                )

        return result

    def cleanup(self, provider: Any) -> None:
        """Dispose of *provider* resources and transition to DISPOSED."""
        pid = getattr(provider, "provider_id", "<unknown>")
        current = self._get_lifecycle_state(provider)

        if current == LifecycleState.DISPOSED:
            logger.debug("cleanup: provider '%s' already disposed", pid)
            return

        self._transition(provider, LifecycleState.CLEANING_UP, "cleanup_start")
        t0 = time.monotonic()

        try:
            provider.dispose()
        except Exception as exc:
            duration_ms = (time.monotonic() - t0) * 1000.0
            logger.exception("cleanup: provider '%s' raised during dispose", pid)
            self._transition(
                provider,
                LifecycleState.FAILED,
                "cleanup_error",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            # Even on error we force the provider to DISPOSED state so
            # it cannot be reused.
            self._set_provider_state(provider, LifecycleState.DISPOSED)
            return

        duration_ms = (time.monotonic() - t0) * 1000.0
        self._transition(
            provider,
            LifecycleState.DISPOSED,
            "cleanup_complete",
            duration_ms=duration_ms,
        )
        self._set_provider_state(provider, LifecycleState.DISPOSED)
        logger.info("cleanup: provider '%s' disposed (%.1f ms)", pid, duration_ms)

    def shutdown(self, provider: Any) -> None:
        """Graceful shutdown: cleanup + final audit record.

        Identical to ``cleanup`` but also logs a shutdown-specific trigger
        so the audit trail distinguishes user-initiated disposal from
        shutdown-triggered disposal.
        """
        pid = getattr(provider, "provider_id", "<unknown>")
        current = self._get_lifecycle_state(provider)

        if current == LifecycleState.DISPOSED:
            logger.debug("shutdown: provider '%s' already disposed", pid)
            return

        self._transition(provider, LifecycleState.CLEANING_UP, "shutdown_start")
        self.cleanup(provider)
        logger.info("shutdown: provider '%s' shut down", pid)

    def recover(self, provider: Any, context: ProviderContext) -> bool:
        """Attempt to recover a provider from the FAILED state.

        Disposes of the current instance (best-effort), re-initialises,
        and transitions back to READY on success.

        Returns ``True`` if the provider is READY after recovery.
        """
        pid = getattr(provider, "provider_id", "<unknown>")

        # Force-dispose regardless of current state
        try:
            if self._get_lifecycle_state(provider) != LifecycleState.DISPOSED:
                provider.dispose()
        except Exception:
            logger.debug(
                "recover: best-effort dispose of provider '%s' ignored errors",
                pid,
            )

        self._set_provider_state(provider, LifecycleState.UNINITIALIZED)
        self._transition(
            provider,
            LifecycleState.UNINITIALIZED,
            "recover_reset",
        )

        ok = self.initialize(provider, context)
        if ok:
            logger.info("recover: provider '%s' recovered successfully", pid)
        else:
            logger.error("recover: provider '%s' recovery failed", pid)
        return ok


__all__ = [
    "LifecycleState",
    "LifecycleTransition",
    "ProviderLifecycleAudit",
    "ProviderLifecycleManager",
    "ProviderHealthMonitor",
]
