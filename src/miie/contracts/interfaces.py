"""
ACS v1.0 Protocol Definitions
Defines the interface contracts for all MIIE v1.0 modules.
Implements ACS Section 3: Internal Module Interfaces (INT-01 through INT-18)
"""

from typing import Protocol, runtime_checkable, List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Import schema models for type hints
from miie.schemas.models import (
    RepositoryContext,
    MetricDataFrame,
    WindowDefinition,
    DetectorResults,
    ScorePackage,
    EvidencePackage,
    ExplanationReport,
    ReportOutput,
    BenchmarkRun,
    EvaluationResult,
    GroundTruthInput,
    Annotation
)


@runtime_checkable
class IIngestionEngine(Protocol):
    """INT-01: Repository Ingestion Engine"""

    def ingest(self, repo_path: str, cache_dir: Optional[Path] = None,
               keep_cache: bool = False, shallow_depth: Optional[int] = None) -> RepositoryContext:
        """Ingest repository and extract context.

        Args:
            repo_path: Path to repository (local or URL)
            cache_dir: Optional directory to cache Git objects
            keep_cache: Whether to keep cache after ingestion
            shallow_depth: Depth for shallow clone (None for full clone)

        Returns:
            RepositoryContext: Repository context extracted during ingestion
        """
        ...

    def validate(self, context: RepositoryContext) -> bool:
        """Validate repository context meets minimum requirements.

        Args:
            context: Repository context to validate

        Returns:
            bool: True if context is valid, False otherwise
        """
        ...


@runtime_checkable
class IExtractionEngine(Protocol):
    """INT-02: Metric Extraction Engine"""

    def extract(self, context: RepositoryContext, metric_list: List[str],
                since: Optional[datetime] = None, until: Optional[datetime] = None,
                exclude_bots: bool = False) -> MetricDataFrame:
        """Extract metrics from repository.

        Args:
            context: Repository context from ingestion
            metric_list: List of metric IDs to extract (e.g., ["M-01", "M-06"])
            since: Extract metrics since this timestamp (inclusive)
            until: Extract metrics until this timestamp (inclusive)
            exclude_bots: Whether to exclude bot-generated commits

        Returns:
            MetricDataFrame: Container for extracted metrics
        """
        ...


@runtime_checkable
class ISegmentationEngine(Protocol):
    """INT-03: Window Segmentation Engine"""

    def segment(self, metric_dataframe: MetricDataFrame, strategy: str,
                size: int, custom_boundaries: Optional[List[tuple[datetime, datetime]]] = None) -> List[WindowDefinition]:
        """Segment metric data into analysis windows.

        Args:
            metric_dataframe: Container for extracted metrics
            strategy: Segmentation strategy ("time", "commit", "release", "custom")
            size: Window size (number of time units, commits, or releases)
            custom_boundaries: Custom window boundaries for "custom" strategy

        Returns:
            List[WindowDefinition]: List of window definitions
        """
        ...


@runtime_checkable
class IDetectorEngine(Protocol):
    """INT-04: Detector Engine"""

    def invoke(self, metric_dataframe: MetricDataFrame, windows: List[WindowDefinition],
               detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
               enabled_detectors: Optional[List[str]] = None) -> DetectorResults:
        """Invoke detectors on segmented metric data.

        Args:
            metric_dataframe: Container for extracted metrics
            windows: List of window definitions for analysis
            detector_config: Optional configuration for detectors
            enabled_detectors: Optional list of detector IDs to enable (None for all)

        Returns:
            DetectorResults: Container for detector outputs
        """
        ...


@runtime_checkable
class IScoringEngine(Protocol):
    """INT-05: Scoring Engine"""

    def compute_integrity_score(self, detector_results: DetectorResults,
                                metric_dataframe: MetricDataFrame,
                                windows: List[WindowDefinition],
                                detector_weights: Optional[Dict[str, float]] = None) -> ScorePackage:
        """Compute integrity and confidence scores.

        Args:
            detector_results: Container for detector outputs
            metric_dataframe: Container for extracted metrics
            windows: List of window definitions used in analysis
            detector_weights: Optional weights for detectors (defaults to equal weights)

        Returns:
            ScorePackage: Container for computed integrity and confidence scores
        """
        ...


