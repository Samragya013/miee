"""Scientific Assurance Engine.

Orchestrates assumption validation, evidence sufficiency,
threats-to-validity, limitations, and audit trail generation.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from miie.assurance.assumptions import check_detector_assumptions
from miie.assurance.audit_trail import build_audit_trail
from miie.assurance.limitations import build_limitation_report
from miie.assurance.models import (
    AssumptionReport,
    EvidenceSufficiencyReport,
    ExtendedAuditTrail,
    ScientificAssuranceReport,
    ThreatAssessment,
)
from miie.assurance.sufficiency import assess_evidence_sufficiency
from miie.assurance.threats import assess_threats


def _hash_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def build_assurance_report(
    findings: List[Dict[str, Any]],
    analysis_context: Dict[str, Any],
) -> ScientificAssuranceReport:
    """Build complete scientific assurance report for all findings.

    Args:
        findings: List of finding dicts with keys: finding_id, detector_id,
                  metric, evidence, confidence, reasoning, ground_truth.
        analysis_context: Global analysis context (sample_size, power, etc).

    Returns:
        ScientificAssuranceReport with all assurance dimensions.
    """
    assumption_reports: List[AssumptionReport] = []
    sufficiency_reports: List[EvidenceSufficiencyReport] = []
    threat_assessments: List[ThreatAssessment] = []
    audit_trails: List[ExtendedAuditTrail] = []

    for finding in findings:
        fid = finding.get("finding_id", "unknown")
        det = finding.get("detector_id", "unknown")
        met = finding.get("metric", "unknown")
        evidence = finding.get("evidence", {})
        conf = finding.get("confidence", {})
        reasoning = finding.get("reasoning", {})
        gt = finding.get("ground_truth", {})

        # Combine evidence data for analysis
        analysis_data: Dict[str, Any] = {
            "sample_size": analysis_context.get("sample_size", 0),
            "power": analysis_context.get("power", 0.0),
            "effect_size": evidence.get("effect_size", 0.0),
            "ci_lower": evidence.get("ci_lower"),
            "ci_upper": evidence.get("ci_upper"),
            "observations_total": evidence.get("observations_total", 0),
            "observations_valid": evidence.get("observations_valid", 0),
            "detector_results": evidence.get("detector_results", {}),
            "missing_data_pct": evidence.get("missing_data_pct", 0.0),
            "num_tests_conducted": analysis_context.get("num_tests_conducted", 1),
        }

        # Metric data for assumption checking
        metric_data = analysis_context.get("metric_data", {})

        # 1. Assumption validation
        assum_report = check_detector_assumptions(det, met, finding, metric_data)
        assumption_reports.append(assum_report)

        # 2. Evidence sufficiency
        suff_report = assess_evidence_sufficiency(det, met, analysis_data)
        sufficiency_reports.append(suff_report)

        # 3. Threats to validity
        threat_assess = assess_threats(det, met, analysis_data)
        threat_assessments.append(threat_assess)

        # 4. Audit trail
        trail = build_audit_trail(
            finding_id=fid,
            finding_data=finding,
            reasoning_data=reasoning,
            evidence_data=evidence,
            detector_id=det,
            metric=met,
            confidence_data=conf,
            assumption_data={
                "satisfied": assum_report.satisfied_count,
                "total": assum_report.total_count,
                "status": assum_report.overall_status.value,
            },
            ground_truth_data=gt,
        )
        audit_trails.append(trail)

    # 5. Limitation report (aggregate)
    all_metrics = list({f.get("metric", "unknown") for f in findings})
    first_detector = findings[0].get("detector_id", "unknown") if findings else "unknown"
    limitation_report = build_limitation_report(first_detector, ",".join(all_metrics), analysis_context)

    # Compute overall assurance
    assum_impacts = [a.confidence_impact for a in assumption_reports]
    suff_impacts = [s.confidence_impact for s in sufficiency_reports]
    avg_assum = sum(assum_impacts) / len(assum_impacts) if assum_impacts else 0.8
    avg_suff = sum(suff_impacts) / len(suff_impacts) if suff_impacts else 0.8

    high_threats = sum(t.high_severity_count for t in threat_assessments)
    threat_penalty = min(0.3, high_threats * 0.1)

    overall_confidence = max(0.0, min(1.0, (avg_assum * 0.4 + avg_suff * 0.4 + 0.2) - threat_penalty))

    if overall_confidence >= 0.8:
        overall_assurance = "STRONG"
    elif overall_confidence >= 0.6:
        overall_assurance = "MODERATE"
    elif overall_confidence >= 0.4:
        overall_assurance = "WEAK"
    else:
        overall_assurance = "INSUFFICIENT"

    # Build executive summary
    total_assumptions = sum(a.total_count for a in assumption_reports)
    satisfied_assumptions = sum(a.satisfied_count for a in assumption_reports)
    total_suff = sum(s.total_count for s in sufficiency_reports)
    met_suff = sum(s.met_count for s in sufficiency_reports)
    total_threats = sum(t.total_count for t in threat_assessments)
    active_threats = sum(t.active_count for t in threat_assessments)

    exec_summary = (
        f"Scientific Assurance: {overall_assurance} (confidence={overall_confidence:.3f}). "
        f"Assumptions: {satisfied_assumptions}/{total_assumptions} satisfied. "
        f"Sufficiency: {met_suff}/{total_suff} criteria met. "
        f"Threats: {active_threats}/{total_threats} active. "
        f"Limitations: {limitation_report.total_count} identified."
    )

    return ScientificAssuranceReport(
        report_id=_hash_id(f"assurance_{len(findings)}"),
        executive_summary=exec_summary,
        assumption_reports=assumption_reports,
        sufficiency_reports=sufficiency_reports,
        threat_assessment=ThreatAssessment(
            assessment_id=_hash_id(f"threats_agg_{len(findings)}"),
            threats=[t for ta in threat_assessments for t in ta.threats],
            active_count=active_threats,
            total_count=total_threats,
            high_severity_count=high_threats,
            overall_risk="high" if high_threats > 2 else "medium" if active_threats > 0 else "low",
        ),
        limitation_report=limitation_report,
        audit_trails=audit_trails,
        overall_assurance=overall_assurance,
        overall_confidence=overall_confidence,
    )
