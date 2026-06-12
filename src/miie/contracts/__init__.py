"""MIIE package contracts module."""

# Import and expose submodules
from . import dataclasses
from . import errors
from . import interfaces
from . import validators

# Expose key classes and functions for convenience
from .dataclasses import (
    # Input DTOs
    IngestionInputDTO,
    ExtractionInputDTO,
    SegmentationInputDTO,
    DetectionInputDTO,
    D01InputDTO,
    D01OutputDTO,
    D02InputDTO,
    D02OutputDTO,
    D03InputDTO,
    D03OutputDTO,
    ScoringInputDTO,
    EvidenceInputDTO,
    ExplanationInputDTO,
    BenchmarkInputDTO,
    EvaluationInputDTO,
    ReportInputDTO,
    CLIErrorInfo,
    # Response DTOs
    IngestionOutputDTO,
    AnalyzeOutputDTO,
    DetectOutputDTO,
    BenchmarkOutputDTO,
    EvaluateOutputDTO,
    ExplainOutputDTO,
    ExportOutputDTO,
    GenerateOutputDTO
)

from .errors import (
    MIIEError,
    ValidationError,
    IngestionError,
    ExtractionError,
    SegmentationError,
    DetectionError,
    ScoreError,
    EvidenceError,
    ExplanationError,
    BenchmarkError,
    EvaluationError,
    SerializationError,
    ReportError,
    TemplateError,
    CLIError,
    IngestionCLIError,
    AnalyzeCLIError,
    DetectCLIError,
    BenchmarkCLIError,
    EvaluateCLIError,
    ExplainCLIError,
    ExportCLIError,
    GenerateCLIError,
    validation_error,
    ingestion_error,
    extraction_error,
    segmentation_error,
    detection_error,
    score_error,
    evidence_error,
    explanation_error,
    benchmark_error,
    evaluation_error,
    serialization_error,
    report_error,
    template_error
)

from .interfaces import (
    # Protocols
    IIngestionEngine,
    IExtractionEngine,
    ISegmentationEngine,
    IDetectorEngine,
    IScoringEngine,
    IEvidenceEngine,
    IExplanationEngine,
    IBenchmarkEngine,
    IEvaluationEngine,
    IReportGenerator,
    IDataExporter,
    IDatasetGenerator
)

from .validators import (
    validate_repository_inputs,
    validate_extraction_inputs,
    validate_segmentation_inputs,
    validate_detection_inputs,
    validate_d01_input,
    validate_d02_input,
    validate_d03_input,
    validate_scoring_inputs,
    validate_evidence_inputs,
    validate_explanation_inputs,
    validate_benchmark_inputs,
    validate_evaluation_inputs,
    validate_report_inputs,
    validate_cli_ingest_inputs,
    validate_cli_analyze_inputs,
    is_valid_uuid,
    is_valid_sha256,
    is_valid_window_id,
    is_valid_metric_id,
    is_valid_detector_id
)