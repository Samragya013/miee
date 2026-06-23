"""Integration test demonstrating Day 10 dry-run pipeline execution."""
from src.miie.processing.scoring.engine import ScoringEngine
from src.miie.processing.explanation.engine import ExplanationEngine
from src.miie.processing.benchmark.engine import BenchmarkEngine
from src.miie.processing.evaluation.engine import EvaluationEngine
from src.miie.processing.reporting.engine import ReportGenerator
from src.miie.processing.scoring.mock_scoring import MockScoringEngine
from src.miie.schemas.models import (
    RepositoryContext, MetricDataFrame, WindowDefinition, DetectorResults,
    ScorePackage, EvidencePackage, ExplanationReport, BenchmarkRun,
    EvaluationResult, ReportOutput, Provenance, IntegrityScore, ConfidenceScore
)
from pathlib import Path
import tempfile
import datetime


def create_mock_repository_context():
    """Create a mock repository context for testing."""
    return RepositoryContext(
        repo_id="test-repo",
        local_path=Path("/tmp/test-repo"),
        is_remote=False,
        total_commits=100,
        first_commit_date=datetime.datetime(2025, 1, 1),
        last_commit_date=datetime.datetime(2025, 12, 31),
        contributor_count=5,
        is_shallow=False,
        is_fork=False,
        language_distribution={"Python": 80, "JavaScript": 20}
    )


def create_mock_metric_dataframe():
    """Create a mock metric dataframe for testing."""
    return MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run-001",
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        metrics={
            "M-02": {"w01": [10.0, 12.0, 11.0], "w02": [9.0, 13.0, 10.0]},
            "M-06": {"w01": [5.0, 6.0, 5.5], "w02": [4.0, 7.0, 5.0]}
        }
    )


def create_mock_window_definitions():
    """Create mock window definitions for testing."""
    return [
        WindowDefinition(
            window_id="w01",
            start_date=datetime.datetime(2025, 1, 1),
            end_date=datetime.datetime(2025, 1, 31),
            commits=10,
            strategy="fixed_size"
        ),
        WindowDefinition(
            window_id="w02",
            start_date=datetime.datetime(2025, 2, 1),
            end_date=datetime.datetime(2025, 2, 28),
            commits=10,
            strategy="fixed_size"
        )
    ]


def create_mock_detector_results():
    """Create mock detector results for testing."""
    return DetectorResults(
        detector_outputs={
            "D-01": {"some_metric": 0.5, "trend": "increasing"},
            "D-02": {"another_metric": 0.3, "pattern": "cyclic"},
            "D-03": {"third_metric": 0.7, "status": "stable"}
        }
    )


def create_mock_evidence_package(repository_context, metric_dataframe, windows, detector_results):
    """Create a mock evidence package for testing."""
    return EvidencePackage(
        provenance=Provenance(
            miie_version="1.0.0",
            config_hash="test-config-hash",
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            seed=42,
            platform="test-platform",
            python_version="3.9.0",
            dependency_hash="test-dep-hash"
        ),
        windows=windows,
        metrics=metric_dataframe.metrics,
        detector_outputs=detector_results,
        scores=ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.80, factors={}, band="medium"),
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
            config_hash="test-config-hash",
            formula_version="1.0.0"
        )
    )


