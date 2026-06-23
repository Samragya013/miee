"""
Detector Framework package for MIIE v1.0.
Exports detector framework components.
"""

from src.miie.processing.detection.base import BaseDetector
from src.miie.processing.detection.registry import DetectorRegistry
from src.miie.processing.detection.dispatcher import DetectorDispatcherEngine
from src.miie.processing.detection.runner import DetectorRunner
from src.miie.processing.detection.mock_detectors import (
    MockDistributionDriftDetector,
    MockCorrelationBreakdownDetector,
    MockThresholdCompressionDetector
)

__all__ = [
    "BaseDetector",
    "DetectorRegistry",
    "DetectorDispatcherEngine",
    "DetectorRunner",
    "MockDistributionDriftDetector",
    "MockCorrelationBreakdownDetector",
    "MockThresholdCompressionDetector"
]
