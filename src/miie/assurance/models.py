"""Scientific Assurance Framework data models.

Deterministic models for assumption validation, evidence sufficiency,
threats-to-validity, limitation reporting, and audit trail.

FROZEN: No scientific computation modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class AssumptionStatus(Enum):
    """Assumption check status."""

    SATISFIED = "satisfied"
    LIKELY_SATISFIED = "likely_satisfied"
    UNCERTAIN = "uncertain"
    LIKELY_VIOLATED = "likely_violated"
    VIOLATED = "violated"
    NOT_CHECKABLE = "not_checkable"


class ThreatCategory(Enum):
    """Threat-to-validity categories."""

    CONSTRUCT = "construct_validity"
    STATISTICAL = "statistical_conclusion_validity"
    INTERNAL = "internal_validity"
    EXTERNAL = "external_validity"
    CONCLUSION = "conclusion_validity"


class ThreatSeverity(Enum):
    """Threat severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SufficiencyStatus(Enum):
    """Evidence sufficiency status."""

    SUFFICIENT = "sufficient"
    CONDITIONALLY_SUFFICIENT = "conditionally_sufficient"
    INSUFFICIENT = "insufficient"
    NOT_ASSESSABLE = "not_assessable"


class LimitationCategory(Enum):
    """Limitation categories."""

    SAMPLE_SIZE = "sample_size"
    STATISTICAL_POWER = "statistical_power"
    ASSUMPTION_VIOLATION = "assumption_violation"
    DATA_QUALITY = "data_quality"
    METHODOLOGICAL = "methodological"
    EXTERNAL = "external"
    TEMPORAL = "temporal"


# ---------------------------------------------------------------------------
# Assumption Validation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AssumptionCheck:
    """Single assumption check result.

    Attributes:
        assumption_id: Unique identifier.
        name: Assumption name (e.g., "normality", "independence").
        statistical_method: Which statistical method this applies to.
        status: Check status.
        test_statistic: Value of the assumption test statistic.
        p_value: P-value of the assumption test.
        threshold: Threshold used for判断.
        evidence: Supporting evidence for the status.
        impact_if_violated: What happens if this assumption is violated.
        recommendation: What to do if violated.
    """

    assumption_id: str
    name: str
    statistical_method: str
    status: AssumptionStatus
    test_statistic: float = 0.0
    p_value: float = 1.0
    threshold: float = 0.05
    evidence: str = ""
    impact_if_violated: str = ""
    recommendation: str = ""


@dataclass(frozen=True)
class AssumptionReport:
    """Complete assumption validation report for a detector.

    Attributes:
        report_id: Unique identifier.
        detector_id: Detector this report covers.
        metric: Metric analyzed.
        assumptions: All assumption checks.
        overall_status: Worst status across all assumptions.
        satisfied_count: Number of satisfied assumptions.
        total_count: Total assumptions checked.
        confidence_impact: How assumptions affect confidence [0, 1].
    """

    report_id: str
    detector_id: str
    metric: str
    assumptions: List[AssumptionCheck]
    overall_status: AssumptionStatus
    satisfied_count: int
    total_count: int
    confidence_impact: float


# ---------------------------------------------------------------------------
# Evidence Sufficiency
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SufficiencyCriterion:
    """Single sufficiency criterion.

    Attributes:
        criterion_id: Unique identifier.
        name: Criterion name.
        description: What this criterion requires.
        threshold: Required threshold value.
        actual: Actual observed value.
        met: Whether criterion is met.
        evidence: Supporting evidence.
    """

    criterion_id: str
    name: str
    description: str
    threshold: float
    actual: float
    met: bool
    evidence: str = ""


@dataclass(frozen=True)
class EvidenceSufficiencyReport:
    """Evidence sufficiency assessment.

    Attributes:
        report_id: Unique identifier.
        detector_id: Detector assessed.
        metric: Metric assessed.
        criteria: All criteria evaluated.
        status: Overall sufficiency status.
        met_count: Number of criteria met.
        total_count: Total criteria.
        gaps: List of unmet criteria.
        confidence_impact: How sufficiency affects confidence [0, 1].
    """

    report_id: str
    detector_id: str
    metric: str
    criteria: List[SufficiencyCriterion]
    status: SufficiencyStatus
    met_count: int
    total_count: int
    gaps: List[str]
    confidence_impact: float


