"""Deterministic Recommendation Engine.

Generates recommendations ONLY from existing scientific outputs.
No AI reasoning, no heuristics outside approved specifications.
Every recommendation is traceable to a specific scientific finding.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .engine import WorkspaceEngine


@dataclass
class Recommendation:
    """A single deterministic recommendation."""

    category: str
    priority: str
    title: str
    description: str
    reason: str
    evidence_refs: List[str]
    confidence: float
    spec_reference: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "reason": self.reason,
            "evidence_refs": self.evidence_refs,
            "confidence": self.confidence,
            "spec_reference": self.spec_reference,
        }


class RecommendationEngine:
    """Generates deterministic recommendations from scientific outputs.

    All recommendations follow this pattern:
    1. Find a scientific finding (integrity, confidence, evidence, etc.)
    2. Determine if recommendation threshold is met
    3. Generate recommendation with traceability to source finding
    """

    def __init__(self, workspace: WorkspaceEngine) -> None:
        self.workspace = workspace

    def generate_all(self) -> List[Recommendation]:
        """Generate all recommendations from workspace state."""
        recommendations = []

        # Integrity-based recommendations
        recommendations.extend(self._integrity_recommendations())

        # Confidence-based recommendations
        recommendations.extend(self._confidence_recommendations())

        # Evidence-based recommendations
        recommendations.extend(self._evidence_recommendations())

        # Metric-specific recommendations
        recommendations.extend(self._metric_recommendations())

        return recommendations

    def _integrity_recommendations(self) -> List[Recommendation]:
        """Generate recommendations from integrity findings."""
        state = self.workspace.state
        sp = state.score_package
        if sp is None:
            return []

        integrity = getattr(sp, "integrity", None)
        if integrity is None:
            return []

        recommendations = []
        score = getattr(integrity, "score", 0.0) or 0.0
        findings = getattr(integrity, "findings", []) or []

        # Low integrity score
        if score < 0.5:
            recommendations.append(
                Recommendation(
                    category="integrity",
                    priority="high",
                    title="Low Integrity Score Detected",
                    description=(
                        f"The overall integrity score is {score:.2f}, which is below the "
                        "recommended threshold of 0.5. This indicates potential issues with "
                        "data quality or analysis validity."
                    ),
                    reason="Integrity score below threshold",
                    evidence_refs=[f"integrity.score = {score:.4f}"],
                    confidence=0.9,
                    spec_reference="Spec §5.1 — Integrity Thresholds",
                )
            )

        # High-severity findings
        high_severity = [f for f in findings if getattr(f, "severity", "") == "HIGH"]
        if high_severity:
            recommendations.append(
                Recommendation(
                    category="integrity",
                    priority="high",
                    title="High-Severity Integrity Findings",
                    description=(
                        f"Found {len(high_severity)} high-severity integrity findings. "
                        "These should be investigated immediately."
                    ),
                    reason="High-severity findings detected",
                    evidence_refs=[f"integrity.findings[{i}].severity = HIGH" for i in range(len(high_severity))],
                    confidence=0.85,
                    spec_reference="Spec §5.2 — Severity Classification",
                )
            )

        return recommendations

    def _confidence_recommendations(self) -> List[Recommendation]:
        """Generate recommendations from confidence analysis."""
        state = self.workspace.state
        sp = state.score_package
        if sp is None:
            return []

        confidence = getattr(sp, "confidence", None)
        if confidence is None:
            return []

        recommendations = []
        score = getattr(confidence, "score", 0.0) or 0.0

        # Low confidence score
        if score < 0.6:
            recommendations.append(
                Recommendation(
                    category="confidence",
                    priority="medium",
                    title="Low Confidence Score",
                    description=(
                        f"The overall confidence score is {score:.2f}, which is below the "
                        "recommended threshold of 0.6. Consider gathering more data or "
                        "refining the analysis."
                    ),
                    reason="Confidence score below threshold",
                    evidence_refs=[f"confidence.score = {score:.4f}"],
                    confidence=0.8,
                    spec_reference="Spec §5.3 — Confidence Thresholds",
                )
            )

        # Low beta factors
        for i in range(1, 7):
            factor_name = f"beta_{i}"
            value = getattr(confidence, factor_name, None)
            if value is not None and value < 0.3:
                recommendations.append(
                    Recommendation(
                        category="confidence",
                        priority="low",
                        title=f"Low Confidence Factor: {factor_name}",
                        description=(
                            f"Factor {factor_name} is {value:.4f}, which is below the " "recommended threshold of 0.3."
                        ),
                        reason=f"Low value for {factor_name}",
                        evidence_refs=[f"confidence.{factor_name} = {value:.4f}"],
                        confidence=0.7,
                        spec_reference=f"Spec §5.4 — {factor_name} Definition",
                    )
                )

        return recommendations

    def _evidence_recommendations(self) -> List[Recommendation]:
        """Generate recommendations from evidence analysis."""
        state = self.workspace.state
        ep = state.evidence_package
        if ep is None:
            return []

        recommendations = []

        # Check observation quality
        obs_summary = getattr(ep, "observation_summary", None)
        if obs_summary is not None:
            quality = getattr(obs_summary, "quality_score", 1.0) or 1.0
            if quality < 0.7:
                recommendations.append(
                    Recommendation(
                        category="evidence",
                        priority="medium",
                        title="Low Observation Quality",
                        description=(
                            f"The observation quality score is {quality:.2f}, which is below "
                            "the recommended threshold of 0.7. Consider reviewing data "
                            "collection methodology."
                        ),
                        reason="Observation quality below threshold",
                        evidence_refs=[f"observation_summary.quality_score = {quality:.4f}"],
                        confidence=0.75,
                        spec_reference="Spec §5.5 — Observation Quality",
                    )
                )

        # Check validation metrics
        vm = getattr(ep, "validation_metrics", None)
        if vm:
            total = vm.get("total_observations", 0)
            invalid = vm.get("invalid_observations", 0)
            if total > 0 and invalid / total > 0.1:
                recommendations.append(
                    Recommendation(
                        category="evidence",
                        priority="medium",
                        title="High Invalid Observation Rate",
                        description=(
                            f"{invalid} of {total} observations are invalid "
                            f"({invalid / total * 100:.1f}%). This exceeds the 10% threshold."
                        ),
                        reason="Invalid observation rate exceeds threshold",
                        evidence_refs=[
                            f"validation_metrics.invalid_observations = {invalid}",
                            f"validation_metrics.total_observations = {total}",
                        ],
                        confidence=0.8,
                        spec_reference="Spec §5.6 — Validation Thresholds",
                    )
                )

        return recommendations

    def _metric_recommendations(self) -> List[Recommendation]:
        """Generate metric-specific recommendations."""
        state = self.workspace.state
        sp = state.score_package
        if sp is None:
            return []

        integrity = getattr(sp, "integrity", None)
        if integrity is None:
            return []

        recommendations = []
        metric_scores = getattr(integrity, "metric_scores", {}) or {}

        for metric_name, ms in metric_scores.items():
            if ms is not None:
                m_score = getattr(ms, "score", 1.0) or 1.0
                if m_score < 0.4:
                    recommendations.append(
                        Recommendation(
                            category="metric",
                            priority="medium",
                            title=f"Low Integrity for Metric: {metric_name}",
                            description=(
                                f"Metric '{metric_name}' has an integrity score of "
                                f"{m_score:.2f}, which is below the recommended threshold."
                            ),
                            reason="Metric integrity below threshold",
                            evidence_refs=[f"integrity.metric_scores.{metric_name}.score = {m_score:.4f}"],
                            confidence=0.75,
                            spec_reference=f"Spec §5.7 — {metric_name} Thresholds",
                        )
                    )

        return recommendations
