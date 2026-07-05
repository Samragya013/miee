"""
MIIE v1.5 Sampling Framework — Diagnostics Engine.

Produces complete diagnostic output for the sampling pipeline:
repository profile, sampling plan, window diagnostics, readiness,
execution traces, and a unified reasoning chain.

Reference: PR-7B Phase 6, OEAS SS21
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from miie.processing.observation.models import ObservationCollection

from .adaptive_window import AdaptiveWindowBuilder
from .models import (
    SamplingDiagnostics,
)
from .planner import SamplingPlanner
from .readiness import DetectorReadinessAnalyzer
from .trace import ExecutionTracer

logger = logging.getLogger(__name__)


class DiagnosticsEngine:
    """Orchestrates the complete sampling pipeline and produces diagnostics.

    Pipeline:
    1. SamplingPlanner.profile() -> RepositoryProfile
    2. SamplingPlanner.plan() -> SamplingPlan
    3. AdaptiveWindowBuilder.build() -> WindowBuilderResult + WindowDiagnostics
    4. DetectorReadinessAnalyzer.analyze() -> ReadinessReport
    5. ExecutionTracer.trace() -> ExecutionTraces
    6. Assemble SamplingDiagnostics
    """

    def __init__(self) -> None:
        self._planner = SamplingPlanner()
        self._window_builder = AdaptiveWindowBuilder()
        self._readiness_analyzer = DetectorReadinessAnalyzer()
        self._execution_tracer = ExecutionTracer()

    def run(
        self,
        collection: ObservationCollection,
    ) -> SamplingDiagnostics:
        """Run the complete sampling diagnostics pipeline.

        Args:
            collection: ObservationCollection containing all observations.

        Returns:
            SamplingDiagnostics with complete pipeline output.
        """
        warnings: List[str] = []

        # Phase 1-2: Profile and plan
        plan = self._planner.plan(collection)
        profile = plan.profile

        if profile is None:
            warnings.append("Could not compute repository profile")
            return SamplingDiagnostics(warnings=warnings)

        # Phase 3: Build windows
        window_result, window_diags = self._window_builder.build(collection, plan)

        if not window_result.windows:
            warnings.append("No windows produced by adaptive builder")

        # Phase 4: Analyze readiness
        readiness = self._readiness_analyzer.analyze(window_result.windows, plan, window_diags)

        # Phase 5: Trace
        traces = self._execution_tracer.trace(readiness, window_result.windows, plan)

        return SamplingDiagnostics(
            profile=profile,
            plan=plan,
            window_diagnostics=tuple(window_diags),
            readiness=readiness,
            execution_traces=traces,
            strategy_used=plan.chosen.strategy,
            total_windows=len(window_result.windows),
            total_observations=sum(w.observation_count for w in window_result.windows),
            unassigned_observations=len(window_result.unassigned_observations),
            warnings=warnings + window_result.warnings,
        )

    def format_terminal(self, diagnostics: SamplingDiagnostics) -> str:
        """Format diagnostics for terminal display.

        Produces a concise, human-readable block like:

        ──────────────────────────────
          Sampling Strategy
          Commit-25
          Score: 0.94

          Detector Readiness
          [OK] D-01 READY
          [~~] D-02 PARTIAL
          [X]  D-03 SKIPPED

          Scientific Confidence: High
        ──────────────────────────────
        """
        lines: List[str] = []
        lines.append("")
        lines.append("-" * 50)
        lines.append("  Sampling Strategy")
        lines.append("  " + "-" * 40)

        if diagnostics.plan:
            plan = diagnostics.plan
            lines.append(f"  {plan.chosen.strategy.title()}-{plan.chosen.window_size}")
            lines.append(f"  Score: {plan.chosen.score:.2f}")
            lines.append(
                f"  Expected: {plan.chosen.expected_windows} windows, "
                f"~{plan.chosen.expected_obs_per_window:.0f} obs/window"
            )
            lines.append(f"  Confidence: {plan.scientific_confidence.title()}")
        else:
            lines.append("  No plan available")

        lines.append("")

        # Detector readiness
        lines.append("  Detector Readiness")
        lines.append("  " + "-" * 40)

        if diagnostics.readiness:
            for r in diagnostics.readiness.detector_readiness:
                if r.state == "READY":
                    icon = "[OK]"
                elif r.state == "PARTIAL":
                    icon = "[~~]"
                elif r.state == "SKIPPED":
                    icon = "[X] "
                else:
                    icon = "[--]"
                lines.append(f"  {icon} {r.detector_id} {r.state}")
                if r.skip_reason:
                    lines.append(f"        Reason: {r.skip_reason}")
                if r.recommendation:
                    lines.append(f"        Action: {r.recommendation}")
        else:
            lines.append("  No readiness data available")

        lines.append("")

        # Window summary
        lines.append("  Windows")
        lines.append("  " + "-" * 40)
        lines.append(f"  Total: {diagnostics.total_windows}")
        lines.append(f"  Observations: {diagnostics.total_observations}")
        if diagnostics.unassigned_observations > 0:
            lines.append(f"  Unassigned: {diagnostics.unassigned_observations}")

        # Per-window summary (first 10)
        if diagnostics.window_diagnostics:
            shown = min(10, len(diagnostics.window_diagnostics))
            for wd in diagnostics.window_diagnostics[:shown]:
                flags = []
                if wd.meets_d01_threshold:
                    flags.append("D01")
                if wd.meets_d02_threshold:
                    flags.append("D02")
                if wd.meets_d03_threshold:
                    flags.append("D03")
                flag_str = ",".join(flags) if flags else "---"
                lines.append(f"  {wd.window_id}: {wd.observation_count} obs " f"[{flag_str}]")
            if len(diagnostics.window_diagnostics) > shown:
                lines.append(f"  ... and {len(diagnostics.window_diagnostics) - shown} more")

        lines.append("")

        # Warnings
        if diagnostics.warnings:
            lines.append("  Warnings")
            lines.append("  " + "-" * 40)
            for w in diagnostics.warnings[:5]:
                lines.append(f"  - {w}")
            if len(diagnostics.warnings) > 5:
                lines.append(f"  ... and {len(diagnostics.warnings) - 5} more")
            lines.append("")

        lines.append("-" * 50)
        lines.append("")

        return "\n".join(lines)

    def to_dict(self, diagnostics: SamplingDiagnostics) -> Dict[str, Any]:
        """Convert diagnostics to a JSON-serializable dictionary.

        Args:
            diagnostics: SamplingDiagnostics to convert.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        result: Dict[str, Any] = {}

        # Profile
        if diagnostics.profile:
            p = diagnostics.profile
            result["profile"] = {
                "commit_count": p.commit_count,
                "repo_age_days": p.repo_age_days,
                "observation_count": p.observation_count,
                "observation_density": p.observation_density,
                "commit_density": p.commit_density,
                "activity_class": p.activity_class,
                "scale": p.scale,
                "volatility": p.volatility,
                "metrics_available": list(p.metrics_available),
                "time_span_days": p.time_span_days,
            }

        # Plan
        if diagnostics.plan:
            plan = diagnostics.plan
            result["plan"] = {
                "chosen_strategy": plan.chosen.strategy,
                "chosen_window_size": plan.chosen.window_size,
                "chosen_score": plan.chosen.score,
                "expected_windows": plan.chosen.expected_windows,
                "expected_obs_per_window": plan.chosen.expected_obs_per_window,
                "scientific_confidence": plan.scientific_confidence,
                "selection_rationale": plan.selection_rationale,
                "alternatives_count": len(plan.alternatives),
                "rejected_count": len(plan.rejected),
                "prediction_error": plan.prediction_error,
                "window_difference": plan.window_difference,
                "observation_difference": plan.observation_difference,
                "confidence_adjustment": plan.confidence_adjustment,
            }

        # Readiness
        if diagnostics.readiness:
            result["readiness"] = {
                "overall_state": diagnostics.readiness.overall_state,
                "ready_count": diagnostics.readiness.ready_count,
                "partial_count": diagnostics.readiness.partial_count,
                "skipped_count": diagnostics.readiness.skipped_count,
                "detectors": [
                    {
                        "detector_id": r.detector_id,
                        "state": r.state,
                        "required_obs_per_window": r.required_obs_per_window,
                        "actual_obs_per_window": r.actual_obs_per_window,
                        "required_windows": r.required_windows,
                        "actual_windows": r.actual_windows,
                        "skip_reason": r.skip_reason,
                        "execution_confidence": r.execution_confidence,
                        "recommendation": r.recommendation,
                    }
                    for r in diagnostics.readiness.detector_readiness
                ],
            }

        # Execution traces
        result["execution_traces"] = [
            {
                "detector_id": t.detector_id,
                "observation_count": t.observation_count,
                "window_count": t.window_count,
                "sample_size": t.sample_size,
                "required_sample": t.required_sample,
                "readiness_state": t.readiness_state,
                "execution_decision": t.execution_decision,
                "evidence_generated": t.evidence_generated,
                "skip_reason": t.skip_reason,
            }
            for t in diagnostics.execution_traces
        ]

        # Window summary
        result["window_summary"] = {
            "total_windows": diagnostics.total_windows,
            "total_observations": diagnostics.total_observations,
            "unassigned_observations": diagnostics.unassigned_observations,
            "strategy_used": diagnostics.strategy_used,
        }

        # Warnings
        result["warnings"] = diagnostics.warnings

        return result
