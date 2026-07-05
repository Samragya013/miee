"""Tests for miie.providers.capabilities module."""

import pytest

from miie.providers.capabilities import (
    CapabilityCompatibility,
    CapabilityDiscovery,
    CapabilityNegotiator,
    MetricSupport,
    ProviderCapabilities,
    ProviderStateInfo,
    ProviderVersion,
    SupportedSources,
)
from miie.providers.context import (
    HealthStatus,
    PriorityLevel,
    ProviderCapability,
    ProviderEntry,
    ProviderHealth,
    ProviderState,
)


class TestMetricSupport:
    def test_creation(self):
        ms = MetricSupport(metric_id="M-02", min_confidence=0.8, max_confidence=1.0)
        assert ms.metric_id == "M-02"
        assert ms.min_confidence == 0.8

    def test_invalid_min_confidence(self):
        with pytest.raises(ValueError):
            MetricSupport(metric_id="M-02", min_confidence=-0.1)

    def test_min_greater_than_max(self):
        with pytest.raises(ValueError):
            MetricSupport(metric_id="M-02", min_confidence=0.9, max_confidence=0.5)


class TestProviderVersion:
    def test_creation(self):
        v = ProviderVersion(1, 2, 3)
        assert v.major == 1
        assert str(v) == "1.2.3"

    def test_compatible_same_major(self):
        v1 = ProviderVersion(1, 0, 0)
        v2 = ProviderVersion(1, 5, 0)
        assert v1.is_compatible(v2)

    def test_incompatible_different_major(self):
        v1 = ProviderVersion(1, 0, 0)
        v2 = ProviderVersion(2, 0, 0)
        assert not v1.is_compatible(v2)


class TestSupportedSources:
    def test_supports_source_type(self):
        sources = SupportedSources(source_types=frozenset(["commit", "file"]))
        assert sources.supports_source_type("commit")
        assert not sources.supports_source_type("branch")


class TestProviderStateInfo:
    def test_available(self):
        info = ProviderStateInfo.available(ProviderState.READY)
        assert info.is_available is True

    def test_unavailable(self):
        info = ProviderStateInfo.unavailable(ProviderState.FAILED, "error")
        assert info.is_available is False
        assert info.reason == "error"


class TestProviderCapabilities:
    def test_creation(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        assert caps.supports_metric("M-01")
        assert not caps.supports_metric("M-03")

    def test_has_capability(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
            capabilities=frozenset(["git-native"]),
        )
        assert caps.has_capability("git-native")
        assert not caps.has_capability("api-required")

    def test_get_metric_support(self):
        ms = MetricSupport(metric_id="M-02", min_confidence=0.8)
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
            metric_supports=frozenset([ms]),
        )
        assert caps.get_metric_support("M-02") is ms
        assert caps.get_metric_support("M-01") is None

    def test_to_provider_capability(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        base = caps.to_provider_capability()
        assert isinstance(base, ProviderCapability)
        assert base.supports_metric("M-02")


class TestCapabilityNegotiator:
    def test_calculate_compatibility_score(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        score = CapabilityNegotiator.calculate_compatibility_score(caps, frozenset(["M-01", "M-02"]))
        assert score == 1.0

    def test_calculate_compatibility_partial(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-01"]),
            supported_source_types=frozenset(["commit"]),
        )
        score = CapabilityNegotiator.calculate_compatibility_score(caps, frozenset(["M-01", "M-02"]))
        assert 0.0 < score < 1.0

    def test_select_best_provider(self):
        entry1 = ProviderEntry(
            provider_id="git",
            provider="mock",
            capability=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
            priority=PriorityLevel.HIGH,
            health=ProviderHealth(status=HealthStatus.HEALTHY),
        )
        entry2 = ProviderEntry(
            provider_id="coverage",
            provider="mock",
            capability=ProviderCapability(
                supported_metrics=frozenset(["M-04"]),
                supported_source_types=frozenset(["ci"]),
            ),
            priority=PriorityLevel.LOW,
            health=ProviderHealth(status=HealthStatus.HEALTHY),
        )
        best = CapabilityNegotiator.select_best_provider([entry1, entry2], frozenset(["M-02"]))
        assert best is not None
        assert best.provider_id == "git"

    def test_select_best_provider_none_usable(self):
        entry = ProviderEntry(
            provider_id="git",
            provider="mock",
            capability=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
            health=ProviderHealth(status=HealthStatus.UNHEALTHY),
        )
        best = CapabilityNegotiator.select_best_provider([entry], frozenset(["M-02"]))
        assert best is None


class TestCapabilityDiscovery:
    def test_register_and_find(self):
        discovery = CapabilityDiscovery()
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        discovery.register(caps)
        assert discovery.get("git") is caps

    def test_unregister(self):
        discovery = CapabilityDiscovery()
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        discovery.register(caps)
        discovery.unregister("git")
        assert discovery.get("git") is None

    def test_find_providers_for_metric(self):
        discovery = CapabilityDiscovery()
        caps1 = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        caps2 = ProviderCapabilities(
            provider_id="coverage",
            supported_metrics=frozenset(["M-04"]),
            supported_source_types=frozenset(["ci"]),
        )
        discovery.register(caps1)
        discovery.register(caps2)
        providers = discovery.find_providers_for_metric("M-02")
        assert len(providers) == 1
        assert providers[0].provider_id == "git"

    def test_get_all(self):
        discovery = CapabilityDiscovery()
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        discovery.register(caps)
        all_caps = discovery.get_all()
        assert len(all_caps) == 1


class TestCapabilityCompatibility:
    def test_check_metric_compatibility(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        result = CapabilityCompatibility.check_metric_compatibility(caps, frozenset(["M-01", "M-02", "M-03"]))
        assert result["M-01"] is True
        assert result["M-02"] is True
        assert result["M-03"] is False

    def test_check_source_compatibility(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        result = CapabilityCompatibility.check_source_compatibility(caps, frozenset(["commit", "file"]))
        assert result["commit"] is True
        assert result["file"] is False

    def test_check_version_compatibility(self):
        v1 = ProviderVersion(1, 0, 0)
        v2 = ProviderVersion(1, 5, 0)
        assert CapabilityCompatibility.check_version_compatibility(v1, v2)

    def test_is_fully_compatible(self):
        caps = ProviderCapabilities(
            provider_id="git",
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        assert CapabilityCompatibility.is_fully_compatible(caps, frozenset(["M-01"]), frozenset(["commit"]))
        assert not CapabilityCompatibility.is_fully_compatible(caps, frozenset(["M-01", "M-03"]))
