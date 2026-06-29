"""
Comprehensive tests for ObservationWindowBuilder, DetectorAdapter, WindowConfig,
WindowBuilderResult, and DetectorAdapterOutput.

Covers:
  - WindowConfig validation (strategy, window_size, min_observations, max_windows, custom_boundaries)
  - ObservationWindowBuilder all four strategies (temporal, commit_count, hybrid, custom)
  - Determinism, boundary correctness, sequential window IDs
  - Empty collection, single observation, sparse observations
  - max_windows truncation
  - DetectorAdapter.to_metric_dataframe translation
  - DetectorAdapter.to_paired_observations alignment
  - Edge cases: empty windows, missing metrics, single window, overlapping timestamps
  - WindowBuilderResult structure
  - DetectorAdapterOutput structure
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

import pytest

from miie.contracts.errors import DetectorAdapterError, WindowBuilderError
from miie.processing.observation.adapter import DetectorAdapter
from miie.processing.observation.models import (
    DetectorAdapterOutput,
    Observation,
    ObservationCollection,
    ObservationWindow,
    WindowBuilderResult,
    WindowConfig,
    create_observation,
)
from miie.processing.observation.window_builder import ObservationWindowBuilder

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_obs(
    source_id: str,
    metric_id: str,
    value: float,
    timestamp: str,
    source_type: str = "file",
    quality: str = "complete",
) -> Observation:
    """Create a valid Observation for testing."""
    return create_observation(
        source_type=source_type,
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        timestamp=timestamp,
        quality=quality,
    )


def _make_obs_list(
    metric_id: str,
    start_date: str,
    count: int,
    value_start: float = 1.0,
    source_type: str = "file",
    days_between: int = 5,
) -> List[Observation]:
    """Create a list of observations with sequential timestamps."""
    start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    result = []
    for i in range(count):
        ts = start + timedelta(days=i * days_between)
        ts_str = ts.isoformat() if "+" in ts.isoformat() or ts.isoformat().endswith("Z") else ts.isoformat()
        result.append(
            _make_obs(
                source_id=f"file-{i:04d}",
                metric_id=metric_id,
                value=value_start + i,
                timestamp=ts_str,
                source_type=source_type,
            )
        )
    return result


def _make_collection(observations: List[Observation]) -> ObservationCollection:
    """Wrap observations in a single-window ObservationCollection."""
    window = ObservationWindow(
        window_id="w00",
        window_index=0,
        strategy="temporal",
        start_boundary="2024-01-01T00:00:00+00:00",
        end_boundary="2024-12-31T00:00:00+00:00",
        observations=observations,
    )
    return ObservationCollection(
        collection_id="test-collection",
        repository_id="repo-1",
        analysis_id="analysis-1",
        windows=[window],
    )


# ===================================================================
# WindowConfig Tests
# ===================================================================


class TestWindowConfig:
    """ODSS §24 — WindowConfig validation."""

    def test_valid_temporal_config(self):
        config = WindowConfig(strategy="temporal", window_size=30)
        assert config.strategy == "temporal"
        assert config.window_size == 30
        assert config.min_observations == 2
        assert config.max_windows is None
        assert config.custom_boundaries is None

    def test_valid_commit_count_config(self):
        config = WindowConfig(strategy="commit_count", window_size=10)
        assert config.strategy == "commit_count"
        assert config.window_size == 10

    def test_valid_hybrid_config(self):
        config = WindowConfig(strategy="hybrid", window_size=30, min_observations=5)
        assert config.strategy == "hybrid"
        assert config.min_observations == 5

    def test_valid_custom_config(self):
        boundaries = [("2024-01-01T00:00:00+00:00", "2024-03-01T00:00:00+00:00")]
        config = WindowConfig(strategy="custom", custom_boundaries=boundaries)
        assert config.strategy == "custom"
        assert len(config.custom_boundaries) == 1

    def test_invalid_strategy_rejected(self):
        with pytest.raises(ValueError, match="strategy must be one of"):
            WindowConfig(strategy="invalid")

    def test_invalid_window_size_rejected(self):
        with pytest.raises(ValueError, match="window_size must be >= 1"):
            WindowConfig(strategy="temporal", window_size=0)

    def test_invalid_min_observations_rejected(self):
        with pytest.raises(ValueError, match="min_observations must be >= 0"):
            WindowConfig(strategy="temporal", min_observations=-1)

    def test_invalid_max_windows_rejected(self):
        with pytest.raises(ValueError, match="max_windows must be >= 1"):
            WindowConfig(strategy="temporal", max_windows=0)

    def test_custom_without_boundaries_rejected(self):
        with pytest.raises(ValueError, match="custom_boundaries required"):
            WindowConfig(strategy="custom")

    def test_custom_with_invalid_boundary_format_rejected(self):
        with pytest.raises(ValueError, match="must be valid ISO-8601"):
            WindowConfig(strategy="custom", custom_boundaries=[("not-a-date", "2024-01-01T00:00:00+00:00")])

    def test_custom_with_start_after_end_rejected(self):
        with pytest.raises(ValueError, match="start must be < end"):
            WindowConfig(
                strategy="custom",
                custom_boundaries=[("2024-06-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00")],
            )

    def test_frozen_dataclass(self):
        config = WindowConfig(strategy="temporal")
        with pytest.raises(AttributeError):
            config.strategy = "commit_count"  # type: ignore[misc]


# ===================================================================
# WindowBuilderResult Tests
# ===================================================================


class TestWindowBuilderResult:
    """ODSS §25 — WindowBuilderResult validation."""

    def test_empty_result(self):
        result = WindowBuilderResult()
        assert result.windows == []
        assert result.unassigned_observations == []
        assert result.warnings == []

    def test_result_with_windows(self):
        obs = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs],
        )
        result = WindowBuilderResult(windows=[window])
        assert len(result.windows) == 1
        assert result.windows[0].window_id == "w00"

    def test_result_with_warnings(self):
        result = WindowBuilderResult(warnings=["test warning"])
        assert "test warning" in result.warnings

    def test_frozen_dataclass(self):
        result = WindowBuilderResult()
        with pytest.raises(AttributeError):
            result.windows = []  # type: ignore[misc]


# ===================================================================
# DetectorAdapterOutput Tests
# ===================================================================


class TestDetectorAdapterOutput:
    """ODSS §27 — DetectorAdapterOutput validation."""

    def test_empty_output(self):
        output = DetectorAdapterOutput()
        assert output.metrics == {}
        assert output.window_ids == []
        assert output.metadata == {}

    def test_output_with_data(self):
        output = DetectorAdapterOutput(
            metrics={"M-02": {"w00": [1.0, 2.0]}},
            window_ids=["w00"],
            metadata={"source": "test"},
        )
        assert "M-02" in output.metrics
        assert "w00" in output.window_ids

    def test_frozen_dataclass(self):
        output = DetectorAdapterOutput()
        with pytest.raises(AttributeError):
            output.metrics = {}  # type: ignore[misc]


# ===================================================================
# ObservationWindowBuilder Tests
# ===================================================================


class TestObservationWindowBuilderTemporal:
    """OEAS §18.2 — Temporal windowing strategy."""

    def setup_method(self):
        self.builder = ObservationWindowBuilder()

    def test_empty_collection_returns_empty(self):
        collection = _make_collection([])
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        assert result.windows == []
        assert any("No observations" in w for w in result.warnings)

    def test_single_observation_single_window(self):
        obs = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        collection = _make_collection([obs])
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        assert len(result.windows) == 1
        assert result.windows[0].observations[0].metric_id == "M-02"

    def test_multiple_observations_in_one_window(self):
        obs_list = _make_obs_list("M-02", "2024-01-05T00:00:00+00:00", count=5, days_between=2)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        # All 5 observations within 10 days → 1 window of 30 days
        assert len(result.windows) == 1
        assert len(result.windows[0].observations) == 5

    def test_observations_spanning_multiple_windows(self):
        # 120 days span with 30-day windows → 4 windows
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=24, days_between=5)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        assert len(result.windows) >= 4

    def test_window_ids_are_sequential(self):
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=60, days_between=5)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        for i, window in enumerate(result.windows):
            assert window.window_id == f"w{i:02d}"

    def test_windows_are_non_overlapping(self):
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=60, days_between=5)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        # Check no observation appears in multiple windows
        seen_ids = set()
        for window in result.windows:
            for obs in window.observations:
                assert obs.observation_id not in seen_ids, f"Duplicate observation {obs.observation_id}"
                seen_ids.add(obs.observation_id)

    def test_statistics_are_computed(self):
        obs_list = _make_obs_list("M-02", "2024-01-05T00:00:00+00:00", count=5, days_between=2)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        stats = result.windows[0].statistics
        assert stats is not None
        assert stats.n == 5
        assert stats.mean == pytest.approx(3.0)  # values 1,2,3,4,5 → mean=3

    def test_metrics_present_populated(self):
        obs_list = _make_obs_list("M-02", "2024-01-05T00:00:00+00:00", count=3, days_between=2) + _make_obs_list(
            "M-06", "2024-01-05T00:00:00+00:00", count=3, days_between=2
        )
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        assert set(result.windows[0].metrics_present) == {"M-02", "M-06"}

    def test_empty_windows_are_excluded(self):
        # Only observations in days 0-5, then gap, then observations at day 60-65
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-01T00:00:00+00:00")
        obs2 = _make_obs("sha-0060", "M-02", 20.0, "2024-03-01T00:00:00+00:00")
        collection = _make_collection([obs1, obs2])
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        # Days 1-30 has obs1, days 31-60 has nothing (excluded), day 61+ has obs2
        assert len(result.windows) == 2


class TestObservationWindowBuilderCommitCount:
    """OEAS §18.3 — Commit-count windowing strategy."""

    def setup_method(self):
        self.builder = ObservationWindowBuilder()

    def test_basic_commit_count(self):
        # 10 M-02 observations, commits_per_window=5 → 2 windows
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=10, days_between=5)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="commit_count", window_size=5)
        result = self.builder.build(collection, config)
        assert len(result.windows) == 2

    def test_fallback_when_no_m02(self):
        # Only M-06 observations → falls back to temporal
        obs_list = _make_obs_list("M-06", "2024-01-01T00:00:00+00:00", count=10, days_between=5)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="commit_count", window_size=5)
        result = self.builder.build(collection, config)
        assert any("No M-02" in w for w in result.warnings)
        # Falls back to temporal → should still have windows
        assert len(result.windows) >= 1

    def test_mixed_metrics_respect_commit_count(self):
        # Mix of M-02 and M-06
        m02_obs = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=10, days_between=5)
        m06_obs = _make_obs_list("M-06", "2024-01-01T00:00:00+00:00", count=10, days_between=5)
        collection = _make_collection(m02_obs + m06_obs)
        config = WindowConfig(strategy="commit_count", window_size=5)
        result = self.builder.build(collection, config)
        # Windows still split by M-02 boundaries
        assert len(result.windows) >= 2


class TestObservationWindowBuilderHybrid:
    """OEAS §18.4 — Hybrid windowing strategy."""

    def setup_method(self):
        self.builder = ObservationWindowBuilder()

    def test_hybrid_merges_small_windows(self):
        # Temporal windows with few commits get merged
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=10, days_between=10)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="hybrid", window_size=30, min_observations=3)
        result = self.builder.build(collection, config)
        assert len(result.windows) >= 1

    def test_hybrid_preserves_large_windows(self):
        # All observations in one temporal window
        obs_list = _make_obs_list("M-02", "2024-01-05T00:00:00+00:00", count=10, days_between=2)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="hybrid", window_size=30, min_observations=3)
        result = self.builder.build(collection, config)
        assert len(result.windows) == 1


class TestObservationWindowBuilderCustom:
    """OEAS §18.1 — Custom boundary windowing."""

    def setup_method(self):
        self.builder = ObservationWindowBuilder()

    def test_custom_boundaries(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-02-15T00:00:00+00:00")
        obs2 = _make_obs("sha-0002", "M-02", 20.0, "2024-05-15T00:00:00+00:00")
        collection = _make_collection([obs1, obs2])
        config = WindowConfig(
            strategy="custom",
            custom_boundaries=[
                ("2024-01-01T00:00:00+00:00", "2024-04-01T00:00:00+00:00"),
                ("2024-04-01T00:00:00+00:00", "2024-07-01T00:00:00+00:00"),
            ],
        )
        result = self.builder.build(collection, config)
        assert len(result.windows) == 2
        assert result.windows[0].observations[0].value == 10.0
        assert result.windows[1].observations[0].value == 20.0

    def test_custom_empty_boundary_window_excluded(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-02-15T00:00:00+00:00")
        collection = _make_collection([obs1])
        config = WindowConfig(
            strategy="custom",
            custom_boundaries=[
                ("2024-01-01T00:00:00+00:00", "2024-04-01T00:00:00+00:00"),
                ("2024-04-01T00:00:00+00:00", "2024-07-01T00:00:00+00:00"),
            ],
        )
        result = self.builder.build(collection, config)
        assert len(result.windows) == 1  # Only first boundary has observation


class TestObservationWindowBuilderMaxWindows:
    """Test max_windows truncation."""

    def setup_method(self):
        self.builder = ObservationWindowBuilder()

    def test_max_windows_truncates(self):
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=60, days_between=5)
        collection = _make_collection(obs_list)
        config = WindowConfig(strategy="temporal", window_size=30, max_windows=2)
        result = self.builder.build(collection, config)
        assert len(result.windows) == 2
        # Overflow observations moved to unassigned
        total_in_windows = sum(len(w.observations) for w in result.windows)
        assert total_in_windows + len(result.unassigned_observations) == 60


class TestObservationWindowBuilderEdgeCases:
    """Edge cases for ObservationWindowBuilder."""

    def setup_method(self):
        self.builder = ObservationWindowBuilder()

    def test_invalid_collection_type_raises(self):
        config = WindowConfig(strategy="temporal")
        with pytest.raises(WindowBuilderError, match="must be an ObservationCollection"):
            self.builder.build("not-a-collection", config)

    def test_invalid_config_type_raises(self):
        collection = _make_collection([])
        with pytest.raises(WindowBuilderError, match="must be a WindowConfig"):
            self.builder.build(collection, "not-a-config")

    def test_determinism_same_input_same_output(self):
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=20, days_between=5)
        config = WindowConfig(strategy="temporal", window_size=30)

        result1 = self.builder.build(_make_collection(obs_list), config)
        result2 = self.builder.build(_make_collection(obs_list), config)

        assert len(result1.windows) == len(result2.windows)
        for w1, w2 in zip(result1.windows, result2.windows):
            assert w1.window_id == w2.window_id
            assert len(w1.observations) == len(w2.observations)
            for o1, o2 in zip(w1.observations, w2.observations):
                assert o1.observation_id == o2.observation_id
                assert o1.value == o2.value

    def test_observations_sorted_by_timestamp(self):
        # Observations provided out of order
        obs1 = _make_obs("sha-0002", "M-02", 20.0, "2024-01-15T00:00:00+00:00")
        obs2 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-05T00:00:00+00:00")
        obs3 = _make_obs("sha-0003", "M-02", 30.0, "2024-01-10T00:00:00+00:00")
        collection = _make_collection([obs1, obs2, obs3])
        config = WindowConfig(strategy="temporal", window_size=30)
        result = self.builder.build(collection, config)
        # All in one window, sorted
        timestamps = [o.timestamp for o in result.windows[0].observations]
        assert timestamps == sorted(timestamps)


# ===================================================================
# DetectorAdapter Tests
# ===================================================================


class TestDetectorAdapterToMetricDataFrame:
    """OEAS §21.4 / ODSS §27 — to_metric_dataframe translation."""

    def setup_method(self):
        self.adapter = DetectorAdapter()

    def test_basic_translation(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        obs2 = _make_obs("sha-0002", "M-02", 20.0, "2024-02-15T00:00:00+00:00")
        obs3 = _make_obs("sha-0003", "M-06", 5.0, "2024-01-15T00:00:00+00:00")
        obs4 = _make_obs("sha-0004", "M-06", 15.0, "2024-02-15T00:00:00+00:00")

        window1 = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1, obs3],
        )
        window2 = ObservationWindow(
            window_id="w01",
            window_index=1,
            strategy="temporal",
            start_boundary="2024-02-01T00:00:00+00:00",
            end_boundary="2024-03-01T00:00:00+00:00",
            observations=[obs2, obs4],
        )
        collection = _make_collection([obs1, obs2, obs3, obs4])

        result = self.adapter.to_metric_dataframe([window1, window2], collection)

        assert "M-02" in result
        assert "M-06" in result
        assert len(result["M-02"]) == 2
        assert result["M-02"][0] == 10.0  # mean of window1 M-02
        assert result["M-02"][1] == 20.0  # mean of window2 M-02
        assert result["M-06"][0] == 5.0
        assert result["M-06"][1] == 15.0

    def test_empty_windows_raises(self):
        collection = _make_collection([])
        with pytest.raises(DetectorAdapterError, match="No windows provided"):
            self.adapter.to_metric_dataframe([], collection)

    def test_no_valid_metrics_raises(self):
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[],  # empty
        )
        collection = _make_collection([])
        with pytest.raises(DetectorAdapterError, match="No valid metric"):
            self.adapter.to_metric_dataframe([window], collection)

    def test_multiple_observations_per_window_averaged(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-05T00:00:00+00:00")
        obs2 = _make_obs("sha-0002", "M-02", 30.0, "2024-01-15T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1, obs2],
        )
        collection = _make_collection([obs1, obs2])
        result = self.adapter.to_metric_dataframe([window], collection)
        assert result["M-02"][0] == pytest.approx(20.0)  # (10+30)/2

    def test_missing_metric_in_window_not_in_output(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-05T00:00:00+00:00")
        obs2 = _make_obs("sha-0002", "M-06", 20.0, "2024-01-05T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1],  # Only M-02
        )
        collection = _make_collection([obs1, obs2])
        result = self.adapter.to_metric_dataframe([window], collection)
        assert result["M-02"][0] == 10.0
        # M-06 not in windows → not in output
        assert "M-06" not in result


class TestDetectorAdapterToPairedObservations:
    """OEAS §21.4 / ODSS §27 — to_paired_observations alignment."""

    def setup_method(self):
        self.adapter = DetectorAdapter()

    def test_basic_pairing(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        obs2 = _make_obs("sha-0001", "M-06", 20.0, "2024-01-15T00:00:00+00:00")
        obs3 = _make_obs("sha-0002", "M-02", 30.0, "2024-01-20T00:00:00+00:00")
        obs4 = _make_obs("sha-0002", "M-06", 40.0, "2024-01-20T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1, obs2, obs3, obs4],
        )
        values_i, values_j = self.adapter.to_paired_observations(window, "M-02", "M-06")
        assert values_i == [10.0, 30.0]
        assert values_j == [20.0, 40.0]

    def test_no_common_source_raises(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        obs2 = _make_obs("sha-0002", "M-06", 20.0, "2024-01-15T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1, obs2],
        )
        with pytest.raises(DetectorAdapterError, match="No common source_ids"):
            self.adapter.to_paired_observations(window, "M-02", "M-06")

    def test_missing_metric_raises(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1],
        )
        with pytest.raises(DetectorAdapterError, match="No observations for M-06"):
            self.adapter.to_paired_observations(window, "M-02", "M-06")

    def test_invalid_metric_id_raises(self):
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1],
        )
        with pytest.raises(DetectorAdapterError, match="Invalid metric"):
            self.adapter.to_paired_observations(window, "M-99", "M-02")

    def test_invalid_window_type_raises(self):
        with pytest.raises(DetectorAdapterError, match="must be an ObservationWindow"):
            self.adapter.to_paired_observations("not-a-window", "M-02", "M-06")

    def test_partial_source_overlap(self):
        # sha-0001 has both, sha-0002 has only M-02, sha-0003 has only M-06
        obs1 = _make_obs("sha-0001", "M-02", 10.0, "2024-01-15T00:00:00+00:00")
        obs2 = _make_obs("sha-0001", "M-06", 20.0, "2024-01-15T00:00:00+00:00")
        obs3 = _make_obs("sha-0002", "M-02", 30.0, "2024-01-20T00:00:00+00:00")
        obs4 = _make_obs("sha-0003", "M-06", 40.0, "2024-01-25T00:00:00+00:00")
        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2024-01-01T00:00:00+00:00",
            end_boundary="2024-02-01T00:00:00+00:00",
            observations=[obs1, obs2, obs3, obs4],
        )
        values_i, values_j = self.adapter.to_paired_observations(window, "M-02", "M-06")
        # Only sha-0001 has both → 1 pair
        assert len(values_i) == 1
        assert values_i == [10.0]
        assert values_j == [20.0]


# ===================================================================
# Integration: Full Pipeline
# ===================================================================


class TestFullPipeline:
    """End-to-end: ObservationCollection → WindowBuilder → DetectorAdapter."""

    def test_full_pipeline_temporal(self):
        # Create 60 observations spanning 300 days
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=60, days_between=5)
        collection = _make_collection(obs_list)

        # Build windows
        builder = ObservationWindowBuilder()
        config = WindowConfig(strategy="temporal", window_size=60)
        result = builder.build(collection, config)

        assert len(result.windows) >= 5  # 300 days / 60 days = 5 windows
        assert result.unassigned_observations == []

        # Translate to metric dataframe
        adapter = DetectorAdapter()
        metric_df = adapter.to_metric_dataframe(result.windows, collection)

        assert "M-02" in metric_df
        assert len(metric_df["M-02"]) == len(result.windows)

    def test_full_pipeline_commit_count(self):
        obs_list = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=20, days_between=5)
        collection = _make_collection(obs_list)

        builder = ObservationWindowBuilder()
        config = WindowConfig(strategy="commit_count", window_size=5)
        result = builder.build(collection, config)

        assert len(result.windows) == 4  # 20 / 5 = 4

        adapter = DetectorAdapter()
        metric_df = adapter.to_metric_dataframe(result.windows, collection)

        assert "M-02" in metric_df
        assert len(metric_df["M-02"]) == 4

    def test_full_pipeline_with_paired_observations(self):
        m02_obs = _make_obs_list("M-02", "2024-01-01T00:00:00+00:00", count=5, days_between=5)
        m06_obs = _make_obs_list("M-06", "2024-01-01T00:00:00+00:00", count=5, days_between=5)
        collection = _make_collection(m02_obs + m06_obs)

        builder = ObservationWindowBuilder()
        config = WindowConfig(strategy="temporal", window_size=30)
        result = builder.build(collection, config)

        adapter = DetectorAdapter()
        for window in result.windows:
            values_i, values_j = adapter.to_paired_observations(window, "M-02", "M-06")
            assert len(values_i) > 0
            assert len(values_i) == len(values_j)
