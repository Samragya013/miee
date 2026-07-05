"""
MIIE v1.6 — M-04 Test Coverage Ratio Computer.

Measures the proportion of code covered by automated tests.
Critical for assessing code quality and maintainability.

Aggregation: mean across observations.
"""

from __future__ import annotations

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition


class M04TestCoverageComputer(BaseMetricComputer):
    """Computer for M-04 Test Coverage Ratio."""

    _DEFINITION = MetricDefinition(
        metric_id="M-04",
        name="Test Coverage Ratio",
        unit="ratio",
        min_value=0.0,
        max_value=1.0,
        description="Proportion of code covered by automated tests",
        aggregation="mean",
        required_observations=1,
        dependencies=(),
    )

    @property
    def metric_definition(self):
        return self._DEFINITION
