"""Tests for miie.providers.context module."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from miie.providers.context import (
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
    ObservationState,
    PriorityLevel,
    ProviderCapability,
    ProviderContext,
    ProviderEntry,
    ProviderHealth,
    ProviderRegistrationConfig,
    ProviderState,
    QualityState,
    ValidationResult,
)


class TestProviderState:
    def test_all_states_exist(self):
        expected = {"uninitialized", "ready", "active", "degraded", "failed", "disposed"}
        actual = {s.value for s in ProviderState}
        assert actual == expected

    def test_string_values(self):
        assert ProviderState.READY.value == "ready"
        assert ProviderState.FAILED.value == "failed"


class TestQualityState:
    def test_all_states_exist(self):
        expected = {"complete", "degraded", "uncertain", "stale", "recovering", "missing"}
        actual = {s.value for s in QualityState}
        assert actual == expected


class TestObservationState:
    def test_all_states_exist(self):
        expected = {"extracted", "validated", "transformed", "stored", "failed"}
        actual = {s.value for s in ObservationState}
        assert actual == expected


class TestPriorityLevel:
    def test_ordering(self):
        assert PriorityLevel.CRITICAL < PriorityLevel.HIGH < PriorityLevel.MEDIUM
        assert PriorityLevel.MEDIUM < PriorityLevel.LOW < PriorityLevel.BACKGROUND

    def test_int_values(self):
        assert PriorityLevel.CRITICAL.value == 1
        assert PriorityLevel.BACKGROUND.value == 5


class TestHealthStatus:
    def test_all_statuses(self):
        expected = {"healthy", "degraded", "unhealthy", "draining", "unknown"}
        actual = {s.value for s in HealthStatus}
        assert actual == expected


class TestExtractionPhase:
    def test_all_phases(self):
        expected = {"health_check", "extract", "transform"}
        actual = {p.value for p in ExtractionPhase}
        assert actual == expected


class TestProviderContext:
    def test_creation(self):
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        assert ctx.repo_path == "/tmp/repo"
        assert ctx.repository_id == "repo-123"
        assert ctx.analysis_id == "analysis-456"
        assert ctx.since is None
        assert ctx.until is None
        assert ctx.exclude_bots is False
        assert ctx.timeout_seconds == 30.0

    def test_frozen(self):
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        with pytest.raises(FrozenInstanceError):
            ctx.repo_path = "/other"

    def test_empty_repo_path_raises(self):
        with pytest.raises(ValueError, match="repo_path must not be empty"):
            ProviderContext(
                repo_path="",
                repository_id="repo-123",
                analysis_id="analysis-456",
            )

    def test_empty_repository_id_raises(self):
        with pytest.raises(ValueError, match="repository_id must not be empty"):
            ProviderContext(
                repo_path="/tmp/repo",
                repository_id="",
                analysis_id="analysis-456",
            )

    def test_empty_analysis_id_raises(self):
        with pytest.raises(ValueError, match="analysis_id must not be empty"):
            ProviderContext(
                repo_path="/tmp/repo",
                repository_id="repo-123",
                analysis_id="",
            )

    def test_negative_timeout_raises(self):
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            ProviderContext(
                repo_path="/tmp/repo",
                repository_id="repo-123",
                analysis_id="analysis-456",
                timeout_seconds=-1.0,
            )

    def test_with_optional_fields(self):
        now = datetime.now(timezone.utc)
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-123",
            analysis_id="analysis-456",
            since=now,
            until=now,
            exclude_bots=True,
            config={"key": "value"},
            timeout_seconds=60.0,
        )
        assert ctx.since == now
        assert ctx.until == now
        assert ctx.exclude_bots is True
        assert ctx.config == {"key": "value"}
        assert ctx.timeout_seconds == 60.0


class TestProviderCapability:
    def test_creation(self):
        cap = ProviderCapability(
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        assert cap.supports_metric("M-01")
        assert cap.supports_metric("M-02")
        assert not cap.supports_metric("M-03")
        assert cap.supports_source_type("commit")
        assert not cap.supports_source_type("file")

    def test_defaults(self):
        cap = ProviderCapability(
            supported_metrics=frozenset(),
            supported_source_types=frozenset(),
        )
        assert cap.requires_network is False
        assert cap.requires_api_token is False
        assert cap.max_observations_per_batch == 10000


class TestProviderHealth:
    def test_success_rate_zero_extractions(self):
        health = ProviderHealth()
        assert health.success_rate == 1.0

    def test_success_rate(self):
        health = ProviderHealth(
            total_extractions=10,
            successful_extractions=8,
            failed_extractions=2,
        )
        assert health.success_rate == 0.8

    def test_is_healthy(self):
        assert ProviderHealth(status=HealthStatus.HEALTHY).is_healthy
        assert ProviderHealth(status=HealthStatus.DRAINING).is_healthy
        assert not ProviderHealth(status=HealthStatus.DEGRADED).is_healthy
        assert not ProviderHealth(status=HealthStatus.UNHEALTHY).is_healthy

    def test_is_usable(self):
        assert ProviderHealth(status=HealthStatus.HEALTHY).is_usable
        assert ProviderHealth(status=HealthStatus.DEGRADED).is_usable
        assert ProviderHealth(status=HealthStatus.UNKNOWN).is_usable
        assert not ProviderHealth(status=HealthStatus.UNHEALTHY).is_usable
        assert not ProviderHealth(status=HealthStatus.DRAINING).is_usable


class TestMetricBounds:
    def test_validate_within_bounds(self):
        bounds = MetricBounds("M-01", 0.0, 1.0, "ratio", "test")
        assert bounds.validate(0.5)
        assert bounds.validate(0.0)
        assert bounds.validate(1.0)

    def test_validate_out_of_bounds(self):
        bounds = MetricBounds("M-01", 0.0, 1.0, "ratio", "test")
        assert not bounds.validate(-0.1)
        assert not bounds.validate(1.1)


class TestMetricBoundsDict:
    def test_all_metrics_defined(self):
        for i in range(1, 8):
            metric_id = f"M-{i:02d}"
            assert metric_id in METRIC_BOUNDS

    def test_m02_unbounded_upper(self):
        bounds = METRIC_BOUNDS["M-02"]
        assert bounds.max_value == float("inf")


class TestValidationResult:
    def test_success(self):
        result = ValidationResult.success()
        assert result.is_valid
        assert result.violations == []
        assert result.warnings == []

    def test_failure(self):
        result = ValidationResult.failure(["error1", "error2"], rule_id="R-01")
        assert not result.is_valid
        assert result.violations == ["error1", "error2"]
        assert result.rule_id == "R-01"

    def test_with_warnings(self):
        result = ValidationResult.with_warnings(["warn1"])
        assert result.is_valid
        assert result.warnings == ["warn1"]


class TestObservationMetrics:
    def test_creation(self):
        m = ObservationMetrics(metric_id="M-02", value=42.0, unit="count")
        assert m.metric_id == "M-02"
        assert m.value == 42.0
        assert m.confidence == 1.0
        assert m.is_estimated is False

    def test_valid_value(self):
        m = ObservationMetrics(metric_id="M-02", value=42.0, unit="count")
        assert m.is_valid

    def test_invalid_confidence(self):
        with pytest.raises(ValueError, match="confidence must be in"):
            ObservationMetrics(metric_id="M-02", value=1.0, unit="count", confidence=1.5)


class TestExtractionResult:
    def test_creation(self):
        result = ExtractionResult(
            provider_id="git",
            metric_id="M-02",
            observations=(1, 2, 3),
        )
        assert result.observation_count == 3
        assert not result.is_empty

    def test_empty(self):
        result = ExtractionResult(
            provider_id="git",
            metric_id="M-02",
            observations=(),
        )
        assert result.observation_count == 0
        assert result.is_empty


class TestProviderEntry:
    def test_creation(self):
        entry = ProviderEntry(
            provider_id="git",
            provider="mock",
            capability=ProviderCapability(
                supported_metrics=frozenset(["M-02"]),
                supported_source_types=frozenset(["commit"]),
            ),
        )
        assert entry.provider_id == "git"
        assert entry.registered_at is not None

    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="provider_id must not be empty"):
            ProviderEntry(
                provider_id="",
                provider="mock",
                capability=ProviderCapability(
                    supported_metrics=frozenset(),
                    supported_source_types=frozenset(),
                ),
            )


class TestProviderRegistrationConfig:
    def test_creation(self):
        config = ProviderRegistrationConfig(
            provider_id="git",
            provider_class="miie.providers.base.BaseGitProvider",
        )
        assert config.provider_id == "git"
        assert config.priority == PriorityLevel.MEDIUM
        assert config.enabled is True

    def test_empty_id_raises(self):
        with pytest.raises(ValueError):
            ProviderRegistrationConfig(
                provider_id="",
                provider_class="some.Class",
            )

    def test_empty_class_raises(self):
        with pytest.raises(ValueError):
            ProviderRegistrationConfig(
                provider_id="git",
                provider_class="",
            )


class TestConstants:
    def test_valid_metric_ids(self):
        assert len(VALID_METRIC_IDS) == 7
        for i in range(1, 8):
            assert f"M-{i:02d}" in VALID_METRIC_IDS

    def test_capability_constants(self):
        assert CAPABILITY_GIT_NATIVE == "git-native"
        assert CAPABILITY_API_REQUIRED == "api-required"
        assert CAPABILITY_LOCAL_ONLY == "local-only"
        assert CAPABILITY_REMOTE_ONLY == "remote-only"
        assert CAPABILITY_REAL_TIME == "real-time"
        assert CAPABILITY_BATCH == "batch"


class TestQualityStateTransitions:
    def test_transitions_defined(self):
        assert len(VALID_QUALITY_TRANSITIONS) > 0

    def test_complete_to_degraded(self):
        transitions = [
            t
            for t in VALID_QUALITY_TRANSITIONS
            if t.source == QualityState.COMPLETE and t.target == QualityState.DEGRADED
        ]
        assert len(transitions) == 1
        assert transitions[0].trigger == "data_degradation"
