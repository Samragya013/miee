"""Comprehensive Tests for Observation-Aware Scoring (PR-6 Phase 8).

Tests cover:
- Integrity Score observation-aware computation
- Confidence Score observation-aware factors
- Observation quality factor
- Scoring utility functions
- Sparse, balanced, and unbalanced window scenarios
- Missing evidence handling
- Legacy compatibility
- Deterministic scoring
- Regression tests
"""

import datetime
from typing import Dict, List

from miie.processing.scoring.engine import ScoringEngine
from miie.processing.scoring.utils import (
    compute_balance_factor,
    compute_clamped,
    compute_coverage_ratio,
    compute_cv,
    compute_detector_success_factor,
    compute_mean,
    compute_missing_data_factor,
    compute_observation_quality_factor,
    compute_sample_size_factor,
    compute_std,
    compute_variance_factor,
    safe_divide,
)
from miie.schemas.models import (
    DetectorResults,
    EvidencePackage,
    MetricDataFrame,
    Provenance,
    ScorePackage,
    WindowDefinition,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_window(
    window_id: str,
    start: datetime.date,
    end: datetime.date,
    commits: int,
    strategy: str = "fixed_size",
) -> WindowDefinition:
    return WindowDefinition(
        window_id=window_id,
        start_date=start,
        end_date=end,
        commits=commits,
        strategy=strategy,
    )


def _make_evidence(
    windows: List[WindowDefinition],
    detector_results: DetectorResults,
    observation_summary: Dict = None,
    detector_execution_metadata: Dict = None,
    observation_quality: Dict = None,
) -> EvidencePackage:
    """Create a minimal EvidencePackage for testing."""
    provenance = Provenance(
        miie_version="1.0.0",
        config_hash="test-hash",
        timestamp=datetime.datetime(2023, 6, 15, tzinfo=datetime.timezone.utc).isoformat(),
        seed=42,
        platform="test",
        python_version="3.11.0",
        dependency_hash="dep-hash",
    )
    return EvidencePackage(
        provenance=provenance,
        windows=windows,
        metrics={},
        detector_outputs=detector_results,
        scores=None,
        warnings=[],
        observation_summary=observation_summary or {},
        detector_execution_metadata=detector_execution_metadata or {},
    )


# ---------------------------------------------------------------------------
# Utility Function Tests
# ---------------------------------------------------------------------------


class TestScoringUtils:
    """Tests for scoring utility functions."""

    def test_safe_divide_normal(self):
        assert safe_divide(10.0, 2.0) == 5.0

    def test_safe_divide_by_zero(self):
        assert safe_divide(10.0, 0.0) == 0.0

    def test_safe_divide_by_zero_custom_default(self):
        assert safe_divide(10.0, 0.0, default=-1.0) == -1.0

    def test_safe_divide_by_near_zero(self):
        assert safe_divide(10.0, 1e-20) == 0.0

    def test_compute_mean_empty(self):
        assert compute_mean([]) == 0.0

    def test_compute_mean_single(self):
        assert compute_mean([5.0]) == 5.0

    def test_compute_mean_multiple(self):
        assert abs(compute_mean([1.0, 2.0, 3.0]) - 2.0) < 1e-10

    def test_compute_std_empty(self):
        assert compute_std([]) == 0.0

    def test_compute_std_single(self):
        assert compute_std([5.0]) == 0.0

    def test_compute_std_known(self):
        # population std of [2, 4, 4, 4, 5, 5, 7, 9] ≈ 2.0
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        assert abs(compute_std(values) - 2.0) < 0.01

    def test_compute_cv_empty(self):
        assert compute_cv([]) == 0.0

    def test_compute_cv_single(self):
        assert compute_cv([5.0]) == 0.0

    def test_compute_cv_all_zeros(self):
        assert compute_cv([0.0, 0.0, 0.0]) == 0.0

    def test_compute_cv_nonzero_mean(self):
        values = [10.0, 10.0, 10.0]
        assert abs(compute_cv(values)) < 1e-10

    def test_compute_clamped_within_range(self):
        assert compute_clamped(0.5) == 0.5

    def test_compute_clamped_below(self):
        assert compute_clamped(-0.5) == 0.0

    def test_compute_clamped_above(self):
        assert compute_clamped(1.5) == 1.0

    def test_compute_coverage_ratio_normal(self):
        assert abs(compute_coverage_ratio(80, 100) - 0.8) < 1e-10

    def test_compute_coverage_ratio_zero_total(self):
        assert compute_coverage_ratio(0, 0) == 0.0

    def test_compute_coverage_ratio_full(self):
        assert compute_coverage_ratio(100, 100) == 1.0

    def test_compute_balance_factor_empty(self):
        assert compute_balance_factor([]) == 0.0

    def test_compute_balance_factor_single(self):
        # Single window is perfectly balanced (nothing to unbalance)
        assert compute_balance_factor([10.0]) == 1.0

    def test_compute_balance_factor_equal(self):
        assert compute_balance_factor([10.0, 10.0, 10.0]) == 1.0

    def test_compute_balance_factor_unequal(self):
        # Sizes: [1, 100] → std/mean ≈ 0.99, factor ≈ 0.01
        result = compute_balance_factor([1.0, 100.0])
        assert 0.0 <= result <= 0.1

    def test_compute_sample_size_factor_normal(self):
        assert abs(compute_sample_size_factor(25.0, 50.0) - 0.5) < 1e-10

    def test_compute_sample_size_factor_oversized(self):
        assert compute_sample_size_factor(100.0, 50.0) == 1.0

    def test_compute_variance_factor_low_cv(self):
        assert compute_variance_factor(0.1) == 0.8

    def test_compute_variance_factor_high_cv(self):
        assert compute_variance_factor(1.0) == 0.0

    def test_compute_missing_data_factor_none_missing(self):
        assert compute_missing_data_factor(0, 100) == 1.0

    def test_compute_missing_data_factor_all_missing(self):
        assert compute_missing_data_factor(100, 100) == 0.0

    def test_compute_detector_success_factor_all_success(self):
        assert compute_detector_success_factor(10, 10) == 1.0

    def test_compute_detector_success_factor_none_success(self):
        assert compute_detector_success_factor(0, 10) == 0.0

    def test_compute_observation_quality_factor_all_complete(self):
        assert compute_observation_quality_factor(10, 0, 0) == 1.0

    def test_compute_observation_quality_factor_all_estimated(self):
        assert compute_observation_quality_factor(0, 0, 10) == 0.0

    def test_compute_observation_quality_factor_mixed(self):
        # complete=8, partial=2, estimated=0 → (8 + 0.5*2) / 10 = 0.9
        assert abs(compute_observation_quality_factor(8, 2, 0) - 0.9) < 1e-10

    def test_compute_observation_quality_factor_zero_total(self):
        assert compute_observation_quality_factor(0, 0, 0) == 0.0


# ---------------------------------------------------------------------------
# Integrity Score Observation-Aware Tests
# ---------------------------------------------------------------------------


class TestIntegrityScoreObservationAware:
    """Tests for IS computation with observation-level evidence."""

    def _make_engine_and_inputs(self):
        engine = ScoringEngine()
        detector_results = DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": True, "ks_statistic": 0.3},
                "D-02": {},
                "D-03": {},
            }
        )
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="run-001",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-01": {"w01": [1.0, 2.0, 3.0], "w02": [4.0, 5.0, 6.0]},
                "M-02": {"w01": [0.1, 0.2], "w02": [0.3, 0.4]},
            },
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 10),
            _make_window("w02", datetime.date(2020, 2, 1), datetime.date(2020, 2, 29), 10),
        ]
        return engine, detector_results, metric_dataframe, windows

    def test_is_with_full_observation_coverage(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        evidence = _make_evidence(
            windows,
            dr,
            observation_summary={
                "total_observations": 200,
                "per_metric": {
                    "M-01": {"count": 100, "window_count": 2},
                    "M-02": {"count": 100, "window_count": 2},
                },
                "observation_quality": {"complete": 200, "partial": 0, "estimated": 0},
            },
        )

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence,
        )
        assert isinstance(score, ScorePackage)
        assert 0.0 <= score.integrity.overall <= 1.0
        # With full observations, severity should not be reduced
        assert "M-01" in score.integrity.per_metric
        assert "M-02" in score.integrity.per_metric

    def test_is_with_low_observation_coverage(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        # Low observation coverage: only 5 observations
        evidence_low = _make_evidence(
            windows,
            dr,
            observation_summary={
                "total_observations": 5,
                "per_metric": {
                    "M-01": {"count": 3, "window_count": 1},
                    "M-02": {"count": 2, "window_count": 1},
                },
                "observation_quality": {"complete": 3, "partial": 0, "estimated": 2},
            },
        )

        evidence_full = _make_evidence(
            windows,
            dr,
            observation_summary={
                "total_observations": 200,
                "per_metric": {
                    "M-01": {"count": 100, "window_count": 2},
                    "M-02": {"count": 100, "window_count": 2},
                },
                "observation_quality": {"complete": 200, "partial": 0, "estimated": 0},
            },
        )

        score_low = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence_low,
        )
        score_full = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence_full,
        )

        # Low observation coverage should yield higher IS (less severe penalty)
        # because the severity multiplier reduces the penalty
        assert score_low.integrity.overall >= score_full.integrity.overall

    def test_is_without_evidence_package(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert isinstance(score, ScorePackage)
        assert 0.0 <= score.integrity.overall <= 1.0

    def test_is_per_metric_deterministic_ordering(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        # Run twice to verify deterministic ordering
        score1 = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        score2 = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert list(score1.integrity.per_metric.keys()) == list(score2.integrity.per_metric.keys())


# ---------------------------------------------------------------------------
# Confidence Score Observation-Aware Tests
# ---------------------------------------------------------------------------


class TestConfidenceScoreObservationAware:
    """Tests for CS computation with observation-level evidence."""

    def _make_engine_and_inputs(self):
        engine = ScoringEngine()
        detector_results = DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="run-001",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-01": {"w01": [10.0, 12.0, 11.0], "w02": [9.0, 13.0, 10.0]},
            },
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 10),
            _make_window("w02", datetime.date(2020, 2, 1), datetime.date(2020, 2, 29), 10),
        ]
        return engine, detector_results, metric_dataframe, windows

    def test_cs_has_observation_quality_factor(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert "observation_quality" in score.confidence.factors

    def test_cs_observation_quality_factor_with_evidence(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        evidence = _make_evidence(
            windows,
            dr,
            observation_summary={
                "total_observations": 100,
                "per_metric": {"M-01": {"count": 50, "window_count": 2}},
                "observation_quality": {"complete": 80, "partial": 15, "estimated": 5},
            },
        )

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence,
        )

        # observation_quality factor: (80 + 0.5*15) / 100 = 0.875
        expected_quality = (80 + 0.5 * 15) / 100
        assert abs(score.confidence.factors["observation_quality"] - expected_quality) < 1e-6

    def test_cs_sample_size_factor_uses_observations(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        evidence = _make_evidence(
            windows,
            dr,
            observation_summary={
                "total_observations": 200,
                "per_metric": {"M-01": {"count": 200, "window_count": 2}},
            },
        )

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence,
        )

        # 200 observations / 50 target = 1.0 (capped)
        assert score.confidence.factors["sample_size"] == 1.0

    def test_cs_window_balance_uses_observations(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        evidence = _make_evidence(
            windows,
            dr,
            observation_summary={
                "total_observations": 100,
                "per_metric": {"M-01": {"count": 100, "window_count": 2}},
            },
        )

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence,
        )

        # Balance factor is computed; should be in [0, 1]
        assert 0.0 <= score.confidence.factors["window_balance"] <= 1.0

    def test_cs_missing_data_factor_uses_observations(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        evidence = _make_evidence(
            windows,
            dr,
            observation_summary={
                "total_observations": 100,
                "per_metric": {"M-01": {"count": 50, "window_count": 2}},
            },
        )

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence,
        )

        # All metrics have observation data, so missing_data should be high
        assert score.confidence.factors["missing_data"] >= 0.5

    def test_cs_without_evidence_uses_fallback(self):
        engine, dr, mdf, windows = self._make_engine_and_inputs()

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )

        # All factors should be present
        assert "sample_size" in score.confidence.factors
        assert "variance" in score.confidence.factors
        assert "missing_data" in score.confidence.factors
        assert "window_balance" in score.confidence.factors
        assert "detector_success" in score.confidence.factors
        assert "observation_quality" in score.confidence.factors
        assert 0.0 <= score.confidence.overall <= 1.0


