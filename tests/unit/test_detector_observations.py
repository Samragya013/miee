"""
Observation-aware detector tests for D-01, D-02, D-03.

Tests the v1.5 detect_observations() path that consumes ObservationWindow
data directly instead of the legacy MetricDataFrame path.

Covers:
  - D-01: KS test and PSI on observation-level samples
  - D-02: Pearson/Spearman on paired observations aligned by source_id
  - D-03: Excess mass and dip test on observation-level distributions
  - Shared statistics module functions
  - Dispatcher observation-aware routing
"""

from __future__ import annotations

import math
from typing import List

import numpy as np
import pytest

from miie.processing.detection.correlation_breakdown_detector import (
    CorrelationBreakdownDetector,
)
from miie.processing.detection.distribution_drift_detector import (
    DistributionDriftDetector,
)
from miie.processing.detection.statistics import (
    auto_thresholds,
    compute_epsilon,
    compute_psi,
    dip_test,
    excess_mass_test,
    fisher_z,
    fisher_z_ci,
    fisher_z_inverse,
    ks_2samp,
    pearson_r,
    spearman_rho,
)
from miie.processing.detection.threshold_compression_detector import (
    ThresholdCompressionDetector,
)
from miie.processing.observation.models import (
    Observation,
    ObservationProvenance,
    ObservationWindow,
)
from miie.schemas.models import DetectorResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROVENANCE = ObservationProvenance(
    extractor_id="test-extractor",
    extraction_timestamp="2025-01-01T00:00:00+00:00",
    seed=42,
)

_METRIC_UNIT_MAP = {
    "M-01": "ratio",
    "M-02": "count",
    "M-03": "ratio",
    "M-04": "ratio",
    "M-05": "hours",
    "M-06": "count",
    "M-07": "ratio",
}


def _make_obs(
    source_id: str,
    metric_id: str,
    value: float,
    timestamp: str = "2025-01-01T00:00:00+00:00",
) -> Observation:
    """Create a minimal Observation for testing."""
    import hashlib

    payload = f"commit:{source_id}:{metric_id}"
    obs_id = hashlib.sha256(payload.encode()).hexdigest()[:16]
    unit = _METRIC_UNIT_MAP[metric_id]
    return Observation(
        observation_id=obs_id,
        source_type="commit",
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        unit=unit,
        timestamp=timestamp,
        quality="complete",
        provenance=_PROVENANCE,
    )


def _make_window(
    window_id: str,
    window_index: int,
    observations: List[Observation],
    start: str = "2025-01-01T00:00:00+00:00",
    end: str = "2025-01-31T00:00:00+00:00",
) -> ObservationWindow:
    """Create an ObservationWindow for testing."""
    return ObservationWindow(
        window_id=window_id,
        window_index=window_index,
        strategy="temporal",
        start_boundary=start,
        end_boundary=end,
        observations=observations,
    )


def _make_sha(idx: int) -> str:
    """Generate a fake 40-char commit SHA."""
    return f"{idx:040x}"


# ---------------------------------------------------------------------------
# Shared Statistics Module Tests
# ---------------------------------------------------------------------------


