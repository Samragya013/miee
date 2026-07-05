"""Tests for miie.contracts.observation_interfaces module."""

from typing import Any, Dict, FrozenSet, List, Optional
from unittest.mock import MagicMock

import pytest

from miie.contracts.observation_interfaces import (
    CommitObservationProvider,
    GitObservationProvider,
    IGitProvider,
    IObservationProvider,
    IObservationTransformer,
    IObservationValidator,
    IProviderFactory,
    IProviderHealthReporter,
    IProviderRegistry,
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


class TestIObservationProvider:
    """Test IObservationProvider Protocol."""

    def test_is_protocol(self):
        """Test IObservationProvider is a Protocol."""
        assert hasattr(IObservationProvider, "_is_protocol")

    def test_runtime_checkable(self):
        """Test IObservationProvider is runtime_checkable."""

        # Create a mock that implements the protocol
        class MockProvider:
            @property
            def provider_id(self) -> str:
                return "mock-provider"

            @property
            def state(self) -> ProviderState:
                return ProviderState.READY

            def supports_metric(self, metric_id: str) -> bool:
                return True

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-01"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def initialize(self, context: ProviderContext) -> None:
                pass

            def extract_observations(
                self,
                context: ProviderContext,
                metric_ids: List[str],
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id="mock-provider",
                    metric_id="M-01",
                    observations=(),
                )

            def health_check(self) -> ProviderHealth:
                return ProviderHealth(status=HealthStatus.HEALTHY)

            def dispose(self) -> None:
                pass

        provider = MockProvider()
        assert isinstance(provider, IObservationProvider)


class TestIGitProvider:
    """Test IGitProvider Protocol."""

    def test_is_protocol(self):
        """Test IGitProvider is a Protocol."""
        assert hasattr(IGitProvider, "_is_protocol")

    def test_runtime_checkable(self):
        """Test IGitProvider is runtime_checkable."""

        # Create a mock that implements the protocol
        class MockGitProvider:
            @property
            def provider_id(self) -> str:
                return "mock-git-provider"

            @property
            def state(self) -> ProviderState:
                return ProviderState.READY

            def supports_metric(self, metric_id: str) -> bool:
                return True

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-01"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def initialize(self, context: ProviderContext) -> None:
                pass

            def extract_observations(
                self,
                context: ProviderContext,
                metric_ids: List[str],
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id="mock-git-provider",
                    metric_id="M-01",
                    observations=(),
                )

            def health_check(self) -> ProviderHealth:
                return ProviderHealth(status=HealthStatus.HEALTHY)

            def dispose(self) -> None:
                pass

            def extract_commits(
                self,
                context: ProviderContext,
                since: Optional[str] = None,
                until: Optional[str] = None,
                exclude_bots: bool = False,
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id="mock-git-provider",
                    metric_id="M-02",
                    observations=(),
                )

            def extract_branches(self, context: ProviderContext) -> ExtractionResult:
                return ExtractionResult(
                    provider_id="mock-git-provider",
                    metric_id="M-07",
                    observations=(),
                )

            def extract_tags(self, context: ProviderContext) -> ExtractionResult:
                return ExtractionResult(
                    provider_id="mock-git-provider",
                    metric_id="M-07",
                    observations=(),
                )

        provider = MockGitProvider()
        assert isinstance(provider, IGitProvider)
        assert isinstance(provider, IObservationProvider)


class TestIObservationValidator:
    """Test IObservationValidator Protocol."""

    def test_is_protocol(self):
        """Test IObservationValidator is a Protocol."""
        assert hasattr(IObservationValidator, "_is_protocol")

    def test_runtime_checkable(self):
        """Test IObservationValidator is runtime_checkable."""

        class MockValidator:
            def validate_observation(
                self,
                observation: Any,
                metric_id: str,
            ) -> ValidationResult:
                return ValidationResult.success()

            def validate_batch(
                self,
                observations: List[Any],
                metric_id: str,
            ) -> List[ValidationResult]:
                return [ValidationResult.success() for _ in observations]

            def get_validation_rules(self, metric_id: str) -> List[Any]:
                return []

        validator = MockValidator()
        assert isinstance(validator, IObservationValidator)


class TestIObservationTransformer:
    """Test IObservationTransformer Protocol."""

    def test_is_protocol(self):
        """Test IObservationTransformer is a Protocol."""
        assert hasattr(IObservationTransformer, "_is_protocol")

    def test_runtime_checkable(self):
        """Test IObservationTransformer is runtime_checkable."""

        class MockTransformer:
            def transform_to_internal(
                self,
                observation: Any,
                source_format: str,
            ) -> Any:
                return observation

            def transform_batch(
                self,
                observations: List[Any],
                source_format: str,
            ) -> List[Any]:
                return observations

            def get_supported_formats(self) -> FrozenSet[str]:
                return frozenset({"json", "csv"})

        transformer = MockTransformer()
        assert isinstance(transformer, IObservationTransformer)


class TestIProviderHealthReporter:
    """Test IProviderHealthReporter Protocol."""

    def test_is_protocol(self):
        """Test IProviderHealthReporter is a Protocol."""
        assert hasattr(IProviderHealthReporter, "_is_protocol")

    def test_runtime_checkable(self):
        """Test IProviderHealthReporter is runtime_checkable."""

        class MockHealthReporter:
            def report_health(
                self,
                provider_id: str,
                health: ProviderHealth,
            ) -> None:
                pass

            def get_health(self, provider_id: str) -> Optional[ProviderHealth]:
                return None

            def reset_health(self, provider_id: str) -> None:
                pass

        reporter = MockHealthReporter()
        assert isinstance(reporter, IProviderHealthReporter)


class TestIProviderRegistry:
    """Test IProviderRegistry Protocol."""

    def test_is_protocol(self):
        """Test IProviderRegistry is a Protocol."""
        assert hasattr(IProviderRegistry, "_is_protocol")

    def test_runtime_checkable(self):
        """Test IProviderRegistry is runtime_checkable."""

        class MockRegistry:
            def register(
                self,
                provider: IObservationProvider,
                capability: ProviderCapability,
                priority: PriorityLevel = PriorityLevel.MEDIUM,
                config: Optional[Dict[str, Any]] = None,
            ) -> None:
                pass

            def unregister(self, provider_id: str) -> None:
                pass

            def get_provider(self, provider_id: str) -> Optional[IObservationProvider]:
                return None

            def discover(self, metric_id: str) -> List[IObservationProvider]:
                return []

            def get_all(self) -> List[ProviderEntry]:
                return []

            def get_by_metric(self, metric_id: str) -> List[ProviderEntry]:
                return []

            def get_healthy_providers(self, metric_id: str) -> List[IObservationProvider]:
                return []

        registry = MockRegistry()
        assert isinstance(registry, IProviderRegistry)


class TestIProviderFactory:
    """Test IProviderFactory Protocol."""

    def test_is_protocol(self):
        """Test IProviderFactory is a Protocol."""
        assert hasattr(IProviderFactory, "_is_protocol")

    def test_runtime_checkable(self):
        """Test IProviderFactory is runtime_checkable."""

        class MockFactory:
            def create_provider(
                self,
                provider_class: str,
                config: Dict[str, Any],
            ) -> IObservationProvider:
                # Return a mock provider
                mock = MagicMock()
                mock.provider_id = "mock-provider"
                return mock

            def validate_config(
                self,
                provider_class: str,
                config: Dict[str, Any],
            ) -> ValidationResult:
                return ValidationResult.success()

            def get_provider_type(self, provider_class: str) -> str:
                return "git"

        factory = MockFactory()
        assert isinstance(factory, IProviderFactory)


class TestGitObservationProvider:
    """Test GitObservationProvider abstract base class."""

    def test_cannot_instantiate_directly(self):
        """Test GitObservationProvider cannot be instantiated directly."""
        # GitObservationProvider has abstract method get_capabilities
        # so it cannot be instantiated directly
        pass  # This is tested by the fact that ConcreteGitProvider must implement get_capabilities

    def test_concrete_implementation(self):
        """Test concrete implementation of GitObservationProvider."""

        class ConcreteGitProvider(GitObservationProvider):
            def __init__(self, provider_id: str = "test-provider"):
                super().__init__(provider_id)

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-01"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def extract_observations(
                self,
                context: ProviderContext,
                metric_ids: List[str],
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id=self.provider_id,
                    metric_id="M-01",
                    observations=(),
                )

        provider = ConcreteGitProvider()
        assert provider.provider_id == "test-provider"
        assert provider.state == ProviderState.UNINITIALIZED

    def test_initialization(self):
        """Test provider initialization."""

        class ConcreteGitProvider(GitObservationProvider):
            def __init__(self, provider_id: str = "test-provider"):
                super().__init__(provider_id)

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-01"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def extract_observations(
                self,
                context: ProviderContext,
                metric_ids: List[str],
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id=self.provider_id,
                    metric_id="M-01",
                    observations=(),
                )

        provider = ConcreteGitProvider()
        assert provider.state == ProviderState.UNINITIALIZED

        ctx = ProviderContext(
            repo_path="/path/to/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        provider.initialize(ctx)
        assert provider.state == ProviderState.READY

    def test_health_check(self):
        """Test health check."""

        class ConcreteGitProvider(GitObservationProvider):
            def __init__(self, provider_id: str = "test-provider"):
                super().__init__(provider_id)

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-01"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def extract_observations(
                self,
                context: ProviderContext,
                metric_ids: List[str],
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id=self.provider_id,
                    metric_id="M-01",
                    observations=(),
                )

        provider = ConcreteGitProvider()
        # Before initialization, state is UNINITIALIZED -> UNKNOWN health
        health = provider.health_check()
        assert health.status == HealthStatus.UNKNOWN

        # After initialization, state is READY -> HEALTHY health
        ctx = ProviderContext(
            repo_path="/path/to/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        provider.initialize(ctx)
        health = provider.health_check()
        assert health.status == HealthStatus.HEALTHY

    def test_dispose(self):
        """Test provider disposal."""

        class ConcreteGitProvider(GitObservationProvider):
            def __init__(self, provider_id: str = "test-provider"):
                super().__init__(provider_id)

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-01"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def extract_observations(
                self,
                context: ProviderContext,
                metric_ids: List[str],
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id=self.provider_id,
                    metric_id="M-01",
                    observations=(),
                )

        provider = ConcreteGitProvider()
        provider.dispose()
        assert provider.state == ProviderState.DISPOSED

    def test_supports_metric(self):
        """Test supports_metric method."""

        class ConcreteGitProvider(GitObservationProvider):
            def __init__(self, provider_id: str = "test-provider"):
                super().__init__(provider_id)

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-01", "M-02"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def extract_observations(
                self,
                context: ProviderContext,
                metric_ids: List[str],
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id=self.provider_id,
                    metric_id="M-01",
                    observations=(),
                )

        provider = ConcreteGitProvider()
        assert provider.supports_metric("M-01") is True
        assert provider.supports_metric("M-02") is True
        assert provider.supports_metric("M-03") is False


