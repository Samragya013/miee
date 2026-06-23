"""Unit tests for EvaluationEngine implementation."""
from miie.processing.evaluation.engine import EvaluationEngine
from miie.processing.benchmark.engine import BenchmarkEngine
from miie.schemas.models import EvaluationResult, BenchmarkRun
import datetime


def test_evaluation_engine_creation():
    """Test creating an EvaluationEngine instance."""
    engine = EvaluationEngine()
    assert isinstance(engine, EvaluationEngine)


def test_evaluation_engine_evaluate_returns_expected_structure():
    """Test that EvaluationEngine.evaluate returns expected EvaluationResult structure."""
    engine = EvaluationEngine()

    # Create a mock benchmark run
    benchmark_engine = BenchmarkEngine()
    benchmark_run = benchmark_engine.execute(
        suite_id="test-suite",
        detector_ids=["D-01", "D-02"],
        config={"test": True},
        seed=42
    )

    ground_truth = {"example": "data"}

    evaluation_result = engine.evaluate(benchmark_run, ground_truth)

    assert evaluation_result is not None
    assert isinstance(evaluation_result, EvaluationResult)
    # Check that all fields are present and are floats
    assert hasattr(evaluation_result, 'accuracy')
    assert hasattr(evaluation_result, 'precision')
    assert hasattr(evaluation_result, 'recall')
    assert hasattr(evaluation_result, 'f1_score')
    assert isinstance(evaluation_result.accuracy, float)
    assert isinstance(evaluation_result.precision, float)
    assert isinstance(evaluation_result.recall, float)
    assert isinstance(evaluation_result.f1_score, float)
    # Check that values are in valid range [0.0, 1.0]
    assert 0.0 <= evaluation_result.accuracy <= 1.0
    assert 0.0 <= evaluation_result.precision <= 1.0
    assert 0.0 <= evaluation_result.recall <= 1.0
    assert 0.0 <= evaluation_result.f1_score <= 1.0


def test_evaluation_engine_evaluate_handles_empty_benchmark_run():
    """Test that EvaluationEngine.evaluate handles benchmark runs with no valid detectors."""
    engine = EvaluationEngine()

    # Create a benchmark run with no valid detector predictions
    benchmark_run = BenchmarkRun(
        predictions={
            "suite_summary": {
                "suite_id": "test",
                "seed_used": 42
            }
        },
        metadata={
            "test": "metadata"
        }
    )

    ground_truth = {}

    evaluation_result = engine.evaluate(benchmark_run, ground_truth)

    assert evaluation_result is not None
    assert isinstance(evaluation_result, EvaluationResult)
    # Should return zero scores when no valid detectors
    assert evaluation_result.accuracy == 0.0
    assert evaluation_result.precision == 0.0
    assert evaluation_result.recall == 0.0
    assert evaluation_result.f1_score == 0.0


def test_evaluation_engine_evaluate_calculates_correct_averages():
    """Test that EvaluationEngine.evaluate correctly averages metrics across detectors."""
    engine = EvaluationEngine()

    # Create a mock benchmark run with known values
    benchmark_run = BenchmarkRun(
        predictions={
            "D-01": {
                "accuracy": 0.8,
                "precision": 0.75,
                "recall": 0.85,
                "f1_score": 0.79
            },
            "D-02": {
                "accuracy": 0.9,
                "precision": 0.85,
                "recall": 0.9,
                "f1_score": 0.87
            },
            "D-03": {
                "accuracy": 0.7,
                "precision": 0.65,
                "recall": 0.75,
                "f1_score": 0.70
            },
            "suite_summary": {
                "suite_id": "test",
                "seed_used": 42
            }
        },
        metadata={}
    )

    ground_truth = {}

    evaluation_result = engine.evaluate(benchmark_run, ground_truth)

    # Expected averages:
    # accuracy: (0.8 + 0.9 + 0.7) / 3 = 0.8
    # precision: (0.75 + 0.85 + 0.65) / 3 = 0.75
    # recall: (0.85 + 0.9 + 0.75) / 3 = 0.8333...
    # f1_score: (0.79 + 0.87 + 0.70) / 3 = 0.7866...
    assert abs(evaluation_result.accuracy - 0.8) < 0.001
    assert abs(evaluation_result.precision - 0.75) < 0.001
    assert abs(evaluation_result.recall - 0.8333) < 0.001
    assert abs(evaluation_result.f1_score - 0.7867) < 0.001


def test_evaluation_engine_evaluate_ignores_non_detector_predictions():
    """Test that EvaluationEngine.evaluate ignores non-detector entries in predictions."""
    engine = EvaluationEngine()

    # Create a benchmark run with mixed prediction types
    benchmark_run = BenchmarkRun(
        predictions={
            "D-01": {
                "accuracy": 0.8,
                "precision": 0.7,
                "recall": 0.9,
                "f1_score": 0.79
            },
            "suite_summary": {
                "suite_id": "test",
                "timestamp": "2026-01-01"
            },
            "config_info": {
                "method": "test"
            }
        },
        metadata={}
    )

    ground_truth = {}

    evaluation_result = engine.evaluate(benchmark_run, ground_truth)

    # Should only consider D-01 for averaging
    assert evaluation_result.accuracy == 0.8
    assert evaluation_result.precision == 0.7
    assert evaluation_result.recall == 0.9
    assert evaluation_result.f1_score == 0.79


def test_evaluation_engine_evaluate_respects_ground_truth_parameter():
    """Test that EvaluationEngine.evaluate accepts ground_truth parameter (even if not used yet)."""
    engine = EvaluationEngine()

    # Create a benchmark run
    benchmark_engine = BenchmarkEngine()
    benchmark_run = benchmark_engine.execute(
        suite_id="test-suite",
        detector_ids=["D-01"],
        config={"test": True},
        seed=42
    )

    # Test with different ground truth values
    ground_truth1 = {"key": "value1"}
    ground_truth2 = {"different": "structure"}
    ground_truth3 = []

    # All should work without errors
    result1 = engine.evaluate(benchmark_run, ground_truth1)
    result2 = engine.evaluate(benchmark_run, ground_truth2)
    result3 = engine.evaluate(benchmark_run, ground_truth3)

    # All should return valid EvaluationResult objects
    assert isinstance(result1, EvaluationResult)
    assert isinstance(result2, EvaluationResult)
    assert isinstance(result3, EvaluationResult)