"""
Unit tests for Detector Registry.
Tests registry registration, lookup, duplicate prevention, and validation.
"""

import pytest
from miie.processing.detection.registry import DetectorRegistry
from miie.processing.detection.mock_detectors import (
    MockDistributionDriftDetector,
    MockCorrelationBreakdownDetector,
    MockThresholdCompressionDetector
)


class TestDetectorRegistry:
    """Test cases for DetectorRegistry class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.registry = DetectorRegistry()
        self.dist_drift_detector = MockDistributionDriftDetector()
        self.correlation_detector = MockCorrelationBreakdownDetector()
        self.threshold_detector = MockThresholdCompressionDetector()
    
    def test_registry_initialization(self):
        """Test that registry initializes empty."""
        assert len(self.registry.get_registered_ids()) == 0
        assert self.registry.get_all() == []
    
    def test_register_single_detector(self):
        """Test registering a single detector."""
        self.registry.register(self.dist_drift_detector)
        
        assert "D-01" in self.registry.get_registered_ids()
        assert len(self.registry.get_registered_ids()) == 1
        retrieved = self.registry.get("D-01")
        assert retrieved is not None
        assert retrieved.get_detector_id() == "D-01"
    
    def test_register_all_three_detectors(self):
        """Test registering all three required detectors."""
        self.registry.register(self.dist_drift_detector)
        self.registry.register(self.correlation_detector)
        self.registry.register(self.threshold_detector)
        
        registered_ids = set(self.registry.get_registered_ids())
        expected_ids = {"D-01", "D-02", "D-03"}
        assert registered_ids == expected_ids
        assert len(self.registry.get_registered_ids()) == 3
    
    def test_get_detector_by_id(self):
        """Test retrieving detector by ID."""
        self.registry.register(self.dist_drift_detector)
        
        detector = self.registry.get("D-01")
        assert detector is not None
        assert detector.get_detector_id() == "D-01"
        assert detector.get_detector_name() == "Distribution Drift Detector"
        
        # Test getting non-existent detector
        non_existent = self.registry.get("D-99")
        assert non_existent is None
    
    def test_get_all_detectors(self):
        """Test getting all registered detectors."""
        self.registry.register(self.dist_drift_detector)
        self.registry.register(self.correlation_detector)
        
        detectors = self.registry.get_all()
        assert len(detectors) == 2
        
        detector_ids = {d.get_detector_id() for d in detectors}
        assert detector_ids == {"D-01", "D-02"}
    
    def test_is_registered(self):
        """Test checking if detector ID is registered."""
        assert not self.registry.is_registered("D-01")
        
        self.registry.register(self.dist_drift_detector)
        assert self.registry.is_registered("D-01")
        assert not self.registry.is_registered("D-02")
    
    def test_register_invalid_detector_id(self):
        """Test registering detector with invalid ID raises ValueError."""
        # Create detector with invalid ID
        invalid_detector = MockDistributionDriftDetector()
        invalid_detector.detector_id = "D-99"  # Invalid ID
        
        with pytest.raises(ValueError, match="Invalid detector ID"):
            self.registry.register(invalid_detector)
    
    def test_register_duplicate_detector_id(self):
        """Test registering duplicate detector ID raises ValueError."""
        self.registry.register(self.dist_drift_detector)
        
        # Try to register another detector with same ID
        duplicate_detector = MockDistributionDriftDetector()
        
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register(duplicate_detector)
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        self.registry.register(self.dist_drift_detector)
        self.registry.register(self.correlation_detector)
        
        assert len(self.registry.get_registered_ids()) == 2
        
        self.registry.clear()
        
        assert len(self.registry.get_registered_ids()) == 0
        assert self.registry.get_all() == []
