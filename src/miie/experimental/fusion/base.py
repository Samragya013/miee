"""
Base classes for Multi-Evidence Fusion Framework

Defines abstract base classes for evidence collection and fusion strategies.

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DetectorEvidence:
    """Evidence from a single detector.

    Attributes:
        detector_id: Unique identifier for the detector
        detector_name: Human-readable name
        drift_detected: Binary decision (True/False)
        confidence: Confidence score in [0, 1]
        p_value: Statistical p-value (if available)
        test_statistic: Test statistic value (if available)
        metadata: Additional detector-specific information
    """

    detector_id: str
    detector_name: str
    drift_detected: bool
    confidence: float
    p_value: Optional[float] = None
    test_statistic: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FusedDecision:
    """Result of evidence fusion.

    Attributes:
        drift_detected: Fused binary decision (True/False)
        fused_score: Fused continuous score in [0, 1]
        strategy_name: Name of fusion strategy used
        evidence_count: Number of evidence sources
        agreement_score: Level of agreement among detectors
        metadata: Additional strategy-specific information
    """

    drift_detected: bool
    fused_score: float
    strategy_name: str
    evidence_count: int
    agreement_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseFusionStrategy(ABC):
    """Abstract base class for fusion strategies.

    All fusion strategies must implement the fuse() method.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Name of the fusion strategy."""
        pass

    @abstractmethod
    def fuse(self, evidences: List[DetectorEvidence], threshold: float = 0.5) -> FusedDecision:
        """Fuse multiple evidence sources into a single decision.

        Args:
            evidences: List of detector evidence objects
            threshold: Decision threshold for fused score

        Returns:
            FusedDecision with the fused result
        """
        pass

    def _compute_agreement(self, evidences: List[DetectorEvidence]) -> float:
        """Compute agreement score among detectors.

        Agreement is the proportion of detectors that agree with the majority.

        Args:
            evidences: List of detector evidence objects

        Returns:
            Agreement score in [0, 1]
        """
        if not evidences:
            return 0.0

        decisions = [e.drift_detected for e in evidences]
        n_drift = sum(decisions)
        n_no_drift = len(decisions) - n_drift

        majority_count = max(n_drift, n_no_drift)
        return majority_count / len(decisions)


class BaseDetector(ABC):
    """Abstract base class for individual detectors used in fusion.

    Wraps existing detectors to provide a uniform interface for fusion.
    """

    @property
    @abstractmethod
    def detector_id(self) -> str:
        """Unique identifier for the detector."""
        pass

    @property
    @abstractmethod
    def detector_name(self) -> str:
        """Human-readable name for the detector."""
        pass

    @abstractmethod
    def detect(self, baseline: List[float], target: List[float]) -> DetectorEvidence:
        """Run detection on a pair of windows.

        Args:
            baseline: Baseline window values
            target: Target window values

        Returns:
            DetectorEvidence with the detection result
        """
        pass
