"""
MIIE v1.6 Observation Errors — Error hierarchy for Observation Provider Architecture.

Implements OPC-v1.0 §4 and OPA-v1.0 §17 error definitions.
All observation provider errors inherit from these base classes.

Reference: OPC-v1.0, OPA-v1.0
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from miie.contracts.observation_types import ExtractionPhase, ProviderErrorContext

# ---------------------------------------------------------------------------
# Base Error Classes
# ---------------------------------------------------------------------------


class ObservationError(Exception):
    """Base class for all observation-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[ProviderErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize observation error.

        Args:
            message: Human-readable error message.
            error_code: Machine-readable error code.
            context: Error context for debugging.
            cause: Original exception that caused this error.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        result: Dict[str, Any] = {
            "error_type": type(self).__name__,
            "message": self.message,
        }
        if self.error_code:
            result["error_code"] = self.error_code
        if self.context:
            result["context"] = {
                "provider_id": self.context.provider_id,
                "metric_id": self.context.metric_id,
                "extraction_phase": self.context.extraction_phase.value,
                "repository_id": self.context.repository_id,
                "analysis_id": self.context.analysis_id,
                "timestamp": self.context.timestamp.isoformat(),
            }
        if self.cause:
            result["cause"] = str(self.cause)
        return result


# ---------------------------------------------------------------------------
# Provider Errors (OPA §17.1)
# ---------------------------------------------------------------------------


class ProviderError(ObservationError):
    """OPA §17.1 — Base class for provider errors.

    Raised when a provider encounters an error during any operation.
    """

    pass


class ConnectionError(ProviderError):
    """OPA §17.1 — Provider cannot connect to data source."""

    pass


class AuthenticationError(ProviderError):
    """OPA §17.1 — Provider authentication failed."""

    pass


class TimeoutError(ProviderError):
    """OPA §17.1 — Provider operation timed out."""

    pass


class RateLimitError(ProviderError):
    """OPA §17.1 — Provider rate limit exceeded."""

    def __init__(
        self,
        message: str,
        retry_after_seconds: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Human-readable error message.
            retry_after_seconds: Seconds to wait before retrying.
            **kwargs: Additional arguments for ProviderError.
        """
        super().__init__(message, **kwargs)
        self.retry_after_seconds = retry_after_seconds


class DataFormatError(ProviderError):
    """OPA §17.1 — Provider returned unexpected data format."""

    pass


class ProviderNotInitializedError(ProviderError):
    """OPA §17.1 — Provider has not been initialized."""

    pass


class ProviderDisposedError(ProviderError):
    """OPA §17.1 — Provider has been disposed."""

    pass


class ProviderPausedError(ProviderError):
    """OPA §17.1 — Provider is paused."""

    pass


# ---------------------------------------------------------------------------
# Extraction Errors (OPA §17.1)
# ---------------------------------------------------------------------------


class ExtractionError(ObservationError):
    """OPA §17.1 — Base class for extraction errors.

    Raised when extraction fails for any reason.
    """

    pass


class ProviderNotReadyError(ExtractionError):
    """OPA §17.1 — Provider is not in READY state."""

    pass


class IncompatibleProviderError(ExtractionError):
    """OPA §17.1 — Provider cannot handle the requested metric."""

    pass


class PartialExtractionError(ExtractionError):
    """OPA §17.1 — Extraction partially failed.

    Contains partial results that can still be used.
    """

    def __init__(
        self,
        message: str,
        partial_results: Optional[List[Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize partial extraction error.

        Args:
            message: Human-readable error message.
            partial_results: Partial results that were successfully extracted.
            **kwargs: Additional arguments for ExtractionError.
        """
        super().__init__(message, **kwargs)
        self.partial_results = partial_results or []


class ExtractionTimeoutError(ExtractionError):
    """OPA §17.1 — Extraction operation timed out."""

    pass


class ProviderExtractionError(ExtractionError):
    """OPA §17.1 — Extraction failed due to provider error.

    Wraps a ProviderError for extraction context.
    """

    def __init__(
        self,
        message: str,
        provider_error: Optional[ProviderError] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize provider extraction error.

        Args:
            message: Human-readable error message.
            provider_error: Original provider error.
            **kwargs: Additional arguments for ExtractionError.
        """
        super().__init__(message, **kwargs)
        self.provider_error = provider_error


# ---------------------------------------------------------------------------
# Validation Errors (OPC §4.3)
# ---------------------------------------------------------------------------


class ValidationError(ObservationError):
    """OPC §4.3 — Base class for validation errors.

    Raised when observation validation fails.
    """

    def __init__(
        self,
        message: str,
        violations: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Human-readable error message.
            violations: List of validation violations.
            **kwargs: Additional arguments for ObservationError.
        """
        super().__init__(message, **kwargs)
        self.violations = violations or []


class SchemaViolationError(ValidationError):
    """OPC §4.3 — Observation violates ODSS schema."""

    pass


class RangeViolationError(ValidationError):
    """OPC §4.3 — Observation value is out of valid range."""

    def __init__(
        self,
        message: str,
        metric_id: str,
        value: float,
        min_value: float,
        max_value: float,
        **kwargs: Any,
    ) -> None:
        """Initialize range violation error.

        Args:
            message: Human-readable error message.
            metric_id: Metric identifier.
            value: Observed value.
            min_value: Minimum valid value.
            max_value: Maximum valid value.
            **kwargs: Additional arguments for ValidationError.
        """
        super().__init__(message, **kwargs)
        self.metric_id = metric_id
        self.value = value
        self.min_value = min_value
        self.max_value = max_value


class FreshnessViolationError(ValidationError):
    """OPC §4.3 — Observation is too old or too new."""

    def __init__(
        self,
        message: str,
        observation_time: Optional[str] = None,
        max_age_hours: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize freshness violation error.

        Args:
            message: Human-readable error message.
            observation_time: ISO timestamp of observation.
            max_age_hours: Maximum allowed age in hours.
            **kwargs: Additional arguments for ValidationError.
        """
        super().__init__(message, **kwargs)
        self.observation_time = observation_time
        self.max_age_hours = max_age_hours


class DependencyViolationError(ValidationError):
    """OPC §4.3 — Observation depends on missing data."""

    def __init__(
        self,
        message: str,
        missing_dependencies: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize dependency violation error.

        Args:
            message: Human-readable error message.
            missing_dependencies: List of missing dependency IDs.
            **kwargs: Additional arguments for ValidationError.
        """
        super().__init__(message, **kwargs)
        self.missing_dependencies = missing_dependencies or []


# ---------------------------------------------------------------------------
# Registry Errors (OPR §10)
# ---------------------------------------------------------------------------


class RegistryError(ObservationError):
    """OPR §10 — Base class for registry errors.

    Raised when provider registration or discovery fails.
    """

    pass


class RegistrationError(RegistryError):
    """OPR §10 — Provider registration failed."""

    pass


class DiscoveryError(RegistryError):
    """OPR §10 — Provider discovery failed."""

    pass


class ProviderNotFoundError(RegistryError):
    """OPR §10 — Requested provider not found."""

    def __init__(
        self,
        message: str,
        provider_id: Optional[str] = None,
        metric_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize provider not found error.

        Args:
            message: Human-readable error message.
            provider_id: Provider identifier that was not found.
            metric_id: Metric identifier with no providers.
            **kwargs: Additional arguments for RegistryError.
        """
        super().__init__(message, **kwargs)
        self.provider_id = provider_id
        self.metric_id = metric_id


class DuplicateProviderError(RegistryError):
    """OPR §10 — Provider with same ID already registered."""

    pass


class ConfigurationError(RegistryError):
    """OPR §10 — Provider configuration is invalid."""

    pass


# ---------------------------------------------------------------------------
# Pipeline Errors (OBSERVATION_LIFECYCLE §7)
# ---------------------------------------------------------------------------


class PipelineError(ObservationError):
    """OBSERVATION_LIFECYCLE §7 — Base class for pipeline errors.

    Raised when the observation pipeline encounters an error.
    """

    pass


class PipelineStageError(PipelineError):
    """OBSERVATION_LIFECYCLE §7 — Error in a specific pipeline stage."""

    def __init__(
        self,
        message: str,
        stage: str,
        **kwargs: Any,
    ) -> None:
        """Initialize pipeline stage error.

        Args:
            message: Human-readable error message.
            stage: Pipeline stage where error occurred.
            **kwargs: Additional arguments for PipelineError.
        """
        super().__init__(message, **kwargs)
        self.stage = stage


class PipelineTimeoutError(PipelineError):
    """OBSERVATION_LIFECYCLE §7 — Pipeline operation timed out."""

    pass


class PipelineConsolidationError(PipelineError):
    """OBSERVATION_LIFECYCLE §7 — Error consolidating results from multiple providers."""

    def __init__(
        self,
        message: str,
        failed_providers: Optional[List[str]] = None,
        successful_providers: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize consolidation error.

        Args:
            message: Human-readable error message.
            failed_providers: List of provider IDs that failed.
            successful_providers: List of provider IDs that succeeded.
            **kwargs: Additional arguments for PipelineError.
        """
        super().__init__(message, **kwargs)
        self.failed_providers = failed_providers or []
        self.successful_providers = successful_providers or []


# ---------------------------------------------------------------------------
# Error Factory Functions
# ---------------------------------------------------------------------------


def create_provider_error(
    error_type: str,
    message: str,
    context: Optional[ProviderErrorContext] = None,
    cause: Optional[Exception] = None,
    **kwargs: Any,
) -> ProviderError:
    """Create a provider error by type name.

    Args:
        error_type: Error class name (e.g., "ConnectionError").
        message: Human-readable error message.
        context: Error context for debugging.
        cause: Original exception.
        **kwargs: Additional arguments for specific error types.

    Returns:
        ProviderError instance of the specified type.

    Raises:
        ValueError: If error_type is not a valid provider error type.
    """
    error_classes = {
        "ConnectionError": ConnectionError,
        "AuthenticationError": AuthenticationError,
        "TimeoutError": TimeoutError,
        "RateLimitError": RateLimitError,
        "DataFormatError": DataFormatError,
        "ProviderNotInitializedError": ProviderNotInitializedError,
        "ProviderDisposedError": ProviderDisposedError,
        "ProviderPausedError": ProviderPausedError,
    }

    error_class = error_classes.get(error_type)
    if error_class is None:
        raise ValueError(f"Unknown provider error type: {error_type}")

    return error_class(
        message=message,
        context=context,
        cause=cause,
        **kwargs,
    )


def create_extraction_error(
    error_type: str,
    message: str,
    context: Optional[ProviderErrorContext] = None,
    cause: Optional[Exception] = None,
    **kwargs: Any,
) -> ExtractionError:
    """Create an extraction error by type name.

    Args:
        error_type: Error class name (e.g., "PartialExtractionError").
        message: Human-readable error message.
        context: Error context for debugging.
        cause: Original exception.
        **kwargs: Additional arguments for specific error types.

    Returns:
        ExtractionError instance of the specified type.

    Raises:
        ValueError: If error_type is not a valid extraction error type.
    """
    error_classes = {
        "ProviderNotReadyError": ProviderNotReadyError,
        "IncompatibleProviderError": IncompatibleProviderError,
        "PartialExtractionError": PartialExtractionError,
        "ExtractionTimeoutError": ExtractionTimeoutError,
        "ProviderExtractionError": ProviderExtractionError,
    }

    error_class = error_classes.get(error_type)
    if error_class is None:
        raise ValueError(f"Unknown extraction error type: {error_type}")

    return error_class(
        message=message,
        context=context,
        cause=cause,
        **kwargs,
    )
