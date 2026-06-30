"""
Unit tests for D01 Distribution Drift Detector.

Covers:
  - Initialization
  - Input validation (MetricDataFrame legacy path)
  - Output structure and types
  - Drift detection with synthetic data
  - No drift when data is identical
  - Insufficient data handling
  - Deterministic execution
  - Empty metrics handling
"""

import datetime

import pytest

from miie.processing.detection.distribution_drift_detector import (
    DistributionDriftDetector,
)
from miie.schemas.models import MetricDataFrame


class TestDistributionDriftDetector:
    """Test cases for DistributionDriftDetector (legacy MetricDataFrame path)."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = DistributionDriftDetector()

        # Test data: w00 and w01 are identical (no drift), w02 has a mean shift
        self.test_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {
                    # 10 observations, mean ~5.0
                    "w00": [4.0, 4.5, 5.0, 5.5, 6.0, 4.0, 4.5, 5.0, 5.5, 6.0],
                    # Same as w00 -> no drift expected
                    "w01": [4.0, 4.5, 5.0, 5.5, 6.0, 4.0, 4.5, 5.0, 5.5, 6.0],
                    # Mean shifted to ~15.0 -> drift expected
                    "w02": [14.0, 14.5, 15.0, 15.5, 16.0, 14.0, 14.5, 15.0, 15.5, 16.0],
                },
            },
        )

        # Insufficient data: <10 observations per window
        self.insufficient_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {
                    "w00": [1.0, 2.0, 3.0],  # Only 3 observations
                    "w01": [4.0, 5.0, 6.0],
                },
            },
        )

        # Single window (can't compute drift)
        self.single_window_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {
                    "w00": list(range(10, 20)),  # 10 observations
                },
            },
        )

        # No supported metrics
        self.no_metrics_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={},
        )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def test_detector_initialization(self):
        """Test that detector initializes correctly."""
        assert self.detector.get_detector_id() == "D-01"
        assert self.detector.get_detector_name() == "Distribution Drift Detector"
        supported = self.detector.get_supported_metrics()
        assert len(supported) == 7
        assert "M-01" in supported
        assert "M-07" in supported

    def test_threshold_defaults(self):
        """Test default threshold values."""
        assert self.detector.ks_p_value_threshold == 0.05
        assert self.detector.psi_threshold == 0.25

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    def test_validate_input_with_supported_metric(self):
        """Test validation passes with at least one supported metric."""
        assert self.detector.validate_input(self.test_metric_dataframe) is True

    def test_validate_input_no_metrics(self):
        """Test validation fails with no metrics."""
        assert self.detector.validate_input(self.no_metrics_metric_dataframe) is False

    def test_validate_input_insufficient_data_still_passes(self):
        """Validation only checks metric presence, not data sizes."""
        assert self.detector.validate_input(self.insufficient_metric_dataframe) is True

    # ------------------------------------------------------------------
    # Execute - output structure
    # ------------------------------------------------------------------

    def test_execute_returns_detector_result(self):
        """Test that execute returns a DetectorResult."""
        result = self.detector.execute(self.test_metric_dataframe)
        from miie.schemas.models import DetectorResult

        assert isinstance(result, DetectorResult)
        assert hasattr(result, "detector_outputs")
        assert self.detector.get_detector_id() in result.detector_outputs

    def test_execute_output_structure(self):
        """Test that execute returns the expected output structure."""
        result = self.detector.execute(self.test_metric_dataframe)
        output = result.detector_outputs[self.detector.get_detector_id()]

        assert "drift_detected" in output
        assert "drift_magnitude" in output
        assert "metrics_analyzed" in output
        assert "drift_events" in output
        assert "ks_statistics" in output
        assert "psi_values" in output
        assert "drift_directions" in output
        assert "window_pairs_analyzed" in output

        assert isinstance(output["drift_detected"], bool)
        assert isinstance(output["drift_magnitude"], float)
        assert isinstance(output["metrics_analyzed"], list)
        assert isinstance(output["drift_events"], list)
        assert isinstance(output["ks_statistics"], dict)
        assert isinstance(output["psi_values"], dict)
        assert isinstance(output["drift_directions"], dict)
        assert isinstance(output["window_pairs_analyzed"], list)

    def test_execute_analyzes_correct_metric(self):
        """Test that the correct metric is listed in metrics_analyzed."""
        result = self.detector.execute(self.test_metric_dataframe)
        output = result.detector_outputs[self.detector.get_detector_id()]
        assert "M-02" in output["metrics_analyzed"]

    # ------------------------------------------------------------------
    # Drift detection
    # ------------------------------------------------------------------

    def test_detects_drift_with_mean_shift(self):
        """Test that drift is detected when there is a clear mean shift."""
        result = self.detector.execute(self.test_metric_dataframe)
        output = result.detector_outputs[self.detector.get_detector_id()]

        # w00->w01: identical, no drift
        # w01->w02: mean shift from 5 to 15, drift expected
        drift_events = output["drift_events"]
        assert len(drift_events) > 0

        # Check that the drift event involves w01->w02
        window_pairs = [e["window_pair"] for e in drift_events]
        assert ["w01", "w02"] in window_pairs

    def test_no_drift_when_identical(self):
        """Test that no drift is detected when windows are identical."""
        identical_df = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {
                    "w00": [5.0] * 10,
                    "w01": [5.0] * 10,
                },
            },
        )
        result = self.detector.execute(identical_df)
        output = result.detector_outputs[self.detector.get_detector_id()]

        assert output["drift_detected"] is False
        assert len(output["drift_events"]) == 0

    def test_drift_magnitude_normalized(self):
        """Test that drift magnitude is in [0, 1]."""
        result = self.detector.execute(self.test_metric_dataframe)
        output = result.detector_outputs[self.detector.get_detector_id()]
        assert 0.0 <= output["drift_magnitude"] <= 1.0

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_insufficient_data_no_drift(self):
        """Test that insufficient data per window yields no drift detection."""
        result = self.detector.execute(self.insufficient_metric_dataframe)
        output = result.detector_outputs[self.detector.get_detector_id()]
        assert output["drift_detected"] is False
        assert len(output["drift_events"]) == 0

    def test_single_window_no_drift(self):
        """Test that single window yields no drift detection."""
        result = self.detector.execute(self.single_window_metric_dataframe)
        output = result.detector_outputs[self.detector.get_detector_id()]
        assert output["drift_detected"] is False

    def test_empty_metrics_no_drift(self):
        """Test that empty metrics yields no drift detection."""
        result = self.detector.execute(self.no_metrics_metric_dataframe)
        output = result.detector_outputs[self.detector.get_detector_id()]
        assert output["drift_detected"] is False
        assert output["metrics_analyzed"] == []

    # ------------------------------------------------------------------
    # Determinism
    # ------------------------------------------------------------------

    def test_deterministic_output(self):
        """Test that the same input produces identical output."""
        result1 = self.detector.execute(self.test_metric_dataframe)
        result2 = self.detector.execute(self.test_metric_dataframe)

        o1 = result1.detector_outputs[self.detector.get_detector_id()]
        o2 = result2.detector_outputs[self.detector.get_detector_id()]

        assert o1["drift_detected"] == o2["drift_detected"]
        assert o1["drift_magnitude"] == o2["drift_magnitude"]
        assert o1["metrics_analyzed"] == o2["metrics_analyzed"]
        assert len(o1["drift_events"]) == len(o2["drift_events"])

        for e1, e2 in zip(o1["drift_events"], o2["drift_events"]):
            assert e1["metric"] == e2["metric"]
            assert e1["window_pair"] == e2["window_pair"]
            assert e1["ks_statistic"] == e2["ks_statistic"]
            assert e1["psi_value"] == e2["psi_value"]
            assert e1["direction"] == e2["direction"]


if __name__ == "__main__":
    pytest.main([__file__])
