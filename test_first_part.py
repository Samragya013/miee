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
    """INT-01: Repository Ingestion Engine Contract"""

    def ingest(self, repo_path: str, cache_dir: Optional[Path] = None,
               keep_cache: bool = False, shallow_depth: Optional[int] = None) -> RepositoryContext:
        """Ingest and validate a repository.

        Args:
            repo_path: Local path or HTTPS/SSH URL
            cache_dir: Cache directory path (default: ~/.miie/cache)
            keep_cache: Whether to keep cloned repositories
            shallow_depth: Depth for shallow clone (optional)

        Returns:
            RepositoryContext object with repository metadata

        Raises:
            ValidationError: If repo_path is invalid
            SystemError: If git operations fail
        """
        ...

    def validate(self, path: Path) -> RepositoryContext:
        """Validate an existing repository path.

        Args:
            path: Local repository path

        Returns:
            RepositoryContext object

        Raises:
            ValidationError: If path is not a valid repository
        """
        ...


@runtime_checkable
class IExtractionEngine(Protocol):
    """INT-02: Metric Extraction Engine Contract"""

    def extract(self, repository_context: RepositoryContext,
                metric_list: List[str], since: Optional[datetime] = None,
                until: Optional[datetime] = None, exclude_bots: bool = False) -> MetricDataFrame:
        """Extract metrics from repository.

        Args:
            repository_context: Valid RepositoryContext object
            metric_list: List of metric IDs or ["all"]
            since: Start datetime for extraction (optional)
            until: End datetime for extraction (optional)
            exclude_bots: Whether to exclude bot commits

        Returns:
            MetricDataFrame with extracted metric values

        Raises:
            ValidationError: If inputs are invalid
            MetricError: If extraction fails
        """
        ...


@runtime_checkable
class ISegmentationEngine(Protocol):
    """INT-03: Window Segmentation Engine Contract"""

    def segment(self, metric_dataframe: MetricDataFrame,
                strategy: str, size: int,
                custom_boundaries: Optional[List[tuple[datetime, datetime]]] = None) -> List[WindowDefinition]:
        """Segment metric data into analysis windows.

        Args:
            metric_dataframe: Valid MetricDataFrame object
            strategy: Segmentation strategy ("time", "commit", "release", "custom")
            size: Window size (days for time, commits for commit, etc.)
            custom_boundaries: List of (start, end) tuples for custom strategy

        Returns:
            List of WindowDefinition objects

        Raises:
            ValidationError: If strategy invalid or size < 1
            SegmentationError: If segmentation fails
        """
        ...


@runtime_checkable
class IDetectorEngine(Protocol):
    """INT-04 through INT-04.3: Detector Engine Contract"""

    def detect(self, metric_dataframe: MetricDataFrame,
               windows: List[WindowDefinition],
               detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
               enabled_detectors: Optional[List[str]] = None) -> DetectorResults:
        """Run all enabled detectors on windowed metric data.

        Args:
            metric_dataframe: Valid MetricDataFrame object
            windows: List of WindowDefinition objects
            detector_config: Configuration for each detector (optional)
            enabled_detectors: List of detector IDs to run (optional, defaults to all)

        Returns:
            DetectorResults object with detection outputs

        Raises:
            ValidationError: If inputs invalid
            DetectionError: If detection fails
        """
        ...

    def detect_drift(self, metric_values_a: List[float],
                     metric_values_b: List[float],
                     config: Dict[str, Any]) -> Any:  # D01Output
        """Detect distributional drift between two windows.

        Args:
            metric_values_a: Metric values from window A
            metric_values_b: Metric values from window B
            config: Detector configuration (alpha, psi_threshold)

        Returns:
            D01Output with drift detection results
        """
        ...

    def detect_breakdown(self, values_a: List[float], values_b: List[float],
                         windows: List[WindowDefinition],
                         config: Dict[str, Any]) -> Any:  # D02Output
        """Detect correlation breakdown between two metrics.

        Args:
            values_a: Values of metric A
            values_b: Values of metric B
            windows: List of window definitions
            config: Detector configuration (correlation_threshold)

        Returns:
            D02Output with breakdown detection results
        """
        ...

    def detect_compression(self, metric_values: List[float],
                           thresholds: List[float],
                           window_id: str, config: Dict[str, Any]) -> Any:  # D03Output
        """Detect threshold compression in metric values.

        Args:
            metric_values: List of metric values
            thresholds: List of threshold values to test
            window_id: ID of window being analyzed
            config: Detector configuration (margin, bootstrap settings)

        Returns:
            D03Output with compression detection results
        """
        ...


