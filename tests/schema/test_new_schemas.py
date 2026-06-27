"""
Tests for the new/updated MIIE schema classes.

Covers: D01Output, D02Output, D03Output, DetectorResults (typed),
        Explanation, ExplanationReport, BenchmarkRun, ConfusionMatrix,
        EvaluationResult, GroundTruthLabel, GroundTruthInput.
"""

import pytest

from miie.schemas.models import (
    BenchmarkRun,
    ConfusionMatrix,
    D01Output,
    D02Output,
    D03Output,
    DetectorResult,
    DetectorResults,
    EvaluationResult,
    Explanation,
    ExplanationReport,
    GroundTruthInput,
    GroundTruthLabel,
)

# ---------------------------------------------------------------------------
# D01Output
# ---------------------------------------------------------------------------


class TestD01Output:
    def test_valid_construction(self):
        out = D01Output(
            ks_statistic=0.12,
            ks_p_value=0.04,
            psi_value=0.08,
            direction="mean_shift",
            severity=0.6,
            flagged=True,
        )
        assert out.flagged is True
        assert out.severity == 0.6

    def test_valid_directions(self):
        for d in ("mean_shift", "variance_collapse", "shape_change"):
            out = D01Output(
                ks_statistic=0.1,
                ks_p_value=0.05,
                psi_value=0.1,
                direction=d,
                severity=0.5,
                flagged=False,
            )
            assert out.direction == d

    def test_invalid_direction(self):
        with pytest.raises(ValueError, match="direction"):
            D01Output(
                ks_statistic=0.1,
                ks_p_value=0.05,
                psi_value=0.1,
                direction="invalid",
                severity=0.5,
                flagged=False,
            )

    def test_severity_out_of_range(self):
        with pytest.raises(ValueError, match="severity"):
            D01Output(
                ks_statistic=0.1,
                ks_p_value=0.05,
                psi_value=0.1,
                direction="mean_shift",
                severity=1.5,
                flagged=False,
            )


# ---------------------------------------------------------------------------
# D02Output
# ---------------------------------------------------------------------------


class TestD02Output:
    def test_valid_construction(self):
        out = D02Output(
            pearson_r=0.85,
            spearman_r=0.82,
            fisher_z_ci=(0.7, 0.9),
            breakdown_type="sudden_drop",
            delta_r=-0.3,
            severity=0.7,
            flagged=True,
        )
        assert out.breakdown_type == "sudden_drop"

    def test_none_breakdown_type(self):
        out = D02Output(
            pearson_r=0.9,
            spearman_r=0.88,
            fisher_z_ci=(0.8, 0.95),
            breakdown_type=None,
            delta_r=0.0,
            severity=0.2,
            flagged=False,
        )
        assert out.breakdown_type is None

    def test_valid_breakdown_types(self):
        for bt in (
            "sudden_drop",
            "sign_reversal",
            "gradual_erosion",
            "confidence_exclusion",
        ):
            out = D02Output(
                pearson_r=0.5,
                spearman_r=0.5,
                fisher_z_ci=(0.4, 0.6),
                breakdown_type=bt,
                delta_r=0.1,
                severity=0.3,
                flagged=False,
            )
            assert out.breakdown_type == bt

    def test_invalid_breakdown_type(self):
        with pytest.raises(ValueError, match="breakdown_type"):
            D02Output(
                pearson_r=0.5,
                spearman_r=0.5,
                fisher_z_ci=(0.4, 0.6),
                breakdown_type="unknown",
                delta_r=0.1,
                severity=0.3,
                flagged=False,
            )

    def test_severity_out_of_range(self):
        with pytest.raises(ValueError, match="severity"):
            D02Output(
                pearson_r=0.5,
                spearman_r=0.5,
                fisher_z_ci=(0.4, 0.6),
                breakdown_type=None,
                delta_r=0.1,
                severity=-0.1,
                flagged=False,
            )


# ---------------------------------------------------------------------------
# D03Output
# ---------------------------------------------------------------------------


