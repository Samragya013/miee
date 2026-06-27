"""Unit tests for ReportGenerator implementation."""

import json
import tempfile
from pathlib import Path

from miie.processing.reporting.engine import ReportGenerator
from miie.schemas.models import ReportOutput


def test_report_generator_creation():
    """Test creating a ReportGenerator instance."""
    generator = ReportGenerator()
    assert isinstance(generator, ReportGenerator)


def test_report_generator_generate_json_format():
    """Test ReportGenerator.generate with JSON output format."""
    generator = ReportGenerator()
    analysis_result = {
        "integrity_score": 0.85,
        "confidence_score": 0.92,
        "metrics_processed": 5,
        "detectors_used": ["D-01", "D-02", "D-03"],
    }
    output_formats = ["json"]

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        report_output = generator.generate(analysis_result, output_formats, output_dir)

        assert isinstance(report_output, ReportOutput)
        assert hasattr(report_output, "report_paths")
        assert isinstance(report_output.report_paths, dict)
        assert "json" in report_output.report_paths

        json_file = report_output.report_paths["json"]
        assert json_file.exists()
        assert json_file.suffix == ".json"

        # Verify JSON content
        with open(json_file, "r") as f:
            data = json.load(f)
            assert "metadata" in data
            assert "analysis_result" in data
            assert data["analysis_result"]["integrity_score"] == 0.85
            assert data["analysis_result"]["confidence_score"] == 0.92


def test_report_generator_generate_multiple_formats():
    """Test ReportGenerator.generate with multiple output formats."""
    generator = ReportGenerator()
    analysis_result = {"test_metric": 42.5, "status": "completed"}
    output_formats = ["json", "md", "txt"]

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        report_output = generator.generate(analysis_result, output_formats, output_dir)

        assert isinstance(report_output, ReportOutput)
        assert "json" in report_output.report_paths
        assert "markdown" in report_output.report_paths
        assert "text" in report_output.report_paths

        # Verify all files exist
        for format_type, file_path in report_output.report_paths.items():
            assert file_path.exists(), f"File for format {format_type} does not exist"

        # Verify JSON content
        json_path = report_output.report_paths["json"]
        with open(json_path, "r") as f:
            data = json.load(f)
            assert data["analysis_result"]["test_metric"] == 42.5

        # Verify markdown content
        md_path = report_output.report_paths["markdown"]
        with open(md_path, "r") as f:
            content = f.read()
            assert "# MIIE Analysis Report" in content
            assert "test_metric" in content
            assert "42.5" in content

        # Verify text content
        txt_path = report_output.report_paths["text"]
        with open(txt_path, "r") as f:
            content = f.read()
            assert "MIIE Analysis Report" in content
            assert "test_metric" in content
            assert "42.5" in content


def test_report_generator_generate_csv_format():
    """Test ReportGenerator.generate with CSV output format."""
    generator = ReportGenerator()
    analysis_result = {
        "metric_a": 10.5,
        "metric_b": 20.3,
        "nested": {"sub_metric": 5.0},
    }
    output_formats = ["csv"]

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        report_output = generator.generate(analysis_result, output_formats, output_dir)

        assert "csv" in report_output.report_paths
        csv_file = report_output.report_paths["csv"]
        assert csv_file.exists()
        assert csv_file.suffix == ".csv"

        # Verify CSV content (basic check)
        with open(csv_file, "r") as f:
            content = f.read()
            assert "metric_a" in content
            assert "10.5" in content
            assert "metric_b" in content
            assert "20.3" in content


def test_report_generator_handles_empty_analysis_result():
    """Test ReportGenerator.generate with empty analysis result."""
    generator = ReportGenerator()
    analysis_result = {}
    output_formats = ["json"]

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        report_output = generator.generate(analysis_result, output_formats, output_dir)

        assert isinstance(report_output, ReportOutput)
        assert "json" in report_output.report_paths
        json_file = report_output.report_paths["json"]
        assert json_file.exists()

        # Verify it contains metadata even with empty analysis
        with open(json_file, "r") as f:
            data = json.load(f)
            assert "metadata" in data
            assert "analysis_result" in data
            assert data["analysis_result"] == {}


def test_report_generator_handles_unknown_format():
    """Test ReportGenerator.generate handles unknown formats gracefully (defaults to JSON)."""
    generator = ReportGenerator()
    analysis_result = {"test": "value"}
    output_formats = ["unknown_format", "json"]  # Mix of unknown and known

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        report_output = generator.generate(analysis_result, output_formats, output_dir)

        # Should have entries for both formats (unknown_format will be treated as JSON)
        assert "unknown_format" in report_output.report_paths
        assert "json" in report_output.report_paths

        # Both should point to existing files
        assert report_output.report_paths["unknown_format"].exists()
        assert report_output.report_paths["json"].exists()


def test_report_generator_creates_output_directory():
    """Test ReportGenerator.generate creates output directory if it doesn't exist."""
    generator = ReportGenerator()
    analysis_result = {"test": "data"}
    output_formats = ["json"]

    with tempfile.TemporaryDirectory() as temp_dir:
        # Use a subdirectory that doesn't exist yet
        output_dir = Path(temp_dir) / "new_subdir"
        assert not output_dir.exists()

        report_output = generator.generate(analysis_result, output_formats, output_dir)

        # Directory should now exist
        assert output_dir.exists()
        assert output_dir.is_dir()

        # And should contain the report file
        assert "json" in report_output.report_paths
        assert report_output.report_paths["json"].exists()
