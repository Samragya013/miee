"""Deterministic reasoning engine for MIIE.

Consumes existing scientific outputs and produces reasoning objects.
No scientific computation modified. Only interpretation layer added.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple

from miie.reasoning.models import (
    Assessment,
    AssessmentDimension,
    CertificationResult,
    CertificationStatus,
    ConfidenceLevel,
    EvidenceGraph,
    EvidenceNode,
    FindingExplanation,
    IntegrityFinding,
    JustifiedRecommendation,
    ReasoningChain,
    ReasoningStep,
    Severity,
    Verdict,
    VerdictValue,
)


def _hash_id(content: str) -> str:
    """Deterministic ID from content."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _classify_severity(value: float, thresholds: Tuple[float, float] = (0.3, 0.6)) -> Severity:
    """Classify numeric value into severity."""
    if value < thresholds[0]:
        return Severity.MILD
    if value < thresholds[1]:
        return Severity.MODERATE
    return Severity.SEVERE


def _classify_confidence(value: float) -> ConfidenceLevel:
    """Classify confidence value."""
    if value >= 0.8:
        return ConfidenceLevel.HIGH
    if value >= 0.5:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def _classify_level(score: float) -> str:
    """Classify score into qualitative level."""
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Finding extraction
# ---------------------------------------------------------------------------


def extract_findings(
    detector_outputs: Dict[str, Dict[str, Any]],
    evidence_package: Dict[str, Any],
    metric_dataframe: Dict[str, Any],
) -> List[IntegrityFinding]:
    """Extract structured findings from detector outputs.

    Consumes existing detector outputs without modification.
    """
    findings: List[IntegrityFinding] = []

    # D-01: Distribution Drift
    d01 = detector_outputs.get("D-01", {})
    if d01.get("drift_detected"):
        for event in d01.get("drift_events", []):
            metric = event.get("metric", "unknown")
            ks_stat = event.get("ks_statistic", 0.0)
            psi_val = event.get("psi_value", 0.0)
            severity = _classify_severity(max(ks_stat, psi_val))

            step = ReasoningStep(
                step_id=_hash_id(f"d01_step_{metric}"),
                description=f"KS two-sample test for distribution drift in {metric}",
                method="Kolmogorov-Smirnov two-sample test",
                inputs=[f"metric_{metric}_w1", f"metric_{metric}_w2"],
                output=f"drift_{'detected' if d01.get('drift_detected') else 'not_detected'}",
                parameters={"alpha": 0.05, "test": "KS"},
                result={"ks_statistic": ks_stat, "psi_value": psi_val},
                assumptions_met=True,
                confidence=0.9 if ks_stat > 0.3 else 0.7,
            )

            chain = ReasoningChain(
                chain_id=_hash_id(f"chain_d01_{metric}"),
                conclusion=f"Distribution drift detected in {metric} (KS D={ks_stat:.3f})",
                steps=[step],
                evidence_refs=[f"evidence_{metric}_drift"],
                spec_reference="docs/specifications/04_DETECTOR_SCIENTIFIC_SPECIFICATION.md",
                confidence=step.confidence,
            )

            finding = IntegrityFinding(
                finding_id=_hash_id(f"finding_d01_{metric}"),
                category="distribution_drift",
                metric=metric,
                detector="D-01",
                severity=severity,
                description=f"Distribution drift detected in {metric}: KS D={ks_stat:.3f}, PSI={psi_val:.3f}",
                evidence_refs=[f"evidence_{metric}_drift"],
                confidence=step.confidence,
                reasoning_chain=chain,
            )
            findings.append(finding)

    # D-02: Correlation Breakdown
    d02 = detector_outputs.get("D-02", {})
    if d02.get("breakdown_detected"):
        for event in d02.get("breakdown_events", []):
            pair = event.get("metric_pair", ("unknown", "unknown"))
            delta_r = event.get("delta_pearson", 0.0)
            severity = _classify_severity(abs(delta_r))

            step = ReasoningStep(
                step_id=_hash_id(f"d02_step_{pair}"),
                description=f"Correlation analysis between {pair[0]} and {pair[1]}",
                method="Pearson correlation with Benjamini-Hochberg correction",
                inputs=[f"metric_{pair[0]}", f"metric_{pair[1]}"],
                output=f"breakdown_{'detected' if d02.get('breakdown_detected') else 'not_detected'}",
                parameters={"method": "Pearson", "correction": "BH"},
                result={"delta_pearson": delta_r},
                assumptions_met=True,
                confidence=0.85 if abs(delta_r) > 0.4 else 0.65,
            )

            chain = ReasoningChain(
                chain_id=_hash_id(f"chain_d02_{pair}"),
                conclusion=f"Correlation breakdown between {pair[0]} and {pair[1]} (delta_r={delta_r:.3f})",
                steps=[step],
                evidence_refs=[f"evidence_{pair[0]}_{pair[1]}_corr"],
                spec_reference="docs/specifications/04_DETECTOR_SCIENTIFIC_SPECIFICATION.md",
                confidence=step.confidence,
            )

            finding = IntegrityFinding(
                finding_id=_hash_id(f"finding_d02_{pair}"),
                category="correlation_breakdown",
                metric=f"{pair[0]}-{pair[1]}",
                detector="D-02",
                severity=severity,
                description=f"Correlation breakdown between {pair[0]} and {pair[1]}: delta_r={delta_r:.3f}",
                evidence_refs=[f"evidence_{pair[0]}_{pair[1]}_corr"],
                confidence=step.confidence,
                reasoning_chain=chain,
            )
            findings.append(finding)

    # D-03: Threshold Compression
    d03 = detector_outputs.get("D-03", {})
    if d03.get("compression_detected"):
        for event in d03.get("compression_events", []):
            metric = event.get("metric", "unknown")
            comp_idx = event.get("compression_index", 0.0)
            severity = _classify_severity(comp_idx)

            step = ReasoningStep(
                step_id=_hash_id(f"d03_step_{metric}"),
                description=f"Threshold compression analysis for {metric}",
                method="Excess mass test with dip test",
                inputs=[f"metric_{metric}_distribution"],
                output=f"compression_{'detected' if d03.get('compression_detected') else 'not_detected'}",
                parameters={"method": "excess_mass + dip_test"},
                result={"compression_index": comp_idx},
                assumptions_met=True,
                confidence=0.88 if comp_idx > 0.5 else 0.7,
            )

            chain = ReasoningChain(
                chain_id=_hash_id(f"chain_d03_{metric}"),
                conclusion=f"Threshold compression in {metric} (index={comp_idx:.3f})",
                steps=[step],
                evidence_refs=[f"evidence_{metric}_compression"],
                spec_reference="docs/specifications/04_DETECTOR_SCIENTIFIC_SPECIFICATION.md",
                confidence=step.confidence,
            )

            finding = IntegrityFinding(
                finding_id=_hash_id(f"finding_d03_{metric}"),
                category="threshold_compression",
                metric=metric,
                detector="D-03",
                severity=severity,
                description=f"Threshold compression in {metric}: index={comp_idx:.3f}",
                evidence_refs=[f"evidence_{metric}_compression"],
                confidence=step.confidence,
                reasoning_chain=chain,
            )
            findings.append(finding)

    return findings


