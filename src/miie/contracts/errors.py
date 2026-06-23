"""
ACS v1.0 Contract Error Model
Implements unified error hierarchy per ACS Section 19: Error Model.
Based on interface-specific error types defined in interfaces.py.
Provides structured error reporting with error codes and human-readable messages.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class MIIEError(Exception):
    """Base exception for all MIIE v1.0 errors.

    Provides common structure for error reporting including error codes,
    human-readable messages, and optional details for debugging.
    """

    def __init__(self,
                 message: str,
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Initialize MIIE error.

        Args:
            message: Human-readable error description
            error_code: Uppercase with hyphens (e.g., VALIDATION-ERROR)
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper().replace('ERROR', '-ERROR')
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            'error': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp
        }

    def __str__(self) -> str:
        """String representation of error."""
        if self.details:
            return f"[{self.error_code}] {self.message} | Details: {self.details}"
        return f"[{self.error_code}] {self.message}"


# Interface-specific error classes (mirroring interfaces.py)
class ValidationError(MIIEError):
    """General validation error."""
    pass


class IngestionError(MIIEError):
    """INT-01: Repository Ingestion Error"""
    pass


class ExtractionError(MIIEError):
    """INT-02: Metric Extraction Error"""
    pass


class SegmentationError(MIIEError):
    """INT-03: Window Segmentation Error"""
    pass


class DetectionError(MIIEError):
    """INT-04: Detector Engine Error"""
    pass


class ScoreError(MIIEError):
    """INT-05: Scoring Engine Error"""
    pass


class EvidenceError(MIIEError):
    """INT-06: Evidence Generation Error"""
    pass


class ExplanationError(MIIEError):
    """INT-07: Explanation Generation Error"""
    pass


class BenchmarkError(MIIEError):
    """INT-09: Benchmark Execution Error"""
    pass


class EvaluationError(MIIEError):
    """INT-10: Evaluation Error"""
    pass


class SerializationError(MIIEError):
    """INT-16: Export Error"""
    pass


class ReportError(MIIEError):
    """INT-08: Report Generation Error"""
    pass


class TemplateError(MIIEError):
    """INT-09: Template Rendering Error"""
    pass


# CLI-specific error classes for standardized error reporting
class ConfigError(MIIEError):
    """M-12: Configuration validation or loading error."""
    pass


class CLIError(MIIEError):
    """Base class for CLI command errors."""

    def __init__(self,
                 message: str,
                 error_code: str,
                 suggestion: Optional[str] = None):
        """Initialize CLI error.

        Args:
            message: Human-readable error description
            error_code: Uppercase with hyphens (e.g., INVALID-REPO)
            suggestion: Optional actionable fix for the user
        """
        super().__init__(message, error_code)
        self.suggestion = suggestion or ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert CLI error to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict['suggestion'] = self.suggestion
        return base_dict

    def __str__(self) -> str:
        """String representation including suggestion (ACS §19)."""
        msg = f"[{self.error_code}] {self.message}"
        if self.suggestion:
            msg += f". Suggestion: {self.suggestion}"
        return msg


class IngestionCLIError(CLIError):
    """Error for miie ingest command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "INGEST-ERROR", suggestion)


class AnalyzeCLIError(CLIError):
    """Error for miie analyze command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "ANALYZE-ERROR", suggestion)


class DetectCLIError(CLIError):
    """Error for miie detect command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "DETECT-ERROR", suggestion)


class BenchmarkCLIError(CLIError):
    """Error for miie benchmark command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "BENCHMARK-ERROR", suggestion)


class EvaluateCLIError(CLIError):
    """Error for miie evaluate command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "EVALUATE-ERROR", suggestion)


class ExplainCLIError(CLIError):
    """Error for miie explain command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "EXPLAIN-ERROR", suggestion)


class ExportCLIError(CLIError):
    """Error for miie export command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "EXPORT-ERROR", suggestion)


