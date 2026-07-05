"""
MIIE v1.6 Scientific Metric Completion Framework — Contracts.

Defines the abstract base classes and protocol interfaces for metric
computation, validation, and diagnostics.

Reference: PR-12 specification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from miie.metrics.models import (
    MetricDefinition,
    MetricResult,
    ObservationInput,
    ValidationResult,
)

# ---------------------------------------------------------------------------
# MetricComputer — Abstract Base
# ---------------------------------------------------------------------------


class MetricComputer(ABC):
    """Abstract base class for metric-specific computation logic.

    Each metric (M-01 through M-07) implements this interface to provide
    deterministic, validated computation from observations.
    """

    @property
    @abstractmethod
    def metric_definition(self) -> MetricDefinition:
        """Return the metric definition this computer handles."""

    @abstractmethod
    def compute(
        self,
        observations: List[ObservationInput],
    ) -> MetricResult:
        """Compute the metric value from observations.

        Args:
            observations: Validated observations for this metric.

        Returns:
            MetricResult with computed value, confidence, and metadata.

        Raises:
            ValueError: If observations list is empty.
        """

    @abstractmethod
    def validate_observations(
        self,
        observations: List[ObservationInput],
    ) -> ValidationResult:
        """Validate that observations are suitable for this metric.

        Args:
            observations: Observations to validate.

        Returns:
            ValidationResult with is_valid, errors, and warnings.
        """

    def minimum_observations(self) -> int:
        """Minimum observations needed for valid computation."""
        return self.metric_definition.required_observations

    def expected_unit(self) -> str:
        """Expected unit for this metric's observations."""
        return self.metric_definition.unit

    def valid_range(self) -> Tuple[float, float]:
        """Valid value range [min, max] for this metric."""
        return (self.metric_definition.min_value, self.metric_definition.max_value)


# ---------------------------------------------------------------------------
# Validator Protocol
# ---------------------------------------------------------------------------


class MetricValidator(ABC):
    """Protocol for metric validation logic."""

    @abstractmethod
    def validate_input_observations(
        self,
        observations: List[ObservationInput],
        metric_def: MetricDefinition,
    ) -> ValidationResult:
        """Validate input observations against metric constraints."""

    @abstractmethod
    def validate_metric_result(
        self,
        result: MetricResult,
        metric_def: MetricDefinition,
    ) -> ValidationResult:
        """Validate a computed metric result."""


# ---------------------------------------------------------------------------
# Diagnostics Protocol
# ---------------------------------------------------------------------------


class MetricDiagnosticsCollector(ABC):
    """Protocol for collecting computation diagnostics."""

    @abstractmethod
    def record_observation_count(
        self,
        metric_id: str,
        count: int,
    ) -> None:
        """Record observation count for a metric."""

    @abstractmethod
    def record_computation_time(
        self,
        metric_id: str,
        time_ms: float,
    ) -> None:
        """Record computation time for a metric."""

    @abstractmethod
    def record_validation_failure(
        self,
        message: str,
    ) -> None:
        """Record a validation failure."""

    @abstractmethod
    def record_warning(
        self,
        message: str,
    ) -> None:
        """Record a warning."""

    @abstractmethod
    def get_summary(self) -> Dict[str, object]:
        """Return a summary of all recorded diagnostics."""
