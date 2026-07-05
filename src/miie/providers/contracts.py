"""
MIIE v1.6 Observation Provider Framework — Protocol interfaces.

Implements OPC-v1.0 §3 and OPA-v1.0 §9 interface definitions.
All observation providers must conform to these Protocol classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, FrozenSet, List, Optional, Protocol, runtime_checkable

from miie.providers.context import (
    ExtractionResult,
    HealthStatus,
    PriorityLevel,
    ProviderCapability,
    ProviderContext,
    ProviderEntry,
    ProviderHealth,
    ProviderState,
    ValidationResult,
)

# ---------------------------------------------------------------------------
# IObservationProvider (OPC §3.1, OPA §9.1)
# ---------------------------------------------------------------------------


@runtime_checkable
class IObservationProvider(Protocol):
    """OPC §3.1 / OPA §9.1 — Base observation provider interface.

    All observation providers must implement this interface.
    Provides lifecycle management, capability declaration, and extraction.
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    def state(self) -> ProviderState:
        """Current lifecycle state of the provider."""
        ...

    def supports_metric(self, metric_id: str) -> bool:
        """Check if this provider supports the given metric."""
        ...

    def get_capabilities(self) -> ProviderCapability:
        """Get the capabilities of this provider."""
        ...

    def initialize(self, context: ProviderContext) -> None:
        """Initialize the provider with extraction context."""
        ...

    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the specified metrics."""
        ...

    def health_check(self) -> ProviderHealth:
        """Check the health status of this provider."""
        ...

    def dispose(self) -> None:
        """Dispose of the provider and release resources."""
        ...


# ---------------------------------------------------------------------------
# IGitProvider (OPA §9.2)
# ---------------------------------------------------------------------------


@runtime_checkable
class IGitProvider(IObservationProvider, Protocol):
    """OPA §9.2 — Git-specific observation provider interface."""

    def extract_commits(
        self,
        context: ProviderContext,
        since: Optional[str] = None,
        until: Optional[str] = None,
        exclude_bots: bool = False,
    ) -> ExtractionResult:
        """Extract commit observations."""
        ...

    def extract_branches(self, context: ProviderContext) -> ExtractionResult:
        """Extract branch observations."""
        ...

    def extract_tags(self, context: ProviderContext) -> ExtractionResult:
        """Extract tag observations."""
        ...


# ---------------------------------------------------------------------------
# IObservationValidator (OPC §3.2)
# ---------------------------------------------------------------------------


@runtime_checkable
class IObservationValidator(Protocol):
    """OPC §3.2 — Observation validation interface."""

    def validate_observation(self, observation: Any, metric_id: str) -> ValidationResult:
        """Validate a single observation."""
        ...

    def validate_batch(self, observations: List[Any], metric_id: str) -> List[ValidationResult]:
        """Validate a batch of observations."""
        ...

    def get_validation_rules(self, metric_id: str) -> List[Any]:
        """Get validation rules for a metric."""
        ...


# ---------------------------------------------------------------------------
# IObservationTransformer (OPC §3.3)
# ---------------------------------------------------------------------------


@runtime_checkable
class IObservationTransformer(Protocol):
    """OPC §3.3 — Observation transformation interface."""

    def transform_to_internal(self, observation: Any, source_format: str) -> Any:
        """Transform a single observation to internal format."""
        ...

    def transform_batch(self, observations: List[Any], source_format: str) -> List[Any]:
        """Transform a batch of observations to internal format."""
        ...

    def get_supported_formats(self) -> FrozenSet[str]:
        """Get list of supported source formats."""
        ...


# ---------------------------------------------------------------------------
# IProviderHealthReporter (OPC §3.4)
# ---------------------------------------------------------------------------


@runtime_checkable
class IProviderHealthReporter(Protocol):
    """OPC §3.4 — Provider health reporting interface."""

    def report_health(self, provider_id: str, health: ProviderHealth) -> None:
        """Report health status for a provider."""
        ...

    def get_health(self, provider_id: str) -> Optional[ProviderHealth]:
        """Get health status for a provider."""
        ...

    def reset_health(self, provider_id: str) -> None:
        """Reset health status for a provider."""
        ...


# ---------------------------------------------------------------------------
# IProviderRegistry (OPC §3.5, OPR §6.1)
# ---------------------------------------------------------------------------


@runtime_checkable
class IProviderRegistry(Protocol):
    """OPC §3.5 / OPR §6.1 — Provider registry interface."""

    def register(
        self,
        provider: IObservationProvider,
        capability: ProviderCapability,
        priority: PriorityLevel = PriorityLevel.MEDIUM,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a provider with the registry."""
        ...

    def unregister(self, provider_id: str) -> None:
        """Unregister a provider from the registry."""
        ...

    def get_provider(self, provider_id: str) -> Optional[IObservationProvider]:
        """Get a provider by ID."""
        ...

    def discover(self, metric_id: str) -> List[IObservationProvider]:
        """Discover providers that support a metric, ordered by priority."""
        ...

    def get_all(self) -> List[ProviderEntry]:
        """Get all registered providers."""
        ...

    def get_by_metric(self, metric_id: str) -> List[ProviderEntry]:
        """Get providers that support a metric."""
        ...

    def get_healthy_providers(self, metric_id: str) -> List[IObservationProvider]:
        """Get healthy providers that support a metric."""
        ...