@runtime_checkable
class IScoringEngine(Protocol):
    """INT-05: Scoring Engine Contract"""

    def compute_integrity_score(self, detector_results: DetectorResults,
                                metric_dataframe: MetricDataFrame,
                                windows: List[WindowDefinition],
                                detector_weights: Optional[Dict[str, float]] = None) -> ScorePackage:
        """Compute Integrity Score and Confidence Score.

        Args:
            detector_results: Valid DetectorResults object
            metric_dataframe: Valid MetricDataFrame object
            windows: List of WindowDefinition objects
            detector_weights: Weights for detectors (defaults to D-01:0.4, D-02:0.35, D-03:0.25)

        Returns:
            ScorePackage with integrity and confidence scores

        Raises:
            ValidationError: If inputs invalid
            ScoreError: If scoring fails
        """
        ...


@runtime_checkable
class IEvidenceAggregator(Protocol):
    """INT-06: Evidence Generation Engine Contract"""

    def aggregate(self, repository_context: RepositoryContext,
                  metric_dataframe: MetricDataFrame,
                  windows: List[WindowDefinition],
                  detector_results: DetectorResults,
                  score_package: ScorePackage,
                  configuration: Dict[str, Any]) -> EvidencePackage:
        """Aggregate all intermediate artifacts into EvidencePackage.

        Args:
            repository_context: Valid RepositoryContext object
            metric_dataframe: Valid MetricDataFrame object
            windows: List of WindowDefinition objects
            detector_results: Valid DetectorResults object
            score_package: Valid ScorePackage object
            configuration: Runtime configuration used

        Returns:
            EvidencePackage with all provenance and results

        Raises:
            ValidationError: If inputs invalid
            EvidenceError: If aggregation fails
        """
        ...


@runtime_checkable
class IExplanationGenerator(Protocol):
    """INT-07: Explanation Generation Engine Contract"""

    def generate(self, evidence_package: EvidencePackage,
                 score_package: ScorePackage,
                 metric_filter: Optional[str] = None,
                 detector_filter: Optional[str] = None) -> ExplanationReport:
        """Generate human-readable explanations from evidence.

        Args:
            evidence_package: Valid EvidencePackage object
            score_package: Valid ScorePackage object
            metric_filter: Optional metric ID to filter explanations
            detector_filter: Optional detector ID to filter explanations

        Returns:
            ExplanationReport with narratives and recommendations

        Raises:
            ValidationError: If inputs invalid
            ExplanationError: If generation fails
        """
        ...


@runtime_checkable
class IBenchmarkRunner(Protocol):
    """INT-09: Benchmark Execution Engine Contract"""

    def run_benchmark(self, suite_id: str, detector_ids: List[str],
                      config: Dict[str, Any], seed: int = 42) -> BenchmarkRun:
        """Execute benchmark suite against detectors.

        Args:
            suite_id: Benchmark suite identifier
            detector_ids: List of detector IDs to evaluate
            config: Configuration overrides for detectors
            seed: Random seed for reproducibility (default: 42)

        Returns:
            BenchmarkRun object with predictions and metadata

        Raises:
            ValidationError: If suite_id invalid or detectors incompatible
            BenchmarkError: If benchmark execution fails
        """
        ...


@runtime_checkable
class IEvaluationEngine(Protocol):
    """INT-10: Evaluation Engine Contract"""

    def evaluate(self, benchmark_run: BenchmarkRun,
                 ground_truth: Dict[str, Any]) -> EvaluationResult:
        """Evaluate benchmark predictions against ground truth.

        Args:
            benchmark_run: Valid BenchmarkRun object
            ground_truth: Ground truth data for benchmark suite

        Returns:
            EvaluationResult with metrics and confusion matrices

        Raises:
            ValidationError: If inputs invalid
            EvaluationError: If evaluation fails
        """
        ...


@runtime_checkable
class IGroundTruthManager(Protocol):
    """INT-12: Ground Truth Management Engine Contract"""

    def submit_annotation(self, dataset_id: str, annotations: List[Annotation],
                          suite_id: str) -> bool:
        """Submit annotator labels for ground truth construction.

        Args:
            dataset_id: Identifier for dataset being annotated
            annotations: List of annotator labels
            suite_id: Benchmark suite identifier

        Returns:
            True if annotation accepted, False if rejected

        Raises:
            ValidationError: If inputs invalid
        """
        ...

    def resolve_conflict(self, annotation_a: Annotation,
                         annotation_b: Annotation,
                         adjudicator_id: str) -> Dict[str, Any]:
        """Resolve conflicting annotations between annotators.

        Args:
            annotation_a: First annotator's label
            annotation_b: Second annotator's label
            adjudicator_id: ID of adjudicator making final decision

        Returns:
            Conflict resolution result with final label and rationale
        """
        ...


@runtime_checkable
class IReportGenerator(Protocol):
    """INT-08: Report Generation Engine Contract"""

