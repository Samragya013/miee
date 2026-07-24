"""
MIIE v1.6 Validation Rules — Rule definitions for observation validation.

Implements OVR-v1.0 §9 validation rules.
Provides composable validation rules for metric values.

Reference: OVR-v1.0, OPC-v1.0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from miie.contracts.observation_types import (
    METRIC_BOUNDS,
    ValidationResult,
)

# ---------------------------------------------------------------------------
# Validation Rule Interface
# ---------------------------------------------------------------------------


class ValidationRule(ABC):
    """OVR §9.1 — Base validation rule interface.

    All validation rules inherit from this class.
    """

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of this rule."""
        ...

    @abstractmethod
    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate a value against this rule.

        Args:
            value: Value to validate.
            context: Optional validation context.

        Returns:
            ValidationResult with validation status.
        """
        ...

    def __and__(self, other: ValidationRule) -> CompositeValidationRule:
        """Combine two rules with AND logic."""
        return CompositeValidationRule([self, other], operator="and")

    def __or__(self, other: ValidationRule) -> CompositeValidationRule:
        """Combine two rules with OR logic."""
        return CompositeValidationRule([self, other], operator="or")


# ---------------------------------------------------------------------------
# Concrete Validation Rules (OVR §9.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RangeValidationRule(ValidationRule):
    """OVR §9.3 — Range validation rule.

    Validates that a numeric value is within specified bounds.
    """

    metric_id: str
    min_value: float
    max_value: float

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return f"VR-RANGE-{self.metric_id}"

    @property
    def description(self) -> str:
        """Human-readable description of this rule."""
        return f"Validate {self.metric_id} is in range [{self.min_value}, {self.max_value}]"

    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate value is within range.

        Args:
            value: Numeric value to validate.
            context: Optional validation context.

        Returns:
            ValidationResult with validation status.
        """
        if not isinstance(value, (int, float)):
            return ValidationResult.failure(
                [f"Expected numeric value, got {type(value).__name__}"],
                rule_id=self.rule_id,
            )

        if value < self.min_value or value > self.max_value:
            return ValidationResult.failure(
                [f"{self.metric_id} value {value} is out of range " f"[{self.min_value}, {self.max_value}]"],
                rule_id=self.rule_id,
            )

        return ValidationResult.success()


@dataclass(frozen=True)
class UnitValidationRule(ValidationRule):
    """OVR §9.3 — Unit validation rule.

    Validates that a metric value has the correct unit.
    """

    metric_id: str
    expected_unit: str

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return f"VR-UNIT-{self.metric_id}"

    @property
    def description(self) -> str:
        """Human-readable description of this rule."""
        return f"Validate {self.metric_id} has unit '{self.expected_unit}'"

    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate value has correct unit.

        Args:
            value: ObservationMetrics to validate.
            context: Optional validation context containing 'unit'.

        Returns:
            ValidationResult with validation status.
        """
        unit = context.get("unit") if context else None
        if unit is None:
            return ValidationResult.failure(
                [f"No unit provided for {self.metric_id}"],
                rule_id=self.rule_id,
            )

        if unit != self.expected_unit:
            return ValidationResult.failure(
                [f"{self.metric_id} unit '{unit}' does not match " f"expected '{self.expected_unit}'"],
                rule_id=self.rule_id,
            )

        return ValidationResult.success()


@dataclass(frozen=True)
class ConfidenceValidationRule(ValidationRule):
    """OVR §9.3 — Confidence validation rule.

    Validates that a confidence score is within valid bounds.
    """

    min_confidence: float = 0.0
    max_confidence: float = 1.0
    min_acceptable: float = 0.3

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "VR-CONFIDENCE"

    @property
    def description(self) -> str:
        """Human-readable description of this rule."""
        return (
            f"Validate confidence is in [{self.min_confidence}, {self.max_confidence}] " f"and >= {self.min_acceptable}"
        )

    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate confidence score.

        Args:
            value: Confidence score to validate.
            context: Optional validation context.

        Returns:
            ValidationResult with validation status.
        """
        if not isinstance(value, (int, float)):
            return ValidationResult.failure(
                [f"Expected numeric confidence, got {type(value).__name__}"],
                rule_id=self.rule_id,
            )

        if value < self.min_confidence or value > self.max_confidence:
            return ValidationResult.failure(
                [f"Confidence {value} is out of range " f"[{self.min_confidence}, {self.max_confidence}]"],
                rule_id=self.rule_id,
            )

        if value < self.min_acceptable:
            return ValidationResult.with_warnings(
                [f"Confidence {value} is below acceptable threshold {self.min_acceptable}"]
            )

        return ValidationResult.success()


