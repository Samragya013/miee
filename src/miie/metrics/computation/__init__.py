"""
MIIE v1.6 Scientific Metric Completion Framework — Computation Module.

Provides metric-specific computers for M-01 through M-07.
"""

from __future__ import annotations

from typing import List

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.computation.m01_entropy_ratio import M01EntropyRatioComputer
from miie.metrics.computation.m02_commit_count import M02CommitCountComputer
from miie.metrics.computation.m03_churn_ratio import M03ChurnRatioComputer
from miie.metrics.computation.m04_test_coverage import M04TestCoverageComputer
from miie.metrics.computation.m05_review_latency import M05ReviewLatencyComputer
from miie.metrics.computation.m06_file_change_count import (
    M06FileChangeCountComputer,
)
from miie.metrics.computation.m07_branch_freshness import (
    M07BranchFreshnessComputer,
)


def create_all_computers() -> List[BaseMetricComputer]:
    """Create instances of all metric computers.

    Returns:
        List of all 7 metric computer instances.
    """
    return [
        M01EntropyRatioComputer(),
        M02CommitCountComputer(),
        M03ChurnRatioComputer(),
        M04TestCoverageComputer(),
        M05ReviewLatencyComputer(),
        M06FileChangeCountComputer(),
        M07BranchFreshnessComputer(),
    ]


__all__ = [
    "BaseMetricComputer",
    "M01EntropyRatioComputer",
    "M02CommitCountComputer",
    "M03ChurnRatioComputer",
    "M04TestCoverageComputer",
    "M05ReviewLatencyComputer",
    "M06FileChangeCountComputer",
    "M07BranchFreshnessComputer",
    "create_all_computers",
]
