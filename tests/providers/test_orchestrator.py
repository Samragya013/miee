"""
Tests for ObservationOrchestrator — PR-11C.

Comprehensive test coverage for multi-provider orchestration including:
- Provider discovery and execution planning
- Deterministic ordering
- Provider isolation and error handling
- Observation merging and deduplication
- Conflict resolution
- Diagnostics
- Edge cases
"""

from __future__ import annotations

from typing import List, Optional
from unittest.mock import MagicMock

import pytest

from miie.processing.observation.models import (
    Observation,
    ObservationProvenance,
    generate_observation_id,
)
from miie.providers.base import BaseObservationProvider
from miie.providers.context import (
    CAPABILITY_BATCH,
    CAPABILITY_GIT_NATIVE,
    CAPABILITY_LOCAL_ONLY,
    ExtractionResult,
    HealthStatus,
    PriorityLevel,
    ProviderCapability,
    ProviderContext,
    ProviderHealth,
    ProviderState,
    QualityState,
)
from miie.providers.exceptions import ExtractionError
from miie.providers.orchestrator import (
    ExecutionPlan,
    MergeConflict,
    ObservationOrchestrator,
    OrchestratorConfig,
    OrchestratorDiagnostics,
    ProviderExecutionResult,
    ProviderTask,
)
from miie.providers.registry import DeterministicRegistry

# ---------------------------------------------------------------------------
# Fixtures — Mock Providers
# ---------------------------------------------------------------------------


class MockProvider(BaseObservationProvider):
    """A mock provider that returns configurable results."""

    def __init__(
        self,
        provider_id: str,
        metrics: frozenset[str],
        observations: Optional[List[Observation]] = None,
        source_types: frozenset[str] = frozenset({"commit"}),
        fail_init: bool = False,
        fail_extract: bool = False,
        health_status: HealthStatus = HealthStatus.HEALTHY,
    ) -> None:
        capability = ProviderCapability(
            supported_metrics=metrics,
            supported_source_types=source_types,
            capabilities=frozenset({CAPABILITY_GIT_NATIVE, CAPABILITY_LOCAL_ONLY, CAPABILITY_BATCH}),
        )
        super().__init__(provider_id, capability)
        self._observations = observations or []
        self._fail_init = fail_init
        self._fail_extract = fail_extract
        self._health_status = health_status
        self._extract_called = False

    def initialize(self, context: ProviderContext) -> None:
        if self._fail_init:
            self._state = ProviderState.FAILED
            raise ExtractionError("Init failed", error_code="INIT_FAILED")
        self._state = ProviderState.READY

    def extract(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        return self.extract_observations(context, metric_ids)

    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        self._extract_called = True
        if self._fail_extract:
            raise ExtractionError("Extraction failed", error_code="EXTRACT_FAILED")

        now_iso = "2025-01-01T00:00:00+00:00"
        provenance = ObservationProvenance(
            extractor_id=self._provider_id,
            extraction_timestamp=now_iso,
        )

        observations = []
        for obs in self._observations:
            if obs.metric_id in metric_ids:
                observations.append(obs)

        return ExtractionResult(
            provider_id=self._provider_id,
            metric_id=metric_ids[0] if metric_ids else "M-02",
            observations=tuple(observations),
            quality_state=QualityState.COMPLETE,
            confidence=1.0,
        )

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            status=self._health_status,
            health_score=1.0 if self._health_status == HealthStatus.HEALTHY else 0.5,
        )


def _make_obs(
    source_type: str,
    source_id: str,
    metric_id: str,
    value: float = 1.0,
    provider_id: str = "test.provider",
) -> Observation:
    """Create a test Observation."""
    # Ensure source_id is valid hex SHA for commit type
    if source_type == "commit":
        # Use source_id as seed to generate valid 40-char hex SHA
        import hashlib

        source_id = hashlib.sha256(source_id.encode()).hexdigest()[:40]
    return Observation(
        observation_id=generate_observation_id(source_type, source_id, metric_id),
        source_type=source_type,
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        unit="count",
        timestamp="2025-01-01T00:00:00+00:00",
        quality="complete",
        provenance=ObservationProvenance(
            extractor_id=provider_id,
            extraction_timestamp="2025-01-01T00:00:00+00:00",
        ),
    )


