"""
MIIE v1.5 Scientific Readiness Certification — Verdict Interpreter (PR-7C-3).

Interprets detector readiness into per-detector verdicts and computes
aggregate repository certification.

Reference: PR-7C-3, OEAS SS21, DES v2.0
"""

from __future__ import annotations

import logging
from typing import List, Optional

from miie.sampling.models import (
    ReadinessReport,
    SamplingDiagnostics,
)

from .models import DetectorVerdict, RepositoryCertification

logger = logging.getLogger(__name__)


class VerdictInterpreter:
    """Interprets detector readiness into verdicts (PR-7C-3).

    Responsibilities:
    - Convert ReadinessReport into per-detector DetectorVerdicts
    - Compute repository-level certification
    - Provide human-readable recommendations
    """

    def interpret_readiness(
        self,
        readiness: Optional[ReadinessReport],
    ) -> Tuple[DetectorVerdict, ...]:
        """Interpret readiness report into per-detector verdicts.

        Args:
            readiness: ReadinessReport from DetectorReadinessAnalyzer.

        Returns:
            Tuple of DetectorVerdict for each detector.
        """
        if readiness is None:
            return ()

        verdicts: List[DetectorVerdict] = []
        for r in readiness.detector_readiness:
            verdicts.append(
                DetectorVerdict(
                    detector_id=r.detector_id,
                    state=r.state,
                    confidence=r.execution_confidence,
                    observation_count=sum(r.actual_obs_per_window.values()) if r.actual_obs_per_window else 0,
                    window_count=r.actual_windows,
                    min_obs_per_window=min(r.actual_obs_per_window.values()) if r.actual_obs_per_window else 0,
                    skip_reason=r.skip_reason,
                    recommendation=r.recommendation,
                )
            )

        return tuple(verdicts)

    def certify_repo(
        self,
        repo_id: str,
        repo_name: str,
        detector_verdicts: tuple,
        sampling_diagnostics: SamplingDiagnostics,
    ) -> RepositoryCertification:
        """Compute repository certification from detector verdicts.

        Args:
            repo_id: Repository identifier.
            repo_name: Human-readable name.
            detector_verdicts: Per-detector verdicts.
            sampling_diagnostics: Full sampling diagnostics.

        Returns:
            RepositoryCertification with verdict and confidence.
        """
        if not detector_verdicts:
            return RepositoryCertification(
                repo_id=repo_id,
                repo_name=repo_name,
                verdict="SKIPPED",
                overall_confidence=0.0,
                warnings=["No detector verdicts available"],
            )

        # Determine verdict
        states = [v.state for v in detector_verdicts]
        ready_count = sum(1 for s in states if s == "READY")
        partial_count = sum(1 for s in states if s == "PARTIAL")
        skipped_count = sum(1 for s in states if s == "SKIPPED")

        if ready_count == len(states):
            verdict = "READY"
        elif ready_count + partial_count == len(states):
            verdict = "PARTIAL"
        elif skipped_count == len(states):
            verdict = "SKIPPED"
        else:
            verdict = "PARTIAL"

        # Compute overall confidence (weighted by detector importance)
        confidences = [v.confidence for v in detector_verdicts]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Apply penalty for low window count
        ws = sampling_diagnostics.window_diagnostics if sampling_diagnostics else []
        warnings: List[str] = []
        if sampling_diagnostics and sampling_diagnostics.total_windows < 5:
            warnings.append(f"Only {sampling_diagnostics.total_windows} windows produced")

        # Get prediction error from plan
        prediction_error = 0.0
        if sampling_diagnostics and sampling_diagnostics.plan:
            prediction_error = sampling_diagnostics.plan.prediction_error

        return RepositoryCertification(
            repo_id=repo_id,
            repo_name=repo_name,
            verdict=verdict,
            overall_confidence=round(overall_confidence, 4),
            detector_verdicts=detector_verdicts,
            strategy_used=sampling_diagnostics.strategy_used if sampling_diagnostics else "",
            window_count=sampling_diagnostics.total_windows if sampling_diagnostics else 0,
            observation_count=sampling_diagnostics.total_observations if sampling_diagnostics else 0,
            prediction_error=prediction_error,
            warnings=warnings,
        )


# Need to import Tuple for type annotation
from typing import Tuple
