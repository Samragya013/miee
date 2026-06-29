"""Ground Truth Dataset Module for MIIE Benchmark Validation.

Loads, validates, and evaluates ground truth data for benchmark scoring.
Ground truth defines expected anomaly types, severity ranges, and metric
thresholds for each benchmark candidate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class GroundTruthEntry:
    """A single ground truth annotation for a benchmark candidate."""

    candidate_id: str
    anomaly_type: str
    severity_min: float = 0.0
    severity_max: float = 1.0
    expected_detectors: List[str] = field(default_factory=list)
    expected_metrics: List[str] = field(default_factory=list)
    notes: str = ""

    def validate_severity_range(self) -> bool:
        """Check that severity_min <= severity_max and both are in [0, 1]."""
        if not (0.0 <= self.severity_min <= 1.0):
            return False
        if not (0.0 <= self.severity_max <= 1.0):
            return False
        return self.severity_min <= self.severity_max

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "candidate_id": self.candidate_id,
            "anomaly_type": self.anomaly_type,
            "severity_min": self.severity_min,
            "severity_max": self.severity_max,
            "expected_detectors": self.expected_detectors,
            "expected_metrics": self.expected_metrics,
            "notes": self.notes,
        }


@dataclass
class GroundTruthDataset:
    """Collection of ground truth entries for benchmark evaluation."""

    entries: List[GroundTruthEntry] = field(default_factory=list)
    version: str = "1.0.0"

    @classmethod
    def from_json(cls, path: str | Path) -> GroundTruthDataset:
        """Load ground truth dataset from a JSON file.

        Args:
            path: Path to ground truth JSON file.

        Returns:
            GroundTruthDataset instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the JSON structure is invalid.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Ground truth file not found: {p}")

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict) or "entries" not in data:
            raise ValueError("Ground truth JSON must contain an 'entries' key")

        entries = []
        for raw in data["entries"]:
            entry = GroundTruthEntry(
                candidate_id=raw["candidate_id"],
                anomaly_type=raw.get("anomaly_type", "unknown"),
                severity_min=raw.get("severity_min", 0.0),
                severity_max=raw.get("severity_max", 1.0),
                expected_detectors=raw.get("expected_detectors", []),
                expected_metrics=raw.get("expected_metrics", []),
                notes=raw.get("notes", ""),
            )
            entries.append(entry)

        return cls(entries=entries, version=data.get("version", "1.0.0"))

    def save(self, path: str | Path) -> None:
        """Save ground truth dataset to a JSON file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": self.version,
            "entries": [e.to_dict() for e in self.entries],
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_entry(self, candidate_id: str) -> Optional[GroundTruthEntry]:
        """Look up a ground truth entry by candidate ID."""
        for entry in self.entries:
            if entry.candidate_id == candidate_id:
                return entry
        return None

    def validate(self) -> List[str]:
        """Validate all entries. Returns a list of error strings (empty = valid)."""
        errors: List[str] = []
        seen_ids: set[str] = set()
        for entry in self.entries:
            if entry.candidate_id in seen_ids:
                errors.append(f"Duplicate candidate_id: {entry.candidate_id}")
            seen_ids.add(entry.candidate_id)
            if not entry.validate_severity_range():
                errors.append(
                    f"Invalid severity range for {entry.candidate_id}: " f"[{entry.severity_min}, {entry.severity_max}]"
                )
        return errors

    def evaluate_candidate(
        self,
        candidate_id: str,
        detected_anomaly_type: str,
        detected_severity: float,
    ) -> Dict[str, Any]:
        """Evaluate a single candidate's detection against ground truth.

        Returns:
            Dict with keys: tp (bool), fp (bool), fn (bool),
            severity_in_range (bool), score (float 0-1).
        """
        gt = self.get_entry(candidate_id)
        if gt is None:
            return {
                "tp": False,
                "fp": True,
                "fn": False,
                "severity_in_range": False,
                "score": 0.0,
                "error": "no_ground_truth",
            }

        type_match = detected_anomaly_type == gt.anomaly_type
        severity_in_range = gt.severity_min <= detected_severity <= gt.severity_max

        tp = type_match
        fp = not type_match and detected_anomaly_type != "none"
        fn = not type_match and detected_anomaly_type == "none"

        # Score: type match contributes 0.6, severity range contributes 0.4
        score = (0.6 if type_match else 0.0) + (0.4 if severity_in_range else 0.0)

        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "severity_in_range": severity_in_range,
            "score": score,
        }

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the dataset."""
        anomaly_counts: Dict[str, int] = {}
        for entry in self.entries:
            anomaly_counts[entry.anomaly_type] = anomaly_counts.get(entry.anomaly_type, 0) + 1
        return {
            "version": self.version,
            "total_entries": len(self.entries),
            "anomaly_type_distribution": anomaly_counts,
            "validation_errors": len(self.validate()),
        }
