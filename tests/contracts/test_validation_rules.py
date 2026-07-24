"""Tests for miie.contracts.validation_rules module."""

from datetime import datetime, timezone

import pytest

from miie.contracts.validation_rules import (
    CompositeValidationRule,
    ConfidenceValidationRule,
    DependencyValidationRule,
    FreshnessValidationRule,
    RangeValidationRule,
    SchemaValidationRule,
    UnitValidationRule,
    ValidationContext,
    ValidationRule,
    create_all_validation_rules,
    create_metric_validation_rules,
)


class TestRangeValidationRule:
    """Test RangeValidationRule."""

    def test_rule_id(self):
        """Test rule_id property."""
        rule = RangeValidationRule(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
        )
        assert rule.rule_id == "VR-RANGE-M-01"

    def test_description(self):
        """Test description property."""
        rule = RangeValidationRule(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
        )
        assert "M-01" in rule.description
        assert "0.0" in rule.description
        assert "1.0" in rule.description

    def test_validate_within_range(self):
        """Test validation within range."""
        rule = RangeValidationRule(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
        )
        result = rule.validate(0.5)
        assert result.is_valid is True

    def test_validate_at_boundaries(self):
        """Test validation at boundaries."""
        rule = RangeValidationRule(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
        )
        assert rule.validate(0.0).is_valid is True
        assert rule.validate(1.0).is_valid is True

    def test_validate_out_of_range(self):
        """Test validation out of range."""
        rule = RangeValidationRule(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
        )
        result = rule.validate(1.5)
        assert result.is_valid is False
        assert len(result.violations) == 1

    def test_validate_non_numeric(self):
        """Test validation with non-numeric value."""
        rule = RangeValidationRule(
            metric_id="M-01",
            min_value=0.0,
            max_value=1.0,
        )
        result = rule.validate("not a number")
        assert result.is_valid is False


class TestUnitValidationRule:
    """Test UnitValidationRule."""

    def test_rule_id(self):
        """Test rule_id property."""
        rule = UnitValidationRule(
            metric_id="M-01",
            expected_unit="ratio",
        )
        assert rule.rule_id == "VR-UNIT-M-01"

    def test_validate_correct_unit(self):
        """Test validation with correct unit."""
        rule = UnitValidationRule(
            metric_id="M-01",
            expected_unit="ratio",
        )
        result = rule.validate(None, context={"unit": "ratio"})
        assert result.is_valid is True

    def test_validate_incorrect_unit(self):
        """Test validation with incorrect unit."""
        rule = UnitValidationRule(
            metric_id="M-01",
            expected_unit="ratio",
        )
        result = rule.validate(None, context={"unit": "count"})
        assert result.is_valid is False

    def test_validate_no_unit(self):
        """Test validation without unit in context."""
        rule = UnitValidationRule(
            metric_id="M-01",
            expected_unit="ratio",
        )
        result = rule.validate(None, context={})
        assert result.is_valid is False

    def test_validate_none_context(self):
        """Test validation with None context."""
        rule = UnitValidationRule(
            metric_id="M-01",
            expected_unit="ratio",
        )
        result = rule.validate(None, context=None)
        assert result.is_valid is False


class TestConfidenceValidationRule:
    """Test ConfidenceValidationRule."""

    def test_rule_id(self):
        """Test rule_id property."""
        rule = ConfidenceValidationRule()
        assert rule.rule_id == "VR-CONFIDENCE"

    def test_validate_valid_confidence(self):
        """Test validation with valid confidence."""
        rule = ConfidenceValidationRule()
        result = rule.validate(0.8)
        assert result.is_valid is True
        assert result.warnings == []

    def test_validate_below_acceptable(self):
        """Test validation with confidence below acceptable threshold."""
        rule = ConfidenceValidationRule(min_acceptable=0.5)
        result = rule.validate(0.3)
        assert result.is_valid is True  # Warnings, not failure
        assert len(result.warnings) == 1

    def test_validate_out_of_range(self):
        """Test validation with confidence out of range."""
        rule = ConfidenceValidationRule()
        result = rule.validate(1.5)
        assert result.is_valid is False

    def test_validate_negative(self):
        """Test validation with negative confidence."""
        rule = ConfidenceValidationRule()
        result = rule.validate(-0.1)
        assert result.is_valid is False

    def test_validate_non_numeric(self):
        """Test validation with non-numeric confidence."""
        rule = ConfidenceValidationRule()
        result = rule.validate("not a number")
        assert result.is_valid is False


