"""
MIIE v1.6 — M-06 File Change Count Computer.

Counts the number of distinct files changed across commits.
Indicates the breadth of codebase impact per analysis window.

Aggregation: sum across observations.
"""

from __future__ import annotations

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition


class M06FileChangeCountComputer(BaseMetricComputer):
    """Computer for M-06 File Change Count."""

    _DEFINITION = MetricDefinition(
        metric_id="M-06",
        name="File Change Count",
        unit="count",
        min_value=0.0,
        max_value=float("inf"),
        description="Number of distinct files changed in the analysis period",
        aggregation="sum",
        required_observations=1,
        dependencies=(),
    )

    @property
    def metric_definition(self):
        return self._DEFINITION
