"""
MIIE v1.6 Scientific Metric Completion Framework — Validation.

Validates input observations, metric completeness, confidence, units,
ranges, scientific assumptions, and derived values.

Reference: PR-12 specification.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from miie.metrics.models import (
    MetricDefinition,
    MetricResult,
    ObservationInput,
    ValidationResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Observation Validator
# ---------------------------------------------------------------------------


class ObservationValidator:
    """Validates input observations against metric constraints.

    Checks unit consistency, value ranges, quality levels, and
    minimum observation counts.
    """

    def validate_input_observations(
        self,
        observations: List[ObservationInput],
        metric_def: MetricDefinition,
    ) -> ValidationResult:
        """Validate observations for a specific metric.

        Args:
            observations: Observations to validate.
            metric_def: The metric definition to validate against.

        Returns:
            ValidationResult with is_valid, errors, and warnings.
        """
        errors: List[str] = []
        warnings: List[str] = []
        checked = 0
        passed = 0

        if not observations:
            errors.append(f"No observations provided for {metric_def.metric_id}")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                checked_count=0,
                passed_count=0,
            )

        for obs in observations:
            checked += 1
            obs_ok = True

            # Unit check
            if obs.unit != metric_def.unit:
                errors.append(
                    f"Observation {obs.observation_id}: unit '{obs.unit}' "
                    f"expected '{metric_def.unit}' for {metric_def.metric_id}"
                )
                obs_ok = False

            # Metric ID check
            if obs.metric_id != metric_def.metric_id:
                errors.append(
                    f"Observation {obs.observation_id}: metric_id '{obs.metric_id}' "
                    f"expected '{metric_def.metric_id}'"
                )
                obs_ok = False

            # Value range check
            if obs.value < metric_def.min_value or obs.value > metric_def.max_value:
                warnings.append(
                    f"Observation {obs.observation_id}: value {obs.value} "
                    f"outside range [{metric_def.min_value}, {metric_def.max_value}]"
                )

            # NaN/Inf check
            if obs.value != obs.value:  # NaN check
                errors.append(f"Observation {obs.observation_id}: value is NaN")
                obs_ok = False
            elif obs.value == float("inf") or obs.value == float("-inf"):
                errors.append(f"Observation {obs.observation_id}: value is Inf")
                obs_ok = False

            if obs_ok:
                passed += 1

        # Minimum observation count
        if len(observations) < metric_def.required_observations:
            errors.append(
                f"Insufficient observations for {metric_def.metric_id}: "
                f"got {len(observations)}, need {metric_def.required_observations}"
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checked_count=checked,
            passed_count=passed,
        )

    def validate_metric_result(
        self,
        result: MetricResult,
        metric_def: MetricDefinition,
    ) -> ValidationResult:
        """Validate a computed metric result.

        Args:
            result: The computed MetricResult.
            metric_def: The metric definition.

        Returns:
            ValidationResult with is_valid, errors, and warnings.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Value range
        if result.value < metric_def.min_value or result.value > metric_def.max_value:
            errors.append(
                f"Result value {result.value} outside valid range " f"[{metric_def.min_value}, {metric_def.max_value}]"
            )

        # Confidence range
        if result.confidence < 0.0 or result.confidence > 1.0:
            errors.append(f"Confidence {result.confidence} outside [0.0, 1.0]")

        # Non-negative uncertainty
        if result.uncertainty < 0.0:
            errors.append(f"Uncertainty {result.uncertainty} is negative")

        # Unit consistency
        if result.unit != metric_def.unit:
            errors.append(f"Result unit '{result.unit}' expected '{metric_def.unit}'")

        # Observation count
        if result.observation_count < metric_def.required_observations:
            warnings.append(
                f"Observation count {result.observation_count} below "
                f"recommended minimum {metric_def.required_observations}"
            )

        # Low confidence warning
        if result.confidence < 0.3:
            warnings.append(f"Low confidence: {result.confidence:.3f}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checked_count=1,
            passed_count=1 if len(errors) == 0 else 0,
        )


# ---------------------------------------------------------------------------
# Collection Validator
# ---------------------------------------------------------------------------


class MetricCollectionValidator:
    """Validates a complete MetricCollection for completeness and consistency."""

    EXPECTED_METRICS = tuple(f"M-{i:02d}" for i in range(1, 8))

    def validate_completeness(
        self,
        results: Dict[str, MetricResult],
    ) -> ValidationResult:
        """Validate that all expected metrics are present.

        Args:
            results: Dict mapping metric_id to MetricResult.

        Returns:
            ValidationResult.
        """
        errors: List[str] = []
        warnings: List[str] = []
        missing = [m for m in self.EXPECTED_METRICS if m not in results]

        if missing:
            warnings.append(f"Missing metrics: {missing}")

        return ValidationResult(
            is_valid=len(missing) == 0,
            errors=errors,
            warnings=warnings,
            checked_count=len(self.EXPECTED_METRICS),
            passed_count=len(self.EXPECTED_METRICS) - len(missing),
        )

    def validate_consistency(
        self,
        results: Dict[str, MetricResult],
    ) -> ValidationResult:
        """Validate cross-metric consistency.

        Checks that derived metrics are consistent with their dependencies.

        Args:
            results: Dict mapping metric_id to MetricResult.

        Returns:
            ValidationResult.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # M-03 (churn ratio) should be <= M-02 (commit count) / max_possible
        if "M-03" in results and "M-02" in results:
            m03 = results["M-03"]
            m02 = results["M-02"]
            if m03.value > 1.0:
                warnings.append(f"M-03 churn ratio {m03.value:.3f} exceeds 1.0")

        # M-01 (entropy ratio) should be in [0, 1]
        if "M-01" in results:
            m01 = results["M-01"]
            if m01.value < 0.0 or m01.value > 1.0:
                errors.append(f"M-01 entropy ratio {m01.value:.3f} outside [0, 1]")

        # M-04 (test coverage) should be in [0, 1]
        if "M-04" in results:
            m04 = results["M-04"]
            if m04.value < 0.0 or m04.value > 1.0:
                errors.append(f"M-04 test coverage {m04.value:.3f} outside [0, 1]")

        # M-05 (review latency) should be non-negative
        if "M-05" in results:
            m05 = results["M-05"]
            if m05.value < 0.0:
                errors.append(f"M-05 review latency {m05.value} is negative")

        # M-07 (branch freshness) should be in [0, 1]
        if "M-07" in results:
            m07 = results["M-07"]
            if m07.value < 0.0 or m07.value > 1.0:
                errors.append(f"M-07 branch freshness {m07.value:.3f} outside [0, 1]")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checked_count=5,
            passed_count=5 - len(errors),
        )
