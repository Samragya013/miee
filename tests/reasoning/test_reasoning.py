"""Tests for MIIE reasoning layer."""

import pytest

from miie.reasoning.engine import (
    _classify_confidence,
    _classify_level,
    _classify_severity,
    _hash_id,
    build_evidence_graph,
    certify_findings,
    determine_verdict,
    explain_finding,
    extract_findings,
    generate_assessment,
    justify_recommendations,
)
from miie.reasoning.models import (
    Assessment,
    AssessmentDimension,
    CertificationResult,
    CertificationStatus,
    ConfidenceLevel,
    IntegrityFinding,
    ReasoningChain,
    ReasoningStep,
    Severity,
    Verdict,
    VerdictValue,
)

# ---------------------------------------------------------------------------
# Model construction tests
# ---------------------------------------------------------------------------


class TestReasoningStep:
    def test_construction(self):
        step = ReasoningStep(
            step_id="s1",
            description="Test step",
            method="KS test",
            inputs=["input1"],
            output="output1",
        )
        assert step.step_id == "s1"
        assert step.method == "KS test"
        assert step.assumptions_met is True
        assert step.confidence == 1.0

    def test_frozen(self):
        step = ReasoningStep(step_id="s1", description="d", method="m", inputs=[], output="o")
        with pytest.raises(AttributeError):
            step.step_id = "changed"


class TestReasoningChain:
    def test_construction(self):
        chain = ReasoningChain(
            chain_id="c1",
            conclusion="Drift detected",
            steps=[],
            evidence_refs=["e1"],
            spec_reference="spec.md",
        )
        assert chain.conclusion == "Drift detected"
        assert chain.confidence == 1.0


