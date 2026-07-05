"""Tests for miie.providers.validation module."""

from datetime import datetime, timezone

import pytest

from miie.providers.context import (
    ExtractionResult,
    ProviderCapability,
    ProviderContext,
    QualityState,
)
from miie.providers.validation import (
    CompositeValidationRule,
    ConfidenceValidationRule,
    DependencyValidationRule,
    FreshnessValidationRule,
    ObservationValidationEngine,
    RangeValidationRule,
    RecoverySuggestion,
    SchemaValidationRule,
)


class TestObservationValidationEngine:
    def test_validate_provider_inputs_valid(self):
        engine = ObservationValidationEngine()
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        result = engine.validate_provider_inputs(ctx, ["M-02"])
        assert result.is_valid

    def test_validate_provider_inputs_empty_metrics(self):
        engine = ObservationValidationEngine()
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        result = engine.validate_provider_inputs(ctx, [])
        assert not result.is_valid

    def test_validate_provider_inputs_invalid_metric(self):
        engine = ObservationValidationEngine()
        ctx = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        result = engine.validate_provider_inputs(ctx, ["M-99"])
        assert not result.is_valid

    def test_validate_provider_outputs_valid(self):
        engine = ObservationValidationEngine()
        result = ExtractionResult(
            provider_id="git",
            metric_id="M-02",
            observations=(1, 2, 3),
            quality_state=QualityState.COMPLETE,
            confidence=0.9,
        )
        validation = engine.validate_provider_outputs(result)
        assert validation.is_valid

    def test_validate_provider_outputs_empty(self):
        engine = ObservationValidationEngine()
        result = ExtractionResult(
            provider_id="git",
            metric_id="M-02",
            observations=(),
        )
        validation = engine.validate_provider_outputs(result)
        assert not validation.is_valid

    def test_validate_observation_completeness_valid(self):
        engine = ObservationValidationEngine()
        obs = [
            {"value": 42.0, "metric_id": "M-02", "timestamp": "2024-01-01"},
            {"value": 100.0, "metric_id": "M-02", "timestamp": "2024-01-02"},
        ]
        result = engine.validate_observation_completeness(obs, "M-02")
        assert result.is_valid

    def test_validate_observation_completeness_missing_fields(self):
        engine = ObservationValidationEngine()
        obs = [{"value": 42.0}]
        result = engine.validate_observation_completeness(obs, "M-02")
        assert not result.is_valid

    def test_validate_observation_completeness_not_dict(self):
        engine = ObservationValidationEngine()
        obs = [1, 2, 3]
        result = engine.validate_observation_completeness(obs, "M-02")
        assert not result.is_valid

    def test_validate_confidence_valid(self):
        engine = ObservationValidationEngine()
        result = engine.validate_confidence(0.95, "M-02")
        assert result.is_valid

    def test_validate_confidence_invalid(self):
        engine = ObservationValidationEngine()
        result = engine.validate_confidence(1.5, "M-02")
        assert not result.is_valid

    def test_validate_confidence_none(self):
        engine = ObservationValidationEngine()
        result = engine.validate_confidence(None, "M-02")
        assert not result.is_valid

    def test_validate_metric_support(self):
        engine = ObservationValidationEngine()
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-01", "M-02"]),
            supported_source_types=frozenset(["commit"]),
        )
        result = engine.validate_metric_support(caps, "M-02")
        assert result.is_valid

    def test_validate_metric_support_not_supported(self):
        engine = ObservationValidationEngine()
        caps = ProviderCapability(
            supported_metrics=frozenset(["M-01"]),
            supported_source_types=frozenset(["commit"]),
        )
        result = engine.validate_metric_support(caps, "M-02")
        assert not result.is_valid

    def test_validate_schema(self):
        engine = ObservationValidationEngine()
        obs = {"value": 42.0, "metric_id": "M-02", "timestamp": "2024-01-01"}
        result = engine.validate_schema(obs, "M-02")
        assert result.is_valid

    def test_validate_schema_missing_fields(self):
        engine = ObservationValidationEngine()
        obs = {"value": 42.0}
        result = engine.validate_schema(obs, "M-02")
        assert not result.is_valid

    def test_validate_bounds_valid(self):
        engine = ObservationValidationEngine()
        result = engine.validate_bounds(0.5, "M-01")
        assert result.is_valid

    def test_validate_bounds_invalid(self):
        engine = ObservationValidationEngine()
        result = engine.validate_bounds(1.5, "M-01")
        assert not result.is_valid

    def test_validate_batch(self):
        engine = ObservationValidationEngine()
        observations = [
            {"value": 42.0, "metric_id": "M-02", "timestamp": "2024-01-01"},
            {"value": 100.0, "metric_id": "M-02", "timestamp": "2024-01-02"},
        ]
        results = engine.validate_batch(observations, "M-02")
        assert len(results) == 2


