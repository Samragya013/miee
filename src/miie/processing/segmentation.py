"""Window Segmentation Engine for MIIE v1.0.

Implements INT-03: Window Segmentation Engine interface.
Segments metric data into windows for analysis.
"""
from typing import Optional, List, Tuple
from datetime import datetime, timezone, timedelta

from ..schemas.models import WindowDefinition, MetricDataFrame
from miie.contracts.errors import ValidationError


class WindowSegmentationEngine:
    """INT-03: Window Segmentation Engine"""

    def segment(
        self,
        metric_dataframe: MetricDataFrame,
        strategy: str,
        size: int,
        custom_boundaries: Optional[List[Tuple[datetime, datetime]]] = None,
        repository_context=None,
    ) -> List[WindowDefinition]:
        """Segment metric data into analysis windows.

        Args:
            metric_dataframe: Container for extracted metrics
            strategy: Segmentation strategy ("time", "commit", "release", "custom")
            size: Window size (number of time units, commits, or releases)
            custom_boundaries: Custom window boundaries for "custom" strategy
            repository_context: Repository context with first/last commit dates (optional)

        Returns:
            List[WindowDefinition]: List of window definitions
        """
        # Validate inputs
        if metric_dataframe is None:
            raise ValueError("metric_dataframe cannot be None")
        if strategy not in {"time", "commit", "release", "custom"}:
            raise ValueError(f"strategy must be one of 'time', 'commit', 'release', 'custom', got {strategy}")
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")
        if strategy == "custom" and custom_boundaries is None:
            raise ValueError("custom_boundaries must be provided for custom strategy")
        if custom_boundaries is not None and strategy != "custom":
            raise ValueError("custom_boundaries can only be used with 'custom' strategy")
        if custom_boundaries is not None:
            for i, boundary in enumerate(custom_boundaries):
                if not isinstance(boundary, tuple) or len(boundary) != 2:
                    raise ValueError(f"custom_boundaries[{i}] must be a tuple of two datetimes, got {boundary}")
                start, end = boundary
                if not isinstance(start, datetime) or not isinstance(end, datetime):
                    raise ValueError(f"custom_boundaries[{i}] elements must be datetime objects, got {type(start)}, {type(end)}")
                if start >= end:
                    raise ValueError(f"custom_boundaries[{i}] start must be before end, got {start} >= {end}")
            # Check for overlapping boundaries
            # Sort boundaries by start date to check for overlaps
            sorted_boundaries = sorted(custom_boundaries, key=lambda x: x[0])
            for i in range(len(sorted_boundaries)-1):
                if sorted_boundaries[i][1] > sorted_boundaries[i+1][0]:
                    raise ValidationError(f"custom_boundaries overlap: {sorted_boundaries[i]} and {sorted_boundaries[i+1]}")

        # Extract basic information from metric_dataframe
        # Get timestamp from metric_dataframe (as a fallback for date)
        run_timestamp = metric_dataframe.timestamp
        run_date = run_timestamp.date()

        # Try to get total commit count from M-02 metric
        total_commits = 0
        if metric_dataframe.metrics and "M-02" in metric_dataframe.metrics:
            m02_data = metric_dataframe.metrics["M-02"]
            # m02_data is a dict mapping window IDs to lists of values
            # We assume the data is for a single window (the entire history) for now
            for window_id, values in m02_data.items():
                if values:
                    # Sum the commit counts? Or take the last? We'll sum for safety.
                    total_commits += sum(v for v in values if v is not None)

        # If we have zero commits and strategy is not custom, return an empty list of windows
        if total_commits < 1 and strategy != "custom":
            return []

        # Generate window definitions based on strategy
        windows: List[WindowDefinition] = []

        if strategy == "custom":
            # Use custom boundaries to create windows
            for i, (start_dt, end_dt) in enumerate(custom_boundaries):
                window_id = f"w{i:02d}"
                # Calculate commit count for this window? We don't have per-window commit data.
                # For now, we distribute total commits evenly? Or set to 1? We'll use 1 as placeholder.
                commit_count = max(1, total_commits // len(custom_boundaries)) if custom_boundaries else 1
                windows.append(
                    WindowDefinition(
                        window_id=window_id,
                        start_date=start_dt.date(),
                        end_date=end_dt.date(),
                        commits=commit_count,
                        strategy=strategy,
                        size_config={"size": size, "boundary_index": i},
                    )
                )
        elif strategy == "time":
            # For time strategy, create a window of 'size' days ending at the run date
            end_date = run_date
            start_date = end_date - timedelta(days=size)
            window_id = "w00"
            windows.append(
                WindowDefinition(
                    window_id=window_id,
                    start_date=start_date,
                    end_date=end_date,
                    commits=total_commits,
                    strategy=strategy,
                    size_config={"size": size},
                )
            )
        elif strategy == "commit":
            # For commit strategy, divide the date range proportionally by commit count.
            # Each window covers 'size' commits worth of time.
            first_date = None
            last_date = None

            # Get first/last commit dates from repository_context if available
            if repository_context is not None:
                if hasattr(repository_context, 'first_commit_date') and repository_context.first_commit_date:
                    first_date = repository_context.first_commit_date
                if hasattr(repository_context, 'last_commit_date') and repository_context.last_commit_date:
                    last_date = repository_context.last_commit_date

            if first_date and last_date and total_commits > 0 and size > 0:
                # Calculate how many days per window based on commit density
                total_days = max(1, (last_date - first_date).days)
                commits_per_day = total_commits / total_days
                days_per_window = max(1, int(size / commits_per_day)) if commits_per_day > 0 else total_days

                window_start = first_date
                window_idx = 0
                while window_start < last_date:
                    window_end = min(window_start + timedelta(days=days_per_window), last_date)
                    # Skip degenerate windows where start == end
                    if window_start.date() >= window_end.date():
                        break
                    # Estimate commits in this window based on proportional time span
                    window_fraction = (window_end - window_start).days / total_days
                    window_commits = max(1, int(total_commits * window_fraction))
                    window_id = f"w{window_idx:02d}"
                    windows.append(
                        WindowDefinition(
                            window_id=window_id,
                            start_date=window_start.date(),
                            end_date=window_end.date(),
                            commits=window_commits,
                            strategy=strategy,
                            size_config={"size": size},
                        )
                    )
                    window_start = window_end
                    window_idx += 1
            else:
                # Fallback: single window with all commits
                windows.append(
                    WindowDefinition(
                        window_id="w00",
                        start_date=run_date,
                        end_date=run_date + timedelta(days=1),
                        commits=total_commits,
                        strategy=strategy,
                        size_config={"size": size},
                    )
                )
        else:
            # For release strategy (and any other), we fall back to a single window with a one-day range
            start_date = run_date
            end_date = start_date + timedelta(days=1)
            window_id = "w00"
            windows.append(
                WindowDefinition(
                    window_id=window_id,
                    start_date=start_date,
                    end_date=end_date,
                    commits=total_commits,
                    strategy=strategy,
                    size_config={"size": size},
                )
            )

        return windows


class MockSegmentationEngine:
    """Mock segmentation engine that returns deterministic window definition."""

    def segment(
        self,
        metric_dataframe: MetricDataFrame,
        strategy: str,
        size: int,
        custom_boundaries: Optional[List[Tuple[datetime, datetime]]] = None,
    ) -> List[WindowDefinition]:
        """Return a fixed list of WindowDefinition for testing."""
        if strategy == "custom" and custom_boundaries is not None:
            # Return a window for each custom boundary
            windows = []
            for i, (start_dt, end_dt) in enumerate(custom_boundaries):
                window_id = f"w{i:02d}"
                windows.append(
                    WindowDefinition(
                        window_id=window_id,
                        start_date=start_dt.date(),
                        end_date=end_dt.date(),
                        commits=1,  # deterministic value for mock
                        strategy=strategy,
                        size_config={"size": size, "boundary_index": i},
                    )
                )
            return windows
        else:
            # Return a single fixed window for non-custom strategies or when no custom boundaries
            return [
                WindowDefinition(
                    window_id="w00",
                    start_date=datetime(2023, 1, 1, tzinfo=timezone.utc).date(),
                    end_date=datetime(2023, 12, 31, tzinfo=timezone.utc).date(),
                    commits=1,
                    strategy=strategy,
                    size_config={"size": size},
                )
            ]