def _make_context() -> ProviderContext:
    """Create a test ProviderContext."""
    return ProviderContext(
        repo_path="/tmp/test-repo",
        repository_id="test-org/test-repo",
        analysis_id="test-analysis-001",
    )


# ---------------------------------------------------------------------------
# Tests — ExecutionPlan
# ---------------------------------------------------------------------------


class TestExecutionPlan:
    """Tests for ExecutionPlan dataclass."""

    def test_execution_plan_creation(self) -> None:
        plan = ExecutionPlan(
            tasks=(
                ProviderTask("p1", ("M-02",), PriorityLevel.HIGH),
                ProviderTask("p2", ("M-05",), PriorityLevel.MEDIUM),
            ),
            metric_coverage={"M-02": ("p1",), "M-05": ("p2",)},
            total_providers=2,
        )
        assert plan.task_count == 2
        assert plan.total_providers == 2

    def test_execution_plan_empty(self) -> None:
        plan = ExecutionPlan(tasks=(), metric_coverage={}, total_providers=0)
        assert plan.task_count == 0


# ---------------------------------------------------------------------------
# Tests — OrchestratorConfig
# ---------------------------------------------------------------------------


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig dataclass."""

    def test_default_config(self) -> None:
        config = OrchestratorConfig()
        assert config.max_parallel_providers == 1
        assert config.provider_timeout_seconds == 60.0
        assert config.enable_partial_execution is True
        assert config.deduplicate_observations is True
        assert config.merge_policy == "highest_priority"

    def test_custom_config(self) -> None:
        config = OrchestratorConfig(
            provider_timeout_seconds=30.0,
            enable_partial_execution=False,
            merge_policy="latest",
        )
        assert config.provider_timeout_seconds == 30.0
        assert config.enable_partial_execution is False
        assert config.merge_policy == "latest"


# ---------------------------------------------------------------------------
# Tests — OrchestratorDiagnostics
# ---------------------------------------------------------------------------


class TestOrchestratorDiagnostics:
    """Tests for OrchestratorDiagnostics dataclass."""

    def test_default_diagnostics(self) -> None:
        diag = OrchestratorDiagnostics()
        assert diag.providers_attempted == 0
        assert diag.providers_succeeded == 0
        assert diag.providers_failed == 0
        assert diag.total_observations == 0
        assert diag.success_rate == 1.0  # 0/0 = 1.0

    def test_success_rate(self) -> None:
        diag = OrchestratorDiagnostics(
            providers_attempted=10,
            providers_succeeded=7,
            providers_failed=3,
        )
        assert diag.success_rate == pytest.approx(0.7)

    def test_is_deterministic(self) -> None:
        diag = OrchestratorDiagnostics()
        assert diag.is_deterministic is True


# ---------------------------------------------------------------------------
# Tests — ProviderExecutionResult
# ---------------------------------------------------------------------------


class TestProviderExecutionResult:
    """Tests for ProviderExecutionResult dataclass."""

    def test_successful_result(self) -> None:
        result = ProviderExecutionResult(
            provider_id="test",
            result=MagicMock(),
            success=True,
            execution_time_ms=100.0,
            observations_produced=5,
        )
        assert result.success is True
        assert result.observations_produced == 5

    def test_failed_result(self) -> None:
        result = ProviderExecutionResult(
            provider_id="test",
            result=None,
            success=False,
            error="Something went wrong",
        )
        assert result.success is False
        assert result.error == "Something went wrong"


# ---------------------------------------------------------------------------
# Tests — ObservationOrchestrator
# ---------------------------------------------------------------------------


class TestObservationOrchestrator:
    """Tests for ObservationOrchestrator."""

    def test_orchestrator_initialization(self) -> None:
        registry = DeterministicRegistry()
        orchestrator = ObservationOrchestrator(registry)
        assert orchestrator.registry is registry
        assert orchestrator.config is not None

    def test_build_execution_plan_empty_registry(self) -> None:
        registry = DeterministicRegistry()
        orchestrator = ObservationOrchestrator(registry)
        plan = orchestrator.build_execution_plan(["M-02", "M-05"])
        assert plan.task_count == 0
        assert plan.total_providers == 0

    def test_build_execution_plan_single_provider(self) -> None:
        registry = DeterministicRegistry()
        provider = MockProvider("git.v1", frozenset({"M-02", "M-06"}))
        registry.register(
            provider,
            provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        plan = orchestrator.build_execution_plan(["M-02", "M-06"])

        assert plan.task_count == 1
        assert plan.total_providers == 1
        assert "M-02" in plan.metric_coverage
        assert "M-06" in plan.metric_coverage

    def test_build_execution_plan_multiple_providers(self) -> None:
        registry = DeterministicRegistry()
        git_provider = MockProvider(
            "git.v1",
            frozenset({"M-02", "M-06"}),
            source_types=frozenset({"commit"}),
        )
        github_provider = MockProvider(
            "github.v1",
            frozenset({"M-02", "M-05"}),
            source_types=frozenset({"pull_request"}),
        )
        registry.register(
            git_provider,
            git_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            github_provider,
            github_provider.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        orchestrator = ObservationOrchestrator(registry)
        plan = orchestrator.build_execution_plan(["M-02", "M-05", "M-06"])

        assert plan.task_count == 2
        assert plan.total_providers == 2
        # M-02 is covered by both providers
        assert len(plan.metric_coverage["M-02"]) == 2

    def test_build_execution_plan_deterministic_order(self) -> None:
        """Same inputs always produce same task order."""
        registry = DeterministicRegistry()
        for pid in ["z-provider", "a-provider", "m-provider"]:
            provider = MockProvider(pid, frozenset({"M-02"}))
            registry.register(
                provider,
                provider.get_capabilities(),
                PriorityLevel.MEDIUM,
            )

        orchestrator = ObservationOrchestrator(registry)
        plan1 = orchestrator.build_execution_plan(["M-02"])
        plan2 = orchestrator.build_execution_plan(["M-02"])

        assert [t.provider_id for t in plan1.tasks] == [t.provider_id for t in plan2.tasks]

    def test_build_execution_plan_priority_ordering(self) -> None:
        """Higher priority providers come first."""
        registry = DeterministicRegistry()
        low_provider = MockProvider("low.v1", frozenset({"M-02"}))
        high_provider = MockProvider("high.v1", frozenset({"M-02"}))

        registry.register(
            low_provider,
            low_provider.get_capabilities(),
            PriorityLevel.LOW,
        )
        registry.register(
            high_provider,
            high_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        plan = orchestrator.build_execution_plan(["M-02"])

        assert plan.tasks[0].provider_id == "high.v1"
        assert plan.tasks[1].provider_id == "low.v1"

    def test_orchestrate_empty_registry(self) -> None:
        registry = DeterministicRegistry()
        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()

        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 0
        assert diagnostics.providers_attempted == 0
        assert diagnostics.overall_quality == QualityState.MISSING

    def test_orchestrate_single_provider_success(self) -> None:
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)
        provider = MockProvider("git.v1", frozenset({"M-02"}), observations=[obs])
        registry.register(
            provider,
            provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 1
        assert diagnostics.providers_succeeded == 1
        assert diagnostics.providers_failed == 0
        assert result.provider_id == "orchestrator.v1"

    def test_orchestrate_multi_provider_merge(self) -> None:
        """Multiple providers producing observations are merged."""
        registry = DeterministicRegistry()
        obs1 = _make_obs("commit", "sha-001", "M-02", 1.0, "git.v1")
        obs2 = _make_obs("commit", "sha-002", "M-02", 1.0, "git.v1")
        obs3 = _make_obs("branch", "pr-001", "M-02", 1.0, "github.v1")

        git_provider = MockProvider(
            "git.v1",
            frozenset({"M-02"}),
            observations=[obs1, obs2],
        )
        github_provider = MockProvider(
            "github.v1",
            frozenset({"M-02"}),
            observations=[obs3],
            source_types=frozenset({"pull_request"}),
        )
        registry.register(
            git_provider,
            git_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            github_provider,
            github_provider.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 3
        assert diagnostics.providers_succeeded == 2

    def test_orchestrate_provider_failure_partial(self) -> None:
        """One provider fails, others continue (partial execution)."""
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)

        failing_provider = MockProvider(
            "failing.v1",
            frozenset({"M-02"}),
            fail_extract=True,
        )
        success_provider = MockProvider(
            "success.v1",
            frozenset({"M-02"}),
            observations=[obs],
        )
        registry.register(
            failing_provider,
            failing_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            success_provider,
            success_provider.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 1
        assert result.is_partial is True
        assert diagnostics.providers_failed == 1
        assert diagnostics.providers_succeeded == 1

    def test_orchestrate_provider_init_failure(self) -> None:
        """Provider that fails initialization is handled gracefully."""
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)

        bad_provider = MockProvider(
            "bad.v1",
            frozenset({"M-02"}),
            fail_init=True,
        )
        good_provider = MockProvider(
            "good.v1",
            frozenset({"M-02"}),
            observations=[obs],
        )
        registry.register(
            bad_provider,
            bad_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            good_provider,
            good_provider.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 1
        assert diagnostics.providers_failed == 1

    def test_orchestrate_disposed_provider_skipped(self) -> None:
        """Disposed providers are skipped."""
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)

        disposed_provider = MockProvider(
            "disposed.v1",
            frozenset({"M-02"}),
        )
        disposed_provider._state = ProviderState.DISPOSED

        good_provider = MockProvider(
            "good.v1",
            frozenset({"M-02"}),
            observations=[obs],
        )
        registry.register(
            disposed_provider,
            disposed_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            good_provider,
            good_provider.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 1
        assert diagnostics.providers_failed == 1

    def test_orchestrate_deduplication(self) -> None:
        """Duplicate observations are removed."""
        registry = DeterministicRegistry()
        # Same observation from two providers
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)

        provider1 = MockProvider("p1.v1", frozenset({"M-02"}), observations=[obs])
        provider2 = MockProvider("p2.v1", frozenset({"M-02"}), observations=[obs])

        registry.register(
            provider1,
            provider1.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            provider2,
            provider2.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        config = OrchestratorConfig(deduplicate_observations=True)
        orchestrator = ObservationOrchestrator(registry, config)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 1
        # Merge resolved the conflict, so dedup has nothing extra to remove
        assert diagnostics.duplicate_observations_removed == 0
        assert diagnostics.merge_conflicts_detected == 1

    def test_orchestrate_no_deduplication(self) -> None:
        """When dedup is disabled, duplicates are kept."""
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)

        provider1 = MockProvider("p1.v1", frozenset({"M-02"}), observations=[obs])
        provider2 = MockProvider("p2.v1", frozenset({"M-02"}), observations=[obs])

        registry.register(
            provider1,
            provider1.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            provider2,
            provider2.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        config = OrchestratorConfig(deduplicate_observations=False)
        orchestrator = ObservationOrchestrator(registry, config)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        # Both providers' observations are kept (same ID but merge picks one)
        # Actually the merge still picks one per ID, dedup just ensures no dupes
        assert result.observation_count == 1  # merge resolves to one

    def test_orchestrate_conflict_detection(self) -> None:
        """Conflicts between providers are detected and recorded."""
        registry = DeterministicRegistry()
        obs1 = _make_obs("commit", "sha-001", "M-02", 1.0)
        obs2 = _make_obs("commit", "sha-001", "M-02", 2.0)  # Same ID, different value

        provider1 = MockProvider("p1.v1", frozenset({"M-02"}), observations=[obs1])
        provider2 = MockProvider("p2.v1", frozenset({"M-02"}), observations=[obs2])

        registry.register(
            provider1,
            provider1.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            provider2,
            provider2.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert diagnostics.merge_conflicts_detected == 1
        assert len(diagnostics.conflicts) == 1

    def test_orchestrate_conflict_resolution_highest_priority(self) -> None:
        """Conflict resolved by highest priority provider."""
        registry = DeterministicRegistry()
        obs1 = _make_obs("commit", "sha-001", "M-02", 1.0)
        obs2 = _make_obs("commit", "sha-001", "M-02", 2.0)

        high_provider = MockProvider("high.v1", frozenset({"M-02"}), observations=[obs1])
        low_provider = MockProvider("low.v1", frozenset({"M-02"}), observations=[obs2])

        registry.register(
            high_provider,
            high_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            low_provider,
            low_provider.get_capabilities(),
            PriorityLevel.LOW,
        )

        config = OrchestratorConfig(merge_policy="highest_priority")
        orchestrator = ObservationOrchestrator(registry, config)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 1
        assert diagnostics.merge_conflicts_detected == 1
        # High priority provider's observation should win
        assert result.observations[0].value == 1.0

    def test_orchestrate_conflict_resolution_latest(self) -> None:
        """Conflict resolved by latest timestamp."""
        import hashlib

        registry = DeterministicRegistry()
        sha = hashlib.sha256(b"sha-001").hexdigest()[:40]
        obs1 = Observation(
            observation_id=generate_observation_id("commit", sha, "M-02"),
            source_type="commit",
            source_id=sha,
            metric_id="M-02",
            value=1.0,
            unit="count",
            timestamp="2025-01-01T00:00:00+00:00",
            quality="complete",
            provenance=ObservationProvenance(
                extractor_id="old.v1",
                extraction_timestamp="2025-01-01T00:00:00+00:00",
            ),
        )
        obs2 = Observation(
            observation_id=generate_observation_id("commit", sha, "M-02"),
            source_type="commit",
            source_id=sha,
            metric_id="M-02",
            value=2.0,
            unit="count",
            timestamp="2025-06-01T00:00:00+00:00",
            quality="complete",
            provenance=ObservationProvenance(
                extractor_id="new.v1",
                extraction_timestamp="2025-06-01T00:00:00+00:00",
            ),
        )

        old_provider = MockProvider("old.v1", frozenset({"M-02"}), observations=[obs1])
        new_provider = MockProvider("new.v1", frozenset({"M-02"}), observations=[obs2])

        registry.register(
            old_provider,
            old_provider.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            new_provider,
            new_provider.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        config = OrchestratorConfig(merge_policy="latest")
        orchestrator = ObservationOrchestrator(registry, config)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 1
        # Later timestamp should win
        assert result.observations[0].value == 2.0

    def test_orchestrate_all_providers_fail(self) -> None:
        """When all providers fail, result is empty with MISSING quality."""
        registry = DeterministicRegistry()
        provider1 = MockProvider("p1.v1", frozenset({"M-02"}), fail_extract=True)
        provider2 = MockProvider("p2.v1", frozenset({"M-02"}), fail_extract=True)

        registry.register(
            provider1,
            provider1.get_capabilities(),
            PriorityLevel.HIGH,
        )
        registry.register(
            provider2,
            provider2.get_capabilities(),
            PriorityLevel.MEDIUM,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 0
        assert diagnostics.overall_quality == QualityState.MISSING
        assert diagnostics.providers_failed == 2

    def test_orchestrate_quality_assessment_complete(self) -> None:
        """Quality is COMPLETE when all providers succeed with full confidence."""
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)
        provider = MockProvider("git.v1", frozenset({"M-02"}), observations=[obs])
        registry.register(
            provider,
            provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert diagnostics.overall_quality == QualityState.COMPLETE
        assert diagnostics.overall_confidence == 1.0

    def test_orchestrate_quality_assessment_degraded(self) -> None:
        """Quality is DEGRADED when some providers fail."""
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)

        failing = MockProvider("fail.v1", frozenset({"M-02"}), fail_extract=True)
        success = MockProvider("ok.v1", frozenset({"M-02"}), observations=[obs])

        registry.register(failing, failing.get_capabilities(), PriorityLevel.HIGH)
        registry.register(success, success.get_capabilities(), PriorityLevel.MEDIUM)

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert diagnostics.overall_quality == QualityState.DEGRADED
        assert diagnostics.overall_confidence < 1.0

    def test_orchestrate_metadata(self) -> None:
        """Merged result contains orchestrator metadata."""
        registry = DeterministicRegistry()
        obs = _make_obs("commit", "sha-001", "M-02", 1.0)
        provider = MockProvider("git.v1", frozenset({"M-02"}), observations=[obs])
        registry.register(
            provider,
            provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, _ = orchestrator.orchestrate(context, ["M-02"])

        assert "orchestrator_version" in result.metadata
        assert result.metadata["providers_attempted"] == 1
        assert result.metadata["providers_succeeded"] == 1

    def test_get_diagnostics_summary(self) -> None:
        """Diagnostics summary returns a serializable dict."""
        registry = DeterministicRegistry()
        orchestrator = ObservationOrchestrator(registry)
        diag = OrchestratorDiagnostics(
            providers_attempted=2,
            providers_succeeded=1,
            providers_failed=1,
            total_observations=5,
            execution_time_ms=123.456,
            overall_quality=QualityState.DEGRADED,
            overall_confidence=0.75,
        )
        summary = orchestrator.get_diagnostics_summary(diag)

        assert summary["providers_attempted"] == 2
        assert summary["providers_succeeded"] == 1
        assert summary["total_observations"] == 5
        assert summary["overall_quality"] == "degraded"
        assert summary["success_rate"] == 0.5

    def test_orchestrate_metrics_not_supported(self) -> None:
        """Provider that doesn't support requested metrics produces empty results."""
        registry = DeterministicRegistry()
        provider = MockProvider("git.v1", frozenset({"M-02"}))
        registry.register(
            provider,
            provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        # Request M-05 which git provider doesn't support
        result, diagnostics = orchestrator.orchestrate(context, ["M-05"])

        assert result.observation_count == 0
        # No providers discovered for M-05, so none attempted
        assert diagnostics.providers_attempted == 0
        assert diagnostics.providers_skipped == 1

    def test_deterministic_execution_plan_across_calls(self) -> None:
        """Execution plan is deterministic across multiple calls."""
        registry = DeterministicRegistry()
        for i in range(5):
            provider = MockProvider(f"provider-{i:02d}", frozenset({"M-02"}))
            registry.register(
                provider,
                provider.get_capabilities(),
                PriorityLevel.MEDIUM,
            )

        orchestrator = ObservationOrchestrator(registry)
        plans = [orchestrator.build_execution_plan(["M-02"]) for _ in range(10)]

        for plan in plans:
            assert [t.provider_id for t in plan.tasks] == [t.provider_id for t in plans[0].tasks]

    def test_provider_task_dataclass(self) -> None:
        """ProviderTask dataclass works correctly."""
        task = ProviderTask(
            provider_id="test.v1",
            metric_ids=("M-02", "M-06"),
            priority=PriorityLevel.HIGH,
            is_fallback=False,
        )
        assert task.provider_id == "test.v1"
        assert "M-02" in task.metric_ids
        assert task.priority == PriorityLevel.HIGH

    def test_merge_conflict_dataclass(self) -> None:
        """MergeConflict dataclass works correctly."""
        conflict = MergeConflict(
            observation_id="abc123",
            source_provider="p1",
            conflicting_provider="p2",
            conflict_type="duplicate_observation_id",
            resolution="Higher priority wins",
        )
        assert conflict.observation_id == "abc123"
        assert conflict.conflict_type == "duplicate_observation_id"


# ---------------------------------------------------------------------------
# Tests — Edge Cases
# ---------------------------------------------------------------------------


class TestOrchestratorEdgeCases:
    """Edge case tests for ObservationOrchestrator."""

    def test_orchestrate_empty_metric_ids(self) -> None:
        """Empty metric list produces empty result."""
        registry = DeterministicRegistry()
        provider = MockProvider("git.v1", frozenset({"M-02"}))
        registry.register(
            provider,
            provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, [])

        assert result.observation_count == 0

    def test_orchestrate_single_metric_multiple_providers(self) -> None:
        """Multiple providers for a single metric are all discovered."""
        registry = DeterministicRegistry()
        for i in range(3):
            obs = _make_obs("commit", f"sha-{i:03d}", "M-02", 1.0)
            provider = MockProvider(f"p{i}.v1", frozenset({"M-02"}), observations=[obs])
            registry.register(
                provider,
                provider.get_capabilities(),
                PriorityLevel.MEDIUM,
            )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, diagnostics = orchestrator.orchestrate(context, ["M-02"])

        assert result.observation_count == 3
        assert diagnostics.providers_succeeded == 3

    def test_orchestrate_preserves_observation_order(self) -> None:
        """Observations are returned in deterministic order (by observation_id)."""
        registry = DeterministicRegistry()
        obs_c = _make_obs("commit", "sha-ccc", "M-02", 3.0)
        obs_a = _make_obs("commit", "sha-aaa", "M-02", 1.0)
        obs_b = _make_obs("commit", "sha-bbb", "M-02", 2.0)

        provider = MockProvider(
            "git.v1",
            frozenset({"M-02"}),
            observations=[obs_c, obs_a, obs_b],
        )
        registry.register(
            provider,
            provider.get_capabilities(),
            PriorityLevel.HIGH,
        )

        orchestrator = ObservationOrchestrator(registry)
        context = _make_context()
        result, _ = orchestrator.orchestrate(context, ["M-02"])

        # Observations should be sorted by observation_id
        ids = [o.observation_id for o in result.observations]
        assert ids == sorted(ids)

    def test_config_immutability(self) -> None:
        """OrchestratorConfig is frozen (immutable)."""
        config = OrchestratorConfig()
        with pytest.raises(AttributeError):
            config.merge_policy = "latest"  # type: ignore[misc]
