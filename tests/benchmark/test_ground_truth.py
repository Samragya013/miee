"""Tests for benchmarks/ground_truth/ground_truth.py."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from benchmarks.ground_truth.ground_truth import (
    GroundTruthDataset,
    GroundTruthEntry,
)


class TestGroundTruthEntry:
    """Tests for GroundTruthEntry data class."""

    def test_basic_creation(self):
        entry = GroundTruthEntry(candidate_id="c001", anomaly_type="burst")
        assert entry.candidate_id == "c001"
        assert entry.anomaly_type == "burst"
        assert entry.severity_min == 0.0
        assert entry.severity_max == 1.0
        assert entry.expected_detectors == []
        assert entry.expected_metrics == []

    def test_validate_severity_range_valid(self):
        entry = GroundTruthEntry(candidate_id="c001", anomaly_type="burst",
                                 severity_min=0.2, severity_max=0.8)
        assert entry.validate_severity_range() is True

    def test_validate_severity_range_inverted(self):
        entry = GroundTruthEntry(candidate_id="c001", anomaly_type="burst",
                                 severity_min=0.8, severity_max=0.2)
        assert entry.validate_severity_range() is False

    def test_validate_severity_range_out_of_bounds(self):
        entry = GroundTruthEntry(candidate_id="c001", anomaly_type="burst",
                                 severity_min=-0.1, severity_max=0.5)
        assert entry.validate_severity_range() is False

    def test_to_dict(self):
        entry = GroundTruthEntry(candidate_id="c001", anomaly_type="burst",
                                 severity_min=0.2, severity_max=0.8,
                                 expected_detectors=["d01"],
                                 expected_metrics=["m01"],
                                 notes="test note")
        d = entry.to_dict()
        assert d["candidate_id"] == "c001"
        assert d["anomaly_type"] == "burst"
        assert d["severity_min"] == 0.2
        assert d["severity_max"] == 0.8
        assert d["expected_detectors"] == ["d01"]
        assert d["expected_metrics"] == ["m01"]
        assert d["notes"] == "test note"


class TestGroundTruthDataset:
    """Tests for GroundTruthDataset."""

    def _make_dataset(self, entries=None):
        if entries is None:
            entries = [
                GroundTruthEntry(candidate_id="c001", anomaly_type="burst",
                                 severity_min=0.3, severity_max=0.7),
                GroundTruthEntry(candidate_id="c002", anomaly_type="decline",
                                 severity_min=0.1, severity_max=0.9),
            ]
        return GroundTruthDataset(entries=entries)

    def test_from_json_valid(self, tmp_path):
        data = {
            "version": "1.0.0",
            "entries": [
                {"candidate_id": "c001", "anomaly_type": "burst",
                 "severity_min": 0.3, "severity_max": 0.7},
                {"candidate_id": "c002", "anomaly_type": "decline",
                 "severity_min": 0.1, "severity_max": 0.9},
            ],
        }
        p = tmp_path / "gt.json"
        p.write_text(json.dumps(data), encoding="utf-8")

        ds = GroundTruthDataset.from_json(p)
        assert len(ds.entries) == 2
        assert ds.version == "1.0.0"
        assert ds.entries[0].candidate_id == "c001"

    def test_from_json_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            GroundTruthDataset.from_json("/nonexistent/gt.json")

    def test_from_json_invalid_structure(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text(json.dumps({"not_entries": []}), encoding="utf-8")
        with pytest.raises(ValueError, match="entries"):
            GroundTruthDataset.from_json(p)

    def test_save_and_reload(self, tmp_path):
        ds = self._make_dataset()
        p = tmp_path / "gt_out.json"
        ds.save(p)
        assert p.exists()

        ds2 = GroundTruthDataset.from_json(p)
        assert len(ds2.entries) == 2
        assert ds2.entries[0].anomaly_type == "burst"

    def test_get_entry_found(self):
        ds = self._make_dataset()
        entry = ds.get_entry("c001")
        assert entry is not None
        assert entry.anomaly_type == "burst"

    def test_get_entry_not_found(self):
        ds = self._make_dataset()
        assert ds.get_entry("c999") is None

    def test_validate_no_errors(self):
        ds = self._make_dataset()
        errors = ds.validate()
        assert errors == []

    def test_validate_duplicate_ids(self):
        entries = [
            GroundTruthEntry(candidate_id="c001", anomaly_type="burst"),
            GroundTruthEntry(candidate_id="c001", anomaly_type="decline"),
        ]
        ds = self._make_dataset(entries)
        errors = ds.validate()
        assert len(errors) == 1
        assert "Duplicate" in errors[0]

    def test_validate_invalid_severity(self):
        entries = [
            GroundTruthEntry(candidate_id="c001", anomaly_type="burst",
                             severity_min=0.9, severity_max=0.1),
        ]
        ds = self._make_dataset(entries)
        errors = ds.validate()
        assert len(errors) == 1
        assert "severity" in errors[0].lower()

    def test_evaluate_candidate_tp(self):
        ds = self._make_dataset()
        result = ds.evaluate_candidate("c001", "burst", 0.5)
        assert result["tp"] is True
        assert result["fp"] is False
        assert result["fn"] is False
        assert result["severity_in_range"] is True
        assert result["score"] == 1.0  # 0.6 type + 0.4 severity

    def test_evaluate_candidate_type_mismatch(self):
        ds = self._make_dataset()
        result = ds.evaluate_candidate("c001", "decline", 0.5)
        assert result["tp"] is False
        assert result["fp"] is True
        assert result["severity_in_range"] is True
        assert result["score"] == 0.4  # severity only

    def test_evaluate_candidate_no_ground_truth(self):
        ds = self._make_dataset()
        result = ds.evaluate_candidate("c999", "burst", 0.5)
        assert result["fp"] is True
        assert result["error"] == "no_ground_truth"
        assert result["score"] == 0.0

    def test_summary(self):
        ds = self._make_dataset()
        s = ds.summary()
        assert s["total_entries"] == 2
        assert s["version"] == "1.0.0"
        assert s["anomaly_type_distribution"]["burst"] == 1
        assert s["anomaly_type_distribution"]["decline"] == 1