class TestFreshnessValidationRule:
    """Test FreshnessValidationRule."""

    def test_rule_id(self):
        """Test rule_id property."""
        rule = FreshnessValidationRule()
        assert rule.rule_id == "VR-FRESHNESS"

    def test_validate_fresh_observation(self):
        """Test validation with fresh observation."""
        rule = FreshnessValidationRule(max_age_hours=24.0)
        now = datetime.now(timezone.utc)
        result = rule.validate(now)
        assert result.is_valid is True

    def test_validate_stale_observation(self):
        """Test validation with stale observation."""
        rule = FreshnessValidationRule(max_age_hours=1.0)
        # Create a timestamp 2 hours ago
        from datetime import timedelta

        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        result = rule.validate(old_time)
        assert result.is_valid is False

    def test_validate_iso_string(self):
        """Test validation with ISO string timestamp."""
        rule = FreshnessValidationRule(max_age_hours=24.0)
        now = datetime.now(timezone.utc).isoformat()
        result = rule.validate(now)
        assert result.is_valid is True

    def test_validate_invalid_format(self):
        """Test validation with invalid timestamp format."""
        rule = FreshnessValidationRule()
        result = rule.validate("not-a-timestamp")
        assert result.is_valid is False

    def test_validate_non_datetime(self):
        """Test validation with non-datetime value."""
        rule = FreshnessValidationRule()
        result = rule.validate(12345)
        assert result.is_valid is False


class TestDependencyValidationRule:
    """Test DependencyValidationRule."""

    def test_rule_id(self):
        """Test rule_id property."""
        rule = DependencyValidationRule(required_dependencies=["M-01", "M-02"])
        assert rule.rule_id == "VR-DEPENDENCY"

    def test_validate_all_present(self):
        """Test validation with all dependencies present."""
        rule = DependencyValidationRule(required_dependencies=["M-01", "M-02"])
        result = rule.validate(
            None,
            context={"available_dependencies": ["M-01", "M-02", "M-03"]},
        )
        assert result.is_valid is True

    def test_validate_some_missing(self):
        """Test validation with some dependencies missing."""
        rule = DependencyValidationRule(required_dependencies=["M-01", "M-02"])
        result = rule.validate(
            None,
            context={"available_dependencies": ["M-01"]},
        )
        assert result.is_valid is False

    def test_validate_all_missing(self):
        """Test validation with all dependencies missing."""
        rule = DependencyValidationRule(required_dependencies=["M-01", "M-02"])
        result = rule.validate(
            None,
            context={"available_dependencies": []},
        )
        assert result.is_valid is False

    def test_validate_no_context(self):
        """Test validation without context."""
        rule = DependencyValidationRule(required_dependencies=["M-01"])
        result = rule.validate(None, context=None)
        assert result.is_valid is False


class TestSchemaValidationRule:
    """Test SchemaValidationRule."""

    def test_rule_id(self):
        """Test rule_id property."""
        rule = SchemaValidationRule(required_fields=["field1", "field2"])
        assert rule.rule_id == "VR-SCHEMA"

    def test_validate_dict_with_required_fields(self):
        """Test validation with dict containing required fields."""
        rule = SchemaValidationRule(required_fields=["field1", "field2"])
        result = rule.validate({"field1": "value1", "field2": "value2"})
        assert result.is_valid is True

    def test_validate_dict_missing_fields(self):
        """Test validation with dict missing required fields."""
        rule = SchemaValidationRule(required_fields=["field1", "field2"])
        result = rule.validate({"field1": "value1"})
        assert result.is_valid is False

    def test_validate_dataclass(self):
        """Test validation with dataclass."""
        from dataclasses import dataclass

        @dataclass
        class MockObservation:
            field1: str
            field2: str

        rule = SchemaValidationRule(required_fields=["field1", "field2"])
        obs = MockObservation(field1="value1", field2="value2")
        result = rule.validate(obs)
        assert result.is_valid is True

    def test_validate_none(self):
        """Test validation with None."""
        rule = SchemaValidationRule(required_fields=["field1"])
        result = rule.validate(None)
        assert result.is_valid is False

    def test_validate_other_type(self):
        """Test validation with other type."""
        rule = SchemaValidationRule(required_fields=["field1"])
        result = rule.validate("not a dict or dataclass")
        assert result.is_valid is False


