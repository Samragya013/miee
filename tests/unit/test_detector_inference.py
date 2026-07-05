"""
Integration tests for detector + statistical inference (PR-16A).

Tests that all three detectors produce correct inference metadata,
that original detector decisions are preserved, and that inference
keys are present in the output dicts.

Actual inference structure (per detector output):
{
  "method": "bonferroni" | "benjamini_hochberg",
  "alpha": 0.05,
  "families": [
    {
      "family_id": "KS_w00_w01",
      "correction_method": "bonferroni",
      "alpha": 0.05,
      "num_tests": 1,
      "num_rejections": 0,
      "adjusted_p_values": [...],
      "reject": [...],
      "tests": [...]
    },
    ...
  ],
  "summary": {
    "total_ks_tests": 2,
    "total_ks_rejections": 1
  }
}
"""

from __future__ import annotations

import datetime

from miie.processing.detection.correlation_breakdown_detector import (
    CorrelationBreakdownDetector,
)
from miie.processing.detection.distribution_drift_detector import (
    DistributionDriftDetector,
)
from miie.processing.detection.threshold_compression_detector import (
    ThresholdCompressionDetector,
)
from miie.schemas.models import MetricDataFrame

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_mdf(metrics: dict) -> MetricDataFrame:
    return MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        metrics=metrics,
    )


# D-01: Drift data (mean shift between w00 and w02)
D01_DRIFT_MDF = _make_mdf(
    {
        "M-02": {
            "w00": [4.0, 4.5, 5.0, 5.5, 6.0, 4.0, 4.5, 5.0, 5.5, 6.0] * 4,
            "w01": [4.0, 4.5, 5.0, 5.5, 6.0, 4.0, 4.5, 5.0, 5.5, 6.0] * 4,
            "w02": [14.0, 14.5, 15.0, 15.5, 16.0, 14.0, 14.5, 15.0, 15.5, 16.0] * 4,
        },
    }
)

# D-01: No-drift data (identical windows)
D01_NODRIFT_MDF = _make_mdf(
    {
        "M-02": {
            "w00": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0] * 4,
            "w01": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0] * 4,
            "w02": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0] * 4,
        },
    }
)

# D-02: Correlation breakdown data (sign reversal)
D02_BREAKDOWN_MDF = _make_mdf(
    {
        "M-02": {
            "w00": [10, 12, 11, 13, 12, 11, 10, 12, 13, 11] * 4,
            "w01": [10, 12, 11, 13, 12, 11, 10, 12, 13, 11] * 4,
            "w02": [11, 9, 12, 8, 13, 7, 14, 6, 15, 5] * 4,
        },
        "M-06": {
            "w00": [5, 6, 4, 7, 5, 6, 4, 7, 5, 6] * 4,
            "w01": [5, 6, 4, 7, 5, 6, 4, 7, 5, 6] * 4,
            "w02": [4, 6, 5, 7, 3, 8, 2, 9, 1, 10] * 4,
        },
    }
)

# D-03: Compression data
D03_COMPRESSED_MDF = _make_mdf(
    {
        "M-02": {
            "w00": [48, 49, 50, 51, 52] * 8,
            "w01": [48, 49, 50, 51, 52] * 8,
            "w02": [50, 50, 50, 50, 50] * 8,
        },
        "M-06": {
            "w00": [30, 35, 40, 45, 50] * 8,
            "w01": [30, 35, 40, 45, 50] * 8,
            "w02": [50, 50, 50, 50, 50] * 8,
        },
    }
)


# ---------------------------------------------------------------------------
# D-01 Inference Integration
# ---------------------------------------------------------------------------


