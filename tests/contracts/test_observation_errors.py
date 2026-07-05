"""Tests for miie.contracts.observation_errors module."""

from datetime import datetime, timezone

import pytest

from miie.contracts.observation_errors import (
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
from miie.contracts.observation_types import ExtractionPhase, ProviderErrorContext


class TestObservationError:
    """Test ObservationError base class."""

    def test_creation(self):
        """Test basic creation."""
        error = ObservationError("test error")
        assert str(error) == "test error"
        assert error.message == "test error"
        assert error.error_code is None
        assert error.context is None
        assert error.cause is None

    def test_with_context(self):
        """Test creation with context."""
        ctx = ProviderErrorContext(
            provider_id="test-provider",
            metric_id="M-01",
            extraction_phase=ExtractionPhase.EXTRACT,
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        error = ObservationError("test error", context=ctx)
        assert error.context is not None
        assert error.context.provider_id == "test-provider"

    def test_with_cause(self):
        """Test creation with cause."""
        original = ValueError("original error")
        error = ObservationError("test error", cause=original)
        assert error.cause is original

    def test_to_dict(self):
        """Test to_dict serialization."""
        error = ObservationError(
            "test error",
            error_code="E-001",
        )
        result = error.to_dict()
        assert result["error_type"] == "ObservationError"
        assert result["message"] == "test error"
        assert result["error_code"] == "E-001"

    def test_to_dict_with_context(self):
        """Test to_dict with context."""
        ctx = ProviderErrorContext(
            provider_id="test-provider",
            metric_id="M-01",
            extraction_phase=ExtractionPhase.EXTRACT,
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        error = ObservationError("test error", context=ctx)
        result = error.to_dict()
        assert "context" in result
        assert result["context"]["provider_id"] == "test-provider"

    def test_to_dict_with_cause(self):
        """Test to_dict with cause."""
        original = ValueError("original error")
        error = ObservationError("test error", cause=original)
        result = error.to_dict()
        assert "cause" in result
        assert result["cause"] == "original error"


class TestProviderErrors:
    """Test Provider error hierarchy."""

    def test_provider_error_is_observation_error(self):
        """Test ProviderError inherits from ObservationError."""
        error = ProviderError("test")
        assert isinstance(error, ObservationError)

    def test_connection_error(self):
        """Test ConnectionError."""
        error = ConnectionError("connection failed")
        assert isinstance(error, ProviderError)
        assert str(error) == "connection failed"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("auth failed")
        assert isinstance(error, ProviderError)

    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError("timed out")
        assert isinstance(error, ProviderError)

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("rate limited", retry_after_seconds=60.0)
        assert isinstance(error, ProviderError)
        assert error.retry_after_seconds == 60.0

    def test_data_format_error(self):
        """Test DataFormatError."""
        error = DataFormatError("invalid format")
        assert isinstance(error, ProviderError)

    def test_provider_not_initialized_error(self):
        """Test ProviderNotInitializedError."""
        error = ProviderNotInitializedError("not initialized")
        assert isinstance(error, ProviderError)

    def test_provider_disposed_error(self):
        """Test ProviderDisposedError."""
        error = ProviderDisposedError("disposed")
        assert isinstance(error, ProviderError)

    def test_provider_paused_error(self):
        """Test ProviderPausedError."""
        error = ProviderPausedError("paused")
        assert isinstance(error, ProviderError)


class TestExtractionErrors:
    """Test Extraction error hierarchy."""

    def test_extraction_error_is_observation_error(self):
        """Test ExtractionError inherits from ObservationError."""
        error = ExtractionError("test")
        assert isinstance(error, ObservationError)

    def test_provider_not_ready_error(self):
        """Test ProviderNotReadyError."""
        error = ProviderNotReadyError("not ready")
        assert isinstance(error, ExtractionError)

    def test_incompatible_provider_error(self):
        """Test IncompatibleProviderError."""
        error = IncompatibleProviderError("incompatible")
        assert isinstance(error, ExtractionError)

    def test_partial_extraction_error(self):
        """Test PartialExtractionError."""
        error = PartialExtractionError(
            "partial failure",
            partial_results=[1, 2, 3],
        )
        assert isinstance(error, ExtractionError)
        assert error.partial_results == [1, 2, 3]

    def test_extraction_timeout_error(self):
        """Test ExtractionTimeoutError."""
        error = ExtractionTimeoutError("extraction timed out")
        assert isinstance(error, ExtractionError)

    def test_provider_extraction_error(self):
        """Test ProviderExtractionError."""
        provider_error = ConnectionError("connection failed")
        error = ProviderExtractionError(
            "extraction failed",
            provider_error=provider_error,
        )
        assert isinstance(error, ExtractionError)
        assert error.provider_error is provider_error


class TestValidationErrors:
    """Test Validation error hierarchy."""

    def test_validation_error_is_observation_error(self):
        """Test ValidationError inherits from ObservationError."""
        error = ValidationError("test")
        assert isinstance(error, ObservationError)

    def test_validation_error_with_violations(self):
        """Test ValidationError with violations."""
        error = ValidationError(
            "validation failed",
            violations=["violation 1", "violation 2"],
        )
        assert error.violations == ["violation 1", "violation 2"]

    def test_schema_violation_error(self):
        """Test SchemaViolationError."""
        error = SchemaViolationError("schema violated")
        assert isinstance(error, ValidationError)

    def test_range_violation_error(self):
        """Test RangeViolationError."""
        error = RangeViolationError(
            "value out of range",
            metric_id="M-01",
            value=1.5,
            min_value=0.0,
            max_value=1.0,
        )
        assert isinstance(error, ValidationError)
        assert error.metric_id == "M-01"
        assert error.value == 1.5
        assert error.min_value == 0.0
        assert error.max_value == 1.0

    def test_freshness_violation_error(self):
        """Test FreshnessViolationError."""
        error = FreshnessViolationError(
            "observation too old",
            observation_time="2026-01-01T00:00:00Z",
            max_age_hours=24.0,
        )
        assert isinstance(error, ValidationError)
        assert error.observation_time == "2026-01-01T00:00:00Z"
        assert error.max_age_hours == 24.0

    def test_dependency_violation_error(self):
        """Test DependencyViolationError."""
        error = DependencyViolationError(
            "missing dependencies",
            missing_dependencies=["M-01", "M-02"],
        )
        assert isinstance(error, ValidationError)
        assert error.missing_dependencies == ["M-01", "M-02"]


class TestRegistryErrors:
    """Test Registry error hierarchy."""

    def test_registry_error_is_observation_error(self):
        """Test RegistryError inherits from ObservationError."""
        error = RegistryError("test")
        assert isinstance(error, ObservationError)

    def test_registration_error(self):
        """Test RegistrationError."""
        error = RegistrationError("registration failed")
        assert isinstance(error, RegistryError)

    def test_discovery_error(self):
        """Test DiscoveryError."""
        error = DiscoveryError("discovery failed")
        assert isinstance(error, RegistryError)

    def test_provider_not_found_error(self):
        """Test ProviderNotFoundError."""
        error = ProviderNotFoundError(
            "provider not found",
            provider_id="test-provider",
            metric_id="M-01",
        )
        assert isinstance(error, RegistryError)
        assert error.provider_id == "test-provider"
        assert error.metric_id == "M-01"

    def test_duplicate_provider_error(self):
        """Test DuplicateProviderError."""
        error = DuplicateProviderError("duplicate provider")
        assert isinstance(error, RegistryError)

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("invalid config")
        assert isinstance(error, RegistryError)


class TestPipelineErrors:
    """Test Pipeline error hierarchy."""

    def test_pipeline_error_is_observation_error(self):
        """Test PipelineError inherits from ObservationError."""
        error = PipelineError("test")
        assert isinstance(error, ObservationError)

    def test_pipeline_stage_error(self):
        """Test PipelineStageError."""
        error = PipelineStageError(
            "stage failed",
            stage="extraction",
        )
        assert isinstance(error, PipelineError)
        assert error.stage == "extraction"

    def test_pipeline_timeout_error(self):
        """Test PipelineTimeoutError."""
        error = PipelineTimeoutError("pipeline timed out")
        assert isinstance(error, PipelineError)

    def test_pipeline_consolidation_error(self):
        """Test PipelineConsolidationError."""
        error = PipelineConsolidationError(
            "consolidation failed",
            failed_providers=["provider-1", "provider-2"],
            successful_providers=["provider-3"],
        )
        assert isinstance(error, PipelineError)
        assert error.failed_providers == ["provider-1", "provider-2"]
        assert error.successful_providers == ["provider-3"]


class TestErrorFactory:
    """Test error factory functions."""

    def test_create_provider_error(self):
        """Test create_provider_error factory."""
        error = create_provider_error(
            "ConnectionError",
            "connection failed",
        )
        assert isinstance(error, ConnectionError)
        assert str(error) == "connection failed"

    def test_create_provider_error_with_context(self):
        """Test create_provider_error with context."""
        ctx = ProviderErrorContext(
            provider_id="test-provider",
            metric_id="M-01",
            extraction_phase=ExtractionPhase.EXTRACT,
            repository_id="repo-123",
            analysis_id="analysis-456",
        )
        error = create_provider_error(
            "TimeoutError",
            "timed out",
            context=ctx,
        )
        assert isinstance(error, TimeoutError)
        assert error.context is ctx

    def test_create_provider_error_unknown_type(self):
        """Test create_provider_error with unknown type."""
        with pytest.raises(ValueError, match="Unknown provider error type"):
            create_provider_error("UnknownError", "error")

    def test_create_extraction_error(self):
        """Test create_extraction_error factory."""
        error = create_extraction_error(
            "PartialExtractionError",
            "partial failure",
            partial_results=[1, 2],
        )
        assert isinstance(error, PartialExtractionError)
        assert error.partial_results == [1, 2]

    def test_create_extraction_error_unknown_type(self):
        """Test create_extraction_error with unknown type."""
        with pytest.raises(ValueError, match="Unknown extraction error type"):
            create_extraction_error("UnknownError", "error")
