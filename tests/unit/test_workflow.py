"""
Unit Tests for MIIE v1.0 Workflow Dispatcher
Tests workflow routing and execution.
"""

from unittest.mock import Mock

import pytest

from miie.orchestration.pipeline import AnalysisPipeline
from miie.orchestration.workflow import WorkflowDispatcher, WorkflowType
from miie.schemas.models import BenchmarkRun
from tests.fixtures.mock_services import (
    MockBenchmarkEngine,
    MockDetectorEngine,
    MockEvaluationEngine,
    MockEvidenceEngine,
    MockExplanationEngine,
    MockExtractionEngine,
    MockIngestionEngine,
    MockReportGenerator,
    MockScoringEngine,
    MockSegmentationEngine,
)


class TestWorkflowDispatcher:
    """Test the WorkflowDispatcher."""

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
            evaluation_engine=MockEvaluationEngine(),
        )

    @pytest.fixture
    def dispatcher(self, pipeline):
        """Create a workflow dispatcher."""
        return WorkflowDispatcher(pipeline)

    def test_dispatcher_initialization(self, dispatcher, pipeline):
        """Test that dispatcher initializes correctly."""
        assert dispatcher.pipeline is pipeline
        assert dispatcher.workflow_history == []

    def test_workflow_types_exist(self):
        """Test that all workflow types are defined."""
        assert WorkflowType.WF_01.value == "basic_analysis"
        assert WorkflowType.WF_02.value == "with_evidence"
        assert WorkflowType.WF_03.value == "full_analysis"
        assert WorkflowType.WF_04.value == "benchmark_only"
        assert WorkflowType.WF_05.value == "evaluation_only"

    def test_execute_wf_01_basic_analysis(self, dispatcher):
        """Test execution of WF_01 (basic analysis)."""
        # Act
        result = dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_01,
            repo_path="/tmp/test-repo",
            metric_list=["M-01", "M-02"],
        )

        # Assert
        assert result["status"] == "completed"
        assert result["workflow_type"] == "basic_analysis"
        assert "repository_context" in result
        assert "metric_dataframe" in result
        assert "windows" in result
        assert "detector_results" in result
        assert "score_package" in result
        assert "workflow_steps" in result
        assert len(result["workflow_steps"]) == 5
        assert "ingestion" in result["workflow_steps"]
        assert "scoring" in result["workflow_steps"]

    def test_execute_wf_02_with_evidence(self, dispatcher):
        """Test execution of WF_02 (with evidence)."""
        # Act
        result = dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_02,
            repo_path="/tmp/test-repo",
            metric_list=["M-01"],
        )

        # Assert
        assert result["status"] == "completed"
        assert result["workflow_type"] == "with_evidence"
        assert "evidence_package" in result
        assert "workflow_steps" in result
        assert len(result["workflow_steps"]) == 6
        assert "evidence_generation" in result["workflow_steps"]

    def test_execute_wf_03_full_analysis(self, dispatcher, tmp_path):
        """Test execution of WF_03 (full analysis)."""
        # Arrange
        output_dir = tmp_path / "output"

        # Act
        result = dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_03,
            repo_path="/tmp/test-repo",
            metric_list=["M-01", "M-02"],
            output_dir=output_dir,
        )

        # Assert
        assert result["status"] == "completed"
        assert result["workflow_type"] == "full_analysis"
        assert "explanation_report" in result
        assert "report_output" in result
        assert "workflow_steps" in result
        assert len(result["workflow_steps"]) == 8
        assert "explanation_generation" in result["workflow_steps"]
        assert "report_generation" in result["workflow_steps"]

    def test_execute_wf_04_benchmark_only(self, dispatcher):
        """Test execution of WF_04 (benchmark only)."""
        # Act
        result = dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_04,
            suite_id="test-suite",
            detector_ids=["D-01", "D-02"],
            config={"threshold": 0.05},
        )

        # Assert
        assert result["status"] == "completed"
        assert result["workflow_type"] == "benchmark_only"
        assert "benchmark_run" in result
        assert "workflow_steps" in result
        assert result["workflow_steps"] == ["benchmark_execution"]

    def test_execute_wf_05_evaluation_only(self, dispatcher):
        """Test execution of WF_05 (evaluation only)."""
        # Arrange
        benchmark_run = BenchmarkRun(predictions={"D-01": [0.8, 0.75, 0.82]}, metadata={})
        ground_truth = {"D-01": [0.78, 0.76, 0.80]}

        # Act
        result = dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_05,
            benchmark_run=benchmark_run,
            ground_truth=ground_truth,
        )

        # Assert
        assert result["status"] == "completed"
        assert result["workflow_type"] == "evaluation_only"
        assert "evaluation_result" in result
        assert "workflow_steps" in result
        assert result["workflow_steps"] == ["benchmark_evaluation"]

    def test_workflow_history_tracking(self, dispatcher):
        """Test that workflow execution history is tracked."""
        # Act
        dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_01,
            repo_path="/tmp/test-repo",
            metric_list=["M-01"],
        )
        dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_03,
            repo_path="/tmp/test-repo",
            metric_list=["M-02"],
        )

        # Assert
        history = dispatcher.get_workflow_history()
        assert len(history) == 2
        assert history[0]["workflow_type"] == "basic_analysis"
        assert history[1]["workflow_type"] == "full_analysis"
        assert history[0]["status"] == "completed"
        assert history[1]["status"] == "completed"

    def test_clear_workflow_history(self, dispatcher):
        """Test clearing workflow history."""
        # Arrange
        dispatcher.execute_workflow(
            workflow_type=WorkflowType.WF_01,
            repo_path="/tmp/test-repo",
            metric_list=["M-01"],
        )
        assert len(dispatcher.get_workflow_history()) == 1

        # Act
        dispatcher.clear_workflow_history()

        # Assert
        assert len(dispatcher.get_workflow_history()) == 0

    def test_invalid_workflow_type(self, dispatcher):
        """Test executing an invalid workflow type."""
        # Act & Assert
        with pytest.raises(ValueError, match="Unknown workflow type"):
            dispatcher.execute_workflow(
                workflow_type="INVALID_WORKFLOW",  # Not a WorkflowType enum
                repo_path="/tmp/test-repo",
                metric_list=["M-01"],
            )

    def test_workflow_error_handling(self, dispatcher):
        """Test that workflow errors are properly handled and recorded."""
        # Arrange - Create a dispatcher with a pipeline that will fail
        failing_pipeline = AnalysisPipeline(
            ingestion_engine=MockIngestionEngine(),
            extraction_engine=MockExtractionEngine(),
            segmentation_engine=MockSegmentationEngine(),
            detection_engine=Mock(fail_on_invoke=True),  # This will cause an error
            scoring_engine=MockScoringEngine(),
            evidence_engine=MockEvidenceEngine(),
            explanation_engine=MockExplanationEngine(),
            report_generator=MockReportGenerator(),
        )
        dispatcher = WorkflowDispatcher(failing_pipeline)

        # Act & Assert
        with pytest.raises(Exception):
            dispatcher.execute_workflow(
                workflow_type=WorkflowType.WF_01,
                repo_path="/tmp/test-repo",
                metric_list=["M-01"],
            )

        # Check that error was recorded in history
        history = dispatcher.get_workflow_history()
        assert len(history) == 1
        assert history[0]["status"] == "failed"
        assert "error" in history[0]


if __name__ == "__main__":
    pytest.main([__file__])
