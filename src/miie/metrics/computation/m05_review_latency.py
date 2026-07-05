"""
MIIE v1.6 — M-05 Review Latency Computer.

Measures the time between PR creation and first review action.
Lower latency indicates responsive review culture.

Aggregation: mean across observations.
"""

from __future__ import annotations

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition


class M05ReviewLatencyComputer(BaseMetricComputer):
    """Computer for M-05 Review Latency."""

    _DEFINITION = MetricDefinition(
        metric_id="M-05",
        name="Review Latency",
        unit="hours",
        min_value=0.0,
        max_value=float("inf"),
        description="Hours between PR creation and first review",
        aggregation="mean",
        required_observations=2,
        dependencies=(),
    )

    @property
    def metric_definition(self):
        return self._DEFINITION