@dataclass(frozen=True)
class FreshnessValidationRule(ValidationRule):
    """OVR §9.3 — Freshness validation rule.

    Validates that an observation is within acceptable age.
    """

    max_age_hours: float = 24.0

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "VR-FRESHNESS"

    @property
    def description(self) -> str:
        """Human-readable description of this rule."""
        return f"Validate observation is less than {self.max_age_hours} hours old"

    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate observation freshness.

        Args:
            value: Observation timestamp (datetime or ISO string).
            context: Optional validation context.

        Returns:
            ValidationResult with validation status.
        """
        if isinstance(value, str):
            try:
                obs_time = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return ValidationResult.failure(
                    [f"Invalid timestamp format: {value}"],
                    rule_id=self.rule_id,
                )
        elif isinstance(value, datetime):
            obs_time = value
        else:
            return ValidationResult.failure(
                [f"Expected datetime or ISO string, got {type(value).__name__}"],
                rule_id=self.rule_id,
            )

        now = datetime.now(timezone.utc)
        age_hours = (now - obs_time).total_seconds() / 3600

        if age_hours > self.max_age_hours:
            return ValidationResult.failure(
                [f"Observation is {age_hours:.1f} hours old, " f"exceeds max age {self.max_age_hours} hours"],
                rule_id=self.rule_id,
            )

        return ValidationResult.success()


@dataclass(frozen=True)
class DependencyValidationRule(ValidationRule):
    """OVR §9.3 — Dependency validation rule.

    Validates that all required dependencies are present.
    """

    required_dependencies: List[str] = field(default_factory=list)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "VR-DEPENDENCY"

    @property
    def description(self) -> str:
        """Human-readable description of this rule."""
        return f"Validate required dependencies are present: {self.required_dependencies}"

    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate dependencies are present.

        Args:
            value: Value to check (ignored for this rule).
            context: Optional validation context containing 'available_dependencies'.

        Returns:
            ValidationResult with validation status.
        """
        available = context.get("available_dependencies", []) if context else []
        missing = [dep for dep in self.required_dependencies if dep not in available]

        if missing:
            return ValidationResult.failure(
                [f"Missing required dependencies: {missing}"],
                rule_id=self.rule_id,
            )

        return ValidationResult.success()


