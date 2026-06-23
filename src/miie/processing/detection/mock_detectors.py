"""
Mock Detectors for MIIE v1.0 Detector Framework testing.
Returns schema-valid DetectorResult objects with deterministic values.
No real detection mathematics implemented.
"""

from typing import Dict, List, Optional, Any
from src.miie.processing.detection.base import BaseDetector
from src.miie.processing.detection.dispatcher import DetectorDispatcherEngine
from src.miie.processing.detection.registry import DetectorRegistry
from src.miie.schemas.models import DetectorResult, DetectorResults, MetricDataFrame


class MockDistributionDriftDetector(BaseDetector):
    """
    Mock detector for distribution drift detection (D-01).
    Returns deterministic placeholder values.
    No actual distribution drift mathematics implemented.
    """
    
    def __init__(self):
        super().__init__(
            detector_id="D-01",
            detector_name="Distribution Drift Detector",
            supported_metrics=["M-02", "M-06"]  # Commit Frequency and Code Churn
        )
    
    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool:
        """
        Validate that required metrics (M-02, M-06) are present.
        
        Args:
            metric_dataframe: Input metrics to validate
            
        Returns:
            bool: True if M-02 and M-06 metrics are present
        """
        required_metrics = {"M-02", "M-06"}
        available_metrics = set(metric_dataframe.metrics.keys())
        return required_metrics.issubset(available_metrics)
    
    def execute(self, metric_dataframe: MetricDataFrame) -> DetectorResult:
        """
        Execute mock distribution drift detection.
        
        Args:
            metric_dataframe: Input metrics for detection
            
        Returns:
            DetectorResult: Schema-valid detector result with placeholder values
        """
        # Return deterministic placeholder result
        # No actual detection mathematics - just placeholder structure
        return DetectorResult(
            detector_outputs={
                "D-01": {
                    "drift_detected": False,
                    "drift_magnitude": 0.0,
                    "window_size": 10,
                    "timestamp": metric_dataframe.timestamp.isoformat()
                }
            }
        )


class MockCorrelationBreakdownDetector(BaseDetector):
    """
    Mock detector for correlation breakdown detection (D-02).
    Returns deterministic placeholder values.
    No actual correlation mathematics implemented.
    """
    
    def __init__(self):
        super().__init__(
            detector_id="D-02",
            detector_name="Correlation Breakdown Detector",
            supported_metrics=["M-02", "M-06"]  # Commit Frequency and Code Churn
        )
    
    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool:
        """
        Validate that required metrics (M-02, M-06) are present.
        
        Args:
            metric_dataframe: Input metrics to validate
            
        Returns:
            bool: True if M-02 and M-06 metrics are present
        """
        required_metrics = {"M-02", "M-06"}
        available_metrics = set(metric_dataframe.metrics.keys())
        return required_metrics.issubset(available_metrics)
    
    def execute(self, metric_dataframe: MetricDataFrame) -> DetectorResult:
        """
        Execute mock correlation breakdown detection.
        
        Args:
            metric_dataframe: Input metrics for detection
            
        Returns:
            DetectorResult: Schema-valid detector result with placeholder values
        """
        # Return deterministic placeholder result
        # No actual correlation mathematics - just placeholder structure
        return DetectorResult(
            detector_outputs={
                "D-02": {
                    "correlation_breakdown": False,
                    "correlation_change": 0.0,
                    "baseline_correlation": 0.0,
                    "current_correlation": 0.0,
                    "timestamp": metric_dataframe.timestamp.isoformat()
                }
            }
        )


class MockThresholdCompressionDetector(BaseDetector):
    """
    Mock detector for threshold compression detection (D-03).
    Returns deterministic placeholder values.
    No actual threshold mathematics implemented.
    """
    
    def __init__(self):
        super().__init__(
            detector_id="D-03",
            detector_name="Threshold Compression Detector",
            supported_metrics=["M-02", "M-06"]  # Commit Frequency and Code Churn
        )
    
    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool:
        """
        Validate that required metrics (M-02, M-06) are present.
        
        Args:
            metric_dataframe: Input metrics to validate
            
        Returns:
            bool: True if M-02 and M-06 metrics are present
        """
        required_metrics = {"M-02", "M-06"}
        available_metrics = set(metric_dataframe.metrics.keys())
        return required_metrics.issubset(available_metrics)
    
    def execute(self, metric_dataframe: MetricDataFrame) -> DetectorResult:
        """
        Execute mock threshold compression detection.
        
        Args:
            metric_dataframe: Input metrics for detection
            
        Returns:
            DetectorResult: Schema-valid detector result with placeholder values
        """
        # Return deterministic placeholder result
        # No actual threshold mathematics - just placeholder structure
        return DetectorResult(
            detector_outputs={
                "D-03": {
                    "threshold_compressed": False,
                    "compression_ratio": 1.0,
                    "original_threshold": 0.5,
                    "current_threshold": 0.5,
                    "timestamp": metric_dataframe.timestamp.isoformat()
                }
            }
        )


class MockDetectorEngine(DetectorDispatcherEngine):
    """
    Mock detector engine for testing.
    Returns deterministic placeholder DetectorResults.
    """

    def __init__(self):
        # Create a registry with mock detectors
        registry = DetectorRegistry()
        registry.register(MockDistributionDriftDetector())
        registry.register(MockCorrelationBreakdownDetector())
        registry.register(MockThresholdCompressionDetector())
        super().__init__(registry)

    def invoke(
        self,
        metric_dataframe: MetricDataFrame,
        windows: List[object],  # List[WindowDefinition] but avoiding circular import
        detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
        enabled_detectors: Optional[List[str]] = None,
        seed: int = 42,
    ) -> DetectorResults:
        """Return a fixed DetectorResults for testing."""
        # Return fixed detector outputs that match expected test structure
        return DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": False, "drift_magnitude": 0.0},
                "D-02": {"correlation_breakdown": False, "correlation_change": 0.0},
                "D-03": {"threshold_compressed": False, "compression_ratio": 1.0}
            }
        )
