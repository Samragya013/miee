"""
Unit tests for window segmentation engine.
"""

import datetime
from datetime import timezone
import pytest

from miie.processing.segmentation import WindowSegmentationEngine, MockSegmentationEngine
from miie.schemas.models import WindowDefinition, MetricDataFrame
from miie.contracts.errors import ValidationError


def create_mock_metric_dataframe(repo_id="repo_001", run_id="run_001", timestamp=None, m02_data=None):
    """Helper to create a mock MetricDataFrame for testing."""
    if timestamp is None:
        timestamp = datetime.datetime(2023, 6, 15, 10, 30, 0, tzinfo=timezone.utc)

    metrics = {}
    if m02_data is not None:
        metrics["M-02"] = m02_data

    return MetricDataFrame(
        repo_id=repo_id,
        run_id=run_id,
        timestamp=timestamp,
        metrics=metrics
    )


def test_time_window_basic():
    """Verify time-based window creation."""
    engine = WindowSegmentationEngine()
    mdf = create_mock_metric_dataframe(m02_data={"w01": [10.0, 12.0, 15.0]})

    windows = engine.segment(
        metric_dataframe=mdf,
        strategy="time",
        size=7  # 7 days per window
    )

    # Currently returns a single window for the entire data
    assert len(windows) == 1
    window = windows[0]
    assert isinstance(window, WindowDefinition)
    assert window.strategy == "time"
    assert window.size_config == {"size": 7}
    # The commit count should be derived from M-02 data
    # In the current implementation, it sums the M-02 values for the window
    # We have [10.0, 12.0, 15.0] -> sum = 37.0
    assert window.commits == 37


def test_commit_window_basic():
    """Verify commit-based window creation."""
    engine = WindowSegmentationEngine()
    mdf = create_mock_metric_dataframe(m02_data={"w01": [5.0, 10.0, 3.0]})

    windows = engine.segment(
        metric_dataframe=mdf,
        strategy="commit",
        size=10  # 10 commits per window
    )

    assert len(windows) == 1
    window = windows[0]
    assert window.strategy == "commit"
    assert window.size_config == {"size": 10}
    # Sum of M-02 values: 5+10+3 = 18
    assert window.commits == 18


def test_custom_boundaries_validation():
    """Verify user-defined boundary handling."""
    engine = WindowSegmentationEngine()
    mdf = create_mock_metric_dataframe()

    # Define custom boundaries
    start1 = datetime.datetime(2023, 1, 1, tzinfo=timezone.utc)
    end1 = datetime.datetime(2023, 1, 7, tzinfo=timezone.utc)
    start2 = datetime.datetime(2023, 1, 8, tzinfo=timezone.utc)
    end2 = datetime.datetime(2023, 1, 14, tzinfo=timezone.utc)
    custom_boundaries = [(start1, end1), (start2, end2)]

    windows = engine.segment(
        metric_dataframe=mdf,
        strategy="custom",
        size=5,  # size is ignored for custom? but we pass it
        custom_boundaries=custom_boundaries
    )

    assert len(windows) == 2
    # First window
    assert windows[0].window_id == "w00"
    assert windows[0].start_date == start1.date()
    assert windows[0].end_date == end1.date()
    assert windows[0].strategy == "custom"
    assert windows[0].size_config == {"size": 5, "boundary_index": 0}
    # Second window
    assert windows[1].window_id == "w01"
    assert windows[1].start_date == start2.date()
    assert windows[1].end_date == end2.date()
    assert windows[1].strategy == "custom"
    assert windows[1].size_config == {"size": 5, "boundary_index": 1}


def test_empty_data_handling():
    """Verify empty metric data returns empty window list."""
    engine = WindowSegmentationEngine()
    # Create a MetricDataFrame with no metrics
    mdf = MetricDataFrame(
        repo_id="repo_001",
        run_id="run_001",
        timestamp=datetime.datetime(2023, 6, 15, tzinfo=timezone.utc),
        metrics={}  # empty metrics
    )

    windows = engine.segment(
        metric_dataframe=mdf,
        strategy="time",
        size=7
    )

    # Currently, the engine returns a single window even with empty data?
    # Let's check the implementation: it sets total_commits to 1 if zero.
    # So we expect one window.
    # However, the test says "empty metric data returns empty window list".
    # We'll adjust the test to match the expected behavior from the spec.
    # But note: the current implementation does not return empty list.
    # We are writing the test as per spec, so we expect empty list.
    # However, we must follow the existing code? The spec says to verify.
    # We'll write the test expecting empty list and note that the implementation may need to change.
    # For now, we'll assert empty list as per spec.
    assert len(windows) == 0


