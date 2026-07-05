"""
Integration tests for detector diagnostics (PR-16B).

Tests that D-01, D-02, and D-03 detectors include diagnostics
in their output without breaking existing functionality.
"""

from typing import List
from unittest.mock import MagicMock

import numpy as np
import pytest

from miie.processing.detection.correlation_breakdown_detector import (
    CorrelationBreakdownDetector,
)
from miie.processing.detection.diagnostics import (
    d01_diagnostics,
    d02_diagnostics,
    d03_diagnostics,
)
from miie.processing.detection.distribution_drift_detector import (
    DistributionDriftDetector,
)
from miie.processing.detection.threshold_compression_detector import (
    ThresholdCompressionDetector,
)

# ---------------------------------------------------------------------------
# Mock observation window builder
# ---------------------------------------------------------------------------


def _make_observation(metric_id: str, value: float, source_id: str = "s1"):
    obs = MagicMock()
    obs.metric_id = metric_id
    obs.value = value
    obs.source_id = source_id
    return obs


def _make_window(window_id: str, observations: List[MagicMock]):
    w = MagicMock()
    w.window_id = window_id
    w.observations = observations
    return w


# ---------------------------------------------------------------------------
# D-01 Diagnostics unit tests
# ---------------------------------------------------------------------------


class TestD01Diagnostics:
    def test_basic_diagnostics(self):
        np.random.seed(42)
        x = np.random.normal(0, 1, 30)
        y = np.random.normal(0.3, 1, 30)
        d = d01_diagnostics(x.tolist(), y.tolist(), 0.3, 0.01)

        assert "effect_sizes" in d
        assert "power_analysis" in d
        assert "sample_adequacy" in d
        assert "ci_diagnostic" in d
        assert "summary" in d

        assert d["effect_sizes"]["ks_d"] > 0
        assert d["sample_adequacy"]["n_group1"] == 30
        assert d["sample_adequacy"]["adequate"] is True
        assert 0.0 <= d["power_analysis"]["observed_power"] <= 1.0

    def test_inadequate_sample(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 3.0, 4.0, 5.0, 6.0]
        d = d01_diagnostics(x, y, 0.2, 0.1)

        assert d["sample_adequacy"]["adequate"] is False
        assert d["sample_adequacy"]["shortfall"] > 0

    def test_high_effect_gives_high_power(self):
        np.random.seed(42)
        x = np.random.normal(0, 1, 100)
        y = np.random.normal(2.0, 1, 100)  # Large shift
        d = d01_diagnostics(x.tolist(), y.tolist(), 0.8, 0.001)

        assert d["power_analysis"]["observed_power"] > 0.9


# ---------------------------------------------------------------------------
# D-02 Diagnostics unit tests
# ---------------------------------------------------------------------------


class TestD02Diagnostics:
    def test_basic_diagnostics(self):
        d = d02_diagnostics(0.4, 50)

        assert "effect_sizes" in d
        assert "power_analysis" in d
        assert "sample_adequacy" in d
        assert "ci_diagnostic" in d
        assert "summary" in d

        assert d["effect_sizes"]["pearson_r"] == 0.4
        assert d["effect_sizes"]["r_squared"] == pytest.approx(0.16, abs=0.001)
        assert d["sample_adequacy"]["adequate"] is True
        assert 0.0 <= d["power_analysis"]["observed_power"] <= 1.0

    def test_strong_correlation_high_power(self):
        d = d02_diagnostics(0.7, 100)
        assert d["power_analysis"]["observed_power"] > 0.95

    def test_weak_correlation_low_power(self):
        d = d02_diagnostics(0.05, 20)
        assert d["power_analysis"]["observed_power"] < 0.5

    def test_strength_interpretation(self):
        d1 = d02_diagnostics(0.05, 50)
        assert d1["effect_sizes"]["strength"] == "negligible"

        d2 = d02_diagnostics(0.2, 50)
        assert d2["effect_sizes"]["strength"] == "small"

        d3 = d02_diagnostics(0.4, 50)
        assert d3["effect_sizes"]["strength"] == "medium"

        d4 = d02_diagnostics(0.6, 50)
        assert d4["effect_sizes"]["strength"] == "large"


# ---------------------------------------------------------------------------
# D-03 Diagnostics unit tests
# ---------------------------------------------------------------------------


