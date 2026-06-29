"""
DetectorAdapter — translate ObservationWindows to legacy MetricDataFrame.

Implements IDetectorAdapter per OEAS §21.4, ODSS §27, IMS Phase 4.

Accepts ObservationWindows from the Window Builder and produces a
MetricDataFrame compatible with the existing detector pipeline.

Reference: OEAS-v1.5 §21.4, ODSS-v1.0 §27, IMS-v1.0 Phase 4
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from miie.contracts.errors import DetectorAdapterError
from miie.processing.observation.models import (
    _VALID_METRIC_IDS,
    ObservationCollection,
    ObservationWindow,
)

logger = logging.getLogger(__name__)


class DetectorAdapter:
    """OEAS §21.4 / ODSS §27 — IDetectorAdapter implementation.

    Translates ObservationWindowCollection into MetricDataFrame and
    paired observations for legacy detectors.
    """

    def to_metric_dataframe(
        self,
        windows: List[ObservationWindow],
        collection: ObservationCollection,
    ) -> Any:
        """Translate ObservationWindows into a MetricDataFrame.

        Builds a metric_id → [value_per_window] structure suitable for
        the existing detector pipeline. Each window becomes one column.

        Args:
            windows: List of ObservationWindows from the Window Builder.
            collection: ObservationCollection (unused but kept for interface).

        Returns:
            A dictionary compatible with MetricDataFrame structure.

        Raises:
            DetectorAdapterError: If windows list is empty or translation fails.
        """
        if not windows:
            raise DetectorAdapterError("No windows provided for translation")

        # Collect all metric IDs across all windows
        all_metrics: set[str] = set()
        for window in windows:
            for obs in window.observations:
                if obs.metric_id in _VALID_METRIC_IDS:
                    all_metrics.add(obs.metric_id)

        if not all_metrics:
            raise DetectorAdapterError("No valid metric IDs found in any window")

        # Build metric_id → {window_id → [values]} mapping
        metrics_by_window: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        for window in windows:
            for obs in window.observations:
                if obs.metric_id in _VALID_METRIC_IDS:
                    metrics_by_window[obs.metric_id][window.window_id].append(obs.value)

        # Build result: metric_id → [values_for_each_window_in_order]
        window_ids = [w.window_id for w in windows]
        result: Dict[str, List[float]] = {}
        for metric_id in sorted(all_metrics):
            values: List[float] = []
            for wid in window_ids:
                window_values = metrics_by_window[metric_id][wid]
                if window_values:
                    values.append(sum(window_values) / len(window_values))  # mean per window
                else:
                    values.append(0.0)
            result[metric_id] = values

        return result

    def to_paired_observations(
        self,
        window: ObservationWindow,
        metric_i: str,
        metric_j: str,
    ) -> Tuple[List[float], List[float]]:
        """Extract paired observations for correlation detectors.

        Returns observations for two metrics aligned by source_id within
        a window, suitable for D-02 correlation analysis.

        Args:
            window: A single ObservationWindow.
            metric_i: First metric identifier.
            metric_j: Second metric identifier.

        Returns:
            Tuple of (values_i, values_j) aligned by source_id.

        Raises:
            DetectorAdapterError: If either metric has no observations.
        """
        if not isinstance(window, ObservationWindow):
            raise DetectorAdapterError("window must be an ObservationWindow")
        if metric_i not in _VALID_METRIC_IDS:
            raise DetectorAdapterError(f"Invalid metric_i: {metric_i!r}")
        if metric_j not in _VALID_METRIC_IDS:
            raise DetectorAdapterError(f"Invalid metric_j: {metric_j!r}")

        # Index observations by source_id for each metric
        obs_i: Dict[str, float] = {}
        obs_j: Dict[str, float] = {}
        for obs in window.observations:
            if obs.metric_id == metric_i and obs.source_id not in obs_i:
                obs_i[obs.source_id] = obs.value
            elif obs.metric_id == metric_j and obs.source_id not in obs_j:
                obs_j[obs.source_id] = obs.value

        if not obs_i:
            raise DetectorAdapterError(f"No observations for {metric_i} in window {window.window_id}")
        if not obs_j:
            raise DetectorAdapterError(f"No observations for {metric_j} in window {window.window_id}")

        # Align by source_id (intersection)
        common_sources = sorted(set(obs_i.keys()) & set(obs_j.keys()))

        if not common_sources:
            raise DetectorAdapterError(
                f"No common source_ids between {metric_i} and {metric_j} in window {window.window_id}"
            )

        values_i = [obs_i[s] for s in common_sources]
        values_j = [obs_j[s] for s in common_sources]

        return values_i, values_j
