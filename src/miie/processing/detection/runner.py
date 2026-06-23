"""
Detector Runner for MIIE v1.0 Detector Framework.
Executes detectors through registry and collects results.
"""

from typing import List, Optional
from src.miie.schemas.models import MetricDataFrame, DetectorResult
from src.miie.processing.detection.registry import DetectorRegistry
from src.miie.processing.detection.base import BaseDetector


class DetectorRunner:
    """
    Executes detectors and manages detector execution lifecycle.
    
    Responsibilities:
    - Execute detectors through registry
    - Collect DetectorResult objects
    - Handle failures gracefully
    - Maintain deterministic order
    - No scoring, aggregation, or ranking
    """
    
    def __init__(self, registry: DetectorRegistry):
        """
        Initialize detector runner.
        
        Args:
            registry: DetectorRegistry containing registered detectors
        """
        self._registry = registry
    
    def run_all(
        self, 
        metric_dataframe: MetricDataFrame
    ) -> List[DetectorResult]:
        """
        Run all registered detectors on the input metric data.
        
        Args:
            metric_dataframe: Input metrics for detection
            
        Returns:
            List[DetectorResult]: List of detector results in deterministic order
        """
        results = []
        
        # Get detectors in deterministic order (sorted by ID)
        detectors = sorted(
            self._registry.get_all(), 
            key=lambda d: d.get_detector_id()
        )
        
        # Execute each detector
        for detector in detectors:
            try:
                # Validate input before execution
                if detector.validate_input(metric_dataframe):
                    # Execute detector and collect result
                    result = detector.execute(metric_dataframe)
                    results.append(result)
                # If validation fails, we skip the detector
                # In a production system, we might want to log this
            except Exception:
                # Handle failures gracefully - continue with other detectors
                # In a production system, we might want to log the error
                continue
        
        return results
    
    def run_specific(
        self, 
        metric_dataframe: MetricDataFrame,
        detector_ids: List[str]
    ) -> List[DetectorResult]:
        """
        Run specific detectors on the input metric data.
        
        Args:
            metric_dataframe: Input metrics for detection
            detector_ids: List of detector IDs to run
            
        Returns:
            List[DetectorResult]: List of detector results in requested order
        """
        results = []
        
        # Execute detectors in requested order
        for detector_id in detector_ids:
            detector = self._registry.get(detector_id)
            if detector is not None:
                try:
                    # Validate input before execution
                    if detector.validate_input(metric_dataframe):
                        # Execute detector and collect result
                        result = detector.execute(metric_dataframe)
                        results.append(result)
                except Exception:
                    # Handle failures gracefully - continue with other detectors
                    continue
        
        return results
