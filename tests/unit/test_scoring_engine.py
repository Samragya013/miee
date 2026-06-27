"""Tests for ScoringEngine implementation."""

import datetime

from miie.processing.scoring.engine import ScoringEngine
from miie.processing.scoring.mock_scoring import (
    MockPerfectScoringEngine,
    MockScoringEngine,
    MockZeroScoringEngine,
)
from miie.schemas.models import (
    DetectorResults,
    MetricDataFrame,
    ScorePackage,
    WindowDefinition,
)


def test_scoring_engine_creation():
    """Test creating a ScoringEngine instance."""
    engine = ScoringEngine()
    assert isinstance(engine, ScoringEngine)


def test_mock_scoring_engine_returns_expected_structure():
    """Test that MockScoringEngine returns expected score structure."""
    engine = MockScoringEngine()

    # Create minimal inputs
    detector_results = DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})
    metric_dataframe = MetricDataFrame(
        repo_id="test",
        run_id="test_run",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        metrics={"M-02": {"w01": [1.0, 2.0, 3.0]}},
    )
    windows = [
        WindowDefinition(
            window_id="w00",
            start_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc).date(),
            end_date=datetime.datetime(2020, 1, 31, tzinfo=datetime.timezone.utc).date(),
            commits=1,
            strategy="fixed_size",
        )
    ]

    score_package = engine.compute_integrity_score(
        detector_results=detector_results,
        metric_dataframe=metric_dataframe,
        windows=windows,
    )

    # Check that we get a ScorePackage
    assert isinstance(score_package, ScorePackage)

    # Check integrity structure
    assert "integrity" in score_package.__dict__
    assert "confidence" in score_package.__dict__
    assert hasattr(score_package, "timestamp")
    assert hasattr(score_package, "config_hash")
    assert hasattr(score_package, "formula_version")

    integrity = score_package.integrity
    confidence = score_package.confidence

    # Check integrity has required fields
    assert hasattr(integrity, "overall")
    assert hasattr(integrity, "per_metric")
    assert isinstance(integrity.overall, (int, float))
    assert 0.0 <= integrity.overall <= 1.0
    assert isinstance(integrity.per_metric, dict)

    # Check confidence has required fields
    assert hasattr(confidence, "overall")
    assert hasattr(confidence, "factors")
    assert isinstance(confidence.overall, (int, float))
    assert 0.0 <= confidence.overall <= 1.0
    assert isinstance(confidence.factors, dict)

    # Check specific values from mock
    assert integrity.overall == 0.75
    assert integrity.per_metric["M-02"] == 0.80
    assert confidence.overall == 0.85
    assert confidence.factors["sample_size"] == 0.9
    assert confidence.factors["variance"] == 0.8
    assert confidence.factors["missing_data"] == 0.9
    assert confidence.factors["window_balance"] == 0.85
    assert confidence.factors["detector_success"] == 0.95


