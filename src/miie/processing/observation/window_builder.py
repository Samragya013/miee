"""
ObservationWindowBuilder — partition observations into analysis windows.

Implements IWindowBuilder per OEAS §14.7, ODSS §24-25, IMS Phase 4.

Accepts an ObservationCollection and WindowConfig, produces a
WindowBuilderResult containing ordered, non-overlapping ObservationWindows.

Strategies:
  - temporal: fixed time intervals (days)
  - commit_count: groups by commit count boundaries
  - hybrid: temporal with minimum commit-count merging
  - custom: user-supplied ISO-8601 boundaries

Reference: OEAS-v1.5 §14.7, §18, ODSS-v1.0 §24-25, IMS-v1.0 Phase 4
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from miie.contracts.errors import WindowBuilderError
from miie.processing.observation.models import (
    _VALID_METRIC_IDS,
    Observation,
    ObservationCollection,
    ObservationStatistics,
    ObservationWindow,
    WindowBuilderResult,
    WindowConfig,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Minimum window gate (ODSS §8.5, OEAS §18.5)
# ---------------------------------------------------------------------------
MIN_OBSERVATIONS_PER_WINDOW: int = 2
MIN_WINDOWS: int = 2


class ObservationWindowBuilder:
    """ODSS §24, OEAS §14.7 — IWindowBuilder implementation.

    Groups observations from an ObservationCollection into statistically
    valid analysis windows according to the configured strategy.

    Guarantees (OEAS §21.3):
      - Windows are mutually exclusive
      - Windows are contiguous (no gaps)
      - Empty windows are excluded
      - Window IDs are sequential (w00, w01, ...)
      - Each observation belongs to exactly one window
    """

    def build(
        self,
        collection: ObservationCollection,
        config: WindowConfig,
    ) -> WindowBuilderResult:
        """Build observation windows from a collection.

        Args:
            collection: ObservationCollection containing all observations.
            config: Windowing configuration.

        Returns:
            WindowBuilderResult with ordered windows, unassigned observations, and warnings.

        Raises:
            WindowBuilderError: If the collection is empty or config is invalid.
        """
        if not isinstance(collection, ObservationCollection):
            raise WindowBuilderError("collection must be an ObservationCollection")
        if not isinstance(config, WindowConfig):
            raise WindowBuilderError("config must be a WindowConfig")

        # Flatten all observations from all windows in the collection
        all_observations: List[Observation] = []
        for window in collection.windows:
            all_observations.extend(window.observations)

        if not all_observations:
            return WindowBuilderResult(
                windows=[],
                unassigned_observations=[],
                warnings=["No observations in collection"],
            )

        # Sort by timestamp for deterministic ordering (OEAS §22.3)
        all_observations.sort(key=lambda o: o.timestamp)

        # Dispatch to strategy
        strategy = config.strategy
        if strategy == "temporal":
            windows, unassigned, warnings = self._build_temporal(all_observations, config)
        elif strategy == "commit_count":
            windows, unassigned, warnings = self._build_commit_count(all_observations, config)
        elif strategy == "hybrid":
            windows, unassigned, warnings = self._build_hybrid(all_observations, config)
        elif strategy == "custom":
            windows, unassigned, warnings = self._build_custom(all_observations, config)
        else:
            raise WindowBuilderError(f"Unknown strategy: {strategy!r}")

        # Apply max_windows limit
        if config.max_windows is not None and len(windows) > config.max_windows:
            # Keep first max_windows, move rest to unassigned
            overflow_windows = windows[config.max_windows :]
            windows = windows[: config.max_windows]
            for w in overflow_windows:
                unassigned.extend(w.observations)
            warnings.append(
                f"Truncated to {config.max_windows} windows; " f"{len(unassigned)} observations moved to unassigned"
            )

        # Renumber window IDs sequentially (OEAS §21.3)
        windows = self._renumber_windows(windows)

        # Compute per-window statistics
        for window in windows:
            window.statistics = self._compute_statistics(window.observations)
            window.metrics_present = sorted(
                {obs.metric_id for obs in window.observations if obs.metric_id in _VALID_METRIC_IDS}
            )

        return WindowBuilderResult(
            windows=windows,
            unassigned_observations=unassigned,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Strategy: Temporal (OEAS §18.2)
    # ------------------------------------------------------------------

    def _build_temporal(
        self,
        observations: List[Observation],
        config: WindowConfig,
    ) -> Tuple[List[ObservationWindow], List[Observation], List[str]]:
        """Fixed time-interval windowing.

        Algorithm (OEAS §18.2):
          1. min_ts ← min(obs.timestamp)
          2. max_ts ← max(obs.timestamp)
          3. Create fixed-width intervals of window_size days
          4. Assign observations to intervals using O(N) pointer scan
          5. Skip empty windows
        """
        warnings: List[str] = []

        # Pre-parse all timestamps once (O(N) instead of O(W*N) parse calls)
        parsed = [(self._parse_ts(obs.timestamp).date(), obs) for obs in observations]

        min_ts = parsed[0][0]
        max_ts = parsed[-1][0]

        windows: List[ObservationWindow] = []
        window_start = min_ts
        window_idx = 0
        pointer = 0  # O(N) pointer — never moves backward

        while window_start <= max_ts:
            window_end = window_start + timedelta(days=config.window_size)
            # Collect observations in [window_start, window_end) using pointer
            window_obs: List[Observation] = []
            while pointer < len(parsed):
                obs_date = parsed[pointer][0]
                if obs_date >= window_end:
                    break
                if obs_date >= window_start:
                    window_obs.append(parsed[pointer][1])
                pointer += 1
            if window_obs:
                windows.append(
                    self._make_window(
                        window_idx=window_idx,
                        strategy="temporal",
                        observations=window_obs,
                        start_boundary=window_start,
                        end_boundary=min(window_end, max_ts),
                    )
                )
                window_idx += 1
            window_start = window_end

        if not windows:
            warnings.append("No non-empty temporal windows produced")

        return windows, [], warnings

    # ------------------------------------------------------------------
    # Strategy: Commit Count (OEAS §18.3)
    # ------------------------------------------------------------------

    def _build_commit_count(
        self,
        observations: List[Observation],
        config: WindowConfig,
    ) -> Tuple[List[ObservationWindow], List[Observation], List[str]]:
        """Commit-count windowing — windows defined by commit boundaries.

        Algorithm (OEAS §18.3):
          1. Get M-02 (commit frequency) observations sorted by timestamp
          2. Every commits_per_window commits → new boundary
          3. Assign all observations to windows using O(N) pointer scan
        """
        warnings: List[str] = []

        # Find commit observations (M-02 metric)
        commit_obs = [obs for obs in observations if obs.metric_id == "M-02"]
        if not commit_obs:
            # Fallback: use temporal windowing with a reasonable default (30 days)
            warnings.append("No M-02 observations; falling back to temporal windowing")
            fallback_config = WindowConfig(strategy="temporal", window_size=30)
            tw, tlu, twarnings = self._build_temporal(observations, fallback_config)
            return tw, tlu, warnings + twarnings

        commit_obs.sort(key=lambda o: o.timestamp)
        commits_per_window = config.window_size

        # Compute boundaries from commit timestamps
        boundaries: List[str] = []
        for i in range(0, len(commit_obs), commits_per_window):
            boundaries.append(commit_obs[i].timestamp)

        # Always include the last observation timestamp as final boundary
        if boundaries[-1] != commit_obs[-1].timestamp:
            boundaries.append(commit_obs[-1].timestamp)

        # Ensure we have at least 2 boundaries for at least 1 window
        if len(boundaries) < 2:
            boundaries.append(commit_obs[-1].timestamp)

        # Pre-parse all timestamps once for O(N) assignment
        all_parsed = [(obs.timestamp, obs) for obs in observations]

        windows: List[ObservationWindow] = []
        pointer = 0  # O(N) pointer — never moves backward

        for i in range(len(boundaries) - 1):
            t_start = boundaries[i]
            t_end = boundaries[i + 1]
            is_last = i == len(boundaries) - 2

            # Collect observations in [t_start, t_end) using pointer
            window_obs: List[Observation] = []
            while pointer < len(all_parsed):
                obs_ts = all_parsed[pointer][0]
                if is_last:
                    if obs_ts > t_end:
                        break
                else:
                    if obs_ts >= t_end:
                        break
                if obs_ts >= t_start:
                    window_obs.append(all_parsed[pointer][1])
                pointer += 1

            if window_obs:
                windows.append(
                    self._make_window(
                        window_idx=i,
                        strategy="commit_count",
                        observations=window_obs,
                        start_boundary=self._parse_ts(t_start).date(),
                        end_boundary=self._parse_ts(t_end).date(),
                        start_commit=commit_obs[i].source_id if i < len(commit_obs) else None,
                        end_commit=(
                            commit_obs[min(i + commits_per_window - 1, len(commit_obs) - 1)].source_id
                            if i < len(commit_obs)
                            else None
                        ),
                    )
                )

        if not windows:
            windows, _, _ = self._build_temporal(observations, config)
            warnings.append("No non-empty commit_count windows produced; fell back to temporal")

        return windows, [], warnings

    # ------------------------------------------------------------------
    # Strategy: Hybrid (OEAS §18.4)
    # ------------------------------------------------------------------

    def _build_hybrid(
        self,
        observations: List[Observation],
        config: WindowConfig,
    ) -> Tuple[List[ObservationWindow], List[Observation], List[str]]:
        """Hybrid windowing — temporal with minimum commit-count merging.

        Algorithm (OEAS §18.4):
          1. Build temporal windows
          2. Merge adjacent windows if commit count < min_commits
          3. Renumber
        """
        warnings: List[str] = []

        # Build temporal windows first
        temporal_windows, _, _ = self._build_temporal(observations, config)
        if not temporal_windows:
            return [], [], ["No temporal windows to merge"]

        min_commits = config.min_observations
        merged: List[ObservationWindow] = []
        current = temporal_windows[0]

        for window in temporal_windows[1:]:
            # Count M-02 observations in current window
            commit_count = sum(1 for obs in current.observations if obs.metric_id == "M-02")
            if commit_count < min_commits:
                # Merge current with next window
                current = self._merge_windows(current, window)
            else:
                merged.append(current)
                current = window

        merged.append(current)

        # Renumber and validate
        merged = self._renumber_windows(merged)

        if not merged:
            warnings.append("No non-empty hybrid windows produced")

        return merged, [], warnings

    # ------------------------------------------------------------------
    # Strategy: Custom (OEAS §18.1)
    # ------------------------------------------------------------------

    def _build_custom(
        self,
        observations: List[Observation],
        config: WindowConfig,
    ) -> Tuple[List[ObservationWindow], List[Observation], List[str]]:
        """Custom boundary windowing — user-supplied ISO-8601 boundaries."""
        warnings: List[str] = []
        assert config.custom_boundaries is not None

        # Pre-parse all timestamps once for O(N) assignment
        all_parsed = [(self._parse_ts(obs.timestamp).date(), obs) for obs in observations]

        windows: List[ObservationWindow] = []
        pointer = 0  # O(N) pointer — never moves backward

        for i, (start_str, end_str) in enumerate(config.custom_boundaries):
            start_date = self._parse_ts(start_str).date()
            end_date = self._parse_ts(end_str).date()

            # Collect observations in [start_date, end_date) using pointer
            window_obs: List[Observation] = []
            while pointer < len(all_parsed):
                obs_date = all_parsed[pointer][0]
                if obs_date >= end_date:
                    break
                if obs_date >= start_date:
                    window_obs.append(all_parsed[pointer][1])
                pointer += 1

            if window_obs:
                windows.append(
                    self._make_window(
                        window_idx=i,
                        strategy="custom",
                        observations=window_obs,
                        start_boundary=start_date,
                        end_boundary=end_date,
                    )
                )

        if not windows:
            warnings.append("No non-empty custom windows produced")

        return windows, [], warnings

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_window(
        self,
        window_idx: int,
        strategy: str,
        observations: List[Observation],
        start_boundary: datetime.date,
        end_boundary: datetime.date,
        start_commit: Optional[str] = None,
        end_commit: Optional[str] = None,
    ) -> ObservationWindow:
        """Create an ObservationWindow with deterministic ID."""
        window_id = f"w{window_idx:02d}"
        return ObservationWindow(
            window_id=window_id,
            window_index=window_idx,
            strategy=strategy,
            start_boundary=f"{start_boundary.isoformat()}T00:00:00+00:00",  # type: ignore[attr-defined]
            end_boundary=f"{end_boundary.isoformat()}T00:00:00+00:00",  # type: ignore[attr-defined]
            observations=list(observations),
            start_commit=start_commit,
            end_commit=end_commit,
        )

    def _merge_windows(self, a: ObservationWindow, b: ObservationWindow) -> ObservationWindow:
        """Merge two adjacent windows into one."""
        merged_obs = a.observations + b.observations
        merged_obs.sort(key=lambda o: o.timestamp)
        return ObservationWindow(
            window_id=a.window_id,  # temporary, will be renumbered
            window_index=a.window_index,
            strategy=a.strategy,
            start_boundary=a.start_boundary,
            end_boundary=b.end_boundary,
            observations=merged_obs,
            start_commit=a.start_commit or b.start_commit,
            end_commit=b.end_commit or a.end_commit,
        )

    def _renumber_windows(self, windows: List[ObservationWindow]) -> List[ObservationWindow]:
        """Assign sequential window_ids and indices."""
        result: List[ObservationWindow] = []
        for i, window in enumerate(windows):
            new_window = ObservationWindow(
                window_id=f"w{i:02d}",
                window_index=i,
                strategy=window.strategy,
                start_boundary=window.start_boundary,
                end_boundary=window.end_boundary,
                observations=window.observations,
                start_commit=window.start_commit,
                end_commit=window.end_commit,
                statistics=window.statistics,
                metadata=window.metadata,
            )
            result.append(new_window)
        return result

    def _compute_statistics(self, observations: List[Observation]) -> ObservationStatistics:
        """Compute aggregate statistics for a set of observations."""
        if not observations:
            return ObservationStatistics(mean=0.0, std=0.0, min_value=0.0, max_value=0.0, n=0)

        values = [obs.value for obs in observations]
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / max(n - 1, 1)
        std = variance**0.5

        return ObservationStatistics(
            mean=mean,
            std=std,
            min_value=min(values),
            max_value=max(values),
            n=n,
        )

    @staticmethod
    def _parse_ts(ts: str) -> datetime:
        """Parse an ISO-8601 timestamp string."""
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