# ---------------------------------------------------------------------------
# Threats to Validity
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ThreatToValidity:
    """Single threat to validity.

    Attributes:
        threat_id: Unique identifier.
        category: Threat category.
        name: Threat name.
        description: Description of the threat.
        impact: Impact if realized.
        severity: Threat severity.
        evidence: Evidence that this threat is active.
        mitigation: How to mitigate.
        residual_risk: Risk remaining after mitigation.
        detector_ids: Which detectors are affected.
        metric_ids: Which metrics are affected.
    """

    threat_id: str
    category: ThreatCategory
    name: str
    description: str
    impact: str
    severity: ThreatSeverity
    evidence: str
    mitigation: str
    residual_risk: str
    detector_ids: List[str]
    metric_ids: List[str]


@dataclass(frozen=True)
class ThreatAssessment:
    """Complete threat assessment for an analysis.

    Attributes:
        assessment_id: Unique identifier.
        threats: All identified threats.
        active_count: Number of active threats.
        total_count: Total threats assessed.
        high_severity_count: Count of high/critical threats.
        overall_risk: Overall risk level.
    """

    assessment_id: str
    threats: List[ThreatToValidity]
    active_count: int
    total_count: int
    high_severity_count: int
    overall_risk: str


# ---------------------------------------------------------------------------
# Limitations
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Limitation:
    """Single scientific limitation.

    Attributes:
        limitation_id: Unique identifier.
        category: Limitation category.
        name: Limitation name.
        description: Description.
        impact: Impact on conclusions.
        quantification: Quantitative assessment when possible.
        mitigation: How to mitigate.
        detector_ids: Which detectors affected.
        metric_ids: Which metrics affected.
    """

    limitation_id: str
    category: LimitationCategory
    name: str
    description: str
    impact: str
    quantification: str
    mitigation: str
    detector_ids: List[str]
    metric_ids: List[str]


@dataclass(frozen=True)
class LimitationReport:
    """Complete limitation report.

    Attributes:
        report_id: Unique identifier.
        limitations: All identified limitations.
        total_count: Total limitations.
        by_category: Count by category.
        overall_impact: Overall impact assessment.
    """

    report_id: str
    limitations: List[Limitation]
    total_count: int
    by_category: Dict[str, int]
    overall_impact: str


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuditTrailNode:
    """Single node in extended audit trail.

    Attributes:
        node_id: Unique identifier.
        node_type: Type (finding/reasoning/evidence/detector/metric/observation/confidence/validation/assumption/ground_truth/spec/certification).
        label: Human-readable label.
        data: Associated data.
        parent_ids: Parent node references.
    """

    node_id: str
    node_type: str
    label: str
    data: Dict[str, Any] = field(default_factory=dict)
    parent_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExtendedAuditTrail:
    """Extended audit trail for a finding.

        Finding
        -> Reasoning
        -> Evidence
        -> Detector
        -> Metric
        -> Observation
        -> Confidence
        -> Validation
        -> Assumptions
        -> Ground Truth
        -> Specification
        -> Certification

    Attributes:
        trail_id: Unique identifier.
        finding_id: Reference to root finding.
        nodes: All audit trail nodes.
        root_node_id: The finding node.
    """

    trail_id: str
    finding_id: str
    nodes: List[AuditTrailNode]
    root_node_id: str


# ---------------------------------------------------------------------------
# Scientific Assurance Report
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScientificAssuranceReport:
    """Complete scientific assurance report.

    Attributes:
        report_id: Unique identifier.
        executive_summary: Executive-level assurance summary.
        assumption_reports: Assumption validation reports.
        sufficiency_reports: Evidence sufficiency reports.
        threat_assessment: Threats-to-validity assessment.
        limitation_report: Limitation report.
        audit_trails: Extended audit trails.
        overall_assurance: Overall assurance level.
        overall_confidence: Confidence in assurance [0, 1].
    """

    report_id: str
    executive_summary: str
    assumption_reports: List[AssumptionReport]
    sufficiency_reports: List[EvidenceSufficiencyReport]
    threat_assessment: ThreatAssessment
    limitation_report: LimitationReport
    audit_trails: List[ExtendedAuditTrail]
    overall_assurance: str
    overall_confidence: float