class TestD03Output:
    def test_valid_construction(self):
        out = D03Output(
            excess_mass_z=2.5,
            excess_mass_flag=True,
            dip_test_p_value=0.01,
            multimodal_flag=True,
            compression_index=0.4,
            threshold=1.0,
            severity=0.8,
            flagged=True,
        )
        assert out.flagged is True
        assert out.multimodal_flag is True

    def test_severity_out_of_range(self):
        with pytest.raises(ValueError, match="severity"):
            D03Output(
                excess_mass_z=1.0,
                excess_mass_flag=False,
                dip_test_p_value=0.5,
                multimodal_flag=False,
                compression_index=0.1,
                threshold=1.0,
                severity=2.0,
                flagged=False,
            )


# ---------------------------------------------------------------------------
# DetectorResults (typed)
# ---------------------------------------------------------------------------


class TestDetectorResults:
    def test_empty_construction(self):
        dr = DetectorResults()
        assert dr.d_01 == {}
        assert dr.d_02 == {}
        assert dr.d_03 == {}

    def test_valid_typed_fields(self):
        d01_out = D01Output(
            ks_statistic=0.1,
            ks_p_value=0.05,
            psi_value=0.1,
            direction="mean_shift",
            severity=0.5,
            flagged=True,
        )
        dr = DetectorResults(
            d_01={"M-01": {"w01-w02": d01_out}},
        )
        assert "M-01" in dr.d_01
        assert dr.d_01["M-01"]["w01-w02"].flagged is True

    def test_legacy_detector_outputs_still_works(self):
        dr = DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})
        assert len(dr.detector_outputs) == 3

    def test_full_nested_d03(self):
        d03_out = D03Output(
            excess_mass_z=1.0,
            excess_mass_flag=False,
            dip_test_p_value=0.5,
            multimodal_flag=False,
            compression_index=0.1,
            threshold=1.0,
            severity=0.3,
            flagged=False,
        )
        dr = DetectorResults(d_03={"M-02": {"0.5": {"w01": d03_out}}})
        assert dr.d_03["M-02"]["0.5"]["w01"].severity == 0.3


# ---------------------------------------------------------------------------
# Explanation / ExplanationReport
# ---------------------------------------------------------------------------


class TestExplanation:
    def test_valid_construction(self):
        exp = Explanation(
            metric_id="M-01",
            detector_id="D-01",
            narrative="Coverage dropped significantly",
            severity="severe",
            evidence_refs=["ref_001"],
            confidence="high",
            rule_fired="drift_threshold",
        )
        assert exp.severity == "severe"
        assert exp.confidence == "high"

    def test_invalid_severity(self):
        with pytest.raises(ValueError, match="severity"):
            Explanation(
                metric_id="M-01",
                detector_id="D-01",
                narrative="x",
                severity="critical",
                evidence_refs=[],
                confidence="high",
                rule_fired="r",
            )

    def test_invalid_confidence(self):
        with pytest.raises(ValueError, match="confidence"):
            Explanation(
                metric_id="M-01",
                detector_id="D-01",
                narrative="x",
                severity="mild",
                evidence_refs=[],
                confidence="certain",
                rule_fired="r",
            )


class TestExplanationReport:
    def test_empty_report(self):
        report = ExplanationReport()
        assert report.explanations == []
        assert report.summary == ""
        assert report.recommendations == []

    def test_report_with_explanations(self):
        exp = Explanation(
            metric_id="M-01",
            detector_id="D-01",
            narrative="Test",
            severity="mild",
            evidence_refs=[],
            confidence="medium",
            rule_fired="rule_1",
        )
        report = ExplanationReport(
            explanations=[exp],
            summary="One mild issue found",
            recommendations=["Monitor coverage"],
        )
        assert len(report.explanations) == 1
        assert report.summary == "One mild issue found"

    def test_report_legacy_narratives(self):
        report = ExplanationReport(narratives=["old style narrative"])
        assert report.narratives == ["old style narrative"]

    def test_invalid_explanation_type(self):
        with pytest.raises(ValueError, match="explanations"):
            ExplanationReport(explanations=["not an Explanation"])


