"""
MIIE v1.6 Observation Interfaces — Protocol definitions for Observation Provider Architecture.

Implements OPC-v1.0 §3 and OPA-v1.0 §9 interface definitions.
All observation providers must conform to these Protocol classes.

Reference: OPC-v1.0, OPA-v1.0, OPR-v1.0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, FrozenSet, List, Optional, Protocol, runtime_checkable

from miie.contracts.observation_errors import (
    ExtractionError,
    ProviderError,
    ValidationError,
)
from miie.contracts.observation_types import (
    ExtractionResult,
    HealthStatus,
    ObservationMetrics,
    PriorityLevel,
    ProviderCapability,
    ProviderContext,
    ProviderEntry,
    ProviderHealth,
    ProviderState,
    QualityState,
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
        """Check if this provider supports the given metric.

        Args:
            metric_id: Metric identifier (e.g., "M-01").

        Returns:
            True if the provider can extract this metric.
        """
        ...

    def get_capabilities(self) -> ProviderCapability:
        """Get the capabilities of this provider.

        Returns:
            ProviderCapability declaring supported metrics and features.
        """
        ...

    def initialize(self, context: ProviderContext) -> None:
        """Initialize the provider with extraction context.

        Args:
            context: Provider context with repository and analysis info.

        Raises:
            ProviderError: If initialization fails.
        """
        ...

    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the specified metrics.

        Args:
            context: Provider context with repository and analysis info.
            metric_ids: List of metric identifiers to extract.

        Returns:
            ExtractionResult containing observations and metadata.

        Raises:
            ExtractionError: If extraction fails.
            ProviderError: If provider is not in valid state.
        """
        ...

    def health_check(self) -> ProviderHealth:
        """Check the health status of this provider.

        Returns:
            ProviderHealth with current health information.
        """
        ...

    def dispose(self) -> None:
        """Dispose of the provider and release resources.

        After disposal, the provider cannot be used for extraction.
        """
        ...


# ---------------------------------------------------------------------------
# IGitProvider (OPA §9.2)
# ---------------------------------------------------------------------------


@runtime_checkable
class IGitProvider(IObservationProvider, Protocol):
    """OPA §9.2 — Git-specific observation provider interface.

    Extends base provider with Git-specific extraction capabilities.
    """

    def extract_commits(
        self,
        context: ProviderContext,
        since: Optional[str] = None,
        until: Optional[str] = None,
        exclude_bots: bool = False,
    ) -> ExtractionResult:
        """Extract commit observations.

        Args:
            context: Provider context.
            since: Start commit SHA (exclusive).
            until: End commit SHA (inclusive).
            exclude_bots: Whether to exclude bot commits.

        Returns:
            ExtractionResult with commit observations.
        """
        ...

    def extract_branches(self, context: ProviderContext) -> ExtractionResult:
        """Extract branch observations.

        Args:
            context: Provider context.

        Returns:
            ExtractionResult with branch observations.
        """
        ...

    def extract_tags(self, context: ProviderContext) -> ExtractionResult:
        """Extract tag observations.

        Args:
            context: Provider context.

        Returns:
            ExtractionResult with tag observations.
        """
        ...


# ---------------------------------------------------------------------------
# IObservationValidator (OPC §3.2)
# ---------------------------------------------------------------------------


@runtime_checkable
class IObservationValidator(Protocol):
    """OPC §3.2 — Observation validation interface.

    Validates observations against schema, range, and freshness rules.
    """

    def validate_observation(
        self,
        observation: Any,
        metric_id: str,
    ) -> ValidationResult:
        """Validate a single observation.

        Args:
            observation: Observation to validate.
            metric_id: Metric identifier for validation rules.

        Returns:
            ValidationResult with validation status.
        """
        ...

    def validate_batch(
        self,
        observations: List[Any],
        metric_id: str,
    ) -> List[ValidationResult]:
        """Validate a batch of observations.

        Args:
            observations: List of observations to validate.
            metric_id: Metric identifier for validation rules.

        Returns:
            List of ValidationResult, one per observation.
        """
        ...

    def get_validation_rules(self, metric_id: str) -> List[Any]:
        """Get validation rules for a metric.

        Args:
            metric_id: Metric identifier.

        Returns:
            List of validation rule objects.
        """
        ...


