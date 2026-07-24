"""
MIIE v1.6 Observation Provider Framework — Capabilities system.

ProviderCapabilities, capability negotiation, discovery, and compatibility.
Implements OPR §6.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional

from miie.providers.context import (
    CAPABILITY_API_REQUIRED,
    CAPABILITY_BATCH,
    CAPABILITY_GIT_NATIVE,
    CAPABILITY_LOCAL_ONLY,
    CAPABILITY_REAL_TIME,
    CAPABILITY_REMOTE_ONLY,
    ProviderCapability,
    ProviderEntry,
    ProviderState,
)

# ---------------------------------------------------------------------------
# Capability Type Enum
# ---------------------------------------------------------------------------


class CapabilityType:
    """Constants for capability type strings."""

    GIT_NATIVE = CAPABILITY_GIT_NATIVE
    API_REQUIRED = CAPABILITY_API_REQUIRED
    LOCAL_ONLY = CAPABILITY_LOCAL_ONLY
    REMOTE_ONLY = CAPABILITY_REMOTE_ONLY
    REAL_TIME = CAPABILITY_REAL_TIME
    BATCH = CAPABILITY_BATCH


# ---------------------------------------------------------------------------
# Metric Support
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MetricSupport:
    """Declares which metrics a provider supports and with what confidence."""

    metric_id: str
    min_confidence: float = 0.0
    max_confidence: float = 1.0
    requires_external_data: bool = False
    estimated_only: bool = False

    def __post_init__(self) -> None:
        if self.min_confidence < 0.0 or self.min_confidence > 1.0:
            raise ValueError("min_confidence must be in [0.0, 1.0]")
        if self.max_confidence < 0.0 or self.max_confidence > 1.0:
            raise ValueError("max_confidence must be in [0.0, 1.0]")
        if self.min_confidence > self.max_confidence:
            raise ValueError("min_confidence must be <= max_confidence")


# ---------------------------------------------------------------------------
# Provider Version
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderVersion:
    """Version information for a provider."""

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible(self, required: ProviderVersion) -> bool:
        """Check if this version is compatible with required version.

        Uses semver compatibility: same major version required.
        """
        return self.major == required.major


# ---------------------------------------------------------------------------
# Supported Sources
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SupportedSources:
    """Declares which observation sources a provider supports."""

    source_types: FrozenSet[str] = field(default_factory=frozenset)
    file_patterns: FrozenSet[str] = field(default_factory=frozenset)
    branch_patterns: FrozenSet[str] = field(default_factory=frozenset)

    def supports_source_type(self, source_type: str) -> bool:
        """Check if this provider supports a given source type."""
        return source_type in self.source_types


# ---------------------------------------------------------------------------
# Provider State
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderStateInfo:
    """Extended state information for a provider."""

    state: ProviderState
    is_available: bool = True
    reason: Optional[str] = None

    @classmethod
    def available(cls, state: ProviderState = ProviderState.READY) -> ProviderStateInfo:
        """Create an available state."""
        return cls(state=state, is_available=True)

    @classmethod
    def unavailable(cls, state: ProviderState, reason: str = "") -> ProviderStateInfo:
        """Create an unavailable state."""
        return cls(state=state, is_available=False, reason=reason)


# ---------------------------------------------------------------------------
# Provider Capabilities (Extended)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderCapabilities:
    """Extended capabilities declaration for a provider.

    Wraps ProviderCapability with additional metadata and compatibility info.
    """

    provider_id: str
    supported_metrics: FrozenSet[str]
    supported_source_types: FrozenSet[str]
    capabilities: FrozenSet[str] = field(default_factory=frozenset)
    requires_network: bool = False
    requires_api_token: bool = False
    max_observations_per_batch: int = 10000
    version: ProviderVersion = field(default_factory=ProviderVersion)
    metric_supports: FrozenSet[MetricSupport] = field(default_factory=frozenset)
    supported_sources: SupportedSources = field(default_factory=SupportedSources)

    def supports_metric(self, metric_id: str) -> bool:
        """Check if this provider supports a given metric."""
        return metric_id in self.supported_metrics

    def supports_source_type(self, source_type: str) -> bool:
        """Check if this provider supports a given source type."""
        return source_type in self.supported_source_types

    def has_capability(self, capability: str) -> bool:
        """Check if this provider has a specific capability."""
        return capability in self.capabilities

    def get_metric_support(self, metric_id: str) -> Optional[MetricSupport]:
        """Get metric support details for a metric."""
        for ms in self.metric_supports:
            if ms.metric_id == metric_id:
                return ms
        return None

    def to_provider_capability(self) -> ProviderCapability:
        """Convert to base ProviderCapability."""
        return ProviderCapability(
            supported_metrics=self.supported_metrics,
            supported_source_types=self.supported_source_types,
            capabilities=self.capabilities,
            requires_network=self.requires_network,
            requires_api_token=self.requires_api_token,
            max_observations_per_batch=self.max_observations_per_batch,
        )


# ---------------------------------------------------------------------------
# Capability Negotiation
# ---------------------------------------------------------------------------


class CapabilityNegotiator:
    """Negotiates capabilities between providers and consumers.

    Determines which provider is best suited for a given metric
    based on capabilities, priority, and health.
    """

    @staticmethod
    def calculate_compatibility_score(
        provider_caps: ProviderCapabilities,
        required_metrics: FrozenSet[str],
        required_source_types: FrozenSet[str] = frozenset(),
    ) -> float:
        """Calculate compatibility score between provider and requirements.

        Args:
            provider_caps: Provider capabilities.
            required_metrics: Metrics the consumer needs.
            required_source_types: Source types the consumer needs.

        Returns:
            Score from 0.0 (incompatible) to 1.0 (perfect match).
        """
        if not required_metrics:
            return 0.0

        # Calculate metric coverage
        supported_count = sum(1 for m in required_metrics if provider_caps.supports_metric(m))
        metric_score = supported_count / len(required_metrics)

        # Calculate source type coverage
        source_score = 1.0
        if required_source_types:
            source_count = sum(1 for s in required_source_types if provider_caps.supports_source_type(s))
            source_score = source_count / len(required_source_types)

        # Combined score (metrics weighted more heavily)
        return (metric_score * 0.7) + (source_score * 0.3)

    @staticmethod
    def select_best_provider(
        providers: List[ProviderEntry],
        required_metrics: FrozenSet[str],
        required_source_types: FrozenSet[str] = frozenset(),
    ) -> Optional[ProviderEntry]:
        """Select the best provider for given requirements.

        Args:
            providers: Available providers.
            required_metrics: Metrics needed.
            required_source_types: Source types needed.

        Returns:
            Best provider entry, or None if no suitable provider.
        """
        if not providers:
            return None

        scored: List[tuple] = []
        for entry in providers:
            if not entry.health.is_usable:
                continue

            caps = ProviderCapabilities(
                provider_id=entry.provider_id,
                supported_metrics=entry.capability.supported_metrics,
                supported_source_types=entry.capability.supported_source_types,
                capabilities=entry.capability.capabilities,
                requires_network=entry.capability.requires_network,
                requires_api_token=entry.capability.requires_api_token,
                max_observations_per_batch=entry.capability.max_observations_per_batch,
            )

            compat_score = CapabilityNegotiator.calculate_compatibility_score(
                caps, required_metrics, required_source_types
            )

            # Priority score (lower priority value = higher priority)
            priority_score = 1.0 / entry.priority.value

            # Health score
            health_score = entry.health.health_score

            # Combined score
            total_score = (compat_score * 0.5) + (priority_score * 0.3) + (health_score * 0.2)
            scored.append((total_score, entry))

        if not scored:
            return None

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]


# ---------------------------------------------------------------------------
# Capability Discovery
# ---------------------------------------------------------------------------


class CapabilityDiscovery:
    """Discovers and catalogs provider capabilities."""

    def __init__(self) -> None:
        self._capabilities: Dict[str, ProviderCapabilities] = {}

    def register(self, capabilities: ProviderCapabilities) -> None:
        """Register provider capabilities."""
        self._capabilities[capabilities.provider_id] = capabilities

    def unregister(self, provider_id: str) -> None:
        """Unregister provider capabilities."""
        self._capabilities.pop(provider_id, None)

    def get(self, provider_id: str) -> Optional[ProviderCapabilities]:
        """Get capabilities for a provider."""
        return self._capabilities.get(provider_id)

    def find_providers_for_metric(self, metric_id: str) -> List[ProviderCapabilities]:
        """Find all providers that support a metric."""
        return [caps for caps in self._capabilities.values() if caps.supports_metric(metric_id)]

    def find_providers_for_source_type(self, source_type: str) -> List[ProviderCapabilities]:
        """Find all providers that support a source type."""
        return [caps for caps in self._capabilities.values() if caps.supports_source_type(source_type)]

    def get_all(self) -> List[ProviderCapabilities]:
        """Get all registered capabilities."""
        return list(self._capabilities.values())


# ---------------------------------------------------------------------------
# Capability Compatibility
# ---------------------------------------------------------------------------


class CapabilityCompatibility:
    """Checks compatibility between providers and requirements."""

    @staticmethod
    def check_metric_compatibility(
        provider_caps: ProviderCapabilities,
        required_metrics: FrozenSet[str],
    ) -> Dict[str, bool]:
        """Check which required metrics are supported by provider.

        Returns:
            Dict mapping metric_id to whether it's supported.
        """
        return {m: provider_caps.supports_metric(m) for m in required_metrics}

    @staticmethod
    def check_source_compatibility(
        provider_caps: ProviderCapabilities,
        required_sources: FrozenSet[str],
    ) -> Dict[str, bool]:
        """Check which required source types are supported by provider.

        Returns:
            Dict mapping source_type to whether it's supported.
        """
        return {s: provider_caps.supports_source_type(s) for s in required_sources}

    @staticmethod
    def check_version_compatibility(
        provider_version: ProviderVersion,
        required_version: ProviderVersion,
    ) -> bool:
        """Check if provider version meets requirements."""
        return provider_version.is_compatible(required_version)

    @staticmethod
    def is_fully_compatible(
        provider_caps: ProviderCapabilities,
        required_metrics: FrozenSet[str],
        required_sources: FrozenSet[str] = frozenset(),
        required_version: Optional[ProviderVersion] = None,
    ) -> bool:
        """Check if provider is fully compatible with all requirements."""
        # Check metrics
        for m in required_metrics:
            if not provider_caps.supports_metric(m):
                return False

        # Check sources
        for s in required_sources:
            if not provider_caps.supports_source_type(s):
                return False

        # Check version
        if required_version is not None:
            if not provider_caps.version.is_compatible(required_version):
                return False

        return True