class TestSharedStatistics:
    """Tests for the shared statistics utilities (DES v2.0 §25)."""

    def test_ks_2samp_identical(self):
        """KS test on identical distributions should give low statistic, high p."""
        data = list(np.random.default_rng(42).normal(0, 1, 100))
        stat, p = ks_2samp(data, data)
        assert stat == pytest.approx(0.0, abs=1e-10)
        assert p == pytest.approx(1.0, abs=1e-10)

    def test_ks_2samp_different(self):
        """KS test on clearly different distributions should detect drift."""
        rng = np.random.default_rng(42)
        data1 = list(rng.normal(0, 1, 100))
        data2 = list(rng.normal(5, 1, 100))
        stat, p = ks_2samp(data1, data2)
        assert stat > 0.3
        assert p < 0.01

    def test_ks_2samp_empty(self):
        """KS test with empty data returns (0, 1)."""
        stat, p = ks_2samp([], [1.0, 2.0])
        assert stat == 0.0
        assert p == 1.0

    def test_compute_psi_identical(self):
        """PSI on identical distributions should be 0."""
        data = list(np.random.default_rng(42).normal(5, 1, 200))
        psi = compute_psi(data, data)
        assert psi == pytest.approx(0.0, abs=1e-10)

    def test_compute_psi_different(self):
        """PSI on different distributions should be > 0."""
        rng = np.random.default_rng(42)
        data1 = list(rng.normal(0, 1, 200))
        data2 = list(rng.normal(5, 1, 200))
        psi = compute_psi(data1, data2)
        assert psi > 0.1

    def test_compute_psi_empty(self):
        """PSI with empty data returns 0."""
        assert compute_psi([], [1.0]) == 0.0
        assert compute_psi([1.0], []) == 0.0

    def test_pearson_r_perfect(self):
        """Perfect positive correlation."""
        x = list(range(100))
        y = list(range(100))
        assert pearson_r(x, y) == pytest.approx(1.0, abs=1e-10)

    def test_pearson_r_negative(self):
        """Perfect negative correlation."""
        x = list(range(100))
        y = list(range(100, 0, -1))
        assert pearson_r(x, y) == pytest.approx(-1.0, abs=1e-10)

    def test_pearson_r_no_correlation(self):
        """Uncorrelated data should give low correlation."""
        rng = np.random.default_rng(42)
        x = list(rng.normal(0, 1, 500))
        y = list(rng.normal(0, 1, 500))
        r = pearson_r(x, y)
        assert abs(r) < 0.2

    def test_pearson_r_short_data(self):
        """Too few data points returns 0."""
        assert pearson_r([1.0], [2.0]) == 0.0
        assert pearson_r([], []) == 0.0

    def test_spearman_rho_monotonic(self):
        """Monotonic relationship should give high Spearman rho."""
        x = list(range(100))
        y = [v**3 for v in x]  # Monotonic but not linear
        rho = spearman_rho(x, y)
        assert rho == pytest.approx(1.0, abs=1e-10)

    def test_fisher_z_roundtrip(self):
        """Fisher z and inverse should roundtrip."""
        for r in [-0.9, -0.5, 0.0, 0.5, 0.9]:
            z = fisher_z(r)
            r_back = fisher_z_inverse(z)
            assert r_back == pytest.approx(r, abs=1e-10)

    def test_fisher_z_ci_contains_true(self):
        """95% CI should contain the true correlation most of the time."""
        rng = np.random.default_rng(42)
        true_r = 0.5
        contained = 0
        for _ in range(100):
            x = list(rng.normal(0, 1, 50))
            y = [true_r * xi + math.sqrt(1 - true_r**2) * yi for xi, yi in zip(x, rng.normal(0, 1, 50))]
            r = pearson_r(x, y)
            lo, hi = fisher_z_ci(r, 50)
            if lo <= true_r <= hi:
                contained += 1
        # Should contain true value at least 80% of the time
        assert contained >= 80

    def test_excess_mass_test_at_threshold(self):
        """Values clustered at threshold should give positive z-score."""
        rng = np.random.default_rng(42)
        # Generate values clustered around 50
        vals = list(rng.normal(50, 0.5, 100))
        eps = compute_epsilon(vals, 50.0)
        z = excess_mass_test(vals, 50.0, eps)
        # Clustered values produce a positive excess mass z-score
        assert z > 0.0

    def test_excess_mass_test_uniform(self):
        """Uniformly distributed values should give low z-score."""
        rng = np.random.default_rng(42)
        vals = list(rng.uniform(0, 100, 100))
        eps = compute_epsilon(vals, 50.0)
        z = excess_mass_test(vals, 50.0, eps)
        assert abs(z) < 3.0  # Should not be extreme

    def test_dip_test_unimodal(self):
        """Unimodal data should not show multimodality."""
        rng = np.random.default_rng(42)
        vals = list(rng.normal(50, 5, 100))
        stat, p = dip_test(vals, bootstrap_samples=100, random_seed=42)
        assert stat >= 0.0
        assert 0.0 <= p <= 1.0

    def test_auto_thresholds_basic(self):
        """Auto-threshold detection should find round numbers."""
        vals = [1.0, 5.0, 10.0, 25.0, 50.0, 75.0, 100.0]
        thresholds = auto_thresholds(vals)
        assert 5.0 in thresholds or 10.0 in thresholds or 50.0 in thresholds

    def test_auto_thresholds_empty(self):
        """Empty values should return empty thresholds."""
        assert auto_thresholds([]) == []