@dataclass(frozen=True)
class SchemaValidationRule(ValidationRule):
    """OVR §9.3 — Schema validation rule.

    Validates that an observation conforms to the expected schema.
    """

    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "VR-SCHEMA"

    @property
    def description(self) -> str:
        """Human-readable description of this rule."""
        return f"Validate schema with required fields: {self.required_fields}"

    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate observation schema.

        Args:
            value: Observation to validate (must be a dict or dataclass).
            context: Optional validation context.

        Returns:
            ValidationResult with validation status.
        """
        if value is None:
            return ValidationResult.failure(
                ["Observation is None"],
                rule_id=self.rule_id,
            )

        # Convert dataclass to dict if needed
        if hasattr(value, "__dataclass_fields__"):
            obs_dict = {f: getattr(value, f) for f in value.__dataclass_fields__}
        elif isinstance(value, dict):
            obs_dict = value
        else:
            return ValidationResult.failure(
                [f"Expected dict or dataclass, got {type(value).__name__}"],
                rule_id=self.rule_id,
            )

        missing = [field for field in self.required_fields if field not in obs_dict]
        if missing:
            return ValidationResult.failure(
                [f"Missing required fields: {missing}"],
                rule_id=self.rule_id,
            )

        return ValidationResult.success()


# ---------------------------------------------------------------------------
# Composite Validation Rule (OVR §9.4)
# ---------------------------------------------------------------------------


@dataclass
class CompositeValidationRule(ValidationRule):
    """OVR §9.4 — Composite validation rule.

    Combines multiple rules with AND or OR logic.
    """

    rules: List[ValidationRule] = field(default_factory=list)
    operator: str = "and"  # "and" or "or"

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        rule_ids = [r.rule_id for r in self.rules]
        return f"VR-COMPOSITE-{self.operator.upper()}-{'-'.join(rule_ids)}"

    @property
    def description(self) -> str:
        """Human-readable description of this rule."""
        rule_descs = [r.description for r in self.rules]
        return f"Composite ({self.operator}): {rule_descs}"

    def validate(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate value against all rules.

        Args:
            value: Value to validate.
            context: Optional validation context.

        Returns:
            ValidationResult with validation status.
        """
        if not self.rules:
            return ValidationResult.success()

        results = [rule.validate(value, context) for rule in self.rules]

        if self.operator == "and":
            # All rules must pass
            violations = []
            warnings = []
            for result in results:
                if not result.is_valid:
                    violations.extend(result.violations)
                warnings.extend(result.warnings)

            if violations:
                return ValidationResult.failure(violations, rule_id=self.rule_id)
            return ValidationResult.with_warnings(warnings) if warnings else ValidationResult.success()

        elif self.operator == "or":
            # At least one rule must pass
            all_violations = []
            any_warnings = []
            for result in results:
                if result.is_valid:
                    return ValidationResult.with_warnings(result.warnings)
                all_violations.extend(result.violations)
                any_warnings.extend(result.warnings)

            # No rules passed
            return ValidationResult.failure(all_violations, rule_id=self.rule_id)

        else:
            raise ValueError(f"Unknown operator: {self.operator}")


# ---------------------------------------------------------------------------
# Validation Context (OVR §9.5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ValidationContext:
    """OVR §9.5 — Context for validation rules.

    Provides additional information needed for validation.
    """

    metric_id: str
    timestamp: Optional[datetime] = None
    source_type: Optional[str] = None
    available_dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        result: Dict[str, Any] = {
            "metric_id": self.metric_id,
            "available_dependencies": self.available_dependencies,
        }
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        if self.source_type:
            result["source_type"] = self.source_type
        result.update(self.metadata)
        return result


# ---------------------------------------------------------------------------
# Rule Factory Functions
# ---------------------------------------------------------------------------


def create_metric_validation_rules(metric_id: str) -> List[ValidationRule]:
    """Create default validation rules for a metric.

    Args:
        metric_id: Metric identifier (e.g., "M-01").

    Returns:
        List of validation rules for the metric.

    Raises:
        ValueError: If metric_id is not valid.
    """
    if metric_id not in METRIC_BOUNDS:
        raise ValueError(f"Unknown metric_id: {metric_id}")

    bounds = METRIC_BOUNDS[metric_id]

    return [
        RangeValidationRule(
            metric_id=metric_id,
            min_value=bounds.min_value,
            max_value=bounds.max_value,
        ),
        UnitValidationRule(
            metric_id=metric_id,
            expected_unit=bounds.unit,
        ),
        ConfidenceValidationRule(),
        SchemaValidationRule(
            required_fields=["metric_id", "value", "unit"],
            optional_fields=["confidence", "is_estimated"],
        ),
    ]


def create_all_validation_rules() -> Dict[str, List[ValidationRule]]:
    """Create validation rules for all metrics.

    Returns:
        Dict mapping metric_id to list of validation rules.
    """
    rules: Dict[str, List[ValidationRule]] = {}
    for metric_id in METRIC_BOUNDS:
        rules[metric_id] = create_metric_validation_rules(metric_id)
    return rules
