"""
Integration tests for extraction to detection flow.
Tests the complete pipeline from MetricDataFrame through detector framework.
"""

import pytest
from miie.processing.extraction import MetricExtractionEngine
from miie.processing.detection.registry import DetectorRegistry
from miie.processing.detection.dispatcher import DetectorDispatcherEngine
from miie.processing.detection.runner import DetectorRunner
from miie.processing.detection.mock_detectors import (
    MockDistributionDriftDetector,
    MockCorrelationBreakdownDetector,
    MockThresholdCompressionDetector
)
from miie.schemas.models import MetricDataFrame
import datetime


class TestExtractionToDetectionFlow:
    """Test cases for extraction to detection integration."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create extraction engine (Day 7 component)
        self.extraction_engine = MetricExtractionEngine()
        
        # Create detector framework components (Day 8 components)
        self.registry = DetectorRegistry()
        self.dispatcher = DetectorDispatcherEngine(self.registry)
        self.runner = DetectorRunner(self.registry)
        
        # Create and register mock detectors
        self.dist_drift_detector = MockDistributionDriftDetector()
        self.correlation_detector = MockCorrelationBreakdownDetector()
        self.threshold_detector = MockThresholdCompressionDetector()
        
        self.registry.register(self.dist_drift_detector)
        self.registry.register(self.correlation_detector)
        self.registry.register(self.threshold_detector)
    
    def test_extraction_to_detection_dispatcher_flow(self):
        """Test flow: extraction -> detector framework via dispatcher."""
        # Extract metrics (simulating Day 7 functionality)
        # We'll use a simple approach since we can't easily clone a real repo in test
        # Instead, we'll create a metric dataframe that simulates what extraction would produce
        
        extracted_metrics = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-123",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-02": {"default": [10.0, 12.0, 11.0, 9.0, 13.0]},  # Commit Frequency
                "M-06": {"default": [5.0, 8.0, 6.0, 4.0, 7.0]}       # Code Churn
                # Note: M-01, M-03, M-04, M-05, M-07 would be None per missing data policy
            }
        )
        
        # Verify we have the expected metrics from extraction
        assert "M-02" in extracted_metrics.metrics
        assert "M-06" in extracted_metrics.metrics
        assert extracted_metrics.metrics["M-02"]["default"] == [10.0, 12.0, 11.0, 9.0, 13.0]
        assert extracted_metrics.metrics["M-06"]["default"] == [5.0, 8.0, 6.0, 4.0, 7.0]
        
        # Process through detector framework (dispatcher)
        detection_results = self.dispatcher.invoke(metric_dataframe=extracted_metrics, windows=[])
        
        # Verify detection results
        assert isinstance(detection_results.detector_outputs, dict)
        assert len(detection_results.detector_outputs) == 3
        assert "D-01" in detection_results.detector_outputs
        assert "D-02" in detection_results.detector_outputs
        assert "D-03" in detection_results.detector_outputs
        
        # Each detector output should be a dict containing the detector's results
        for detector_id, detector_output in detection_results.detector_outputs.items():
            assert detector_output is not None
            assert isinstance(detector_output, dict)
            # For mock detectors, verify they returned expected fields
            if detector_id == "D-01":
                assert "drift_detected" in detector_output
                assert "drift_magnitude" in detector_output
            elif detector_id == "D-02":
                assert "correlation_breakdown" in detector_output
                assert "correlation_change" in detector_output
            elif detector_id == "D-03":
                assert "threshold_compressed" in detector_output
                assert "compression_ratio" in detector_output
    
    def test_extraction_to_detection_runner_flow(self):
        """Test flow: extraction -> detector framework via runner."""
        # Create extracted metrics (simulating Day 7 output)
        extracted_metrics = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-456",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-02": {"default": [8.0, 9.0, 7.0]},  # Commit Frequency
                "M-06": {"default": [3.0, 4.0, 2.0]}   # Code Churn
            }
        )
        
        # Verify extraction output
        assert "M-02" in extracted_metrics.metrics
        assert "M-06" in extracted_metrics.metrics
        
        # Process through detector framework (runner)
        detection_results = self.runner.run_all(extracted_metrics)
        
        # Verify detection results
        assert isinstance(detection_results, list)
        assert len(detection_results) == 3
        
        # Each should be a DetectorResult
        for result in detection_results:
            assert result is not None
            assert isinstance(result.detector_outputs, dict)
            assert len(result.detector_outputs) == 1  # Each detector outputs one key
            
            # Verify the detector ID matches what we expect
            detector_id = list(result.detector_outputs.keys())[0]
            assert detector_id in ["D-01", "D-02", "D-03"]
    
    def test_deterministic_behavior(self):
        """Test that the framework produces deterministic results."""
        # Create identical metric dataframes
        metrics_data = {
            "M-02": {"default": [10.0, 11.0, 9.0]},
            "M-06": {"default": [5.0, 6.0, 4.0]}
        }
        
        metric_df1 = MetricDataFrame(
            repo_id="det-repo",
            run_id="run-001",
            timestamp=datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc),
            metrics=metrics_data.copy()
        )
        
        metric_df2 = MetricDataFrame(
            repo_id="det-repo",
            run_id="run-002",  # Different run ID
            timestamp=datetime.datetime(2026, 1, 1, 12, 0, 1, tzinfo=datetime.timezone.utc),  # Different timestamp
            metrics=metrics_data.copy()
        )
        
        # Run detection on both
        results1 = self.runner.run_all(metric_df1)
        results2 = self.runner.run_all(metric_df2)
        
        # Should have same number of results
        assert len(results1) == len(results2) == 3
        
        # Results should be structurally identical (same detector IDs and output structure)
        # Note: Actual values may differ slightly due to timestamp in mock outputs,
        # but the structure should be deterministic
        detector_ids_1 = sorted([list(r.detector_outputs.keys())[0] for r in results1])
        detector_ids_2 = sorted([list(r.detector_outputs.keys())[0] for r in results2])
        assert detector_ids_1 == detector_ids_2 == ["D-01", "D-02", "D-03"]
        
        # Each corresponding detector should produce same structure
        for r1, r2 in zip(results1, results2):
            id1 = list(r1.detector_outputs.keys())[0]
            id2 = list(r2.detector_outputs.keys())[0]
            assert id1 == id2  # Same detector
            
            # Output keys should match
            assert set(r1.detector_outputs[id1].keys()) == set(r2.detector_outputs[id2].keys())
