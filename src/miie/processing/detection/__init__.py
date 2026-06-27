"""
Detector Framework package for MIIE v1.0.
Exports detector framework components.
"""

from miie.processing.detection.base import BaseDetector
from miie.processing.detection.dispatcher import DetectorDispatcherEngine
from miie.processing.detection.mock_detectors import (
    MockCorrelationBreakdownDetector,
    MockDistributionDriftDetector,
    MockThresholdCompressionDetector,
)
from miie.processing.detection.registry import DetectorRegistry
from miie.processing.detection.runner import DetectorRunner

__all__ = [
    "BaseDetector",
    "DetectorRegistry",
    "DetectorDispatcherEngine",
    "DetectorRunner",
    "MockDistributionDriftDetector",
    "MockCorrelationBreakdownDetector",
    "MockThresholdCompressionDetector",
]
