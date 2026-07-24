"""Scientific Assurance Framework tests."""

from __future__ import annotations

from miie.assurance.assumptions import (
    _check_ks_assumptions,
    _check_pearson_assumptions,
    _check_sample_size,
    check_detector_assumptions,
)
from miie.assurance.audit_trail import build_audit_trail
from miie.assurance.engine import build_assurance_report
from miie.assurance.limitations import build_limitation_report
from miie.assurance.models import (
    AssumptionStatus,
    LimitationCategory,
    SufficiencyStatus,
    ThreatSeverity,
)
from miie.assurance.sufficiency import assess_evidence_sufficiency
from miie.assurance.threats import assess_threats

# ---------------------------------------------------------------------------
# Assumption Checks
# ---------------------------------------------------------------------------


class TestSampleSizeCheck:
    def test_satisfied(self):
        result = _check_sample_size(50, 20)
        assert result.status == AssumptionStatus.SATISFIED
        assert result.test_statistic == 50.0

    def test_likely_satisfied(self):
        result = _check_sample_size(18, 20)
        assert result.status == AssumptionStatus.LIKELY_SATISFIED

    def test_uncertain(self):
        result = _check_sample_size(10, 20)
        assert result.status == AssumptionStatus.UNCERTAIN

    def test_violated(self):
        result = _check_sample_size(2, 20)
        assert result.status == AssumptionStatus.VIOLATED

    def test_exact_threshold(self):
        result = _check_sample_size(20, 20)
        assert result.status == AssumptionStatus.SATISFIED


class TestKSAssumptions:
    def test_independent_data(self):
        import random

        random.seed(42)
        w1 = [random.gauss(0, 1) for _ in range(50)]
        w2 = [random.gauss(0.5, 1) for _ in range(50)]
        checks = _check_ks_assumptions(w1, w2)
        assert len(checks) >= 2  # sample_size + independence
        assert checks[0].name == "minimum_sample_size"

    def test_small_sample(self):
        checks = _check_ks_assumptions([1, 2], [3, 4])
        assert any(c.status == AssumptionStatus.VIOLATED for c in checks)


class TestPearsonAssumptions:
    def test_linear_data(self):
        x = list(range(10))
        y = [2 * i + 1 for i in range(10)]
        checks = _check_pearson_assumptions(x, y)
        assert len(checks) >= 2
        linearity = [c for c in checks if c.name == "linearity"]
        assert len(linearity) == 1
        assert linearity[0].status == AssumptionStatus.LIKELY_SATISFIED

    def test_no_relationship(self):
        import random

        random.seed(42)
        x = [random.gauss(0, 1) for _ in range(20)]
        y = [random.gauss(0, 1) for _ in range(20)]
        checks = _check_pearson_assumptions(x, y)
        linearity = [c for c in checks if c.name == "linearity"]
        if linearity:
            assert linearity[0].status in (AssumptionStatus.UNCERTAIN, AssumptionStatus.LIKELY_VIOLATED)


class TestDetectorAssumptions:
    def test_d01(self):
        report = check_detector_assumptions("D-01", "M-01", {}, {"w1": list(range(30)), "w2": list(range(20, 50))})
        assert report.detector_id == "D-01"
        assert report.total_count >= 2
        assert report.confidence_impact > 0

    def test_d02(self):
        report = check_detector_assumptions("D-02", "M-02", {}, {"x": list(range(20)), "y": [2 * i for i in range(20)]})
        assert report.detector_id == "D-02"
        assert report.total_count >= 2

    def test_d03(self):
        report = check_detector_assumptions("D-03", "M-03", {}, {"values": list(range(30)), "threshold": 0.5})
        assert report.detector_id == "D-03"
        assert report.total_count >= 2

    def test_no_data(self):
        report = check_detector_assumptions("D-01", "M-01", {}, {})
        assert report.total_count == 1
        assert report.assumptions[0].status == AssumptionStatus.NOT_CHECKABLE


# ---------------------------------------------------------------------------
# Sufficiency
# ---------------------------------------------------------------------------


class TestSufficiency:
    def test_sufficient(self):
        report = assess_evidence_sufficiency(
            "D-01",
            "M-01",
            {"observations_total": 100, "observations_valid": 90, "sample_size": 50, "power": 0.9, "effect_size": 0.5},
        )
        assert report.status == SufficiencyStatus.SUFFICIENT
        assert report.met_count == report.total_count

    def test_insufficient(self):
        report = assess_evidence_sufficiency(
            "D-01",
            "M-01",
            {"observations_total": 100, "observations_valid": 50, "sample_size": 5, "power": 0.3},
        )
        assert report.status in (SufficiencyStatus.INSUFFICIENT, SufficiencyStatus.CONDITIONALLY_SUFFICIENT)

    def test_no_data(self):
        report = assess_evidence_sufficiency("D-01", "M-01", {})
        assert report.status == SufficiencyStatus.INSUFFICIENT

    def test_gaps_identified(self):
        report = assess_evidence_sufficiency(
            "D-01",
            "M-01",
            {"observations_total": 100, "observations_valid": 50},
        )
        assert len(report.gaps) > 0