# ---------------------------------------------------------------------------
# Window Scenario Tests
# ---------------------------------------------------------------------------


class TestWindowScenarios:
    """Tests for scoring with various window configurations."""

    def _make_engine(self):
        return ScoringEngine()

    def _make_detector_results(self):
        return DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})

    def test_balanced_windows(self):
        engine = self._make_engine()
        dr = self._make_detector_results()
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0], "w02": [2.0], "w03": [3.0]}},
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 10),
            _make_window("w02", datetime.date(2020, 2, 1), datetime.date(2020, 2, 29), 10),
            _make_window("w03", datetime.date(2020, 3, 1), datetime.date(2020, 3, 31), 10),
        ]
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert score.confidence.factors["window_balance"] == 1.0

    def test_unbalanced_windows(self):
        engine = self._make_engine()
        dr = self._make_detector_results()
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0], "w02": [2.0]}},
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 1),
            _make_window("w02", datetime.date(2020, 2, 1), datetime.date(2020, 2, 29), 100),
        ]
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert 0.0 <= score.confidence.factors["window_balance"] < 0.5

    def test_single_window(self):
        engine = self._make_engine()
        dr = self._make_detector_results()
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0]}},
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 10),
        ]
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert isinstance(score, ScorePackage)


# ---------------------------------------------------------------------------
# Missing Evidence Handling Tests
# ---------------------------------------------------------------------------


