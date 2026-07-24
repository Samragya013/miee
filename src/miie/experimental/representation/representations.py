"""
Observation Representations

Implements multiple observation representation strategies
for improving downstream detector performance.

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

from datetime import datetime
from typing import Dict, List, Optional

import numpy as np

from miie.experimental.representation.base import (
    BaseRepresentation,
    EnhancedObservation,
    EnhancedWindow,
)
from miie.processing.observation.models import Observation, ObservationWindow


class BaselineRepresentation(BaseRepresentation):
    """Baseline representation using raw observation values.

    This is the current production representation that serves
    as the control for comparison.
    """

    @property
    def name(self) -> str:
        return "baseline"

    @property
    def description(self) -> str:
        return "Raw observation values without additional features"

    @property
    def feature_names(self) -> List[str]:
        return []

    def transform(self, windows: List[ObservationWindow]) -> List[EnhancedWindow]:
        """Transform windows using baseline representation.

        Args:
            windows: List of observation windows

        Returns:
            List of enhanced windows (no additional features)
        """
        enhanced_windows = []

        for window in windows:
            enhanced_observations = []

            for obs in window.observations:
                enhanced_obs = EnhancedObservation.from_observation(obs, features={})
                enhanced_observations.append(enhanced_obs)

            enhanced_window = EnhancedWindow(
                window_id=window.window_id,
                window_index=window.window_index,
                strategy=window.strategy,
                start_boundary=window.start_boundary,
                end_boundary=window.end_boundary,
                enhanced_observations=enhanced_observations,
                representation_name=self.name,
            )
            enhanced_windows.append(enhanced_window)

        return enhanced_windows


class MultiScaleRepresentation(BaseRepresentation):
    """Multi-scale window representation.

    Organizes observations at multiple temporal scales to capture
    patterns at different granularities.

    Scientific Justification:
    - Software evolution exhibits multi-scale temporal patterns (Basili et al., 2008)
    - Different defect types manifest at different time scales (Mockus & Weiss, 2000)
    - Change magnitude varies by temporal context (Nagappan & Ball, 2005)
    """

    def __init__(self, scales: Optional[List[int]] = None):
        """Initialize multi-scale representation.

        Args:
            scales: List of window sizes in number of observations.
                   Defaults to [5, 10, 20] for daily, weekly, monthly.
        """
        self._scales = scales or [5, 10, 20]

    @property
    def name(self) -> str:
        return "multi_scale"

    @property
    def description(self) -> str:
        return f"Multi-scale window representation with scales {self._scales}"

    @property
    def feature_names(self) -> List[str]:
        features = []
        for scale in self._scales:
            features.extend(
                [
                    f"scale_{scale}_mean",
                    f"scale_{scale}_std",
                    f"scale_{scale}_min",
                    f"scale_{scale}_max",
                ]
            )
        return features

    def transform(self, windows: List[ObservationWindow]) -> List[EnhancedWindow]:
        """Transform windows using multi-scale representation.

        Args:
            windows: List of observation windows

        Returns:
            List of enhanced windows with multi-scale features
        """
        enhanced_windows = []

        # Collect all observations across windows for multi-scale computation
        all_observations = []
        for window in windows:
            all_observations.extend(window.observations)

        for window in windows:
            enhanced_observations = []

            for obs in window.observations:
                # Compute multi-scale features for this observation
                features = self._compute_multiscale_features(obs, all_observations)

                enhanced_obs = EnhancedObservation.from_observation(obs, features)
                enhanced_observations.append(enhanced_obs)

            enhanced_window = EnhancedWindow(
                window_id=window.window_id,
                window_index=window.window_index,
                strategy=window.strategy,
                start_boundary=window.start_boundary,
                end_boundary=window.end_boundary,
                enhanced_observations=enhanced_observations,
                representation_name=self.name,
            )
            enhanced_windows.append(enhanced_window)

        return enhanced_windows

    def _compute_multiscale_features(self, obs: Observation, all_observations: List[Observation]) -> Dict[str, float]:
        """Compute multi-scale features for an observation.

        Args:
            obs: Target observation
            all_observations: All observations for context

        Returns:
            Dictionary of multi-scale features
        """
        features = {}

        # Filter observations for same metric
        metric_obs = [o for o in all_observations if o.metric_id == obs.metric_id]

        # Find index of current observation
        obs_idx = None
        for i, o in enumerate(metric_obs):
            if o.observation_id == obs.observation_id:
                obs_idx = i
                break

        if obs_idx is None:
            # Observation not found, return defaults
            for scale in self._scales:
                features[f"scale_{scale}_mean"] = 0.0
                features[f"scale_{scale}_std"] = 0.0
                features[f"scale_{scale}_min"] = 0.0
                features[f"scale_{scale}_max"] = 0.0
            return features

        # Compute features for each scale
        for scale in self._scales:
            # Get window of observations around current
            start_idx = max(0, obs_idx - scale // 2)
            end_idx = min(len(metric_obs), obs_idx + scale // 2 + 1)
            window_values = [o.value for o in metric_obs[start_idx:end_idx]]

            if window_values:
                features[f"scale_{scale}_mean"] = np.mean(window_values)
                features[f"scale_{scale}_std"] = np.std(window_values) if len(window_values) > 1 else 0.0
                features[f"scale_{scale}_min"] = min(window_values)
                features[f"scale_{scale}_max"] = max(window_values)
            else:
                features[f"scale_{scale}_mean"] = 0.0
                features[f"scale_{scale}_std"] = 0.0
                features[f"scale_{scale}_min"] = 0.0
                features[f"scale_{scale}_max"] = 0.0

        return features


class TemporalContextRepresentation(BaseRepresentation):
    """Temporal-context representation.

    Enriches observations with temporal context including
    day of week, time since last commit, and commit velocity.

    Scientific Justification:
    - Commit timing correlates with defect introduction (Graves et al., 2000)
    - Velocity changes indicate process shifts (Hinde & Dempsey, 1998)
    - Temporal context improves anomaly detection (Li et al., 2019)
    """

    @property
    def name(self) -> str:
        return "temporal_context"

    @property
    def description(self) -> str:
        return "Temporal context features including timing and velocity"

    @property
    def feature_names(self) -> List[str]:
        return [
            "day_of_week",
            "hour_of_day",
            "time_since_last_commit_hours",
            "commits_per_day",
            "is_weekend",
        ]

    def transform(self, windows: List[ObservationWindow]) -> List[EnhancedWindow]:
        """Transform windows using temporal-context representation.

        Args:
            windows: List of observation windows

        Returns:
            List of enhanced windows with temporal context features
        """
        enhanced_windows = []

        # Sort observations by timestamp
        all_observations = []
        for window in windows:
            all_observations.extend(window.observations)

        # Sort by timestamp
        all_observations.sort(key=lambda o: o.timestamp)

        # Compute temporal context for each observation
        obs_timestamps = {}
        for obs in all_observations:
            try:
                dt = datetime.fromisoformat(obs.timestamp.replace("Z", "+00:00"))
                obs_timestamps[obs.observation_id] = dt
            except (ValueError, AttributeError):
                obs_timestamps[obs.observation_id] = None

        for window in windows:
            enhanced_observations = []

            for obs in window.observations:
                # Compute temporal context features
                features = self._compute_temporal_features(obs, obs_timestamps, all_observations)

                enhanced_obs = EnhancedObservation.from_observation(obs, features)
                enhanced_observations.append(enhanced_obs)

            enhanced_window = EnhancedWindow(
                window_id=window.window_id,
                window_index=window.window_index,
                strategy=window.strategy,
                start_boundary=window.start_boundary,
                end_boundary=window.end_boundary,
                enhanced_observations=enhanced_observations,
                representation_name=self.name,
            )
            enhanced_windows.append(enhanced_window)

        return enhanced_windows

    def _compute_temporal_features(
        self,
        obs: Observation,
        obs_timestamps: Dict[str, Optional[datetime]],
        all_observations: List[Observation],
    ) -> Dict[str, float]:
        """Compute temporal context features for an observation.

        Args:
            obs: Target observation
            obs_timestamps: Map of observation_id to timestamp
            all_observations: All observations for context

        Returns:
            Dictionary of temporal context features
        """
        features = {}

        obs_dt = obs_timestamps.get(obs.observation_id)

        if obs_dt is None:
            # No timestamp available
            features["day_of_week"] = 0.0
            features["hour_of_day"] = 0.0
            features["time_since_last_commit_hours"] = 0.0
            features["commits_per_day"] = 0.0
            features["is_weekend"] = 0.0
            return features

        # Day of week (0=Monday, 6=Sunday)
        features["day_of_week"] = float(obs_dt.weekday())

        # Hour of day (0-23)
        features["hour_of_day"] = float(obs_dt.hour)

        # Is weekend
        features["is_weekend"] = 1.0 if obs_dt.weekday() >= 5 else 0.0

        # Time since last commit
        prev_commits = [
            obs_timestamps[o.observation_id]
            for o in all_observations
            if o.source_type == "commit"
            and obs_timestamps.get(o.observation_id) is not None
            and obs_timestamps[o.observation_id] < obs_dt
        ]

        if prev_commits:
            last_commit = max(prev_commits)  # type: ignore[type-var]
            time_diff = obs_dt - last_commit
            features["time_since_last_commit_hours"] = time_diff.total_seconds() / 3600.0
        else:
            features["time_since_last_commit_hours"] = 0.0

        # Commits per day (count of commits on same day)
        same_day_commits = [
            o
            for o in all_observations
            if o.source_type == "commit"
            and obs_timestamps.get(o.observation_id) is not None
            and obs_timestamps[o.observation_id].date() == obs_dt.date()
        ]
        features["commits_per_day"] = float(len(same_day_commits))

        return features


class HistoricalContextRepresentation(BaseRepresentation):
    """Historical-context representation.

    Enriches observations with historical context including
    rolling statistics, trend indicators, and anomaly scores.

    Scientific Justification:
    - Software metrics exhibit autocorrelation (El Emam et al., 2001)
    - Trend analysis improves change detection (Menzies et al., 2001)
    - Historical context reduces false positives (Kim et al., 2007)
    """

    def __init__(self, window_size: int = 10):
        """Initialize historical-context representation.

        Args:
            window_size: Number of historical observations to consider
        """
        self._window_size = window_size

    @property
    def name(self) -> str:
        return "historical_context"

    @property
    def description(self) -> str:
        return f"Historical context with rolling window size {self._window_size}"

    @property
    def feature_names(self) -> List[str]:
        return [
            "rolling_mean",
            "rolling_std",
            "rolling_min",
            "rolling_max",
            "trend_slope",
            "trend_direction",
            "anomaly_score",
        ]

    def transform(self, windows: List[ObservationWindow]) -> List[EnhancedWindow]:
        """Transform windows using historical-context representation.

        Args:
            windows: List of observation windows

        Returns:
            List of enhanced windows with historical context features
        """
        enhanced_windows = []

        # Sort observations by timestamp
        all_observations = []
        for window in windows:
            all_observations.extend(window.observations)

        # Group by metric
        metric_observations = {}
        for obs in all_observations:
            if obs.metric_id not in metric_observations:
                metric_observations[obs.metric_id] = []
            metric_observations[obs.metric_id].append(obs)

        # Sort each metric's observations by timestamp
        for metric_id in metric_observations:
            metric_observations[metric_id].sort(key=lambda o: o.timestamp)

        for window in windows:
            enhanced_observations = []

            for obs in window.observations:
                # Compute historical context features
                features = self._compute_historical_features(obs, metric_observations)

                enhanced_obs = EnhancedObservation.from_observation(obs, features)
                enhanced_observations.append(enhanced_obs)

            enhanced_window = EnhancedWindow(
                window_id=window.window_id,
                window_index=window.window_index,
                strategy=window.strategy,
                start_boundary=window.start_boundary,
                end_boundary=window.end_boundary,
                enhanced_observations=enhanced_observations,
                representation_name=self.name,
            )
            enhanced_windows.append(enhanced_window)

        return enhanced_windows

    def _compute_historical_features(
        self,
        obs: Observation,
        metric_observations: Dict[str, List[Observation]],
    ) -> Dict[str, float]:
        """Compute historical context features for an observation.

        Args:
            obs: Target observation
            metric_observations: Map of metric_id to sorted observations

        Returns:
            Dictionary of historical context features
        """
        features = {}

        metric_obs = metric_observations.get(obs.metric_id, [])

        # Find index of current observation
        obs_idx = None
        for i, o in enumerate(metric_obs):
            if o.observation_id == obs.observation_id:
                obs_idx = i
                break

        if obs_idx is None or obs_idx < 2:
            # Not enough history
            features["rolling_mean"] = obs.value
            features["rolling_std"] = 0.0
            features["rolling_min"] = obs.value
            features["rolling_max"] = obs.value
            features["trend_slope"] = 0.0
            features["trend_direction"] = 0.0
            features["anomaly_score"] = 0.0
            return features

        # Get historical window
        start_idx = max(0, obs_idx - self._window_size)
        historical_values = [o.value for o in metric_obs[start_idx:obs_idx]]

        if not historical_values:
            features["rolling_mean"] = obs.value
            features["rolling_std"] = 0.0
            features["rolling_min"] = obs.value
            features["rolling_max"] = obs.value
            features["trend_slope"] = 0.0
            features["trend_direction"] = 0.0
            features["anomaly_score"] = 0.0
            return features

        # Rolling statistics
        features["rolling_mean"] = np.mean(historical_values)
        features["rolling_std"] = np.std(historical_values) if len(historical_values) > 1 else 0.0
        features["rolling_min"] = min(historical_values)
        features["rolling_max"] = max(historical_values)

        # Trend analysis (linear regression slope)
        if len(historical_values) >= 2:
            x = np.arange(len(historical_values))
            y = np.array(historical_values)
            slope = np.polyfit(x, y, 1)[0]
            features["trend_slope"] = slope
            features["trend_direction"] = 1.0 if slope > 0 else (-1.0 if slope < 0 else 0.0)
        else:
            features["trend_slope"] = 0.0
            features["trend_direction"] = 0.0

        # Anomaly score (z-score)
        if features["rolling_std"] > 0:
            features["anomaly_score"] = abs(obs.value - features["rolling_mean"]) / features["rolling_std"]
        else:
            features["anomaly_score"] = 0.0

        return features


class RepositoryStateRepresentation(BaseRepresentation):
    """Repository-state representation.

    Enriches observations with repository state context including
    file count, directory depth, author count, and branch count.

    Scientific Justification:
    - Repository structure correlates with defect density (Nagappan et al., 2006)
    - Author count indicates complexity (Wolf et al., 2009)
    - Branch count indicates development activity (Kagdi et al., 2007)
    """

    @property
    def name(self) -> str:
        return "repository_state"

    @property
    def description(self) -> str:
        return "Repository state features including structure and activity"

    @property
    def feature_names(self) -> List[str]:
        return [
            "file_count",
            "author_count",
            "branch_count",
            "total_commits",
            "activity_level",
        ]

    def transform(self, windows: List[ObservationWindow]) -> List[EnhancedWindow]:
        """Transform windows using repository-state representation.

        Args:
            windows: List of observation windows

        Returns:
            List of enhanced windows with repository state features
        """
        enhanced_windows = []

        # Collect all observations
        all_observations = []
        for window in windows:
            all_observations.extend(window.observations)

        # Compute repository state from observations
        repo_state = self._compute_repository_state(all_observations)

        for window in windows:
            enhanced_observations = []

            for obs in window.observations:
                # Compute repository state features for this observation
                features = self._compute_state_features(obs, repo_state)

                enhanced_obs = EnhancedObservation.from_observation(obs, features)
                enhanced_observations.append(enhanced_obs)

            enhanced_window = EnhancedWindow(
                window_id=window.window_id,
                window_index=window.window_index,
                strategy=window.strategy,
                start_boundary=window.start_boundary,
                end_boundary=window.end_boundary,
                enhanced_observations=enhanced_observations,
                representation_name=self.name,
            )
            enhanced_windows.append(enhanced_window)

        return enhanced_windows

    def _compute_repository_state(self, observations: List[Observation]) -> Dict[str, float]:
        """Compute repository state from observations.

        Args:
            observations: All observations

        Returns:
            Dictionary of repository state metrics
        """
        # Count unique files
        files = set()
        for obs in observations:
            if obs.source_type == "file":
                files.add(obs.source_id)

        # Count unique authors
        authors = set()
        for obs in observations:
            if "author_name" in obs.metadata:
                authors.add(obs.metadata["author_name"])
            elif "author_email" in obs.metadata:
                authors.add(obs.metadata["author_email"])

        # Count unique branches
        branches = set()
        for obs in observations:
            if obs.source_type == "branch":
                branches.add(obs.source_id)

        # Count commits
        commits = set()
        for obs in observations:
            if obs.source_type == "commit":
                commits.add(obs.source_id)

        # Compute activity level (commits per observation)
        activity_level = len(commits) / len(observations) if observations else 0.0

        return {
            "file_count": float(len(files)),
            "author_count": float(len(authors)),
            "branch_count": float(len(branches)),
            "total_commits": float(len(commits)),
            "activity_level": activity_level,
        }

    def _compute_state_features(self, obs: Observation, repo_state: Dict[str, float]) -> Dict[str, float]:
        """Compute repository state features for an observation.

        Args:
            obs: Target observation
            repo_state: Repository state metrics

        Returns:
            Dictionary of repository state features
        """
        return repo_state.copy()


class QualityWeightedRepresentation(BaseRepresentation):
    """Quality-weighted representation.

    Enriches observations with quality indicators including
    completeness, confidence, and provenance.

    Scientific Justification:
    - Observation quality affects detection accuracy (Kim et al., 2011)
    - Quality weighting reduces noise (Menzies & Greenwald, 2003)
    - Provenance tracking improves reproducibility (Potters et al., 2016)
    """

    @property
    def name(self) -> str:
        return "quality_weighted"

    @property
    def description(self) -> str:
        return "Quality-weighted representation with completeness and confidence"

    @property
    def feature_names(self) -> List[str]:
        return [
            "quality_score",
            "confidence_score",
            "has_provenance",
        ]

    def transform(self, windows: List[ObservationWindow]) -> List[EnhancedWindow]:
        """Transform windows using quality-weighted representation.

        Args:
            windows: List of observation windows

        Returns:
            List of enhanced windows with quality features
        """
        enhanced_windows = []

        for window in windows:
            enhanced_observations = []

            for obs in window.observations:
                # Compute quality features
                features = self._compute_quality_features(obs)

                enhanced_obs = EnhancedObservation.from_observation(obs, features)
                enhanced_observations.append(enhanced_obs)

            enhanced_window = EnhancedWindow(
                window_id=window.window_id,
                window_index=window.window_index,
                strategy=window.strategy,
                start_boundary=window.start_boundary,
                end_boundary=window.end_boundary,
                enhanced_observations=enhanced_observations,
                representation_name=self.name,
            )
            enhanced_windows.append(enhanced_window)

        return enhanced_windows

    def _compute_quality_features(self, obs: Observation) -> Dict[str, float]:
        """Compute quality features for an observation.

        Args:
            obs: Target observation

        Returns:
            Dictionary of quality features
        """
        features = {}

        # Quality score
        quality_map = {
            "complete": 1.0,
            "estimated": 0.8,
            "derived": 0.6,
            "missing": 0.0,
        }
        features["quality_score"] = quality_map.get(obs.quality, 0.5)

        # Confidence score (based on quality and provenance)
        confidence = features["quality_score"]
        if obs.provenance and obs.provenance.seed is not None:
            confidence = min(1.0, confidence + 0.1)
        features["confidence_score"] = confidence

        # Has provenance
        features["has_provenance"] = 1.0 if obs.provenance else 0.0

        return features
