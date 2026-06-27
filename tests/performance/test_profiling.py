"""Performance tests for profiling end-to-end execution time."""

import time
from unittest.mock import Mock

import pytest

from miie.benchmark.evaluation import EvaluationEngine as MockEvaluationEngine
from miie.benchmark.runner import MockBenchmarkRunner
from miie.orchestration.pipeline import AnalysisPipeline
from miie.processing.detection.mock_detectors import MockDetectorEngine
from miie.processing.evidence import MockEvidenceEngine
from miie.processing.explanation.mock_explanation import MockExplanationEngine
from miie.processing.reporting.engine import MockReportGenerator
from miie.processing.scoring.mock_scoring import MockScoringEngine
from miie.processing.segmentation import MockSegmentationEngine
from tests.fixtures.mock_services import MockExtractionEngine, MockIngestionEngine


class TestPerformanceProfiling:
    """Test cases for profiling end-to-end execution performance."""

    def setup_method(self):
        """Set up test fixtures with mock components."""
        self.ingestion_engine = MockIngestionEngine()
        self.extraction_engine = MockExtractionEngine()
        self.segmentation_engine = MockSegmentationEngine()
        self.detection_engine = MockDetectorEngine()
        self.scoring_engine = MockScoringEngine()
        self.evidence_engine = MockEvidenceEngine()
        self.explanation_engine = MockExplanationEngine()
        self.report_generator = MockReportGenerator()
        self.benchmark_engine = MockBenchmarkRunner()
        self.evaluation_engine = MockEvaluationEngine()

        self.pipeline = AnalysisPipeline(
            ingestion_engine=self.ingestion_engine,
            extraction_engine=self.extraction_engine,
            segmentation_engine=self.segmentation_engine,
            detection_engine=self.detection_engine,
            scoring_engine=self.scoring_engine,
            evidence_engine=self.evidence_engine,
            explanation_engine=self.explanation_engine,
            report_generator=self.report_generator,
            benchmark_engine=self.benchmark_engine,
            evaluation_engine=self.evaluation_engine,
        )

    def test_end_to_end_execution_time(self):
        """Profile end-to-end execution time for a single analysis run."""
        from pathlib import Path

        output_dir = Path("test_performance_output")

        # Clean up any existing output directory
        import shutil

        if output_dir.exists():
            shutil.rmtree(output_dir)

        # Measure execution time
        start_time = time.time()
        result = self.pipeline.run_analysis(
            repo_path=".",
            metric_list=["M-02", "M-06"],
            output_dir=output_dir,
        )
        end_time = time.time()

        execution_time = end_time - start_time

        # Verify the analysis completed successfully
        assert result is not None

        # Log the execution time (for informational purposes)
        # In a real performance test, we might assert that execution time is within bounds
        print(f"End-to-end execution time: {execution_time:.4f} seconds")

        # Basic sanity check: execution should take a reasonable amount of time
        # (not instant, not unreasonably slow for mock components)
        assert execution_time >= 0.0  # Time should be non-negative
        assert execution_time < 30.0  # Should complete well under 30 seconds with mocks

        # Clean up output directory
        if output_dir.exists():
            shutil.rmtree(output_dir)

    def test_multiple_sequential_runs(self):
        """Profile performance of multiple sequential analysis runs."""
        from pathlib import Path

        execution_times = []

        for i in range(3):  # Run 3 times
            output_dir = Path(f"test_performance_output_{i}")

            # Clean up any existing output directory
            import shutil

            if output_dir.exists():
                shutil.rmtree(output_dir)

            # Measure execution time for this run
            start_time = time.time()
            result = self.pipeline.run_analysis(
                repo_path=".",
                metric_list=["M-02", "M-06"],
                output_dir=output_dir,
            )
            end_time = time.time()

            execution_time = end_time - start_time
            execution_times.append(execution_time)

            # Verify the analysis completed successfully
            assert result is not None

            # Clean up output directory
            if output_dir.exists():
                shutil.rmtree(output_dir)

        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)

        print(f"Execution times: {[f'{t:.4f}' + 's' for t in execution_times]}")
        print(f"Average: {avg_time:.4f}s, Min: {min_time:.4f}s, Max: {max_time:.4f}s")

        # Performance assertions
        assert all(t >= 0.0 for t in execution_times)  # All non-negative
        assert all(t < 30.0 for t in execution_times)  # All under 30 seconds

    def test_component_isolation_performance(self):
        """Test that individual components perform adequately in isolation."""
        # Test benchmark runner performance
        start_time = time.time()
        benchmark_run = self.benchmark_engine.execute(
            suite_id="B-01",
            detector_ids=["D-01", "D-02", "D-03"],
            config={"test": True},
            seed=42,
        )
        benchmark_time = time.time() - start_time

        assert benchmark_run is not None
        print(f"Benchmark runner execution time: {benchmark_time:.4f} seconds")
        assert benchmark_time < 5.0  # Should be fast with mocks

        # Test evaluation engine performance
        from miie.schemas.models import BenchmarkRun

        mock_benchmark_run = Mock(spec=BenchmarkRun)
        mock_benchmark_run.predictions = {
            "D-01": {
                "accuracy": 0.85,
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
            },
            "suite_summary": {"suite_id": "B-01", "detectors_benchmarked": 1},
        }

        ground_truth = {"labels": [1, 0, 1, 1, 0, 0, 1, 0, 1, 0]}

        start_time = time.time()
        eval_result = self.evaluation_engine.evaluate(mock_benchmark_run, ground_truth)
        eval_time = time.time() - start_time

        assert eval_result is not None
        print(f"Evaluation engine execution time: {eval_time:.4f} seconds")
        assert eval_time < 5.0  # Should be fast with mocks


if __name__ == "__main__":
    pytest.main([__file__])