# ---------------------------------------------------------------------------
# D-01 Observation-Aware Tests
# ---------------------------------------------------------------------------


class TestD01Observations:
    """Tests for DistributionDriftDetector.detect_observations()."""

    def setup_method(self):
        self.detector = DistributionDriftDetector()

    def _make_windows_with_drift(self):
        """Create windows: w00 and w01 identical, w02 shifted."""
        rng = np.random.default_rng(42)
        windows = []

        # w00: 20 observations around mean 5
        obs_w00 = []
        for i in range(20):
            sha = _make_sha(i)
            obs_w00.append(_make_obs(sha, "M-02", 5.0 + rng.normal(0, 0.5)))
        windows.append(_make_window("w00", 0, obs_w00))

        # w01: same distribution as w00
        obs_w01 = []
        for i in range(20):
            sha = _make_sha(i + 100)
            obs_w01.append(_make_obs(sha, "M-02", 5.0 + rng.normal(0, 0.5)))
        windows.append(_make_window("w01", 1, obs_w01))

        # w02: shifted to mean 15
        obs_w02 = []
        for i in range(20):
            sha = _make_sha(i + 200)
            obs_w02.append(_make_obs(sha, "M-02", 15.0 + rng.normal(0, 0.5)))
        windows.append(_make_window("w02", 2, obs_w02))

        return windows

    def test_returns_detector_result(self):
        """detect_observations returns DetectorResult."""
        windows = self._make_windows_with_drift()
        result = self.detector.detect_observations(windows)
        assert isinstance(result, DetectorResult)
        assert "D-01" in result.detector_outputs

    def test_output_structure(self):
        """Output has all expected fields."""
        windows = self._make_windows_with_drift()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-01"]

        assert "drift_detected" in output
        assert "drift_magnitude" in output
        assert "metrics_analyzed" in output
        assert "drift_events" in output
        assert "ks_statistics" in output
        assert "psi_values" in output
        assert "drift_directions" in output
        assert "window_pairs_analyzed" in output

    def test_detects_drift_with_mean_shift(self):
        """Drift should be detected between w01 and w02."""
        windows = self._make_windows_with_drift()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-01"]

        # Should detect at least one drift event
        assert output["drift_detected"] is True
        assert len(output["drift_events"]) > 0

        # The drift should involve w01->w02
        pairs = [e["window_pair"] for e in output["drift_events"]]
        assert ["w01", "w02"] in pairs

    def test_no_drift_when_identical(self):
        """No drift when all windows have the same distribution (large samples)."""
        rng = np.random.default_rng(42)
        windows = []
        for wi in range(3):
            obs = []
            for i in range(200):
                sha = _make_sha(i + wi * 200)
                obs.append(_make_obs(sha, "M-02", 5.0 + rng.normal(0, 0.3)))
            windows.append(_make_window(f"w0{wi}", wi, obs))

        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-01"]
        assert output["drift_detected"] is False

    def test_empty_windows_no_drift(self):
        """No crash with empty window list."""
        result = self.detector.detect_observations([])
        output = result.detector_outputs["D-01"]
        assert output["drift_detected"] is False

    def test_insufficient_sample_size_skips(self):
        """Windows with <10 observations should be skipped."""
        obs_few = [_make_obs(_make_sha(i), "M-02", float(i)) for i in range(5)]
        obs_few2 = [_make_obs(_make_sha(i + 50), "M-02", float(i)) for i in range(5)]
        windows = [
            _make_window("w00", 0, obs_few),
            _make_window("w01", 1, obs_few2),
        ]
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-01"]
        assert output["drift_detected"] is False

    def test_multiple_metrics(self):
        """Supports analysis across multiple metrics."""
        rng = np.random.default_rng(42)
        windows = []
        for wi in range(3):
            obs = []
            for i in range(20):
                sha = _make_sha(i + wi * 100)
                obs.append(_make_obs(sha, "M-02", 5.0 + rng.normal(0, 0.5)))
                obs.append(_make_obs(sha, "M-06", 10.0 + rng.normal(0, 0.5)))
            windows.append(_make_window(f"w0{wi}", wi, obs))

        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-01"]
        assert "M-02" in output["metrics_analyzed"]
        assert "M-06" in output["metrics_analyzed"]

    def test_deterministic_execution(self):
        """Same input produces identical output."""
        windows = self._make_windows_with_drift()
        r1 = self.detector.detect_observations(windows)
        r2 = self.detector.detect_observations(windows)
        o1 = r1.detector_outputs["D-01"]
        o2 = r2.detector_outputs["D-01"]
        assert o1["drift_detected"] == o2["drift_detected"]
        assert o1["drift_magnitude"] == o2["drift_magnitude"]
        assert len(o1["drift_events"]) == len(o2["drift_events"])

    def test_config_override(self):
        """Config overrides detection thresholds."""
        windows = self._make_windows_with_drift()
        # Very strict thresholds: should detect more drift
        result = self.detector.detect_observations(windows, config={"ks_p_value_threshold": 0.5, "psi_threshold": 0.01})
        output = result.detector_outputs["D-01"]
        # With relaxed thresholds, should detect more events
        assert len(output["drift_events"]) >= 1


