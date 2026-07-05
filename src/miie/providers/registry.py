"""
MIIE v1.6 Observation Provider Framework — Provider Registry.

Implements OPR §6.1 — central registry for observation providers.
Thread-safe, deterministic provider selection ordered by priority then name.

Classes:
    ObservationProviderRegistry: IProviderRegistry implementation with
        thread-safe registration, discovery, and health tracking.
    DeterministicRegistry: Extended registry with deterministic provider
        selection and fallback chain support.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, FrozenSet, List, Optional

from miie.providers.context import (
    PriorityLevel,
    ProviderCapability,
    ProviderEntry,
    ProviderHealth,
)
from miie.providers.contracts import IObservationProvider
from miie.providers.exceptions import (
    DuplicateProviderError,
    ProviderNotFoundError,
    RegistrationError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _priority_sort_key(entry: ProviderEntry) -> tuple:
    """Sort key: priority ascending (lower int = higher priority), then name."""
    return (entry.priority.value, entry.provider_id)


def _priority_sort_key_entry(provider_id: str, entry: ProviderEntry) -> tuple:
    """Sort key from an (id, entry) pair."""
    return (entry.priority.value, provider_id)


# ---------------------------------------------------------------------------
# ObservationProviderRegistry (OPR §6.1)
# ---------------------------------------------------------------------------


class ObservationProviderRegistry:
    """OPR §6.1 — Thread-safe, deterministic observation provider registry.

    Maintains an internal mapping from provider_id to ProviderEntry.
    All public methods are safe to call from multiple threads; a reentrant
    lock serialises mutations while keeping read-path lock scope minimal.

    Determinism guarantee: for the same set of registered providers the
    same ordering is always returned — first by priority (ascending, lower
    value = higher priority), then lexicographically by provider_id.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, ProviderEntry] = {}
        self._lock = threading.Lock()

    # -- Mutation -----------------------------------------------------------

    def register(
        self,
        provider: IObservationProvider,
        capability: ProviderCapability,
        priority: PriorityLevel = PriorityLevel.MEDIUM,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a provider with the registry.

        Args:
            provider: The provider instance.
            capability: Capability declaration for the provider.
            priority: Priority level (lower = higher priority).
            config: Optional provider-specific configuration.

        Raises:
            DuplicateProviderError: If a provider with the same ID is
                already registered.
            RegistrationError: On any other registration failure.
        """
        if config is None:
            config = {}

        provider_id = provider.provider_id
        if not provider_id:
            raise RegistrationError("Provider must declare a non-empty provider_id")

        with self._lock:
            if provider_id in self._entries:
                raise DuplicateProviderError(f"Provider '{provider_id}' is already registered")
            entry = ProviderEntry(
                provider_id=provider_id,
                provider=provider,
                capability=capability,
                priority=priority,
                config=config,
            )
            self._entries[provider_id] = entry

    def unregister(self, provider_id: str) -> None:
        """Remove a provider from the registry.

        Args:
            provider_id: ID of the provider to remove.

        Raises:
            ProviderNotFoundError: If the provider is not registered.
        """
        with self._lock:
            if provider_id not in self._entries:
                raise ProviderNotFoundError(
                    f"Provider '{provider_id}' not found in registry",
                    provider_id=provider_id,
                )
            del self._entries[provider_id]

    # -- Read ---------------------------------------------------------------

    def get_provider(self, provider_id: str) -> Optional[IObservationProvider]:
        """Get a provider instance by its ID.

        Args:
            provider_id: The provider's unique identifier.

        Returns:
            The provider, or ``None`` if not registered.
        """
        entry = self._entries.get(provider_id)
        if entry is None:
            return None
        return entry.provider  # type: ignore[return-value]

    def discover(self, metric_id: str) -> List[IObservationProvider]:
        """Discover providers that support *metric_id*, ordered by priority.

        Providers with lower ``PriorityLevel`` values come first.  Among
        providers with equal priority the sort is alphabetical by ID.

        Args:
            metric_id: The metric to search for.

        Returns:
            Ordered list of providers supporting the metric.
        """
        with self._lock:
            matches = [entry for entry in self._entries.values() if entry.capability.supports_metric(metric_id)]
            matches.sort(key=_priority_sort_key)
        return [m.provider for m in matches]  # type: ignore[misc]

    def get_all(self) -> List[ProviderEntry]:
        """Get all registered provider entries.

        Returns:
            List of :class:`ProviderEntry` sorted by priority then name.
        """
        with self._lock:
            entries = sorted(self._entries.values(), key=_priority_sort_key)
            return list(entries)

    def get_by_metric(self, metric_id: str) -> List[ProviderEntry]:
        """Get entries supporting *metric_id*, ordered by priority.

        Args:
            metric_id: The metric to filter on.

        Returns:
            Sorted list of matching :class:`ProviderEntry`.
        """
        with self._lock:
            matches = [entry for entry in self._entries.values() if entry.capability.supports_metric(metric_id)]
            matches.sort(key=_priority_sort_key)
            return list(matches)

    def get_healthy_providers(self, metric_id: str) -> List[IObservationProvider]:
        """Get healthy providers for *metric_id*, ordered by priority.

        A provider is considered healthy when its ``ProviderHealth.is_usable``
        flag is ``True``.

        Args:
            metric_id: The metric to filter on.

        Returns:
            Ordered list of healthy providers supporting the metric.
        """
        with self._lock:
            matches = [
                entry
                for entry in self._entries.values()
                if entry.capability.supports_metric(metric_id) and entry.health.is_usable
            ]
            matches.sort(key=_priority_sort_key)
        return [m.provider for m in matches]  # type: ignore[misc]

    def get_entry(self, provider_id: str) -> Optional[ProviderEntry]:
        """Get the full :class:`ProviderEntry` for a provider ID.

        Args:
            provider_id: The provider's unique identifier.

        Returns:
            The entry, or ``None`` if not registered.
        """
        entry = self._entries.get(provider_id)
        if entry is None:
            return None
        return entry

    def update_health(self, provider_id: str, health: ProviderHealth) -> None:
        """Update the health snapshot stored in the registry.

        Args:
            provider_id: The provider whose health to update.
            health: New health snapshot.

        Raises:
            ProviderNotFoundError: If the provider is not registered.
        """
        with self._lock:
            entry = self._entries.get(provider_id)
            if entry is None:
                raise ProviderNotFoundError(
                    f"Provider '{provider_id}' not found in registry",
                    provider_id=provider_id,
                )
            entry.health = health

    def get_priority_order(self, metric_id: str) -> List[str]:
        """Get provider IDs that support *metric_id* in priority order.

        Args:
            metric_id: The metric to filter on.

        Returns:
            List of provider IDs sorted by priority then name.
        """
        with self._lock:
            items = [
                (pid, entry) for pid, entry in self._entries.items() if entry.capability.supports_metric(metric_id)
            ]
            items.sort(key=lambda item: (item[1].priority.value, item[0]))
        return [pid for pid, _ in items]


# ---------------------------------------------------------------------------
# DeterministicRegistry (OPR §6.1, extension)
# ---------------------------------------------------------------------------


class DeterministicRegistry(ObservationProviderRegistry):
    """Extended registry that guarantees deterministic provider selection.

    For the same set of registered providers, metric, and required source
    types the ``select_provider`` method always returns the same provider.
    The fallback chain is similarly stable across calls.

    Determinism is achieved by sorting on (priority, provider_id) and
    applying a strict source-type compatibility filter.
    """

    def select_provider(
        self,
        metric_id: str,
        required_source_types: Optional[FrozenSet[str]] = None,
    ) -> Optional[IObservationProvider]:
        """Deterministically select the best provider for *metric_id*.

        Selection criteria (in order of precedence):

        1. Provider must support the metric.
        2. Provider must be usable (``health.is_usable == True``).
        3. Provider must support every required source type.
        4. Among remaining candidates, pick the one with the lowest
           priority value (highest priority), breaking ties by
           lexicographic provider_id.

        Args:
            metric_id: The metric to select a provider for.
            required_source_types: Source types the provider must support.
                If ``None`` or empty, no source-type filtering is applied.

        Returns:
            The selected provider, or ``None`` if no suitable candidate
            exists.
        """
        if required_source_types is None:
            required_source_types = frozenset()

        with self._lock:
            candidates = []
            for entry in self._entries.values():
                if not entry.capability.supports_metric(metric_id):
                    continue
                if not entry.health.is_usable:
                    continue
                # Source-type check: provider must support every requested type
                if required_source_types:
                    if not all(entry.capability.supports_source_type(st) for st in required_source_types):
                        continue
                candidates.append(entry)

            if not candidates:
                return None

            candidates.sort(key=_priority_sort_key)
            return candidates[0].provider  # type: ignore[return-value]

    def get_fallback_chain(
        self,
        metric_id: str,
        required_source_types: Optional[FrozenSet[str]] = None,
    ) -> List[IObservationProvider]:
        """Build a deterministic fallback chain for *metric_id*.

        Returns an ordered list of usable providers supporting the metric.
        The first element is the highest-priority provider; the last is the
        lowest.  Among equal priorities providers are sorted by ID.

        Args:
            metric_id: The metric to build a fallback chain for.
            required_source_types: Optional source-type constraint applied
                to every candidate.

        Returns:
            Ordered list of providers suitable as fallback targets.
        """
        if required_source_types is None:
            required_source_types = frozenset()

        with self._lock:
            chain: List[ProviderEntry] = []
            for entry in self._entries.values():
                if not entry.capability.supports_metric(metric_id):
                    continue
                if not entry.health.is_usable:
                    continue
                if required_source_types:
                    if not all(entry.capability.supports_source_type(st) for st in required_source_types):
                        continue
                chain.append(entry)

            chain.sort(key=_priority_sort_key)
        return [e.provider for e in chain]  # type: ignore[misc]
