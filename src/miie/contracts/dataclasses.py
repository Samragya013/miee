"""
ACS v1.0 Data Transfer Objects
Implements the data structures for module communication.
These mirror the schemas defined in the interfaces but are used for actual data transfer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import from schemas to avoid duplication but re-export as DTOs
from miie.schemas.models import Annotation as SchemaAnnotation
from miie.schemas.models import BenchmarkRun as SchemaBenchmarkRun
from miie.schemas.models import DetectorResults as SchemaDetectorResults
from miie.schemas.models import EvaluationResult as SchemaEvaluationResult
from miie.schemas.models import EvidencePackage as SchemaEvidencePackage
from miie.schemas.models import ExplanationReport as SchemaExplanationReport
from miie.schemas.models import GroundTruthInput as SchemaGroundTruthInput
from miie.schemas.models import MetricDataFrame as SchemaMetricDataFrame
from miie.schemas.models import ReportOutput as SchemaReportOutput
from miie.schemas.models import RepositoryContext as SchemaRepositoryContext
from miie.schemas.models import ScorePackage as SchemaScorePackage
from miie.schemas.models import WindowDefinition as SchemaWindowDefinition

# Re-export schema models as DTOs for clarity in contract layer
RepositoryContext = SchemaRepositoryContext
MetricDataFrame = SchemaMetricDataFrame
WindowDefinition = SchemaWindowDefinition
DetectorResults = SchemaDetectorResults
ScorePackage = SchemaScorePackage
EvidencePackage = SchemaEvidencePackage
ExplanationReport = SchemaExplanationReport
ReportOutput = SchemaReportOutput
BenchmarkRun = SchemaBenchmarkRun
EvaluationResult = SchemaEvaluationResult
GroundTruthInput = SchemaGroundTruthInput
Annotation = SchemaAnnotation


# Additional DTOs specific to contract layer that aren't in schemas
@dataclass
class IngestionInputDTO:
    """DTO for INT-01: Repository Ingestion input"""

    repo_path: str
    cache_dir: Optional[Path] = None
    keep_cache: bool = False
    shallow_depth: Optional[int] = None


@dataclass
class ExtractionInputDTO:
    """DTO for INT-02: Metric Extraction input"""

    repository_context: RepositoryContext
    metric_list: List[str]
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    exclude_bots: bool = False


@dataclass
class SegmentationInputDTO:
    """DTO for INT-03: Window Segmentation input"""

    metric_dataframe: MetricDataFrame
    strategy: str  # "time" | "commit" | "release" | "custom"
    size: int
    custom_boundaries: Optional[List[tuple[datetime, datetime]]] = None


@dataclass
class DetectionInputDTO:
    """DTO for INT-04: Detector Invocation input"""

    metric_dataframe: MetricDataFrame
    windows: List[WindowDefinition]
    detector_config: Optional[Dict[str, Dict[str, Any]]] = None
    enabled_detectors: Optional[List[str]] = None  # Items from {D-01, D-02, D-03, "all"}


@dataclass
class D01InputDTO:
    """DTO for D-01 Distributional Dretector input"""

    metric_values_window_a: List[float]
    metric_values_window_b: List[float]
    metric_id: str
    window_pair: tuple[str, str]
    config: Dict[str, Any] = field(default_factory=lambda: {"alpha": 0.05, "psi_threshold": 0.25})


@dataclass
class D01OutputDTO:
    """DTO for D-01 Distributional Drift detector output"""

    detected: bool
    ks_statistic: float  # [0.0, 1.0]
    ks_p_value: float  # [0.0, 1.0]
    psi_value: float  # ≥ 0.0
    direction: str  # "mean_shift" | "variance_collapse" | "shape_change"
    severity: float  # [0.0, 1.0]; min(1.0, ks_statistic / 0.5)
    mean_shift: Optional[float] = None
    variance_ratio: Optional[float] = None
    sample_sizes: List[int] = field(default_factory=list)  # [n_a, n_b], each ≥ 10
    metric_id: str = ""
    window_pair: List[str] = field(default_factory=list)


@dataclass
class D02InputDTO:
    """DTO for D-02 Correlation Breakdown detector input"""

    values_a: List[float]
    values_b: List[float]
    metric_a: str
    metric_b: str
    window_history: List[WindowDefinition]
    config: Dict[str, Any] = field(default_factory=lambda: {"correlation_threshold": 0.3})


@dataclass
class D02OutputDTO:
    """DTO for D-02 Correlation Breakdown detector output"""

    detected: bool
    breakdown_type: str  # "sudden_drop" | "sign_reversal" | "gradual_erosion" | "confidence_exclusion"
    pearson_trajectory: List[float] = field(default_factory=list)  # Per window, [-1.0, 1.0]
    spearman_trajectory: List[float] = field(default_factory=list)  # Per window, [-1.0, 1.0]
    window_pairs_flagged: List[List[str]] = field(default_factory=list)
    confidence_intervals: List[List[float]] = field(default_factory=list)  # [[lower, upper], ...]
    severity: float = 0.0  # [0.0, 1.0]; min(1.0, |delta_r| / 0.3)
    metric_pair: List[str] = field(default_factory=list)  # [M_i, M_j], i < j


@dataclass
class D03InputDTO:
    """DTO for D-03 Threshold Compression detector input"""

    metric_values: List[float]
    thresholds: List[float]
    metric_id: str
    window_id: str
    config: Dict[str, Any] = field(
        default_factory=lambda: {
            "margin": 0.02,
            "bootstrap_iterations": 1000,
            "bootstrap_seed": 42,
        }
    )


@dataclass
class D03OutputDTO:
    """DTO for D-03 Threshold Compression detector output"""

    detected: bool
    threshold: float
    margin: float
    compression_index: float
    excess_mass_z_score: float
    dip_test_statistic: float
    dip_test_p_value: float
    hypothesized_cause: str  # "POLICY_MANDATE" | "UNKNOWN" | "THRESHOLD_GAMING" | "SLA_COMPLIANCE"
    sample_size: int  # ≥ 20
    window_id: str
    metric_id: str


@dataclass
class ScoringInputDTO:
    """DTO for INT-05: Score Calculation input"""

    detector_results: DetectorResults
    metric_dataframe: MetricDataFrame
    windows: List[WindowDefinition]
    detector_weights: Optional[Dict[str, float]] = None  # Defaults to {"D-01": 0.40, "D-02": 0.35, "D-03": 0.25}


@dataclass
class EvidenceInputDTO:
    """DTO for INT-06: Evidence Generation input"""

    repository_context: RepositoryContext
    metric_dataframe: MetricDataFrame
    windows: List[WindowDefinition]
    detector_results: DetectorResults
    score_package: ScorePackage
    configuration: Dict[str, Any]


@dataclass
class ExplanationInputDTO:
    """DTO for INT-07: Explanation Generation input"""

    evidence_package: EvidencePackage
    score_package: ScorePackage
    metric_filter: Optional[str] = None  # Specific metric_id or None for all
    detector_filter: Optional[str] = None  # Specific detector_id or None for all


@dataclass
class BenchmarkInputDTO:
    """DTO for INT-09: Benchmark Execution input"""

    suite_id: str
    detector_ids: List[str]  # Items from {D-01, D-02, D-03, "all"}
    config: Dict[str, Any] = field(default_factory=dict)
    seed: int = 42


@dataclass
class EvaluationInputDTO:
    """DTO for INT-10: Evaluation input"""

    benchmark_run: BenchmarkRun
    ground_truth: Dict[str, Any]  # GroundTruth object


@dataclass
class ReportInputDTO:
    """DTO for INT-08: Report Generation input"""

    analysis_result: Dict[str, Any]
    output_formats: List[str]  # ["json", "md", "csv"]
    output_dir: Path


@dataclass
class CLIErrorInfo:
    """DTO for CLI error information"""

    error_code: str  # Uppercase with hyphens: INVALID-REPO
    message: str  # Human-readable description
    suggestion: str  # Actionable fix


# Response DTOs for CLI commands
@dataclass
class IngestionOutputDTO:
    """DTO for miie ingest command output"""

    repository_context: RepositoryContext
    json_output: str  # RepositoryContext serialized to JSON


@dataclass
class AnalyzeOutputDTO:
    """DTO for miie analyze command output"""

    exit_code: int  # 0 (IS=1.0), 1 (IS<1.0), 2 (error), 3 (invalid input)
    output_files: Dict[str, Path]  # format -> path mapping
    manifest_path: Path
    overall_integrity_score: float
    overall_confidence: float


@dataclass
class DetectOutputDTO:
    """DTO for miie detect command output"""

    exit_code: int  # 0 (success), 2 (error), 3 (invalid input)
    detector_results: DetectorResults
    json_output: str  # DetectorResults serialized to JSON


@dataclass
class BenchmarkOutputDTO:
    """DTO for miie benchmark command output"""

    exit_code: int  # 0 (success), 4 (benchmark failure)
    benchmark_run: BenchmarkRun
    json_output: str  # BenchmarkRun serialized to JSON


@dataclass
class EvaluateOutputDTO:
    """DTO for miie evaluate command output"""

    exit_code: int  # 0 (success), 2 (error), 3 (invalid input)
    evaluation_result: EvaluationResult
    json_output: str  # EvaluationResult serialized to JSON


@dataclass
class ExplainOutputDTO:
    """DTO for miie explain command output"""

    exit_code: int  # 0 (success), 3 (invalid input)
    explanation_report: ExplanationReport
    output_content: str  # Markdown or JSON explanation report


@dataclass
class ExportOutputDTO:
    """DTO for miie export command output"""

    exit_code: int  # 0 (success), 3 (invalid input)
    output_files: Dict[str, Path]  # format -> path mapping


@dataclass
class GenerateOutputDTO:
    """DTO for miie generate command output"""

    exit_code: int  # 0 (success), 2 (error), 3 (invalid input)
    generated_datasets: List[Path]  # Paths to generated dataset directories
