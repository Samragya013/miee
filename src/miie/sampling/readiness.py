"""
MIIE v1.5 Sampling Framework — Detector Readiness Analyzer.

Analyzes whether each detector can execute given the current window
configuration. Produces deterministic readiness reports with precise
skip reasons.

Reference: PR-7B Phase 4, DES v2.0
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from miie.processing.observation.models import ObservationWindow

from .models import (
    DetectorReadiness,
    ReadinessReport,
    ReadinessState,
    SamplingPlan,
    WindowDiagnostics,
)

logger = logging.getLogger(__name__)

# Detector minimum requirements (immutable, from DES v2.0)
_DETECTOR_REQUIREMENTS: Dict[str, Dict[str, int]] = {
    "D-01": {"obs_per_window": 10, "windows": 2, "metrics": 1},
    "D-02": {"obs_per_window": 10, "windows": 2, "metrics": 2},
    "D-03": {"obs_per_window": 20, "windows": 1, "metrics": 1},
}

# Statistical tests per detector
_DETECTOR_TESTS: Dict[str, Tuple[str, ...]] = {
    "D-01": ("kolmogorov_smirnov", "psi"),
    "D-02": ("pearson_r", "spearman_rho", "fisher_z_ci"),
    "D-03": ("excess_mass", "dip_test"),
}


class DetectorReadinessAnalyzer:
    """Analyzes detector readiness before execution.

    For each detector, computes:
    - Required vs actual observations, windows, metrics
    - Expected execution decision
    - Precise skip reason if applicable
    - Scientific validity assessment
    """

    def analyze(
        self,
        windows: List[ObservationWindow],
        plan: SamplingPlan,
        window_diagnostics: Optional[List[WindowDiagnostics]] = None,
    ) -> ReadinessReport:
        """Analyze readiness for all detectors.

        Args:
            windows: ObservationWindows produced by the AdaptiveWindowBuilder.
            plan: The SamplingPlan used.
            window_diagnostics: Optional per-window diagnostics.

        Returns:
            ReadinessReport with per-detector readiness.
        """
        readiness_list: List[DetectorReadiness] = []

        for det_id in ("D-01", "D-02", "D-03"):
            readiness = self._analyze_detector(det_id, windows, plan, window_diagnostics)
            readiness_list.append(readiness)

        # Compute overall state
        states = [r.state for r in readiness_list]
        if all(s == ReadinessState.READY.value for s in states):
            overall = ReadinessState.READY.value
        elif any(s == ReadinessState.SKIPPED.value for s in states):
            overall = ReadinessState.PARTIAL.value
        else:
            overall = ReadinessState.PARTIAL.value

        return ReadinessReport(
            detector_readiness=tuple(readiness_list),
            overall_state=overall,
            ready_count=sum(1 for s in states if s == ReadinessState.READY.value),
            partial_count=sum(1 for s in states if s == ReadinessState.PARTIAL.value),
            skipped_count=sum(1 for s in states if s == ReadinessState.SKIPPED.value),
            not_applicable_count=sum(1 for s in states if s == ReadinessState.NOT_APPLICABLE.value),
        )

    def _analyze_detector(
        self,
        det_id: str,
        windows: List[ObservationWindow],
        plan: SamplingPlan,
        window_diagnostics: Optional[List[WindowDiagnostics]] = None,
    ) -> DetectorReadiness:
        """Analyze readiness for a single detector."""
        reqs = _DETECTOR_REQUIREMENTS[det_id]

        # Compute actual values
        actual_windows = len(windows)
        obs_per_window = {w.window_id: w.observation_count for w in windows}

        # Metrics available across all windows
        all_metrics: set = set()
        for w in windows:
            all_metrics.update(w.metrics_present)
        actual_metrics = len(all_metrics)

        # Metric pairs (for D-02)
        actual_metric_pairs = 0
        if actual_metrics >= 2:
            actual_metric_pairs = (actual_metrics * (actual_metrics - 1)) // 2

        # Minimum observations across windows
        min_obs = min(obs_per_window.values()) if obs_per_window else 0
        _avg_obs = sum(obs_per_window.values()) / len(obs_per_window) if obs_per_window else 0

        # Check requirements
        obs_ok = min_obs >= reqs["obs_per_window"]
        windows_ok = actual_windows >= reqs["windows"]
        metrics_ok = actual_metrics >= reqs["metrics"]

        # Determine state and skip reason
        skip_parts: List[str] = []
        if not obs_ok:
            skip_parts.append(f"minimum observations per window is {min_obs} " f"(required: {reqs['obs_per_window']})")
        if not windows_ok:
            skip_parts.append(f"only {actual_windows} window(s) " f"(required: {reqs['windows']})")
        if not metrics_ok:
            skip_parts.append(f"only {actual_metrics} metric(s) " f"(required: {reqs['metrics']})")

        # For D-02, also check metric pairs
        if det_id == "D-02" and actual_metric_pairs < 1:
            skip_parts.append("no metric pairs available " "(need at least 2 metrics for correlation)")

        if not skip_parts:
            # All requirements met
            state = ReadinessState.READY.value
            skip_reason = ""
            confidence = 1.0
            recommendation = ""
            validity = "statistically_valid"
        elif windows_ok and metrics_ok and min_obs >= reqs["obs_per_window"] * 0.7:
            # Partially met
            state = ReadinessState.PARTIAL.value
            skip_reason = "; ".join(skip_parts)
            confidence = 0.5
            recommendation = f"Increase observations per window to {reqs['obs_per_window']} " f"(currently {min_obs})"
            validity = "marginal"
        else:
            # Not met
            state = ReadinessState.SKIPPED.value
            skip_reason = "; ".join(skip_parts)
            confidence = 0.0
            recommendation = self._build_recommendation(det_id, min_obs, actual_windows, actual_metrics)
            validity = "insufficient_data"

        # Special case: D-03 only needs 1 window
        if det_id == "D-03" and actual_windows >= 1 and min_obs >= 20:
            state = ReadinessState.READY.value
            skip_reason = ""
            confidence = 1.0
            recommendation = ""
            validity = "statistically_valid"

        return DetectorReadiness(
            detector_id=det_id,
            state=state,
            required_obs_per_window=reqs["obs_per_window"],
            actual_obs_per_window=obs_per_window,
            required_windows=reqs["windows"],
            actual_windows=actual_windows,
            required_metrics=reqs["metrics"],
            actual_metrics=actual_metrics,
            required_metric_pairs=1 if det_id == "D-02" else 0,
            actual_metric_pairs=actual_metric_pairs,
            skip_reason=skip_reason,
            execution_confidence=confidence,
            recommendation=recommendation,
            scientific_validity=validity,
        )

    def _build_recommendation(
        self,
        det_id: str,
        min_obs: int,
        actual_windows: int,
        actual_metrics: int,
    ) -> str:
        """Build a specific recommendation to enable this detector."""
        reqs = _DETECTOR_REQUIREMENTS[det_id]
        parts = []

        if min_obs < reqs["obs_per_window"]:
            deficit = reqs["obs_per_window"] - min_obs
            parts.append(
                f"Need {deficit} more observations per window "
                f"(currently {min_obs}, required {reqs['obs_per_window']})"
            )
        if actual_windows < reqs["windows"]:
            parts.append(
                f"Need {reqs['windows'] - actual_windows} more window(s) "
                f"(currently {actual_windows}, required {reqs['windows']})"
            )
        if actual_metrics < reqs["metrics"]:
            parts.append(
                f"Need {reqs['metrics'] - actual_metrics} more metric(s) "
                f"(currently {actual_metrics}, required {reqs['metrics']})"
            )

        return "; ".join(parts) if parts else ""