# ---------------------------------------------------------------------------
# Explanation generation
# ---------------------------------------------------------------------------


def explain_finding(finding: IntegrityFinding) -> FindingExplanation:
    """Generate deterministic explanation for a finding."""
    detector_descriptions = {
        "D-01": "Kolmogorov-Smirnov two-sample test for distribution drift",
        "D-02": "Pearson correlation analysis with multiple testing correction",
        "D-03": "Threshold compression detection via excess mass and dip tests",
    }

    detector_desc = detector_descriptions.get(finding.detector, finding.detector)

    what = f"Detector {finding.detector} identified {finding.category.replace('_', ' ')} in metric {finding.metric}"
    why = f"Statistical analysis revealed significant deviation: {finding.description}"
    certainty = f"Confidence level: {finding.confidence:.0%} ({_classify_confidence(finding.confidence).value})"
    det_ref = f"{finding.detector}: {detector_desc}"
    met_ref = f"Metric {finding.metric} analyzed across observation windows"
    obs_ref = f"Observations from metric {finding.metric} data points"
    evidence_ref = ", ".join(finding.evidence_refs) if finding.evidence_refs else "Evidence package"
    spec_ref = finding.reasoning_chain.spec_reference

    narrative = (
        f"Analysis of metric {finding.metric} using detector {finding.detector} "
        f"({detector_desc}) revealed {finding.category.replace('_', ' ')}. "
        f"{why}. "
        f"This finding has {finding.confidence:.0%} confidence "
        f"({_classify_confidence(finding.confidence).value}). "
        f"Severity: {finding.severity.value}."
    )

    return FindingExplanation(
        explanation_id=_hash_id(f"explanation_{finding.finding_id}"),
        finding_id=finding.finding_id,
        what_happened=what,
        why=why,
        how_certain=certainty,
        detector_reference=det_ref,
        metric_reference=met_ref,
        observation_reference=obs_ref,
        evidence_reference=evidence_ref,
        specification_reference=spec_ref,
        narrative=narrative,
    )