class TestValidationRules:
    def test_schema_rule_valid(self):
        rule = SchemaValidationRule()
        obs = {"value": 42.0, "metric_id": "M-02", "timestamp": "2024-01-01"}
        result = rule.validate(obs, "M-02")
        assert result.is_valid

    def test_schema_rule_missing(self):
        rule = SchemaValidationRule()
        obs = {}
        result = rule.validate(obs, "M-02")
        assert not result.is_valid

    def test_schema_rule_not_dict(self):
        rule = SchemaValidationRule()
        result = rule.validate("not a dict", "M-02")
        assert not result.is_valid

    def test_range_rule_valid(self):
        rule = RangeValidationRule()
        obs = {"value": 0.5}
        result = rule.validate(obs, "M-01")
        assert result.is_valid

    def test_range_rule_out_of_bounds(self):
        rule = RangeValidationRule()
        obs = {"value": 1.5}
        result = rule.validate(obs, "M-01")
        assert not result.is_valid

    def test_range_rule_no_value(self):
        rule = RangeValidationRule()
        obs = {}
        result = rule.validate(obs, "M-01")
        assert not result.is_valid

    def test_confidence_rule_valid(self):
        rule = ConfidenceValidationRule()
        obs = {"confidence": 0.95}
        result = rule.validate(obs, "M-02")
        assert result.is_valid

    def test_confidence_rule_no_confidence(self):
        rule = ConfidenceValidationRule()
        obs = {}
        result = rule.validate(obs, "M-02")
        assert result.is_valid  # defaults to 1.0

    def test_confidence_rule_out_of_bounds(self):
        rule = ConfidenceValidationRule()
        obs = {"confidence": 1.5}
        result = rule.validate(obs, "M-02")
        assert not result.is_valid

    def test_freshness_rule(self):
        rule = FreshnessValidationRule()
        obs = {"timestamp": datetime.now(timezone.utc).isoformat()}
        result = rule.validate(obs, "M-02")
        assert result.is_valid

    def test_dependency_rule(self):
        rule = DependencyValidationRule()
        obs = {}
        result = rule.validate(obs, "M-02")
        assert result.is_valid


class TestCompositeValidationRule:
    def test_composite_all_pass(self):
        rule = CompositeValidationRule(
            [
                RangeValidationRule(),
                ConfidenceValidationRule(),
            ]
        )
        obs = {"value": 0.5, "confidence": 0.95}
        result = rule.validate(obs, "M-01")
        assert result.is_valid

    def test_composite_one_fails(self):
        rule = CompositeValidationRule(
            [
                RangeValidationRule(),
                ConfidenceValidationRule(),
            ]
        )
        obs = {"value": 1.5, "confidence": 0.95}
        result = rule.validate(obs, "M-01")
        assert not result.is_valid


class TestRecoverySuggestion:
    def test_creation(self):
        suggestion = RecoverySuggestion(
            issue="Missing data",
            suggestion="Check provider configuration",
            severity="medium",
        )
        assert suggestion.issue == "Missing data"
        assert suggestion.suggestion == "Check provider configuration"
        assert suggestion.severity == "medium"

    def test_invalid_severity(self):
        with pytest.raises(ValueError):
            RecoverySuggestion(
                issue="test",
                suggestion="test",
                severity="invalid",
            )