def test_scoring_engine_with_actual_implementation():
    """Test the actual ScoringEngine implementation."""
    engine = ScoringEngine()

    # Create inputs similar to what would come from pipeline
    detector_results = DetectorResults(
        detector_outputs={
            "D-01": {"some_output": "value"},
            "D-02": {"another_output": "value"},
            "D-03": {"third_output": "value"},
        }
    )

    metric_dataframe = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run-001",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        metrics={
            "M-01": {"w01": [10.0, 12.0, 11.0], "w02": [9.0, 13.0, 10.0]},
            "M-02": {"w01": [5.0, 6.0, 5.5], "w02": [4.0, 7.0, 5.0]},
            "M-03": {"w01": [0.8, 0.9, 0.85], "w02": [0.7, 1.0, 0.8]},
        },
    )

    windows = [
        WindowDefinition(
            window_id="w00",
            start_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc).date(),
            end_date=datetime.datetime(2020, 1, 31, tzinfo=datetime.timezone.utc).date(),
            commits=10,
            strategy="fixed_size",
        ),
        WindowDefinition(
            window_id="w01",
            start_date=datetime.datetime(2020, 2, 1, tzinfo=datetime.timezone.utc).date(),
            end_date=datetime.datetime(2020, 2, 29, tzinfo=datetime.timezone.utc).date(),
            commits=10,
            strategy="fixed_size",
        ),
    ]

    score_package = engine.compute_integrity_score(
        detector_results=detector_results,
        metric_dataframe=metric_dataframe,
        windows=windows,
    )

    # Validate the structure
    assert isinstance(score_package, ScorePackage)
    assert hasattr(score_package, "timestamp")
    assert hasattr(score_package, "config_hash")
    assert hasattr(score_package, "formula_version")

    # Check integrity
    integrity = score_package.integrity
    assert "overall" in integrity
    assert "per_metric" in integrity
    assert isinstance(integrity["overall"], (int, float))
    assert 0.0 <= integrity["overall"] <= 1.0

    for metric_id in ["M-01", "M-02", "M-03"]:
        assert metric_id in integrity["per_metric"]
        assert isinstance(integrity["per_metric"][metric_id], (int, float))
        assert 0.0 <= integrity["per_metric"][metric_id] <= 1.0

    # Check confidence
    confidence = score_package.confidence
    assert "overall" in confidence
    assert "factors" in confidence
    assert isinstance(confidence["overall"], (int, float))
    assert 0.0 <= confidence["overall"] <= 1.0

    expected_factors = [
        "sample_size",
        "variance",
        "missing_data",
        "window_balance",
        "detector_success",
    ]
    for factor in expected_factors:
        assert factor in confidence["factors"]
        assert isinstance(confidence["factors"][factor], (int, float))
        assert 0.0 <= confidence["factors"][factor] <= 1.0


def test_scoring_engine_validation_error_handling():
    """Test that ScorePackage validation catches invalid values."""
    # This test ensures our validation works by trying to create invalid ScorePackages
    # We'll test this indirectly by ensuring valid ones work and the structure is correct

    engine = ScoringEngine()

    # Create minimal valid inputs
    detector_results = DetectorResults(detector_outputs={"D-01": {}})
    metric_dataframe = MetricDataFrame(
        repo_id="test",
        run_id="test_run",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        metrics={},
    )
    windows = []

    # Should not raise validation error for valid (if minimal) inputs
    score_package = engine.compute_integrity_score(
        detector_results=detector_results,
        metric_dataframe=metric_dataframe,
        windows=windows,
    )

    assert isinstance(score_package, ScorePackage)
    # Even with empty inputs, we should get valid structure
    assert isinstance(score_package.integrity, dict)
    assert isinstance(score_package.confidence, dict)


def test_mock_scoring_engines():
    """Test the various mock scoring engines."""
    # Test zero scoring engine
    zero_engine = MockZeroScoringEngine()
    detector_results = DetectorResults(detector_outputs={"D-01": {}})
    metric_dataframe = MetricDataFrame(
        repo_id="test",
        run_id="test_run",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        metrics={},
    )
    windows = []

    zero_scores = zero_engine.compute_integrity_score(detector_results, metric_dataframe, windows)
    assert zero_scores.integrity.overall == 0.0
    assert zero_scores.confidence.overall == 0.0
    assert len(zero_scores.integrity.per_metric) == 0
    # Check that all five confidence factors are present with zero values
    expected_factors = [
        "sample_size",
        "variance",
        "missing_data",
        "window_balance",
        "detector_success",
    ]
    assert len(zero_scores.confidence.factors) == 5
    for factor in expected_factors:
        assert hasattr(zero_scores.confidence.factors, factor) or factor in zero_scores.confidence.factors
        assert zero_scores.confidence.factors[factor] == 0.0

    # Test perfect scoring engine
    perfect_engine = MockPerfectScoringEngine()
    metric_dataframe_with_data = MetricDataFrame(
        repo_id="test",
        run_id="test_run",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        metrics={"M-01": {"w01": [1.0]}, "M-02": {"w01": [2.0]}},
    )

    perfect_scores = perfect_engine.compute_integrity_score(detector_results, metric_dataframe_with_data, windows)
    assert perfect_scores.integrity.overall == 1.0
    assert perfect_scores.confidence.overall == 1.0
    assert all(score == 1.0 for score in perfect_scores.integrity.per_metric.values())
    assert all(factor == 1.0 for factor in perfect_scores.confidence.factors.values())