# ---------------------------------------------------------------------------
# Threats
# ---------------------------------------------------------------------------


class TestThreats:
    def test_basic_threats(self):
        assessment = assess_threats("D-01", "M-01", {"sample_size": 50})
        assert assessment.total_count >= 3
        assert assessment.overall_risk in ("low", "medium", "high")

    def test_small_sample_threat(self):
        assessment = assess_threats("D-01", "M-01", {"sample_size": 5})
        high = [t for t in assessment.threats if t.severity == ThreatSeverity.HIGH]
        assert len(high) >= 1

    def test_multiple_comparisons_threat(self):
        assessment = assess_threats("D-01", "M-01", {"num_tests_conducted": 10})
        multi = [t for t in assessment.threats if t.name == "multiple_comparisons"]
        assert len(multi) == 1
        assert multi[0].severity == ThreatSeverity.HIGH


# ---------------------------------------------------------------------------
# Limitations
# ---------------------------------------------------------------------------


class TestLimitations:
    def test_basic_limitations(self):
        report = build_limitation_report("D-01", "M-01", {"sample_size": 50})
        assert report.total_count >= 3
        assert "methodological" in report.by_category

    def test_small_sample_limitation(self):
        report = build_limitation_report("D-01", "M-01", {"sample_size": 10})
        sample_lims = [lm for lm in report.limitations if lm.category == LimitationCategory.SAMPLE_SIZE]
        assert len(sample_lims) == 1

    def test_missing_data_limitation(self):
        report = build_limitation_report("D-01", "M-01", {"missing_data_pct": 0.25})
        missing = [lm for lm in report.limitations if lm.category == LimitationCategory.DATA_QUALITY]
        assert len(missing) == 1


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------


class TestAuditTrail:
    def test_trail_construction(self):
        trail = build_audit_trail(
            finding_id="f1",
            finding_data={"title": "Test finding"},
            reasoning_data={"explanation": "Because"},
            evidence_data={"summary": "Evidence", "observations_total": 10, "observations_valid": 8},
            detector_id="D-01",
            metric="M-01",
            confidence_data={"overall": 0.9},
            assumption_data={"satisfied": 3, "total": 3, "status": "satisfied"},
            ground_truth_data={"status": "validated"},
        )
        assert len(trail.nodes) == 12
        assert trail.root_node_id == trail.nodes[0].node_id
        node_types = [n.node_type for n in trail.nodes]
        assert "finding" in node_types
        assert "certification" in node_types
        assert "ground_truth" in node_types

    def test_trail_node_types(self):
        trail = build_audit_trail(
            finding_id="f2",
            finding_data={"title": "X"},
            reasoning_data={"explanation": "Y"},
            evidence_data={"summary": "Z"},
            detector_id="D-02",
            metric="M-02",
            confidence_data={"overall": 0.7},
            assumption_data={"satisfied": 2, "total": 3, "status": "uncertain"},
            ground_truth_data={"status": "not_validated"},
        )
        expected = {
            "finding",
            "reasoning",
            "evidence",
            "detector",
            "metric",
            "observation",
            "confidence",
            "validation",
            "assumptions",
            "ground_truth",
            "specification",
            "certification",
        }
        assert set(n.node_type for n in trail.nodes) == expected


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class TestEngine:
    def test_full_assurance_report(self):
        findings = [
            {
                "finding_id": "f1",
                "detector_id": "D-01",
                "metric": "M-01",
                "evidence": {"effect_size": 0.5, "observations_total": 100, "observations_valid": 90},
                "confidence": {"overall": 0.85},
                "reasoning": {"explanation": "KS test significant"},
                "ground_truth": {"status": "validated"},
            },
        ]
        context = {"sample_size": 50, "power": 0.85}
        report = build_assurance_report(findings, context)
        assert report.overall_assurance in ("STRONG", "MODERATE", "WEAK", "INSUFFICIENT")
        assert 0 <= report.overall_confidence <= 1
        assert len(report.assumption_reports) == 1
        assert len(report.sufficiency_reports) == 1
        assert len(report.audit_trails) == 1

    def test_multiple_findings(self):
        findings = [
            {
                "finding_id": f"f{i}",
                "detector_id": "D-01",
                "metric": "M-01",
                "evidence": {},
                "confidence": {"overall": 0.7},
                "reasoning": {},
                "ground_truth": {},
            }
            for i in range(5)
        ]
        report = build_assurance_report(findings, {"sample_size": 30})
        assert len(report.assumption_reports) == 5
        assert len(report.audit_trails) == 5

    def test_empty_findings(self):
        report = build_assurance_report([], {})
        assert report.overall_confidence >= 0
