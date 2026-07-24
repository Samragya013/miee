"""Tests for miie.contracts.observation_types module."""

from dataclasses import FrozenInstanceError

import pytest

from miie.contracts.observation_types import (
    CAPABILITY_API_REQUIRED,
    CAPABILITY_BATCH,
    CAPABILITY_GIT_NATIVE,
    CAPABILITY_LOCAL_ONLY,
    CAPABILITY_REAL_TIME,
    CAPABILITY_REMOTE_ONLY,
    METRIC_BOUNDS,
    VALID_METRIC_IDS,
    VALID_QUALITY_TRANSITIONS,
    ExtractionPhase,
    ExtractionResult,
    HealthStatus,
    MetricBounds,
    ObservationMetrics,
    PriorityLevel,
    ProviderCapability,
    ProviderContext,
    ProviderErrorContext,
    ProviderFactoryResult,
    ProviderHealth,
    ProviderRegistrationConfig,
    ProviderState,
    QualityState,
    QualityStateTransition,
    ValidationResult,
)


class TestProviderState:
    """Test ProviderState enum."""

    def test_all_states_exist(self):
        """Test all expected states are defined."""
        expected = {"uninitialized", "ready", "active", "degraded", "failed", "disposed"}
        actual = {state.value for state in ProviderState}
        assert actual == expected

    def test_state_ordering(self):
        """Test state values are strings."""
        for state in ProviderState:
            assert isinstance(state.value, str)


class TestQualityState:
    """Test QualityState enum."""

    def test_all_states_exist(self):
        """Test all expected states are defined."""
        expected = {"complete", "degraded", "uncertain", "stale", "recovering", "missing"}
        actual = {state.value for state in QualityState}
        assert actual == expected


class TestPriorityLevel:
    """Test PriorityLevel enum."""

    def test_priority_values(self):
        """Test priority values are integers."""
        assert PriorityLevel.CRITICAL.value == 1
        assert PriorityLevel.HIGH.value == 2
        assert PriorityLevel.MEDIUM.value == 3
        assert PriorityLevel.LOW.value == 4
        assert PriorityLevel.BACKGROUND.value == 5

    def test_priority_ordering(self):
        """Test priority ordering (lower = higher priority)."""
        assert PriorityLevel.CRITICAL < PriorityLevel.HIGH
        assert PriorityLevel.HIGH < PriorityLevel.MEDIUM
        assert PriorityLevel.MEDIUM < PriorityLevel.LOW
        assert PriorityLevel.LOW < PriorityLevel.BACKGROUND


