"""
Integration Tests for MIIE v1.0 Pipeline Skeleton
Tests the orchestration pipeline with mock implementations.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from miie.orchestration.pipeline import AnalysisPipeline
from tests.fixtures.mock_services import (
    MockIngestionEngine,
    MockExtractionEngine,
    MockSegmentationEngine,
    MockDetectorEngine,
    MockScoringEngine,
    MockEvidenceEngine,
    MockExplanationEngine,
    MockReportGenerator,
    MockBenchmarkEngine,
    MockEvaluationEngine
)
from miie.schemas.models import BenchmarkRun


class TestAnalysisPipeline:
    """Test the AnalysisPipeline orchestrator."""

    @pytest.fixture
    def pipeline(self):
        """Create a pipeline with mock engines."""
        return AnalysisPipeline(
            ingestion_engine=MockIngestionEngine(),
            extraction_engine=MockExtractionEngine(),
            segmentation_engine=MockSegmentationEngine(),
            detection_engine=MockDetectorEngine(),
            scoring_engine=MockScoringEngine(),
            evidence_engine=MockEvidenceEngine(),
            explanation_engine=MockExplanationEngine(),
            report_generator=MockReportGenerator(),
            benchmark_engine=MockBenchmarkEngine(),
            evaluation_engine=MockEvaluationEngine()
        )

    def test_pipeline_initialization(self, pipeline):
        """Test that pipeline initializes with all engines."""
        assert pipeline.ingestion_engine is not None
        assert pipeline.extraction_engine is not None
        assert pipeline.segmentation_engine is not None
        assert pipeline.detection_engine is not None
        assert pipeline.scoring_engine is not None
        assert pipeline.evidence_engine is not None
        assert pipeline.explanation_engine is not None
        assert pipeline.report_generator is not None
        assert pipeline.benchmark_engine is not None
        assert pipeline.evaluation_engine is not None

    def test_run_analysis_success(self, pipeline, tmp_path):
        """Test successful execution of the full analysis pipeline."""
        # Arrange
        repo_path = "/tmp/test-repo"
        metric_list = ["M-01", "M-02", "M-03"]
        output_dir = tmp_path / "output"

        # Act
        result = pipeline.run_analysis(
            repo_path=repo_path,
            metric_list=metric_list,
            output_dir=output_dir
        )

        # Assert
        assert result is not None
        assert "repository_context" in result
        assert "metric_dataframe" in result
        assert "windows" in result
        assert "detector_results" in result
        assert "score_package" in result
        assert "evidence_package" in result
        assert "explanation_report" in result
        assert "report_output" in result

        # Verify mocks were called
        assert pipeline.ingestion_engine.ingest_called
        assert pipeline.ingestion_engine.validate_called
        assert pipeline.extraction_engine.extract_called
        assert pipeline.segmentation_engine.segment_called
        assert pipeline.detection_engine.invoke_called
        assert pipeline.scoring_engine.compute_integrity_score_called
        assert pipeline.evidence_engine.generate_called
        assert pipeline.explanation_engine.generate_called
        assert pipeline.report_generator.generate_called

        # Verify output files were created
        assert output_dir.exists()
        assert (output_dir / "analysis_report.json").exists()
        assert (output_dir / "analysis_report.md").exists()

    def test_run_analysis_with_different_params(self, pipeline, tmp_path):
        """Test pipeline with different configuration parameters."""
        # Arrange
        repo_path = "/tmp/test-repo-2"
        metric_list = ["M-06"]
        output_dir = tmp_path / "output2"
        since = datetime.now() - timedelta(days=7)
        until = datetime.now()

        # Act
        result = pipeline.run_analysis(
            repo_path=repo_path,
            metric_list=metric_list,
            since=since,
            until=until,
            exclude_bots=True,
            segmentation_strategy="commit",
            segmentation_size=5,
            output_dir=output_dir
        )

        # Assert
        assert result is not None
        assert result["repository_context"].repo_id == "test-repo"
        assert len(result["metric_dataframe"].metrics) == 1
        assert "M-06" in result["metric_dataframe"].metrics

    def test_run_benchmark_success(self, pipeline):
        """Test benchmark execution."""
        # Arrange
        suite_id = "suite-001"
        detector_ids = ["D-01", "D-02"]
        config = {"threshold": 0.05}

        # Act
        benchmark_run = pipeline.run_benchmark(
            suite_id=suite_id,
            detector_ids=detector_ids,
            config=config
        )

        # Assert
        assert benchmark_run is not None
        assert benchmark_run.metadata["suite_id"] == suite_id
        assert benchmark_run.metadata["detector_ids"] == detector_ids
        assert benchmark_run.metadata["seed"] == 42
        assert pipeline.benchmark_engine.execute_called

    def test_evaluate_benchmark_success(self, pipeline):
        """Test benchmark evaluation."""
        # Arrange
        benchmark_run = BenchmarkRun(
            predictions={"D-01": [0.8, 0.75, 0.82]},
            metadata={}
        )
        ground_truth = {"D-01": [0.78, 0.76, 0.80]}

        # Act
        evaluation_result = pipeline.evaluate_benchmark(
            benchmark_run=benchmark_run,
            ground_truth=ground_truth
        )

        # Assert
        assert evaluation_result is not None
        assert evaluation_result.accuracy == 0.92
        assert pipeline.evaluation_engine.evaluate_called

    def test_pipeline_without_optional_engines(self):
        """Test pipeline works without benchmark and evaluation engines."""
        # Arrange
        pipeline = AnalysisPipeline(
            ingestion_engine=MockIngestionEngine(),
            extraction_engine=MockExtractionEngine(),
            segmentation_engine=MockSegmentationEngine(),
            detection_engine=MockDetectorEngine(),
            scoring_engine=MockScoringEngine(),
            evidence_engine=MockEvidenceEngine(),
            explanation_engine=MockExplanationEngine(),
            report_generator=MockReportGenerator()
            # No benchmark_engine or evaluation_engine
        )

        # Act & Assert - Should not raise initialization error
        assert pipeline.benchmark_engine is None
        assert pipeline.evaluation_engine is None

        # Should still be able to run analysis
        result = pipeline.run_analysis(
            repo_path="/tmp/test",
            metric_list=["M-01"],
            output_dir=Path("./tmp_output")
        )
        assert result is not None

        # But benchmark/evaluation methods should fail
        with pytest.raises(RuntimeError, match="Benchmark engine not available"):
            pipeline.run_benchmark("suite", ["D-01"], {})

        with pytest.raises(RuntimeError, match="Evaluation engine not available"):
            pipeline.evaluate_benchmark(
                BenchmarkRun(
                    predictions={},
                    metadata={}
                ),
                {}
            )


if __name__ == "__main__":
    pytest.main([__file__])