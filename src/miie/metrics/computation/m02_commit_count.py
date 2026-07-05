"""
MIIE v1.6 — M-02 Commit Count Computer.

Counts the number of commits in the analysis window.
A fundamental activity metric.

Aggregation: sum across observations.
"""

from __future__ import annotations

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition


class M02CommitCountComputer(BaseMetricComputer):
    """Computer for M-02 Commit Count."""

    _DEFINITION = MetricDefinition(
        metric_id="M-02",
        name="Commit Count",
        unit="count",
        min_value=0,
        max_value=float("inf"),
        description="Total number of commits in the analysis period",
        aggregation="sum",
        required_observations=1,
        dependencies=(),
    )

    @property
    def metric_definition(self):
        return self._DEFINITION