def test_day10_dry_run_pipeline_integration():
    """Test that demonstrates the complete Day 10 dry-run pipeline integration."""

    # Step 1: Create mock inputs (simulating repository ingestion and metric extraction)
    repository_context = create_mock_repository_context()
    metric_dataframe = create_mock_metric_dataframe()
    windows = create_mock_window_definitions()
    detector_results = create_mock_detector_results()

    # Step 2: Scoring Engine (Day 9 component)
    scoring_engine = ScoringEngine()
    score_package = scoring_engine.compute_integrity_score(
        detector_results=detector_results,
        metric_dataframe=metric_dataframe,
        windows=windows
    )

    # Validate scoring output
    assert isinstance(score_package, ScorePackage)
    assert hasattr(score_package, 'integrity')
    assert hasattr(score_package, 'confidence')
    assert isinstance(score_package.integrity, dict)
    assert isinstance(score_package.confidence, dict)
    assert "overall" in score_package.integrity
    assert "overall" in score_package.confidence

    # Step 3: Evidence Package Creation (simulating evidence generation)
    evidence_package = create_mock_evidence_package(
        repository_context, metric_dataframe, windows, detector_results
    )

    # Validate evidence package
    assert isinstance(evidence_package, EvidencePackage)
    assert hasattr(evidence_package, 'provenance')
    assert hasattr(evidence_package, 'windows')
    assert hasattr(evidence_package, 'metrics')
    assert hasattr(evidence_package, 'detector_outputs')

    # Step 4: Explanation Engine (Day 10 component)
    explanation_engine = ExplanationEngine()
    explanation_report = explanation_engine.generate(
        evidence_package=evidence_package,
        score_package=score_package
    )

    # Validate explanation output
    assert isinstance(explanation_report, ExplanationReport)
    assert hasattr(explanation_report, 'narratives')
    assert hasattr(explanation_report, 'recommendations')
    assert isinstance(explanation_report.narratives, list)
    assert isinstance(explanation_report.recommendations, list)
    assert len(explanation_report.narratives) > 0
    assert len(explanation_report.recommendations) > 0

    # Step 5: Benchmark Engine (Day 10 component)
    benchmark_engine = BenchmarkEngine()
    benchmark_run = benchmark_engine.execute(
        suite_id="test-suite-001",
        detector_ids=["D-01", "D-02", "D-03"],
        config={"test": True, "pipeline_stage": "validation"},
        seed=42
    )

    # Validate benchmark output
    assert isinstance(benchmark_run, BenchmarkRun)
    assert hasattr(benchmark_run, 'predictions')
    assert hasattr(benchmark_run, 'metadata')
    assert isinstance(benchmark_run.predictions, dict)
    assert isinstance(benchmark_run.metadata, dict)
    assert len(benchmark_run.predictions) > 0

    # Step 6: Evaluation Engine (Day 10 component)
    evaluation_engine = EvaluationEngine()
    # Create minimal ground truth for evaluation
    ground_truth = {"test": "validation_data"}
    evaluation_result = evaluation_engine.evaluate(
        benchmark_run=benchmark_run,
        ground_truth=ground_truth
    )

    # Validate evaluation output
    assert isinstance(evaluation_result, EvaluationResult)
    assert hasattr(evaluation_result, 'accuracy')
    assert hasattr(evaluation_result, 'precision')
    assert hasattr(evaluation_result, 'recall')
    assert hasattr(evaluation_result, 'f1_score')
    assert isinstance(evaluation_result.accuracy, float)
    assert isinstance(evaluation_result.precision, float)
    assert isinstance(evaluation_result.recall, float)
    assert isinstance(evaluation_result.f1_score, float)
    assert 0.0 <= evaluation_result.accuracy <= 1.0
    assert 0.0 <= evaluation_result.precision <= 1.0
    assert 0.0 <= evaluation_result.recall <= 1.0
    assert 0.0 <= evaluation_result.f1_score <= 1.0

    # Step 7: Report Generator (Day 10 component)
    report_generator = ReportGenerator()

    # Prepare analysis results from pipeline
    analysis_results = {
        "repository_context": {
            "repo_id": repository_context.repo_id,
            "total_commits": repository_context.total_commits,
            "contributor_count": repository_context.contributor_count
        },
        "scores": {
            "integrity_overall": score_package.integrity["overall"],
            "confidence_overall": score_package.confidence["overall"]
        },
        "explanation": {
            "narrative_count": len(explanation_report.narratives),
            "recommendation_count": len(explanation_report.recommendations)
        },
        "benchmark": {
            "detectors_evaluated": len(["D-01", "D-02", "D-03"]),
            "suite_id": "test-suite-001"
        },
        "evaluation": {
            "accuracy": evaluation_result.accuracy,
            "precision": evaluation_result.precision,
            "recall": evaluation_result.recall,
            "f1_score": evaluation_result.f1_score
        }
    }

    # Generate reports in multiple formats
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        output_formats = ["json", "md"]
        report_output = report_generator.generate(
            analysis_result=analysis_results,
            output_formats=output_formats,
            output_dir=output_dir
        )

        # Validate report output
        assert isinstance(report_output, ReportOutput)
        assert hasattr(report_output, 'report_paths')
        assert isinstance(report_output.report_paths, dict)
        assert "json" in report_output.report_paths
        assert "markdown" in report_output.report_paths

        # Verify JSON report exists and is valid
        json_report_path = report_output.report_paths["json"]
        assert json_report_path.exists()
        assert json_report_path.suffix == ".json"

        import json
        with open(json_report_path, 'r') as f:
            report_data = json.load(f)
            assert "metadata" in report_data
            assert "analysis_result" in report_data
            assert report_data["analysis_result"]["repository_context"]["repo_id"] == "test-repo"

        # Verify markdown report exists
        md_report_path = report_output.report_paths["markdown"]
        assert md_report_path.exists()
        assert md_report_path.suffix == ".md"

        with open(md_report_path, 'r') as f:
            md_content = f.read()
            assert "# MIIE Analysis Report" in md_content
            assert "test-repo" in md_content

    # If we reach this point, the entire pipeline has successfully executed
    # demonstrating that all Day 10 components work together
    assert True  # Pipeline completed successfully


def test_day10_components_can_be_instantiated_together():
    """Test that all Day 10 components can be instantiated and are of correct types."""
    # Test Explanation Engine
    explanation_engine = ExplanationEngine()
    assert isinstance(explanation_engine, ExplanationEngine)

    # Test Benchmark Engine
    benchmark_engine = BenchmarkEngine()
    assert isinstance(benchmark_engine, BenchmarkEngine)

    # Test Evaluation Engine
    evaluation_engine = EvaluationEngine()
    assert isinstance(evaluation_engine, EvaluationEngine)

    # Test Report Generator
    report_generator = ReportGenerator()
    assert isinstance(report_generator, ReportGenerator)

    # Verify they all implement their respective interfaces
    from src.miie.contracts.interfaces import (
        IExplanationEngine, IBenchmarkEngine, IEvaluationEngine, IReportGenerator
    )

    assert isinstance(explanation_engine, IExplanationEngine)
    assert isinstance(benchmark_engine, IBenchmarkEngine)
    assert isinstance(evaluation_engine, IEvaluationEngine)
    assert isinstance(report_generator, IReportGenerator)