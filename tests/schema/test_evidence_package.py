"""
Tests for EvidencePackage schema validation.
"""

import datetime

import pytest

from miie.schemas.models import (
    ConfidenceScore,
    DetectorResults,
    EvidencePackage,
    IntegrityScore,
    Provenance,
    ScorePackage,
    WindowDefinition,
)
from miie.schemas.serialization import json_dumps, json_loads


def test_evidence_package_creation():
    """Test creating a valid EvidencePackage with mock data."""
    evidence = EvidencePackage(
        provenance=Provenance(
            miie_version="1.0.0",
            config_hash="abc123",
            timestamp=datetime.datetime(2020, 6, 15, 10, 30, 0, tzinfo=datetime.timezone.utc).isoformat(),
            seed=42,
            platform="linux-x86_64",
            python_version="3.10.0",
            dependency_hash="def456",
        ),
        windows=[
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2020, 1, 1),
                end_date=datetime.date(2020, 3, 31),
                commits=50,
                strategy="time",
            ),
            WindowDefinition(
                window_id="w02",
                start_date=datetime.date(2020, 4, 1),
                end_date=datetime.date(2020, 6, 30),
                commits=75,
                strategy="time",
            ),
        ],
        metrics={
            "M-02": {  # Commit Frequency
                "w01": [10.0, 12.0, 15.0],
                "w02": None,  # Missing data
            }
        },
        detector_outputs=DetectorResults(
            detector_outputs={
                "D-01": {},  # Mock distributional drift results
                "D-02": {},  # Mock correlation breakdown results
                "D-03": {},  # Mock threshold compression results
            }
        ),
        scores=ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={"M-02": 0.80}, formula_version="1.0.0"),
            confidence=ConfidenceScore(
                overall=0.85,
                factors={"sample_size": 0.9, "data_quality": 0.8},
                band="high",
            ),
            timestamp=datetime.datetime(2020, 6, 15, 10, 30, 0, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        ),
    )

    assert evidence.provenance.miie_version == "1.0.0"
    assert len(evidence.windows) == 2
    assert "M-02" in evidence.metrics
    assert len(evidence.detector_outputs.detector_outputs) == 3
    assert isinstance(evidence.scores, ScorePackage)


def test_evidence_package_invalid_provenance():
    """Test that EvidencePackage rejects invalid provenance."""
    with pytest.raises(ValueError):
        EvidencePackage(
            provenance={
                "miie_version": "1.0.0"
                # Missing required fields
            },
            windows=[],
            metrics={},
            detector_outputs={},
            scores={},
        )


def test_evidence_package_invalid_window():
    """Test that EvidencePackage rejects invalid window structure."""
    with pytest.raises(ValueError):
        EvidencePackage(
            provenance={
                "miie_version": "1.0.0",
                "config_hash": "abc123",
                "timestamp": datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc).isoformat(),
                "seed": 42,
                "platform": "linux-x86_64",
                "python_version": "3.10.0",
                "dependency_hash": "def456",
            },
            windows=[
                {
                    "id": "w01"
                    # Missing required fields: start, end, commits
                }
            ],
            metrics={},
            detector_outputs={},
            scores={},
        )


def test_evidence_package_invalid_metric():
    """Test that EvidencePackage rejects invalid metric IDs."""
    with pytest.raises(ValueError):
        EvidencePackage(
            provenance={
                "miie_version": "1.0.0",
                "config_hash": "abc123",
                "timestamp": datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc).isoformat(),
                "seed": 42,
                "platform": "linux-x86_64",
                "python_version": "3.10.0",
                "dependency_hash": "def456",
            },
            windows=[],
            metrics={"M-08": [100.0]},  # Invalid metric ID
            detector_outputs={},
            scores={},
        )


def test_evidence_package_invalid_detector():
    """Test that EvidencePackage rejects invalid detector IDs."""
    with pytest.raises(ValueError):
        EvidencePackage(
            provenance={
                "miie_version": "1.0.0",
                "config_hash": "abc123",
                "timestamp": datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc).isoformat(),
                "seed": 42,
                "platform": "linux-x86_64",
                "python_version": "3.10.0",
                "dependency_hash": "def456",
            },
            windows=[],
            metrics={},
            detector_outputs={"D-04": {}},  # Invalid detector ID
            scores={},
        )


def test_evidence_package_serialization():
    """Test deterministic serialization of EvidencePackage."""
    evidence = EvidencePackage(
        provenance=Provenance(
            miie_version="1.0.0",
            config_hash="abc123",
            timestamp=datetime.datetime(2020, 6, 15, 10, 30, 0, tzinfo=datetime.timezone.utc).isoformat(),
            seed=42,
            platform="linux-x86_64",
            python_version="3.10.0",
            dependency_hash="def456",
        ),
        windows=[
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2020, 1, 1),
                end_date=datetime.date(2020, 3, 31),
                commits=50,
                strategy="time",
            )
        ],
        metrics={},
        detector_outputs=DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}}),
        scores=ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
            timestamp=datetime.datetime(2020, 6, 15, 10, 30, 0, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        ),
    )

    # Convert to dict for JSON serialization
    evidence_dict = {
        "provenance": {
            "miie_version": evidence.provenance.miie_version,
            "config_hash": evidence.provenance.config_hash,
            "timestamp": evidence.provenance.timestamp,
            "seed": evidence.provenance.seed,
            "platform": evidence.provenance.platform,
            "python_version": evidence.provenance.python_version,
            "dependency_hash": evidence.provenance.dependency_hash,
        },
        "windows": [
            {
                "window_id": w.window_id,
                "start_date": w.start_date.isoformat(),
                "end_date": w.end_date.isoformat(),
                "commits": w.commits,
                "strategy": w.strategy,
            }
            for w in evidence.windows
        ],
        "metrics": evidence.metrics,
        "detector_outputs": evidence.detector_outputs.detector_outputs,
        "scores": {
            "integrity": {
                "overall": evidence.scores.integrity.overall,
                "per_metric": evidence.scores.integrity.per_metric,
            },
            "confidence": {
                "overall": evidence.scores.confidence.overall,
                "factors": evidence.scores.confidence.factors,
            },
        },
        "warnings": evidence.warnings,
    }

    # Serialize
    json_str = json_dumps(evidence_dict)

    # Deserialize
    parsed = json_loads(json_str)

    # Should be byte-identical on second serialization
    json_str2 = json_dumps(parsed)
    assert json_str == json_str2


def test_evidence_package_empty():
    """Test EvidencePackage with minimal valid data."""
    evidence = EvidencePackage(
        provenance=Provenance(
            miie_version="1.0.0",
            config_hash="abc123",
            timestamp=datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc).isoformat(),
            seed=42,
            platform="linux-x86_64",
            python_version="3.10.0",
            dependency_hash="def456",
        ),
        windows=[],
        metrics={},
        detector_outputs=DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}}),
        scores=ScorePackage(
            integrity=IntegrityScore(overall=0.0, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.0, factors={}, band=None),
            timestamp=datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        ),
    )

    assert len(evidence.windows) == 0
    assert len(evidence.metrics) == 0
    assert len(evidence.detector_outputs.detector_outputs) == 3