class TestMissingEvidence:
    """Tests for scoring when evidence is missing or incomplete."""

    def test_no_evidence_package(self):
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={"D-01": {}, "D-02": {}})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0]}},
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5)]
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert isinstance(score, ScorePackage)
        assert 0.0 <= score.confidence.overall <= 1.0

    def test_empty_observation_summary(self):
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={"D-01": {}})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0]}},
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5)]
        evidence = _make_evidence(windows, dr, observation_summary={})
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            evidence_package=evidence,
        )
        assert isinstance(score, ScorePackage)

    def test_no_detectors(self):
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0]}},
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5)]
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )
        assert score.integrity.overall == 1.0
        assert score.confidence.overall == 0.0

    def test_no_windows(self):
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={"D-01": {}})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0]}},
        )
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=[],
        )
        assert score.integrity.overall == 1.0
        assert score.confidence.overall == 0.0


# ---------------------------------------------------------------------------
# Legacy Compatibility Tests
# ---------------------------------------------------------------------------


class TestLegacyCompatibility:
    """Tests that legacy scoring still works without observation evidence."""

    def test_legacy_no_evidence_package(self):
        engine = ScoringEngine()
        dr = DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": True, "ks_statistic": 0.2},
                "D-02": {"correlation_breakdown": False},
                "D-03": {"threshold_compressed": False},
            }
        )
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-01": {"w01": [10.0, 11.0, 12.0], "w02": [9.0, 10.0, 11.0]},
                "M-02": {"w01": [5.0, 6.0], "w02": [4.0, 5.0]},
            },
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 10),
            _make_window("w02", datetime.date(2020, 2, 1), datetime.date(2020, 2, 29), 10),
        ]

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
        )

        assert isinstance(score, ScorePackage)
        assert 0.0 <= score.integrity.overall <= 1.0
        assert 0.0 <= score.confidence.overall <= 1.0
        # All 6 factors present
        assert len(score.confidence.factors) == 6

    def test_legacy_with_empty_metrics(self):
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={"D-01": {}})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={},
        )
        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=[],
        )
        assert score.integrity.overall == 1.0
        assert score.confidence.overall == 0.0

    def test_legacy_with_detector_weights(self):
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0]}},
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5)]

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            detector_weights={"D-01": 0.5, "D-02": 0.3, "D-03": 0.2},
        )
        assert isinstance(score, ScorePackage)