# ---------------------------------------------------------------------------
# BenchmarkRun
# ---------------------------------------------------------------------------


class TestBenchmarkRun:
    def test_empty_construction(self):
        br = BenchmarkRun()
        assert br.run_id == ""
        assert br.predictions == {}

    def test_full_construction(self):
        br = BenchmarkRun(
            run_id="run-001",
            suite_id="suite-001",
            detector_id="D-01",
            detector_version="1.0.0",
            seed=42,
            started_at="2026-01-01T00:00:00Z",
            completed_at="2026-01-01T00:05:00Z",
            predictions={"repo_001": {"M-01": {"w01-w02": True}}},
            timing={"repo_001": 1.23},
            environment={
                "miie_version": "1.0.0",
                "python_version": "3.11",
                "platform": "linux",
            },
        )
        assert br.run_id == "run-001"
        assert br.seed == 42
        assert br.timing["repo_001"] == 1.23

    def test_legacy_metadata(self):
        br = BenchmarkRun(
            predictions={"D-01": [0.8, 0.75]},
            metadata={"suite_id": "s1", "seed": 42},
        )
        assert br.metadata["suite_id"] == "s1"
        assert br.predictions["D-01"] == [0.8, 0.75]

    def test_invalid_detector_id(self):
        with pytest.raises(ValueError, match="detector_id"):
            BenchmarkRun(detector_id="D-04")


# ---------------------------------------------------------------------------
# ConfusionMatrix / EvaluationResult
# ---------------------------------------------------------------------------


class TestConfusionMatrix:
    def test_valid_construction(self):
        cm = ConfusionMatrix(tp=80, fp=10, tn=85, fn=5)
        assert cm.tp == 80
        assert cm.fn == 5

    def test_negative_value(self):
        with pytest.raises(ValueError, match="tp"):
            ConfusionMatrix(tp=-1, fp=0, tn=0, fn=0)

    def test_defaults(self):
        cm = ConfusionMatrix()
        assert cm.tp == 0 and cm.fp == 0 and cm.tn == 0 and cm.fn == 0


class TestEvaluationResult:
    def test_legacy_construction(self):
        er = EvaluationResult(accuracy=0.92, precision=0.89, recall=0.94, f1_score=0.91)
        assert er.accuracy == 0.92
        assert er.f1_score == 0.91

    def test_full_construction(self):
        cm = ConfusionMatrix(tp=80, fp=10, tn=85, fn=5)
        er = EvaluationResult(
            suite_id="suite-001",
            detector_id="D-01",
            detector_version="1.0.0",
            metrics={
                "accuracy": 0.92,
                "precision": 0.89,
                "recall": 0.94,
                "f1": 0.91,
                "auc_roc": 0.95,
                "auc_pr": 0.93,
                "fpr": 0.10,
                "fnr": 0.06,
            },
            confusion_matrix=cm,
            per_dataset_results={"repo_001": {"accuracy": 0.95}},
        )
        assert er.metrics["auc_roc"] == 0.95
        assert er.confusion_matrix.tp == 80
        assert er.per_dataset_results["repo_001"]["accuracy"] == 0.95

    def test_accuracy_out_of_range(self):
        with pytest.raises(ValueError, match="accuracy"):
            EvaluationResult(accuracy=1.5)

    def test_metrics_out_of_range(self):
        with pytest.raises(ValueError, match="metrics"):
            EvaluationResult(metrics={"f1": 2.0})

    def test_empty_construction(self):
        er = EvaluationResult()
        assert er.accuracy == 0.0
        assert er.metrics == {}


# ---------------------------------------------------------------------------
# GroundTruthLabel / GroundTruthInput
# ---------------------------------------------------------------------------


