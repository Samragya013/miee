"""
Integration Tests for MIIE v1.0 Pipeline with Real Ingestion Engine
Tests the orchestration pipeline with real RepositoryIngestionEngine and mock implementations for other engines.
"""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from miie.contracts.errors import IngestionError
from miie.orchestration.pipeline import AnalysisPipeline
from miie.processing.ingestion import RepositoryIngestionEngine
from miie.schemas.models import BenchmarkRun
from tests.fixtures.mock_services import (
    MockBenchmarkEngine,
    MockDetectorEngine,
    MockEvaluationEngine,
    MockEvidenceEngine,
    MockExplanationEngine,
    MockExtractionEngine,
    MockReportGenerator,
    MockScoringEngine,
    MockSegmentationEngine,
)


class TestAnalysisPipelineWithRealIngestion:
    """Test the AnalysisPipeline orchestrator with real ingestion engine."""

    @pytest.fixture
    def real_ingestion_engine(self):
        """Create a real RepositoryIngestionEngine."""
        return RepositoryIngestionEngine()

    @pytest.fixture
    def mock_engines(self):
        """Create mock engines for all other components."""
        return {
            "extraction": MockExtractionEngine(),
            "segmentation": MockSegmentationEngine(),
            "detection": MockDetectorEngine(),
            "scoring": MockScoringEngine(),
            "evidence": MockEvidenceEngine(),
            "explanation": MockExplanationEngine(),
            "report_generator": MockReportGenerator(),
            "benchmark": MockBenchmarkEngine(),
            "evaluation": MockEvaluationEngine(),
        }

    @pytest.fixture
    def sample_repo(self, tmp_path):
        """Create a sample Git repository for testing with at least 10 commits."""
        repo_path = tmp_path / "sample-repo"
        repo_path.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
        )

        # Add initial commit
        (repo_path / "README.md").write_text("# Test Repository\n")
        subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

        # Add 9 more commits to have at least 10 total
        for i in range(9):
            (repo_path / f"file{i}.txt").write_text(f"Content {i}\n")
            subprocess.run(["git", "add", f"file{i}.txt"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", f"Add file {i}"], cwd=repo_path, check=True)

        return str(repo_path)

    def test_pipeline_initialization_with_real_ingestion(self, real_ingestion_engine, mock_engines):
        """Test that pipeline initializes with real ingestion engine and mock others."""
        pipeline = AnalysisPipeline(
            ingestion_engine=real_ingestion_engine,
            extraction_engine=mock_engines["extraction"],
            segmentation_engine=mock_engines["segmentation"],
            detection_engine=mock_engines["detection"],
            scoring_engine=mock_engines["scoring"],
            evidence_engine=mock_engines["evidence"],
            explanation_engine=mock_engines["explanation"],
            report_generator=mock_engines["report_generator"],
            benchmark_engine=mock_engines["benchmark"],
            evaluation_engine=mock_engines["evaluation"],
        )

        assert pipeline.ingestion_engine is not None
        assert isinstance(pipeline.ingestion_engine, RepositoryIngestionEngine)
        assert pipeline.extraction_engine is not None
        assert pipeline.segmentation_engine is not None
        assert pipeline.detection_engine is not None
        assert pipeline.scoring_engine is not None
        assert pipeline.evidence_engine is not None
        assert pipeline.explanation_engine is not None
        assert pipeline.report_generator is not None
        assert pipeline.benchmark_engine is not None
        assert pipeline.evaluation_engine is not None

    def test_run_analysis_success_with_real_ingestion(self, real_ingestion_engine, mock_engines, sample_repo):
        """Test successful execution of the full analysis pipeline with real ingestion."""
        # Arrange
        pipeline = AnalysisPipeline(
            ingestion_engine=real_ingestion_engine,
            extraction_engine=mock_engines["extraction"],
            segmentation_engine=mock_engines["segmentation"],
            detection_engine=mock_engines["detection"],
            scoring_engine=mock_engines["scoring"],
            evidence_engine=mock_engines["evidence"],
            explanation_engine=mock_engines["explanation"],
            report_generator=mock_engines["report_generator"],
        )

        repo_path = sample_repo
        metric_list = ["M-01", "M-02", "M-03"]
        output_dir = Path("./tmp_output_ingestion")

        # Act
        result = pipeline.run_analysis(repo_path=repo_path, metric_list=metric_list, output_dir=output_dir)

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

        # Verify that the real ingestion engine was used (we can check by the type of repository_context)
        assert result["repository_context"].repo_id is not None
        assert len(result["repository_context"].repo_id) == 64  # SHA256 hex digest length
        assert result["repository_context"].local_path == Path(repo_path).resolve()
        assert result["repository_context"].total_commits == 10  # We made 10 commits

        # Verify mocks were called
        assert mock_engines["extraction"].extract_called
        assert mock_engines["segmentation"].segment_called
        assert mock_engines["detection"].invoke_called
        assert mock_engines["scoring"].compute_integrity_score_called
        assert mock_engines["evidence"].generate_called
        assert mock_engines["explanation"].generate_called
        assert mock_engines["report_generator"].generate_called

        # Verify output files were created
        assert output_dir.exists()
        assert (output_dir / "analysis_report.json").exists()
        assert (output_dir / "analysis_report.md").exists()

    def test_run_analysis_with_different_params(self, real_ingestion_engine, mock_engines, sample_repo):
        """Test pipeline with different configuration parameters."""
        # Arrange
        pipeline = AnalysisPipeline(
            ingestion_engine=real_ingestion_engine,
            extraction_engine=mock_engines["extraction"],
            segmentation_engine=mock_engines["segmentation"],
            detection_engine=mock_engines["detection"],
            scoring_engine=mock_engines["scoring"],
            evidence_engine=mock_engines["evidence"],
            explanation_engine=mock_engines["explanation"],
            report_generator=mock_engines["report_generator"],
        )

        repo_path = sample_repo
        metric_list = ["M-06"]
        output_dir = Path("./tmp_output_ingestion2")
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()

        # Act
        result = pipeline.run_analysis(
            repo_path=repo_path,
            metric_list=metric_list,
            since=since,
            until=until,
            exclude_bots=True,
            segmentation_strategy="commit",
            segmentation_size=1,
            output_dir=output_dir,
        )

        # Assert
        assert result is not None
        assert result["repository_context"].repo_id is not None
        # Note: The mock extraction engine doesn't actually use the parameters,
        # but we can still check that the pipeline accepted them and produced results
        assert len(result["metric_dataframe"].metrics) == 1
        assert "M-06" in result["metric_dataframe"].metrics

    def test_run_benchmark_success(self, real_ingestion_engine, mock_engines):
        """Test benchmark execution with real ingestion engine (though benchmark doesn't use ingestion)."""
        # Arrange
        pipeline = AnalysisPipeline(
            ingestion_engine=real_ingestion_engine,
            extraction_engine=mock_engines["extraction"],
            segmentation_engine=mock_engines["segmentation"],
            detection_engine=mock_engines["detection"],
            scoring_engine=mock_engines["scoring"],
            evidence_engine=mock_engines["evidence"],
            explanation_engine=mock_engines["explanation"],
            report_generator=mock_engines["report_generator"],
            benchmark_engine=mock_engines["benchmark"],
            evaluation_engine=mock_engines["evaluation"],
        )

        suite_id = "suite-001"
        detector_ids = ["D-01", "D-02"]
        config = {"threshold": 0.05}

        # Act
        benchmark_run = pipeline.run_benchmark(suite_id=suite_id, detector_ids=detector_ids, config=config)

        # Assert
        assert benchmark_run is not None
        assert benchmark_run.metadata["suite_id"] == suite_id
        assert benchmark_run.metadata["detector_ids"] == detector_ids
        assert benchmark_run.metadata["seed"] == 42
        assert mock_engines["benchmark"].execute_called

    def test_evaluate_benchmark_success(self, real_ingestion_engine, mock_engines):
        """Test benchmark evaluation."""
        # Arrange
        pipeline = AnalysisPipeline(
            ingestion_engine=real_ingestion_engine,
            extraction_engine=mock_engines["extraction"],
            segmentation_engine=mock_engines["segmentation"],
            detection_engine=mock_engines["detection"],
            scoring_engine=mock_engines["scoring"],
            evidence_engine=mock_engines["evidence"],
            explanation_engine=mock_engines["explanation"],
            report_generator=mock_engines["report_generator"],
            benchmark_engine=mock_engines["benchmark"],
            evaluation_engine=mock_engines["evaluation"],
        )

        benchmark_run = BenchmarkRun(predictions={"D-01": [0.8, 0.75, 0.82]}, metadata={})
        ground_truth = {"D-01": [0.78, 0.76, 0.80]}

        # Act
        evaluation_result = pipeline.evaluate_benchmark(benchmark_run=benchmark_run, ground_truth=ground_truth)

        # Assert
        assert evaluation_result is not None
        assert evaluation_result.accuracy == 0.92
        assert mock_engines["evaluation"].evaluate_called

    def test_pipeline_without_optional_engines(self, real_ingestion_engine, mock_engines):
        """Test pipeline works without benchmark and evaluation engines."""
        # Arrange
        pipeline = AnalysisPipeline(
            ingestion_engine=real_ingestion_engine,
            extraction_engine=mock_engines["extraction"],
            segmentation_engine=mock_engines["segmentation"],
            detection_engine=mock_engines["detection"],
            scoring_engine=mock_engines["scoring"],
            evidence_engine=mock_engines["evidence"],
            explanation_engine=mock_engines["explanation"],
            report_generator=mock_engines["report_generator"],
            # No benchmark_engine or evaluation_engine
        )

        # Act & Assert - Should not raise initialization error
        assert pipeline.benchmark_engine is None
        assert pipeline.evaluation_engine is None

        # Should still be able to run analysis
        # We need a sample repo for this test with at least 10 commits
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            repo_path.mkdir()
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                check=True,
            )
            # Add initial commit
            (repo_path / "README.md").write_text("# Test\n")
            subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
            # Add 9 more commits
            for i in range(9):
                (repo_path / f"file{i}.txt").write_text(f"Content {i}\n")
                subprocess.run(["git", "add", f"file{i}.txt"], cwd=repo_path, check=True)
                subprocess.run(["git", "commit", "-m", f"Add file {i}"], cwd=repo_path, check=True)

            result = pipeline.run_analysis(
                repo_path=str(repo_path),
                metric_list=["M-01"],
                output_dir=Path("./tmp_output"),
            )
            assert result is not None

        # But benchmark/evaluation methods should fail
        with pytest.raises(RuntimeError, match="Benchmark engine not available"):
            pipeline.run_benchmark("suite", ["D-01"], {})

        with pytest.raises(RuntimeError, match="Evaluation engine not available"):
            pipeline.evaluate_benchmark(BenchmarkRun(predictions={}, metadata={}), {})

    def test_error_propagation_ingestion_failure(self, mock_engines):
        """Test that IngestionError from real ingestion engine propagates as ACS error."""
        # Arrange
        pipeline = AnalysisPipeline(
            ingestion_engine=RepositoryIngestionEngine(),  # real engine
            extraction_engine=mock_engines["extraction"],
            segmentation_engine=mock_engines["segmentation"],
            detection_engine=mock_engines["detection"],
            scoring_engine=mock_engines["scoring"],
            evidence_engine=mock_engines["evidence"],
            explanation_engine=mock_engines["explanation"],
            report_generator=mock_engines["report_generator"],
        )

        # Use a non-existent repository path
        non_existent_path = "/non/existent/repo/path"

        # Act & Assert
        with pytest.raises(IngestionError) as exc_info:
            pipeline.run_analysis(
                repo_path=non_existent_path,
                metric_list=["M-01"],
                output_dir=Path("./tmp_output"),
            )

        # Verify it's an ACS error (IngestionError is a MIIEError)
        assert isinstance(exc_info.value, IngestionError)
        assert exc_info.value.error_code == "INGESTION-ERROR"
        # Check that the error message contains the repository path (may be resolved to absolute)
        assert non_existent_path.replace("/", "\\") in exc_info.value.message


if __name__ == "__main__":
    pytest.main([__file__])