# ---------------------------------------------------------------------------
# D-02 Observation-Aware Tests
# ---------------------------------------------------------------------------


class TestD02Observations:
    """Tests for CorrelationBreakdownDetector.detect_observations()."""

    def setup_method(self):
        self.detector = CorrelationBreakdownDetector()

    def _make_windows_with_sign_reversal(self):
        """Create windows where correlation reverses sign."""
        windows = []

        # w00: positive correlation between M-02 and M-06
        obs_w00 = []
        for i in range(20):
            sha = _make_sha(i)
            x = float(i)
            obs_w00.append(_make_obs(sha, "M-02", x))
            obs_w00.append(_make_obs(sha, "M-06", x + 0.1 * (i % 3)))
        windows.append(_make_window("w00", 0, obs_w00))

        # w01: positive correlation (same)
        obs_w01 = []
        for i in range(20):
            sha = _make_sha(i + 100)
            x = float(i)
            obs_w01.append(_make_obs(sha, "M-02", x))
            obs_w01.append(_make_obs(sha, "M-06", x + 0.1 * (i % 3)))
        windows.append(_make_window("w01", 1, obs_w01))

        # w02: negative correlation (reversed)
        obs_w02 = []
        for i in range(20):
            sha = _make_sha(i + 200)
            x = float(i)
            obs_w02.append(_make_obs(sha, "M-02", x))
            obs_w02.append(_make_obs(sha, "M-06", 20.0 - x))
        windows.append(_make_window("w02", 2, obs_w02))

        return windows

    def test_returns_detector_result(self):
        """detect_observations returns DetectorResult."""
        windows = self._make_windows_with_sign_reversal()
        result = self.detector.detect_observations(windows)
        assert isinstance(result, DetectorResult)
        assert "D-02" in result.detector_outputs

    def test_output_structure(self):
        """Output has all expected fields."""
        windows = self._make_windows_with_sign_reversal()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-02"]

        assert "breakdown_detected" in output
        assert "breakdown_type" in output
        assert "metric_pairs_analyzed" in output
        assert "breakdown_events" in output
        assert "pearson_trajectories" in output
        assert "spearman_trajectories" in output
        assert "confidence_intervals" in output
        assert "window_pairs_flagged" in output

    def test_detects_sign_reversal(self):
        """Should detect sign reversal breakdown."""
        windows = self._make_windows_with_sign_reversal()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-02"]

        assert output["breakdown_detected"] is True
        breakdown_types = [e["breakdown_type"] for e in output["breakdown_events"]]
        assert "sign_reversal" in breakdown_types

    def test_no_breakdown_with_stable_correlation(self):
        """No breakdown when correlation is stable."""
        windows = []
        for wi in range(3):
            obs = []
            for i in range(20):
                sha = _make_sha(i + wi * 100)
                x = float(i)
                obs.append(_make_obs(sha, "M-02", x))
                obs.append(_make_obs(sha, "M-06", x + 1.0))
            windows.append(_make_window(f"w0{wi}", wi, obs))

        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-02"]
        assert output["breakdown_detected"] is False

    def test_insufficient_metrics(self):
        """Only one metric should yield no breakdown."""
        obs = [_make_obs(_make_sha(i), "M-02", float(i)) for i in range(20)]
        windows = [_make_window("w00", 0, obs), _make_window("w01", 1, obs)]
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-02"]
        assert output["breakdown_detected"] is False

    def test_pearson_trajectories_populated(self):
        """Pearson trajectories should have values for each metric pair."""
        windows = self._make_windows_with_sign_reversal()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-02"]

        assert "M-02_M-06" in output["pearson_trajectories"]
        traj = output["pearson_trajectories"]["M-02_M-06"]
        assert len(traj) == 3  # 3 windows
        # First two should be positive, last should be negative
        assert traj[0] is not None and traj[0] > 0
        assert traj[2] is not None and traj[2] < 0

    def test_empty_windows(self):
        """Empty windows should not crash."""
        result = self.detector.detect_observations([])
        output = result.detector_outputs["D-02"]
        assert output["breakdown_detected"] is False

    def test_deterministic_execution(self):
        """Same input produces identical output."""
        windows = self._make_windows_with_sign_reversal()
        r1 = self.detector.detect_observations(windows)
        r2 = self.detector.detect_observations(windows)
        o1 = r1.detector_outputs["D-02"]
        o2 = r2.detector_outputs["D-02"]
        assert o1["breakdown_detected"] == o2["breakdown_detected"]
        assert o1["breakdown_type"] == o2["breakdown_type"]
        assert len(o1["breakdown_events"]) == len(o2["breakdown_events"])


