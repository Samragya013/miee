"""Tests for miie.providers.base module."""

import pytest

from miie.providers.base import BaseGitProvider, BaseObservationProvider, ProviderMixin
from miie.providers.context import (
    ExtractionResult,
    HealthStatus,
    ProviderCapability,
    ProviderContext,
    ProviderState,
)


class TestProviderMixin:
    def test_timing_context(self):
        mixin = ProviderMixin()
        with mixin.timing_context("test") as timer:
            assert timer["operation"] == "test"
            assert timer["elapsed_ms"] == 0.0

    def test_error_handler_reraises(self):
        mixin = ProviderMixin()
        with pytest.raises(Exception):
            with mixin.error_handler("test-provider", "M-02"):
                raise ValueError("boom")


class ConcreteObservationProvider(BaseObservationProvider):
    """Concrete implementation for testing."""

    def extract(self, context: ProviderContext, metric_ids: list) -> ExtractionResult:
        return ExtractionResult(
            provider_id=self.provider_id,
            metric_id="M-02",
            observations=(1, 2, 3),
        )


class ConcreteGitProvider(BaseGitProvider):
    """Concrete implementation for testing."""

    def extract_observations(self, context: ProviderContext, metric_ids: list) -> ExtractionResult:
        return ExtractionResult(
            provider_id=self.provider_id,
            metric_id="M-02",
            observations=(1, 2, 3),
        )


class TestBaseObservationProvider:
    def test_initialization(self):
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        assert provider.provider_id == "test"
        assert provider.state == ProviderState.UNINITIALIZED

    def test_initialize(self):
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        provider.initialize(ctx)
        assert provider.state == ProviderState.READY

    def test_extract(self):
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        result = provider.extract(ctx, ["M-02"])
        assert result.observation_count == 3

    def test_dispose(self):
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        provider.dispose()
        assert provider.state == ProviderState.DISPOSED

    def test_is_healthy(self):
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        # health_check maps state to status; UNINITIALIZED -> UNKNOWN
        assert provider.health_check().status == HealthStatus.UNKNOWN
        provider.initialize(
            ProviderContext(
                repo_path="/tmp",
                repository_id="repo",
                analysis_id="a1",
            )
        )
        assert provider.health_check().status == HealthStatus.HEALTHY
        provider.dispose()
        assert provider.health_check().status == HealthStatus.UNKNOWN

    def test_get_health(self):
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        provider.initialize(
            ProviderContext(
                repo_path="/tmp",
                repository_id="repo",
                analysis_id="a1",
            )
        )
        health = provider.health_check()
        assert health is not None
        assert health.status == HealthStatus.HEALTHY

    def test_get_capability(self):
        cap = ProviderCapability(
            supported_metrics=frozenset(["M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=cap,
        )
        assert provider.get_capabilities() is cap

    def test_supports_metric(self):
        provider = ConcreteObservationProvider(
            provider_id="test",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        assert provider.supports_metric("M-02")
        assert not provider.supports_metric("M-03")

    def test_empty_provider_id_raises(self):
        with pytest.raises(ValueError):
            ConcreteObservationProvider(
                provider_id="",
                capabilities=ProviderCapability(
                    supported_metrics=frozenset(["M-02"]),
                    supported_source_types=frozenset(["commit"]),
                ),
            )


class TestBaseGitProvider:
    def test_initialization(self):
        provider = ConcreteGitProvider(
            provider_id="test-git",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        assert provider.provider_id == "test-git"
        assert provider.state == ProviderState.UNINITIALIZED

    def test_initialize(self):
        provider = ConcreteGitProvider(
            provider_id="test-git",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        provider.initialize(ctx)
        assert provider.state == ProviderState.READY

    def test_extract(self):
        provider = ConcreteGitProvider(
            provider_id="test-git",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        result = provider.extract(ctx, ["M-02"])
        assert result.observation_count == 3

    def test_is_git_provider(self):
        provider = ConcreteGitProvider(
            provider_id="test-git",
            capabilities=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        assert isinstance(provider, BaseGitProvider)
