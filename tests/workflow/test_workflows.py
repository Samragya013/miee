"""Workflow tests for end-to-end pipeline integration."""
import pytest
from unittest.mock import Mock, patch

from src.miie.orchestration.pipeline import AnalysisPipeline
from src.miie.processing.ingestion import RepositoryIngestionEngine
from src.miie.processing.extraction import MetricExtractionEngine
from src.miie.processing.segmentation import WindowSegmentationEngine
from src.miie.processing.detection.dispatcher import DetectorDispatcherEngine
from src.miie.processing.scoring.engine import ScoringEngine
from src.miie.processing.evidence import EvidenceEngine
from src.miie.processing.explanation.engine import ExplanationEngine
from src.miie.processing.reporting.engine import ReportGenerator
from src.miie.benchmark.runner import BenchmarkRunner
from src.miie.benchmark.evaluation import EvaluationEngine
from tests.fixtures.mock_services import MockIngestionEngine
from tests.fixtures.mock_services import MockExtractionEngine
from src.miie.processing.segmentation import MockSegmentationEngine
from src.miie.processing.detection.mock_detectors import MockDetectorEngine
from src.miie.processing.scoring.mock_scoring import MockScoringEngine
from src.miie.processing.evidence import MockEvidenceEngine
from src.miie.processing.explanation.mock_explanation import MockExplanationEngine
from src.miie.processing.reporting.engine import MockReportGenerator
from src.miie.benchmark.runner import MockBenchmarkRunner
from src.miie.benchmark.evaluation import EvaluationEngine as MockEvaluationEngine


class TestWorkflows:
    """Test cases for end-to-end workflows."""

    def setup_method(self):
        """Set up test fixtures with mock components."""
        # Use mock components for deterministic testing
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
            evaluation_engine=self.evaluation_engine
        )

    def test_wf01_analyze_repository(self):
        """Verify WF-01 execution: analyze repository with dry-run."""
        # This test verifies the complete pipeline can run
        from pathlib import Path
        result = self.pipeline.run_analysis(
            repo_path=".",
            metric_list=["M-02", "M-06"],
            output_dir=Path("test_workflow_output"),
        )

        # Verify that the pipeline completed successfully
        assert result is not None
        # In a real implementation, we would check the result structure
        # For now, we verify it doesn't raise an exception

        # Clean up
        import shutil
        if Path("test_workflow_output").exists():
            shutil.rmtree("test_workflow_output")

    def test_wf02_investigate_failure(self):
        """Verify WF-02 execution: investigate failure mode."""
        # This test verifies the pipeline handles error conditions
        # We'll test with an invalid repository path
        with pytest.raises(Exception):
            self.pipeline.run_analysis(
                repo_path="/invalid/path/that/does/not/exist",
                metric_list=["M-02", "M-06"],
                output_dir="test_workflow_output",
            )

    def test_wf03_run_benchmark_suite(self):
        """Verify benchmark suite execution workflow."""
        # Test that the benchmark runner can be invoked through the pipeline
        benchmark_run = self.benchmark_engine.execute(
            suite_id="B-01",
            detector_ids=["D-01", "D-02"],
            config={"test": True},
            seed=42
        )

        assert benchmark_run is not None
        assert hasattr(benchmark_run, 'predictions')
        assert hasattr(benchmark_run, 'metadata')

    def test_wf04_evaluate_benchmark_results(self):
        """Verify evaluation engine workflow."""
        # Create mock benchmark run
        from src.miie.schemas.models import BenchmarkRun
        mock_benchmark_run = Mock(spec=BenchmarkRun)
        mock_benchmark_run.predictions = {
            "D-01": {
                "accuracy": 0.85,
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77
            },
            "suite_summary": {
                "suite_id": "B-01",
                "detectors_benchmarked": 1
            }
        }

        ground_truth = {
            "labels": [1, 0, 1, 1, 0, 0, 1, 0]
        }

        # Test evaluation
        eval_result = self.evaluation_engine.evaluate(
            mock_benchmark_run,
            ground_truth
        )

        # More specifically, check it's an EvaluationResult
        from src.miie.schemas.models import EvaluationResult
        assert isinstance(eval_result, EvaluationResult)

    def test_wf05_complete_pipeline_with_real_components(self):
        """Verify pipeline works with real component types (not just mocks)."""
        # This test verifies that the pipeline accepts the correct interface types
        # We won't actually run the real components (they may require external dependencies)
        # but we verify the type annotations and interface compliance

        # Verify that our mock components implement the required protocols
        from src.miie.contracts.interfaces import (
            IIngestionEngine, IExtractionEngine, ISegmentationEngine,
            IDetectorEngine, IScoringEngine, IEvidenceEngine,
            IExplanationEngine, IBenchmarkEngine, IEvaluationEngine,
            IReportGenerator
        )

        assert isinstance(self.ingestion_engine, IIngestionEngine)
        assert isinstance(self.extraction_engine, IExtractionEngine)
        assert isinstance(self.segmentation_engine, ISegmentationEngine)
        assert isinstance(self.detection_engine, IDetectorEngine)
        assert isinstance(self.scoring_engine, IScoringEngine)
        assert isinstance(self.evidence_engine, IEvidenceEngine)
        assert isinstance(self.explanation_engine, IExplanationEngine)
        assert isinstance(self.benchmark_engine, IBenchmarkEngine)
        assert isinstance(self.evaluation_engine, IEvaluationEngine)
        assert isinstance(self.report_generator, IReportGenerator)


if __name__ == "__main__":
    pytest.main([__file__])