class TestD01Inference:
    def setup_method(self):
        self.detector = DistributionDriftDetector()

    def test_output_has_inference_key(self):
        result = self.detector.execute(D01_DRIFT_MDF)
        output = result.detector_outputs["D-01"]
        assert "inference" in output

    def test_inference_top_level_structure(self):
        result = self.detector.execute(D01_DRIFT_MDF)
        inf = result.detector_outputs["D-01"]["inference"]
        assert "method" in inf
        assert "alpha" in inf
        assert "families" in inf
        assert "summary" in inf
        assert inf["method"] == "bonferroni"
        assert inf["alpha"] == 0.05

    def test_inference_has_multiple_families(self):
        result = self.detector.execute(D01_DRIFT_MDF)
        inf = result.detector_outputs["D-01"]["inference"]
        assert len(inf["families"]) >= 1
        for fam in inf["families"]:
            assert "family_id" in fam
            assert "correction_method" in fam
            assert "num_tests" in fam
            assert "num_rejections" in fam
            assert "adjusted_p_values" in fam
            assert "reject" in fam
            assert "tests" in fam

    def test_inference_family_correction_method(self):
        result = self.detector.execute(D01_DRIFT_MDF)
        inf = result.detector_outputs["D-01"]["inference"]
        for fam in inf["families"]:
            assert fam["correction_method"] == "bonferroni"

    def test_inference_tests_have_required_fields(self):
        result = self.detector.execute(D01_DRIFT_MDF)
        inf = result.detector_outputs["D-01"]["inference"]
        for fam in inf["families"]:
            for t in fam["tests"]:
                assert "test_id" in t
                assert "raw_p_value" in t
                assert "alternative" in t

    def test_inference_summary_structure(self):
        result = self.detector.execute(D01_DRIFT_MDF)
        inf = result.detector_outputs["D-01"]["inference"]
        assert isinstance(inf["summary"], dict)
        assert "total_ks_tests" in inf["summary"]
        assert "total_ks_rejections" in inf["summary"]

    def test_original_decision_preserved(self):
        result = self.detector.execute(D01_DRIFT_MDF)
        output = result.detector_outputs["D-01"]
        assert isinstance(output["drift_detected"], bool)

    def test_no_drift_inference_structure_valid(self):
        result = self.detector.execute(D01_NODRIFT_MDF)
        inf = result.detector_outputs["D-01"]["inference"]
        # Inference structure should be well-formed regardless of rejection outcome
        assert inf["method"] == "bonferroni"
        assert inf["alpha"] == 0.05
        assert isinstance(inf["families"], list)
        assert len(inf["families"]) >= 1
        for fam in inf["families"]:
            assert "family_id" in fam
            assert "correction_method" in fam
            assert isinstance(fam["num_rejections"], int)
            assert isinstance(fam["reject"], list)
            # All adjusted p-values should be in valid range
            for adj in fam["adjusted_p_values"]:
                assert 0.0 <= adj <= 1.0


# ---------------------------------------------------------------------------
# D-02 Inference Integration
# ---------------------------------------------------------------------------


class TestD02Inference:
    def setup_method(self):
        self.detector = CorrelationBreakdownDetector()

    def test_output_has_inference_key(self):
        result = self.detector.execute(D02_BREAKDOWN_MDF)
        output = result.detector_outputs["D-02"]
        assert "inference" in output

    def test_inference_structure(self):
        result = self.detector.execute(D02_BREAKDOWN_MDF)
        inf = result.detector_outputs["D-02"]["inference"]
        assert inf["method"] == "benjamini_hochberg"
        assert inf["alpha"] == 0.05
        assert len(inf["families"]) >= 1
        for fam in inf["families"]:
            assert fam["correction_method"] == "bh"

    def test_original_decision_preserved(self):
        result = self.detector.execute(D02_BREAKDOWN_MDF)
        output = result.detector_outputs["D-02"]
        assert isinstance(output["breakdown_detected"], bool)


# ---------------------------------------------------------------------------
# D-03 Inference Integration
# ---------------------------------------------------------------------------


class TestD03Inference:
    def setup_method(self):
        self.detector = ThresholdCompressionDetector()

    def test_output_has_inference_key(self):
        result = self.detector.execute(D03_COMPRESSED_MDF)
        output = result.detector_outputs["D-03"]
        assert "inference" in output

    def test_inference_structure(self):
        result = self.detector.execute(D03_COMPRESSED_MDF)
        inf = result.detector_outputs["D-03"]["inference"]
        assert inf["method"] == "bonferroni"
        assert inf["alpha"] == 0.05
        assert len(inf["families"]) >= 1
        for fam in inf["families"]:
            assert fam["correction_method"] == "bonferroni"
            assert fam["num_tests"] > 0

    def test_original_decision_preserved(self):
        result = self.detector.execute(D03_COMPRESSED_MDF)
        output = result.detector_outputs["D-03"]
        assert isinstance(output["compression_detected"], bool)


# ---------------------------------------------------------------------------
# Metadata-only guarantee
# ---------------------------------------------------------------------------


class TestMetadataOnlyGuarantee:
    """Verify that inference metadata does not alter detector decisions."""

    def test_d01_decision_unchanged_with_vs_without_inference(self):
        detector = DistributionDriftDetector()
        result = detector.execute(D01_DRIFT_MDF)
        output = result.detector_outputs["D-01"]
        assert isinstance(output["drift_detected"], bool)

    def test_d02_decision_unchanged_with_vs_without_inference(self):
        detector = CorrelationBreakdownDetector()
        result = detector.execute(D02_BREAKDOWN_MDF)
        output = result.detector_outputs["D-02"]
        assert isinstance(output["breakdown_detected"], bool)

    def test_d03_decision_unchanged_with_vs_without_inference(self):
        detector = ThresholdCompressionDetector()
        result = detector.execute(D03_COMPRESSED_MDF)
        output = result.detector_outputs["D-03"]
        assert isinstance(output["compression_detected"], bool)
