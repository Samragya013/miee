"""
MIIE v1.5 Sampling Framework — Adaptive Window Builder.

Builds observation windows according to a SamplingPlan. The builder does NOT
choose strategies — it executes exactly the plan provided by the SamplingPlanner.

Reference: PR-7B Phase 3, OEAS SS21
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

from miie.processing.observation.models import (
    ObservationCollection,
    ObservationWindow,
    WindowBuilderResult,
    WindowConfig,
)
from miie.processing.observation.window_builder import ObservationWindowBuilder

from .models import SamplingPlan, WindowDiagnostics

logger = logging.getLogger(__name__)

# Terminal window merge thresholds (PR-7C-2)
_MIN_OBS_PER_MERGE = 10


class AdaptiveWindowBuilder:
    """Builds observation windows according to a SamplingPlan.

    Responsibilities:
    - Execute exactly the SamplingPlan (no strategy selection)
    - Construct windows using ObservationWindowBuilder
    - Validate window output
    - Compute per-window diagnostics
    - Preserve observation provenance
    - Merge undersized terminal windows deterministically (PR-7C-2)

    Does NOT:
    - Choose strategies (that is the planner's job)
    - Fabricate observations
    - Merge observations artificially
    - Duplicate observations
    """

    def __init__(self) -> None:
        self._builder = ObservationWindowBuilder()

    def build(
        self,
        collection: ObservationCollection,
        plan: SamplingPlan,
    ) -> Tuple[WindowBuilderResult, List[WindowDiagnostics]]:
        """Build windows according to the sampling plan.

        Args:
            collection: ObservationCollection containing all observations.
            plan: SamplingPlan specifying the strategy and parameters.

        Returns:
            Tuple of (WindowBuilderResult, per-window diagnostics).
        """
        chosen = plan.chosen

        # Create WindowConfig from the plan
        config = WindowConfig(
            strategy=chosen.strategy,
            window_size=chosen.window_size,
            min_observations=2,
        )

        # Build windows using the existing builder
        result = self._builder.build(collection, config)

        # Merge undersized terminal windows (PR-7C-2)
        result = self._merge_terminal_windows(result)

        # Compute per-window diagnostics
        diagnostics = self._compute_window_diagnostics(result)

        return result, diagnostics

    def _merge_terminal_windows(
        self,
        result: WindowBuilderResult,
    ) -> WindowBuilderResult:
        """Merge undersized terminal windows with their predecessor (PR-7C-2).

        Deterministic merge policy:
        - Only merges the terminal (last) window if its observation count < 10
        - Merges into the previous window if chronological order/validity preserved
        - Records every merge decision as a warning
        - No randomness, no observation loss

        Args:
            result: WindowBuilderResult from the base builder.

        Returns:
            WindowBuilderResult with terminal window merged if applicable.
        """
        windows = list(result.windows)
        if len(windows) < 2:
            return result

        last_window = windows[-1]
        if last_window.observation_count >= _MIN_OBS_PER_MERGE:
            return result

        # Undersized terminal window — merge with previous
        prev_window = windows[-2]

        # Merge observations (chronological order preserved)
        merged_observations = list(prev_window.observations) + list(last_window.observations)
        merged_observations.sort(key=lambda o: o.timestamp)

        # Compute new start/end boundaries
        merged_start = prev_window.start_boundary
        merged_end = last_window.end_boundary

        # Compute merged statistics
        from miie.processing.observation.window_builder import ObservationWindowBuilder

        temp_builder = ObservationWindowBuilder()
        merged_stats = temp_builder._compute_statistics(merged_observations)
        merged_metrics = sorted({obs.metric_id for obs in merged_observations})

        # Create merged window
        merged_window = ObservationWindow(
            window_id=prev_window.window_id,
            window_index=prev_window.window_index,
            strategy=prev_window.strategy,
            start_boundary=merged_start,
            end_boundary=merged_end,
            observations=merged_observations,
            start_commit=prev_window.start_commit,
            end_commit=last_window.end_commit,
            metrics_present=merged_metrics,
            statistics=merged_stats,
        )

        # Replace previous window with merged, drop last
        windows[-2] = merged_window
        windows = windows[:-1]

        # Renumber windows sequentially
        from miie.processing.observation.window_builder import ObservationWindowBuilder

        builder = ObservationWindowBuilder()
        windows = builder._renumber_windows(windows)

        # Record merge as warning
        warnings = list(result.warnings)
        warnings.append(
            f"Terminal window merge: {last_window.window_id} "
            f"({last_window.observation_count} obs) merged into "
            f"{prev_window.window_id} ({prev_window.observation_count} obs) "
            f"combined {len(merged_observations)} obs"
        )

        logger.info(
            "Terminal window merge: %s (%d obs) -> %s",
            last_window.window_id,
            last_window.observation_count,
            prev_window.window_id,
        )

        return WindowBuilderResult(
            windows=windows,
            unassigned_observations=result.unassigned_observations,
            warnings=warnings,
        )

    def _compute_window_diagnostics(
        self,
        result: WindowBuilderResult,
    ) -> List[WindowDiagnostics]:
        """Compute diagnostics for each window.

        Checks each window against detector minimum thresholds:
        - D-01: 10 observations per window
        - D-02: 10 paired observations per window
        - D-03: 20 observations per window
        """
        diagnostics: List[WindowDiagnostics] = []

        for window in result.windows:
            obs_count = window.observation_count

            # Compute statistics
            if window.observations:
                values = [obs.value for obs in window.observations]
                mean_val = sum(values) / len(values)
                variance = sum((v - mean_val) ** 2 for v in values) / max(len(values) - 1, 1)
                std_val = variance**0.5
            else:
                mean_val = 0.0
                std_val = 0.0

            # Metrics present
            metrics = tuple(sorted({obs.metric_id for obs in window.observations}))

            # For D-02, we need paired observations (same source_id across metrics)
            paired_count = self._count_paired_observations(window)

            diagnostics.append(
                WindowDiagnostics(
                    window_id=window.window_id,
                    observation_count=obs_count,
                    metrics_present=metrics,
                    meets_d01_threshold=obs_count >= 10,
                    meets_d02_threshold=paired_count >= 10,
                    meets_d03_threshold=obs_count >= 20,
                    mean_value=round(mean_val, 4),
                    std_value=round(std_val, 4),
                )
            )

        return diagnostics

    def _count_paired_observations(self, window: ObservationWindow) -> int:
        """Count observations that have pairs across metrics (for D-02).

        A 'paired' observation is one where the same source_id appears
        in at least 2 different metrics within this window.
        """
        from collections import defaultdict

        source_metrics: Dict[str, set] = defaultdict(set)
        for obs in window.observations:
            source_metrics[obs.source_id].add(obs.metric_id)

        # Count sources that appear in 2+ metrics
        paired = sum(1 for metrics in source_metrics.values() if len(metrics) >= 2)
        return paired
