"""Scientific Traceability Framework.

Provides full traceability chains:
conclusion → evidence → detector → metric → observation → confidence → spec

Each traceability chain is deterministic and derived solely from frozen
scientific core outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .engine import WorkspaceEngine


@dataclass
class TraceabilityNode:
    """A node in a traceability chain."""

    level: str
    name: str
    value: Any
    source: str
    children: List["TraceabilityNode"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "name": self.name,
            "value": str(self.value),
            "source": self.source,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class TraceabilityChain:
    """A complete traceability chain from conclusion to specification."""

    finding: str
    evidence_items: List[Dict[str, Any]]
    detector: str
    metric: str
    observations: List[Dict[str, Any]]
    confidence_factors: Dict[str, float]
    spec_reference: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding": self.finding,
            "evidence_items": self.evidence_items,
            "detector": self.detector,
            "metric": self.metric,
            "observations": self.observations,
            "confidence_factors": self.confidence_factors,
            "spec_reference": self.spec_reference,
        }

    def render_lines(self) -> List[str]:
        """Render chain as human-readable lines."""
        lines = []
        lines.append("=" * 72)
        lines.append("TRACEABILITY CHAIN")
        lines.append("=" * 72)
        lines.append("")
        lines.append(f"Finding: {self.finding}")
        lines.append(f"Detector: {self.detector}")
        lines.append(f"Metric: {self.metric}")
        lines.append("")

        lines.append("Evidence Items:")
        for i, ev in enumerate(self.evidence_items, 1):
            lines.append(f"  {i}. {ev.get('type', 'Unknown')}: {ev.get('description', '')[:60]}")

        lines.append("")
        lines.append("Observations:")
        for obs in self.observations:
            lines.append(f"  - {obs.get('type', '')}: {obs.get('value', '')}")

        lines.append("")
        lines.append("Confidence Factors:")
        for factor, value in self.confidence_factors.items():
            lines.append(f"  {factor}: {value:.4f}")

        lines.append("")
        lines.append(f"Specification: {self.spec_reference}")

        return lines


class TraceabilityEngine:
    """Builds traceability chains from workspace state."""

    def __init__(self, workspace: WorkspaceEngine) -> None:
        self.workspace = workspace

    def get_traceability_for_finding(self, finding_index: int) -> Optional[TraceabilityChain]:
        """Build traceability chain for a specific finding.

        Args:
            finding_index: Index of the finding in integrity findings

        Returns:
            TraceabilityChain or None if finding not found
        """
        state = self.workspace.state
        sp = state.score_package
        if sp is None:
            return None

        integrity = getattr(sp, "integrity", None)
        if integrity is None:
            return None

        findings = getattr(integrity, "findings", []) or []
        if finding_index >= len(findings):
            return None

        finding = findings[finding_index]
        category = getattr(finding, "category", "Unknown")
        metric_name = getattr(finding, "metric", "Unknown")
        detector_name = getattr(finding, "detector", "Unknown")

        # Get evidence for this finding
        evidence_items = self._get_evidence_for_finding(finding)

        # Get observations for this metric
        observations = self._get_observations_for_metric(metric_name)

        # Get confidence factors
        confidence_factors = self._get_confidence_factors()

        # Get spec reference
        spec_ref = self._get_spec_reference(detector_name)

        return TraceabilityChain(
            finding=f"{category} (metric: {metric_name}, detector: {detector_name})",
            evidence_items=evidence_items,
            detector=detector_name,
            metric=metric_name,
            observations=observations,
            confidence_factors=confidence_factors,
            spec_reference=spec_ref,
        )

    def get_traceability_for_metric(self, metric_name: str) -> List[TraceabilityChain]:
        """Get all traceability chains for a metric."""
        state = self.workspace.state
        sp = state.score_package
        if sp is None:
            return []

        integrity = getattr(sp, "integrity", None)
        if integrity is None:
            return []

        findings = getattr(integrity, "findings", []) or []
        chains = []
        for i, f in enumerate(findings):
            f_metric = getattr(f, "metric", "Unknown")
            if f_metric == metric_name:
                chain = self.get_traceability_for_finding(i)
                if chain:
                    chains.append(chain)

        return chains

    def get_all_chains(self) -> List[TraceabilityChain]:
        """Get traceability chains for all findings."""
        state = self.workspace.state
        sp = state.score_package
        if sp is None:
            return []

        integrity = getattr(sp, "integrity", None)
        if integrity is None:
            return []

        findings = getattr(integrity, "findings", []) or []
        chains = []
        for i in range(len(findings)):
            chain = self.get_traceability_for_finding(i)
            if chain:
                chains.append(chain)

        return chains

    def _get_evidence_for_finding(self, finding: Any) -> List[Dict[str, Any]]:
        """Get evidence items related to a finding."""
        state = self.workspace.state
        ep = state.evidence_package
        if ep is None:
            return []

        evidence = getattr(ep, "evidence", {}) or {}
        metric = getattr(finding, "metric", "")

        metric_evidence = evidence.get(metric, [])
        if isinstance(metric_evidence, list):
            return [
                {
                    "type": type(e).__name__,
                    "description": str(e)[:100],
                    "metric": metric,
                }
                for e in metric_evidence[:5]
            ]

        return [{"type": "Evidence", "description": str(metric_evidence)[:100], "metric": metric}]

    def _get_observations_for_metric(self, metric_name: str) -> List[Dict[str, Any]]:
        """Get observations for a metric."""
        state = self.workspace.state
        ep = state.evidence_package
        if ep is None:
            return []

        obs_summary = getattr(ep, "observation_summary", None)
        if obs_summary is None:
            return []

        # Try to get metric-specific observations
        metric_observations = getattr(obs_summary, "metric_observations", {}) or {}
        obs_list = metric_observations.get(metric_name, [])

        return [
            {
                "type": type(o).__name__,
                "value": str(getattr(o, "value", "")),
                "metric": metric_name,
            }
            for o in obs_list[:5]
        ]

    def _get_confidence_factors(self) -> Dict[str, float]:
        """Get all confidence factors."""
        state = self.workspace.state
        sp = state.score_package
        if sp is None:
            return {}

        confidence = getattr(sp, "confidence", None)
        if confidence is None:
            return {}

        factors = {}
        for i in range(1, 7):
            factor_name = f"beta_{i}"
            value = getattr(confidence, factor_name, None)
            if value is not None:
                factors[factor_name] = float(value)

        return factors

    def _get_spec_reference(self, detector_name: str) -> str:
        """Get specification reference for a detector."""
        spec_map = {
            "saturation": "Spec §4.5 — Saturation Detection",
            "herfindahl": "Spec §4.6 — Herfindahl Index",
            "velocity": "Spec §4.7 — Velocity Anomaly",
            "ownership": "Spec §4.8 — Ownership Concentration",
            "commit": "Spec §4.9 — Commit Pattern",
        }
        return spec_map.get(detector_name.lower(), f"Spec §4.x — {detector_name} Detection")
