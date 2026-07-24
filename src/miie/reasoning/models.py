"""Deterministic reasoning data models for MIIE.

These models formalize the reasoning chain from raw scientific outputs
to explainable, traceable, certifiable conclusions.

FROZEN: This module defines new reasoning objects only.
It does not modify any existing scientific computation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class Severity(Enum):
    """Finding severity levels."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ConfidenceLevel(Enum):
    """Confidence classification."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerdictValue(Enum):
    """Overall assessment verdict."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class CertificationStatus(Enum):
    """Certification status."""

    CERTIFIED = "certified"
    CONDITIONAL = "conditional"
    FAILED = "failed"
    INSUFFICIENT = "insufficient"


# ---------------------------------------------------------------------------
# Reasoning primitives
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReasoningStep:
    """Single step in a deterministic reasoning chain.

    Attributes:
        step_id: Unique identifier for this step.
        description: What this step does.
        method: Statistical or logical method applied.
        inputs: References to input data/evidence.
        output: What this step produces.
        parameters: Method parameters (alpha, thresholds, etc.).
        result: Computed result value.
        assumptions_met: Whether test assumptions were satisfied.
        confidence: Confidence in this step's conclusion [0, 1].
    """

    step_id: str
    description: str
    method: str
    inputs: List[str]
    output: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    assumptions_met: bool = True
    confidence: float = 1.0


@dataclass(frozen=True)
class ReasoningChain:
    """Complete reasoning trace for a finding.

    Attributes:
        chain_id: Unique identifier.
        conclusion: Final conclusion from this chain.
        steps: Ordered reasoning steps.
        evidence_refs: References to supporting evidence.
        spec_reference: Reference to scientific specification.
        confidence: Overall chain confidence [0, 1].
    """

    chain_id: str
    conclusion: str
    steps: List[ReasoningStep]
    evidence_refs: List[str]
    spec_reference: str
    confidence: float = 1.0


# ---------------------------------------------------------------------------
# Finding model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IntegrityFinding:
    """Structured finding from integrity scoring.

    Attributes:
        finding_id: Unique identifier.
        category: Finding category (distribution_drift, etc.).
        metric: Metric identifier (M-01, M-02, etc.).
        detector: Detector identifier (D-01, D-02, D-03).
        severity: Finding severity.
        description: Human-readable description.
        evidence_refs: References to supporting evidence.
        confidence: Confidence in this finding [0, 1].
        reasoning_chain: Full reasoning trace.
    """

    finding_id: str
    category: str
    metric: str
    detector: str
    severity: Severity
    description: str
    evidence_refs: List[str]
    confidence: float
    reasoning_chain: ReasoningChain


# ---------------------------------------------------------------------------
# Explanation model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FindingExplanation:
    """Deterministic explanation for a finding.

    Answers: What happened? Why? How certain? Which detector? Which metrics?
    Which observations? Which evidence? Which specification?

    Attributes:
        explanation_id: Unique identifier.
        finding_id: Reference to the finding being explained.
        what_happened: Description of the observation.
        why: Root cause or contributing factor.
        how_certain: Confidence assessment with justification.
        detector_reference: Which detector and why chosen.
        metric_reference: Which metrics involved.
        observation_reference: Which observations支撑 this.
        evidence_reference: Which evidence items support this.
        specification_reference: Which specification governs this.
        narrative: Full explanatory narrative.
    """

    explanation_id: str
    finding_id: str
    what_happened: str
    why: str
    how_certain: str
    detector_reference: str
    metric_reference: str
    observation_reference: str
    evidence_reference: str
    specification_reference: str
    narrative: str


# ---------------------------------------------------------------------------
# Evidence graph
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceNode:
    """Node in a deterministic evidence graph.

    Attributes:
        node_id: Unique identifier.
        node_type: Type of node (finding/evidence/detector/metric/observation/context/spec).
        label: Human-readable label.
        data: Associated data payload.
        parent_ids: References to parent nodes.
    """

    node_id: str
    node_type: str
    label: str
    data: Dict[str, Any] = field(default_factory=dict)
    parent_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvidenceGraph:
    """Deterministic evidence graph linking finding to specification.

    Structure: Finding -> Evidence -> Detector -> Metric -> Observation -> Context -> Spec

    Attributes:
        graph_id: Unique identifier.
        finding_id: Reference to the root finding.
        nodes: All nodes in the graph.
        root_node_id: The finding node.
    """

    graph_id: str
    finding_id: str
    nodes: List[EvidenceNode]
    root_node_id: str


# ---------------------------------------------------------------------------
# Certification model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CertificationResult:
    """Deterministic certification of analysis quality.

    Attributes:
        certification_id: Unique identifier.
        name: Certification name (e.g., "Repository Healthy").
        status: Certification status.
        requirements: What must be true for this certification.
        supporting_evidence: Evidence that supports/contradicts.
        confidence: Confidence in this certification [0, 1].
        failure_conditions: What would cause failure.
        reasoning: Explanation of why this status was assigned.
    """

    certification_id: str
    name: str
    status: CertificationStatus
    requirements: List[str]
    supporting_evidence: List[str]
    confidence: float
    failure_conditions: List[str]
    reasoning: str


# ---------------------------------------------------------------------------
# Verdict model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Verdict:
    """Overall assessment verdict.

    Attributes:
        value: Verdict value (PASS/WARN/FAIL).
        reasoning: Explanation of why this verdict was reached.
        supporting_findings: Findings that support this verdict.
        confidence: Confidence in the verdict [0, 1].
    """

    value: VerdictValue
    reasoning: str
    supporting_findings: List[str]
    confidence: float


# ---------------------------------------------------------------------------
# Assessment model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AssessmentDimension:
    """Single dimension of an assessment.

    Attributes:
        dimension: Name of the dimension (e.g., "Statistical Rigor").
        score: Numeric score [0, 1].
        level: Qualitative level (high/medium/low).
        reasoning: Why this score was assigned.
        evidence_refs: Supporting evidence.
    """

    dimension: str
    score: float
    level: str
    reasoning: str
    evidence_refs: List[str]


@dataclass(frozen=True)
class Assessment:
    """Multi-dimensional assessment of analysis quality.

    Attributes:
        assessment_id: Unique identifier.
        assessment_type: Type (executive/scientific/measurement/repository/validation).
        dimensions: Assessed dimensions.
        overall_score: Aggregate score [0, 1].
        overall_level: Aggregate level.
        verdict: Overall verdict.
        summary: Human-readable summary.
    """

    assessment_id: str
    assessment_type: str
    dimensions: List[AssessmentDimension]
    overall_score: float
    overall_level: str
    verdict: Verdict
    summary: str


# ---------------------------------------------------------------------------
# Decision justification model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JustifiedRecommendation:
    """Recommendation with full decision justification.

    Attributes:
        recommendation_id: Unique identifier.
        category: Recommendation category.
        priority: Priority level (high/medium/low).
        title: Short title.
        description: What to do.
        reason: Why this recommendation exists.
        evidence: Supporting evidence.
        confidence: Confidence in this recommendation [0, 1].
        affected_metrics: Metrics this affects.
        affected_detectors: Detectors this relates to.
        certification_impact: How this affects certifications.
        reasoning_chain: Full reasoning trace.
    """

    recommendation_id: str
    category: str
    priority: str
    title: str
    description: str
    reason: str
    evidence: List[str]
    confidence: float
    affected_metrics: List[str]
    affected_detectors: List[str]
    certification_impact: List[str]
    reasoning_chain: ReasoningChain
