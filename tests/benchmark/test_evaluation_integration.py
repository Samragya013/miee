"""Integration tests for EvaluationEngine."""
import pytest
from unittest.mock import Mock

from src.miie.benchmark.evaluation import EvaluationEngine
from src.miie.schemas.models import BenchmarkRun, EvaluationResult


class TestEvaluationEngineIntegration:
    """Integration test cases for EvaluationEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = EvaluationEngine()

    def test_end_to_end_evaluation_with_benchmark_runner_output(self):
        """Test end-to-end evaluation using benchmark runner output format."""
        # Create a benchmark run similar to what BenchmarkRunner would produce
        benchmark_run = Mock(spec=BenchmarkRun)
        benchmark_run.predictions = {
            "D-01": {
                "accuracy": 0.85,
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "processing_time_ms": 12.5,
                "memory_usage_mb": 150.0,
                "samples_processed": 95,
                "false_positive_rate": 0.04,
                "false_negative_rate": 0.12
            },
            "D-02": {
                "accuracy": 0.78,
                "precision": 0.72,
                "recall": 0.68,
                "f1_score": 0.70,
                "processing_time_ms": 15.2,
                "memory_usage_mb": 180.0,
                "samples_processed": 88,
                "false_positive_rate": 0.06,
                "false_negative_rate": 0.18
            },
            "suite_summary": {
                "suite_id": "B-01",
                "timestamp": "2023-06-15T12:00:00",
                "seed_used": 42,
                "detectors_benchmarked": 2,
                "execution_time_ms": 27.7,
                "config_used": {"test": True},
                "pathology_type": "metric-drift",
                "suite_candidates_count": 40
            }
        }

        # Create realistic ground truth
        ground_truth = {
            "labels": [0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1],
            "metadata": {
                "total_samples": 15,
                "anomaly_count": 6,
                "normal_count": 9
            }
        }

        # Run evaluation
        result = self.engine.evaluate(benchmark_run, ground_truth)

        # Verify result is a valid EvaluationResult
        assert isinstance(result, EvaluationResult)
        assert result.accuracy >= 0.0 and result.accuracy <= 1.0
        assert result.precision >= 0.0 and result.precision <= 1.0
        assert result.recall >= 0.0 and result.recall <= 1.0
        assert result.f1_score >= 0.0 and result.f1_score <= 1.0

        # Verify that the metrics are reasonable (not all zeros or ones unless expected)
        # Since we're using simulated predictions, we expect reasonable values
        assert isinstance(result.accuracy, float)
        assert isinstance(result.precision, float)
        assert isinstance(result.recall, float)
        assert isinstance(result.f1_score, float)

    def test_evaluation_deterministic_with_fixed_seed(self):
        """Test that evaluation produces deterministic results with fixed seed."""
        # Create identical benchmark runs
        benchmark_run1 = Mock(spec=BenchmarkRun)
        benchmark_run1.predictions = {
            "D-01": {
                "accuracy": 0.8,
                "precision": 0.7,
                "recall": 0.6,
                "f1_score": 0.64
            },
            "suite_summary": {
                "suite_id": "B-01",
                "detectors_benchmarked": 1
            }
        }

        benchmark_run2 = Mock(spec=BenchmarkRun)
        benchmark_run2.predictions = {
            "D-01": {
                "accuracy": 0.8,
                "precision": 0.7,
                "recall": 0.6,
                "f1_score": 0.64
            },
            "suite_summary": {
                "suite_id": "B-01",
                "detectors_benchmarked": 1
            }
        }

        # Identical ground truth
        ground_truth = {
            "labels": [1, 0, 1, 1, 0, 0, 1, 0, 1, 0]
        }

        # Run evaluations
        result1 = self.engine.evaluate(benchmark_run1, ground_truth)
        result2 = self.engine.evaluate(benchmark_run2, ground_truth)

        # Results should be identical due to fixed seeds in the evaluation engine
        assert result1.accuracy == result2.accuracy
        assert result1.precision == result2.precision
        assert result1.recall == result2.recall
        assert result1.f1_score == result2.f1_score

    def test_evaluation_integration_with_baseline_methods(self):
        """Test that evaluation works correctly with baseline comparison methods."""
        # Create benchmark run
        benchmark_run = Mock(spec=BenchmarkRun)
        benchmark_run.predictions = {
            "D-01": {
                "accuracy": 0.75,
                "precision": 0.70,
                "recall": 0.65,
                "f1_score": 0.67
            },
            "suite_summary": {
                "suite_id": "B-02",
                "detectors_benchmarked": 1
            }
        }

        # Ground truth with known imbalance
        ground_truth = {
            "labels": [0, 0, 0, 0, 0, 1, 1, 1, 0, 0]  # 70% zeros, 30% ones
        }

        # Get evaluation result
        result = self.engine.evaluate(benchmark_run, ground_truth)

        # Generate baseline predictions
        true_labels = ground_truth["labels"]
        random_preds = self.engine.random_baseline(true_labels)
        majority_preds = self.engine.majority_class_baseline(true_labels)
        statistical_preds = self.engine.statistical_baseline(true_labels)

        # Verify baseline methods produce expected outputs
        assert len(random_preds) == len(true_labels)
        assert len(majority_preds) == len(true_labels)
        assert len(statistical_preds) == len(true_labels)

        # Majority class should be all zeros (since zeros are majority)
        assert all(p == 0 for p in majority_preds)

        # Verify that evaluation result is sane
        assert 0.0 <= result.accuracy <= 1.0
        assert 0.0 <= result.precision <= 1.0
        assert 0.0 <= result.recall <= 1.0
        assert 0.0 <= result.f1_score <= 1.0

    def test_extended_metrics_integration(self):
        """Test integration of extended metrics evaluation."""
        # Create benchmark run
        benchmark_run = Mock(spec=BenchmarkRun)
        benchmark_run.predictions = {
            "D-01": {
                "accuracy": 0.82,
                "precision": 0.78,
                "recall": 0.75,
                "f1_score": 0.76
            },
            "suite_summary": {
                "suite_id": "B-03",
                "detectors_benchmarked": 1
            }
        }

        # Ground truth
        ground_truth = {
            "labels": [1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0]
        }

        # Get extended metrics
        extended_result = self.engine.evaluate_with_extended_metrics(
            benchmark_run, ground_truth
        )

        # Verify all expected metrics are present and valid
        expected_keys = {
            "accuracy", "precision", "recall", "f1_score",
            "auc_roc", "auc_pr", "fpr", "fnr",
            "confusion_matrix"
        }
        assert set(extended_result.keys()) == expected_keys

        # Validate ranges
        assert 0.0 <= extended_result["accuracy"] <= 1.0
        assert 0.0 <= extended_result["precision"] <= 1.0
        assert 0.0 <= extended_result["recall"] <= 1.0
        assert 0.0 <= extended_result["f1_score"] <= 1.0
        assert 0.5 <= extended_result["auc_roc"] <= 1.0
        assert 0.0 <= extended_result["auc_pr"] <= 1.0
        assert 0.0 <= extended_result["fpr"] <= 1.0
        assert 0.0 <= extended_result["fnr"] <= 1.0

        # Validate confusion matrix
        cm = extended_result["confusion_matrix"]
        assert isinstance(cm["true_negative"], int) and cm["true_negative"] >= 0
        assert isinstance(cm["false_positive"], int) and cm["false_positive"] >= 0
        assert isinstance(cm["false_negative"], int) and cm["false_negative"] >= 0
        assert isinstance(cm["true_positive"], int) and cm["true_positive"] >= 0

        # Verify that TP + TN + FP + FN equals total samples
        total_from_cm = (
            cm["true_negative"] + cm["false_positive"] +
            cm["false_negative"] + cm["true_positive"]
        )
        assert total_from_cm == len(ground_truth["labels"])

    def test_evaluation_handles_edge_cases_gracefully(self):
        """Test that evaluation handles various edge cases without crashing."""
        engine = EvaluationEngine()

        # Test with None-like inputs (empty structures)
        benchmark_run_empty = Mock(spec=BenchmarkRun)
        benchmark_run_empty.predictions = {}

        ground_truth_empty = {"labels": []}

        result = engine.evaluate(benchmark_run_empty, ground_truth_empty)
        assert isinstance(result, EvaluationResult)
        assert result.accuracy == 0.0
        assert result.precision == 0.0
        assert result.recall == 0.0
        assert result.f1_score == 0.0

        # Test with missing detector data
        benchmark_run_no_detectors = Mock(spec=BenchmarkRun)
        benchmark_run_no_detectors.predictions = {
            "suite_summary": {
                "suite_id": "B-01",
                "detectors_benchmarked": 0
            }
        }

        ground_truth_normal = {"labels": [1, 0, 1, 0]}

        result = engine.evaluate(benchmark_run_no_detectors, ground_truth_normal)
        assert isinstance(result, EvaluationResult)
        # Should handle gracefully (likely zero metrics)

    def test_evaluation_result_validation(self):
        """Test that EvaluationResult properly validates its constraints."""
        # Valid EvaluationResult should work
        valid_result = EvaluationResult(
            accuracy=0.85,
            precision=0.78,
            recall=0.72,
            f1_score=0.75
        )
        assert valid_result.accuracy == 0.85

        # Test that invalid values would raise validation errors
        # (This tests the __post_init__ validation in EvaluationResult)
        with pytest.raises(ValueError):
            EvaluationResult(accuracy=1.5, precision=0.8, recall=0.7, f1_score=0.75)  # accuracy > 1.0

        with pytest.raises(ValueError):
            EvaluationResult(accuracy=0.8, precision=-0.1, recall=0.7, f1_score=0.75)  # precision < 0.0

        with pytest.raises(ValueError):
            EvaluationResult(accuracy=0.8, precision=0.8, recall=1.5, f1_score=0.75)  # recall > 1.0

        with pytest.raises(ValueError):
            EvaluationResult(accuracy=0.8, precision=0.8, recall=0.8, f1_score=1.2)  # f1_score > 1.0


if __name__ == "__main__":
    pytest.main([__file__])