class TestIntegrityFinding:
    def test_construction(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        finding = IntegrityFinding(
            finding_id="f1",
            category="distribution_drift",
            metric="M-01",
            detector="D-01",
            severity=Severity.MODERATE,
            description="Drift in M-01",
            evidence_refs=["e1"],
            confidence=0.85,
            reasoning_chain=chain,
        )
        assert finding.detector == "D-01"
        assert finding.severity == Severity.MODERATE


class TestCertificationResult:
    def test_construction(self):
        cert = CertificationResult(
            certification_id="c1",
            name="Healthy",
            status=CertificationStatus.CERTIFIED,
            requirements=["req1"],
            supporting_evidence=["ev1"],
            confidence=0.9,
            failure_conditions=["fail1"],
            reasoning="All good",
        )
        assert cert.status == CertificationStatus.CERTIFIED


class TestVerdict:
    def test_construction(self):
        verdict = Verdict(
            value=VerdictValue.PASS,
            reasoning="No issues",
            supporting_findings=[],
            confidence=0.95,
        )
        assert verdict.value == VerdictValue.PASS


class TestAssessment:
    def test_construction(self):
        dim = AssessmentDimension(dimension="Rigor", score=0.85, level="high", reasoning="Good", evidence_refs=[])
        verdict = Verdict(value=VerdictValue.PASS, reasoning="ok", supporting_findings=[], confidence=0.9)
        assessment = Assessment(
            assessment_id="a1",
            assessment_type="executive",
            dimensions=[dim],
            overall_score=0.85,
            overall_level="high",
            verdict=verdict,
            summary="Good",
        )
        assert assessment.overall_score == 0.85


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------


class TestUtilities:
    def test_hash_id_deterministic(self):
        assert _hash_id("test") == _hash_id("test")
        assert _hash_id("test") != _hash_id("other")

    def test_classify_severity_mild(self):
        assert _classify_severity(0.1) == Severity.MILD

    def test_classify_severity_moderate(self):
        assert _classify_severity(0.45) == Severity.MODERATE

    def test_classify_severity_severe(self):
        assert _classify_severity(0.8) == Severity.SEVERE

    def test_classify_confidence_high(self):
        assert _classify_confidence(0.9) == ConfidenceLevel.HIGH

    def test_classify_confidence_medium(self):
        assert _classify_confidence(0.6) == ConfidenceLevel.MEDIUM

    def test_classify_confidence_low(self):
        assert _classify_confidence(0.3) == ConfidenceLevel.LOW

    def test_classify_level_high(self):
        assert _classify_level(0.85) == "high"

    def test_classify_level_medium(self):
        assert _classify_level(0.6) == "medium"

    def test_classify_level_low(self):
        assert _classify_level(0.3) == "low"


# ---------------------------------------------------------------------------
# Finding extraction tests
# ---------------------------------------------------------------------------


class TestExtractFindings:
    def test_no_findings_when_clean(self):
        outputs = {
            "D-01": {"drift_detected": False},
            "D-02": {"breakdown_detected": False},
            "D-03": {"compression_detected": False},
        }
        findings = extract_findings(outputs, {}, {})
        assert len(findings) == 0

    def test_d01_findings(self):
        outputs = {
            "D-01": {
                "drift_detected": True,
                "drift_events": [{"metric": "M-01", "ks_statistic": 0.35, "psi_value": 0.28}],
            }
        }
        findings = extract_findings(outputs, {}, {})
        assert len(findings) == 1
        assert findings[0].detector == "D-01"
        assert findings[0].category == "distribution_drift"
        assert findings[0].metric == "M-01"

    def test_d02_findings(self):
        outputs = {
            "D-02": {
                "breakdown_detected": True,
                "breakdown_events": [{"metric_pair": ("M-01", "M-02"), "delta_pearson": 0.45}],
            }
        }
        findings = extract_findings(outputs, {}, {})
        assert len(findings) == 1
        assert findings[0].detector == "D-02"
        assert findings[0].category == "correlation_breakdown"

    def test_d03_findings(self):
        outputs = {
            "D-03": {
                "compression_detected": True,
                "compression_events": [{"metric": "M-03", "compression_index": 0.65}],
            }
        }
        findings = extract_findings(outputs, {}, {})
        assert len(findings) == 1
        assert findings[0].detector == "D-03"
        assert findings[0].category == "threshold_compression"

    def test_multiple_findings(self):
        outputs = {
            "D-01": {
                "drift_detected": True,
                "drift_events": [{"metric": "M-01", "ks_statistic": 0.4, "psi_value": 0.3}],
            },
            "D-02": {
                "breakdown_detected": True,
                "breakdown_events": [{"metric_pair": ("M-01", "M-03"), "delta_pearson": 0.5}],
            },
            "D-03": {
                "compression_detected": True,
                "compression_events": [{"metric": "M-02", "compression_index": 0.7}],
            },
        }
        findings = extract_findings(outputs, {}, {})
        assert len(findings) == 3

    def test_finding_has_reasoning_chain(self):
        outputs = {
            "D-01": {
                "drift_detected": True,
                "drift_events": [{"metric": "M-01", "ks_statistic": 0.4, "psi_value": 0.3}],
            }
        }
        findings = extract_findings(outputs, {}, {})
        assert findings[0].reasoning_chain is not None
        assert len(findings[0].reasoning_chain.steps) == 1


# ---------------------------------------------------------------------------
# Explanation tests
# ---------------------------------------------------------------------------


class TestExplainFinding:
    def test_explanation_complete(self):
        chain = ReasoningChain(
            chain_id="c1", conclusion="Drift detected", steps=[], evidence_refs=["e1"], spec_reference="spec.md"
        )
        finding = IntegrityFinding(
            finding_id="f1",
            category="distribution_drift",
            metric="M-01",
            detector="D-01",
            severity=Severity.MODERATE,
            description="Drift in M-01",
            evidence_refs=["e1"],
            confidence=0.85,
            reasoning_chain=chain,
        )
        explanation = explain_finding(finding)
        assert explanation.finding_id == "f1"
        assert "M-01" in explanation.what_happened
        assert "D-01" in explanation.detector_reference
        assert len(explanation.narrative) > 0

    def test_explanation_frozen(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        finding = IntegrityFinding(
            finding_id="f1",
            category="drift",
            metric="M-01",
            detector="D-01",
            severity=Severity.MILD,
            description="d",
            evidence_refs=[],
            confidence=0.8,
            reasoning_chain=chain,
        )
        explanation = explain_finding(finding)
        with pytest.raises(AttributeError):
            explanation.narrative = "changed"


# ---------------------------------------------------------------------------
# Evidence graph tests
# ---------------------------------------------------------------------------


class TestEvidenceGraph:
    def test_graph_construction(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=["e1"], spec_reference="s")
        finding = IntegrityFinding(
            finding_id="f1",
            category="drift",
            metric="M-01",
            detector="D-01",
            severity=Severity.MILD,
            description="d",
            evidence_refs=["e1"],
            confidence=0.8,
            reasoning_chain=chain,
        )
        graph = build_evidence_graph(finding)
        assert graph.finding_id == "f1"
        assert len(graph.nodes) >= 4  # finding, evidence, detector, metric, obs, spec
        assert graph.root_node_id == "f1"

    def test_graph_node_types(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=["e1"], spec_reference="s")
        finding = IntegrityFinding(
            finding_id="f1",
            category="drift",
            metric="M-01",
            detector="D-01",
            severity=Severity.MILD,
            description="d",
            evidence_refs=["e1"],
            confidence=0.8,
            reasoning_chain=chain,
        )
        graph = build_evidence_graph(finding)
        node_types = {n.node_type for n in graph.nodes}
        assert "finding" in node_types
        assert "evidence" in node_types
        assert "detector" in node_types
        assert "metric" in node_types
        assert "spec" in node_types


# ---------------------------------------------------------------------------
# Certification tests
# ---------------------------------------------------------------------------


class TestCertification:
    def test_healthy_certification(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        findings = [
            IntegrityFinding(
                finding_id="f1",
                category="drift",
                metric="M-01",
                detector="D-01",
                severity=Severity.MILD,
                description="d",
                evidence_refs=[],
                confidence=0.8,
                reasoning_chain=chain,
            )
        ]
        certs = certify_findings(findings, confidence_score=0.85, evidence_completeness=0.9)
        names = [c.name for c in certs]
        assert "Repository Healthy" in names

    def test_failed_when_severe(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        findings = [
            IntegrityFinding(
                finding_id="f1",
                category="drift",
                metric="M-01",
                detector="D-01",
                severity=Severity.SEVERE,
                description="d",
                evidence_refs=[],
                confidence=0.8,
                reasoning_chain=chain,
            )
        ]
        certs = certify_findings(findings, confidence_score=0.85, evidence_completeness=0.9)
        healthy = [c for c in certs if c.name == "Repository Healthy"]
        assert healthy[0].status == CertificationStatus.FAILED

    def test_low_confidence_cert(self):
        certs = certify_findings([], confidence_score=0.4, evidence_completeness=0.9)
        names = [c.name for c in certs]
        assert "Low Confidence" in names

    def test_benchmark_certified(self):
        certs = certify_findings([], confidence_score=0.9, evidence_completeness=0.95)
        names = [c.name for c in certs]
        assert "Benchmark Certified" in names


# ---------------------------------------------------------------------------
# Verdict tests
# ---------------------------------------------------------------------------


class TestVerdictLogic:
    def test_pass_verdict(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        findings = [
            IntegrityFinding(
                finding_id="f1",
                category="drift",
                metric="M-01",
                detector="D-01",
                severity=Severity.MILD,
                description="d",
                evidence_refs=[],
                confidence=0.8,
                reasoning_chain=chain,
            )
        ]
        verdict = determine_verdict(findings, integrity_score=0.85, confidence_score=0.9)
        assert verdict.value == VerdictValue.PASS

    def test_fail_verdict(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        findings = [
            IntegrityFinding(
                finding_id="f1",
                category="drift",
                metric="M-01",
                detector="D-01",
                severity=Severity.SEVERE,
                description="d",
                evidence_refs=[],
                confidence=0.8,
                reasoning_chain=chain,
            )
        ]
        verdict = determine_verdict(findings, integrity_score=0.3, confidence_score=0.9)
        assert verdict.value == VerdictValue.FAIL

    def test_warn_verdict(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        findings = [
            IntegrityFinding(
                finding_id=f"f{i}",
                category="drift",
                metric=f"M-0{i}",
                detector="D-01",
                severity=Severity.MODERATE,
                description="d",
                evidence_refs=[],
                confidence=0.8,
                reasoning_chain=chain,
            )
            for i in range(4)
        ]
        verdict = determine_verdict(findings, integrity_score=0.55, confidence_score=0.55)
        assert verdict.value == VerdictValue.WARN


# ---------------------------------------------------------------------------
# Assessment tests
# ---------------------------------------------------------------------------


class TestAssessmentLogic:
    def test_assessment_construction(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=[], spec_reference="s")
        findings = [
            IntegrityFinding(
                finding_id="f1",
                category="drift",
                metric="M-01",
                detector="D-01",
                severity=Severity.MILD,
                description="d",
                evidence_refs=[],
                confidence=0.8,
                reasoning_chain=chain,
            )
        ]
        certs = certify_findings(findings, 0.85, 0.9)
        verdict = determine_verdict(findings, 0.85, 0.9)
        assessment = generate_assessment("executive", findings, 0.85, 0.9, 0.9, certs, verdict)
        assert assessment.assessment_type == "executive"
        assert len(assessment.dimensions) == 5
        assert assessment.overall_score > 0


# ---------------------------------------------------------------------------
# Justified recommendation tests
# ---------------------------------------------------------------------------


class TestJustifiedRecommendations:
    def test_rec_from_findings(self):
        chain = ReasoningChain(chain_id="c1", conclusion="x", steps=[], evidence_refs=["e1"], spec_reference="s")
        findings = [
            IntegrityFinding(
                finding_id="f1",
                category="drift",
                metric="M-01",
                detector="D-01",
                severity=Severity.MODERATE,
                description="d",
                evidence_refs=["e1"],
                confidence=0.85,
                reasoning_chain=chain,
            )
        ]
        certs = certify_findings(findings, 0.85, 0.9)
        verdict = determine_verdict(findings, 0.85, 0.9)
        recs = justify_recommendations(findings, certs, verdict)
        assert len(recs) == 1
        assert recs[0].affected_metrics == ["M-01"]
        assert recs[0].affected_detectors == ["D-01"]
        assert recs[0].reasoning_chain is not None