class TestGroundTruthLabel:
    def test_valid_construction(self):
        label = GroundTruthLabel(
            repo_id="repo_001",
            metric_id="M-01",
            label=True,
            event_type="MDE-01",
            severity="severe",
            evidence_refs=["ref_001"],
            annotator_agreement=0.9,
        )
        assert label.repo_id == "repo_001"
        assert label.event_type == "MDE-01"

    def test_valid_all_event_types(self):
        for et in ("MDE-01", "MDE-02", "MDE-03", "MDE-04"):
            label = GroundTruthLabel(repo_id="repo_002", metric_id="M-01", label=False, event_type=et)
            assert label.event_type == et

    def test_invalid_repo_id(self):
        with pytest.raises(ValueError, match="repo_id"):
            GroundTruthLabel(repo_id="invalid", metric_id="M-01", label=True, event_type="MDE-01")

    def test_invalid_event_type(self):
        with pytest.raises(ValueError, match="event_type"):
            GroundTruthLabel(repo_id="repo_001", metric_id="M-01", label=True, event_type="MDE-05")

    def test_invalid_severity(self):
        with pytest.raises(ValueError, match="severity"):
            GroundTruthLabel(
                repo_id="repo_001",
                metric_id="M-01",
                label=True,
                event_type="MDE-01",
                severity="critical",
            )

    def test_invalid_confidence(self):
        with pytest.raises(ValueError, match="confidence"):
            GroundTruthLabel(
                repo_id="repo_001",
                metric_id="M-01",
                label=True,
                event_type="MDE-01",
                confidence="certain",
            )

    def test_annotator_agreement_out_of_range(self):
        with pytest.raises(ValueError, match="annotator_agreement"):
            GroundTruthLabel(
                repo_id="repo_001",
                metric_id="M-01",
                label=True,
                event_type="MDE-01",
                annotator_agreement=1.5,
            )

    def test_optional_fields(self):
        label = GroundTruthLabel(
            repo_id="repo_001",
            metric_id="M-01",
            label=True,
            event_type="MDE-01",
            window_id="w01",
            window_pair=["w01", "w02"],
            metric_pair=["M-01", "M-02"],
            threshold=0.5,
        )
        assert label.window_id == "w01"
        assert label.threshold == 0.5


class TestGroundTruthInput:
    def test_empty_construction(self):
        gt = GroundTruthInput()
        assert gt.suite_id == ""
        assert gt.labels == []

    def test_full_construction(self):
        lbl = GroundTruthLabel(repo_id="repo_001", metric_id="M-01", label=True, event_type="MDE-01")
        gt = GroundTruthInput(
            suite_id="suite-001",
            version="1.0.0",
            labels=[lbl],
        )
        assert gt.suite_id == "suite-001"
        assert len(gt.labels) == 1
        assert gt.labels[0].repo_id == "repo_001"

    def test_legacy_data(self):
        gt = GroundTruthInput(data={"key": "value"})
        assert gt.data["key"] == "value"

    def test_invalid_label_type(self):
        with pytest.raises(ValueError, match="labels"):
            GroundTruthInput(labels=["not a label"])


# ---------------------------------------------------------------------------
# Backward-compat: DetectorResult still accepts dict-based detector_outputs
# ---------------------------------------------------------------------------


class TestDetectorResultBackwardCompat:
    def test_old_style_construction(self):
        dr = DetectorResult(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})
        assert len(dr.detector_outputs) == 3

    def test_invalid_detector_rejected(self):
        with pytest.raises(ValueError, match="Invalid detector ID"):
            DetectorResult(detector_outputs={"D-04": {}})

    def test_empty_construction(self):
        dr = DetectorResult()
        assert dr.detector_outputs == {}

    def test_new_typed_fields(self):
        d01 = D01Output(
            ks_statistic=0.1,
            ks_p_value=0.05,
            psi_value=0.1,
            direction="mean_shift",
            severity=0.5,
            flagged=True,
        )
        dr = DetectorResult(d_01={"M-01": {"w01-w02": d01}})
        assert dr.d_01["M-01"]["w01-w02"].flagged is True