# ---------------------------------------------------------------------------
# D-03 Observation-Aware Tests
# ---------------------------------------------------------------------------


class TestD03Observations:
    """Tests for ThresholdCompressionDetector.detect_observations()."""

    def setup_method(self):
        self.detector = ThresholdCompressionDetector()

    def _make_windows_with_compression(self):
        """Create windows with values clustered at threshold 50."""
        windows = []

        # w00: values uniformly spread across [0, 100]
        obs_w00 = []
        rng = np.random.default_rng(42)
        for i in range(40):
            sha = _make_sha(i)
            obs_w00.append(_make_obs(sha, "M-02", float(rng.uniform(0, 100))))
        windows.append(_make_window("w00", 0, obs_w00))

        # w01: values spread across [0, 100] BUT with a heavy spike at 50
        obs_w01 = []
        for i in range(60):
            sha = _make_sha(i + 100)
            if i < 30:
                # 50% of values clustered at 50
                obs_w01.append(_make_obs(sha, "M-02", 50.0 + rng.normal(0, 0.5)))
            else:
                # 50% spread uniformly
                obs_w01.append(_make_obs(sha, "M-02", float(rng.uniform(0, 100))))
        windows.append(_make_window("w01", 1, obs_w01))

        return windows

    def test_returns_detector_result(self):
        """detect_observations returns DetectorResult."""
        windows = self._make_windows_with_compression()
        result = self.detector.detect_observations(windows)
        assert isinstance(result, DetectorResult)
        assert "D-03" in result.detector_outputs

    def test_output_structure(self):
        """Output has all expected fields."""
        windows = self._make_windows_with_compression()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-03"]

        assert "compression_detected" in output
        assert "compression_index" in output
        assert "metrics_analyzed" in output
        assert "compression_events" in output
        assert "thresholds_used" in output
        assert "excess_mass_z_scores" in output
        assert "dip_test_statistics" in output
        assert "dip_test_p_values" in output
        assert "windows_analyzed" in output

    def test_detects_compression(self):
        """Should detect compression in w01."""
        windows = self._make_windows_with_compression()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-03"]

        # w01 has 40 observations extremely clustered at 50 -> should trigger
        assert output["compression_detected"] is True
        assert len(output["compression_events"]) > 0

    def test_no_compression_uniform(self):
        """Uniform distribution should not trigger compression."""
        rng = np.random.default_rng(42)
        windows = []
        for wi in range(2):
            obs = []
            for i in range(30):
                sha = _make_sha(i + wi * 100)
                obs.append(_make_obs(sha, "M-02", float(rng.uniform(0, 100))))
            windows.append(_make_window(f"w0{wi}", wi, obs))

        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-03"]
        assert output["compression_detected"] is False

    def test_insufficient_sample_size_skips(self):
        """Windows with <20 observations should be skipped."""
        obs_few = [_make_obs(_make_sha(i), "M-02", 50.0) for i in range(10)]
        windows = [
            _make_window("w00", 0, obs_few),
            _make_window("w01", 1, obs_few),
        ]
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-03"]
        assert output["compression_detected"] is False

    def test_empty_windows(self):
        """Empty windows should not crash."""
        result = self.detector.detect_observations([])
        output = result.detector_outputs["D-03"]
        assert output["compression_detected"] is False

    def test_compression_events_have_required_fields(self):
        """Each compression event should have all required fields."""
        windows = self._make_windows_with_compression()
        result = self.detector.detect_observations(windows)
        output = result.detector_outputs["D-03"]

        for event in output["compression_events"]:
            assert "metric" in event
            assert "threshold" in event
            assert "window" in event
            assert "compression_detected" in event
            assert "compression_index" in event
            assert "excess_mass_z_score" in event
            assert "dip_test_statistic" in event
            assert "dip_test_p_value" in event
            assert "epsilon" in event
            assert "sample_size" in event
            assert "hypothesized_cause" in event

    def test_deterministic_execution(self):
        """Same input produces identical output."""
        windows = self._make_windows_with_compression()
        r1 = self.detector.detect_observations(windows)
        r2 = self.detector.detect_observations(windows)
        o1 = r1.detector_outputs["D-03"]
        o2 = r2.detector_outputs["D-03"]
        assert o1["compression_detected"] == o2["compression_detected"]
        assert o1["compression_index"] == o2["compression_index"]
        assert len(o1["compression_events"]) == len(o2["compression_events"])


