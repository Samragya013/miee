"""
Deterministic Mock Services for MIIE v1.0 Pipeline Testing
Provides mock implementations of all engine protocols for testing.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta, timezone

from miie.contracts.interfaces import (
    IIngestionEngine,
    IExtractionEngine,
    ISegmentationEngine,
    IDetectorEngine,
    IScoringEngine,
    IEvidenceEngine,
    IExplanationEngine,
    IReportGenerator,
    IBenchmarkEngine,
    IEvaluationEngine
)
from miie.schemas.models import (
    RepositoryContext,
    MetricDataFrame,
    WindowDefinition,
    DetectorResults,
    ScorePackage,
    IntegrityScore,
    ConfidenceScore,
    EvidencePackage,
    Provenance,
    WarningItem,
    ExplanationReport,
    ReportOutput,
    BenchmarkRun,
    EvaluationResult
)


class MockIngestionEngine(IIngestionEngine):
    """Mock implementation of IIngestionEngine."""

    def __init__(self, repo_id: str = "test-repo"):
        self.repo_id = repo_id
        self.ingest_called = False
        self.validate_called = False

    def ingest(
        self,
        repo_path: str,
        cache_dir: Optional[Path] = None,
        keep_cache: bool = False,
        shallow_depth: Optional[int] = None
    ) -> RepositoryContext:
        self.ingest_called = True
        return RepositoryContext(
            repo_id=self.repo_id,
            local_path=Path(repo_path) if isinstance(repo_path, str) else repo_path,
            is_remote=False,
            total_commits=100,
            contributor_count=10,
            language_distribution={"Python": 1000}
        )

    def validate(self, context: RepositoryContext) -> bool:
        self.validate_called = True
        return context.total_commits >= 10 and context.contributor_count >= 1


class MockExtractionEngine(IExtractionEngine):
    """Mock implementation of IExtractionEngine."""

    def __init__(self):
        self.extract_called = False

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        exclude_bots: bool = False
    ) -> MetricDataFrame:
        self.extract_called = True

        # Create deterministic metric data matching MetricDataFrame format
        fixed_base_time = datetime(2026, 5, 24, tzinfo=timezone.utc)
        timestamps = [fixed_base_time + timedelta(days=i) for i in range(30)]

        metrics_dict = {}
        for metric_id in metric_list:
            # Generate deterministic values based on metric ID
            values = [float((hash(metric_id + str(i)) % 100)) / 10.0 for i in range(30)]
            # Format as Dict[str, Dict[str, List[Optional[float]]]]
            metrics_dict[metric_id] = {
                "values": [v for v in values],  # Simple list of floats
                "timestamps": [ts.isoformat() for ts in timestamps]  # Store as strings for simplicity
            }

        return MetricDataFrame(
            repo_id=context.repo_id,
            run_id="test-run-001",
            timestamp=fixed_base_time,
            metrics=metrics_dict
        )


class MockSegmentationEngine(ISegmentationEngine):
    """Mock implementation of ISegmentationEngine."""

    def __init__(self):
        self.segment_called = False

    def segment(
        self,
        metric_dataframe: MetricDataFrame,
        strategy: str,
        size: int,
        custom_boundaries: Optional[List[tuple[datetime, datetime]]] = None
    ) -> List[WindowDefinition]:
        self.segment_called = True

        # Create deterministic windows matching WindowDefinition format
        fixed_base_time = datetime(2026, 5, 24, tzinfo=timezone.utc)
        windows = []

        for i in range(0, 30, size):
            start_time = fixed_base_time + timedelta(days=i)
            end_time = fixed_base_time + timedelta(days=min(i + size, 30))
            windows.append(WindowDefinition(
                window_id=f"w{i:02d}",
                start_date=start_time.date() if hasattr(start_time, 'date') else start_time,
                end_date=end_time.date() if hasattr(end_time, 'date') else end_time,
                commits=10,
                strategy="fixed_size"
            ))

        return windows


class MockDetectorEngine(IDetectorEngine):
    """Mock implementation of IDetectorEngine."""

    def __init__(self):
        self.invoke_called = False

    def invoke(
        self,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
        enabled_detectors: Optional[List[str]] = None
    ) -> DetectorResults:
        self.invoke_called = True

        # Create deterministic detector results
        detector_ids = enabled_detectors or ["D-01", "D-02", "D-03"]
        detector_outputs = {}

        for detector_id in detector_ids:
            outputs_by_window = {}
            for i, window in enumerate(windows):
                # Generate deterministic results based on detector and window
                outputs_by_window[f"window_{i}"] = {
                    "drift_detected": (i % 2 == 0),  # Alternate True/False
                    "ks_statistic": 0.1 * (i + 1),
                    "ks_p_value": 0.05 * (i + 1),
                    "psi_value": 0.02 * (i + 1),
                    "mean_shift": 0.5 * (i + 1),
                    "variance_ratio": 1.0 + (0.1 * i),
                    "severity": 0.3 * (i + 1)
                }
            detector_outputs[detector_id] = outputs_by_window

        return DetectorResults(detector_outputs=detector_outputs)


class MockScoringEngine(IScoringEngine):
    """Mock implementation of IScoringEngine."""

    def __init__(self):
        self.compute_integrity_score_called = False

    def compute_integrity_score(
        self,
        detector_results: DetectorResults,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_weights: Optional[Dict[str, float]] = None
    ) -> ScorePackage:
        self.compute_integrity_score_called = True

        # Create deterministic score package
        scores = {}
        for detector_id in detector_results.detector_outputs.keys():
            scores[f"{detector_id}_integrity"] = 0.75
            scores[f"{detector_id}_confidence"] = 0.80

        return ScorePackage(
            integrity=IntegrityScore(
                overall=0.75,
                per_metric={},
                formula_version="1.0.0"
            ),
            confidence=ConfidenceScore(
                overall=0.80,
                factors={},
                band="medium"
            ),
            timestamp=datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
            config_hash="mock_hash"
        )


class MockEvidenceEngine(IEvidenceEngine):
    """Mock implementation of IEvidenceEngine."""

    def __init__(self):
        self.generate_called = False

    def generate(
        self,
        repository_context: RepositoryContext,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_results: DetectorResults,
        score_package: ScorePackage,
        configuration: Dict[str, Any]
    ) -> EvidencePackage:
        self.generate_called = True

        return EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123def456",
                timestamp=datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
                seed=42,
                platform="test-platform",
                python_version="3.9.0",
                dependency_hash="dep123hash456"
            ),
            windows=windows,
            metrics=metric_dataframe.metrics,
            detector_outputs=detector_results,
            scores=score_package,
            warnings=[]
        )


class MockExplanationEngine(IExplanationEngine):
    """Mock implementation of IExplanationEngine."""

    def __init__(self):
        self.generate_called = False

    def generate(
        self,
        evidence_package: EvidencePackage,
        score_package: ScorePackage,
        metric_filter: Optional[str] = None,
        detector_filter: Optional[str] = None
    ) -> ExplanationReport:
        self.generate_called = True

        return ExplanationReport(
            narratives=[
                "Analysis completed successfully.",
                "No significant drift detected in metrics.",
                "All detectors operated within normal parameters."
            ],
            recommendations=[
                "Continue regular monitoring",
                "Consider increasing sampling frequency",
                "Review detector configurations quarterly"
            ]
        )


class MockReportGenerator(IReportGenerator):
    """Mock implementation of IReportGenerator."""

    def __init__(self):
        self.generate_called = False

    def generate(
        self,
        analysis_result: Dict[str, Any],
        output_formats: List[str],
        output_dir: Path
    ) -> ReportOutput:
        self.generate_called = True

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create mock output files
        report_paths = {}
        for fmt in output_formats:
            file_path = output_dir / f"analysis_report.{fmt}"
            # Write minimal content based on format
            if fmt == "json":
                file_path.write_text('{"status": "completed", "timestamp": "' + datetime.now().isoformat() + '"}')
            elif fmt == "md":
                file_path.write_text("# Analysis Report\n\nCompleted successfully at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".")
            elif fmt == "csv":
                file_path.write_text("metric,value\nM-01,0.75\nM-02,0.68\n")
            else:
                file_path.write_text(f"Mock {fmt} output generated at {datetime.now().isoformat()}")

            report_paths[fmt] = file_path

        return ReportOutput(report_paths=report_paths)


class MockBenchmarkEngine(IBenchmarkEngine):
    """Mock implementation of IBenchmarkEngine."""

    def __init__(self):
        self.execute_called = False

    def execute(
        self,
        suite_id: str,
        detector_ids: List[str],
        config: Dict[str, Any],
        seed: int = 42
    ) -> BenchmarkRun:
        self.execute_called = True

        # Create deterministic predictions
        predictions = {}
        for detector_id in detector_ids:
            predictions[detector_id] = [0.8, 0.75, 0.82, 0.78, 0.85]  # Deterministic predictions

        return BenchmarkRun(
            predictions=predictions,
            metadata={
                "suite_id": suite_id,
                "detector_ids": detector_ids,
                "config": config,
                "seed": seed,
                "total_samples": 100,
                "passed_checks": 95,
                "failed_checks": 5
            }
        )


class MockEvaluationEngine(IEvaluationEngine):
    """Mock implementation of IEvaluationEngine."""

    def __init__(self):
        self.evaluate_called = False

    def evaluate(
        self,
        benchmark_run: BenchmarkRun,
        ground_truth: Dict[str, Any]
    ) -> EvaluationResult:
        self.evaluate_called = True

        # Simple mock evaluation - in reality would compare predictions to ground truth
        return EvaluationResult(
            accuracy=0.92,
            precision=0.89,
            recall=0.94,
            f1_score=0.91
        )