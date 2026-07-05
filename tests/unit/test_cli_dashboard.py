"""Tests for MIIE CLI dashboard module."""

import pytest

from miie.cli.dashboard import (
    display_dashboard,
    display_compact_dashboard,
    display_verdict,
    _score_label,
)


class TestScoreLabel:
    def test_very_high(self):
        assert _score_label(0.95) == "Very High"

    def test_high(self):
        assert _score_label(0.75) == "High"

    def test_moderate(self):
        assert _score_label(0.55) == "Moderate"

    def test_low(self):
        assert _score_label(0.3) == "Low"


class TestDisplayDashboard:
    def test_basic_dashboard(self, capsys):
        detector_outputs = {
            "D-01": {"drift_detected": False},
            "D-02": {"breakdown_detected": False},
            "D-03": {"compression_detected": False},
        }
        display_dashboard(
            integrity_score=0.95,
            confidence_score=0.7,
            detector_outputs=detector_outputs,
            metric_names=["M-01", "M-02"],
            window_count=5,
            total_commits=100,
            contributor_count=10,
        )
        captured = capsys.readouterr()
        assert "0.950" in captured.out
        assert "0.700" in captured.out


class TestDisplayCompactDashboard:
    def test_compact_all_clear(self, capsys):
        detector_outputs = {
            "D-01": {"drift_detected": False},
            "D-02": {"breakdown_detected": False},
            "D-03": {"compression_detected": False},
        }
        display_compact_dashboard(
            integrity_score=1.0,
            confidence_score=0.8,
            detector_outputs=detector_outputs,
            window_count=5,
        )
        captured = capsys.readouterr()
        assert "ALL CLEAR" in captured.out

    def test_compact_anomalies(self, capsys):
        detector_outputs = {
            "D-01": {"drift_detected": True},
            "D-02": {"breakdown_detected": False},
            "D-03": {"compression_detected": False},
        }
        display_compact_dashboard(
            integrity_score=0.8,
            confidence_score=0.6,
            detector_outputs=detector_outputs,
            window_count=5,
        )
        captured = capsys.readouterr()
        assert "ANOMALIES DETECTED" in captured.out


class TestDisplayVerdict:
    def test_verdict_no_anomalies(self, capsys):
        display_verdict(
            integrity_score=0.95,
            confidence_score=0.8,
            triggered_count=0,
            failed_detectors=[],
        )
        captured = capsys.readouterr()
        assert "Very High" in captured.out or "High" in captured.out

    def test_verdict_with_anomalies(self, capsys):
        display_verdict(
            integrity_score=0.7,
            confidence_score=0.5,
            triggered_count=2,
            failed_detectors=["D-03"],
        )
        captured = capsys.readouterr()
        assert "Moderate" in captured.out or "Low" in captured.out
