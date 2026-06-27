"""MIIE package contracts module."""

# Import and expose submodules
# Expose key classes and functions for convenience
from .dataclasses import AnalyzeOutputDTO  # Input DTOs; Response DTOs
from .dataclasses import (
    BenchmarkInputDTO,
    BenchmarkOutputDTO,
    CLIErrorInfo,
    D01InputDTO,
    D01OutputDTO,
    D02InputDTO,
    D02OutputDTO,
    D03InputDTO,
    D03OutputDTO,
    DetectionInputDTO,
    DetectOutputDTO,
    EvaluateOutputDTO,
    EvaluationInputDTO,
    EvidenceInputDTO,
    ExplainOutputDTO,
    ExplanationInputDTO,
    ExportOutputDTO,
    ExtractionInputDTO,
    GenerateOutputDTO,
    IngestionInputDTO,
    IngestionOutputDTO,
    ReportInputDTO,
    ScoringInputDTO,
    SegmentationInputDTO,
)
from .interfaces import IDataExporter  # Protocols
from .interfaces import (
    IBenchmarkEngine,
    IDatasetGenerator,
    IDetectorEngine,
    IEvaluationEngine,
    IEvidenceEngine,
    IExplanationEngine,
    IExtractionEngine,
    IIngestionEngine,
    IReportGenerator,
    IScoringEngine,
    ISegmentationEngine,
)
