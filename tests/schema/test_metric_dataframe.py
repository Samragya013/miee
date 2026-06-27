"""
Tests for MetricDataFrame schema validation.
"""

import datetime

import pytest

from miie.schemas.models import MetricDataFrame
from miie.schemas.serialization import json_dumps, json_loads


def test_metric_dataframe_creation():
    """Test creating a valid MetricDataFrame."""
    mdf = MetricDataFrame(
        repo_id="repo_001",
        run_id="run_001",
        timestamp=datetime.datetime(2020, 6, 15, 10, 30, 0, tzinfo=datetime.timezone.utc),
        metrics={
            "M-01": {  # Code Coverage
                "w01": [80.0, 82.5, 85.0],
                "w02": [87.0, 88.0, 90.0],
            },
            "M-02": {  # Commit Frequency
                "w01": [10.0, 12.0, 15.0],
                "w02": None,  # Missing data
            },
        },
    )

    assert mdf.repo_id == "repo_001"
    assert mdf.run_id == "run_001"
    assert len(mdf.metrics) == 2
    assert "M-01" in mdf.metrics
    assert "M-02" in mdf.metrics


def test_metric_dataframe_invalid_metric():
    """Test that MetricDataFrame rejects invalid metric IDs."""
    with pytest.raises(ValueError):
        MetricDataFrame(
            repo_id="repo_001",
            run_id="run_001",
            timestamp=datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc),
            metrics={"M-08": [100.0]},  # Invalid metric ID
        )


def test_metric_dataframe_valid_metrics():
    """Test that MetricDataFrame accepts all valid metric IDs."""
    valid_metrics = {f"M-{i:02d}" for i in range(1, 8)}  # M-01 through M-07
    metrics_dict = {metric_id: {"w01": [1.0, 2.0, 3.0]} for metric_id in valid_metrics}

    # Should not raise an exception
    mdf = MetricDataFrame(
        repo_id="repo_001",
        run_id="run_001",
        timestamp=datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc),
        metrics=metrics_dict,
    )

    assert len(mdf.metrics) == 7


def test_metric_dataframe_serialization():
    """Test deterministic serialization of MetricDataFrame."""
    mdf = MetricDataFrame(
        repo_id="repo_001",
        run_id="run_001",
        timestamp=datetime.datetime(2020, 6, 15, 10, 30, 0, tzinfo=datetime.timezone.utc),
        metrics={
            "M-01": {
                "w01": [80.0, 82.5, None],  # None represents missing data
                "w02": [87.0, 88.0, 90.0],
            }
        },
    )

    # Convert to dict for JSON serialization
    mdf_dict = {
        "repo_id": mdf.repo_id,
        "run_id": mdf.run_id,
        "timestamp": mdf.timestamp.isoformat(),
        "metrics": mdf.metrics,
    }

    # Serialize
    json_str = json_dumps(mdf_dict)

    # Deserialize
    parsed = json_loads(json_str)

    # Should be byte-identical on second serialization
    json_str2 = json_dumps(parsed)
    assert json_str == json_str2


def test_metric_dataframe_missing_data_handling():
    """Test that MetricDataFrame properly handles missing data (null values)."""
    mdf = MetricDataFrame(
        repo_id="repo_001",
        run_id="run_001",
        timestamp=datetime.datetime(2020, 6, 15, tzinfo=datetime.timezone.utc),
        metrics={
            "M-02": {  # Commit Frequency
                "w01": [10.0, 12.0, None],  # Missing data represented as None
                "w02": None,  # Entire window missing
            }
        },
    )

    assert mdf.metrics["M-02"]["w01"] == [10.0, 12.0, None]
    assert mdf.metrics["M-02"]["w02"] is None
