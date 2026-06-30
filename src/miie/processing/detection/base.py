"""
Base Detector class for MIIE v1.0 Detector Framework.
Implements the BaseDetector contract without actual detection mathematics.

Extended in v1.5 with detect_observations() for observation-window-aware
detectors. Legacy execute(MetricDataFrame) is preserved for backward
compatibility via the DetectorAdapter.

Reference: IMS-v1.0 Phase 5, DES-v2.0 §16
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from miie.schemas.models import DetectorResult, MetricDataFrame


class BaseDetector(ABC):
    """
    Base detector contract for Day 8 Detector Framework.

    Responsibilities:
    - detector_id
    - detector_name
    - supported_metrics
    - validate_input()
    - execute() returning DetectorResult (legacy, MetricDataFrame)
    - detect_observations() returning DetectorResult (v1.5, ObservationWindow)

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
        Execute detection logic on input metrics (legacy path).

        Args:
            metric_dataframe: Input metrics for detection

        Returns:
            DetectorResult: Detection outputs (placeholder implementation)
        """

    def detect_observations(
        self,
        windows: List[Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> DetectorResult:
        """Execute detection on ObservationWindow data (v1.5 path).

        Subclasses should override this to consume ObservationWindows
        directly. The default implementation returns an empty result
        so that not-yet-migrated detectors remain functional.

        Args:
            windows: List of ObservationWindow objects containing
                     per-commit observations.
            config: Optional detector-specific configuration overrides.

        Returns:
            DetectorResult with detection outputs.
        """
        # Default: empty result (not implemented yet)
        return DetectorResult(detector_outputs={self.detector_id: {}})

    def get_detector_id(self) -> str:
        """Get detector ID."""
        return self.detector_id

    def get_detector_name(self) -> str:
        """Get detector name."""
        return self.detector_name

    def get_supported_metrics(self) -> List[str]:
        """Get list of supported metrics."""
        return self.supported_metrics.copy()