# ---------------------------------------------------------------------------
# Evidence graph construction
# ---------------------------------------------------------------------------


def build_evidence_graph(finding: IntegrityFinding) -> EvidenceGraph:
    """Construct deterministic evidence graph for a finding."""
    nodes: List[EvidenceNode] = []

    # Finding node
    finding_node = EvidenceNode(
        node_id=finding.finding_id,
        node_type="finding",
        label=f"{finding.category}: {finding.metric}",
        data={"severity": finding.severity.value, "confidence": finding.confidence},
    )
    nodes.append(finding_node)

    # Evidence nodes
    for ref in finding.evidence_refs:
        evidence_node = EvidenceNode(
            node_id=ref,
            node_type="evidence",
            label=f"Evidence: {ref}",
            data={"ref": ref},
            parent_ids=[finding.finding_id],
        )
        nodes.append(evidence_node)

    # Detector node
    detector_node = EvidenceNode(
        node_id=finding.detector,
        node_type="detector",
        label=f"Detector {finding.detector}",
        data={"detector": finding.detector},
        parent_ids=[finding.finding_id],
    )
    nodes.append(detector_node)

    # Metric node
    metric_node = EvidenceNode(
        node_id=f"metric_{finding.metric}",
        node_type="metric",
        label=f"Metric {finding.metric}",
        data={"metric": finding.metric},
        parent_ids=[finding.detector],
    )
    nodes.append(metric_node)

    # Observation node
    obs_node = EvidenceNode(
        node_id=f"obs_{finding.metric}",
        node_type="observation",
        label=f"Observations for {finding.metric}",
        parent_ids=[f"metric_{finding.metric}"],
    )
    nodes.append(obs_node)

    # Spec node
    spec_node = EvidenceNode(
        node_id="spec",
        node_type="spec",
        label=finding.reasoning_chain.spec_reference,
        data={"reference": finding.reasoning_chain.spec_reference},
        parent_ids=[finding.finding_id],
    )
    nodes.append(spec_node)

    return EvidenceGraph(
        graph_id=_hash_id(f"graph_{finding.finding_id}"),
        finding_id=finding.finding_id,
        nodes=nodes,
        root_node_id=finding.finding_id,
    )


# ---------------------------------------------------------------------------
# Certification
# ---------------------------------------------------------------------------


