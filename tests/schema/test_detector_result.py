"""
Tests for DetectorResult schema validation.
"""

import pytest

from miie.schemas.models import DetectorResult
from miie.schemas.serialization import json_dumps, json_loads


def test_detector_result_creation():
    """Test creating a valid DetectorResult with mock data."""
    # Mock detector outputs (structure would be more complex in real implementation)
    detector_result = DetectorResult(
        detector_outputs={
            "D-01": {},  # Distributional Drift Detector
            "D-02": {},  # Correlation Breakdown Detector
            "D-03": {}   # Threshold Compression Detector
        }
    )

    assert len(detector_result.detector_outputs) == 3
    assert "D-01" in detector_result.detector_outputs
    assert "D-02" in detector_result.detector_outputs
    assert "D-03" in detector_result.detector_outputs


def test_detector_result_invalid_detector():
    """Test that DetectorResult rejects invalid detector IDs."""
    with pytest.raises(ValueError):
        DetectorResult(
            detector_outputs={
                "D-01": {},  # Valid
                "D-04": {}   # Invalid - V1 only has D-01 through D-03
            }
        )


def test_detector_result_valid_detectors():
    """Test that DetectorResult accepts all valid detector IDs."""
    valid_detectors = {f"D-{i:02d}" for i in range(1, 4)}  # D-01 through D-03
    detector_outputs = {detector_id: {} for detector_id in valid_detectors}

    # Should not raise an exception
    detector_result = DetectorResult(detector_outputs=detector_outputs)

    assert len(detector_result.detector_outputs) == 3


def test_detector_result_serialization():
    """Test deterministic serialization of DetectorResult."""
    detector_result = DetectorResult(
        detector_outputs={
            "D-01": {"sample_key": "sample_value"},
            "D-02": {"another_key": 42},
            "D-03": {}
        }
    )

    # Convert to dict for JSON serialization
    result_dict = {
        "detector_outputs": detector_result.detector_outputs
    }

    # Serialize
    json_str = json_dumps(result_dict)

    # Deserialize
    parsed = json_loads(json_str)

    # Should be byte-identical on second serialization
    json_str2 = json_dumps(parsed)
    assert json_str == json_str2


def test_detector_result_empty_outputs():
    """Test DetectorResult with empty detector outputs."""
    detector_result = DetectorResult(detector_outputs={})

    assert len(detector_result.detector_outputs) == 0