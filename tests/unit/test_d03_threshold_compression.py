"""
Unit tests for D03 Threshold Compression Detector.
"""
import numpy as np
import pytest
from miie.processing.detection.threshold_compression_detector import (
    ThresholdCompressionDetector
)
from miie.schemas.models import MetricDataFrame
import datetime


class TestThresholdCompressionDetector:
    """Test cases for ThresholdCompressionDetector."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = ThresholdCompressionDetector()

        # Create test metric dataframe with known threshold compression
        # We'll create data that should trigger compression around threshold 50
        self.test_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {  # Some metric
                    "w00": [48, 49, 50, 51, 52] * 4,  # 20 observations around 50
                    "w01": [48, 49, 50, 51, 52] * 4,  # Same as w00
                    "w02": [10, 20, 30, 40, 50] * 4   # Spread out, but with 50s
                },
                "M-06": {  # Another metric
                    "w00": [30, 35, 40, 45, 50] * 4,  # 20 observations
                    "w01": [30, 35, 40, 45, 50] * 4,  # Same as w00
                    "w02": [50, 50, 50, 50, 50] * 4   # All 50s - strong compression
                }
            }
        )

        # Create test metric dataframe with insufficient data per window (<20)
        self.insufficient_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {
                    "w00": [1, 2, 3]  # Only 3 observations (<20 required)
                },
                "M-06": {
                    "w00": [1, 2, 3]  # Only 3 observations
                }
            }
        )

        # Create test metric dataframe with only one metric
        self.single_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {
                    "w00": [1, 2, 3, 4, 5] * 4,  # 20 observations
                    "w01": [1, 2, 3, 4, 5] * 4   # 20 observations
                }
                # M-06 missing
            }
        )

        # Create test metric dataframe with no metrics
        self.empty_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={}
        )

    def test_detector_initialization(self):
        """Test that detector initializes correctly."""
        assert self.detector.get_detector_id() == "D-03"
        assert self.detector.get_detector_name() == "Threshold Compression Detector"
        supported_metrics = self.detector.get_supported_metrics()
        assert len(supported_metrics) == 7
        assert "M-02" in supported_metrics
        assert "M-06" in supported_metrics

    def test_validate_input_sufficient_metrics(self):
        """Test input validation with sufficient metrics."""
        assert self.detector.validate_input(self.test_metric_dataframe) == True

    def test_validate_input_insufficient_metrics(self):
        """Test input validation with only one metric."""
        # For D03, at least one metric is sufficient
        assert self.detector.validate_input(self.single_metric_dataframe) == True

    def test_validate_input_no_metrics(self):
        """Test input validation with no metrics."""
        assert self.detector.validate_input(self.empty_metric_dataframe) == False

    def test_validate_input_insufficient_data(self):
        """Test input validation passes (validation only checks metric presence, not data size)."""
        # The validate_input method only checks if at least one metric is present
        # It does not check window sizes or data points - those are checked in execute
        assert self.detector.validate_input(self.insufficient_metric_dataframe) == True

    def test_execute_returns_detector_result(self):
        """Test that execute returns a DetectorResult."""
        result = self.detector.execute(self.test_metric_dataframe)
        from miie.schemas.models import DetectorResult
        assert isinstance(result, DetectorResult)
        assert hasattr(result, 'detector_outputs')
        assert self.detector.get_detector_id() in result.detector_outputs

    def test_execute_output_structure(self):
        """Test that execute returns the expected output structure."""
        result = self.detector.execute(self.test_metric_dataframe)
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        # Check required fields exist
        assert "compression_detected" in detector_output
        assert "compression_index" in detector_output
        assert "metrics_analyzed" in detector_output
        assert "compression_events" in detector_output
        assert "thresholds_used" in detector_output
        assert "excess_mass_z_scores" in detector_output
        assert "dip_test_statistics" in detector_output
        assert "dip_test_p_values" in detector_output
        assert "windows_analyzed" in detector_output

        # Check field types
        assert isinstance(detector_output["compression_detected"], bool)
        assert isinstance(detector_output["compression_index"], float)
        assert isinstance(detector_output["metrics_analyzed"], list)
        assert isinstance(detector_output["compression_events"], list)
        assert isinstance(detector_output["thresholds_used"], dict)
        assert isinstance(detector_output["excess_mass_z_scores"], dict)
        assert isinstance(detector_output["dip_test_statistics"], dict)
        assert isinstance(detector_output["dip_test_p_values"], dict)
        assert isinstance(detector_output["windows_analyzed"], list)

        # Check that we analyzed the expected metric pairs
        assert "M-02" in detector_output["metrics_analyzed"]
        assert "M-06" in detector_output["metrics_analyzed"]

    def test_execute_compression_detection(self):
        """Test that compression is detected in our test data."""
        result = self.detector.execute(self.test_metric_dataframe)
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        # Our test data should show compression, especially in M-06 w02 (all 50s)
        # We expect at least one compression event
        assert detector_output["compression_detected"] == True
        assert len(detector_output["compression_events"]) > 0
        assert detector_output["compression_index"] >= 0.0
        assert detector_output["compression_index"] <= 1.0

        # Check that we have events for the metrics we expect
        compression_metrics = [event["metric"] for event in detector_output["compression_events"]]
        assert "M-02" in compression_metrics or "M-06" in compression_metrics

        # Check that compression events have required fields
        for event in detector_output["compression_events"]:
            assert "metric" in event
            assert "threshold" in event
            assert "window" in event
            assert event["compression_detected"] == True
            assert "compression_index" in event
            assert "excess_mass_z_score" in event
            assert "dip_test_statistic" in event
            assert "dip_test_p_value" in event
            assert "epsilon" in event
            assert "sample_size" in event
            assert "hypothesized_cause" in event

    def test_execute_no_compression_when_insufficient_data(self):
        """Test that no compression is detected when there's insufficient data per window."""
        result = self.detector.execute(self.insufficient_metric_dataframe)
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        # With only 3 observations per window (<20 required), no compression should be detected
        assert detector_output["compression_detected"] == False
        assert detector_output["compression_index"] == 0.0
        assert len(detector_output["compression_events"]) == 0
        assert len(detector_output["windows_analyzed"]) == 0
        # Note: thresholds_used and other dicts may still be populated because we still
        # compute thresholds, but we skip windows due to insufficient data

    def test_execute_with_no_metrics(self):
        """Test execution with no metrics present."""
        result = self.detector.execute(self.empty_metric_dataframe)
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        assert detector_output["compression_detected"] == False
        assert detector_output["compression_index"] == 0.0
        assert detector_output["metrics_analyzed"] == []
        assert len(detector_output["compression_events"]) == 0
        assert detector_output["thresholds_used"] == {}
        assert detector_output["excess_mass_z_scores"] == {}
        assert detector_output["dip_test_statistics"] == {}
        assert detector_output["dip_test_p_values"] == {}
        assert detector_output["windows_analyzed"] == []

    def test_deterministic_output(self):
        """Test that the same input produces identical output."""
        result1 = self.detector.execute(self.test_metric_dataframe)
        result2 = self.detector.execute(self.test_metric_dataframe)

        # The detector outputs should be identical
        output1 = result1.detector_outputs[self.detector.get_detector_id()]
        output2 = result2.detector_outputs[self.detector.get_detector_id()]

        # Compare key fields
        assert output1["compression_detected"] == output2["compression_detected"]
        assert output1["compression_index"] == output2["compression_index"]
        assert output1["metrics_analyzed"] == output2["metrics_analyzed"]
        # Compare compression events (should be identical)
        assert len(output1["compression_events"]) == len(output2["compression_events"])
        for i in range(len(output1["compression_events"])):
            event1 = output1["compression_events"][i]
            event2 = output2["compression_events"][i]
            assert event1["metric"] == event2["metric"]
            assert event1["threshold"] == event2["threshold"]
            assert event1["window"] == event2["window"]
            assert event1["compression_index"] == event2["compression_index"]
            assert event1["excess_mass_z_score"] == event2["excess_mass_z_score"]
            assert event1["dip_test_statistic"] == event2["dip_test_statistic"]
            assert event1["dip_test_p_value"] == event2["dip_test_p_value"]
            # note: hypothesized_cause may be the same if deterministic

if __name__ == "__main__":
    pytest.main([__file__])