# ---------------------------------------------------------------------------
# Deterministic Scoring Tests
# ---------------------------------------------------------------------------


class TestDeterministicScoring:
    """Tests that scoring is deterministic and reproducible."""

    def test_same_inputs_same_output(self):
        engine = ScoringEngine()
        dr = DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": True, "ks_statistic": 0.25},
                "D-02": {"correlation_breakdown": True, "delta_r": 0.15},
                "D-03": {"threshold_compressed": False},
            }
        )
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-01": {"w01": [1.0, 2.0, 3.0]},
                "M-02": {"w01": [4.0, 5.0, 6.0]},
            },
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 10),
        ]

        scores = []
        for _ in range(5):
            s = engine.compute_integrity_score(
                detector_results=dr,
                metric_dataframe=mdf,
                windows=windows,
            )
            scores.append(s)

        # All runs should produce identical scores
        for s in scores[1:]:
            assert s.integrity.overall == scores[0].integrity.overall
            assert s.confidence.overall == scores[0].confidence.overall
            assert s.integrity.per_metric == scores[0].integrity.per_metric
            assert s.confidence.factors == scores[0].confidence.factors

    def test_metric_ordering_deterministic(self):
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={"D-01": {}})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-03": {"w01": [3.0]},
                "M-01": {"w01": [1.0]},
                "M-02": {"w01": [2.0]},
            },
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5)]

        s1 = engine.compute_integrity_score(dr, mdf, windows)
        s2 = engine.compute_integrity_score(dr, mdf, windows)

        # Per-metric keys should be in sorted order
        assert list(s1.integrity.per_metric.keys()) == ["M-01", "M-02", "M-03"]
        assert list(s2.integrity.per_metric.keys()) == ["M-01", "M-02", "M-03"]


