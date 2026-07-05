"""
MIIE v1.6 — M-07 Branch Freshness Ratio Computer.

Measures how recently the branch was updated relative to a reference
point (e.g., main branch tip). Freshness = 1.0 means current.

Aggregation: mean across observations.
"""

from __future__ import annotations

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition


class M07BranchFreshnessComputer(BaseMetricComputer):
    """Computer for M-07 Branch Freshness Ratio."""

    _DEFINITION = MetricDefinition(
        metric_id="M-07",
        name="Branch Freshness Ratio",
        unit="ratio",
        min_value=0.0,
        max_value=1.0,
        description="How recently the branch was updated (1.0 = current)",
        aggregation="mean",
        required_observations=1,
        dependencies=(),
    )

    @property
    def metric_definition(self):
        return self._DEFINITION
