"""
MIIE v1.5 Sampling Framework — Sampling Planner.

Profiles repositories and produces SamplingPlans with recommended strategies.
The planner evaluates all candidates and selects the highest-scoring valid
strategy.

Reference: PR-7B Phase 1-2, OEAS SS21
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from miie.processing.observation.models import (
    Observation,
    ObservationCollection,
)

from .models import (
    ActivityClass,
    ReadinessReport,
    RepositoryProfile,
    RepositoryScale,
    SamplingPlan,
    StrategyCandidate,
    VolatilityClass,
)
from .strategy import StrategyEngine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Activity Classification Thresholds
# ---------------------------------------------------------------------------

_ACTIVITY_THRESHOLDS = {
    ActivityClass.INACTIVE.value: (0, 0.01),
    ActivityClass.SPARSE.value: (0.01, 0.1),
    ActivityClass.MODERATE.value: (0.1, 1.0),
    ActivityClass.ACTIVE.value: (1.0, 5.0),
    ActivityClass.HIGHLY_ACTIVE.value: (5.0, float("inf")),
}

_SCALE_THRESHOLDS = {
    RepositoryScale.TINY.value: (0, 100),
    RepositoryScale.SMALL.value: (100, 1000),
    RepositoryScale.MEDIUM.value: (1000, 10000),
    RepositoryScale.LARGE.value: (10000, 100000),
    RepositoryScale.MASSIVE.value: (100000, float("inf")),
}

_VOLATILITY_THRESHOLDS = {
    VolatilityClass.STABLE.value: (0.0, 0.3),
    VolatilityClass.MODERATE.value: (0.3, 0.7),
    VolatilityClass.VOLATILE.value: (0.7, float("inf")),
}


class SamplingPlanner:
    """Profiles repositories and produces SamplingPlans.

    The planner:
    1. Profiles the repository from observations (Phase 1)
    2. Evaluates all candidate strategies (Phase 2)
    3. Selects the highest-scoring VALID strategy
    4. Returns a complete SamplingPlan
    """

    def __init__(
        self,
        strategy_engine: Optional[StrategyEngine] = None,
    ) -> None:
        """Initialize with optional custom strategy engine.

        Args:
            strategy_engine: StrategyEngine instance. Uses default if None.
        """
        self._strategy_engine = strategy_engine or StrategyEngine()

    def profile(
        self,
        collection: ObservationCollection,
    ) -> RepositoryProfile:
        """Compute a deterministic repository profile from observations.

        Args:
            collection: ObservationCollection containing all observations.

        Returns:
            RepositoryProfile with all computed characteristics.
        """
        # Flatten all observations
        all_obs: List[Observation] = []
        for window in collection.windows:
            all_obs.extend(window.observations)

        if not all_obs:
            return self._empty_profile()

        # Basic counts
        commit_count = len({obs.source_id for obs in all_obs if obs.source_type == "commit"})
        observation_count = len(all_obs)

        # Time span
        timestamps = sorted(obs.timestamp for obs in all_obs)
        first_ts = self._parse_ts(timestamps[0])
        last_ts = self._parse_ts(timestamps[-1])
        time_span_days = max(1, (last_ts - first_ts).days)

        # Densities
        repo_age_days = time_span_days
        observation_density = observation_count / repo_age_days if repo_age_days > 0 else 0.0
        commit_density = commit_count / repo_age_days if repo_age_days > 0 else 0.0
        avg_commits_per_day = commit_density

        # Metrics available
        metrics_available = tuple(sorted({obs.metric_id for obs in all_obs}))

        # M-02 observation count (used for commit_count window estimation)
        m02_count = sum(1 for obs in all_obs if obs.metric_id == "M-02")

        # Window statistics (using default temporal windows for profiling)
        window_stats = self._compute_window_stats(all_obs)

        # Classifications
        activity_class = self._classify_activity(avg_commits_per_day)
        scale = self._classify_scale(observation_count)
        volatility = self._classify_volatility(window_stats.get("cv", 0.0))

        return RepositoryProfile(
            commit_count=commit_count,
            repo_age_days=repo_age_days,
            observation_count=observation_count,
            observation_density=round(observation_density, 4),
            commit_density=round(commit_density, 4),
            avg_commits_per_day=round(avg_commits_per_day, 4),
            window_density=window_stats.get("window_density", 0.0),
            avg_obs_per_window=window_stats.get("avg_obs", 0.0),
            min_obs_per_window=window_stats.get("min_obs", 0),
            max_obs_per_window=window_stats.get("max_obs", 0),
            median_obs_per_window=window_stats.get("median_obs", 0.0),
            variance=window_stats.get("variance", 0.0),
            cv=window_stats.get("cv", 0.0),
            window_balance=window_stats.get("window_balance", 0.0),
            activity_class=activity_class,
            scale=scale,
            volatility=volatility,
            metrics_available=metrics_available,
            time_span_days=time_span_days,
            m02_observation_count=m02_count,
        )

    def plan(
        self,
        collection: ObservationCollection,
        readiness: Optional[ReadinessReport] = None,
    ) -> SamplingPlan:
        """Produce a complete sampling plan for a repository.

        Args:
            collection: ObservationCollection containing all observations.
            readiness: Optional pre-computed readiness report.

        Returns:
            SamplingPlan with chosen strategy and diagnostics.
        """
        # Phase 1: Profile
        profile = self.profile(collection)

        # Phase 2: Evaluate candidates
        valid_candidates, rejected_candidates = self._strategy_engine.evaluate(profile)

        # Select best valid candidate
        if valid_candidates:
            chosen = valid_candidates[0]
            alternatives = tuple(valid_candidates[1:])
            rejected = tuple(rejected_candidates)

            # Determine scientific confidence
            confidence = self._assess_confidence(chosen, profile)

            # Build rationale
            rationale = self._build_rationale(chosen, profile)

            # Compute calibration metrics (PR-7C-1): expected vs actual builder behavior
            predicted_windows, predicted_obs_per_window = self._strategy_engine._estimate_windows(
                profile, chosen.strategy, chosen.window_size
            )
            # Actual builder uses M-02 observations for commit_count boundaries
            actual_m02 = profile.m02_observation_count
            if actual_m02 > 0 and chosen.strategy == "commit_count":
                actual_windows = max(1, actual_m02 // chosen.window_size)
                # Include last boundary (builder appends final timestamp)
                if actual_m02 % chosen.window_size > 0:
                    actual_windows += 1
            elif chosen.strategy == "temporal":
                actual_windows = max(1, profile.repo_age_days // chosen.window_size) if profile.repo_age_days > 0 else 1
            elif chosen.strategy == "hybrid":
                temporal_w = max(1, profile.repo_age_days // chosen.window_size) if profile.repo_age_days > 0 else 1
                actual_windows = max(1, int(temporal_w * 0.7))
            else:
                actual_windows = predicted_windows

            window_diff = abs(predicted_windows - actual_windows)
            prediction_error = window_diff / max(predicted_windows, 1)
            # Adjust confidence based on prediction error
            confidence_adj = 0.0
            if prediction_error > 0.3:
                confidence_adj = -0.2

            planning_notes: List[str] = []
            if prediction_error > 0.3:
                planning_notes.append(
                    f"Prediction error {prediction_error:.0%}: planner predicted "
                    f"{predicted_windows} windows, actual builder produces ~{actual_windows}"
                )

            planning_notes.append(
                f"Calibration: planner={predicted_windows}, actual~={actual_windows}, " f"error={prediction_error:.0%}"
            )
            if chosen.expected_windows < 5:
                planning_notes.append(
                    f"Only {chosen.expected_windows} estimated windows; " "results may have limited statistical power"
                )
            if profile.observation_density < 0.5:
                planning_notes.append("Low observation density; consider extending analysis time range")

            return SamplingPlan(
                chosen=chosen,
                alternatives=alternatives,
                rejected=rejected,
                scientific_confidence=confidence,
                selection_rationale=rationale,
                planning_notes=planning_notes,
                profile=profile,
                prediction_error=round(prediction_error, 4),
                window_difference=window_diff,
                observation_difference=round(
                    abs(chosen.expected_obs_per_window * predicted_windows - profile.observation_count), 1
                ),
                confidence_adjustment=confidence_adj,
            )
        else:
            # No valid candidates — use the least-bad rejected one
            if rejected_candidates:
                chosen = rejected_candidates[0]
                return SamplingPlan(
                    chosen=chosen,
                    alternatives=(),
                    rejected=tuple(rejected_candidates[1:]),
                    scientific_confidence="low",
                    selection_rationale=(
                        f"No valid strategy found. Using {chosen.strategy} "
                        f"(size={chosen.window_size}) as best available option."
                    ),
                    planning_notes=["Repository has insufficient data for any strategy to be fully valid"],
                    profile=profile,
                )
            else:
                # No candidates at all
                fallback = StrategyCandidate(
                    strategy="temporal",
                    window_size=30,
                    score=0.0,
                    expected_windows=0,
                    expected_obs_per_window=0.0,
                    verdict="INVALID",
                    notes=["No candidates evaluated"],
                )
                return SamplingPlan(
                    chosen=fallback,
                    scientific_confidence="low",
                    selection_rationale="No viable strategy found for this repository",
                    planning_notes=["Repository has no observations or extremely limited data"],
                    profile=profile,
                )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_window_stats(self, observations: List[Observation]) -> Dict[str, float]:
        """Compute window-level statistics using temporal windowing (30-day windows).

        Returns dict with avg_obs, min_obs, max_obs, median_obs, variance, cv,
        window_balance, window_density.
        """
        if not observations:
            return {
                "avg_obs": 0.0,
                "min_obs": 0,
                "max_obs": 0,
                "median_obs": 0.0,
                "variance": 0.0,
                "cv": 0.0,
                "window_balance": 0.0,
                "window_density": 0.0,
            }

        # Sort by timestamp
        observations = sorted(observations, key=lambda o: o.timestamp)
        first_ts = self._parse_ts(observations[0].timestamp)
        last_ts = self._parse_ts(observations[-1].timestamp)

        # Build 30-day temporal windows
        window_counts: List[int] = []
        window_start = first_ts.date()
        window_size_days = 30

        while window_start <= last_ts.date():
            window_end = window_start + __import__("datetime").timedelta(days=window_size_days)
            count = sum(1 for obs in observations if window_start <= self._parse_ts(obs.timestamp).date() < window_end)
            if count > 0:
                window_counts.append(count)
            window_start = window_end

        if not window_counts:
            return {
                "avg_obs": 0.0,
                "min_obs": 0,
                "max_obs": 0,
                "median_obs": 0.0,
                "variance": 0.0,
                "cv": 0.0,
                "window_balance": 0.0,
                "window_density": 0.0,
            }

        n = len(window_counts)
        avg = sum(window_counts) / n
        variance = sum((x - avg) ** 2 for x in window_counts) / max(n - 1, 1)
        std = variance**0.5
        cv = std / avg if avg > 0 else 0.0
        window_balance = 1.0 - min(1.0, std / avg) if avg > 0 else 0.0

        sorted_counts = sorted(window_counts)
        median = sorted_counts[n // 2] if n % 2 == 1 else (sorted_counts[n // 2 - 1] + sorted_counts[n // 2]) / 2

        repo_age_days = max(1, (last_ts - first_ts).days)

        return {
            "avg_obs": round(avg, 2),
            "min_obs": min(window_counts),
            "max_obs": max(window_counts),
            "median_obs": round(median, 2),
            "variance": round(variance, 2),
            "cv": round(cv, 4),
            "window_balance": round(window_balance, 4),
            "window_density": round(len(window_counts) / repo_age_days, 4),
        }

    def _classify_activity(self, avg_commits_per_day: float) -> str:
        """Classify repository activity level."""
        for cls, (low, high) in _ACTIVITY_THRESHOLDS.items():
            if low <= avg_commits_per_day < high:
                return cls
        return ActivityClass.MODERATE.value

    def _classify_scale(self, observation_count: int) -> str:
        """Classify repository scale."""
        for cls, (low, high) in _SCALE_THRESHOLDS.items():
            if low <= observation_count < high:
                return cls
        return RepositoryScale.MEDIUM.value

    def _classify_volatility(self, cv: float) -> str:
        """Classify repository volatility."""
        for cls, (low, high) in _VOLATILITY_THRESHOLDS.items():
            if low <= cv < high:
                return cls
        return VolatilityClass.MODERATE.value

    def _assess_confidence(
        self,
        chosen: StrategyCandidate,
        profile: RepositoryProfile,
    ) -> str:
        """Assess scientific confidence in the chosen strategy."""
        if chosen.score >= 0.8 and chosen.expected_windows >= 5 and chosen.expected_obs_per_window >= 20:
            return "high"
        elif chosen.score >= 0.5 and chosen.expected_windows >= 2:
            return "medium"
        else:
            return "low"

    def _build_rationale(
        self,
        chosen: StrategyCandidate,
        profile: RepositoryProfile,
    ) -> str:
        """Build human-readable rationale for strategy selection."""
        parts = [f"Selected {chosen.strategy} (size={chosen.window_size}) " f"with score {chosen.score:.2f}."]
        parts.append(
            f"Expected {chosen.expected_windows} windows with "
            f"~{chosen.expected_obs_per_window:.0f} observations each."
        )
        if profile.activity_class in ("active", "highly_active"):
            parts.append("Repository is active; temporal windowing provides good coverage.")
        elif profile.activity_class in ("inactive", "sparse"):
            parts.append("Repository has limited activity; commit-based windowing maximizes data usage.")
        return " ".join(parts)

    def _empty_profile(self) -> RepositoryProfile:
        """Return an empty profile for repositories with no observations."""
        return RepositoryProfile(
            commit_count=0,
            repo_age_days=0,
            observation_count=0,
            observation_density=0.0,
            commit_density=0.0,
            avg_commits_per_day=0.0,
            window_density=0.0,
            avg_obs_per_window=0.0,
            min_obs_per_window=0,
            max_obs_per_window=0,
            median_obs_per_window=0.0,
            variance=0.0,
            cv=0.0,
            window_balance=0.0,
            activity_class=ActivityClass.INACTIVE.value,
            scale=RepositoryScale.TINY.value,
            volatility=VolatilityClass.STABLE.value,
            metrics_available=(),
            time_span_days=0,
            m02_observation_count=0,
        )

    @staticmethod
    def _parse_ts(ts: str) -> Any:
        """Parse ISO-8601 timestamp."""
        from datetime import datetime

        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