class GenerateCLIError(CLIError):
    """Error for miie generate command."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message, "GENERATE-ERROR", suggestion)


# Error factories for common validation scenarios
def validation_error(message: str, field: Optional[str] = None, value: Any = None) -> ValidationError:
    """Create a validation error with optional field context."""
    details = {}
    if field:
        details['field'] = field
    if value is not None:
        details['value'] = str(value)
    return ValidationError(message, "VALIDATION-ERROR", details)


def ingestion_error(message: str, repo_path: Optional[str] = None) -> IngestionError:
    """Create an ingestion error with repository context."""
    details = {}
    if repo_path:
        details['repo_path'] = repo_path
    return IngestionError(message, "INGESTION-ERROR", details)


def extraction_error(message: str, metric_list: Optional[List[str]] = None) -> ExtractionError:
    """Create an extraction error with metric context."""
    details = {}
    if metric_list:
        details['metric_list'] = metric_list
    return ExtractionError(message, "EXTRACTION-ERROR", details)


def segmentation_error(message: str, strategy: Optional[str] = None, size: Optional[int] = None) -> SegmentationError:
    """Create a segmentation error with strategy context."""
    details = {}
    if strategy:
        details['strategy'] = strategy
    if size is not None:
        details['size'] = size
    return SegmentationError(message, "SEGMENTATION-ERROR", details)


def detection_error(message: str, detector_ids: Optional[List[str]] = None) -> DetectionError:
    """Create a detection error with detector context."""
    details = {}
    if detector_ids:
        details['detector_ids'] = detector_ids
    return DetectionError(message, "DETECTION-ERROR", details)


def score_error(message: str, detector_weights: Optional[Dict[str, float]] = None) -> ScoreError:
    """Create a scoring error with weight context."""
    details = {}
    if detector_weights:
        details['detector_weights'] = detector_weights
    return ScoreError(message, "SCORE-ERROR", details)


def evidence_error(message: str, missing_components: Optional[List[str]] = None) -> EvidenceError:
    """Create an evidence error with missing component context."""
    details = {}
    if missing_components:
        details['missing_components'] = missing_components
    return EvidenceError(message, "EVIDENCE-ERROR", details)


def explanation_error(message: str, metric_filter: Optional[str] = None,
                      detector_filter: Optional[str] = None) -> ExplanationError:
    """Create an explanation error with filter context."""
    details = {}
    if metric_filter:
        details['metric_filter'] = metric_filter
    if detector_filter:
        details['detector_filter'] = detector_filter
    return ExplanationError(message, "EXPLANATION-ERROR", details)


def benchmark_error(message: str, suite_id: Optional[str] = None) -> BenchmarkError:
    """Create a benchmark error with suite context."""
    details = {}
    if suite_id:
        details['suite_id'] = suite_id
    return BenchmarkError(message, "BENCHMARK-ERROR", details)


def evaluation_error(message: str, metric_name: Optional[str] = None) -> EvaluationError:
    """Create an evaluation error with metric context."""
    details = {}
    if metric_name:
        details['metric_name'] = metric_name
    return EvaluationError(message, "EVALUATION-ERROR", details)


def serialization_error(message: str, format_type: Optional[str] = None) -> SerializationError:
    """Create a serialization error with format context."""
    details = {}
    if format_type:
        details['format_type'] = format_type
    return SerializationError(message, "SERIALIZATION-ERROR", details)


def report_error(message: str, output_format: Optional[str] = None) -> ReportError:
    """Create a report error with format context."""
    details = {}
    if output_format:
        details['output_format'] = output_format
    return ReportError(message, "REPORT-ERROR", details)


def template_error(message: str, template_name: Optional[str] = None) -> TemplateError:
    """Create a template error with template context."""
    details = {}
    if template_name:
        details['template_name'] = template_name
    return TemplateError(message, "TEMPLATE-ERROR", details)