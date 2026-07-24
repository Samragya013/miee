"""
Multi-Evidence Fusion Detector

Main detector that orchestrates evidence collection from multiple
statistical tests and fuses them using configurable strategies.

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

import time
from typing import Any, Dict, List, Optional

from miie.experimental.fusion.base import (
    BaseDetector,
    BaseFusionStrategy,
    DetectorEvidence,
    FusedDecision,
)
from miie.experimental.fusion.detectors import (
    DipTestDetector,
    KSDetector,
    PSIDetector,
    WassersteinDetector,
)
from miie.experimental.fusion.strategies import (
    BayesianFusion,
    ConfidenceFusion,
    LikelihoodRatioFusion,
    MajorityVote,
    WeightedVote,
)


class MultiEvidenceFusionDetector:
    """Multi-Evidence Fusion Detector.

    Combines evidence from multiple statistical detectors using
    configurable fusion strategies.

    Architecture:
    1. Collect evidence from each detector
    2. Fuse evidence using selected strategy
    3. Return fused decision with metadata
    """

    def __init__(
        self,
        detectors: Optional[List[BaseDetector]] = None,
        strategy: Optional[BaseFusionStrategy] = None,
        strategy_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize Multi-Evidence Fusion Detector.

        Args:
            detectors: List of detector instances. If None, uses default set.
            strategy: Fusion strategy instance. If None, uses MajorityVote.
            strategy_config: Additional configuration for the strategy.
        """
        # Default detectors
        if detectors is None:
            self._detectors = [
                KSDetector(),
                PSIDetector(),
                WassersteinDetector(n_permutations=500, alpha=0.10),
                DipTestDetector(),
            ]
        else:
            self._detectors = detectors

        # Default strategy
        if strategy is None:
            self._strategy = MajorityVote()
        else:
            self._strategy = strategy

        self._strategy_config = strategy_config or {}

    @property
    def detector_id(self) -> str:
        """Detector identifier."""
        return "MULTI_EVIDENCE_FUSION"

    @property
    def detector_name(self) -> str:
        """Detector name."""
        return f"Multi-Evidence Fusion ({self._strategy.strategy_name})"

    @property
    def strategy_name(self) -> str:
        """Name of the fusion strategy."""
        return self._strategy.strategy_name

    @property
    def detectors(self) -> List[BaseDetector]:
        """List of detectors used."""
        return self._detectors

    def collect_evidence(self, baseline: List[float], target: List[float]) -> List[DetectorEvidence]:
        """Collect evidence from all detectors.

        Args:
            baseline: Baseline window values
            target: Target window values

        Returns:
            List of DetectorEvidence objects
        """
        evidences = []

        for detector in self._detectors:
            try:
                evidence = detector.detect(baseline, target)
                evidences.append(evidence)
            except Exception as e:
                # Handle detector errors gracefully
                evidences.append(
                    DetectorEvidence(
                        detector_id=detector.detector_id,
                        detector_name=detector.detector_name,
                        drift_detected=False,
                        confidence=0.0,
                        metadata={"error": str(e)},
                    )
                )

        return evidences

    def fuse_evidence(
        self,
        evidences: List[DetectorEvidence],
        threshold: float = 0.5,
    ) -> FusedDecision:
        """Fuse evidence using the selected strategy.

        Args:
            evidences: List of detector evidence objects
            threshold: Decision threshold

        Returns:
            FusedDecision with the fused result
        """
        return self._strategy.fuse(evidences, threshold)

    def detect(
        self,
        baseline: List[float],
        target: List[float],
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Run complete multi-evidence fusion detection.

        Args:
            baseline: Baseline window values
            target: Target window values
            threshold: Decision threshold

        Returns:
            Dictionary with detection results
        """
        start_time = time.time()

        # Collect evidence
        evidences = self.collect_evidence(baseline, target)

        # Fuse evidence
        fused = self.fuse_evidence(evidences, threshold)

        # Compute runtime
        runtime_ms = (time.time() - start_time) * 1000

        return {
            "detector_id": self.detector_id,
            "detector_name": self.detector_name,
            "strategy_name": self.strategy_name,
            "drift_detected": fused.drift_detected,
            "fused_score": fused.fused_score,
            "agreement_score": fused.agreement_score,
            "evidence_count": fused.evidence_count,
            "evidences": [
                {
                    "detector_id": e.detector_id,
                    "detector_name": e.detector_name,
                    "drift_detected": e.drift_detected,
                    "confidence": e.confidence,
                    "p_value": e.p_value,
                    "test_statistic": e.test_statistic,
                }
                for e in evidences
            ],
            "runtime_ms": runtime_ms,
            "metadata": fused.metadata,
        }

    def detect_windows(
        self,
        windows: List[List[float]],
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Run detection on multiple windows (first window is reference).

        Args:
            windows: List of windows (each window is a list of values)
            threshold: Decision threshold

        Returns:
            Dictionary with detection results for all window pairs
        """
        if len(windows) < 2:
            raise ValueError("Need at least 2 windows for drift detection")

        reference = windows[0]
        results: Dict[str, Any] = {
            "detector_id": self.detector_id,
            "detector_name": self.detector_name,
            "strategy_name": self.strategy_name,
            "n_windows": len(windows),
            "drift_detected": False,
            "window_results": [],
        }

        for i, window in enumerate(windows[1:], start=1):
            window_result = self.detect(reference, window, threshold)
            window_result["window_idx"] = i
            results["window_results"].append(window_result)

            if window_result["drift_detected"]:
                results["drift_detected"] = True

        return results


def create_fusion_detector(
    strategy_name: str = "majority_vote",
    detectors: Optional[List[BaseDetector]] = None,
    **kwargs,
) -> MultiEvidenceFusionDetector:
    """Factory function to create fusion detector with specified strategy.

    Args:
        strategy_name: Name of fusion strategy
        detectors: List of detector instances
        **kwargs: Additional arguments for strategy

    Returns:
        MultiEvidenceFusionDetector instance
    """
    strategy_map = {
        "majority_vote": MajorityVote,
        "weighted_vote": WeightedVote,
        "confidence_fusion": ConfidenceFusion,
        "bayesian_fusion": BayesianFusion,
        "likelihood_ratio": LikelihoodRatioFusion,
    }

    if strategy_name not in strategy_map:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(strategy_map.keys())}")

    strategy_class = strategy_map[strategy_name]
    strategy = strategy_class(**kwargs)

    return MultiEvidenceFusionDetector(detectors=detectors, strategy=strategy)
