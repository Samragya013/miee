"""
Integration tests for segmentation integration.
Tests the integration between extraction and segmentation components.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from miie.orchestration.pipeline import AnalysisPipeline
from miie.processing.benchmark.engine import MockBenchmarkEngine
from miie.processing.detection.mock_detectors import MockDetectorEngine
from miie.processing.evaluation.engine import MockEvaluationEngine
from miie.processing.evidence import MockEvidenceEngine
from miie.processing.explanation.engine import MockExplanationEngine
from miie.processing.reporting.engine import MockReportGenerator
from miie.processing.scoring.mock_scoring import MockScoringEngine
from miie.processing.segmentation import MockSegmentationEngine
from tests.fixtures.mock_services import MockExtractionEngine, MockIngestionEngine


class TestSegmentationIntegration:
    """Test cases for segmentation integration."""

    def test_m02_to_m03_pipeline(self):
        """Verify M-02→M-03 pipeline chain."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            pipeline = AnalysisPipeline(
                ingestion_engine=MockIngestionEngine(),
                extraction_engine=MockExtractionEngine(),
                segmentation_engine=MockSegmentationEngine(),
                detection_engine=MockDetectorEngine(),
                scoring_engine=MockScoringEngine(),
                evidence_engine=MockEvidenceEngine(),
                explanation_engine=MockExplanationEngine(),
                report_generator=MockReportGenerator(),
                benchmark_engine=MockBenchmarkEngine(),
                evaluation_engine=MockEvaluationEngine(),
            )

            # Act
            report_output = pipeline.run_analysis(
                repo_path="/tmp/test-repo",
                metric_list=[
                    "M-02",
                    "M-06",
                ],  # Using M-02 and M-06 as in the CLI example
                output_dir=output_dir,
            )

            # Assert
            assert report_output is not None
            # Since we're using dry_run=True, we can check that output files were generated
            assert any(output_dir.iterdir()), "Output directory should not be empty in dry-run mode"

    def test_repository_context_flow(self):
        """Verify repository context flow through pipeline."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            pipeline = AnalysisPipeline(
                ingestion_engine=MockIngestionEngine(),
                extraction_engine=MockExtractionEngine(),
                segmentation_engine=MockSegmentationEngine(),
                detection_engine=MockDetectorEngine(),
                scoring_engine=MockScoringEngine(),
                evidence_engine=MockEvidenceEngine(),
                explanation_engine=MockExplanationEngine(),
                report_generator=MockReportGenerator(),
                benchmark_engine=MockBenchmarkEngine(),
                evaluation_engine=MockEvaluationEngine(),
            )

            # Act
            report_output = pipeline.run_analysis(
                repo_path="/tmp/test-repo", metric_list=["M-02"], output_dir=output_dir
            )

            # Assert
            assert report_output is not None
            # Verify that the pipeline executed without error
            assert any(output_dir.iterdir()), "Output directory should not be empty in dry-run mode"

    def test_metric_dataframe_segmentation(self):
        """Verify segmentation works with actual metric data."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Create a metric dataframe with some data
            ingestion_engine = MockIngestionEngine()
            extraction_engine = MockExtractionEngine()

            # First, we need a repository context
            context = ingestion_engine.ingest(repo_path="/tmp/test-repo")
            metric_df = extraction_engine.extract(
                context=context,
                metric_list=["M-02", "M-06"],
                since=datetime.now() - timedelta(days=30),
                until=datetime.now(),
                exclude_bots=False,
            )

            # Verify we have a valid MetricDataFrame
            assert hasattr(metric_df, "repo_id")
            assert hasattr(metric_df, "metrics")
            # MockIngestionEngine always returns "test-repo"
            assert metric_df.repo_id == "test-repo"
            assert "M-02" in metric_df.metrics
            assert "M-06" in metric_df.metrics

            # Now test segmentation
            segmentation_engine = MockSegmentationEngine()
            windows = segmentation_engine.segment(
                metric_dataframe=metric_df,
                strategy="time",
                size=7,  # week-sized windows
            )

            # Assert
            assert isinstance(windows, list)
            # MockSegmentationEngine returns 2 windows for non-custom strategies
            # (minimum for drift detection per AFD §Step 8)
            assert len(windows) == 2
            window = windows[0]
            assert hasattr(window, "window_id")
            assert hasattr(window, "start_date")
            assert hasattr(window, "end_date")
            assert window.start_date is not None
            assert window.end_date is not None
            assert window.strategy == "time"
            assert window.size_config["size"] == 7
