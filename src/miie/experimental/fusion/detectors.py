"""
Individual Detector Wrappers for Fusion Framework

Adapts existing detectors (KS, PSI, Wasserstein, Dip Test) to the
uniform BaseDetector interface for use in fusion.

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

from typing import List

import numpy as np

from miie.experimental.d01_candidates.wasserstein_detector import (
    wasserstein_two_sample_test,
)
from miie.experimental.fusion.base import BaseDetector, DetectorEvidence
from miie.processing.detection.statistics import compute_psi, dip_test, ks_2samp


class KSDetector(BaseDetector):
    """Kolmogorov-Smirnov two-sample test detector."""

    @property
    def detector_id(self) -> str:
        return "KS"

    @property
    def detector_name(self) -> str:
        return "Kolmogorov-Smirnov Test"

    def detect(self, baseline: List[float], target: List[float]) -> DetectorEvidence:
        """Run KS test on baseline and target windows.

        Args:
            baseline: Baseline window values
            target: Target window values

        Returns:
            DetectorEvidence with KS test result
        """
        ks_stat, ks_p = ks_2samp(baseline, target)

        # Confidence: 1 - p_value (higher p = less confident)
        confidence = 1.0 - ks_p

        return DetectorEvidence(
            detector_id=self.detector_id,
            detector_name=self.detector_name,
            drift_detected=ks_p < 0.05,
            confidence=confidence,
            p_value=ks_p,
            test_statistic=ks_stat,
            metadata={"ks_statistic": ks_stat, "ks_p_value": ks_p},
        )


class PSIDetector(BaseDetector):
    """Population Stability Index detector."""

    @property
    def detector_id(self) -> str:
        return "PSI"

    @property
    def detector_name(self) -> str:
        return "Population Stability Index"

    def detect(self, baseline: List[float], target: List[float]) -> DetectorEvidence:
        """Run PSI test on baseline and target windows.

        Args:
            baseline: Baseline window values
            target: Target window values

        Returns:
            DetectorEvidence with PSI test result
        """
        psi_val = compute_psi(baseline, target)

        # Confidence: PSI normalized to [0, 1] (PSI > 0.25 indicates drift)
        confidence = min(1.0, psi_val / 0.5)

        return DetectorEvidence(
            detector_id=self.detector_id,
            detector_name=self.detector_name,
            drift_detected=psi_val > 0.25,
            confidence=confidence,
            test_statistic=psi_val,
            metadata={"psi_value": psi_val},
        )


class WassersteinDetector(BaseDetector):
    """Wasserstein distance two-sample test detector."""

    def __init__(self, n_permutations: int = 500, alpha: float = 0.10):
        """Initialize Wasserstein detector.

        Args:
            n_permutations: Number of permutations for p-value
            alpha: Significance level
        """
        self._n_permutations = n_permutations
        self._alpha = alpha

    @property
    def detector_id(self) -> str:
        return "WASSERSTEIN"

    @property
    def detector_name(self) -> str:
        return "Wasserstein Distance Test"

    def detect(self, baseline: List[float], target: List[float]) -> DetectorEvidence:
        """Run Wasserstein test on baseline and target windows.

        Args:
            baseline: Baseline window values
            target: Target window values

        Returns:
            DetectorEvidence with Wasserstein test result
        """
        dist, p_value = wasserstein_two_sample_test(
            np.array(baseline),
            np.array(target),
            n_permutations=self._n_permutations,
            random_state=42,
        )

        # Confidence: 1 - p_value
        confidence = 1.0 - p_value

        return DetectorEvidence(
            detector_id=self.detector_id,
            detector_name=self.detector_name,
            drift_detected=p_value < self._alpha,
            confidence=confidence,
            p_value=p_value,
            test_statistic=dist,
            metadata={"wasserstein_distance": dist, "wasserstein_p_value": p_value},
        )


class DipTestDetector(BaseDetector):
    """Hartigan's Dip test for multimodality."""

    @property
    def detector_id(self) -> str:
        return "DIP"

    @property
    def detector_name(self) -> str:
        return "Hartigan's Dip Test"

    def detect(self, baseline: List[float], target: List[float]) -> DetectorEvidence:
        """Run Dip test on combined baseline and target windows.

        Tests whether the combined distribution is multimodal,
        which may indicate drift.

        Args:
            baseline: Baseline window values
            target: Target window values

        Returns:
            DetectorEvidence with Dip test result
        """
        # Combine windows for multimodality test
        combined = baseline + target
        dip_stat, dip_p = dip_test(combined)

        # Confidence: 1 - p_value
        confidence = 1.0 - dip_p

        return DetectorEvidence(
            detector_id=self.detector_id,
            detector_name=self.detector_name,
            drift_detected=dip_p < 0.05,
            confidence=confidence,
            p_value=dip_p,
            test_statistic=dip_stat,
            metadata={"dip_statistic": dip_stat, "dip_p_value": dip_p},
        )
