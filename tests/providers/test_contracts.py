"""Tests for miie.providers.contracts module."""

import pytest

from miie.providers.context import (
    ExtractionResult,
    HealthStatus,
    ProviderCapability,
    ProviderContext,
    ProviderHealth,
    ProviderState,
)
from miie.providers.contracts import (
    CommitObservationProvider,
    GitObservationProvider,
    IObservationProvider,
)


class TestGitObservationProviderABC:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            GitObservationProvider(provider_id="test")


class TestCommitObservationProviderABC:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            CommitObservationProvider(provider_id="test")


class ConcreteIObservationProvider:
    """Minimal concrete implementation for testing protocols."""

    def __init__(self):
        self.provider_id = "concrete"
        self.provider = "concrete"
        self.state = ProviderState.UNINITIALIZED
        self.capability = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )

    def extract_observations(self, context: ProviderContext, metric_ids: list) -> ExtractionResult:
        return ExtractionResult(
            provider_id=self.provider_id,
            metric_id="M-02",
            observations=(1, 2, 3),
        )

    def initialize(self, context: ProviderContext) -> None:
        self.state = ProviderState.READY

    def dispose(self) -> None:
        self.state = ProviderState.DISPOSED

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(status=HealthStatus.HEALTHY)

    def supports_metric(self, metric_id: str) -> bool:
        return metric_id in self.capability.supported_metrics

    def get_capabilities(self) -> ProviderCapability:
        return self.capability


class TestProtocolConformance:
    def test_concrete_provider_meets_protocol(self):
        provider = ConcreteIObservationProvider()
        assert isinstance(provider, IObservationProvider)
