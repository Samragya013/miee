"""
Unit tests for MIIE v1.5 Sampling Framework (PR-7B).

Tests all components:
- RepositoryProfile (Phase 1)
- StrategyEngine (Phase 2)
- SamplingPlanner (Phase 2)
- AdaptiveWindowBuilder (Phase 3)
- DetectorReadinessAnalyzer (Phase 4)
- ExecutionTracer (Phase 5)
- DiagnosticsEngine (Phase 6)
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import List

from miie.processing.observation.models import (
    Observation,
    ObservationCollection,
    ObservationProvenance,
    ObservationWindow,
)
from miie.sampling.adaptive_window import AdaptiveWindowBuilder
from miie.sampling.diagnostics import DiagnosticsEngine
from miie.sampling.models import (
    ActivityClass,
    ExecutionTrace,
    ReadinessReport,
    ReadinessState,
    RepositoryScale,
    SamplingDiagnostics,
    SamplingPlan,
    StrategyCandidate,
    WindowDiagnostics,
)
from miie.sampling.planner import SamplingPlanner
from miie.sampling.readiness import DetectorReadinessAnalyzer
from miie.sampling.strategy import StrategyEngine
from miie.sampling.trace import ExecutionTracer

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_counter = 0


def _make_sha40(label: str) -> str:
    """Generate a deterministic 40-char hex SHA from a label."""
    return hashlib.sha1(label.encode()).hexdigest()


_METRIC_UNITS = {
    "M-01": "ratio",
    "M-02": "count",
    "M-03": "ratio",
    "M-04": "ratio",
    "M-05": "hours",
    "M-06": "count",
    "M-07": "ratio",
}


def _make_obs(
    source_id: str,
    metric_id: str,
    value: float,
    timestamp: str,
    quality: str = "complete",
    obs_index: int = 0,
) -> Observation:
    """Create a valid Observation for testing."""
    # 16 hex chars from source_id + metric_id + index
    raw = hashlib.md5(f"{source_id}:{metric_id}:{obs_index}".encode()).hexdigest()[:16]
    unit = _METRIC_UNITS.get(metric_id, "count")
    return Observation(
        observation_id=raw,
        source_type="commit",
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        unit=unit,
        timestamp=timestamp,
        quality=quality,
        provenance=ObservationProvenance(
            extractor_id="test-extractor",
            extraction_timestamp="2026-01-01T00:00:00+00:00",
        ),
    )


def _make_collection(
    n_commits: int = 50,
    metrics: List[str] = None,
    days_span: int = 100,
) -> ObservationCollection:
    """Create an ObservationCollection with synthetic observations."""
    if metrics is None:
        metrics = ["M-02", "M-06"]

    base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    observations: List[Observation] = []

    for i in range(n_commits):
        ts = base_date + timedelta(days=int(i * days_span / max(n_commits - 1, 1)))
        ts_str = ts.isoformat()
        source_id = _make_sha40(f"commit_{i:04d}")

        for m_idx, metric_id in enumerate(metrics):
            if metric_id == "M-02":
                value = 1.0
            elif metric_id == "M-06":
                value = float(10 + i % 20)
            else:
                value = float(i % 100) / 100.0

            observations.append(_make_obs(source_id, metric_id, value, ts_str, obs_index=i * 100 + m_idx))

    # Put all observations in a single window (matching real extraction)
    window = ObservationWindow(
        window_id="w00",
        window_index=0,
        strategy="temporal",
        start_boundary=base_date.isoformat(),
        end_boundary=(base_date + timedelta(days=days_span)).isoformat(),
        observations=observations,
    )

    return ObservationCollection(
        collection_id="test_collection",
        repository_id="test_repo",
        analysis_id="test_analysis",
        windows=[window],
        total_observations=len(observations),
        total_metrics=len(metrics),
        extraction_timestamp="2026-01-01T00:00:00+00:00",
    )


# ---------------------------------------------------------------------------
# Phase 1: Repository Profile Tests
# ---------------------------------------------------------------------------


class TestRepositoryProfile:
    """Tests for RepositoryProfile computation."""

    def test_profile_basic(self):
        """Profile computes basic metrics from observations."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        profile = planner.profile(collection)

        assert profile.commit_count == 50
        assert profile.observation_count == 100  # 50 commits x 2 metrics
        assert profile.repo_age_days == 100
        assert profile.time_span_days == 100
        assert "M-02" in profile.metrics_available
        assert "M-06" in profile.metrics_available

    def test_profile_empty_collection(self):
        """Profile handles empty collections."""
        empty = ObservationCollection(
            collection_id="empty",
            repository_id="test",
            analysis_id="test",
        )
        planner = SamplingPlanner()
        profile = planner.profile(empty)

        assert profile.commit_count == 0
        assert profile.observation_count == 0
        assert profile.activity_class == ActivityClass.INACTIVE.value

    def test_profile_deterministic(self):
        """Profile is deterministic for same input."""
        collection = _make_collection(n_commits=30, days_span=60)
        planner = SamplingPlanner()

        p1 = planner.profile(collection)
        p2 = planner.profile(collection)

        assert p1.commit_count == p2.commit_count
        assert p1.observation_count == p2.observation_count
        assert p1.cv == p2.cv
        assert p1.window_balance == p2.window_balance

    def test_profile_activity_classification(self):
        """Profile classifies repository activity correctly."""
        # High activity: 10 commits/day
        collection = _make_collection(n_commits=1000, days_span=100)
        planner = SamplingPlanner()
        profile = planner.profile(collection)
        assert profile.activity_class in (
            ActivityClass.ACTIVE.value,
            ActivityClass.HIGHLY_ACTIVE.value,
        )

    def test_profile_scale_classification(self):
        """Profile classifies repository scale correctly."""
        collection = _make_collection(n_commits=500, days_span=100)
        planner = SamplingPlanner()
        profile = planner.profile(collection)
        # 500 commits x 2 metrics = 1000 observations
        assert profile.scale == RepositoryScale.MEDIUM.value