# ---------------------------------------------------------------------------
# IObservationTransformer (OPC §3.3)
# ---------------------------------------------------------------------------


@runtime_checkable
class IObservationTransformer(Protocol):
    """OPC §3.3 — Observation transformation interface.

    Transforms observations from provider format to internal format.
    """

    def transform_to_internal(
        self,
        observation: Any,
        source_format: str,
    ) -> Any:
        """Transform a single observation to internal format.

        Args:
            observation: Observation in provider format.
            source_format: Format identifier of the source.

        Returns:
            Observation in internal format.

        Raises:
            ValidationError: If observation cannot be transformed.
        """
        ...

    def transform_batch(
        self,
        observations: List[Any],
        source_format: str,
    ) -> List[Any]:
        """Transform a batch of observations to internal format.

        Args:
            observations: List of observations in provider format.
            source_format: Format identifier of the source.

        Returns:
            List of observations in internal format.
        """
        ...

    def get_supported_formats(self) -> FrozenSet[str]:
        """Get list of supported source formats.

        Returns:
            FrozenSet of format identifiers.
        """
        ...


# ---------------------------------------------------------------------------
# IProviderHealthReporter (OPC §3.4)
# ---------------------------------------------------------------------------


@runtime_checkable
class IProviderHealthReporter(Protocol):
    """OPC §3.4 — Provider health reporting interface.

    Tracks and reports provider health status.
    """

    def report_health(
        self,
        provider_id: str,
        health: ProviderHealth,
    ) -> None:
        """Report health status for a provider.

        Args:
            provider_id: Provider identifier.
            health: Health status to report.
        """
        ...

    def get_health(self, provider_id: str) -> Optional[ProviderHealth]:
        """Get health status for a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            ProviderHealth if provider exists, None otherwise.
        """
        ...

    def reset_health(self, provider_id: str) -> None:
        """Reset health status for a provider.

        Args:
            provider_id: Provider identifier.
        """
        ...


# ---------------------------------------------------------------------------
# IProviderRegistry (OPC §3.5, OPR §6.1)
# ---------------------------------------------------------------------------


