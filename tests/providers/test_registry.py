"""Tests for miie.providers.registry module."""

from unittest.mock import MagicMock

import pytest

from miie.providers.context import (
    HealthStatus,
    PriorityLevel,
    ProviderCapability,
    ProviderHealth,
)
from miie.providers.exceptions import (
    DuplicateProviderError,
    ProviderNotFoundError,
)
from miie.providers.registry import DeterministicRegistry, ObservationProviderRegistry


def make_mock_provider(provider_id, metrics=None, source_types=None):
    """Create a mock provider for testing."""
    provider = MagicMock()
    provider.provider_id = provider_id
    provider.state = MagicMock()
    provider.state.value = "ready"
    caps = ProviderCapability(
        supported_metrics=frozenset(metrics or ["M-02"]),
        supported_source_types=frozenset(source_types or ["commit"]),
    )
    provider.get_capabilities.return_value = caps
    provider.supports_metric = lambda m: m in (metrics or ["M-02"])
    provider.health_check.return_value = ProviderHealth(status=HealthStatus.HEALTHY)
    return provider


class TestObservationProviderRegistry:
    def test_register_and_get(self):
        reg = ObservationProviderRegistry()
        provider = make_mock_provider("git")
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(provider, caps)
        assert reg.get_provider("git") is provider

    def test_register_duplicate_raises(self):
        reg = ObservationProviderRegistry()
        provider = make_mock_provider("git")
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(provider, caps)
        with pytest.raises(DuplicateProviderError):
            reg.register(provider, caps)

    def test_unregister(self):
        reg = ObservationProviderRegistry()
        provider = make_mock_provider("git")
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(provider, caps)
        reg.unregister("git")
        assert reg.get_provider("git") is None

    def test_unregister_not_found_raises(self):
        reg = ObservationProviderRegistry()
        with pytest.raises(ProviderNotFoundError):
            reg.unregister("nonexistent")

    def test_get_provider_not_found(self):
        reg = ObservationProviderRegistry()
        assert reg.get_provider("nonexistent") is None

    def test_discover_by_metric(self):
        reg = ObservationProviderRegistry()
        p1 = make_mock_provider("git", metrics=["M-01", "M-02"])
        p2 = make_mock_provider("coverage", metrics=["M-04", "M-05"])
        caps1 = ProviderCapability(
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        caps2 = ProviderCapability(
            supported_metrics=frozenset(["M-04", "M-05"]),
            supported_source_types=frozenset(["ci"]),
        )
        reg.register(p1, caps1, priority=PriorityLevel.HIGH)
        reg.register(p2, caps2, priority=PriorityLevel.LOW)

        providers = reg.discover("M-02")
        assert len(providers) == 1
        assert providers[0].provider_id == "git"

    def test_discover_ordered_by_priority(self):
        reg = ObservationProviderRegistry()
        p1 = make_mock_provider("slow", metrics=["M-02"])
        p2 = make_mock_provider("fast", metrics=["M-02"])
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(p1, caps, priority=PriorityLevel.LOW)
        reg.register(p2, caps, priority=PriorityLevel.HIGH)

        providers = reg.discover("M-02")
        assert len(providers) == 2
        assert providers[0].provider_id == "fast"
        assert providers[1].provider_id == "slow"

    def test_get_all(self):
        reg = ObservationProviderRegistry()
        p1 = make_mock_provider("git")
        p2 = make_mock_provider("coverage")
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(p1, caps)
        reg.register(p2, caps)

        entries = reg.get_all()
        assert len(entries) == 2

    def test_get_by_metric(self):
        reg = ObservationProviderRegistry()
        p1 = make_mock_provider("git", metrics=["M-02"])
        p2 = make_mock_provider("coverage", metrics=["M-04"])
        caps1 = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        caps2 = ProviderCapability(
            supported_metrics=frozenset(["M-04"]),
            supported_source_types=frozenset(["ci"]),
        )
        reg.register(p1, caps1)
        reg.register(p2, caps2)

        entries = reg.get_by_metric("M-02")
        assert len(entries) == 1
        assert entries[0].provider_id == "git"

    def test_get_healthy_providers(self):
        reg = ObservationProviderRegistry()
        p1 = make_mock_provider("git")
        p2 = make_mock_provider("coverage")
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(p1, caps)
        reg.register(p2, caps)

        # Set health via update_health (not via health_check mock)
        reg.update_health("git", ProviderHealth(status=HealthStatus.HEALTHY))
        reg.update_health("coverage", ProviderHealth(status=HealthStatus.UNHEALTHY))

        healthy = reg.get_healthy_providers("M-02")
        assert len(healthy) == 1
        assert healthy[0].provider_id == "git"

    def test_update_health(self):
        reg = ObservationProviderRegistry()
        provider = make_mock_provider("git")
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(provider, caps)

        new_health = ProviderHealth(status=HealthStatus.DEGRADED, health_score=0.7)
        reg.update_health("git", new_health)

        entry = reg.get_entry("git")
        assert entry.health.status == HealthStatus.DEGRADED

    def test_get_priority_order(self):
        reg = ObservationProviderRegistry()
        p1 = make_mock_provider("git")
        p2 = make_mock_provider("coverage")
        p3 = make_mock_provider("static")
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(p1, caps, priority=PriorityLevel.MEDIUM)
        reg.register(p2, caps, priority=PriorityLevel.HIGH)
        reg.register(p3, caps, priority=PriorityLevel.LOW)

        order = reg.get_priority_order("M-02")
        assert order == ["coverage", "git", "static"]


class TestDeterministicRegistry:
    def test_select_provider(self):
        reg = DeterministicRegistry()
        p1 = make_mock_provider("git", metrics=["M-02"], source_types=["commit"])
        p2 = make_mock_provider("coverage", metrics=["M-04"], source_types=["ci"])
        caps1 = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        caps2 = ProviderCapability(
            supported_metrics=frozenset(["M-04"]),
            supported_source_types=frozenset(["ci"]),
        )
        reg.register(p1, caps1, priority=PriorityLevel.HIGH)
        reg.register(p2, caps2, priority=PriorityLevel.LOW)

        selected = reg.select_provider("M-02")
        assert selected is not None
        assert selected.provider_id == "git"

    def test_select_provider_deterministic(self):
        reg = DeterministicRegistry()
        p1 = make_mock_provider("git", metrics=["M-02"])
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(p1, caps)

        # Should always return the same provider
        for _ in range(10):
            selected = reg.select_provider("M-02")
            assert selected.provider_id == "git"

    def test_get_fallback_chain(self):
        reg = DeterministicRegistry()
        p1 = make_mock_provider("git", metrics=["M-02"])
        p2 = make_mock_provider("fallback", metrics=["M-02"])
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        reg.register(p1, caps, priority=PriorityLevel.HIGH)
        reg.register(p2, caps, priority=PriorityLevel.LOW)

        chain = reg.get_fallback_chain("M-02")
        assert len(chain) == 2
        assert chain[0].provider_id == "git"
        assert chain[1].provider_id == "fallback"
