"""
Fusion Strategies for Multi-Evidence Detection

Implements 5 fusion strategies:
1. Majority Vote (Condorcet)
2. Weighted Vote (Bayesian Model Averaging)
3. Confidence Fusion (Dempster-Shafer)
4. Bayesian Fusion (Posterior Probability)
5. Likelihood Ratio Fusion (Neyman-Pearson)

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

from typing import Dict, List, Optional

from miie.experimental.fusion.base import (
    BaseFusionStrategy,
    DetectorEvidence,
    FusedDecision,
)


class MajorityVote(BaseFusionStrategy):
    """Majority vote fusion strategy.

    Uses Condorcet Jury Theorem: if each voter has probability p > 0.5
    of being correct, the majority decision is correct with high probability.
    """

    @property
    def strategy_name(self) -> str:
        return "Majority Vote"

    def fuse(self, evidences: List[DetectorEvidence], threshold: float = 0.5) -> FusedDecision:
        """Fuse evidence using majority vote.

        Args:
            evidences: List of detector evidence objects
            threshold: Not used (majority is K/2)

        Returns:
            FusedDecision with majority vote result
        """
        if not evidences:
            return FusedDecision(
                drift_detected=False,
                fused_score=0.0,
                strategy_name=self.strategy_name,
                evidence_count=0,
                agreement_score=0.0,
            )

        # Count votes
        n_drift = sum(1 for e in evidences if e.drift_detected)
        n_total = len(evidences)

        # Majority decision
        drift_detected = n_drift > n_total / 2

        # Fused score: proportion voting for drift
        fused_score = n_drift / n_total

        # Agreement score
        agreement = self._compute_agreement(evidences)

        return FusedDecision(
            drift_detected=drift_detected,
            fused_score=fused_score,
            strategy_name=self.strategy_name,
            evidence_count=n_total,
            agreement_score=agreement,
            metadata={"n_drift_votes": n_drift, "n_no_drift_votes": n_total - n_drift},
        )


class WeightedVote(BaseFusionStrategy):
    """Weighted vote fusion strategy.

    Uses Bayesian Model Averaging: weight each detector's vote by its
    empirical accuracy or power on validation data.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize weighted vote.

        Args:
            weights: Dictionary mapping detector_id to weight.
                     If None, equal weights are used.
        """
        self._weights = weights or {}

    @property
    def strategy_name(self) -> str:
        return "Weighted Vote"

    def fuse(self, evidences: List[DetectorEvidence], threshold: float = 0.5) -> FusedDecision:
        """Fuse evidence using weighted vote.

        Args:
            evidences: List of detector evidence objects
            threshold: Decision threshold (default 0.5)

        Returns:
            FusedDecision with weighted vote result
        """
        if not evidences:
            return FusedDecision(
                drift_detected=False,
                fused_score=0.0,
                strategy_name=self.strategy_name,
                evidence_count=0,
                agreement_score=0.0,
            )

        # Compute weighted score
        total_weight = 0.0
        weighted_sum = 0.0

        for evidence in evidences:
            weight = self._weights.get(evidence.detector_id, 1.0)
            vote = 1.0 if evidence.drift_detected else 0.0
            weighted_sum += weight * vote
            total_weight += weight

        # Normalized weighted score
        fused_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Decision
        drift_detected = fused_score > threshold

        # Agreement
        agreement = self._compute_agreement(evidences)

        return FusedDecision(
            drift_detected=drift_detected,
            fused_score=fused_score,
            strategy_name=self.strategy_name,
            evidence_count=len(evidences),
            agreement_score=agreement,
            metadata={"weights": self._weights, "total_weight": total_weight},
        )


class ConfidenceFusion(BaseFusionStrategy):
    """Confidence fusion strategy.

    Uses Dempster-Shafer evidence theory: combine evidence from multiple
    sources using belief functions weighted by confidence.
    """

    @property
    def strategy_name(self) -> str:
        return "Confidence Fusion"

    def fuse(self, evidences: List[DetectorEvidence], threshold: float = 0.5) -> FusedDecision:
        """Fuse evidence using confidence-weighted combination.

        Args:
            evidences: List of detector evidence objects
            threshold: Decision threshold (default 0.5)

        Returns:
            FusedDecision with confidence fusion result
        """
        if not evidences:
            return FusedDecision(
                drift_detected=False,
                fused_score=0.0,
                strategy_name=self.strategy_name,
                evidence_count=0,
                agreement_score=0.0,
            )

        # Compute combined belief using product rule
        belief_drift = 1.0
        belief_no_drift = 1.0

        for evidence in evidences:
            # Belief(drift) = confidence if drift detected, else 1 - confidence
            if evidence.drift_detected:
                belief_drift *= evidence.confidence
                belief_no_drift *= 1.0 - evidence.confidence
            else:
                belief_drift *= 1.0 - evidence.confidence
                belief_no_drift *= evidence.confidence

        # Normalize
        total = belief_drift + belief_no_drift
        if total > 0:
            belief_drift /= total
            belief_no_drift /= total

        # Decision
        drift_detected = belief_drift > threshold

        # Agreement
        agreement = self._compute_agreement(evidences)

        return FusedDecision(
            drift_detected=drift_detected,
            fused_score=belief_drift,
            strategy_name=self.strategy_name,
            evidence_count=len(evidences),
            agreement_score=agreement,
            metadata={"belief_drift": belief_drift, "belief_no_drift": belief_no_drift},
        )


class BayesianFusion(BaseFusionStrategy):
    """Bayesian fusion strategy.

    Uses Bayesian inference: combine prior beliefs with observed evidence
    to compute posterior probability of drift.
    """

    def __init__(
        self,
        prior_drift: float = 0.5,
        true_positive_rates: Optional[Dict[str, float]] = None,
        false_positive_rates: Optional[Dict[str, float]] = None,
    ):
        """Initialize Bayesian fusion.

        Args:
            prior_drift: Prior probability of drift
            true_positive_rates: Dictionary mapping detector_id to TPR
            false_positive_rates: Dictionary mapping detector_id to FPR
        """
        self._prior_drift = prior_drift
        self._tpr = true_positive_rates or {}
        self._fpr = false_positive_rates or {}

    @property
    def strategy_name(self) -> str:
        return "Bayesian Fusion"

    def fuse(self, evidences: List[DetectorEvidence], threshold: float = 0.5) -> FusedDecision:
        """Fuse evidence using Bayesian inference.

        Args:
            evidences: List of detector evidence objects
            threshold: Decision threshold (default 0.5)

        Returns:
            FusedDecision with Bayesian fusion result
        """
        if not evidences:
            return FusedDecision(
                drift_detected=False,
                fused_score=0.0,
                strategy_name=self.strategy_name,
                evidence_count=0,
                agreement_score=0.0,
            )

        # Compute posterior using Bayes' rule
        prior_no_drift = 1.0 - self._prior_drift
        posterior_drift = self._prior_drift
        posterior_no_drift = prior_no_drift

        for evidence in evidences:
            # Get TPR and FPR for this detector
            tpr = self._tpr.get(evidence.detector_id, 0.8)
            fpr = self._fpr.get(evidence.detector_id, 0.2)

            # Likelihood of evidence given drift/no-drift
            if evidence.drift_detected:
                likelihood_drift = tpr
                likelihood_no_drift = fpr
            else:
                likelihood_drift = 1.0 - tpr
                likelihood_no_drift = 1.0 - fpr

            # Update posterior
            posterior_drift *= likelihood_drift
            posterior_no_drift *= likelihood_no_drift

        # Normalize
        total = posterior_drift + posterior_no_drift
        if total > 0:
            posterior_drift /= total
            posterior_no_drift /= total

        # Decision
        drift_detected = posterior_drift > threshold

        # Agreement
        agreement = self._compute_agreement(evidences)

        return FusedDecision(
            drift_detected=drift_detected,
            fused_score=posterior_drift,
            strategy_name=self.strategy_name,
            evidence_count=len(evidences),
            agreement_score=agreement,
            metadata={"posterior_drift": posterior_drift, "posterior_no_drift": posterior_no_drift},
        )


class LikelihoodRatioFusion(BaseFusionStrategy):
    """Likelihood ratio fusion strategy.

    Uses Neyman-Pearson lemma: combine likelihood ratios from multiple
    detectors for optimal test performance.
    """

    def __init__(
        self,
        true_positive_rates: Optional[Dict[str, float]] = None,
        false_positive_rates: Optional[Dict[str, float]] = None,
    ):
        """Initialize likelihood ratio fusion.

        Args:
            true_positive_rates: Dictionary mapping detector_id to TPR
            false_positive_rates: Dictionary mapping detector_id to FPR
        """
        self._tpr = true_positive_rates or {}
        self._fpr = false_positive_rates or {}

    @property
    def strategy_name(self) -> str:
        return "Likelihood Ratio Fusion"

    def fuse(self, evidences: List[DetectorEvidence], threshold: float = 1.0) -> FusedDecision:
        """Fuse evidence using likelihood ratios.

        Args:
            evidences: List of detector evidence objects
            threshold: Decision threshold for combined LR (default 1.0)

        Returns:
            FusedDecision with likelihood ratio fusion result
        """
        if not evidences:
            return FusedDecision(
                drift_detected=False,
                fused_score=0.0,
                strategy_name=self.strategy_name,
                evidence_count=0,
                agreement_score=0.0,
            )

        # Compute combined likelihood ratio
        combined_lr = 1.0

        for evidence in evidences:
            # Get TPR and FPR for this detector
            tpr = self._tpr.get(evidence.detector_id, 0.8)
            fpr = self._fpr.get(evidence.detector_id, 0.2)

            # Likelihood ratio for this evidence
            if evidence.drift_detected:
                lr = tpr / fpr if fpr > 0 else float("inf")
            else:
                lr = (1.0 - tpr) / (1.0 - fpr) if fpr < 1 else 0.0

            combined_lr *= lr

        # Normalize LR to [0, 1] using sigmoid
        fused_score = combined_lr / (1.0 + combined_lr)

        # Decision
        drift_detected = combined_lr > threshold

        # Agreement
        agreement = self._compute_agreement(evidences)

        return FusedDecision(
            drift_detected=drift_detected,
            fused_score=fused_score,
            strategy_name=self.strategy_name,
            evidence_count=len(evidences),
            agreement_score=agreement,
            metadata={"combined_lr": combined_lr, "threshold": threshold},
        )
