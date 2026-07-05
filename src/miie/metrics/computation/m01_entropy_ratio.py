"""
MIIE v1.6 — M-01 Commit Entropy Ratio Computer.

Computes the entropy of commit message distribution as a ratio [0, 1].
Higher entropy indicates more diverse commit types (feature, fix, refactor, etc.).
Lower entropy indicates homogeneous commit patterns.

Aggregation: mean across observations.
"""

from __future__ import annotations

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition


class M01EntropyRatioComputer(BaseMetricComputer):
    """Computer for M-01 Commit Entropy Ratio."""

    _DEFINITION = MetricDefinition(
        metric_id="M-01",
        name="Commit Entropy Ratio",
        unit="ratio",
        min_value=0.0,
        max_value=1.0,
        description="Normalized Shannon entropy of commit message patterns",
        aggregation="mean",
        required_observations=1,
        dependencies=(),
    )

    @property
    def metric_definition(self):
        return self._DEFINITION
