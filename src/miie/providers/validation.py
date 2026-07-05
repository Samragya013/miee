"""
MIIE v1.6 Observation Provider Framework — Validation engine.

Implements OVR validation rules, schema validation, metric bounds checking,
confidence scoring, freshness verification, dependency validation, and
composite rule composition.

Implements OVR §9.3 and OPC §3.2.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, FrozenSet, List, Optional, Sequence

from miie.providers.context import (
    METRIC_BOUNDS,
    VALID_METRIC_IDS,
    ExtractionResult,
    ProviderCapability,
    ProviderContext,
    ValidationResult,
)

# ---------------------------------------------------------------------------
# Required observation fields (ODSS §5)
# ---------------------------------------------------------------------------

REQUIRED_OBSERVATION_FIELDS: FrozenSet[str] = frozenset(
    {
        "metric_id",
        "value",
        "timestamp",
    }
)

OPTIONAL_OBSERVATION_FIELDS: FrozenSet[str] = frozenset(
    {
        "confidence",
        "unit",
        "source",
        "metadata",
        "is_estimated",
    }
)

ALL_OBSERVATION_FIELDS: FrozenSet[str] = REQUIRED_OBSERVATION_FIELDS | OPTIONAL_OBSERVATION_FIELDS


# ---------------------------------------------------------------------------
# Metric dependency graph (ODSS §7)
# ---------------------------------------------------------------------------

METRIC_DEPENDENCIES: Dict[str, FrozenSet[str]] = {
    "M-01": frozenset(),  # commit entropy — no dependencies
    "M-02": frozenset(),  # commit count — no dependencies
    "M-03": frozenset({"M-02"}),  # code churn requires commit count
    "M-04": frozenset(),  # test coverage — no dependencies
    "M-05": frozenset(),  # review latency — no dependencies
    "M-06": frozenset(),  # file change count — no dependencies
    "M-07": frozenset(),  # branch freshness — no dependencies
}


# ---------------------------------------------------------------------------
# Freshness thresholds per metric (OVR §9.4)
# ---------------------------------------------------------------------------

FRESHNESS_MAX_AGE_HOURS: Dict[str, float] = {
    "M-01": 168.0,  # 7 days
    "M-02": 72.0,  # 3 days
    "M-03": 168.0,  # 7 days
    "M-04": 24.0,  # 1 day
    "M-05": 72.0,  # 3 days
    "M-06": 168.0,  # 7 days
    "M-07": 24.0,  # 1 day
}

DEFAULT_FRESHNESS_MAX_AGE_HOURS: float = 168.0  # 7 days fallback


# ---------------------------------------------------------------------------
# Recovery suggestion dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RecoverySuggestion:
    """Actionable suggestion for recovering from a validation failure.

    Attributes:
        issue: Human-readable description of the validation issue.
        suggestion: Recommended action to resolve the issue.
        severity: Impact severity — one of ``"low"``, ``"medium"``, ``"high"``.
    """

    issue: str
    suggestion: str
    severity: str = "medium"

    def __post_init__(self) -> None:
        if self.severity not in ("low", "medium", "high"):
            raise ValueError(f"severity must be low/medium/high, got {self.severity!r}")


# ---------------------------------------------------------------------------
# Validation result helpers
# ---------------------------------------------------------------------------


def _result_ok(rule_id: str = "", warnings: Optional[List[str]] = None) -> ValidationResult:
    """Create a passing validation result."""
    if warnings:
        return ValidationResult(is_valid=True, warnings=warnings, rule_id=rule_id)
    return ValidationResult.success()


def _result_fail(
    violations: List[str],
    rule_id: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> ValidationResult:
    """Create a failing validation result."""
    return ValidationResult(
        is_valid=False,
        violations=violations,
        rule_id=rule_id,
        metadata=metadata or {},
    )


def _merge_results(results: Sequence[ValidationResult]) -> ValidationResult:
    """Merge multiple validation results into one.

    The merged result is valid only when **all** inputs are valid.
    All violations and warnings are concatenated.
    """
    all_violations: List[str] = []
    all_warnings: List[str] = []
    is_valid = True

    for r in results:
        if not r.is_valid:
            is_valid = False
        all_violations.extend(r.violations)
        all_warnings.extend(r.warnings)

    return ValidationResult(
        is_valid=is_valid,
        violations=all_violations,
        warnings=all_warnings,
    )


# ---------------------------------------------------------------------------
# Abstract base — ValidationRule (OVR §9.2)
# ---------------------------------------------------------------------------


class ValidationRule(ABC):
    """OVR §9.2 — Abstract base for validation rules."""

    @abstractmethod
    def validate(self, observation: Any, metric_id: str) -> ValidationResult:
        """Validate a single observation against this rule."""
        ...


# ---------------------------------------------------------------------------
# Concrete validation rules
# ---------------------------------------------------------------------------


class SchemaValidationRule(ValidationRule):
    """OVR §9.3.1 — Validates that required fields are present on an observation."""

    RULE_ID: str = "OVLR-SCHEMA"

    def __init__(
        self,
        required_fields: Optional[FrozenSet[str]] = None,
        allowed_fields: Optional[FrozenSet[str]] = None,
    ) -> None:
        self._required = required_fields or REQUIRED_OBSERVATION_FIELDS
        self._allowed = allowed_fields or ALL_OBSERVATION_FIELDS

    def validate(self, observation: Any, metric_id: str) -> ValidationResult:
        if observation is None:
            return _result_fail(
                [f"Observation is None for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        if not isinstance(observation, dict):
            return _result_fail(
                [f"Observation must be a dict, got {type(observation).__name__}"],
                rule_id=self.RULE_ID,
            )

        violations: List[str] = []
        for field_name in self._required:
            if field_name not in observation:
                violations.append(f"Missing required field '{field_name}' for metric {metric_id}")

        unknown = set(observation.keys()) - self._allowed
        if unknown:
            return _result_fail(
                violations + [f"Unexpected field(s) {sorted(unknown)} for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        if violations:
            return _result_fail(violations, rule_id=self.RULE_ID)

        return _result_ok(self.RULE_ID)


class RangeValidationRule(ValidationRule):
    """OVR §9.3.2 — Validates that a numeric value falls within MetricBounds."""

    RULE_ID: str = "OVLR-RANGE"

    def validate(self, observation: Any, metric_id: str) -> ValidationResult:
        if observation is None:
            return _result_fail(
                [f"Observation is None for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        bounds = METRIC_BOUNDS.get(metric_id)
        if bounds is None:
            return _result_fail(
                [f"No bounds defined for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        value = observation.get("value") if isinstance(observation, dict) else getattr(observation, "value", None)
        if value is None:
            return _result_fail(
                [f"No value to validate for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        if not isinstance(value, (int, float)):
            return _result_fail(
                [f"Value must be numeric for metric {metric_id}, " f"got {type(value).__name__}"],
                rule_id=self.RULE_ID,
            )

        if not bounds.validate(float(value)):
            return _result_fail(
                [
                    f"Value {value} is outside bounds [{bounds.min_value}, "
                    f"{bounds.max_value}] for metric {metric_id}"
                ],
                rule_id=self.RULE_ID,
                metadata={
                    "metric_id": metric_id,
                    "value": value,
                    "min_value": bounds.min_value,
                    "max_value": bounds.max_value,
                },
            )

        return _result_ok(self.RULE_ID)


class ConfidenceValidationRule(ValidationRule):
    """OVR §9.3.3 — Validates that confidence is in [0.0, 1.0]."""

    RULE_ID: str = "OVLR-CONFIDENCE"
    MIN_CONFIDENCE: float = 0.0
    MAX_CONFIDENCE: float = 1.0

    def validate(self, observation: Any, metric_id: str) -> ValidationResult:
        if observation is None:
            return _result_fail(
                [f"Observation is None for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        confidence: Optional[float] = None
        if isinstance(observation, dict):
            confidence = observation.get("confidence")
        else:
            confidence = getattr(observation, "confidence", None)

        if confidence is None:
            return _result_ok(
                self.RULE_ID,
                warnings=[f"No confidence field; defaulting to 1.0 for {metric_id}"],
            )

        if not isinstance(confidence, (int, float)):
            return _result_fail(
                [f"Confidence must be numeric for metric {metric_id}, " f"got {type(confidence).__name__}"],
                rule_id=self.RULE_ID,
            )

        if not (self.MIN_CONFIDENCE <= float(confidence) <= self.MAX_CONFIDENCE):
            return _result_fail(
                [f"Confidence {confidence} is outside [0.0, 1.0] " f"for metric {metric_id}"],
                rule_id=self.RULE_ID,
                metadata={"confidence": confidence},
            )

        if float(confidence) < 0.5:
            return ValidationResult(
                is_valid=True,
                warnings=[f"Low confidence {confidence} for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        return _result_ok(self.RULE_ID)


class FreshnessValidationRule(ValidationRule):
    """OVR §9.3.4 — Validates that observation timestamp is sufficiently recent."""

    RULE_ID: str = "OVLR-FRESHNESS"

    def __init__(
        self,
        max_age_hours: Optional[Dict[str, float]] = None,
        default_max_age_hours: float = DEFAULT_FRESHNESS_MAX_AGE_HOURS,
    ) -> None:
        self._max_age = max_age_hours or FRESHNESS_MAX_AGE_HOURS
        self._default = default_max_age_hours

    def validate(self, observation: Any, metric_id: str) -> ValidationResult:
        if observation is None:
            return _result_fail(
                [f"Observation is None for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        timestamp: Optional[datetime] = None
        if isinstance(observation, dict):
            raw = observation.get("timestamp")
            if isinstance(raw, datetime):
                timestamp = raw
            elif isinstance(raw, str):
                try:
                    timestamp = datetime.fromisoformat(raw)
                except (ValueError, TypeError):
                    return _result_fail(
                        [f"Cannot parse timestamp string {raw!r} for metric {metric_id}"],
                        rule_id=self.RULE_ID,
                    )
        else:
            timestamp = getattr(observation, "timestamp", None)

        if timestamp is None:
            return _result_fail(
                [f"No timestamp on observation for metric {metric_id}"],
                rule_id=self.RULE_ID,
            )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        age = now - timestamp

        if age < timedelta(0):
            return _result_fail(
                [f"Observation timestamp is in the future for metric {metric_id}: " f"{timestamp.isoformat()}"],
                rule_id=self.RULE_ID,
            )

        max_age_h = self._max_age.get(metric_id, self._default)
        max_age = timedelta(hours=max_age_h)

        if age > max_age:
            return _result_fail(
                [
                    f"Observation is stale for metric {metric_id}: age {age.total_seconds() / 3600:.1f}h "
                    f"exceeds max {max_age_h:.1f}h"
                ],
                rule_id=self.RULE_ID,
                metadata={
                    "age_hours": age.total_seconds() / 3600,
                    "max_age_hours": max_age_h,
                },
            )

        return _result_ok(self.RULE_ID)


class DependencyValidationRule(ValidationRule):
    """OVR §9.3.5 — Validates that metric dependencies are satisfied."""

    RULE_ID: str = "OVLR-DEPENDENCY"

    def __init__(
        self,
        dependencies: Optional[Dict[str, FrozenSet[str]]] = None,
        observed_metrics: Optional[FrozenSet[str]] = None,
    ) -> None:
        self._deps = dependencies or METRIC_DEPENDENCIES
        self._observed = observed_metrics or frozenset()

    def set_observed_metrics(self, metrics: FrozenSet[str]) -> None:
        """Update the set of metrics that have been observed in the current batch."""
        self._observed = metrics

    def validate(self, observation: Any, metric_id: str) -> ValidationResult:
        required_deps = self._deps.get(metric_id, frozenset())
        if not required_deps:
            return _result_ok(self.RULE_ID)

        missing = required_deps - self._observed
        if missing:
            return _result_fail(
                [f"Metric {metric_id} depends on {sorted(missing)} " f"which are not present in the observation batch"],
                rule_id=self.RULE_ID,
                metadata={"missing_dependencies": sorted(missing)},
            )

        return _result_ok(self.RULE_ID)


# ---------------------------------------------------------------------------
# CompositeValidationRule — runs all rules, combines results
# ---------------------------------------------------------------------------


class CompositeValidationRule(ValidationRule):
    """OVR §9.3.6 — Runs a list of rules and combines all results.

    A composite rule passes only when **every** child rule passes.
    All violations and warnings from child rules are preserved.
    """

    def __init__(self, rules: List[ValidationRule]) -> None:
        self._rules = list(rules)

    @property
    def rules(self) -> List[ValidationRule]:
        return list(self._rules)

    def validate(self, observation: Any, metric_id: str) -> ValidationResult:
        results = [rule.validate(observation, metric_id) for rule in self._rules]
        return _merge_results(results)


# ---------------------------------------------------------------------------
# ObservationValidationEngine (OVR §9.1)
# ---------------------------------------------------------------------------


class ObservationValidationEngine:
    """OVR §9.1 — Central validation engine for the observation provider framework.

    Orchestrates schema, range, confidence, freshness, dependency, and
    composite validation across providers, results, and observation batches.
    """

    def __init__(self) -> None:
        self._schema_rule = SchemaValidationRule()
        self._range_rule = RangeValidationRule()
        self._confidence_rule = ConfidenceValidationRule()
        self._freshness_rule = FreshnessValidationRule()
        self._dependency_rule = DependencyValidationRule()

        self._composite_rules = CompositeValidationRule(
            [
                self._schema_rule,
                self._range_rule,
                self._confidence_rule,
                self._freshness_rule,
                self._dependency_rule,
            ]
        )

    @property
    def schema_rule(self) -> SchemaValidationRule:
        return self._schema_rule

    @property
    def range_rule(self) -> RangeValidationRule:
        return self._range_rule

    @property
    def confidence_rule(self) -> ConfidenceValidationRule:
        return self._confidence_rule

    @property
    def freshness_rule(self) -> FreshnessValidationRule:
        return self._freshness_rule

    @property
    def dependency_rule(self) -> DependencyValidationRule:
        return self._dependency_rule

    @property
    def composite_rules(self) -> CompositeValidationRule:
        return self._composite_rules

    # ------------------------------------------------------------------
    # Provider input validation
    # ------------------------------------------------------------------

    def validate_provider_inputs(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ValidationResult:
        """Validate provider context and requested metric IDs before extraction.

        Checks:
          - Context is not None.
          - All metric IDs are in the valid set.
          - ``repo_path``, ``repository_id``, and ``analysis_id`` are non-empty.
          - ``timeout_seconds`` is positive.
        """
        violations: List[str] = []
        warnings: List[str] = []

        if context is None:
            return _result_fail(
                ["ProviderContext must not be None"],
                rule_id="ENGINE-INPUT",
            )

        if not isinstance(context, ProviderContext):
            violations.append(f"context must be ProviderContext, got {type(context).__name__}")
            return _result_fail(violations, rule_id="ENGINE-INPUT")

        if not context.repo_path:
            violations.append("repo_path must not be empty")
        if not context.repository_id:
            violations.append("repository_id must not be empty")
        if not context.analysis_id:
            violations.append("analysis_id must not be empty")
        if context.timeout_seconds <= 0:
            violations.append(f"timeout_seconds must be positive, got {context.timeout_seconds}")

        if not metric_ids:
            violations.append("metric_ids must not be empty")
        else:
            for mid in metric_ids:
                if mid not in VALID_METRIC_IDS:
                    violations.append(f"Invalid metric ID: {mid!r} (valid: {sorted(VALID_METRIC_IDS)})")

        if violations:
            return _result_fail(violations, rule_id="ENGINE-INPUT")

        return _result_ok("ENGINE-INPUT", warnings)

    # ------------------------------------------------------------------
    # Provider output validation
    # ------------------------------------------------------------------

    def validate_provider_outputs(self, result: ExtractionResult) -> ValidationResult:
        """Validate the structure of an ExtractionResult after extraction.

        Checks:
          - Result is not None.
          - ``provider_id`` is non-empty.
          - ``metric_id`` is a valid metric.
          - ``observations`` is a non-empty tuple.
          - ``confidence`` is in [0.0, 1.0].
          - ``extraction_time_ms`` is non-negative.
        """
        violations: List[str] = []
        warnings: List[str] = []

        if result is None:
            return _result_fail(
                ["ExtractionResult must not be None"],
                rule_id="ENGINE-OUTPUT",
            )

        if not isinstance(result, ExtractionResult):
            return _result_fail(
                [f"result must be ExtractionResult, got {type(result).__name__}"],
                rule_id="ENGINE-OUTPUT",
            )

        if not result.provider_id:
            violations.append("provider_id must not be empty")

        if result.metric_id not in VALID_METRIC_IDS:
            violations.append(f"metric_id {result.metric_id!r} is not a valid metric ID")

        if not result.observations or not isinstance(result.observations, tuple):
            violations.append("observations must be a non-empty tuple")

        if not isinstance(result.confidence, (int, float)):
            violations.append(f"confidence must be numeric, got {type(result.confidence).__name__}")
        elif not (0.0 <= result.confidence <= 1.0):
            violations.append(f"confidence {result.confidence} is outside [0.0, 1.0]")

        if result.extraction_time_ms < 0:
            violations.append(f"extraction_time_ms must be non-negative, got {result.extraction_time_ms}")

        if result.is_empty:
            warnings.append(f"Extraction produced no observations for metric {result.metric_id}")

        if violations:
            return _result_fail(violations, rule_id="ENGINE-OUTPUT")

        return _result_ok("ENGINE-OUTPUT", warnings)

    # ------------------------------------------------------------------
    # Observation completeness
    # ------------------------------------------------------------------

    def validate_observation_completeness(self, observations: Sequence[Any], metric_id: str) -> ValidationResult:
        """Check that every observation has all required fields populated.

        Runs the schema rule on each observation and collects failures.
        """
        if not observations:
            return _result_fail(
                [f"No observations to validate for metric {metric_id}"],
                rule_id="ENGINE-COMPLETENESS",
            )

        violations: List[str] = []
        warnings: List[str] = []

        for idx, obs in enumerate(observations):
            result = self._schema_rule.validate(obs, metric_id)
            if not result.is_valid:
                for v in result.violations:
                    violations.append(f"Observation[{idx}]: {v}")
            warnings.extend(f"Observation[{idx}]: {w}" for w in result.warnings)

        if violations:
            return _result_fail(violations, rule_id="ENGINE-COMPLETENESS")

        return _result_ok("ENGINE-COMPLETENESS", warnings)

    # ------------------------------------------------------------------
    # Confidence validation (standalone)
    # ------------------------------------------------------------------

    def validate_confidence(self, confidence: Any, metric_id: str) -> ValidationResult:
        """Validate a standalone confidence value."""
        if confidence is None:
            return _result_fail(
                [f"Confidence must not be None for metric {metric_id}"],
                rule_id="ENGINE-CONFIDENCE",
            )

        if not isinstance(confidence, (int, float)):
            return _result_fail(
                [f"Confidence must be numeric for metric {metric_id}, " f"got {type(confidence).__name__}"],
                rule_id="ENGINE-CONFIDENCE",
            )

        if not (0.0 <= float(confidence) <= 1.0):
            return _result_fail(
                [f"Confidence {confidence} is outside [0.0, 1.0] " f"for metric {metric_id}"],
                rule_id="ENGINE-CONFIDENCE",
            )

        return _result_ok("ENGINE-CONFIDENCE")

    # ------------------------------------------------------------------
    # Metric support validation
    # ------------------------------------------------------------------

    def validate_metric_support(
        self,
        provider_caps: ProviderCapability,
        metric_id: str,
    ) -> ValidationResult:
        """Validate that a provider's capabilities support a given metric."""
        violations: List[str] = []
        warnings: List[str] = []

        if provider_caps is None:
            return _result_fail(
                ["ProviderCapability must not be None"],
                rule_id="ENGINE-SUPPORT",
            )

        if not isinstance(provider_caps, ProviderCapability):
            return _result_fail(
                [f"provider_caps must be ProviderCapability, " f"got {type(provider_caps).__name__}"],
                rule_id="ENGINE-SUPPORT",
            )

        if metric_id not in VALID_METRIC_IDS:
            violations.append(f"Invalid metric ID: {metric_id!r}")

        if not provider_caps.supports_metric(metric_id):
            supported = sorted(provider_caps.supported_metrics)
            violations.append(f"Provider does not support metric {metric_id!r}; " f"supported: {supported}")

        if violations:
            return _result_fail(violations, rule_id="ENGINE-SUPPORT")

        return _result_ok("ENGINE-SUPPORT", warnings)

    # ------------------------------------------------------------------
    # Schema validation (standalone)
    # ------------------------------------------------------------------

    def validate_schema(self, observation: Any, metric_id: str) -> ValidationResult:
        """Validate a single observation against the schema rule."""
        return self._schema_rule.validate(observation, metric_id)

    # ------------------------------------------------------------------
    # Bounds validation (standalone)
    # ------------------------------------------------------------------

    def validate_bounds(self, value: Any, metric_id: str) -> ValidationResult:
        """Validate a value against metric bounds."""
        if value is None:
            return _result_fail(
                [f"Value must not be None for metric {metric_id}"],
                rule_id="ENGINE-BOUNDS",
            )

        if not isinstance(value, (int, float)):
            return _result_fail(
                [f"Value must be numeric for metric {metric_id}, " f"got {type(value).__name__}"],
                rule_id="ENGINE-BOUNDS",
            )

        bounds = METRIC_BOUNDS.get(metric_id)
        if bounds is None:
            return _result_fail(
                [f"No bounds defined for metric {metric_id}"],
                rule_id="ENGINE-BOUNDS",
            )

        if not bounds.validate(float(value)):
            return _result_fail(
                [
                    f"Value {value} is outside bounds [{bounds.min_value}, "
                    f"{bounds.max_value}] for metric {metric_id}"
                ],
                rule_id="ENGINE-BOUNDS",
                metadata={
                    "metric_id": metric_id,
                    "value": float(value),
                    "min_value": bounds.min_value,
                    "max_value": bounds.max_value,
                },
            )

        return _result_ok("ENGINE-BOUNDS")

    # ------------------------------------------------------------------
    # Batch validation
    # ------------------------------------------------------------------

    def validate_batch(self, observations: Sequence[Any], metric_id: str) -> List[ValidationResult]:
        """Validate every observation in a batch using the composite rule set.

        Before validating, the dependency rule is seeded with the metric IDs
        present in the batch so dependency checks can resolve correctly.

        Returns:
            One ValidationResult per observation, in order.
        """
        if not observations:
            return [
                _result_fail(
                    [f"No observations to validate for metric {metric_id}"],
                    rule_id="ENGINE-BATCH",
                )
            ]

        # Seed dependency rule with metrics present in this batch
        metrics_in_batch: FrozenSet[str] = frozenset(
            obs.get("metric_id") if isinstance(obs, dict) else getattr(obs, "metric_id", None)
            for obs in observations
            if obs is not None
        ) - {
            None
        }  # type: ignore[arg-type]

        self._dependency_rule.set_observed_metrics(metrics_in_batch)

        results: List[ValidationResult] = []
        for obs in observations:
            results.append(self._composite_rules.validate(obs, metric_id))
        return results

    # ------------------------------------------------------------------
    # Recovery suggestions
    # ------------------------------------------------------------------

    @staticmethod
    def suggest_recovery(result: ValidationResult, metric_id: str) -> List[RecoverySuggestion]:
        """Generate recovery suggestions for a failed validation result.

        Inspects violations and produces actionable recommendations
        ordered by severity (high first).
        """
        suggestions: List[RecoverySuggestion] = []

        for violation in result.violations:
            low = violation.lower()

            if "missing required field" in low:
                field_name = violation.split("'")[1] if "'" in violation else "unknown"
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=f"Populate the '{field_name}' field in the observation payload.",
                        severity="high",
                    )
                )

            elif "outside bounds" in low or "out of valid" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            f"Verify the extracted value against the expected range for "
                            f"metric {metric_id}. Check source data quality."
                        ),
                        severity="high",
                    )
                )

            elif "confidence" in low and "outside" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            "Clamp the confidence score to [0.0, 1.0]. " "Check normalization logic in the provider."
                        ),
                        severity="medium",
                    )
                )

            elif "stale" in low or "freshness" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            "Refresh the observation data. Consider reducing the polling "
                            "interval or switching to a real-time provider."
                        ),
                        severity="medium",
                    )
                )

            elif "depends on" in low and "not present" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            "Ensure prerequisite metrics are extracted in the same batch "
                            "or a preceding batch before this metric."
                        ),
                        severity="high",
                    )
                )

            elif "does not support metric" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            "Register a provider that declares support for this metric, "
                            "or add the metric to this provider's capability set."
                        ),
                        severity="high",
                    )
                )

            elif "no bounds defined" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            f"Add metric {metric_id} to METRIC_BOUNDS in context.py "
                            f"with appropriate min/max values."
                        ),
                        severity="medium",
                    )
                )

            elif "future" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            "Correct the observation timestamp. Ensure clocks are "
                            "synchronised and timestamps use UTC."
                        ),
                        severity="medium",
                    )
                )

            elif "must not be empty" in low or "must not be none" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            "Ensure the provider populates all required fields before " "returning the result."
                        ),
                        severity="high",
                    )
                )

            elif "must be numeric" in low:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion=(
                            "Ensure the value is a numeric type (int or float). "
                            "Check for string-to-number conversion issues."
                        ),
                        severity="medium",
                    )
                )

            else:
                suggestions.append(
                    RecoverySuggestion(
                        issue=violation,
                        suggestion="Review the observation payload and provider logic.",
                        severity="low",
                    )
                )

        # Sort: high first, then medium, then low
        severity_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda s: severity_order.get(s.severity, 3))

        return suggestions
