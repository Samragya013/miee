"""
MIIE v1.6 — M-03 Code Churn Ratio Computer.

Measures the ratio of code changed (additions + deletions) relative
to total codebase size. High churn indicates instability.

Aggregation: mean across observations.
Dependencies: M-07 (branch freshness) for context validation.
"""

from __future__ import annotations

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition


class M03ChurnRatioComputer(BaseMetricComputer):
    """Computer for M-03 Code Churn Ratio."""

    _DEFINITION = MetricDefinition(
        metric_id="M-03",
        name="Code Churn Ratio",
        unit="ratio",
        min_value=0.0,
        max_value=1.0,
        description="Ratio of changed lines to total codebase size",
        aggregation="mean",
        required_observations=5,
        dependencies=("M-07",),
    )

    @property
    def metric_definition(self):
        return self._DEFINITION
