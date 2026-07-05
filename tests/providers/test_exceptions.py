"""Tests for miie.providers.exceptions module."""

import pytest

from miie.providers.context import ExtractionPhase, ProviderErrorContext
from miie.providers.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    DataFormatError,
    DependencyViolationError,
    DiscoveryError,
    DuplicateProviderError,
    ExtractionError,
    ExtractionTimeoutError,
    FreshnessViolationError,
    IncompatibleProviderError,
    ObservationError,
    PartialExtractionError,
    PipelineConsolidationError,
    PipelineError,
    PipelineStageError,
    PipelineTimeoutError,
    ProviderDisposedError,
    ProviderError,
    ProviderExtractionError,
    ProviderNotFoundError,
    ProviderNotInitializedError,
    ProviderNotReadyError,
    ProviderPausedError,
    RangeViolationError,
    RateLimitError,
    RegistrationError,
    RegistryError,
    SchemaViolationError,
    TimeoutError,
    ValidationError,
    create_extraction_error,
    create_provider_error,
)


class TestObservationError:
    def test_creation(self):
        err = ObservationError("test error")
        assert str(err) == "test error"
        assert err.message == "test error"
        assert err.error_code is None
        assert err.context is None
        assert err.cause is None

    def test_to_dict(self):
        err = ObservationError("test", error_code="E-001")
        d = err.to_dict()
        assert d["error_type"] == "ObservationError"
        assert d["message"] == "test"
        assert d["error_code"] == "E-001"

    def test_to_dict_with_context(self):
        ctx = ProviderErrorContext(
            provider_id="git",
            metric_id="M-02",
            extraction_phase=ExtractionPhase.EXTRACT,
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        err = ObservationError("test", context=ctx)
        d = err.to_dict()
        assert "context" in d
        assert d["context"]["provider_id"] == "git"

    def test_to_dict_with_cause(self):
        cause = ValueError("original")
        err = ObservationError("test", cause=cause)
        d = err.to_dict()
        assert d["cause"] == "original"


class TestProviderErrorHierarchy:
    def test_provider_error_is_observation_error(self):
        assert issubclass(ProviderError, ObservationError)

    def test_connection_error(self):
        assert issubclass(ConnectionError, ProviderError)

    def test_authentication_error(self):
        assert issubclass(AuthenticationError, ProviderError)

    def test_timeout_error(self):
        assert issubclass(TimeoutError, ProviderError)

    def test_rate_limit_error(self):
        err = RateLimitError("rate limited", retry_after_seconds=30.0)
        assert err.retry_after_seconds == 30.0

    def test_data_format_error(self):
        assert issubclass(DataFormatError, ProviderError)

    def test_provider_not_initialized_error(self):
        assert issubclass(ProviderNotInitializedError, ProviderError)

    def test_provider_disposed_error(self):
        assert issubclass(ProviderDisposedError, ProviderError)

    def test_provider_paused_error(self):
        assert issubclass(ProviderPausedError, ProviderError)


class TestExtractionErrorHierarchy:
    def test_extraction_error_is_observation_error(self):
        assert issubclass(ExtractionError, ObservationError)

    def test_provider_not_ready_error(self):
        assert issubclass(ProviderNotReadyError, ExtractionError)

    def test_incompatible_provider_error(self):
        assert issubclass(IncompatibleProviderError, ExtractionError)

    def test_partial_extraction_error(self):
        err = PartialExtractionError("partial", partial_results=[1, 2, 3])
        assert err.partial_results == [1, 2, 3]

    def test_extraction_timeout_error(self):
        assert issubclass(ExtractionTimeoutError, ExtractionError)

    def test_provider_extraction_error(self):
        provider_err = ConnectionError("connection failed")
        err = ProviderExtractionError("extraction failed", provider_error=provider_err)
        assert err.provider_error is provider_err


class TestValidationErrorHierarchy:
    def test_validation_error_is_observation_error(self):
        assert issubclass(ValidationError, ObservationError)

    def test_validation_error_with_violations(self):
        err = ValidationError("invalid", violations=["v1", "v2"])
        assert err.violations == ["v1", "v2"]

    def test_schema_violation_error(self):
        assert issubclass(SchemaViolationError, ValidationError)

    def test_range_violation_error(self):
        err = RangeViolationError("out of range", metric_id="M-02", value=100, min_value=0, max_value=10)
        assert err.metric_id == "M-02"
        assert err.value == 100
        assert err.min_value == 0
        assert err.max_value == 10

    def test_freshness_violation_error(self):
        err = FreshnessViolationError("too old", observation_time="2024-01-01T00:00:00", max_age_hours=24.0)
        assert err.observation_time == "2024-01-01T00:00:00"
        assert err.max_age_hours == 24.0

    def test_dependency_violation_error(self):
        err = DependencyViolationError("missing deps", missing_dependencies=["dep1", "dep2"])
        assert err.missing_dependencies == ["dep1", "dep2"]


class TestRegistryErrorHierarchy:
    def test_registry_error_is_observation_error(self):
        assert issubclass(RegistryError, ObservationError)

    def test_registration_error(self):
        assert issubclass(RegistrationError, RegistryError)

    def test_discovery_error(self):
        assert issubclass(DiscoveryError, RegistryError)

    def test_provider_not_found_error(self):
        err = ProviderNotFoundError("not found", provider_id="git", metric_id="M-02")
        assert err.provider_id == "git"
        assert err.metric_id == "M-02"

    def test_duplicate_provider_error(self):
        assert issubclass(DuplicateProviderError, RegistryError)

    def test_configuration_error(self):
        assert issubclass(ConfigurationError, RegistryError)


class TestPipelineErrorHierarchy:
    def test_pipeline_error_is_observation_error(self):
        assert issubclass(PipelineError, ObservationError)

    def test_pipeline_stage_error(self):
        err = PipelineStageError("stage failed", stage="extract")
        assert err.stage == "extract"

    def test_pipeline_timeout_error(self):
        assert issubclass(PipelineTimeoutError, PipelineError)

    def test_pipeline_consolidation_error(self):
        err = PipelineConsolidationError(
            "consolidation failed",
            failed_providers=["git"],
            successful_providers=["coverage"],
        )
        assert err.failed_providers == ["git"]
        assert err.successful_providers == ["coverage"]


class TestErrorFactories:
    def test_create_provider_error(self):
        err = create_provider_error("ConnectionError", "connection failed")
        assert isinstance(err, ConnectionError)
        assert err.message == "connection failed"

    def test_create_provider_error_unknown(self):
        with pytest.raises(ValueError, match="Unknown provider error type"):
            create_provider_error("UnknownError", "test")

    def test_create_extraction_error(self):
        err = create_extraction_error("PartialExtractionError", "partial")
        assert isinstance(err, PartialExtractionError)

    def test_create_extraction_error_unknown(self):
        with pytest.raises(ValueError, match="Unknown extraction error type"):
            create_extraction_error("UnknownError", "test")
