"""
MIIE v1.5 Sampling Framework — Canonical Data Models.

Defines all data structures for repository profiling, strategy evaluation,
detector readiness analysis, and execution tracing.

Reference: PR-7B, OEAS SS21, DES v2.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ActivityClass(str, Enum):
    """Repository activity classification based on commit density."""

    INACTIVE = "inactive"
    SPARSE = "sparse"
    MODERATE = "moderate"
    ACTIVE = "active"
    HIGHLY_ACTIVE = "highly_active"


class RepositoryScale(str, Enum):
    """Repository scale classification based on total observations."""

    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    MASSIVE = "massive"


class VolatilityClass(str, Enum):
    """Repository volatility classification based on coefficient of variation."""

    STABLE = "stable"
    MODERATE = "moderate"
    VOLATILE = "volatile"


class ReadinessState(str, Enum):
    """Detector readiness classification (PR-7B Phase 4)."""

    READY = "READY"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class StrategyVerdict(str, Enum):
    """Strategy evaluation verdict."""

    VALID = "VALID"
    MARGINAL = "MARGINAL"
    INVALID = "INVALID"


# ---------------------------------------------------------------------------
# Repository Profile (PR-7B Phase 1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RepositoryProfile:
    """Repository profiling data computed from observations.

    All fields are deterministic given the same input observations.

    Attributes:
        commit_count: Total number of commits in the analyzed history.
        repo_age_days: Age of the repository in days (last - first commit).
        observation_count: Total number of observations extracted.
        observation_density: observations / repo_age_days (or 0 if age is 0).
        commit_density: commits / repo_age_days (or 0 if age is 0).
        avg_commits_per_day: Alias for commit_density.
        window_density: Estimated observations per window for default strategy.
        avg_obs_per_window: Mean observations across candidate window configurations.
        min_obs_per_window: Minimum observations in any candidate window.
        max_obs_per_window: Maximum observations in any candidate window.
        median_obs_per_window: Median observations across candidate windows.
        variance: Variance of observation counts across windows.
        cv: Coefficient of variation (std / mean) of observation counts.
        window_balance: 1.0 - min(1.0, std / mean) of observation counts.
        activity_class: Repository activity classification.
        scale: Repository scale classification.
        volatility: Repository volatility classification.
        metrics_available: List of metric IDs present in observations.
        time_span_days: Span of observation timestamps in days.
        m02_observation_count: Count of M-02 (commit frequency) observations.
            Used for accurate commit_count window estimation (the builder only
            uses M-02 observations for commit boundaries, not all observations).
    """

    commit_count: int
    repo_age_days: int
    observation_count: int
    observation_density: float
    commit_density: float
    avg_commits_per_day: float
    window_density: float
    avg_obs_per_window: float
    min_obs_per_window: int
    max_obs_per_window: int
    median_obs_per_window: float
    variance: float
    cv: float
    window_balance: float
    activity_class: str
    scale: str
    volatility: str
    metrics_available: Tuple[str, ...]
    time_span_days: int
    m02_observation_count: int = 0


# ---------------------------------------------------------------------------
# Strategy Candidate (PR-7B Phase 2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StrategyCandidate:
    """A candidate windowing strategy with its evaluation score.

    Attributes:
        strategy: Strategy name ('temporal', 'commit_count', 'hybrid').
        window_size: Size parameter (days for temporal, commits for commit_count).
        score: Composite score in [0.0, 1.0]. Higher is better.
        expected_windows: Estimated number of windows this strategy produces.
        expected_obs_per_window: Estimated observations per window.
        expected_detector_readiness: Per-detector expected readiness states.
        verdict: Whether this strategy is VALID, MARGINAL, or INVALID.
        notes: Human-readable evaluation notes.
    """

    strategy: str
    window_size: int
    score: float
    expected_windows: int
    expected_obs_per_window: float
    expected_detector_readiness: Dict[str, str] = field(default_factory=dict)
    verdict: str = "VALID"
    notes: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Sampling Plan (PR-7B Phase 2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SamplingPlan:
    """Complete sampling plan produced by the Sampling Planner.

    Attributes:
        chosen: The selected strategy candidate.
        alternatives: Other evaluated candidates, sorted by score descending.
        rejected: Candidates that failed validation.
        scientific_confidence: Confidence level ('high', 'medium', 'low').
        selection_rationale: Why this strategy was chosen.
        planning_notes: Additional planning diagnostics.
        profile: The repository profile used for planning.
    """

    chosen: StrategyCandidate
    alternatives: Tuple[StrategyCandidate, ...] = ()
    rejected: Tuple[StrategyCandidate, ...] = ()
    scientific_confidence: str = "medium"
    selection_rationale: str = ""
    planning_notes: List[str] = field(default_factory=list)
    profile: Optional[RepositoryProfile] = None
    # Calibration fields (PR-7C-1): planner prediction vs actual builder output
    prediction_error: float = 0.0
    window_difference: int = 0
    observation_difference: float = 0.0
    confidence_adjustment: float = 0.0


# ---------------------------------------------------------------------------
# Detector Readiness (PR-7B Phase 4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DetectorReadiness:
    """Per-detector readiness analysis.

    Attributes:
        detector_id: Detector identifier (e.g., 'D-01').
        state: Readiness state (READY, PARTIAL, SKIPPED, NOT_APPLICABLE).
        required_obs_per_window: Minimum observations per window for this detector.
        actual_obs_per_window: Actual observations per window (window_id -> count).
        required_windows: Minimum number of windows needed.
        actual_windows: Actual number of windows available.
        required_metrics: Minimum number of metrics needed.
        actual_metrics: Actual number of metrics available.
        required_metric_pairs: Minimum number of metric pairs needed (for D-02).
        actual_metric_pairs: Actual metric pairs available.
        skip_reason: If skipped, the exact statistical assumption that failed.
        execution_confidence: Confidence in detector execution in [0.0, 1.0].
        recommendation: Suggested action to enable this detector.
        scientific_validity: Assessment of scientific validity.
    """

    detector_id: str
    state: str
    required_obs_per_window: int
    actual_obs_per_window: Dict[str, int] = field(default_factory=dict)
    required_windows: int = 0
    actual_windows: int = 0
    required_metrics: int = 0
    actual_metrics: int = 0
    required_metric_pairs: int = 0
    actual_metric_pairs: int = 0
    skip_reason: str = ""
    execution_confidence: float = 0.0
    recommendation: str = ""
    scientific_validity: str = ""


# ---------------------------------------------------------------------------
# Readiness Report (PR-7B Phase 4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReadinessReport:
    """Complete readiness report for all detectors.

    Attributes:
        detector_readiness: Per-detector readiness analyses.
        overall_state: Overall readiness (READY if all READY, PARTIAL if any PARTIAL, etc.).
        ready_count: Number of detectors in READY state.
        partial_count: Number of detectors in PARTIAL state.
        skipped_count: Number of detectors in SKIPPED state.
        not_applicable_count: Number of detectors in NOT_APPLICABLE state.
    """

    detector_readiness: Tuple[DetectorReadiness, ...] = ()
    overall_state: str = "READY"
    ready_count: int = 0
    partial_count: int = 0
    skipped_count: int = 0
    not_applicable_count: int = 0


# ---------------------------------------------------------------------------
# Execution Trace (PR-7B Phase 5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionTrace:
    """Per-detector execution trace.

    Attributes:
        detector_id: Detector identifier.
        observation_count: Total observations available.
        window_count: Total windows available.
        sample_size: Actual sample size used.
        required_sample: Minimum sample size required.
        readiness_state: Readiness state at time of trace.
        execution_decision: Whether the detector will execute.
        execution_time_seconds: Time taken (0.0 if not yet executed).
        statistical_tests_invoked: List of statistical tests that were invoked.
        evidence_generated: Whether evidence was produced.
        skip_reason: If skipped, the exact reason.
        notes: Additional trace notes.
    """

    detector_id: str
    observation_count: int
    window_count: int
    sample_size: int
    required_sample: int
    readiness_state: str
    execution_decision: str
    execution_time_seconds: float = 0.0
    statistical_tests_invoked: Tuple[str, ...] = ()
    evidence_generated: bool = False
    skip_reason: str = ""
    notes: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Window Diagnostics (PR-7B Phase 6)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WindowDiagnostics:
    """Diagnostics for a single window after adaptive building.

    Attributes:
        window_id: Window identifier.
        observation_count: Number of observations in this window.
        metrics_present: Metrics present in this window.
        meets_d01_threshold: Whether this window meets D-01 minimum (10 obs).
        meets_d02_threshold: Whether this window meets D-02 minimum (10 paired obs).
        meets_d03_threshold: Whether this window meets D-03 minimum (20 obs).
        mean_value: Mean observation value.
        std_value: Standard deviation of observation values.
    """

    window_id: str
    observation_count: int
    metrics_present: Tuple[str, ...] = ()
    meets_d01_threshold: bool = False
    meets_d02_threshold: bool = False
    meets_d03_threshold: bool = False
    mean_value: float = 0.0
    std_value: float = 0.0


# ---------------------------------------------------------------------------
# Sampling Diagnostics (PR-7B Phase 6)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SamplingDiagnostics:
    """Complete diagnostics for the sampling pipeline.

    Attributes:
        profile: Repository profile.
        plan: Sampling plan.
        window_diagnostics: Per-window diagnostics.
        readiness: Detector readiness report.
        execution_traces: Per-detector execution traces.
        strategy_used: Strategy used for window building.
        total_windows: Total windows produced.
        total_observations: Total observations placed.
        unassigned_observations: Observations not placed in any window.
        warnings: Diagnostic warnings.
    """

    profile: Optional[RepositoryProfile] = None
    plan: Optional[SamplingPlan] = None
    window_diagnostics: Tuple[WindowDiagnostics, ...] = ()
    readiness: Optional[ReadinessReport] = None
    execution_traces: Tuple[ExecutionTrace, ...] = ()
    strategy_used: str = ""
    total_windows: int = 0
    total_observations: int = 0
    unassigned_observations: int = 0
    warnings: List[str] = field(default_factory=list)
