"""
MIIE v1.6 — Scientific Metric Completion Framework Tests.

Tests metric computation, dependency ordering, validation, registry,
graph integration, missing observations, partial repositories,
confidence, determinism, and diagnostics.
"""

from __future__ import annotations

import hashlib
from typing import List
from unittest.mock import MagicMock

import pytest

from miie.metrics import (
    MetricCollection,
    MetricCollectionValidator,
    MetricDiagnosticsEngine,
    MetricEngine,
    MetricRegistry,
    MetricResult,
    ObservationInput,
    ObservationValidator,
    generate_metric_collection_id,
)
from miie.metrics.computation import (
    M01EntropyRatioComputer,
    M02CommitCountComputer,
    M03ChurnRatioComputer,
    M04TestCoverageComputer,
    M05ReviewLatencyComputer,
    M06FileChangeCountComputer,
    M07BranchFreshnessComputer,
    create_all_computers,
)
from miie.metrics.contracts import MetricComputer
from miie.metrics.models import MetricDefinition
from miie.metrics.registry import (
    MetricNotFoundError,
    MetricRegistrationError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ID = "test-repo-abc123"
_ANALYSIS_ID = "analysis-def456"


def _obs(
    metric_id: str = "M-02",
    value: float = 10.0,
    unit: str | None = None,
    quality: str = "complete",
    source_type: str = "commit",
    source_id: str = "abc123def456",
    provider_id: str = "test.extractor.v1",
    observation_id: str | None = None,
) -> ObservationInput:
    """Create a test ObservationInput."""
    _UNITS = {
        "M-01": "ratio",
        "M-02": "count",
        "M-03": "ratio",
        "M-04": "ratio",
        "M-05": "hours",
        "M-06": "count",
        "M-07": "ratio",
    }
    if unit is None:
        unit = _UNITS.get(metric_id, "count")
    if observation_id is None:
        observation_id = hashlib.sha256(f"{metric_id}:{source_id}:{value}".encode()).hexdigest()[:16]
    return ObservationInput(
        observation_id=observation_id,
        metric_id=metric_id,
        value=value,
        unit=unit,
        quality=quality,
        source_type=source_type,
        source_id=source_id,
        timestamp="2026-01-15T12:00:00Z",
        provider_id=provider_id,
    )


def _mock_rog(observations: List) -> MagicMock:
    """Create a mock RepositoryObservationGraph."""
    graph = MagicMock()
    graph.get_all_observations.return_value = observations
    graph.get_node.return_value = None
    return graph


# ===================================================================
# Test Models
# ===================================================================


class TestModels:
    def test_metric_definition(self):
        d = MetricDefinition(
            metric_id="M-01",
            name="Test",
            unit="ratio",
            min_value=0.0,
            max_value=1.0,
            description="desc",
            aggregation="mean",
        )
        assert d.metric_id == "M-01"
        assert d.required_observations == 1
        assert d.dependencies == ()

    def test_observation_input(self):
        obs = _obs()
        assert obs.metric_id == "M-02"
        assert obs.value == 10.0
        assert obs.quality == "complete"

    def test_metric_result(self):
        r = MetricResult(
            metric_id="M-01",
            value=0.5,
            unit="ratio",
            confidence=0.8,
            uncertainty=0.1,
            observation_count=5,
            provider_count=2,
            quality_distribution={"complete": 4, "estimated": 1},
            computation_method="mean",
        )
        assert r.metric_id == "M-01"
        assert r.confidence == 0.8

    def test_metric_collection(self):
        r = MetricResult(
            metric_id="M-01",
            value=0.5,
            unit="ratio",
            confidence=0.8,
            uncertainty=0.1,
            observation_count=5,
            provider_count=2,
            quality_distribution={"complete": 5},
            computation_method="mean",
        )
        c = MetricCollection(
            collection_id="abc123",
            repository_id="repo",
            analysis_id="analysis",
            results={"M-01": r},
        )
        assert c.has_metric("M-01")
        assert not c.has_metric("M-02")
        assert c.metric_count == 1
        assert c.metric_ids == ["M-01"]

    def test_generate_collection_id_deterministic(self):
        id1 = generate_metric_collection_id("repo1", "analysis1")
        id2 = generate_metric_collection_id("repo1", "analysis1")
        assert id1 == id2
        assert len(id1) == 16

    def test_generate_collection_id_unique(self):
        id1 = generate_metric_collection_id("repo1", "analysis1")
        id2 = generate_metric_collection_id("repo1", "analysis2")
        assert id1 != id2


# ===================================================================
# Test Registry
# ===================================================================


class TestMetricRegistry:
    def test_register_all_7(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        assert reg.registered_count() == 7
        assert set(reg.registered_ids()) == {f"M-{i:02d}" for i in range(1, 8)}

    def test_get_computer(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        c = reg.get_computer("M-01")
        assert isinstance(c, M01EntropyRatioComputer)

    def test_get_computer_not_found(self):
        reg = MetricRegistry()
        with pytest.raises(MetricNotFoundError):
            reg.get_computer("M-99")

    def test_duplicate_registration(self):
        reg = MetricRegistry()
        reg.register(M01EntropyRatioComputer())
        with pytest.raises(MetricRegistrationError):
            reg.register(M01EntropyRatioComputer())

    def test_invalid_metric_id(self):
        reg = MetricRegistry()
        computer = MagicMock(spec=MetricComputer)
        computer.metric_definition = MetricDefinition(
            metric_id="M-99",
            name="Bad",
            unit="count",
            min_value=0,
            max_value=100,
            description="bad",
            aggregation="sum",
        )
        with pytest.raises(MetricRegistrationError):
            reg.register(computer)

    def test_invalid_aggregation(self):
        reg = MetricRegistry()
        computer = MagicMock(spec=MetricComputer)
        computer.metric_definition = MetricDefinition(
            metric_id="M-01",
            name="Bad",
            unit="ratio",
            min_value=0,
            max_value=1,
            description="bad",
            aggregation="median",
        )
        with pytest.raises(MetricRegistrationError):
            reg.register(computer)

    def test_execution_order(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        order = reg.execution_order()
        assert len(order) == 7
        # M-03 depends on M-07, so M-07 must come before M-03
        assert order.index("M-07") < order.index("M-03")

    def test_dependency_graph(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        graph = reg.dependency_graph()
        assert graph["M-03"] == ["M-07"]
        assert graph["M-01"] == []

    def test_missing_dependencies(self):
        reg = MetricRegistry()
        reg.register(M03ChurnRatioComputer())
        missing = reg.missing_dependencies()
        assert "M-07" in missing.get("M-03", [])

    def test_validate_registry(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        errors = reg.validate_registry()
        assert errors == []

    def test_validate_registry_missing(self):
        reg = MetricRegistry()
        reg.register(M01EntropyRatioComputer())
        errors = reg.validate_registry()
        assert len(errors) > 0

    def test_contains(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        assert "M-01" in reg
        assert "M-99" not in reg

    def test_len(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        assert len(reg) == 7


# ===================================================================
# Test Metric Computers
# ===================================================================


class TestMetricComputers:
    def test_all_computers_created(self):
        computers = create_all_computers()
        assert len(computers) == 7

    def test_m01_compute(self):
        c = M01EntropyRatioComputer()
        obs = [_obs("M-01", 0.5, unit="ratio") for _ in range(5)]
        result = c.compute(obs)
        assert result.metric_id == "M-01"
        assert result.value == 0.5
        assert result.unit == "ratio"
        assert 0.0 <= result.confidence <= 1.0

    def test_m02_sum(self):
        c = M02CommitCountComputer()
        obs = [_obs("M-02", 10.0), _obs("M-02", 20.0)]
        result = c.compute(obs)
        assert result.value == 30.0

    def test_m03_mean(self):
        c = M03ChurnRatioComputer()
        obs = [_obs("M-03", 0.3), _obs("M-03", 0.7)]
        result = c.compute(obs)
        assert result.value == 0.5

    def test_m04_compute(self):
        c = M04TestCoverageComputer()
        obs = [_obs("M-04", 0.8)]
        result = c.compute(obs)
        assert result.value == 0.8

    def test_m05_mean(self):
        c = M05ReviewLatencyComputer()
        obs = [_obs("M-05", 2.0), _obs("M-05", 4.0)]
        result = c.compute(obs)
        assert result.value == 3.0

    def test_m06_sum(self):
        c = M06FileChangeCountComputer()
        obs = [_obs("M-06", 5.0), _obs("M-06", 15.0)]
        result = c.compute(obs)
        assert result.value == 20.0

    def test_m07_compute(self):
        c = M07BranchFreshnessComputer()
        obs = [_obs("M-07", 0.9)]
        result = c.compute(obs)
        assert result.value == 0.9

    def test_empty_observations_raises(self):
        c = M01EntropyRatioComputer()
        with pytest.raises(ValueError, match="No observations"):
            c.compute([])

    def test_confidence_range(self):
        c = M02CommitCountComputer()
        for n in [1, 5, 10, 20, 50]:
            obs = [_obs("M-02", float(i)) for i in range(n)]
            result = c.compute(obs)
            assert 0.0 <= result.confidence <= 1.0

    def test_uncertainty_zero_single(self):
        c = M01EntropyRatioComputer()
        obs = [_obs("M-01", 0.5)]
        result = c.compute(obs)
        assert result.uncertainty == 0.0

    def test_uncertainty_nonzero_multiple(self):
        c = M01EntropyRatioComputer()
        obs = [_obs("M-01", 0.2), _obs("M-01", 0.8)]
        result = c.compute(obs)
        assert result.uncertainty > 0.0

    def test_quality_distribution(self):
        c = M02CommitCountComputer()
        obs = [
            _obs("M-02", 10.0, quality="complete"),
            _obs("M-02", 20.0, quality="complete"),
            _obs("M-02", 30.0, quality="estimated"),
        ]
        result = c.compute(obs)
        assert result.quality_distribution["complete"] == 2
        assert result.quality_distribution["estimated"] == 1

    def test_provider_diversity(self):
        c = M01EntropyRatioComputer()
        obs = [
            _obs("M-01", 0.5, provider_id="p1"),
            _obs("M-01", 0.6, provider_id="p2"),
        ]
        result = c.compute(obs)
        assert result.provider_count == 2


# ===================================================================
# Test Validation
# ===================================================================


class TestValidation:
    def test_valid_observations(self):
        v = ObservationValidator()
        obs = [_obs("M-01", 0.5)]
        result = v.validate_input_observations(obs, M01EntropyRatioComputer().metric_definition)
        assert result.is_valid

    def test_wrong_unit(self):
        v = ObservationValidator()
        obs = [_obs("M-01", 0.5, unit="count")]
        result = v.validate_input_observations(obs, M01EntropyRatioComputer().metric_definition)
        assert not result.is_valid
        assert any("unit" in e for e in result.errors)

    def test_wrong_metric_id(self):
        v = ObservationValidator()
        obs = [_obs("M-02", 10.0)]
        result = v.validate_input_observations(obs, M01EntropyRatioComputer().metric_definition)
        assert not result.is_valid

    def test_nan_value(self):
        v = ObservationValidator()
        obs = [_obs("M-01", float("nan"))]
        result = v.validate_input_observations(obs, M01EntropyRatioComputer().metric_definition)
        assert not result.is_valid
        assert any("NaN" in e for e in result.errors)

    def test_inf_value(self):
        v = ObservationValidator()
        obs = [_obs("M-01", float("inf"))]
        result = v.validate_input_observations(obs, M01EntropyRatioComputer().metric_definition)
        assert not result.is_valid

    def test_out_of_range_warning(self):
        v = ObservationValidator()
        obs = [_obs("M-01", 1.5)]  # M-01 max is 1.0
        result = v.validate_input_observations(obs, M01EntropyRatioComputer().metric_definition)
        assert len(result.warnings) > 0

    def test_insufficient_observations(self):
        v = ObservationValidator()
        obs = [_obs("M-03", 0.5)]  # M-03 requires 5
        result = v.validate_input_observations(obs, M03ChurnRatioComputer().metric_definition)
        assert not result.is_valid

    def test_validate_metric_result(self):
        v = ObservationValidator()
        r = MetricResult(
            metric_id="M-01",
            value=0.5,
            unit="ratio",
            confidence=0.8,
            uncertainty=0.1,
            observation_count=5,
            provider_count=2,
            quality_distribution={"complete": 5},
            computation_method="mean",
        )
        result = v.validate_metric_result(r, M01EntropyRatioComputer().metric_definition)
        assert result.is_valid

    def test_validate_result_bad_value(self):
        v = ObservationValidator()
        r = MetricResult(
            metric_id="M-01",
            value=2.0,
            unit="ratio",
            confidence=0.8,
            uncertainty=0.1,
            observation_count=5,
            provider_count=2,
            quality_distribution={"complete": 5},
            computation_method="mean",
        )
        result = v.validate_metric_result(r, M01EntropyRatioComputer().metric_definition)
        assert not result.is_valid

    def test_validate_result_bad_confidence(self):
        v = ObservationValidator()
        r = MetricResult(
            metric_id="M-01",
            value=0.5,
            unit="ratio",
            confidence=1.5,
            uncertainty=0.1,
            observation_count=5,
            provider_count=2,
            quality_distribution={"complete": 5},
            computation_method="mean",
        )
        result = v.validate_metric_result(r, M01EntropyRatioComputer().metric_definition)
        assert not result.is_valid

    def test_collection_validator_completeness(self):
        cv = MetricCollectionValidator()
        results = {f"M-{i:02d}": MagicMock() for i in range(1, 8)}
        result = cv.validate_completeness(results)
        assert result.is_valid

    def test_collection_validator_missing(self):
        cv = MetricCollectionValidator()
        results = {"M-01": MagicMock()}
        result = cv.validate_completeness(results)
        assert not result.is_valid

    def test_collection_validator_consistency(self):
        cv = MetricCollectionValidator()
        results = {
            "M-01": MetricResult("M-01", 0.5, "ratio", 0.8, 0.1, 5, 2, {}, "mean"),
            "M-04": MetricResult("M-04", 0.8, "ratio", 0.9, 0.05, 10, 3, {}, "mean"),
            "M-05": MetricResult("M-05", 3.0, "hours", 0.7, 1.0, 8, 2, {}, "mean"),
            "M-07": MetricResult("M-07", 0.9, "ratio", 0.85, 0.05, 6, 2, {}, "mean"),
        }
        result = cv.validate_consistency(results)
        assert result.is_valid


# ===================================================================
# Test Metric Engine
# ===================================================================


class TestMetricEngine:
    def test_engine_default_init(self):
        engine = MetricEngine()
        assert engine.registry.registered_count() == 7

    def test_engine_custom_registry(self):
        reg = MetricRegistry()
        reg.register_all(create_all_computers())
        engine = MetricEngine(registry=reg)
        assert engine.registry.registered_count() == 7

    def test_compute_single_metric(self):
        engine = MetricEngine()
        obs = [_obs("M-02", 10.0), _obs("M-02", 20.0)]
        result = engine.compute_single("M-02", obs)
        assert result.metric_id == "M-02"
        assert result.value == 30.0

    def test_compute_from_observations_all_metrics(self):
        engine = MetricEngine()
        observations = [
            _obs("M-01", 0.5),
            _obs("M-02", 10.0),
            _obs("M-03", 0.3),
            _obs("M-03", 0.4),
            _obs("M-03", 0.5),
            _obs("M-03", 0.6),
            _obs("M-03", 0.7),
            _obs("M-04", 0.8),
            _obs("M-05", 2.0),
            _obs("M-05", 4.0),
            _obs("M-06", 5.0),
            _obs("M-07", 0.9),
        ]
        collection = engine.compute_from_observations(observations, repository_id=_REPO_ID, analysis_id=_ANALYSIS_ID)
        assert collection.repository_id == _REPO_ID
        assert collection.analysis_id == _ANALYSIS_ID
        assert collection.metric_count == 7
        assert 0.0 <= collection.overall_confidence <= 1.0
        assert collection.coverage == 1.0

    def test_compute_from_observations_partial(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.5), _obs("M-02", 10.0)]
        collection = engine.compute_from_observations(observations, repository_id=_REPO_ID, analysis_id=_ANALYSIS_ID)
        assert collection.metric_count == 2
        assert collection.coverage == 2 / 7

    def test_compute_from_observations_empty(self):
        engine = MetricEngine()
        collection = engine.compute_from_observations([])
        assert collection.metric_count == 0
        assert collection.overall_confidence == 0.0

    def test_compute_from_graph(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.5), _obs("M-02", 10.0)]
        graph = _mock_rog(observations)
        collection = engine.compute_from_graph(graph, _REPO_ID, _ANALYSIS_ID)
        assert collection.metric_count == 2

    def test_determinism(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.5), _obs("M-02", 10.0)]
        c1 = engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        c2 = engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        assert c1.overall_confidence == c2.overall_confidence
        for mid in c1.results:
            assert c1.results[mid].value == c2.results[mid].value

    def test_sum_metrics_correct(self):
        engine = MetricEngine()
        observations = [_obs("M-02", 10.0), _obs("M-02", 20.0), _obs("M-02", 30.0)]
        collection = engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        assert collection.get_result("M-02").value == 60.0

    def test_mean_metrics_correct(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.2), _obs("M-01", 0.4), _obs("M-01", 0.6)]
        collection = engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        assert abs(collection.get_result("M-01").value - 0.4) < 1e-10

    def test_multiple_providers(self):
        engine = MetricEngine()
        obs1 = _obs("M-02", 10.0, provider_id="git.observation.v1")
        obs2 = _obs("M-02", 15.0, provider_id="github.pr.observation.v1")
        provider_map = {obs1.observation_id: "git.observation.v1", obs2.observation_id: "github.pr.observation.v1"}
        collection = engine.compute_from_observations(
            [obs1, obs2],
            provider_map=provider_map,
            repository_id=_REPO_ID,
            analysis_id=_ANALYSIS_ID,
        )
        result = collection.get_result("M-02")
        assert result.provider_count == 2
        assert result.value == 25.0

    def test_low_quality_reduces_confidence(self):
        engine = MetricEngine()
        obs_complete = [_obs("M-02", 10.0, quality="complete") for _ in range(10)]
        obs_estimated = [_obs("M-02", 10.0, quality="estimated") for _ in range(10)]
        c1 = engine.compute_from_observations(obs_complete, _REPO_ID, _ANALYSIS_ID)
        c2 = engine.compute_from_observations(obs_estimated, _REPO_ID, _ANALYSIS_ID)
        assert c1.get_result("M-02").confidence > c2.get_result("M-02").confidence

    def test_diagnostics_collected(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.5), _obs("M-02", 10.0)]
        engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        diag = engine.diagnostics.to_diagnostics()
        assert diag.total_observations_processed == 2
        assert "M-01" in diag.observations_by_metric


# ===================================================================
# Test Diagnostics
# ===================================================================


class TestDiagnostics:
    def test_coverage_report(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.5), _obs("M-02", 10.0)]
        collection = engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        diag = MetricDiagnosticsEngine()
        report = diag.coverage_report(collection)
        assert report["coverage_fraction"] == 2 / 7
        assert "M-01" in report["computed_metrics"]
        assert "M-03" in report["missing_metrics"]

    def test_confidence_report(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.5), _obs("M-02", 10.0)]
        collection = engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        diag = MetricDiagnosticsEngine()
        report = diag.confidence_report(collection)
        assert report["high_count"] + report["medium_count"] + report["low_count"] == 2

    def test_missing_observations_report(self):
        diag = MetricDiagnosticsEngine()
        report = diag.missing_observations_report({"M-02": 10, "M-06": 5})
        assert report["adequate_count"] == 2
        assert report["insufficient_count"] == 5

    def test_dependency_graph_report(self):
        diag = MetricDiagnosticsEngine()
        graph = {"M-01": [], "M-03": ["M-07"]}
        report = diag.dependency_graph_report(graph)
        assert "M-01" in report["roots"]
        assert report["total_edges"] == 1

    def test_execution_time_report(self):
        diag = MetricDiagnosticsEngine()
        diag.record_computation_time("M-01", 1.5)
        diag.record_computation_time("M-02", 0.5)
        report = diag.execution_time_report()
        assert report["total_ms"] == 2.0
        assert report["slowest"] == "M-01"

    def test_full_diagnostics(self):
        engine = MetricEngine()
        observations = [_obs("M-01", 0.5)]
        collection = engine.compute_from_observations(observations, _REPO_ID, _ANALYSIS_ID)
        diag = MetricDiagnosticsEngine()
        report = diag.full_diagnostics(collection, engine.registry.dependency_graph())
        assert "coverage" in report
        assert "confidence" in report
        assert "execution_time" in report
        assert "dependency_graph" in report

    def test_timer(self):
        diag = MetricDiagnosticsEngine()
        diag.start_timer("M-01")
        elapsed = diag.stop_timer("M-01")
        assert elapsed >= 0.0


# ===================================================================
# Test Edge Cases
# ===================================================================


class TestEdgeCases:
    def test_single_observation(self):
        engine = MetricEngine()
        collection = engine.compute_from_observations([_obs("M-02", 5.0)], _REPO_ID, _ANALYSIS_ID)
        assert collection.get_result("M-02").value == 5.0

    def test_large_values(self):
        engine = MetricEngine()
        collection = engine.compute_from_observations([_obs("M-02", 1e6)], _REPO_ID, _ANALYSIS_ID)
        assert collection.get_result("M-02").value == 1e6

    def test_zero_values(self):
        engine = MetricEngine()
        collection = engine.compute_from_observations([_obs("M-01", 0.0)], _REPO_ID, _ANALYSIS_ID)
        assert collection.get_result("M-01").value == 0.0

    def test_m03_needs_5_observations(self):
        engine = MetricEngine()
        obs = [_obs("M-03", 0.5) for _ in range(5)]
        collection = engine.compute_from_observations(obs, _REPO_ID, _ANALYSIS_ID)
        assert collection.has_metric("M-03")

    def test_m03_fails_with_4(self):
        engine = MetricEngine()
        obs = [_obs("M-03", 0.5) for _ in range(4)]
        collection = engine.compute_from_observations(obs, _REPO_ID, _ANALYSIS_ID)
        assert not collection.has_metric("M-03")

    def test_m05_needs_2_observations(self):
        engine = MetricEngine()
        obs = [_obs("M-05", 2.0)]
        collection = engine.compute_from_observations(obs, _REPO_ID, _ANALYSIS_ID)
        assert not collection.has_metric("M-05")

    def test_collection_id_deterministic(self):
        engine = MetricEngine()
        obs = [_obs("M-01", 0.5)]
        c1 = engine.compute_from_observations(obs, _REPO_ID, _ANALYSIS_ID)
        c2 = engine.compute_from_observations(obs, _REPO_ID, _ANALYSIS_ID)
        assert c1.collection_id == c2.collection_id

    def test_source_observation_ids_preserved(self):
        engine = MetricEngine()
        obs = [_obs("M-02", 10.0, observation_id="obs_a"), _obs("M-02", 20.0, observation_id="obs_b")]
        collection = engine.compute_from_observations(obs, _REPO_ID, _ANALYSIS_ID)
        result = collection.get_result("M-02")
        assert "obs_a" in result.source_observation_ids
        assert "obs_b" in result.source_observation_ids

    def test_warnings_propagated(self):
        engine = MetricEngine()
        obs = [_obs("M-02", 10.0)]
        collection = engine.compute_from_observations(obs, _REPO_ID, _ANALYSIS_ID)
        # Single observation, low confidence warning may appear
        assert isinstance(collection.warnings, list)

    def test_get_result_none(self):
        engine = MetricEngine()
        collection = engine.compute_from_observations([], _REPO_ID, _ANALYSIS_ID)
        assert collection.get_result("M-01") is None
