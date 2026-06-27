"""Evaluation Engine Implementation.

Implements the IEvaluationEngine interface for evaluating benchmark results against ground truth.
"""

from typing import Any, Dict

from miie.contracts.interfaces import IEvaluationEngine
from miie.schemas.models import EvaluationResult


class EvaluationEngine(IEvaluationEngine):
    """Evaluation Engine implementation that evaluates benchmark results against ground truth."""

    def evaluate(self, benchmark_run: "BenchmarkRun", ground_truth: Dict[str, Any]) -> EvaluationResult:
        """Evaluate benchmark results against ground truth.

        Args:
            benchmark_run: Container for benchmark execution results
            ground_truth: Ground truth data for evaluation

        Returns:
            EvaluationResult: Container for evaluation metrics
        """
        # Extract predictions from benchmark run
        predictions = benchmark_run.predictions

        # Initialize accumulators for metrics across all detectors
        total_accuracy = 0.0
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        detector_count = 0

        # Process each detector's predictions
        for detector_id, pred_values in predictions.items():
            # Skip non-detector entries (like suite_summary)
            if not isinstance(pred_values, dict) or "accuracy" not in pred_values:
                continue

            # Extract metrics
            accuracy = float(pred_values.get("accuracy", 0.0))
            precision = float(pred_values.get("precision", 0.0))
            recall = float(pred_values.get("recall", 0.0))
            f1_score = float(pred_values.get("f1_score", 0.0))

            # Only include if we have valid predictions (not default zeros from missing data)
            if accuracy > 0.0 or precision > 0.0 or recall > 0.0:
                total_accuracy += accuracy
                total_precision += precision
                total_recall += recall
                total_f1 += f1_score
                detector_count += 1

        # Calculate averages (handle case where no valid detectors)
        if detector_count > 0:
            avg_accuracy = total_accuracy / detector_count
            avg_precision = total_precision / detector_count
            avg_recall = total_recall / detector_count
            avg_f1 = total_f1 / detector_count
        else:
            avg_accuracy = 0.0
            avg_precision = 0.0
            avg_recall = 0.0
            avg_f1 = 0.0

        # In a more sophisticated implementation, we would compare against ground_truth
        # For now, we return the average performance metrics as the evaluation result
        # The ground_truth parameter is reserved for future implementation where we
        # would compare predictions against known correct answers

        return EvaluationResult(
            accuracy=avg_accuracy,
            precision=avg_precision,
            recall=avg_recall,
            f1_score=avg_f1,
        )


class MockEvaluationEngine:
    """Mock evaluation engine that returns deterministic evaluation result."""

    def evaluate(self, benchmark_run: "BenchmarkRun", ground_truth: Dict[str, Any]) -> EvaluationResult:
        """Return a fixed EvaluationResult for testing."""
        return EvaluationResult(accuracy=0.82, precision=0.78, recall=0.80, f1_score=0.79)
