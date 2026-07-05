"""Tests for MIIE CLI display module."""

import re
import pytest
from io import StringIO
from unittest.mock import patch

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


from miie.cli.display import (
    console,
    print_banner,
    print_footer,
    print_section,
    print_kv,
    make_table,
    add_metric_row,
    add_detector_row,
    info_panel,
    success_panel,
    error_panel,
    warning_panel,
    print_score,
    print_pipeline_stage,
    print_detection_summary,
)


class TestPrintBanner:
    def test_print_banner_outputs_version(self, capsys):
        print_banner("1.5.0")
        captured = capsys.readouterr()
        assert "1.5.0" in captured.out

    def test_print_banner_with_subtitle(self, capsys):
        print_banner("1.5.0", "Test Subtitle")
        captured = capsys.readouterr()
        assert "Test Subtitle" in captured.out


class TestPrintFooter:
    def test_print_footer_default(self, capsys):
        print_footer()
        captured = capsys.readouterr()
        assert "Analysis Complete" in captured.out

    def test_print_footer_custom(self, capsys):
        print_footer("Custom Message")
        captured = capsys.readouterr()
        assert "Custom Message" in captured.out


class TestPrintSection:
    def test_print_section(self, capsys):
        print_section("Test Section")
        captured = capsys.readouterr()
        assert "Test Section" in captured.out


class TestPrintKv:
    def test_print_kv(self, capsys):
        print_kv("Key", "Value")
        captured = capsys.readouterr()
        assert "Key" in captured.out
        assert "Value" in captured.out


class TestMakeTable:
    def test_make_table(self):
        table = make_table("Test Table")
        assert table is not None


class TestAddMetricRow:
    def test_add_metric_row_ok(self):
        table = make_table()
        add_metric_row(table, "M-01", "Test Metric", 0.5, "ok")
        assert len(table.rows) == 1

    def test_add_metric_row_error(self):
        table = make_table()
        add_metric_row(table, "M-01", "Test Metric", None, "error")
        assert len(table.rows) == 1


class TestAddDetectorRow:
    def test_add_detector_row_clear(self):
        table = make_table()
        add_detector_row(table, "D-01", "Test Detector", False)
        assert len(table.rows) == 1

    def test_add_detector_row_detected(self):
        table = make_table()
        add_detector_row(table, "D-01", "Test Detector", True)
        assert len(table.rows) == 1

    def test_add_detector_row_skip(self):
        table = make_table()
        add_detector_row(table, "D-01", "Test Detector", None)
        assert len(table.rows) == 1


class TestPanels:
    def test_info_panel(self, capsys):
        info_panel("Title", "Content")
        captured = capsys.readouterr()
        assert "Title" in captured.out

    def test_success_panel(self, capsys):
        success_panel("Title", "Content")
        captured = capsys.readouterr()
        assert "Title" in captured.out

    def test_error_panel(self, capsys):
        error_panel("Title", "Content")
        captured = capsys.readouterr()
        assert "Title" in captured.out

    def test_warning_panel(self, capsys):
        warning_panel("Title", "Content")
        captured = capsys.readouterr()
        assert "Title" in captured.out


class TestPrintScore:
    def test_print_score_high(self, capsys):
        print_score("Test", 0.95)
        captured = capsys.readouterr()
        assert "0.950" in captured.out
        assert "Very High" in captured.out

    def test_print_score_low(self, capsys):
        print_score("Test", 0.3)
        captured = capsys.readouterr()
        assert "0.300" in captured.out
        assert "Low" in captured.out


class TestPrintPipelineStage:
    def test_running(self, capsys):
        print_pipeline_stage(1, 7, "Test Stage", "running")
        captured = capsys.readouterr()
        output = strip_ansi(captured.out)
        assert "1/7" in output
        assert "Test Stage" in output

    def test_done(self, capsys):
        print_pipeline_stage(1, 7, "Test Stage", "done", elapsed=1.5)
        captured = capsys.readouterr()
        output = strip_ansi(captured.out)
        assert "1.5s" in output


class TestPrintDetectionSummary:
    def test_all_clear(self, capsys):
        outputs = {
            "D-01": {"drift_detected": False},
            "D-02": {"breakdown_detected": False},
            "D-03": {"compression_detected": False},
        }
        print_detection_summary(outputs)
        captured = capsys.readouterr()
        assert "CLEAR" in captured.out

    def test_detected(self, capsys):
        outputs = {
            "D-01": {"drift_detected": True},
            "D-02": {"breakdown_detected": False},
            "D-03": {"compression_detected": False},
        }
        print_detection_summary(outputs)
        captured = capsys.readouterr()
        assert "DETECTED" in captured.out