def certify_findings(
    findings: List[IntegrityFinding],
    confidence_score: float,
    evidence_completeness: float,
) -> List[CertificationResult]:
    """Generate deterministic certifications from findings."""
    certs: List[CertificationResult] = []

    # Certification 1: Repository Healthy
    high_sev = sum(1 for f in findings if f.severity == Severity.SEVERE)
    med_sev = sum(1 for f in findings if f.severity == Severity.MODERATE)

    if high_sev == 0 and med_sev <= 2:
        status = CertificationStatus.CERTIFIED
        reasoning = f"No severe findings. {med_sev} moderate findings within acceptable range."
    elif high_sev == 0:
        status = CertificationStatus.CONDITIONAL
        reasoning = f"No severe findings but {med_sev} moderate findings exceed threshold."
    else:
        status = CertificationStatus.FAILED
        reasoning = f"{high_sev} severe findings detected."

    certs.append(
        CertificationResult(
            certification_id=_hash_id("cert_healthy"),
            name="Repository Healthy",
            status=status,
            requirements=["No severe findings", "Moderate findings <= 2"],
            supporting_evidence=[f"finding_{f.finding_id}" for f in findings],
            confidence=confidence_score,
            failure_conditions=["Any severe finding", "More than 2 moderate findings"],
            reasoning=reasoning,
        )
    )

    # Certification 2: Measurement Drift Detected
    drift_findings = [f for f in findings if f.category == "distribution_drift"]
    if drift_findings:
        certs.append(
            CertificationResult(
                certification_id=_hash_id("cert_drift"),
                name="Measurement Drift Detected",
                status=CertificationStatus.CERTIFIED,
                requirements=["Drift events present in detector outputs"],
                supporting_evidence=[f"finding_{f.finding_id}" for f in drift_findings],
                confidence=max(f.confidence for f in drift_findings),
                failure_conditions=["No drift events"],
                reasoning=f"{len(drift_findings)} drift event(s) detected across metrics.",
            )
        )

    # Certification 3: Low Confidence
    if confidence_score < 0.6:
        certs.append(
            CertificationResult(
                certification_id=_hash_id("cert_low_conf"),
                name="Low Confidence",
                status=CertificationStatus.CERTIFIED,
                requirements=["Confidence score below 0.6"],
                supporting_evidence=[f"confidence_score_{confidence_score:.3f}"],
                confidence=1.0,
                failure_conditions=["Confidence score >= 0.6"],
                reasoning=f"Confidence score {confidence_score:.3f} is below the 0.6 threshold.",
            )
        )

    # Certification 4: Evidence Insufficient
    if evidence_completeness < 0.7:
        certs.append(
            CertificationResult(
                certification_id=_hash_id("cert_evidence"),
                name="Evidence Insufficient",
                status=CertificationStatus.CERTIFIED,
                requirements=["Evidence completeness below 0.7"],
                supporting_evidence=[f"evidence_completeness_{evidence_completeness:.3f}"],
                confidence=1.0,
                failure_conditions=["Evidence completeness >= 0.7"],
                reasoning=f"Evidence completeness {evidence_completeness:.3f} is below the 0.7 threshold.",
            )
        )

    # Certification 5: Benchmark Certified
    if confidence_score >= 0.8 and high_sev == 0:
        certs.append(
            CertificationResult(
                certification_id=_hash_id("cert_benchmark"),
                name="Benchmark Certified",
                status=CertificationStatus.CERTIFIED,
                requirements=["Confidence >= 0.8", "No severe findings"],
                supporting_evidence=[f"confidence_{confidence_score:.3f}", f"severe_{high_sev}"],
                confidence=confidence_score,
                failure_conditions=["Confidence < 0.8", "Any severe finding"],
                reasoning=f"Confidence {confidence_score:.3f} >= 0.8 and no severe findings.",
            )
        )

    return certs


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def determine_verdict(
    findings: List[IntegrityFinding],
    integrity_score: float,
    confidence_score: float,
) -> Verdict:
    """Determine overall verdict from findings and scores."""
    high_sev = sum(1 for f in findings if f.severity == Severity.SEVERE)
    med_sev = sum(1 for f in findings if f.severity == Severity.MODERATE)

    if high_sev > 0 or integrity_score < 0.4:
        value = VerdictValue.FAIL
        reasoning = f"FAIL: {high_sev} severe findings, integrity={integrity_score:.3f}"
        conf = 0.95
    elif med_sev > 2 or integrity_score < 0.6 or confidence_score < 0.5:
        value = VerdictValue.WARN
        reasoning = (
            f"WARN: {med_sev} moderate findings, integrity={integrity_score:.3f}, confidence={confidence_score:.3f}"
        )
        conf = 0.85
    else:
        value = VerdictValue.PASS
        reasoning = f"PASS: No severe findings, integrity={integrity_score:.3f}, confidence={confidence_score:.3f}"
        conf = 0.9

    return Verdict(
        value=value,
        reasoning=reasoning,
        supporting_findings=[f.finding_id for f in findings],
        confidence=conf,
    )


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------