# ---------------------------------------------------------------------------
# Dispatcher Observation-Aware Routing Tests
# ---------------------------------------------------------------------------


class TestDispatcherObservations:
    """Tests for DetectorDispatcherEngine.invoke_observations()."""

    def setup_method(self):
        from miie.processing.detection.registry import DetectorRegistry

        self.registry = DetectorRegistry()
        self.registry.register(DistributionDriftDetector())
        self.registry.register(CorrelationBreakdownDetector())
        self.registry.register(ThresholdCompressionDetector())

        from miie.processing.detection.dispatcher import DetectorDispatcherEngine

        self.dispatcher = DetectorDispatcherEngine(self.registry)

    def test_invoke_observations_returns_results(self):
        """invoke_observations returns DetectorResults."""
        from miie.schemas.models import DetectorResults

        rng = np.random.default_rng(42)
        windows = []
        for wi in range(3):
            obs = []
            for i in range(20):
                sha = _make_sha(i + wi * 100)
                obs.append(_make_obs(sha, "M-02", float(rng.uniform(0, 100))))
                obs.append(_make_obs(sha, "M-06", float(rng.uniform(0, 100))))
            windows.append(_make_window(f"w0{wi}", wi, obs))

        result = self.dispatcher.invoke_observations(windows)
        assert isinstance(result, DetectorResults)
        assert len(result.detector_outputs) > 0

    def test_enabled_detectors_filtering(self):
        """Only enabled detectors should run."""
        rng = np.random.default_rng(42)
        windows = []
        for wi in range(3):
            obs = []
            for i in range(20):
                sha = _make_sha(i + wi * 100)
                obs.append(_make_obs(sha, "M-02", float(rng.uniform(0, 100))))
            windows.append(_make_window(f"w0{wi}", wi, obs))

        result = self.dispatcher.invoke_observations(windows, enabled_detectors=["D-01"])
        assert "D-01" in result.detector_outputs
        # D-02 and D-03 should not be present (or skipped)
        assert (
            "D-02" not in result.detector_outputs or result.detector_outputs.get("D-02", {}).get("status") == "skipped"
        )

    def test_empty_windows_all_detectors_handle(self):
        """All detectors should handle empty windows gracefully."""
        result = self.dispatcher.invoke_observations([])
        assert len(result.detector_outputs) >= 0  # No crash


if __name__ == "__main__":
    pytest.main([__file__])