class TestD03Diagnostics:
    def test_basic_diagnostics(self):
        np.random.seed(42)
        vals = np.random.normal(50, 10, 40).tolist()
        d = d03_diagnostics(vals, 50.0, 5.0, 2.5, 0.1, 0.3)

        assert "effect_sizes" in d
        assert "power_analysis" in d
        assert "sample_adequacy" in d
        assert "ci_diagnostic" in d
        assert "summary" in d

        assert d["effect_sizes"]["compression_index"] >= 0
        assert d["effect_sizes"]["compression_index"] <= 1
        assert d["sample_adequacy"]["adequate"] is True

    def test_high_compression_large_effect(self):
        np.random.seed(42)
        # Values clustered around threshold
        vals = [50.0 + np.random.normal(0, 0.5) for _ in range(40)]
        d = d03_diagnostics(vals, 50.0, 2.0, 3.0, 0.15, 0.1)

        assert d["effect_sizes"]["compression_index"] > 0.5

    def test_inadequate_sample(self):
        vals = [1.0, 2.0, 3.0]
        d = d03_diagnostics(vals, 2.0, 1.0, 1.5, 0.1, 0.3)
        assert d["sample_adequacy"]["adequate"] is False


# ---------------------------------------------------------------------------
# D-01 Detector integration test
# ---------------------------------------------------------------------------


class TestD01DetectorDiagnostics:
    def test_detect_observations_includes_diagnostics(self):
        np.random.seed(42)
        # Build 3 windows with drifting M-01 values
        windows = []
        for w_idx in range(3):
            obs_list = []
            for i in range(25):
                obs_list.append(
                    _make_observation(
                        "M-01",
                        float(np.random.normal(w_idx * 0.5, 1.0)),
                        f"src_{i}",
                    )
                )
            windows.append(_make_window(f"w{w_idx}", obs_list))

        detector = DistributionDriftDetector()
        result = detector.detect_observations(windows)

        output = result.detector_outputs["D-01"]
        assert "diagnostics" in output
        assert output["diagnostics"]["enabled"] is True
        assert isinstance(output["diagnostics"]["per_event"], list)

    def test_execute_includes_diagnostics(self):
        np.random.seed(42)
        import datetime

        from miie.schemas.models import MetricDataFrame

        mdf = MetricDataFrame(
            repo_id="test_repo",
            run_id="test_run",
            timestamp=datetime.datetime.now(),
            metrics={
                "M-01": {
                    "w0": [float(np.random.normal(0, 1)) for _ in range(25)],
                    "w1": [float(np.random.normal(1.5, 1)) for _ in range(25)],
                }
            },
        )

        detector = DistributionDriftDetector()
        result = detector.execute(mdf)

        output = result.detector_outputs["D-01"]
        assert "diagnostics" in output
        assert output["diagnostics"]["enabled"] is True

    def test_no_drift_no_diagnostics(self):
        np.random.seed(42)
        obs_list = []
        for i in range(25):
            obs_list.append(_make_observation("M-01", float(np.random.normal(0, 0.01)), f"src_{i}"))

        windows = [
            _make_window("w0", obs_list),
            _make_window("w1", obs_list),
        ]

        detector = DistributionDriftDetector()
        result = detector.detect_observations(windows)

        output = result.detector_outputs["D-01"]
        assert "diagnostics" in output
        assert len(output["diagnostics"]["per_event"]) == 0


# ---------------------------------------------------------------------------
# D-02 Detector integration test
# ---------------------------------------------------------------------------


class TestD02DetectorDiagnostics:
    def test_detect_observations_includes_diagnostics(self):
        np.random.seed(42)
        windows = []
        for w_idx in range(3):
            obs_list = []
            for i in range(25):
                # Two correlated metrics
                base = np.random.normal(0, 1)
                obs_list.append(_make_observation("M-01", base, f"src_{i}"))
                obs_list.append(_make_observation("M-02", base + np.random.normal(0, 0.3), f"src_{i}"))
            windows.append(_make_window(f"w{w_idx}", obs_list))

        detector = CorrelationBreakdownDetector()
        result = detector.detect_observations(windows)

        output = result.detector_outputs["D-02"]
        assert "diagnostics" in output
        assert output["diagnostics"]["enabled"] is True


# ---------------------------------------------------------------------------
# D-03 Detector integration test
# ---------------------------------------------------------------------------


class TestD03DetectorDiagnostics:
    def test_detect_observations_includes_diagnostics(self):
        np.random.seed(42)
        windows = []
        for w_idx in range(3):
            obs_list = []
            for i in range(30):
                # Values with some clustering around 50
                val = float(np.random.normal(50, 10))
                obs_list.append(_make_observation("M-01", val, f"src_{i}"))
            windows.append(_make_window(f"w{w_idx}", obs_list))

        detector = ThresholdCompressionDetector()
        result = detector.detect_observations(windows)

        output = result.detector_outputs["D-03"]
        assert "diagnostics" in output
        assert output["diagnostics"]["enabled"] is True
        assert isinstance(output["diagnostics"]["per_event"], list)