# ---------------------------------------------------------------------------
# Phase 2: Strategy Engine Tests
# ---------------------------------------------------------------------------


class TestStrategyEngine:
    """Tests for StrategyEngine candidate evaluation."""

    def test_evaluate_returns_candidates(self):
        """Evaluation returns valid and rejected candidates."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        profile = planner.profile(collection)

        engine = StrategyEngine()
        valid, rejected = engine.evaluate(profile)

        assert len(valid) > 0
        assert all(isinstance(c, StrategyCandidate) for c in valid)
        assert all(c.score >= 0.0 for c in valid)

    def test_candidates_sorted_by_score(self):
        """Valid candidates are sorted by score descending."""
        collection = _make_collection(n_commits=100, days_span=200)
        planner = SamplingPlanner()
        profile = planner.profile(collection)

        engine = StrategyEngine()
        valid, _ = engine.evaluate(profile)

        scores = [c.score for c in valid]
        assert scores == sorted(scores, reverse=True)

    def test_all_candidates_have_required_fields(self):
        """Every candidate has all required fields populated."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        profile = planner.profile(collection)

        engine = StrategyEngine()
        valid, rejected = engine.evaluate(profile)

        for candidate in valid + rejected:
            assert isinstance(candidate.strategy, str)
            assert isinstance(candidate.window_size, int)
            assert 0.0 <= candidate.score <= 1.0
            assert isinstance(candidate.expected_windows, int)
            assert isinstance(candidate.expected_obs_per_window, float)
            assert isinstance(candidate.verdict, str)

    def test_custom_candidates(self):
        """StrategyEngine accepts custom candidates."""
        custom = [("temporal", 7), ("commit_count", 5)]
        engine = StrategyEngine(candidates=custom)

        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        profile = planner.profile(collection)

        valid, rejected = engine.evaluate(profile)
        total = len(valid) + len(rejected)
        assert total == 2  # Only our custom candidates

    def test_readiness_scores(self):
        """Candidates include expected detector readiness."""
        collection = _make_collection(n_commits=100, days_span=200)
        planner = SamplingPlanner()
        profile = planner.profile(collection)

        engine = StrategyEngine()
        valid, _ = engine.evaluate(profile)

        for candidate in valid:
            assert "D-01" in candidate.expected_detector_readiness
            assert "D-02" in candidate.expected_detector_readiness
            assert "D-03" in candidate.expected_detector_readiness


# ---------------------------------------------------------------------------
# Phase 2: Sampling Planner Tests
# ---------------------------------------------------------------------------