def generate_assessment(
    assessment_type: str,
    findings: List[IntegrityFinding],
    integrity_score: float,
    confidence_score: float,
    evidence_completeness: float,
    certifications: List[CertificationResult],
    verdict: Verdict,
) -> Assessment:
    """Generate deterministic assessment."""
    dims: List[AssessmentDimension] = []

    # Dimension: Statistical Rigor
    rigor = confidence_score
    dims.append(
        AssessmentDimension(
            dimension="Statistical Rigor",
            score=rigor,
            level=_classify_level(rigor),
            reasoning=f"Confidence score {rigor:.3f} based on 6 multiplicative factors",
            evidence_refs=["confidence_score"],
        )
    )

    # Dimension: Evidence Completeness
    dims.append(
        AssessmentDimension(
            dimension="Evidence Completeness",
            score=evidence_completeness,
            level=_classify_level(evidence_completeness),
            reasoning=f"Evidence completeness {evidence_completeness:.3f}",
            evidence_refs=["evidence_package"],
        )
    )

    # Dimension: Finding Severity
    sev_score = 1.0 - (
        sum(1 for f in findings if f.severity == Severity.SEVERE) * 0.3
        + sum(1 for f in findings if f.severity == Severity.MODERATE) * 0.1
    )
    sev_score = max(0.0, min(1.0, sev_score))
    dims.append(
        AssessmentDimension(
            dimension="Finding Severity",
            score=sev_score,
            level=_classify_level(sev_score),
            reasoning=f"{sum(1 for f in findings if f.severity == Severity.SEVERE)} severe, "
            f"{sum(1 for f in findings if f.severity == Severity.MODERATE)} moderate findings",
            evidence_refs=[f"finding_{f.finding_id}" for f in findings],
        )
    )

    # Dimension: Integrity
    dims.append(
        AssessmentDimension(
            dimension="Integrity Score",
            score=integrity_score,
            level=_classify_level(integrity_score),
            reasoning=f"Integrity score {integrity_score:.3f}",
            evidence_refs=["integrity_score"],
        )
    )

    # Dimension: Certification Coverage
    cert_score = sum(1 for c in certifications if c.status == CertificationStatus.CERTIFIED) / max(
        len(certifications), 1
    )
    dims.append(
        AssessmentDimension(
            dimension="Certification Coverage",
            score=cert_score,
            level=_classify_level(cert_score),
            reasoning=f"{sum(1 for c in certifications if c.status == CertificationStatus.CERTIFIED)}/{len(certifications)} certifications passed",
            evidence_refs=[f"cert_{c.certification_id}" for c in certifications],
        )
    )

    overall = sum(d.score for d in dims) / len(dims) if dims else 0.0

    summary = (
        f"Assessment type: {assessment_type}. "
        f"Overall score: {overall:.3f} ({_classify_level(overall)}). "
        f"Verdict: {verdict.value.value}. "
        f"Findings: {len(findings)}. "
        f"Certifications: {sum(1 for c in certifications if c.status == CertificationStatus.CERTIFIED)}/{len(certifications)} passed."
    )

    return Assessment(
        assessment_id=_hash_id(f"assessment_{assessment_type}"),
        assessment_type=assessment_type,
        dimensions=dims,
        overall_score=overall,
        overall_level=_classify_level(overall),
        verdict=verdict,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Justified recommendations
# ---------------------------------------------------------------------------


def justify_recommendations(
    findings: List[IntegrityFinding],
    certifications: List[CertificationResult],
    verdict: Verdict,
) -> List[JustifiedRecommendation]:
    """Generate justified recommendations from findings."""
    recs: List[JustifiedRecommendation] = []

    for finding in findings:
        priority = (
            "high"
            if finding.severity == Severity.SEVERE
            else ("medium" if finding.severity == Severity.MODERATE else "low")
        )

        chain = ReasoningChain(
            chain_id=_hash_id(f"rec_chain_{finding.finding_id}"),
            conclusion=f"Recommendation driven by {finding.category} in {finding.metric}",
            steps=finding.reasoning_chain.steps,
            evidence_refs=finding.evidence_refs,
            spec_reference=finding.reasoning_chain.spec_reference,
            confidence=finding.confidence,
        )

        cert_impact = []
        for cert in certifications:
            if cert.status == CertificationStatus.FAILED:
                cert_impact.append(f"Affects {cert.name}: {cert.reasoning}")

        rec = JustifiedRecommendation(
            recommendation_id=_hash_id(f"rec_{finding.finding_id}"),
            category=finding.category,
            priority=priority,
            title=f"Investigate {finding.category.replace('_', ' ')} in {finding.metric}",
            description=f"Review {finding.category.replace('_', ' ')} detected by {finding.detector} in metric {finding.metric}",
            reason=finding.description,
            evidence=finding.evidence_refs,
            confidence=finding.confidence,
            affected_metrics=[finding.metric],
            affected_detectors=[finding.detector],
            certification_impact=cert_impact,
            reasoning_chain=chain,
        )
        recs.append(rec)

    return recs