class TestCommitObservationProvider:
    """Test CommitObservationProvider abstract base class."""

    def test_concrete_implementation(self):
        """Test concrete implementation of CommitObservationProvider."""

        class ConcreteCommitProvider(CommitObservationProvider):
            def __init__(self, provider_id: str = "test-commit-provider"):
                super().__init__(provider_id)

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-02"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def extract_commits(
                self,
                context: ProviderContext,
                since: Optional[str] = None,
                until: Optional[str] = None,
                exclude_bots: bool = False,
            ) -> ExtractionResult:
                return ExtractionResult(
                    provider_id=self.provider_id,
                    metric_id="M-02",
                    observations=(),
                )

        provider = ConcreteCommitProvider()
        assert provider.provider_id == "test-commit-provider"
        assert provider.state == ProviderState.UNINITIALIZED

    def test_extract_observations_delegates(self):
        """Test extract_observations delegates to extract_commits."""

        class ConcreteCommitProvider(CommitObservationProvider):
            def __init__(self):
                super().__init__("test-provider")
                self.extract_commits_called = False
                self.extract_commits_kwargs = {}

            def get_capabilities(self) -> ProviderCapability:
                return ProviderCapability(
                    supported_metrics=frozenset({"M-02"}),
                    supported_source_types=frozenset({"commit"}),
                )

            def extract_commits(
                self,
                context: ProviderContext,
                since: Optional[str] = None,
                until: Optional[str] = None,
                exclude_bots: bool = False,
            ) -> ExtractionResult:
                self.extract_commits_called = True
                self.extract_commits_kwargs = {
                    "since": since,
                    "until": until,
                    "exclude_bots": exclude_bots,
                }
                return ExtractionResult(
                    provider_id=self.provider_id,
                    metric_id="M-02",
                    observations=(),
                )

        provider = ConcreteCommitProvider()
        ctx = ProviderContext(
            repo_path="/path/to/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        provider.initialize(ctx)

        result = provider.extract_observations(ctx, ["M-02"])
        assert provider.extract_commits_called is True
        assert result.provider_id == "test-provider"