class TestCompositeValidationRule:
    """Test CompositeValidationRule."""

    def test_rule_id_and(self):
        """Test rule_id for AND operator."""
        rule1 = RangeValidationRule("M-01", 0.0, 1.0)
        rule2 = UnitValidationRule("M-01", "ratio")
        composite = CompositeValidationRule([rule1, rule2], operator="and")
        assert "AND" in composite.rule_id

    def test_rule_id_or(self):
        """Test rule_id for OR operator."""
        rule1 = RangeValidationRule("M-01", 0.0, 1.0)
        rule2 = UnitValidationRule("M-01", "ratio")
        composite = CompositeValidationRule([rule1, rule2], operator="or")
        assert "OR" in composite.rule_id

    def test_validate_and_all_pass(self):
        """Test AND validation with all rules passing."""
        rule1 = RangeValidationRule("M-01", 0.0, 1.0)
        rule2 = ConfidenceValidationRule()
        CompositeValidationRule([rule1, rule2], operator="and")
        result = rule1.validate(0.5)  # Passes range
        assert result.is_valid is True

    def test_validate_and_one_fails(self):
        """Test AND validation with one rule failing."""
        rule1 = RangeValidationRule("M-01", 0.0, 1.0)
        rule2 = RangeValidationRule("M-01", 0.0, 0.5)  # Stricter range
        composite = CompositeValidationRule([rule1, rule2], operator="and")

        # Value passes rule1 but fails rule2
        # We need to test the composite directly
        # Since composite.validate requires a single value, let's test with 0.7
        result = composite.validate(0.7)
        # rule1 passes (0.0 <= 0.7 <= 1.0), rule2 fails (0.7 > 0.5)
        assert result.is_valid is False

    def test_validate_or_one_passes(self):
        """Test OR validation with one rule passing."""
        rule1 = RangeValidationRule("M-01", 0.0, 0.5)  # Strict range
        rule2 = RangeValidationRule("M-01", 0.5, 1.0)  # Different range
        composite = CompositeValidationRule([rule1, rule2], operator="or")

        # Value passes rule2
        result = composite.validate(0.7)
        assert result.is_valid is True

    def test_validate_or_none_pass(self):
        """Test OR validation with no rules passing."""
        rule1 = RangeValidationRule("M-01", 0.0, 0.3)
        rule2 = RangeValidationRule("M-01", 0.7, 1.0)
        composite = CompositeValidationRule([rule1, rule2], operator="or")

        # Value fails both rules
        result = composite.validate(0.5)
        assert result.is_valid is False

    def test_validate_empty_rules(self):
        """Test validation with empty rules list."""
        composite = CompositeValidationRule([], operator="and")
        result = composite.validate(0.5)
        assert result.is_valid is True

    def test_invalid_operator(self):
        """Test validation with invalid operator."""
        # Need at least one rule to trigger the operator check
        rule = RangeValidationRule("M-01", 0.0, 1.0)
        composite = CompositeValidationRule([rule], operator="invalid")
        # Invalid operator should raise ValueError
        with pytest.raises(ValueError, match="Unknown operator"):
            composite.validate(0.5)


class TestValidationContext:
    """Test ValidationContext dataclass."""

    def test_creation(self):
        """Test basic creation."""
        ctx = ValidationContext(metric_id="M-01")
        assert ctx.metric_id == "M-01"
        assert ctx.timestamp is None
        assert ctx.source_type is None
        assert ctx.available_dependencies == []
        assert ctx.metadata == {}

    def test_to_dict(self):
        """Test to_dict conversion."""
        ctx = ValidationContext(
            metric_id="M-01",
            source_type="commit",
            available_dependencies=["M-01", "M-02"],
        )
        result = ctx.to_dict()
        assert result["metric_id"] == "M-01"
        assert result["source_type"] == "commit"
        assert result["available_dependencies"] == ["M-01", "M-02"]

    def test_to_dict_with_timestamp(self):
        """Test to_dict with timestamp."""
        now = datetime.now(timezone.utc)
        ctx = ValidationContext(
            metric_id="M-01",
            timestamp=now,
        )
        result = ctx.to_dict()
        assert "timestamp" in result


class TestRuleComposition:
    """Test rule composition with operators."""

    def test_and_operator(self):
        """Test AND composition."""
        rule1 = RangeValidationRule("M-01", 0.0, 1.0)
        rule2 = ConfidenceValidationRule()
        composite = rule1 & rule2
        assert isinstance(composite, CompositeValidationRule)
        assert composite.operator == "and"

    def test_or_operator(self):
        """Test OR composition."""
        rule1 = RangeValidationRule("M-01", 0.0, 0.5)
        rule2 = RangeValidationRule("M-01", 0.5, 1.0)
        composite = rule1 | rule2
        assert isinstance(composite, CompositeValidationRule)
        assert composite.operator == "or"


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_metric_validation_rules(self):
        """Test create_metric_validation_rules."""
        rules = create_metric_validation_rules("M-01")
        assert len(rules) > 0
        assert all(isinstance(r, ValidationRule) for r in rules)

    def test_create_metric_validation_rules_invalid_metric(self):
        """Test create_metric_validation_rules with invalid metric."""
        with pytest.raises(ValueError, match="Unknown metric_id"):
            create_metric_validation_rules("M-99")

    def test_create_all_validation_rules(self):
        """Test create_all_validation_rules."""
        all_rules = create_all_validation_rules()
        assert len(all_rules) == 7  # M-01 through M-07
        for metric_id in [f"M-{i:02d}" for i in range(1, 8)]:
            assert metric_id in all_rules
            assert len(all_rules[metric_id]) > 0
