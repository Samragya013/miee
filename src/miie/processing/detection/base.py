"""
Base Detector class for MIIE v1.0 Detector Framework.
Implements the BaseDetector contract without actual detection mathematics.
"""

from abc import ABC, abstractmethod
from typing import List

from miie.schemas.models import DetectorResult, MetricDataFrame


class BaseDetector(ABC):
    """
    Base detector contract for Day 8 Detector Framework.

    Responsibilities:
    - detector_id
    - detector_name
    - supported_metrics
    - validate_input()
    - execute() returning DetectorResult

    No algorithm implementation - placeholders only.
    """

    def __init__(self, detector_id: str, detector_name: str, supported_metrics: List[str]):
        """
        Initialize base detector.

        Args:
            detector_id: Unique detector identifier (e.g., "D-01")
            detector_name: Human-readable detector name
            supported_metrics: List of metric IDs this detector supports
        """
        self.detector_id = detector_id
        self.detector_name = detector_name
        self.supported_metrics = supported_metrics

    @abstractmethod
    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool:
        """
        Validate that the input MetricDataFrame contains required metrics.

        Args:
            metric_dataframe: Input metrics to validate

        Returns:
            bool: True if input is valid, False otherwise
        """

    @abstractmethod
    def execute(self, metric_dataframe: MetricDataFrame) -> DetectorResult:
        """
        Execute detection logic on input metrics.

        Args:
            metric_dataframe: Input metrics for detection

        Returns:
            DetectorResult: Detection outputs (placeholder implementation)
        """

    def get_detector_id(self) -> str:
        """Get detector ID."""
        return self.detector_id

    def get_detector_name(self) -> str:
        """Get detector name."""
        return self.detector_name

    def get_supported_metrics(self) -> List[str]:
        """Get list of supported metrics."""
        return self.supported_metrics.copy()