def test_window_ordering():
    """Verify windows are non-overlapping and ordered chronologically."""
    engine = WindowSegmentationEngine()
    mdf = create_mock_metric_dataframe(m02_data={"w01": [1.0, 2.0, 3.0]})

    # Use custom strategy to create multiple windows
    start1 = datetime.datetime(2023, 1, 1, tzinfo=timezone.utc)
    end1 = datetime.datetime(2023, 1, 5, tzinfo=timezone.utc)
    start2 = datetime.datetime(2023, 1, 6, tzinfo=timezone.utc)
    end2 = datetime.datetime(2023, 1, 10, tzinfo=timezone.utc)
    start3 = datetime.datetime(2023, 1, 11, tzinfo=timezone.utc)
    end3 = datetime.datetime(2023, 1, 15, tzinfo=timezone.utc)
    custom_boundaries = [(start1, end1), (start2, end2), (start3, end3)]

    windows = engine.segment(
        metric_dataframe=mdf,
        strategy="custom",
        size=3,
        custom_boundaries=custom_boundaries
    )

    assert len(windows) == 3
    # Check chronological order
    assert windows[0].start_date <= windows[0].end_date
    assert windows[1].start_date <= windows[1].end_date
    assert windows[2].start_date <= windows[2].end_date
    # Check non-overlapping and consecutive
    assert windows[0].end_date < windows[1].start_date
    assert windows[1].end_date < windows[2].start_date
    # Check IDs are sequential
    assert windows[0].window_id == "w00"
    assert windows[1].window_id == "w01"
    assert windows[2].window_id == "w02"


def test_window_id_determinism():
    """Verify window IDs are stable across runs."""
    engine = WindowSegmentationEngine()
    mdf = create_mock_metric_dataframe(m02_data={"w01": [4.0, 5.0, 6.0]})

    # Run segmentation multiple times with same inputs
    windows1 = engine.segment(
        metric_dataframe=mdf,
        strategy="time",
        size=7
    )
    windows2 = engine.segment(
        metric_dataframe=mdf,
        strategy="time",
        size=7
    )

    # IDs should be the same
    assert len(windows1) == len(windows2)
    for w1, w2 in zip(windows1, windows2):
        assert w1.window_id == w2.window_id
        # Other fields should be deterministic too
        assert w1.start_date == w2.start_date
        assert w1.end_date == w2.end_date
        assert w1.commits == w2.commits


def test_boundary_overlap_detection():
    """Verify overlapping boundaries raise ValidationError."""
    engine = WindowSegmentationEngine()
    mdf = create_mock_metric_dataframe()

    # Define overlapping boundaries: first window ends after second starts
    start1 = datetime.datetime(2023, 1, 1, tzinfo=timezone.utc)
    end1 = datetime.datetime(2023, 1, 10, tzinfo=timezone.utc)  # ends Jan 10
    start2 = datetime.datetime(2023, 1, 5, tzinfo=timezone.utc)  # starts Jan 5 (overlaps)
    end2 = datetime.datetime(2023, 1, 15, tzinfo=timezone.utc)
    custom_boundaries = [(start1, end1), (start2, end2)]

    with pytest.raises(ValidationError):
        engine.segment(
            metric_dataframe=mdf,
            strategy="custom",
            size=5,
            custom_boundaries=custom_boundaries
        )


def test_commit_count_calculation():
    """Verify commit count calculation from M-02 metric data."""
    engine = WindowSegmentationEngine()
    # Create M-02 data with multiple windows and some None values
    m02_data = {
        "w01": [10.0, None, 20.0],  # sum = 30.0 (None treated as 0?)
        "w02": [5.0, 15.0, 25.0],   # sum = 45.0
        "w03": None                 # entire window None -> sum = 0
    }
    mdf = create_mock_metric_dataframe(m02_data=m02_data)

    windows = engine.segment(
        metric_dataframe=mdf,
        strategy="commit",
        size=100  # large size to get one window
    )

    # Currently, the engine sums all values in all windows for M-02
    # Let's check the implementation: it iterates over window_id, values and sums non-None values.
    # For w01: 10 + 20 = 30 (None skipped)
    # For w02: 5 + 15 + 25 = 45
    # For w03: None -> skipped, so 0
    # Total = 30 + 45 + 0 = 75
    assert len(windows) == 1
    assert windows[0].commits == 75