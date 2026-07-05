"""
MIIE v1.6 Scientific Metric Completion Framework — Base Metric Computer.

Provides shared computation utilities for all metric implementations.
"""

from __future__ import annotations

import math
from typing import Dict, List

from miie.metrics.contracts import MetricComputer
from miie.metrics.models import (
    MetricResult,
    ObservationInput,
)


class BaseMetricComputer(MetricComputer):
    """Shared computation utilities for metric computers.

    Provides deterministic aggregation, confidence calculation, and
    quality-weighted computation used by all M-01 through M-07 implementations.
    """

    def compute(self, observations: List[ObservationInput]) -> MetricResult:
        """Compute metric from observations using the definition's aggregation.

        Subclasses can override for custom logic.
        """
        if not observations:
            raise ValueError(f"No observations for {self.metric_definition.metric_id}")

        definition = self.metric_definition
        values = [obs.value for obs in observations]
        qualities = [obs.quality for obs in observations]
        providers = {obs.provider_id for obs in observations}
        obs_ids = tuple(obs.observation_id for obs in observations)

        # Aggregate
        if definition.aggregation == "sum":
            value = sum(values)
        else:
            value = sum(values) / len(values)

        # Clamp to valid range
        value = max(definition.min_value, min(definition.max_value, value))

        # Uncertainty (std dev)
        uncertainty = self._compute_std(values)

        # Confidence
        confidence = self._compute_confidence(observations, uncertainty, value)

        # Quality distribution
        quality_dist: Dict[str, int] = {}
        for q in qualities:
            quality_dist[q] = quality_dist.get(q, 0) + 1

        warnings = self._check_warnings(observations, value, confidence)

        return MetricResult(
            metric_id=definition.metric_id,
            value=value,
            unit=definition.unit,
            confidence=confidence,
            uncertainty=uncertainty,
            observation_count=len(observations),
            provider_count=len(providers),
            quality_distribution=quality_dist,
            computation_method=definition.aggregation,
            warnings=warnings,
            source_observation_ids=obs_ids,
        )

    def validate_observations(
        self,
        observations: List[ObservationInput],
    ) -> "ValidationResult":
        """Default validation: check unit, metric_id, and range."""
        from miie.metrics.models import ValidationResult

        definition = self.metric_definition
        errors: List[str] = []
        warnings: List[str] = []

        for obs in observations:
            if obs.unit != definition.unit:
                errors.append(f"{obs.observation_id}: unit '{obs.unit}' expected '{definition.unit}'")
            if obs.metric_id != definition.metric_id:
                errors.append(f"{obs.observation_id}: metric '{obs.metric_id}' expected '{definition.metric_id}'")
            if obs.value < definition.min_value or obs.value > definition.max_value:
                warnings.append(
                    f"{obs.observation_id}: value {obs.value} outside [{definition.min_value}, {definition.max_value}]"
                )
            if obs.value != obs.value:  # NaN
                errors.append(f"{obs.observation_id}: value is NaN")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checked_count=len(observations),
            passed_count=len(observations) - len(errors),
        )

    # ------------------------------------------------------------------
    # Shared Utilities
    # ------------------------------------------------------------------

    def _compute_std(self, values: List[float]) -> float:
        """Compute population standard deviation."""
        n = len(values)
        if n < 2:
            return 0.0
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        return math.sqrt(variance)

    def _compute_confidence(
        self,
        observations: List[ObservationInput],
        uncertainty: float,
        value: float,
    ) -> float:
        """Compute metric confidence (C_m) using weighted additive composition.

        Formula: C_m = 0.3·α₁ + 0.3·α₂ + 0.2·α₃ + 0.2·α₄

        Factors (α):
            α₁ (sample_sufficiency): min(1, n/20) — Is the sample large enough?
            α₂ (observation_quality): mean(quality_tags) — Are observations high quality?
            α₃ (value_stability): 1 - min(1, CV) — Is the value stable?
            α₄ (provider_diversity): min(1, n_providers/2) — Are there multiple sources?

        Composition rationale: Additive because factors represent independent quality
        dimensions that contribute to reliability. A low sample size reduces confidence
        but does not invalidate it entirely.

        Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4
        """
        n = len(observations)

        # α₁: sample sufficiency (asymptotic to 1.0 at ~20 observations)
        alpha_1 = min(1.0, n / 20.0)

        # α₂: observation quality
        quality_scores = {"complete": 1.0, "estimated": 0.5, "derived": 0.7, "missing": 0.0}
        qualities = [quality_scores.get(obs.quality, 0.5) for obs in observations]
        alpha_2 = sum(qualities) / len(qualities) if qualities else 0.0

        # α₃: value stability (inverse of relative uncertainty)
        if value != 0.0 and abs(value) > 1e-10:
            relative_uncertainty = abs(uncertainty / value)
            alpha_3 = max(0.0, 1.0 - min(1.0, relative_uncertainty))
        else:
            # For values near zero, use absolute uncertainty
            alpha_3 = max(0.0, 1.0 - min(1.0, uncertainty))

        # α₄: provider diversity
        providers = {obs.provider_id for obs in observations}
        alpha_4 = min(1.0, len(providers) / 2.0)

        # C_m = 0.3·α₁ + 0.3·α₂ + 0.2·α₃ + 0.2·α₄
        confidence = 0.3 * alpha_1 + 0.3 * alpha_2 + 0.2 * alpha_3 + 0.2 * alpha_4
        return max(0.0, min(1.0, confidence))

    def _check_warnings(
        self,
        observations: List[ObservationInput],
        value: float,
        confidence: float,
    ) -> List[str]:
        """Generate warnings for the computation."""
        warnings = []

        if len(observations) < self.minimum_observations():
            warnings.append(f"Below minimum observations: {len(observations)} < {self.minimum_observations()}")

        if confidence < 0.3:
            warnings.append(f"Low confidence: {confidence:.3f}")

        # Check for estimated observations
        estimated = sum(1 for obs in observations if obs.quality == "estimated")
        if estimated > len(observations) / 2:
            warnings.append(f"Majority of observations are estimated ({estimated}/{len(observations)})")

        return warnings
