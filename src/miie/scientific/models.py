"""
MIIE v1.5 Scientific Readiness Certification — Data Models (PR-7C-3).

Defines all data structures for per-repository execution reports,
detector verdicts, and aggregate certification.

Reference: PR-7C-3, OEAS SS21, DES v2.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Detector Verdict (PR-7C-3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DetectorVerdict:
    """Per-detector verdict for a single repository.

    Attributes:
        detector_id: Detector identifier (D-01, D-02, D-03).
        state: Execution state (READY, PARTIAL, SKIPPED, NOT_APPLICABLE).
        confidence: Execution confidence in [0.0, 1.0].
        observation_count: Total observations available.
        window_count: Total windows available.
        min_obs_per_window: Minimum observations across windows.
        skip_reason: Precise skip reason if SKIPPED.
        recommendation: Suggested action to enable detector.
    """

    detector_id: str
    state: str
    confidence: float
    observation_count: int = 0
    window_count: int = 0
    min_obs_per_window: int = 0
    skip_reason: str = ""
    recommendation: str = ""


# ---------------------------------------------------------------------------
# Repository Certification (PR-7C-3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RepositoryCertification:
    """Certification result for a single repository.

    Attributes:
        repo_id: Repository identifier (e.g., 'A-02').
        repo_name: Human-readable repository name.
        verdict: Certification verdict (READY, PARTIAL, SKIPPED).
        overall_confidence: Aggregate confidence across all detectors.
        detector_verdicts: Per-detector verdicts.
        strategy_used: Sampling strategy that was applied.
        window_count: Total windows produced.
        observation_count: Total observations placed.
        prediction_error: Planner prediction error for this repo.
        warnings: Any warnings produced during certification.
    """

    repo_id: str
    repo_name: str
    verdict: str
    overall_confidence: float
    detector_verdicts: Tuple[DetectorVerdict, ...] = ()
    strategy_used: str = ""
    window_count: int = 0
    observation_count: int = 0
    prediction_error: float = 0.0
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scientific Execution Report (PR-7C-3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScientificExecutionReport:
    """Complete execution report for one repository.

    Produced by ScientificReadinessEngine. Contains the full audit trail
    from sampling diagnostics through detector readiness to final verdict.

    Attributes:
        repo_id: Repository identifier.
        repo_name: Human-readable repository name.
        certification: The certification result.
        sampling_diagnostics_raw: Raw sampling diagnostics dict (for JSON export).
        detector_summary: Summary dict mapping detector_id -> state string.
        is_valid: Whether this repo passed scientific readiness.
    """

    repo_id: str
    repo_name: str
    certification: RepositoryCertification
    sampling_diagnostics_raw: Dict = field(default_factory=dict)
    detector_summary: Dict[str, str] = field(default_factory=dict)
    is_valid: bool = False


# ---------------------------------------------------------------------------
# Aggregate Certification (PR-7C-3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AggregateCertification:
    """Aggregate certification across all analyzed repositories.

    Attributes:
        total_repos: Total repositories analyzed.
        ready_count: Repositories with READY verdict.
        partial_count: Repositories with PARTIAL verdict.
        skipped_count: Repositories with SKIPPED verdict.
        failed_count: Repositories that failed analysis.
        overall_verdict: Aggregate verdict (READY if all READY, etc.).
        overall_confidence: Mean confidence across all repos.
        certifications: Per-repository certifications.
        warnings: Aggregate warnings.
    """

    total_repos: int = 0
    ready_count: int = 0
    partial_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    overall_verdict: str = "NOT_ASSESSED"
    overall_confidence: float = 0.0
    certifications: Tuple[RepositoryCertification, ...] = ()
    warnings: List[str] = field(default_factory=list)
