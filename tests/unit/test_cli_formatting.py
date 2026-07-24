"""Tests for MIIE CLI formatting module."""

import json

from miie.cli.formatting import (
    generate_csv_metrics,
    generate_csv_scores,
    generate_html_report,
    generate_markdown_report,
    write_reports,
)


class TestGenerateMarkdownReport:
    def test_returns_string(self):
        result = generate_markdown_report(
            repo_name="test-repo",
            integrity_score=0.95,
            confidence_score=0.7,
            detector_outputs={"D-01": {"drift_detected": False}},
            metric_names=["M-01", "M-02"],
            window_count=5,
            total_commits=100,
            contributor_count=10,
        )
        assert isinstance(result, str)
        assert "0.950" in result
        assert "0.700" in result


class TestGenerateCsvScores:
    def test_returns_string(self):
        result = generate_csv_scores(
            repo_name="test-repo",
            integrity_score=0.95,
            confidence_score=0.7,
            detector_outputs={"D-01": {"drift_detected": False}},
        )
        assert isinstance(result, str)
        assert "0.95" in result
        assert "0.7" in result


class TestGenerateCsvMetrics:
    def test_returns_string(self):
        result = generate_csv_metrics(
            metric_names=["M-01", "M-02"],
            metric_values={"M-01": {"status": "ok"}, "M-02": {"status": "error"}},
        )
        assert isinstance(result, str)
        assert "M-01" in result
        assert "M-02" in result


class TestGenerateHtmlReport:
    def test_returns_string(self):
        result = generate_html_report(
            repo_name="test-repo",
            integrity_score=0.95,
            confidence_score=0.7,
            detector_outputs={"D-01": {"drift_detected": False}},
            metric_names=["M-01"],
            window_count=5,
        )
        assert isinstance(result, str)
        assert "0.950" in result
        assert "<!DOCTYPE html>" in result


class TestWriteReports:
    def test_writes_all_formats(self, tmp_path):
        result = write_reports(
            output_dir=str(tmp_path),
            formats=["json", "markdown", "csv_scores", "html"],
            repo_name="test-repo",
            integrity_score=0.95,
            confidence_score=0.7,
            detector_outputs={"D-01": {"drift_detected": False}},
            metric_names=["M-01"],
            window_count=5,
            total_commits=100,
            contributor_count=10,
        )
        assert len(result) > 0
        for path in result.values():
            assert path.exists()

    def test_writes_json(self, tmp_path):
        result = write_reports(
            output_dir=str(tmp_path),
            formats=["json"],
            repo_name="test-repo",
            integrity_score=0.95,
            confidence_score=0.7,
            detector_outputs={},
            metric_names=[],
            window_count=0,
            total_commits=0,
            contributor_count=0,
            json_data={"integrity_score": 0.95, "confidence_score": 0.7},
        )
        assert "json" in result
        data = json.loads(result["json"].read_text(encoding="utf-8"))
        assert data["integrity_score"] == 0.95

    def test_invalid_format_skipped(self, tmp_path):
        result = write_reports(
            output_dir=str(tmp_path),
            formats=["invalid_format"],
            repo_name="test-repo",
            integrity_score=0.95,
            confidence_score=0.7,
            detector_outputs={},
            metric_names=[],
            window_count=0,
            total_commits=0,
            contributor_count=0,
        )
        assert len(result) == 0