# ---------------------------------------------------------------------------
# Regression Tests
# ---------------------------------------------------------------------------


class TestRegression:
    """Regression tests to prevent score drift."""

    def test_no_drift_baseline(self):
        """Baseline: no detectors firing → IS=1.0, CS depends on data."""
        engine = ScoringEngine()
        dr = DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [10.0, 11.0, 12.0]}},
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 10)]

        score = engine.compute_integrity_score(dr, mdf, windows)

        # No detectors firing → all severity = 0 → IS = 1.0
        assert score.integrity.overall == 1.0

    def test_single_detector_drift_only(self):
        """D-01 only with explicit TFS weights: IS = 1.0 - 0.40 * d1."""
        engine = ScoringEngine()
        dr = DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": True, "ks_statistic": 0.25},
                "D-02": {},
                "D-03": {},
            }
        )
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0, 2.0]}},
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5)]

        score = engine.compute_integrity_score(
            detector_results=dr,
            metric_dataframe=mdf,
            windows=windows,
            detector_weights={"D-01": 0.40, "D-02": 0.35, "D-03": 0.25},
        )

        # d1 = min(1.0, 0.25/0.5) = 0.5
        # IS = 1.0 - (0.40 * 0.5) = 0.80
        assert abs(score.integrity.overall - 0.80) < 0.01

    def test_all_detectors_firing(self):
        """All detectors firing at max severity → IS should be low."""
        engine = ScoringEngine()
        dr = DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": True, "ks_statistic": 1.0},
                "D-02": {"correlation_breakdown": True, "delta_r": 1.0},
                "D-03": {"threshold_compressed": True, "compression_index": 1.0},
            }
        )
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={"M-01": {"w01": [1.0]}},
        )
        windows = [_make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5)]

        score = engine.compute_integrity_score(dr, mdf, windows)

        # All severities at 1.0
        # IS = 1.0 - (0.40*1.0 + 0.35*1.0 + 0.25*1.0) = 0.0
        assert score.integrity.overall == 0.0

    def test_score_range_invariants(self):
        """All scores must be in [0, 1]."""
        engine = ScoringEngine()
        dr = DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": True, "ks_statistic": 0.7},
                "D-02": {"correlation_breakdown": True, "delta_r": 0.5},
                "D-03": {"threshold_compressed": True, "compression_index": 0.3},
            }
        )
        mdf = MetricDataFrame(
            repo_id="test",
            run_id="run1",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-01": {"w01": [1.0, 2.0, None], "w02": [3.0]},
                "M-02": {"w01": []},
            },
        )
        windows = [
            _make_window("w01", datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 5),
            _make_window("w02", datetime.date(2020, 2, 1), datetime.date(2020, 2, 29), 3),
        ]

        score = engine.compute_integrity_score(dr, mdf, windows)

        assert 0.0 <= score.integrity.overall <= 1.0
        assert 0.0 <= score.confidence.overall <= 1.0
        for metric_id, val in score.integrity.per_metric.items():
            assert 0.0 <= val <= 1.0, f"{metric_id} out of range"
        for factor_name, val in score.confidence.factors.items():
            assert 0.0 <= val <= 1.0, f"{factor_name} out of range"
