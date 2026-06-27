"""
Tests for the metric registry.
"""

import pytest

from miie.schemas.metric_registry import (
    METRIC_REGISTRY,
    MetricInfo,
    validate_metric_ids,
)


def test_metric_registry_contains_frozen_metrics():
    """Test that the metric registry contains exactly the frozen metrics M-01 through M-07."""
    expected_metric_ids = {f"M-{i:02d}" for i in range(1, 8)}  # M-01 through M-07
    actual_metric_ids = {metric.metric_id for metric in METRIC_REGISTRY}
    assert actual_metric_ids == expected_metric_ids
    assert len(METRIC_REGISTRY) == 7

    # Verify we have the right metric info
    metric_dict = {metric.metric_id: metric for metric in METRIC_REGISTRY}
    assert metric_dict["M-02"].name == "Commit Frequency"
    assert metric_dict["M-02"].extraction_status == "implemented"
    assert metric_dict["M-01"].extraction_status == "implemented"


def test_metric_registry_is_frozen():
    """Test that the metric registry is immutable (frozenset)."""
    assert isinstance(METRIC_REGISTRY, frozenset)
    # Attempt to modify should fail
    with pytest.raises(AttributeError):
        METRIC_REGISTRY.add(
            MetricInfo(
                metric_id="M-08",
                name="Test Metric",
                description="Test description",
                extraction_status="unavailable",
            )
        )


def test_validate_metric_ids_valid():
    """Test that valid metric IDs pass validation."""
    # These should not raise an exception
    validate_metric_ids(["M-01"])
    validate_metric_ids(["M-02", "M-06"])
    validate_metric_ids(["M-01", "M-03", "M-05", "M-07"])
    validate_metric_ids([metric.metric_id for metric in METRIC_REGISTRY])  # All metrics


def test_validate_metric_ids_invalid_single():
    """Test that invalid single metric ID raises ValueError."""
    with pytest.raises(ValueError, match="Invalid metric IDs: \['M-08'\]"):
        validate_metric_ids(["M-08"])

    with pytest.raises(ValueError, match="Invalid metric IDs: \['M-00'\]"):
        validate_metric_ids(["M-00"])

    with pytest.raises(ValueError, match="Invalid metric IDs: \['M-99'\]"):
        validate_metric_ids(["M-99"])


def test_validate_metric_ids_invalid_multiple():
    """Test that invalid multiple metric IDs raise ValueError with all invalid IDs listed."""
    with pytest.raises(ValueError) as exc_info:
        validate_metric_ids(["M-01", "M-08", "M-02", "M-99"])

    error_msg = str(exc_info.value)
    assert "Invalid metric IDs:" in error_msg
    assert "M-08" in error_msg
    assert "M-99" in error_msg
    # The error message includes the full frozen registry, so valid metrics will appear there
    # We should only check that the invalid metrics are mentioned
    assert "M-08" in error_msg
    assert "M-99" in error_msg


def test_validate_metric_ids_empty_list():
    """Test that empty metric list passes validation (no invalid IDs)."""
    # This should not raise an exception
    validate_metric_ids([])


def test_validate_metric_ids_case_sensitive():
    """Test that metric ID validation is case-sensitive."""
    with pytest.raises(ValueError, match="Invalid metric IDs: \['m-01'\]"):
        validate_metric_ids(["m-01"])  # lowercase

    with pytest.raises(ValueError, match="Invalid metric IDs: \['m-01', 'M-08'\]"):
        validate_metric_ids(["m-01", "M-08"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
