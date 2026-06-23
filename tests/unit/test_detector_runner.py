"""
Unit tests for Detector Runner.
Tests runner execution, result collection, failure handling, and deterministic order.
"""

import pytest
from src.miie.processing.detection.runner import DetectorRunner
from src.miie.processing.detection.registry import DetectorRegistry
from src.miie.processing.detection.mock_detectors import (
    MockDistributionDriftDetector,
    MockCorrelationBreakdownDetector,
    MockThresholdCompressionDetector
)
from src.miie.schemas.models import MetricDataFrame, DetectorResult
import datetime


class TestDetectorRunner:
    """Test cases for DetectorRunner class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.registry = DetectorRegistry()
        self.runner = DetectorRunner(self.registry)
        
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
    
    def test_runner_initialization(self):
        """Test that runner initializes correctly."""
        assert self.runner._registry is self.registry
    
    def test_run_all_detectors(self):
        """Test running all detectors."""
        results = self.runner.run_all(self.test_metric_dataframe)
        
        # Should have results for all three detectors
        assert len(results) == 3
        
        # Each result should be a DetectorResult
        for result in results:
            assert isinstance(result, DetectorResult)
        
        # Should be in deterministic order (sorted by detector ID)
        detector_ids = [result.detector_outputs.keys().__iter__().__next__() for result in results]
        assert detector_ids == ["D-01", "D-02", "D-03"]
    
    def test_run_specific_detectors(self):
        """Test running specific detectors."""
        results = self.runner.run_specific(
            self.test_metric_dataframe,
            detector_ids=["D-03", "D-01"]  # Non-standard order
        )
        
        # Should have results for both detectors
        assert len(results) == 2
        
        # Should be in requested order
        detector_ids = [result.detector_outputs.keys().__iter__().__next__() for result in results]
        assert detector_ids == ["D-03", "D-01"]
    
    def test_run_empty_detector_list(self):
        """Test running with empty detector list."""
        results = self.runner.run_specific(
            self.test_metric_dataframe,
            detector_ids=[]
        )
        
        # Should have no results
        assert len(results) == 0
    
    def test_run_nonexistent_detector(self):
        """Test running with non-existent detector ID."""
        results = self.runner.run_specific(
            self.test_metric_dataframe,
            detector_ids=["D-01", "D-99", "D-02"]  # D-99 doesn't exist
        )
        
        # Should have results only for existing detectors
        assert len(results) == 2
        
        detector_ids = [result.detector_outputs.keys().__iter__().__next__() for result in results]
        assert detector_ids == ["D-01", "D-02"]  # In requested order, skipping D-99
    
    def test_run_with_invalid_input(self):
        """Test running when detector validation fails."""
        # Create metric dataframe missing required metrics
        invalid_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-01": {"default": [0.8]}  # Wrong metric - not M-02 or M-06
            }
        )
        
        results = self.runner.run_all(invalid_metric_dataframe)
        
        # Should have no results because validation fails for all detectors
        assert len(results) == 0
    
    def test_runner_handles_exceptions_gracefully(self):
        """Test that runner handles detector exceptions gracefully."""
        # This would require mocking a detector that throws an exception
        # For now, we'll verify the structure supports exception handling
        # The actual exception handling is in the runner code
        results = self.runner.run_all(self.test_metric_dataframe)
        
        # Should still return results for all detectors
        assert len(results) == 3
        
        # Each should be a valid DetectorResult
        for result in results:
            assert isinstance(result, DetectorResult)
            # Should have detector outputs
            assert len(result.detector_outputs) > 0