class TestProviderContext:
    """Test ProviderContext dataclass."""

    def test_creation(self):
        """Test basic creation."""
        ctx = ProviderContext(
            repo_path="/path/to/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        assert ctx.repo_path == "/path/to/repo"
        assert ctx.repository_id == "repo-123"
        assert ctx.analysis_id == "analysis-456"
        assert ctx.since is None
        assert ctx.until is None
        assert ctx.exclude_bots is False
        assert ctx.config == {}
        assert ctx.timeout_seconds == 30.0

    def test_frozen(self):
        """Test context is frozen."""
        ctx = ProviderContext(
            repo_path="/path/to/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        with pytest.raises(FrozenInstanceError):
            ctx.repo_path = "/new/path"  # type: ignore

    def test_validation_empty_repo_path(self):
        """Test validation fails with empty repo_path."""
        with pytest.raises(ValueError, match="repo_path must not be empty"):
            ProviderContext(
                repo_path="",
                repository_id="repo-123",
                analysis_id="analysis-456",
            )

    def test_validation_empty_repository_id(self):
        """Test validation fails with empty repository_id."""
        with pytest.raises(ValueError, match="repository_id must not be empty"):
            ProviderContext(
                repo_path="/path/to/repo",
                repository_id="",
                analysis_id="analysis-456",
            )

    def test_validation_empty_analysis_id(self):
        """Test validation fails with empty analysis_id."""
        with pytest.raises(ValueError, match="analysis_id must not be empty"):
            ProviderContext(
                repo_path="/path/to/repo",
                repository_id="repo-123",
                analysis_id="",
            )

    def test_validation_negative_timeout(self):
        """Test validation fails with negative timeout."""
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            ProviderContext(
                repo_path="/path/to/repo",
                repository_id="repo-123",
                analysis_id="analysis-456",
                timeout_seconds=-1.0,
            )

    def test_validation_zero_timeout(self):
        """Test validation fails with zero timeout."""
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            ProviderContext(
                repo_path="/path/to/repo",
                repository_id="repo-123",
                analysis_id="analysis-456",
                timeout_seconds=0.0,
            )


class TestProviderCapability:
    """Test ProviderCapability dataclass."""

    def test_creation(self):
        """Test basic creation."""
        cap = ProviderCapability(
            supported_metrics=frozenset({"M-01", "M-02"}),
            supported_source_types=frozenset({"commit"}),
        )
        assert cap.supported_metrics == frozenset({"M-01", "M-02"})
        assert cap.supported_source_types == frozenset({"commit"})
        assert cap.requires_network is False
        assert cap.requires_api_token is False
        assert cap.max_observations_per_batch == 10000

    def test_supports_metric(self):
        """Test supports_metric method."""
        cap = ProviderCapability(
            supported_metrics=frozenset({"M-01", "M-02"}),
            supported_source_types=frozenset({"commit"}),
        )
        assert cap.supports_metric("M-01") is True
        assert cap.supports_metric("M-02") is True
        assert cap.supports_metric("M-03") is False

    def test_supports_source_type(self):
        """Test supports_source_type method."""
        cap = ProviderCapability(
            supported_metrics=frozenset({"M-01"}),
            supported_source_types=frozenset({"commit", "file"}),
        )
        assert cap.supports_source_type("commit") is True
        assert cap.supports_source_type("file") is True
        assert cap.supports_source_type("branch") is False


class TestProviderHealth:
    """Test ProviderHealth dataclass."""

    def test_creation(self):
        """Test basic creation."""
        health = ProviderHealth()
        assert health.status == HealthStatus.UNKNOWN
        assert health.health_score == 1.0
        assert health.consecutive_failures == 0
        assert health.total_extractions == 0
        assert health.successful_extractions == 0
        assert health.failed_extractions == 0

    def test_success_rate_no_extractions(self):
        """Test success rate with no extractions."""
        health = ProviderHealth()
        assert health.success_rate == 1.0

    def test_success_rate_with_extractions(self):
        """Test success rate calculation."""
        health = ProviderHealth(
            total_extractions=10,
            successful_extractions=8,
            failed_extractions=2,
        )
        assert health.success_rate == 0.8

    def test_is_healthy(self):
        """Test is_healthy property."""
        healthy = ProviderHealth(status=HealthStatus.HEALTHY)
        assert healthy.is_healthy is True

        degraded = ProviderHealth(status=HealthStatus.DEGRADED)
        assert degraded.is_healthy is False

    def test_is_usable(self):
        """Test is_usable property."""
        for status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNKNOWN]:
            health = ProviderHealth(status=status)
            assert health.is_usable is True

        for status in [HealthStatus.UNHEALTHY, HealthStatus.DRAINING]:
            health = ProviderHealth(status=status)
            assert health.is_usable is False


class TestMetricBounds:
    """Test MetricBounds dataclass."""

    def test_creation(self):
        """Test basic creation."""
        bounds = MetricBounds(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
            unit="ratio",
        )
        assert bounds.metric_id == "M-01"
        assert bounds.min_value == 0.0
        assert bounds.max_value == 1.0
        assert bounds.unit == "ratio"

    def test_validate_within_bounds(self):
        """Test validation within bounds."""
        bounds = MetricBounds(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
            unit="ratio",
        )
        assert bounds.validate(0.5) is True
        assert bounds.validate(0.0) is True
        assert bounds.validate(1.0) is True

    def test_validate_out_of_bounds(self):
        """Test validation out of bounds."""
        bounds = MetricBounds(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
            unit="ratio",
        )
        assert bounds.validate(-0.1) is False
        assert bounds.validate(1.1) is False

    def test_metric_bounds_registry(self):
        """Test METRIC_BOUNDS contains all metrics."""
        for i in range(1, 8):
            metric_id = f"M-{i:02d}"
            assert metric_id in METRIC_BOUNDS


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_success(self):
        """Test successful validation."""
        result = ValidationResult.success()
        assert result.is_valid is True
        assert result.violations == []
        assert result.warnings == []

    def test_failure(self):
        """Test failed validation."""
        result = ValidationResult.failure(
            ["violation 1", "violation 2"],
            rule_id="VR-TEST",
        )
        assert result.is_valid is False
        assert len(result.violations) == 2
        assert result.rule_id == "VR-TEST"

    def test_with_warnings(self):
        """Test validation with warnings."""
        result = ValidationResult.with_warnings(["warning 1"])
        assert result.is_valid is True
        assert len(result.warnings) == 1


class TestObservationMetrics:
    """Test ObservationMetrics dataclass."""

    def test_creation(self):
        """Test basic creation."""
        metrics = ObservationMetrics(
            metric_id="M-01",
            value=0.5,
            unit="ratio",
        )
        assert metrics.metric_id == "M-01"
        assert metrics.value == 0.5
        assert metrics.unit == "ratio"
        assert metrics.confidence == 1.0
        assert metrics.is_estimated is False

    def test_valid_confidence(self):
        """Test valid confidence values."""
        for conf in [0.0, 0.5, 1.0]:
            metrics = ObservationMetrics(
                metric_id="M-01",
                value=0.5,
                unit="ratio",
                confidence=conf,
            )
            assert metrics.confidence == conf

    def test_invalid_confidence(self):
        """Test invalid confidence values."""
        for conf in [-0.1, 1.1]:
            with pytest.raises(ValueError, match="confidence must be in"):
                ObservationMetrics(
                    metric_id="M-01",
                    value=0.5,
                    unit="ratio",
                    confidence=conf,
                )

    def test_unknown_metric(self):
        """Test unknown metric_id."""
        with pytest.raises(ValueError, match="unknown metric_id"):
            ObservationMetrics(
                metric_id="M-99",
                value=0.5,
                unit="ratio",
            )

    def test_is_valid(self):
        """Test is_valid property."""
        valid = ObservationMetrics(metric_id="M-01", value=0.5, unit="ratio")
        assert valid.is_valid is True

        invalid = ObservationMetrics(metric_id="M-01", value=1.5, unit="ratio")
        assert invalid.is_valid is False


class TestProviderErrorContext:
    """Test ProviderErrorContext dataclass."""

    def test_creation(self):
        """Test basic creation."""
        ctx = ProviderErrorContext(
            provider_id="test-provider",
            metric_id="M-01",
            extraction_phase=ExtractionPhase.EXTRACT,
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        assert ctx.provider_id == "test-provider"
        assert ctx.metric_id == "M-01"
        assert ctx.extraction_phase == ExtractionPhase.EXTRACT
        assert ctx.repository_id == "repo-123"
        assert ctx.analysis_id == "analysis-456"
        assert ctx.timestamp is not None

    def test_frozen(self):
        """Test context is frozen."""
        ctx = ProviderErrorContext(
            provider_id="test-provider",
            metric_id="M-01",
            extraction_phase=ExtractionPhase.EXTRACT,
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        with pytest.raises(FrozenInstanceError):
            ctx.provider_id = "new-provider"  # type: ignore


class TestQualityStateTransition:
    """Test QualityStateTransition dataclass."""

    def test_creation(self):
        """Test basic creation."""
        transition = QualityStateTransition(
            source=QualityState.COMPLETE,
            trigger="data_degradation",
            target=QualityState.DEGRADED,
        )
        assert transition.source == QualityState.COMPLETE
        assert transition.trigger == "data_degradation"
        assert transition.target == QualityState.DEGRADED

    def test_valid_transitions_exist(self):
        """Test VALID_QUALITY_TRANSITIONS is populated."""
        assert len(VALID_QUALITY_TRANSITIONS) > 0

    def test_transition_from_complete(self):
        """Test transitions from COMPLETE state."""
        complete_transitions = [t for t in VALID_QUALITY_TRANSITIONS if t.source == QualityState.COMPLETE]
        assert len(complete_transitions) > 0


class TestExtractionResult:
    """Test ExtractionResult dataclass."""

    def test_creation(self):
        """Test basic creation."""
        result = ExtractionResult(
            provider_id="test-provider",
            metric_id="M-01",
            observations=(),
        )
        assert result.provider_id == "test-provider"
        assert result.metric_id == "M-01"
        assert result.observations == ()
        assert result.quality_state == QualityState.COMPLETE
        assert result.confidence == 1.0

    def test_observation_count(self):
        """Test observation_count property."""
        result = ExtractionResult(
            provider_id="test-provider",
            metric_id="M-01",
            observations=(1, 2, 3),
        )
        assert result.observation_count == 3

    def test_is_empty(self):
        """Test is_empty property."""
        empty = ExtractionResult(
            provider_id="test-provider",
            metric_id="M-01",
            observations=(),
        )
        assert empty.is_empty is True

        non_empty = ExtractionResult(
            provider_id="test-provider",
            metric_id="M-01",
            observations=(1,),
        )
        assert non_empty.is_empty is False


class TestProviderRegistrationConfig:
    """Test ProviderRegistrationConfig dataclass."""

    def test_creation(self):
        """Test basic creation."""
        config = ProviderRegistrationConfig(
            provider_id="test-provider",
            provider_class="miie.providers.git.GitProvider",
        )
        assert config.provider_id == "test-provider"
        assert config.provider_class == "miie.providers.git.GitProvider"
        assert config.priority == PriorityLevel.MEDIUM
        assert config.enabled is True
        assert config.timeout_seconds == 30.0

    def test_validation_empty_id(self):
        """Test validation fails with empty provider_id."""
        with pytest.raises(ValueError, match="provider_id must not be empty"):
            ProviderRegistrationConfig(
                provider_id="",
                provider_class="miie.providers.git.GitProvider",
            )

    def test_validation_empty_class(self):
        """Test validation fails with empty provider_class."""
        with pytest.raises(ValueError, match="provider_class must not be empty"):
            ProviderRegistrationConfig(
                provider_id="test-provider",
                provider_class="",
            )

    def test_validation_negative_timeout(self):
        """Test validation fails with negative timeout."""
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            ProviderRegistrationConfig(
                provider_id="test-provider",
                provider_class="miie.providers.git.GitProvider",
                timeout_seconds=-1.0,
            )


class TestProviderFactoryResult:
    """Test ProviderFactoryResult dataclass."""

    def test_creation(self):
        """Test basic creation."""
        result = ProviderFactoryResult(
            provider="mock-provider",
            validation_result=ValidationResult.success(),
        )
        assert result.provider == "mock-provider"
        assert result.is_valid is True
        assert result.config_warnings == []

    def test_is_valid_false(self):
        """Test is_valid with failed validation."""
        result = ProviderFactoryResult(
            provider="mock-provider",
            validation_result=ValidationResult.failure(["error"]),
        )
        assert result.is_valid is False


class TestConstants:
    """Test constant values."""

    def test_valid_metric_ids(self):
        """Test VALID_METRIC_IDS contains all metrics."""
        assert len(VALID_METRIC_IDS) == 7
        for i in range(1, 8):
            assert f"M-{i:02d}" in VALID_METRIC_IDS

    def test_capability_constants(self):
        """Test capability constants exist."""
        assert CAPABILITY_GIT_NATIVE == "git-native"
        assert CAPABILITY_API_REQUIRED == "api-required"
        assert CAPABILITY_LOCAL_ONLY == "local-only"
        assert CAPABILITY_REMOTE_ONLY == "remote-only"
        assert CAPABILITY_REAL_TIME == "real-time"
        assert CAPABILITY_BATCH == "batch"
