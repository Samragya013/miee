"""
MIIE v1.5 Sampling Framework — Strategy Evaluation Engine.

Evaluates candidate windowing strategies against repository characteristics.
Each candidate receives a composite score based on observation density,
window balance, expected detector readiness, and sample adequacy.

Reference: PR-7B Phase 2, OEAS SS21
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from miie.sampling.models import (
    ReadinessState,
    RepositoryProfile,
    StrategyCandidate,
    StrategyVerdict,
)

# ---------------------------------------------------------------------------
# Candidate Strategy Definitions
# ---------------------------------------------------------------------------

# Default candidate strategies (PR-7B Phase 2: do NOT hardcode if/else)
DEFAULT_CANDIDATES: List[Tuple[str, int]] = [
    ("commit_count", 10),
    ("commit_count", 20),
    ("commit_count", 30),
    ("commit_count", 50),
    ("temporal", 14),
    ("temporal", 30),
    ("temporal", 60),
    ("hybrid", 30),
]

# Detector minimum requirements (immutable, from DES v2.0)
_DETECTOR_REQUIREMENTS: Dict[str, Dict[str, int]] = {
    "D-01": {"obs_per_window": 10, "windows": 2, "metrics": 1},
    "D-02": {"obs_per_window": 10, "windows": 2, "metrics": 2},
    "D-03": {"obs_per_window": 20, "windows": 1, "metrics": 1},
}


# ---------------------------------------------------------------------------
# Strategy Scoring Weights
# ---------------------------------------------------------------------------

# Composite score weights (sum = 1.0)
_W_OBSERVATION_DENSITY = 0.25
_W_WINDOW_BALANCE = 0.20
_W_DETECTOR_READINESS = 0.30
_W_SAMPLE_ADEQUACY = 0.15
_W_COVERAGE = 0.10


class StrategyEngine:
    """Evaluates candidate windowing strategies and recommends the best.

    The engine does NOT choose strategies — it evaluates all candidates
    and returns them sorted by score. The SamplingPlanner makes the
    final selection.
    """

    def __init__(
        self,
        candidates: Optional[List[Tuple[str, int]]] = None,
    ) -> None:
        """Initialize with optional custom candidates.

        Args:
            candidates: List of (strategy, window_size) tuples.
                       Defaults to DEFAULT_CANDIDATES.
        """
        self._candidates = candidates or DEFAULT_CANDIDATES

    def evaluate(
        self,
        profile: RepositoryProfile,
    ) -> Tuple[List[StrategyCandidate], List[StrategyCandidate]]:
        """Evaluate all candidate strategies for a repository profile.

        Args:
            profile: Computed repository profile.

        Returns:
            Tuple of (valid_candidates, rejected_candidates), each sorted
            by score descending.
        """
        valid: List[StrategyCandidate] = []
        rejected: List[StrategyCandidate] = []

        for strategy, window_size in self._candidates:
            candidate = self._evaluate_candidate(profile, strategy, window_size)
            if candidate.verdict == StrategyVerdict.INVALID.value:
                rejected.append(candidate)
            else:
                valid.append(candidate)

        # Sort by score descending
        valid.sort(key=lambda c: c.score, reverse=True)
        rejected.sort(key=lambda c: c.score, reverse=True)

        return valid, rejected

    def _evaluate_candidate(
        self,
        profile: RepositoryProfile,
        strategy: str,
        window_size: int,
    ) -> StrategyCandidate:
        """Evaluate a single candidate strategy.

        Scoring criteria:
          1. Observation density: How well the window size matches commit density
          2. Window balance: How evenly distributed observations are across windows
          3. Detector readiness: How many detectors can execute
          4. Sample adequacy: Whether windows have enough observations
          5. Coverage: How much of the repository history is covered
        """
        notes: List[str] = []

        # --- Estimate window characteristics ---
        estimated_windows, estimated_obs_per_window = self._estimate_windows(profile, strategy, window_size)

        # --- Scoring components ---

        # 1. Observation density score (0.0 - 1.0)
        obs_density_score = self._score_observation_density(profile, estimated_obs_per_window, notes)

        # 2. Window balance score (0.0 - 1.0)
        window_balance_score = self._score_window_balance(profile, estimated_windows, notes)

        # 3. Detector readiness score (0.0 - 1.0)
        detector_readiness_score, expected_readiness = self._score_detector_readiness(
            estimated_obs_per_window, estimated_windows, profile, notes
        )

        # 4. Sample adequacy score (0.0 - 1.0)
        sample_adequacy_score = self._score_sample_adequacy(estimated_obs_per_window, estimated_windows, notes)

        # 5. Coverage score (0.0 - 1.0)
        coverage_score = self._score_coverage(profile, strategy, window_size, estimated_windows, notes)

        # --- Composite score ---
        composite = (
            _W_OBSERVATION_DENSITY * obs_density_score
            + _W_WINDOW_BALANCE * window_balance_score
            + _W_DETECTOR_READINESS * detector_readiness_score
            + _W_SAMPLE_ADEQUACY * sample_adequacy_score
            + _W_COVERAGE * coverage_score
        )

        # --- Verdict ---
        if estimated_windows < 2:
            verdict = StrategyVerdict.INVALID.value
            notes.append(f"Estimated {estimated_windows} windows (minimum: 2)")
        elif estimated_obs_per_window < 10:
            verdict = StrategyVerdict.MARGINAL.value
            notes.append(f"Estimated {estimated_obs_per_window:.0f} obs/window (target: 10+)")
        else:
            verdict = StrategyVerdict.VALID.value

        return StrategyCandidate(
            strategy=strategy,
            window_size=window_size,
            score=round(composite, 4),
            expected_windows=estimated_windows,
            expected_obs_per_window=round(estimated_obs_per_window, 1),
            expected_detector_readiness=expected_readiness,
            verdict=verdict,
            notes=notes,
        )

    def _estimate_windows(
        self,
        profile: RepositoryProfile,
        strategy: str,
        window_size: int,
    ) -> Tuple[int, float]:
        """Estimate number of windows and observations per window.

        Uses M-02 observation count for commit_count strategy (the builder
        creates boundaries from M-02 observations, not all observations).

        Returns:
            (estimated_windows, estimated_obs_per_window)
        """
        if profile.observation_count == 0:
            return 0, 0.0

        if strategy == "commit_count":
            # The builder uses M-02 observations for commit boundaries
            m02_count = profile.m02_observation_count if profile.m02_observation_count > 0 else profile.commit_count
            estimated_windows = max(1, m02_count // window_size)
            estimated_obs_per_window = profile.observation_count / estimated_windows if estimated_windows > 0 else 0.0
        elif strategy == "temporal":
            # Windows = repo_age_days / window_size
            if profile.repo_age_days <= 0:
                estimated_windows = 1
            else:
                estimated_windows = max(1, profile.repo_age_days // window_size)
            estimated_obs_per_window = profile.observation_count / estimated_windows if estimated_windows > 0 else 0.0
        elif strategy == "hybrid":
            # Hybrid: start with temporal, estimate merging
            if profile.repo_age_days <= 0:
                estimated_windows = 1
            else:
                estimated_windows = max(1, profile.repo_age_days // window_size)
            # Merging reduces windows by ~30% on average
            estimated_windows = max(1, int(estimated_windows * 0.7))
            estimated_obs_per_window = profile.observation_count / estimated_windows if estimated_windows > 0 else 0.0
        else:
            estimated_windows = 1
            estimated_obs_per_window = float(profile.observation_count)

        return estimated_windows, estimated_obs_per_window

    def _score_observation_density(
        self,
        profile: RepositoryProfile,
        estimated_obs_per_window: float,
        notes: List[str],
    ) -> float:
        """Score how well observations are distributed into windows.

        Target: 20-50 observations per window for statistical power.
        """
        if estimated_obs_per_window <= 0:
            return 0.0

        # Sweet spot: 20-50 obs per window
        if 20 <= estimated_obs_per_window <= 50:
            score = 1.0
        elif 10 <= estimated_obs_per_window < 20:
            score = 0.7 + 0.3 * (estimated_obs_per_window - 10) / 10
        elif 50 < estimated_obs_per_window <= 100:
            score = 0.8 + 0.2 * (100 - estimated_obs_per_window) / 50
        elif estimated_obs_per_window < 10:
            score = max(0.0, estimated_obs_per_window / 10 * 0.7)
            notes.append(f"Low observation density: {estimated_obs_per_window:.0f} obs/window")
        else:
            score = 0.6
            notes.append(f"High observation density: {estimated_obs_per_window:.0f} obs/window")

        return score

    def _score_window_balance(
        self,
        profile: RepositoryProfile,
        estimated_windows: int,
        notes: List[str],
    ) -> float:
        """Score how balanced windows are likely to be.

        Uses the repository's existing window balance as a proxy.
        """
        if estimated_windows <= 1:
            return 0.5

        # Use the profile's window balance as a proxy
        balance = profile.window_balance

        # Penalize very few windows
        if estimated_windows < 3:
            balance *= 0.8
            notes.append(f"Only {estimated_windows} estimated windows")

        return min(1.0, max(0.0, balance))

    def _score_detector_readiness(
        self,
        estimated_obs_per_window: float,
        estimated_windows: int,
        profile: RepositoryProfile,
        notes: List[str],
    ) -> Tuple[float, Dict[str, str]]:
        """Score expected detector readiness.

        Returns:
            (score, expected_readiness_per_detector)
        """
        readiness: Dict[str, str] = {}
        scores: List[float] = []

        for det_id, reqs in _DETECTOR_REQUIREMENTS.items():
            obs_ok = estimated_obs_per_window >= reqs["obs_per_window"]
            windows_ok = estimated_windows >= reqs["windows"]
            metrics_ok = len(profile.metrics_available) >= reqs["metrics"]

            if obs_ok and windows_ok and metrics_ok:
                readiness[det_id] = ReadinessState.READY.value
                scores.append(1.0)
            elif windows_ok and metrics_ok and estimated_obs_per_window >= reqs["obs_per_window"] * 0.7:
                readiness[det_id] = ReadinessState.PARTIAL.value
                scores.append(0.5)
                notes.append(
                    f"{det_id} PARTIAL: ~{estimated_obs_per_window:.0f} obs " f"(need {reqs['obs_per_window']})"
                )
            else:
                readiness[det_id] = ReadinessState.SKIPPED.value
                scores.append(0.0)
                skip_parts = []
                if not obs_ok:
                    skip_parts.append(f"obs={estimated_obs_per_window:.0f}<{reqs['obs_per_window']}")
                if not windows_ok:
                    skip_parts.append(f"windows={estimated_windows}<{reqs['windows']}")
                if not metrics_ok:
                    skip_parts.append(f"metrics={len(profile.metrics_available)}<{reqs['metrics']}")
                notes.append(f"{det_id} SKIPPED: {', '.join(skip_parts)}")

        avg_score = sum(scores) / len(scores) if scores else 0.0
        return avg_score, readiness

    def _score_sample_adequacy(
        self,
        estimated_obs_per_window: float,
        estimated_windows: int,
        notes: List[str],
    ) -> float:
        """Score whether the sample size is adequate for statistical inference.

        Target: at least 10 obs per window, at least 2 windows.
        """
        if estimated_windows < 2:
            return 0.0

        # Adequacy = min(1.0, obs_per_window / 20) * min(1.0, windows / 5)
        obs_factor = min(1.0, estimated_obs_per_window / 20)
        window_factor = min(1.0, estimated_windows / 5)

        return obs_factor * window_factor

    def _score_coverage(
        self,
        profile: RepositoryProfile,
        strategy: str,
        window_size: int,
        estimated_windows: int,
        notes: List[str],
    ) -> float:
        """Score how well the strategy covers the repository history.

        Coverage = fraction of repository age that is analyzed.
        """
        if profile.repo_age_days <= 0:
            return 1.0

        if strategy == "commit_count":
            # Coverage depends on how many commits are included
            analyzed_commits = min(profile.commit_count, estimated_windows * window_size)
            coverage = analyzed_commits / profile.commit_count if profile.commit_count > 0 else 0.0
        elif strategy == "temporal":
            analyzed_days = estimated_windows * window_size
            coverage = min(1.0, analyzed_days / profile.repo_age_days)
        else:
            coverage = 1.0

        return min(1.0, max(0.0, coverage))