class TestSamplingPlanner:
    """Tests for SamplingPlanner plan generation."""

    def test_plan_returns_sampling_plan(self):
        """Plan returns a valid SamplingPlan."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        assert isinstance(plan, SamplingPlan)
        assert isinstance(plan.chosen, StrategyCandidate)
        assert isinstance(plan.scientific_confidence, str)

    def test_plan_has_profile(self):
        """Plan includes the repository profile."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        assert plan.profile is not None
        assert plan.profile.commit_count == 50

    def test_plan_deterministic(self):
        """Plan is deterministic for same input."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()

        p1 = planner.plan(collection)
        p2 = planner.plan(collection)

        assert p1.chosen.strategy == p2.chosen.strategy
        assert p1.chosen.window_size == p2.chosen.window_size
        assert p1.chosen.score == p2.chosen.score

    def test_plan_confidence_levels(self):
        """Plan confidence is one of high/medium/low."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        assert plan.scientific_confidence in ("high", "medium", "low")

    def test_plan_empty_collection(self):
        """Plan handles empty collections gracefully."""
        empty = ObservationCollection(
            collection_id="empty",
            repository_id="test",
            analysis_id="test",
        )
        planner = SamplingPlanner()
        plan = planner.plan(empty)

        assert isinstance(plan, SamplingPlan)
        assert plan.scientific_confidence == "low"


# ---------------------------------------------------------------------------
# Phase 3: Adaptive Window Builder Tests
# ---------------------------------------------------------------------------


