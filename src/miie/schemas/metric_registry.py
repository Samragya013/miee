"""
Metric Registry for MIIE v1.0.
Defines the frozen set of metrics with their metadata.
"""

from typing import Dict, List, Optional, FrozenSet
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetricInfo:
    """
    Information about a MIIE v1.0 metric.
    """
    metric_id: str
    name: str
    description: str
    extraction_status: str  # "implemented", "unavailable", "deferred"
    data_source: Optional[str] = None  # e.g., "Git history", "Coverage artifacts", etc.
    unit: Optional[str] = None  # e.g., "commits", "lines", "percentage", etc.


# Frozen metric registry - contains all MIIE v1.0 metrics with metadata
METRIC_REGISTRY: FrozenSet[MetricInfo] = frozenset([
    MetricInfo(
        metric_id="M-01",
        name="Code Coverage",
        description="Percentage of code covered by automated tests",
        extraction_status="unavailable",
        data_source="Coverage artifacts (cobertura.xml, jacoco.xml, lcov.info)",
        unit="percentage"
    ),
    MetricInfo(
        metric_id="M-02",
        name="Commit Frequency",
        description="Number of commits per time period",
        extraction_status="implemented",
        data_source="Git history",
        unit="commits"
    ),
    MetricInfo(
        metric_id="M-03",
        name="Review Participation",
        description="Number of developers participating in code reviews",
        extraction_status="unavailable",
        data_source="Pull request/comment systems",
        unit="count"
    ),
    MetricInfo(
        metric_id="M-04",
        name="Review Latency",
        description="Average time to complete code reviews",
        extraction_status="unavailable",
        data_source="Pull request/merge request timestamps",
        unit="time (hours)"
    ),
    MetricInfo(
        metric_id="M-05",
        name="Issue Resolution Time",
        description="Average time to resolve issues",
        extraction_status="unavailable",
        data_source="Issue tracking systems",
        unit="time (hours)"
    ),
    MetricInfo(
        metric_id="M-06",
        name="Code Churn",
        description="Lines of code added and deleted",
        extraction_status="implemented",
        data_source="Git history",
        unit="lines"
    ),
    MetricInfo(
        metric_id="M-07",
        name="Cyclomatic Complexity",
        description="Measure of code complexity based on control flow",
        extraction_status="unavailable",
        data_source="Static analysis tools",
        unit="score"
    )
])


def get_metric_info(metric_id: str) -> Optional[MetricInfo]:
    """
    Get metric information by metric ID.

    Args:
        metric_id: The metric ID to look up (e.g., "M-02")

    Returns:
        MetricInfo if found, None otherwise
    """
    for metric in METRIC_REGISTRY:
        if metric.metric_id == metric_id:
            return metric
    return None


def validate_metric_ids(metric_list: List[str]) -> List[str]:
    """
    Validate that all metric IDs are in the frozen registry.

    Args:
        metric_list: List of metric IDs to validate

    Returns:
        List of invalid metric IDs (empty if all valid)

    Raises:
        ValueError: If any metric ID is not in the frozen registry
    """
    valid_metric_ids = {metric.metric_id for metric in METRIC_REGISTRY}
    invalid_metrics = [m for m in metric_list if m not in valid_metric_ids]

    if invalid_metrics:
        raise ValueError(
            f"Invalid metric IDs: {invalid_metrics}. "
            f"Must be from frozen registry: {sorted(valid_metric_ids)}"
        )

    return invalid_metrics


def get_implemented_metrics() -> List[MetricInfo]:
    """
    Get list of metrics that have been implemented.

    Returns:
        List of MetricInfo objects for implemented metrics
    """
    return [metric for metric in METRIC_REGISTRY if metric.extraction_status == "implemented"]


def get_unavailable_metrics() -> List[MetricInfo]:
    """
    Get list of metrics that are currently unavailable.

    Returns:
        List of MetricInfo objects for unavailable metrics
    """
    return [metric for metric in METRIC_REGISTRY if metric.extraction_status == "unavailable"]