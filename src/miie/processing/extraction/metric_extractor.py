"""
MetricExtractor — adapter from ObservationCollection to MetricDataFrame.

Translates observation-centric data back to the legacy MetricDataFrame
format so downstream detectors and scoring engines continue to work
without modification.

Implements IMS Phase 3: MetricExtractor.

Reference: IMS-v1.0 Phase 3, ODSS-v1.0 §7
"""

from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from miie.processing.observation.models import (
    ObservationCollection,
    ObservationWindow,
)
from miie.schemas.models import MetricDataFrame

# Aggregation strategies per metric (ODSS §9.2.6)
# M-02 (Commit Frequency) and M-06 (Code Churn) are count/sum metrics.
# All other metrics are ratio/mean metrics.
_SUM_METRICS: frozenset[str] = frozenset({"M-02", "M-06"})
_MEAN_METRICS: frozenset[str] = frozenset({"M-01", "M-03", "M-04", "M-05", "M-07"})


class MetricExtractor:
    """Adapter from ObservationCollection to MetricDataFrame.

    Converts observation-centric data into the legacy dict-of-dicts format
    expected by existing detectors, scoring engines, and evidence generators.

    Aggregation per metric:
      - M-02 (Commit Frequency): sum of observation values (total count)
      - M-06 (Code Churn): sum of observation values (total churn)
      - M-01, M-03–M-05, M-07: mean of observation values

    This adapter is transitional — it will be removed once detectors
    natively consume ObservationWindow objects.
    """

    def extract_metrics(
        self,
        observation_collection: ObservationCollection,
        metric_list: Optional[List[str]] = None,
    ) -> MetricDataFrame:
        """Convert ObservationCollection to MetricDataFrame.

        Args:
            observation_collection: Source observation collection.
            metric_list: Subset of metric IDs to include. None means
                all metrics present in the collection.

        Returns:
            MetricDataFrame with aggregated values per window.
        """
        windows = observation_collection.windows
        repo_id = observation_collection.repository_id
        run_id = observation_collection.analysis_id
        timestamp_str = observation_collection.extraction_timestamp

        # Parse extraction timestamp
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            timestamp = datetime.datetime.now(datetime.timezone.utc)

        # Determine which metrics to include
        available_metrics = self._collect_available_metrics(windows)
        if metric_list is not None:
            # Use all requested metrics (including those not yet in collection)
            requested = set(metric_list)
        else:
            requested = available_metrics

        # Build metrics dict: metric_id → {window_id → [aggregated_value]}
        metrics: Dict[str, Dict[str, List[float]]] = {}

        for metric_id in sorted(requested):
            window_values: Dict[str, List[float]] = {}
            for window in windows:
                values = self._extract_values_for_metric(window, metric_id)
                if values:
                    aggregated = self._aggregate(metric_id, values)
                    window_values[window.window_id] = [aggregated]
                else:
                    window_values[window.window_id] = [0.0]
            metrics[metric_id] = window_values

        # Also include requested metrics not found anywhere as all-zeros
        for metric_id in sorted(requested):
            if metric_id not in metrics:
                metrics[metric_id] = {w.window_id: [0.0] for w in windows}

        return MetricDataFrame(
            repo_id=repo_id,
            run_id=run_id,
            timestamp=timestamp,
            metrics=metrics,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _collect_available_metrics(self, windows: List[ObservationWindow]) -> set:
        """Collect all metric IDs present across all windows."""
        metrics: set = set()
        for window in windows:
            for obs in window.observations:
                metrics.add(obs.metric_id)
        return metrics

    def _extract_values_for_metric(
        self,
        window: ObservationWindow,
        metric_id: str,
    ) -> List[float]:
        """Extract numeric values for a metric from a window."""
        return [obs.value for obs in window.observations if obs.metric_id == metric_id]

    def _aggregate(self, metric_id: str, values: List[float]) -> float:
        """Aggregate observation values for a metric.

        Args:
            metric_id: Metric identifier (M-01 .. M-07).
            values: Non-empty list of numeric observation values.

        Returns:
            Aggregated value (sum for count metrics, mean for others).
        """
        if not values:
            return 0.0

        if metric_id in _SUM_METRICS:
            return sum(values)

        # Mean for ratio/mean metrics
        return sum(values) / len(values)
