"""
Unit tests for D02 Correlation Breakdown Detector.
"""

import datetime

import numpy as np
import pytest

from miie.processing.detection.correlation_breakdown_detector import (
    CorrelationBreakdownDetector,
)
from miie.schemas.models import MetricDataFrame


class TestCorrelationBreakdownDetector:
    """Test cases for CorrelationBreakdownDetector."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = CorrelationBreakdownDetector()

        # Create test metric dataframe with known correlations
        # We'll create data that should trigger a sign reversal breakdown
        self.test_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {  # Commit Frequency
                    "w00": [10, 12, 11, 13, 12, 11, 10, 12, 13, 11],  # 10 observations
                    "w01": [10, 12, 11, 13, 12, 11, 10, 12, 13, 11],  # Same as w00
                    "w02": [11, 9, 12, 8, 13, 7, 14, 6, 15, 5],  # Inverse trend
                },
                "M-06": {  # Code Churn
                    "w00": [5, 6, 4, 7, 5, 6, 4, 7, 5, 6],  # 10 observations
                    "w01": [5, 6, 4, 7, 5, 6, 4, 7, 5, 6],  # Same as w00
                    "w02": [4, 6, 5, 7, 3, 8, 2, 9, 1, 10],  # Inverse trend
                },
            },
        )

        # Create test metric dataframe with insufficient data
        self.insufficient_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {"w00": [1, 2, 3]},  # Only 3 observations (<10 required)
                "M-06": {"w00": [1, 2, 3]},  # Only 3 observations
            },
        )

        # Create test metric dataframe with only one metric
        self.single_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={
                "M-02": {
                    "w00": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "w01": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                }
                # M-06 missing
            },
        )

    def test_detector_initialization(self):
        """Test that detector initializes correctly."""
        assert self.detector.get_detector_id() == "D-02"
        assert self.detector.get_detector_name() == "Correlation Breakdown Detector"
        supported_metrics = self.detector.get_supported_metrics()
        assert len(supported_metrics) == 7
        assert "M-02" in supported_metrics
        assert "M-06" in supported_metrics

    def test_validate_input_sufficient_metrics(self):
        """Test input validation with sufficient metrics."""
        assert self.detector.validate_input(self.test_metric_dataframe) == True

    def test_validate_input_insufficient_metrics(self):
        """Test input validation with only one metric."""
        assert self.detector.validate_input(self.single_metric_dataframe) == False

    def test_validate_input_insufficient_data(self):
        """Test input validation passes (validation only checks metric presence, not data size)."""
        # The validate_input method only checks if at least two metrics are present
        # It does not check window sizes or data points - those are checked in execute
        assert self.detector.validate_input(self.insufficient_metric_dataframe) == True

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
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        # Check required fields exist
        assert "breakdown_detected" in detector_output
        assert "breakdown_type" in detector_output
        assert "metric_pairs_analyzed" in detector_output
        assert "breakdown_events" in detector_output
        assert "pearson_trajectories" in detector_output
        assert "spearman_trajectories" in detector_output
        assert "confidence_intervals" in detector_output
        assert "window_pairs_flagged" in detector_output

        # Check field types
        assert isinstance(detector_output["breakdown_detected"], bool)
        assert detector_output["breakdown_type"] is None or isinstance(detector_output["breakdown_type"], str)
        assert isinstance(detector_output["metric_pairs_analyzed"], list)
        assert isinstance(detector_output["breakdown_events"], list)
        assert isinstance(detector_output["pearson_trajectories"], dict)
        assert isinstance(detector_output["spearman_trajectories"], dict)
        assert isinstance(detector_output["confidence_intervals"], dict)
        assert isinstance(detector_output["window_pairs_flagged"], list)

        # Check that we analyzed the expected metric pair
        assert "M-02_M-06" in detector_output["metric_pairs_analyzed"]
        assert "M-06_M-02" not in detector_output["metric_pairs_analyzed"]  # Only i<j pairs

    def test_execute_breakdown_detection(self):
        """Test that breakdown is detected in our test data."""
        result = self.detector.execute(self.test_metric_dataframe)
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        # Our test data should show a sign reversal between w01 and w02
        # w00 and w01: same data -> correlation ~1
        # w01 and w02: inverse trend -> correlation ~-1
        # This should trigger sign_reversal detection

        # We expect at least one breakdown event
        assert len(detector_output["breakdown_events"]) > 0

        # Check that we detected sign reversal (highest priority)
        if detector_output["breakdown_detected"]:
            # The breakdown type should be sign_reversal due to our test data
            # Note: Depending on the exact correlations, it might also trigger sudden_drop
            # but sign_reversal has higher priority in our implementation
            breakdown_types = [event["breakdown_type"] for event in detector_output["breakdown_events"]]
            assert "sign_reversal" in breakdown_types or "sudden_drop" in breakdown_types

    def test_execute_no_breakdown_when_insufficient_data(self):
        """Test that no breakdown is detected when there's insufficient data."""
        result = self.detector.execute(self.insufficient_metric_dataframe)
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        # With only 3 observations per window (<10 required), no breakdowns should be detected
        assert detector_output["breakdown_detected"] == False
        assert detector_output["breakdown_type"] is None
        assert len(detector_output["breakdown_events"]) == 0
        assert len(detector_output["window_pairs_flagged"]) == 0

    def test_deterministic_output(self):
        """Test that the same input produces identical output."""
        result1 = self.detector.execute(self.test_metric_dataframe)
        result2 = self.detector.execute(self.test_metric_dataframe)

        # The detector outputs should be identical
        output1 = result1.detector_outputs[self.detector.get_detector_id()]
        output2 = result2.detector_outputs[self.detector.get_detector_id()]

        # Compare key fields
        assert output1["breakdown_detected"] == output2["breakdown_detected"]
        assert output1["breakdown_type"] == output2["breakdown_type"]
        assert output1["metric_pairs_analyzed"] == output2["metric_pairs_analyzed"]
        # Compare breakdown events (should be identical)
        assert len(output1["breakdown_events"]) == len(output2["breakdown_events"])
        for i in range(len(output1["breakdown_events"])):
            event1 = output1["breakdown_events"][i]
            event2 = output2["breakdown_events"][i]
            assert event1["metric_pair"] == event2["metric_pair"]
            assert event1["window_pair"] == event2["window_pair"]
            assert event1["breakdown_type"] == event2["breakdown_type"]
            # Compare numeric values with tolerance - check pearsons_values as they're common to all event types
            assert "pearson_values" in event1 and "pearson_values" in event2
            assert event1["pearson_values"] == event2["pearson_values"]

        # Compare trajectories
        for pair_key in output1["pearson_trajectories"]:
            assert pair_key in output2["pearson_trajectories"]
            assert np.allclose(
                output1["pearson_trajectories"][pair_key],
                output2["pearson_trajectories"][pair_key],
            )
        for pair_key in output1["spearman_trajectories"]:
            assert pair_key in output2["spearman_trajectories"]
            assert np.allclose(
                output1["spearman_trajectories"][pair_key],
                output2["spearman_trajectories"][pair_key],
            )

    def test_execute_with_no_metrics(self):
        """Test execution with no metrics present."""
        empty_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metrics={},
        )
        result = self.detector.execute(empty_dataframe)
        detector_output = result.detector_outputs[self.detector.get_detector_id()]

        assert detector_output["breakdown_detected"] == False
        assert detector_output["breakdown_type"] is None
        assert detector_output["metric_pairs_analyzed"] == []
        assert len(detector_output["breakdown_events"]) == 0


if __name__ == "__main__":
    pytest.main([__file__])