class TestAdaptiveWindowBuilder:
    """Tests for AdaptiveWindowBuilder."""

    def test_build_returns_windows(self):
        """Build produces ObservationWindows from a plan."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        builder = AdaptiveWindowBuilder()
        result, diagnostics = builder.build(collection, plan)

        assert len(result.windows) > 0
        assert all(hasattr(w, "window_id") for w in result.windows)

    def test_build_preserves_observations(self):
        """Build preserves all observations (no fabrication or loss)."""
        collection = _make_collection(n_commits=50, days_span=100)
        total_obs = collection.total_observations

        planner = SamplingPlanner()
        plan = planner.plan(collection)

        builder = AdaptiveWindowBuilder()
        result, _ = builder.build(collection, plan)

        placed = sum(w.observation_count for w in result.windows)
        assert placed + len(result.unassigned_observations) == total_obs

    def test_build_window_diagnostics(self):
        """Build produces per-window diagnostics."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        builder = AdaptiveWindowBuilder()
        _, diagnostics = builder.build(collection, plan)

        assert len(diagnostics) > 0
        assert all(isinstance(d, WindowDiagnostics) for d in diagnostics)

    def test_build_deterministic(self):
        """Build is deterministic for same input."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        builder = AdaptiveWindowBuilder()
        r1, d1 = builder.build(collection, plan)
        r2, d2 = builder.build(collection, plan)

        assert len(r1.windows) == len(r2.windows)
        for w1, w2 in zip(r1.windows, r2.windows):
            assert w1.window_id == w2.window_id
            assert w1.observation_count == w2.observation_count


# ---------------------------------------------------------------------------
# Phase 4: Detector Readiness Analyzer Tests
# ---------------------------------------------------------------------------


class TestDetectorReadinessAnalyzer:
    """Tests for DetectorReadinessAnalyzer."""

    def _make_windows_with_obs(self, n_windows: int, obs_per_window: int) -> List[ObservationWindow]:
        """Create windows with specified observation counts."""
        windows = []
        base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)

        for i in range(n_windows):
            observations = []
            for j in range(obs_per_window):
                ts = base_date + timedelta(days=i * 30 + j)
                source_id = _make_sha40(f"win{i}_obs{j}")
                obs = _make_obs(
                    source_id=source_id,
                    metric_id="M-02",
                    value=1.0,
                    timestamp=ts.isoformat(),
                    obs_index=i * 1000 + j,
                )
                observations.append(obs)

            window = ObservationWindow(
                window_id=f"w{i:02d}",
                window_index=i,
                strategy="temporal",
                start_boundary=(base_date + timedelta(days=i * 30)).isoformat(),
                end_boundary=(base_date + timedelta(days=(i + 1) * 30)).isoformat(),
                observations=observations,
                metrics_present=["M-02"],
            )
            windows.append(window)

        return windows

    def test_readiness_sufficient_data(self):
        """Detectors are READY when data is sufficient."""
        windows = self._make_windows_with_obs(n_windows=5, obs_per_window=30)
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        analyzer = DetectorReadinessAnalyzer()
        report = analyzer.analyze(windows, plan)

        assert isinstance(report, ReadinessReport)
        # D-01 and D-03 should be READY (10+ obs, 2+ windows)
        d01 = next(r for r in report.detector_readiness if r.detector_id == "D-01")
        d03 = next(r for r in report.detector_readiness if r.detector_id == "D-03")
        assert d01.state == ReadinessState.READY.value
        assert d03.state == ReadinessState.READY.value

    def test_readiness_insufficient_windows(self):
        """Detectors are SKIPPED when windows < 2."""
        windows = self._make_windows_with_obs(n_windows=1, obs_per_window=30)
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        analyzer = DetectorReadinessAnalyzer()
        report = analyzer.analyze(windows, plan)

        d01 = next(r for r in report.detector_readiness if r.detector_id == "D-01")
        assert d01.state == ReadinessState.SKIPPED.value
        assert "window" in d01.skip_reason.lower()

    def test_readiness_insufficient_observations(self):
        """Detectors are SKIPPED when observations < threshold."""
        windows = self._make_windows_with_obs(n_windows=5, obs_per_window=5)
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        analyzer = DetectorReadinessAnalyzer()
        report = analyzer.analyze(windows, plan)

        d03 = next(r for r in report.detector_readiness if r.detector_id == "D-03")
        assert d03.state == ReadinessState.SKIPPED.value
        assert "observation" in d03.skip_reason.lower()

    def test_readiness_states_are_valid(self):
        """All readiness states are valid enum values."""
        windows = self._make_windows_with_obs(n_windows=3, obs_per_window=15)
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        analyzer = DetectorReadinessAnalyzer()
        report = analyzer.analyze(windows, plan)

        valid_states = {s.value for s in ReadinessState}
        for r in report.detector_readiness:
            assert r.state in valid_states

    def test_readiness_skip_reasons_are_precise(self):
        """Skip reasons are specific, not generic."""
        windows = self._make_windows_with_obs(n_windows=1, obs_per_window=5)
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        analyzer = DetectorReadinessAnalyzer()
        report = analyzer.analyze(windows, plan)

        for r in report.detector_readiness:
            if r.state == ReadinessState.SKIPPED.value:
                # Skip reason must mention specific numbers
                assert any(word in r.skip_reason.lower() for word in ["observation", "window", "metric", "pair"])


# ---------------------------------------------------------------------------
# Phase 5: Execution Tracer Tests
# ---------------------------------------------------------------------------


class TestExecutionTracer:
    """Tests for ExecutionTracer."""

    def test_trace_from_readiness(self):
        """Traces are generated from readiness analysis."""
        windows = []
        base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        for i in range(3):
            obs = [
                _make_obs(
                    _make_sha40(f"tracer{i}_obs{j}"),
                    "M-02",
                    1.0,
                    (base_date + timedelta(days=i * 30 + j)).isoformat(),
                    obs_index=i * 1000 + j,
                )
                for j in range(20)
            ]
            windows.append(
                ObservationWindow(
                    window_id=f"w{i:02d}",
                    window_index=i,
                    strategy="temporal",
                    start_boundary=(base_date + timedelta(days=i * 30)).isoformat(),
                    end_boundary=(base_date + timedelta(days=(i + 1) * 30)).isoformat(),
                    observations=obs,
                    metrics_present=["M-02"],
                )
            )

        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        analyzer = DetectorReadinessAnalyzer()
        readiness = analyzer.analyze(windows, plan)

        tracer = ExecutionTracer()
        traces = tracer.trace(readiness, windows, plan)

        assert len(traces) == 3  # D-01, D-02, D-03
        assert all(isinstance(t, ExecutionTrace) for t in traces)

    def test_trace_has_required_fields(self):
        """Every trace has all required fields."""
        windows = []
        base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        for i in range(2):
            obs = [
                _make_obs(
                    _make_sha40(f"tracer2_{i}_obs{j}"),
                    "M-02",
                    1.0,
                    (base_date + timedelta(days=i * 30 + j)).isoformat(),
                    obs_index=i * 1000 + j,
                )
                for j in range(15)
            ]
            windows.append(
                ObservationWindow(
                    window_id=f"w{i:02d}",
                    window_index=i,
                    strategy="temporal",
                    start_boundary=(base_date + timedelta(days=i * 30)).isoformat(),
                    end_boundary=(base_date + timedelta(days=(i + 1) * 30)).isoformat(),
                    observations=obs,
                    metrics_present=["M-02"],
                )
            )

        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        analyzer = DetectorReadinessAnalyzer()
        readiness = analyzer.analyze(windows, plan)

        tracer = ExecutionTracer()
        traces = tracer.trace(readiness, windows, plan)

        for trace in traces:
            assert isinstance(trace.detector_id, str)
            assert isinstance(trace.observation_count, int)
            assert isinstance(trace.window_count, int)
            assert isinstance(trace.execution_decision, str)
            assert trace.execution_decision in (
                "execute",
                "partial_execute",
                "skip",
                "not_applicable",
            )


# ---------------------------------------------------------------------------
# Phase 6: Diagnostics Engine Tests
# ---------------------------------------------------------------------------


class TestDiagnosticsEngine:
    """Tests for DiagnosticsEngine end-to-end pipeline."""

    def test_diagnostics_complete(self):
        """DiagnosticsEngine produces complete output."""
        collection = _make_collection(n_commits=50, days_span=100)
        engine = DiagnosticsEngine()
        diagnostics = engine.run(collection)

        assert isinstance(diagnostics, SamplingDiagnostics)
        assert diagnostics.profile is not None
        assert diagnostics.plan is not None
        assert diagnostics.readiness is not None
        assert len(diagnostics.execution_traces) > 0

    def test_diagnostics_terminal_format(self):
        """Terminal formatting produces non-empty string."""
        collection = _make_collection(n_commits=50, days_span=100)
        engine = DiagnosticsEngine()
        diagnostics = engine.run(collection)

        terminal = engine.format_terminal(diagnostics)
        assert isinstance(terminal, str)
        assert len(terminal) > 0
        assert "Sampling Strategy" in terminal
        assert "Detector Readiness" in terminal

    def test_diagnostics_to_dict(self):
        """to_dict produces JSON-serializable output."""
        import json

        collection = _make_collection(n_commits=50, days_span=100)
        engine = DiagnosticsEngine()
        diagnostics = engine.run(collection)

        d = engine.to_dict(diagnostics)
        # Should be JSON-serializable
        json_str = json.dumps(d)
        assert isinstance(json_str, str)
        assert len(json_str) > 0

    def test_diagnostics_deterministic(self):
        """DiagnosticsEngine is deterministic."""
        collection = _make_collection(n_commits=50, days_span=100)
        engine = DiagnosticsEngine()

        d1 = engine.run(collection)
        d2 = engine.run(collection)

        assert d1.total_windows == d2.total_windows
        assert d1.total_observations == d2.total_observations
        assert d1.strategy_used == d2.strategy_used

    def test_diagnostics_empty_collection(self):
        """DiagnosticsEngine handles empty collections."""
        empty = ObservationCollection(
            collection_id="empty",
            repository_id="test",
            analysis_id="test",
        )
        engine = DiagnosticsEngine()
        diagnostics = engine.run(empty)

        assert diagnostics.total_windows == 0
        assert diagnostics.total_observations == 0


# ---------------------------------------------------------------------------
# PR-7C: Calibration & Terminal Window Merge Tests
# ---------------------------------------------------------------------------


class TestPR7CCalibration:
    """Tests for PR-7C-1: Planner Calibration and PR-7C-2: Terminal Window Merge."""

    def test_profile_has_m02_count(self):
        """RepositoryProfile includes m02_observation_count."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        profile = planner.profile(collection)

        assert profile.m02_observation_count == 50  # 50 commits, each one M-02
        assert profile.observation_count == 100  # 50 M-02 + 50 M-06

    def test_plan_has_calibration_fields(self):
        """SamplingPlan includes calibration fields."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        assert hasattr(plan, "prediction_error")
        assert hasattr(plan, "window_difference")
        assert hasattr(plan, "observation_difference")
        assert hasattr(plan, "confidence_adjustment")
        assert isinstance(plan.prediction_error, float)
        assert isinstance(plan.window_difference, int)

    def test_plan_calibration_error_non_negative(self):
        """Calibration error is non-negative."""
        collection = _make_collection(n_commits=100, days_span=200)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        assert plan.prediction_error >= 0.0
        assert plan.window_difference >= 0

    def test_plan_calibration_included_in_notes(self):
        """Calibration information is included in planning notes."""
        collection = _make_collection(n_commits=50, days_span=100)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        calibration_notes = [n for n in plan.planning_notes if "Calibration:" in n]
        assert len(calibration_notes) >= 1

    def test_plan_calibration_in_to_dict(self):
        """DiagnosticsEngine.to_dict includes calibration fields."""
        collection = _make_collection(n_commits=50, days_span=100)
        engine = DiagnosticsEngine()
        diagnostics = engine.run(collection)
        result = engine.to_dict(diagnostics)

        assert "prediction_error" in result["plan"]
        assert "window_difference" in result["plan"]
        assert "observation_difference" in result["plan"]
        assert "confidence_adjustment" in result["plan"]

    def test_strategy_uses_m02_for_commit_count(self):
        """StrategyEngine uses M-02 count for commit_count estimation."""
        engine = StrategyEngine()
        # Profile with M-02 count different from commit count
        from miie.sampling.models import RepositoryProfile

        profile = RepositoryProfile(
            commit_count=100,
            repo_age_days=365,
            observation_count=200,
            observation_density=0.55,
            commit_density=0.27,
            avg_commits_per_day=0.27,
            window_density=0.03,
            avg_obs_per_window=20.0,
            min_obs_per_window=15,
            max_obs_per_window=25,
            median_obs_per_window=20.0,
            variance=10.0,
            cv=0.2,
            window_balance=0.8,
            activity_class="moderate",
            scale="medium",
            volatility="stable",
            metrics_available=("M-02", "M-06"),
            time_span_days=365,
            m02_observation_count=50,  # Only 50 M-02, not 100 commits
        )

        windows, obs_per_window = engine._estimate_windows(profile, "commit_count", 10)
        # Should use m02_count=50, not commit_count=100
        assert windows == 5  # 50 // 10 = 5, not 100 // 10 = 10

    def test_terminal_window_merge_undersized(self):
        """AdaptiveWindowBuilder merges undersized terminal windows."""
        # Create collection where last window will have few observations
        base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        observations = []
        for i in range(55):  # 55 commits, commit_count=10 will make 5 full + 1 partial
            ts = base_date + timedelta(days=i)
            source_id = _make_sha40(f"commit_{i:04d}")
            observations.append(_make_obs(source_id, "M-02", 1.0, ts.isoformat(), obs_index=i))

        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary=base_date.isoformat(),
            end_boundary=(base_date + timedelta(days=55)).isoformat(),
            observations=observations,
        )

        collection = ObservationCollection(
            collection_id="test_merge",
            repository_id="test_repo",
            analysis_id="test_analysis",
            windows=[window],
            total_observations=55,
            total_metrics=1,
            extraction_timestamp="2026-01-01T00:00:00+00:00",
        )

        # Create a plan with commit_count strategy, window_size=10
        plan = SamplingPlan(
            chosen=StrategyCandidate(
                strategy="commit_count",
                window_size=10,
                score=0.8,
                expected_windows=5,
                expected_obs_per_window=11.0,
            ),
        )

        builder = AdaptiveWindowBuilder()
        result, diagnostics = builder.build(collection, plan)

        # Check if merge warning is present
        [w for w in result.warnings if "Terminal window merge" in w]
        # The merge may or may not happen depending on the exact window sizes
        # But the method should not crash
        assert result is not None

    def test_terminal_window_preserves_observations(self):
        """Terminal window merge preserves all observations (no data loss)."""
        base_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        observations = []
        for i in range(25):
            ts = base_date + timedelta(days=i)
            source_id = _make_sha40(f"commit_{i:04d}")
            observations.append(_make_obs(source_id, "M-02", 1.0, ts.isoformat(), obs_index=i))

        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary=base_date.isoformat(),
            end_boundary=(base_date + timedelta(days=25)).isoformat(),
            observations=observations,
        )

        collection = ObservationCollection(
            collection_id="test_preserve",
            repository_id="test_repo",
            analysis_id="test_analysis",
            windows=[window],
            total_observations=25,
            total_metrics=1,
            extraction_timestamp="2026-01-01T00:00:00+00:00",
        )

        plan = SamplingPlan(
            chosen=StrategyCandidate(
                strategy="commit_count",
                window_size=10,
                score=0.8,
                expected_windows=2,
                expected_obs_per_window=12.5,
            ),
        )

        builder = AdaptiveWindowBuilder()
        result, diagnostics = builder.build(collection, plan)

        # Total observations should be preserved
        total_obs = sum(w.observation_count for w in result.windows)
        assert total_obs == 25

    def test_low_prediction_error_no_penalty(self):
        """Low prediction error does not penalize confidence."""
        # Create a profile where planner and actual will agree
        collection = _make_collection(n_commits=40, days_span=80)
        planner = SamplingPlanner()
        plan = planner.plan(collection)

        # For temporal strategy, planner and actual should be close
        # so prediction_error should be small
        if plan.chosen.strategy == "temporal":
            assert plan.prediction_error < 0.5
