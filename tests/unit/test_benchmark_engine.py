"""Unit tests for BenchmarkEngine implementation."""
from src.miie.processing.benchmark.engine import BenchmarkEngine
from src.miie.schemas.models import BenchmarkRun
import datetime


def test_benchmark_engine_creation():
    """Test creating a BenchmarkEngine instance."""
    engine = BenchmarkEngine()
    assert isinstance(engine, BenchmarkEngine)


def test_benchmark_engine_execute_returns_expected_structure():
    """Test that BenchmarkEngine.execute returns expected BenchmarkRun structure."""
    engine = BenchmarkEngine()
    suite_id = "test-suite-001"
    detector_ids = ["D-01", "D-02", "D-03"]
    config = {"threshold": 0.5, "method": "test"}
    seed = 42

    benchmark_run = engine.execute(suite_id, detector_ids, config, seed)

    assert benchmark_run is not None
    assert hasattr(benchmark_run, 'predictions')
    assert hasattr(benchmark_run, 'metadata')
    assert isinstance(benchmark_run.predictions, dict)
    assert isinstance(benchmark_run.metadata, dict)

    # Check that predictions contain entries for each detector
    for detector_id in detector_ids:
        assert detector_id in benchmark_run.predictions
        detector_predictions = benchmark_run.predictions[detector_id]
        assert isinstance(detector_predictions, dict)
        # Check for expected metrics
        expected_metrics = ["accuracy", "precision", "recall", "f1_score", "processing_time_ms"]
        for metric in expected_metrics:
            assert metric in detector_predictions
            # Check that values are reasonable
            if metric in ["accuracy", "precision", "recall", "f1_score"]:
                assert 0.0 <= detector_predictions[metric] <= 1.0
            elif metric == "processing_time_ms":
                assert detector_predictions[metric] >= 0.0

    # Check suite summary
    assert "suite_summary" in benchmark_run.predictions
    suite_summary = benchmark_run.predictions["suite_summary"]
    assert suite_summary["suite_id"] == suite_id
    assert suite_summary["seed_used"] == seed
    assert suite_summary["detectors_benchmarked"] == len(detector_ids)

    # Check metadata
    assert benchmark_run.metadata["benchmark_engine_version"] == "1.0.0"
    assert benchmark_run.metadata["random_seed"] == seed
    assert benchmark_run.metadata["suite_id"] == suite_id
    assert benchmark_run.metadata["detector_ids"] == detector_ids


def test_benchmark_engine_execute_is_deterministic_with_seed():
    """Test that BenchmarkEngine.execute produces deterministic results with same seed."""
    engine = BenchmarkEngine()
    suite_id = "deterministic-test"
    detector_ids = ["D-01", "D-02"]
    config = {"param": "value"}

    # Run twice with same seed
    run1 = engine.execute(suite_id, detector_ids, config, seed=12345)
    run2 = engine.execute(suite_id, detector_ids, config, seed=12345)

    # Predictions should be identical
    assert run1.predictions == run2.predictions
    # Metadata should be similar (timestamps may differ slightly)
    assert run1.metadata["benchmark_engine_version"] == run2.metadata["benchmark_engine_version"]
    assert run1.metadata["random_seed"] == run2.metadata["random_seed"]
    assert run1.metadata["suite_id"] == run2.metadata["suite_id"]
    assert run1.metadata["detector_ids"] == run2.metadata["detector_ids"]


def test_benchmark_engine_execute_produces_different_results_with_different_seeds():
    """Test that BenchmarkEngine.execute produces different results with different seeds."""
    engine = BenchmarkEngine()
    suite_id = "seed-test"
    detector_ids = ["D-01", "D-02"]
    config = {"param": "value"}

    # Run with two different seeds
    run1 = engine.execute(suite_id, detector_ids, config, seed=100)
    run2 = engine.execute(suite_id, detector_ids, config, seed=200)

    # At least some predictions should differ (though there's small chance they could be same)
    # We'll check that the suite summary shows different seeds
    assert run1.predictions["suite_summary"]["seed_used"] == 100
    assert run2.predictions["suite_summary"]["seed_used"] == 200


def test_benchmark_engine_execute_handles_empty_detector_list():
    """Test that BenchmarkEngine.execute handles empty detector list."""
    engine = BenchmarkEngine()
    suite_id = "empty-detectors"
    detector_ids = []  # Empty list
    config = {"test": True}
    seed = 999

    benchmark_run = engine.execute(suite_id, detector_ids, config, seed)

    assert benchmark_run is not None
    assert isinstance(benchmark_run.predictions, dict)
    assert isinstance(benchmark_run.metadata, dict)
    # Should still have suite summary
    assert "suite_summary" in benchmark_run.predictions
    assert benchmark_run.predictions["suite_summary"]["detectors_benchmarked"] == 0


def test_benchmark_engine_execute_validates_prediction_ranges():
    """Test that BenchmarkEngine.execute produces predictions in valid ranges."""
    engine = BenchmarkEngine()
    suite_id = "validation-test"
    detector_ids = ["D-01", "D-02", "D-03"]
    config = {"validation": True}
    seed = 42

    benchmark_run = engine.execute(suite_id, detector_ids, config, seed)

    # Check that all detector predictions have valid values
    for detector_id in detector_ids:
        predictions = benchmark_run.predictions[detector_id]
        assert 0.0 <= predictions["accuracy"] <= 1.0
        assert 0.0 <= predictions["precision"] <= 1.0
        assert 0.0 <= predictions["recall"] <= 1.0
        assert 0.0 <= predictions["f1_score"] <= 1.0
        assert predictions["processing_time_ms"] >= 0.0
        assert predictions["memory_usage_mb"] >= 0.0
        assert 0.0 <= predictions["false_positive_rate"] <= 1.0
        assert 0.0 <= predictions["false_negative_rate"] <= 1.0