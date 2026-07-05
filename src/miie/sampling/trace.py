"""
MIIE v1.5 Sampling Framework — Execution Tracer.

Generates deterministic execution traces for every detector decision.
Every detector execution or skip becomes a structured, explainable trace.

Reference: PR-7B Phase 5, DES v2.0
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from miie.processing.observation.models import ObservationWindow

from .models import (
    DetectorReadiness,
    ExecutionTrace,
    ReadinessReport,
    ReadinessState,
    SamplingPlan,
)

logger = logging.getLogger(__name__)

# Statistical tests per detector
_DETECTOR_TESTS: Dict[str, Tuple[str, ...]] = {
    "D-01": ("kolmogorov_smirnov", "psi"),
    "D-02": ("pearson_r", "spearman_rho", "fisher_z_ci"),
    "D-03": ("excess_mass", "dip_test"),
}


class ExecutionTracer:
    """Generates structured execution traces for every detector decision.

    The tracer records:
    - What was available (observations, windows, metrics)
    - What was required (detector thresholds)
    - What decision was made (execute, skip, partial)
    - Why the decision was made (exact failing condition)
    - What happened (execution time, tests invoked, evidence generated)
    """

    def trace(
        self,
        readiness: ReadinessReport,
        windows: List[ObservationWindow],
        plan: SamplingPlan,
    ) -> Tuple[ExecutionTrace, ...]:
        """Generate execution traces from readiness analysis.

        Args:
            readiness: DetectorReadinessReport from the readiness analyzer.
            windows: ObservationWindows produced by the adaptive builder.
            plan: The SamplingPlan used.

        Returns:
            Tuple of ExecutionTrace, one per detector.
        """
        traces: List[ExecutionTrace] = []

        for det_readiness in readiness.detector_readiness:
            trace = self._build_trace(det_readiness, windows, plan)
            traces.append(trace)

        return tuple(traces)

    def trace_execution(
        self,
        traces: Tuple[ExecutionTrace, ...],
        detector_results: Dict[str, Any],
        execution_times: Optional[Dict[str, float]] = None,
    ) -> Tuple[ExecutionTrace, ...]:
        """Update traces after detector execution with actual results.

        Args:
            traces: Pre-execution traces from trace().
            detector_results: Detector outputs from the dispatcher.
            execution_times: Per-detector execution times in seconds.

        Returns:
            Updated traces with execution results.
        """
        updated: List[ExecutionTrace] = []
        execution_times = execution_times or {}

        for trace in traces:
            det_id = trace.detector_id
            det_output = detector_results.get(det_id, {})

            # Check if detector actually produced output
            has_output = bool(det_output) and det_output != {"status": "skipped"}

            # Get execution time
            exec_time = execution_times.get(det_id, 0.0)

            # Determine which tests were invoked
            if has_output and trace.readiness_state != ReadinessState.SKIPPED.value:
                tests_invoked = _DETECTOR_TESTS.get(det_id, ())
                evidence_generated = True
            else:
                tests_invoked = ()
                evidence_generated = False

            # Update trace
            updated.append(
                ExecutionTrace(
                    detector_id=det_id,
                    observation_count=trace.observation_count,
                    window_count=trace.window_count,
                    sample_size=trace.sample_size,
                    required_sample=trace.required_sample,
                    readiness_state=trace.readiness_state,
                    execution_decision="executed" if has_output else trace.execution_decision,
                    execution_time_seconds=exec_time,
                    statistical_tests_invoked=tests_invoked,
                    evidence_generated=evidence_generated,
                    skip_reason=trace.skip_reason,
                    notes=trace.notes,
                )
            )

        return tuple(updated)

    def _build_trace(
        self,
        readiness: DetectorReadiness,
        windows: List[ObservationWindow],
        plan: SamplingPlan,
    ) -> ExecutionTrace:
        """Build a single execution trace from readiness analysis."""
        det_id = readiness.detector_id

        # Compute sample sizes
        total_obs = sum(w.observation_count for w in windows)
        min_obs_per_window = min(readiness.actual_obs_per_window.values()) if readiness.actual_obs_per_window else 0

        # Required sample depends on detector
        if det_id == "D-01":
            required_sample = readiness.required_obs_per_window * readiness.required_windows
        elif det_id == "D-02":
            required_sample = readiness.required_obs_per_window * readiness.required_windows
        elif det_id == "D-03":
            required_sample = readiness.required_obs_per_window
        else:
            required_sample = 0

        actual_sample = min_obs_per_window

        # Determine execution decision
        if readiness.state == ReadinessState.READY.value:
            decision = "execute"
        elif readiness.state == ReadinessState.PARTIAL.value:
            decision = "partial_execute"
        elif readiness.state == ReadinessState.SKIPPED.value:
            decision = "skip"
        else:
            decision = "not_applicable"

        # Build notes
        notes: List[str] = []
        if readiness.state == ReadinessState.PARTIAL.value:
            notes.append(f"Detector may produce reduced output: {readiness.skip_reason}")
        if plan.chosen.score < 0.5:
            notes.append("Strategy score is low; results may have limited power")

        return ExecutionTrace(
            detector_id=det_id,
            observation_count=total_obs,
            window_count=readiness.actual_windows,
            sample_size=actual_sample,
            required_sample=required_sample,
            readiness_state=readiness.state,
            execution_decision=decision,
            execution_time_seconds=0.0,
            statistical_tests_invoked=(),
            evidence_generated=False,
            skip_reason=readiness.skip_reason,
            notes=notes,
        )
