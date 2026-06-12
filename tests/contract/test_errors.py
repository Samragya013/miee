"""
Contract Layer Error Tests
Tests for error handling in the contracts layer.
"""

import pytest
from datetime import datetime
from miie.contracts.errors import (
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


def test_base_miie_error():
    """Test base MIIEError creation and properties."""
    error = MIIEError(
        message="Test error message",
        error_code="TEST-ERROR",
        details={"key": "value"}
    )

    assert str(error) == "[TEST-ERROR] Test error message | Details: {'key': 'value'}"
    assert error.message == "Test error message"
    assert error.error_code == "TEST-ERROR"
    assert error.details == {"key": "value"}
    assert error.timestamp.endswith("Z")
    assert "T" in error.timestamp  # ISO format contains T

    error_dict = error.to_dict()
    assert error_dict['error'] == "TEST-ERROR"
    assert error_dict['message'] == "Test error message"
    assert error_dict['details'] == {"key": "value"}
    assert 'timestamp' in error_dict


def test_validation_error():
    """Test ValidationError creation."""
    error = ValidationError("Validation failed")
    assert isinstance(error, MIIEError)
    assert error.error_code == "VALIDATION-ERROR"
    assert str(error) == "[VALIDATION-ERROR] Validation failed"


def test_ingestion_error():
    """Test IngestionError creation."""
    error = IngestionError("Ingestion failed", details={"repo_path": "/bad/path"})
    assert isinstance(error, MIIEError)
    assert error.error_code == "INGESTION-ERROR"
    assert error.details.get('repo_path') == "/bad/path"


def test_extraction_error():
    """Test ExtractionError creation."""
    error = ExtractionError("Extraction failed", details={"metric_list": ["M-01", "M-02"]})
    assert isinstance(error, MIIEError)
    assert error.error_code == "EXTRACTION-ERROR"
    assert error.details.get('metric_list') == ["M-01", "M-02"]


def test_segmentation_error():
    """Test SegmentationError creation."""
    error = SegmentationError("Segmentation failed", details={"strategy": "time", "size": 7})
    assert isinstance(error, MIIEError)
    assert error.error_code == "SEGMENTATION-ERROR"
    assert error.details.get('strategy') == "time"
    assert error.details.get('size') == 7


def test_detection_error():
    """Test DetectionError creation."""
    error = DetectionError("Detection failed", details={"detector_ids": ["D-01", "D-02"]})
    assert isinstance(error, MIIEError)
    assert error.error_code == "DETECTION-ERROR"
    assert error.details.get('detector_ids') == ["D-01", "D-02"]


def test_score_error():
    """Test ScoreError creation."""
    error = ScoreError("Scoring failed", details={"detector_weights": {"D-01": 0.5, "D-02": 0.5}})
    assert isinstance(error, MIIEError)
    assert error.error_code == "SCORE-ERROR"
    assert error.details.get('detector_weights') == {"D-01": 0.5, "D-02": 0.5}


def test_evidence_error():
    """Test EvidenceError creation."""
    error = EvidenceError("Evidence failed", details={"missing_components": ["repository_context"]})
    assert isinstance(error, MIIEError)
    assert error.error_code == "EVIDENCE-ERROR"
    assert error.details.get('missing_components') == ["repository_context"]


def test_explanation_error():
    """Test ExplanationError creation."""
    error = ExplanationError("Explanation failed", details={"metric_filter": "M-01", "detector_filter": "D-01"})
    assert isinstance(error, MIIEError)
    assert error.error_code == "EXPLANATION-ERROR"
    assert error.details.get('metric_filter') == "M-01"
    assert error.details.get('detector_filter') == "D-01"


def test_benchmark_error():
    """Test BenchmarkError creation."""
    error = BenchmarkError("Benchmark failed", details={"suite_id": "suite-1"})
    assert isinstance(error, MIIEError)
    assert error.error_code == "BENCHMARK-ERROR"
    assert error.details.get('suite_id') == "suite-1"


def test_evaluation_error():
    """Test EvaluationError creation."""
    error = EvaluationError("Evaluation failed", details={"metric_name": "M-01"})
    assert isinstance(error, MIIEError)
    assert error.error_code == "EVALUATION-ERROR"
    assert error.details.get('metric_name') == "M-01"


def test_serialization_error():
    """Test SerializationError creation."""
    error = SerializationError("Serialization failed", details={"format_type": "json"})
    assert isinstance(error, MIIEError)
    assert error.error_code == "SERIALIZATION-ERROR"
    assert error.details.get('format_type') == "json"


def test_report_error():
    """Test ReportError creation."""
    error = ReportError("Report failed", details={"output_format": "md"})
    assert isinstance(error, MIIEError)
    assert error.error_code == "REPORT-ERROR"
    assert error.details.get('output_format') == "md"


def test_template_error():
    """Test TemplateError creation."""
    error = TemplateError("Template failed", details={"template_name": "explanation.j2"})
    assert isinstance(error, MIIEError)
    assert error.error_code == "TEMPLATE-ERROR"
    assert error.details.get('template_name') == "explanation.j2"


def test_cli_error_base():
    """Test CLIError base class."""
    error = CLIError("CLI failed", "CLI-ERROR", "Fix the CLI usage")
    assert isinstance(error, MIIEError)
    assert error.error_code == "CLI-ERROR"
    assert error.suggestion == "Fix the CLI usage"

    error_dict = error.to_dict()
    assert error_dict['suggestion'] == "Fix the CLI usage"


def test_specific_cli_errors():
    """Test specific CLI error classes."""
    error = IngestionCLIError("Invalid repo", "Check repo path")
    assert isinstance(error, CLIError)
    assert error.error_code == "INGEST-ERROR"
    assert error.suggestion == "Check repo path"

    error = AnalyzeCLIError("Analysis failed", "Check parameters")
    assert isinstance(error, CLIError)
    assert error.error_code == "ANALYZE-ERROR"
    assert error.suggestion == "Check parameters"


def test_error_factories():
    """Test error factory functions."""
    # validation_error
    error = validation_error("Field invalid", field="test_field", value="bad_value")
    assert isinstance(error, ValidationError)
    assert error.details.get('field') == "test_field"
    assert error.details.get('value') == "bad_value"

    # ingestion_error
    error = ingestion_error("Invalid repo", repo_path="/bad/path")
    assert isinstance(error, IngestionError)
    assert error.details.get('repo_path') == "/bad/path"

    # extraction_error
    error = extraction_error("Invalid metrics", metric_list=["M-01", "M-02"])
    assert isinstance(error, ExtractionError)
    assert error.details.get('metric_list') == ["M-01", "M-02"]

    # segmentation_error
    error = segmentation_error("Invalid strategy", strategy="custom", size=5)
    assert isinstance(error, SegmentationError)
    assert error.details.get('strategy') == "custom"
    assert error.details.get('size') == 5

    # detection_error
    error = detection_error("Detection failed", detector_ids=["D-01"])
    assert isinstance(error, DetectionError)
    assert error.details.get('detector_ids') == ["D-01"]

    # score_error
    error = score_error("Scoring failed", detector_weights={"D-01": 1.0})
    assert isinstance(error, ScoreError)
    assert error.details.get('detector_weights') == {"D-01": 1.0}

    # evidence_error
    error = evidence_error("Missing evidence", missing_components=["score_package"])
    assert isinstance(error, EvidenceError)
    assert error.details.get('missing_components') == ["score_package"]

    # explanation_error
    error = explanation_error("Explanation failed", metric_filter="M-01", detector_filter="D-02")
    assert isinstance(error, ExplanationError)
    assert error.details.get('metric_filter') == "M-01"
    assert error.details.get('detector_filter') == "D-02"

    # benchmark_error
    error = benchmark_error("Benchmark failed", suite_id="bench-suite")
    assert isinstance(error, BenchmarkError)
    assert error.details.get('suite_id') == "bench-suite"

    # evaluation_error
    error = evaluation_error("Evaluation failed", metric_name="M-03")
    assert isinstance(error, EvaluationError)
    assert error.details.get('metric_name') == "M-03"

    # serialization_error
    error = serialization_error("Serialization failed", format_type="csv")
    assert isinstance(error, SerializationError)
    assert error.details.get('format_type') == "csv"

    # report_error
    error = report_error("Report failed", output_format="json")
    assert isinstance(error, ReportError)
    assert error.details.get('output_format') == "json"

    # template_error
    error = template_error("Template failed", template_name="report.j2")
    assert isinstance(error, TemplateError)
    assert error.details.get('template_name') == "report.j2"


def test_error_inheritance():
    """Test that all errors inherit from MIIEError."""
    errors = [
        ValidationError("test"),
        IngestionError("test"),
        ExtractionError("test"),
        SegmentationError("test"),
        DetectionError("test"),
        ScoreError("test"),
        EvidenceError("test"),
        ExplanationError("test"),
        BenchmarkError("test"),
        EvaluationError("test"),
        SerializationError("test"),
        ReportError("test"),
        TemplateError("test")
    ]

    for error in errors:
        assert isinstance(error, MIIEError)
        assert hasattr(error, 'message')
        assert hasattr(error, 'error_code')
        assert hasattr(error, 'details')
        assert hasattr(error, 'timestamp')
        assert hasattr(error, 'to_dict')


def test_error_string_representation():
    """Test string representation of errors."""
    error = ValidationError("Test validation error")
    error_str = str(error)
    assert "[VALIDATION-ERROR]" in error_str
    assert "Test validation error" in error_str

    error_with_details = ValidationError("Test error", details={"info": "more"})
    error_str = str(error_with_details)
    assert "[VALIDATION-ERROR]" in error_str
    assert "Test error" in error_str
    assert "Details:" in error_str