@runtime_checkable
class IProviderRegistry(Protocol):
    """OPC §3.5 / OPR §6.1 — Provider registry interface.

    Manages provider registration, discovery, and lifecycle.
    """

    def register(
        self,
        provider: IObservationProvider,
        capability: ProviderCapability,
        priority: PriorityLevel = PriorityLevel.MEDIUM,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a provider with the registry.

        Args:
            provider: Provider instance to register.
            capability: Provider capabilities.
            priority: Provider priority level.
            config: Optional provider configuration.

        Raises:
            RegistrationError: If registration fails.
            DuplicateProviderError: If provider ID already registered.
        """
        ...

    def unregister(self, provider_id: str) -> None:
        """Unregister a provider from the registry.

        Args:
            provider_id: Provider identifier to unregister.

        Raises:
            ProviderNotFoundError: If provider not found.
        """
        ...

    def get_provider(self, provider_id: str) -> Optional[IObservationProvider]:
        """Get a provider by ID.

        Args:
            provider_id: Provider identifier.

        Returns:
            Provider instance if found, None otherwise.
        """
        ...

    def discover(self, metric_id: str) -> List[IObservationProvider]:
        """Discover providers that support a metric, ordered by priority.

        Args:
            metric_id: Metric identifier.

        Returns:
            List of providers ordered by priority (highest first).
        """
        ...

    def get_all(self) -> List[ProviderEntry]:
        """Get all registered providers.

        Returns:
            List of ProviderEntry for all registered providers.
        """
        ...

    def get_by_metric(self, metric_id: str) -> List[ProviderEntry]:
        """Get providers that support a metric.

        Args:
            metric_id: Metric identifier.

        Returns:
            List of ProviderEntry ordered by priority.
        """
        ...

    def get_healthy_providers(self, metric_id: str) -> List[IObservationProvider]:
        """Get healthy providers that support a metric.

        Args:
            metric_id: Metric identifier.

        Returns:
            List of healthy providers ordered by priority.
        """
        ...


# ---------------------------------------------------------------------------
# IProviderFactory (OPR §7.3)
# ---------------------------------------------------------------------------


@runtime_checkable
class IProviderFactory(Protocol):
    """OPR §7.3 — Provider factory interface.

    Creates and validates provider instances from configuration.
    """

    def create_provider(
        self,
        provider_class: str,
        config: Dict[str, Any],
    ) -> IObservationProvider:
        """Create a provider instance from configuration.

        Args:
            provider_class: Fully qualified provider class name.
            config: Provider configuration.

        Returns:
            Configured provider instance.

        Raises:
            ConfigurationError: If configuration is invalid.
            ProviderError: If creation fails.
        """
        ...

    def validate_config(
        self,
        provider_class: str,
        config: Dict[str, Any],
    ) -> ValidationResult:
        """Validate provider configuration.

        Args:
            provider_class: Fully qualified provider class name.
            config: Provider configuration to validate.

        Returns:
            ValidationResult with validation status.
        """
        ...

    def get_provider_type(self, provider_class: str) -> str:
        """Get the type of a provider class.

        Args:
            provider_class: Fully qualified provider class name.

        Returns:
            Provider type string (e.g., "git", "static_analysis").
        """
        ...


# ---------------------------------------------------------------------------
# Abstract Base Classes (OPA §9.3)
# ---------------------------------------------------------------------------


class GitObservationProvider(ABC):
    """OPA §9.3 — Abstract base for Git observation providers.

    Provides common implementation for Git-based providers.
    Concrete providers inherit from this class.
    """

    def __init__(self, provider_id: str) -> None:
        """Initialize the Git observation provider.

        Args:
            provider_id: Unique identifier for this provider.
        """
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
        """Check if this provider supports the given metric.

        Default implementation checks provider capability.
        Subclasses should override for specific metric support.
        """
        capabilities = self.get_capabilities()
        return capabilities.supports_metric(metric_id)

    @abstractmethod
    def get_capabilities(self) -> ProviderCapability:
        """Get the capabilities of this provider.

        Must be implemented by subclasses to declare supported metrics.
        """
        ...

    def initialize(self, context: ProviderContext) -> None:
        """Initialize the provider with extraction context.

        Default implementation sets state to READY.
        Subclasses should call super().initialize() and add custom logic.
        """
        self._state = ProviderState.READY

    @abstractmethod
    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the specified metrics.

        Must be implemented by subclasses.
        """
        ...

    def health_check(self) -> ProviderHealth:
        """Check the health status of this provider.

        Default implementation returns HEALTHY if state is READY or ACTIVE.
        Subclasses should override for custom health checks.
        """
        if self._state in (ProviderState.READY, ProviderState.ACTIVE):
            return ProviderHealth(status=HealthStatus.HEALTHY)
        elif self._state == ProviderState.DEGRADED:
            return ProviderHealth(status=HealthStatus.DEGRADED)
        elif self._state == ProviderState.FAILED:
            return ProviderHealth(status=HealthStatus.UNHEALTHY)
        else:
            return ProviderHealth(status=HealthStatus.UNKNOWN)

    def dispose(self) -> None:
        """Dispose of the provider and release resources.

        Default implementation sets state to DISPOSED.
        Subclasses should call super().dispose() and add cleanup logic.
        """
        self._state = ProviderState.DISPOSED


class CommitObservationProvider(GitObservationProvider):
    """OPA §9.4 — Concrete base for commit observation providers.

    Provides common implementation for commit-based extraction.
    Concrete providers inherit from this class.
    """

    @abstractmethod
    def extract_commits(
        self,
        context: ProviderContext,
        since: Optional[str] = None,
        until: Optional[str] = None,
        exclude_bots: bool = False,
    ) -> ExtractionResult:
        """Extract commit observations.

        Must be implemented by subclasses.
        """
        ...

    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the specified metrics.

        Default implementation delegates to extract_commits.
        Subclasses can override for custom extraction logic.
        """
        return self.extract_commits(
            context,
            since=context.since.isoformat() if context.since else None,
            until=context.until.isoformat() if context.until else None,
            exclude_bots=context.exclude_bots,
        )
