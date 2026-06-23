"""
Detector Registry for MIIE v1.0 Detector Framework.
Manages registration and lookup of D-01 through D-03 detectors.
"""

from typing import Dict, List, Optional
from src.miie.processing.detection.base import BaseDetector


class DetectorRegistry:
    """
    Registry for managing detector instances.
    
    Responsibilities:
    - Register exactly D-01, D-02, D-03
    - Validate detector IDs
    - Prevent duplicates
    - Support lookup by ID
    - No detector logic (only registration and lookup)
    """
    
    def __init__(self):
        """Initialize empty detector registry."""
        self._detectors: Dict[str, BaseDetector] = {}
        self._allowed_ids = {"D-01", "D-02", "D-03"}
    
    def register(self, detector: BaseDetector) -> None:
        """
        Register a detector in the registry.
        
        Args:
            detector: Detector instance to register
            
        Raises:
            ValueError: If detector ID is not allowed or duplicate exists
        """
        detector_id = detector.get_detector_id()
        
        # Validate detector ID
        if detector_id not in self._allowed_ids:
            raise ValueError(
                f"Invalid detector ID: {detector_id}. "
                f"Must be one of {self._allowed_ids}"
            )
        
        # Prevent duplicates
        if detector_id in self._detectors:
            raise ValueError(f"Detector ID {detector_id} already registered")
        
        # Register detector
        self._detectors[detector_id] = detector
    
    def get(self, detector_id: str) -> Optional[BaseDetector]:
        """
        Get detector by ID.
        
        Args:
            detector_id: ID of detector to retrieve
            
        Returns:
            BaseDetector: Detector instance if found, None otherwise
        """
        return self._detectors.get(detector_id)
    
    def get_all(self) -> List[BaseDetector]:
        """
        Get all registered detectors.
        
        Returns:
            List[BaseDetector]: List of all registered detectors
        """
        return list(self._detectors.values())
    
    def get_registered_ids(self) -> List[str]:
        """
        Get list of registered detector IDs.
        
        Returns:
            List[str]: List of registered detector IDs
        """
        return list(self._detectors.keys())
    
    def is_registered(self, detector_id: str) -> bool:
        """
        Check if detector ID is registered.
        
        Args:
            detector_id: ID to check
            
        Returns:
            bool: True if registered, False otherwise
        """
        return detector_id in self._detectors
    
    def clear(self) -> None:
        """Clear all registered detectors (mainly for testing)."""
        self._detectors.clear()
