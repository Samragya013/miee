"""
Unit tests for Detector Dispatcher.
Tests dispatcher routing, orchestration, and validation.
"""

import pytest
from src.miie.processing.detection.dispatcher import DetectorDispatcherEngine
from src.miie.processing.detection.registry import DetectorRegistry
from src.miie.processing.detection.mock_detectors import (
    MockDistributionDriftDetector,
    MockCorrelationBreakdownDetector,
    MockThresholdCompressionDetector
)
from src.miie.schemas.models import MetricDataFrame
import datetime


class TestDetectorDispatcher:
    """Test cases for DetectorDispatcher class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.registry = DetectorRegistry()
        self.dispatcher = DetectorDispatcherEngine(self.registry)
        
        # Create mock detectors
        self.dist_drift_detector = MockDistributionDriftDetector()
        self.correlation_detector = MockCorrelationBreakdownDetector()
        self.threshold_detector = MockThresholdCompressionDetector()
        
        # Register detectors
        self.registry.register(self.dist_drift_detector)
        self.registry.register(self.correlation_detector)
        self.registry.register(self.threshold_detector)
        
        # Create test metric dataframe
        self.test_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-02": {"default": [10.0, 12.0, 11.0]},  # Commit Frequency
                "M-06": {"default": [5.0, 8.0, 6.0]}       # Code Churn
            }
        )
    
    def test_dispatcher_initialization(self):
        """Test that dispatcher initializes correctly."""
        assert self.dispatcher._registry is self.registry
    
    def test_dispatch_all_detectors(self):
        """Test dispatching to all detectors."""
        results = self.dispatcher.invoke(metric_dataframe=self.test_metric_dataframe, windows=[])
        
        # Should have results for all three detectors
        assert len(results.detector_outputs) == 3
        assert "D-01" in results.detector_outputs
        assert "D-02" in results.detector_outputs
        assert "D-03" in results.detector_outputs
        
        # Each result should be a DetectorResult
        assert results.detector_outputs["D-01"] is not None
        assert results.detector_outputs["D-02"] is not None
        assert results.detector_outputs["D-03"] is not None
    
    def test_dispatch_specific_detectors(self):
        """Test dispatching to specific enabled detectors."""
        results = self.dispatcher.invoke(
            metric_dataframe=self.test_metric_dataframe,
            windows=[],
            enabled_detectors=["D-01", "D-03"]
        )
        
        # Should have results only for D-01 and D-03
        assert len(results.detector_outputs) == 2
        assert "D-01" in results.detector_outputs
        assert "D-03" in results.detector_outputs
        assert "D-02" not in results.detector_outputs  # Not enabled
    
    def test_dispatch_nonexistent_detector(self):
        """Test dispatching with non-existent detector ID in enabled list."""
        results = self.dispatcher.invoke(
            metric_dataframe=self.test_metric_dataframe,
            windows=[],
            enabled_detectors=["D-01", "D-99"]  # D-99 doesn't exist
        )
        
        # Should only have result for D-01
        assert len(results.detector_outputs) == 1
        assert "D-01" in results.detector_outputs
        assert "D-99" not in results.detector_outputs
    
    def test_dispatch_empty_enabled_list(self):
        """Test dispatching with empty enabled detectors list."""
        results = self.dispatcher.invoke(
            metric_dataframe=self.test_metric_dataframe,
            windows=[],
            enabled_detectors=[]
        )
        
        # Should have no results
        assert len(results.detector_outputs) == 0
    
    def test_dispatch_with_invalid_input(self):
        """Test dispatching when detector validation fails."""
        # Create metric dataframe missing required metrics
        invalid_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-01": {"default": [0.8]}  # Wrong metric - not M-02 or M-06
            }
        )

        results = self.dispatcher.invoke(metric_dataframe=invalid_metric_dataframe, windows=[])

        # Should have results for all detectors but marked as skipped
        assert len(results.detector_outputs) == 3
        assert "D-01" in results.detector_outputs
        assert "D-02" in results.detector_outputs
        assert "D-03" in results.detector_outputs

        # All should be marked as skipped due to validation failure
        for det_id in ["D-01", "D-02", "D-03"]:
            assert results.detector_outputs[det_id]["status"] == "skipped"
            assert results.detector_outputs[det_id]["reason"] == "input validation failed"
    
    def test_dispatch_returns_detector_results_type(self):
        """Test that dispatch returns DetectorResults object."""
        results = self.dispatcher.invoke(metric_dataframe=self.test_metric_dataframe, windows=[])

        # Check that it's the correct type
        from src.miie.schemas.models import DetectorResults
        assert isinstance(results, DetectorResults)