@runtime_checkable
class IEvidenceEngine(Protocol):
    """INT-06: Evidence Generation Engine"""

    def generate(self, repository_context: RepositoryContext,
                 metric_dataframe: MetricDataFrame, windows: List[WindowDefinition],
                 detector_results: DetectorResults, score_package: ScorePackage,
                 configuration: Dict[str, Any]) -> EvidencePackage:
        """Generate traceable evidence package.

        Args:
            repository_context: Repository context from ingestion
            metric_dataframe: Container for extracted metrics
            windows: List of window definitions
            detector_results: Container for detector outputs
            score_package: Container for integrity and confidence scores
            configuration: Analysis configuration used

        Returns:
            EvidencePackage: Container for traceable evidence
        """
        ...


@runtime_checkable
class IExplanationEngine(Protocol):
    """INT-07: Explanation Generation Engine"""

    def generate(self, evidence_package: EvidencePackage,
                 score_package: ScorePackage, metric_filter: Optional[str] = None,
                 detector_filter: Optional[str] = None) -> ExplanationReport:
        """Generate explanation report from evidence and scores.

        Args:
            evidence_package: Container for traceable evidence
            score_package: Container for integrity and confidence scores
            metric_filter: Specific metric ID to explain (None for all)
            detector_filter: Specific detector ID to explain (None for all)

        Returns:
            ExplanationReport: Container for explanation narratives and recommendations
        """
        ...


@runtime_checkable
class IBenchmarkEngine(Protocol):
    """INT-09: Benchmark Execution Engine"""

    def execute(self, suite_id: str, detector_ids: List[str],
                config: Dict[str, Any], seed: int = 42) -> BenchmarkRun:
        """Execute benchmark suite.

        Args:
            suite_id: Benchmark suite identifier
            detector_ids: List of detector IDs to benchmark
            config: Benchmark configuration
            seed: Random seed for reproducibility

        Returns:
            BenchmarkRun: Container for benchmark execution results
        """
        ...


@runtime_checkable
class IEvaluationEngine(Protocol):
    """INT-10: Evaluation Engine"""

    def evaluate(self, benchmark_run: BenchmarkRun,
                 ground_truth: Dict[str, Any]) -> EvaluationResult:
        """Evaluate benchmark results against ground truth.

        Args:
            benchmark_run: Container for benchmark execution results
            ground_truth: Ground truth data for evaluation

        Returns:
            EvaluationResult: Container for evaluation metrics
        """
        ...


@runtime_checkable
class IReportGenerator(Protocol):
    """INT-08: Report Generation Engine"""

    def generate(self, analysis_result: Dict[str, Any],
                 output_formats: List[str], output_dir: Path) -> ReportOutput:
        """Generate analysis report in specified formats.

        Args:
            analysis_result: Complete analysis results from pipeline
            output_formats: List of output formats (e.g., ["json", "md", "csv"])
            output_dir: Directory to write output files

        Returns:
            ReportOutput: Container for generated report output paths
        """
        ...


@runtime_checkable
class IDataExporter(Protocol):
    """INT-16: Data Export Engine"""

    def export(self, data: Dict[str, Any], formats: List[str],
               output_dir: Path) -> Dict[str, Path]:
        """Export analysis data in specified formats.

        Args:
            data: Analysis data to export
            formats: List of export formats (e.g., ["json", "csv"])
            output_dir: Directory to write exported files

        Returns:
            Dict[str, Path]: Mapping of format to output file path
        """
        ...


@runtime_checkable
class IDatasetGenerator(Protocol):
    """INT-17: Dataset Generation Engine"""

    def generate(self, dataset_type: str, count: int,
                 output_dir: Path, seed: Optional[int] = None) -> List[Path]:
        """Generate synthetic datasets for testing.

        Args:
            dataset_type: Type of dataset to generate
            count: Number of synthetic datasets to generate
            output_dir: Directory to write generated datasets
            seed: Random seed for reproducibility

        Returns:
            List[Path]: Paths to generated dataset directories
        """
        ...