# ---------------------------------------------------------------------------
# IProviderFactory (OPR §7.3)
# ---------------------------------------------------------------------------


@runtime_checkable
class IProviderFactory(Protocol):
    """OPR §7.3 — Provider factory interface."""

    def create_provider(self, provider_class: str, config: Dict[str, Any]) -> IObservationProvider:
        """Create a provider instance from configuration."""
        ...

    def validate_config(self, provider_class: str, config: Dict[str, Any]) -> ValidationResult:
        """Validate provider configuration."""
        ...

    def get_provider_type(self, provider_class: str) -> str:
        """Get the type of a provider class."""
        ...


# ---------------------------------------------------------------------------
# Abstract Base Classes (OPA §9.3)
# ---------------------------------------------------------------------------


class GitObservationProvider(ABC):
    """OPA §9.3 — Abstract base for Git observation providers."""

    def __init__(self, provider_id: str) -> None:
        self._provider_id = provider_id
        self._state = ProviderState.UNINITIALIZED

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        return self._provider_id

    @property
    def state(self) -> ProviderState:
        """Current lifecycle state of the provider."""
        return self._state

    def supports_metric(self, metric_id: str) -> bool:
        """Check if this provider supports the given metric."""
        capabilities = self.get_capabilities()
        return capabilities.supports_metric(metric_id)

    @abstractmethod
    def get_capabilities(self) -> ProviderCapability:
        """Get the capabilities of this provider."""
        ...

    def initialize(self, context: ProviderContext) -> None:
        """Initialize the provider with extraction context."""
        self._state = ProviderState.READY

    @abstractmethod
    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the specified metrics."""
        ...

    def health_check(self) -> ProviderHealth:
        """Check the health status of this provider."""
        if self._state in (ProviderState.READY, ProviderState.ACTIVE):
            return ProviderHealth(status=HealthStatus.HEALTHY)
        elif self._state == ProviderState.DEGRADED:
            return ProviderHealth(status=HealthStatus.DEGRADED)
        elif self._state == ProviderState.FAILED:
            return ProviderHealth(status=HealthStatus.UNHEALTHY)
        else:
            return ProviderHealth(status=HealthStatus.UNKNOWN)

    def dispose(self) -> None:
        """Dispose of the provider and release resources."""
        self._state = ProviderState.DISPOSED


class CommitObservationProvider(GitObservationProvider):
    """OPA §9.4 — Concrete base for commit observation providers."""

    @abstractmethod
    def extract_commits(
        self,
        context: ProviderContext,
        since: Optional[str] = None,
        until: Optional[str] = None,
        exclude_bots: bool = False,
    ) -> ExtractionResult:
        """Extract commit observations."""
        ...

    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the specified metrics.

        Default implementation delegates to extract_commits.
        """
        return self.extract_commits(
            context,
            since=context.since.isoformat() if context.since else None,
            until=context.until.isoformat() if context.until else None,
            exclude_bots=context.exclude_bots,
        )
