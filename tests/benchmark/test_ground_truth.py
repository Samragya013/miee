"""
Unit tests for MIIE Ground Truth Dataset Framework.

Tests the core data models, lifecycle states, schema validation, and
machine-readable formats for ground truth datasets.

Resolves SDV Critical Finding CF-03 (G-09: No ground truth datasets).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from miie.benchmark.ground_truth import (
    AcceptanceCriteria,
    AnomalySeverity,
    AnomalyType,
    Certification,
    DetectorID,
    DetectorOutput,
    DatasetStatus,
    DatasetType,
    ExpectedScores,
    GroundTruth,
    GroundTruthDataset,
    GroundTruthEntry,
    Licensing,
    MetricID,
    Provenance,
    RepositoryClassification,
    TrendType,
    Versioning,
)


class TestDatasetType:
    """Tests for DatasetType enum."""

    def test_synthetic_value(self):
        assert DatasetType.SYNTHETIC.value == "synthetic"

    def test_real_value(self):
        assert DatasetType.REAL.value == "real"

    def test_adversarial_value(self):
        assert DatasetType.ADVERSARIAL.value == "adversarial"

    def test_all_types_exist(self):
        assert len(DatasetType) == 3


class TestDatasetStatus:
    """Tests for DatasetStatus enum."""

    def test_draft_value(self):
        assert DatasetStatus.DRAFT.value == "draft"

    def test_validated_value(self):
        assert DatasetStatus.VALIDATED.value == "validated"

    def test_certified_value(self):
        assert DatasetStatus.CERTIFIED.value == "certified"

    def test_published_value(self):
        assert DatasetStatus.PUBLISHED.value == "published"

    def test_deprecated_value(self):
        assert DatasetStatus.DEPRECATED.value == "deprecated"

    def test_all_statuses_exist(self):
        assert len(DatasetStatus) == 5


class TestRepositoryClassification:
    """Tests for RepositoryClassification enum."""

    def test_healthy_value(self):
        assert RepositoryClassification.HEALTHY.value == "healthy"

    def test_all_categories_exist(self):
        assert len(RepositoryClassification) == 10

    def test_category_ids_are_unique(self):
        values = [c.value for c in RepositoryClassification]
        assert len(values) == len(set(values))


class TestAnomalyType:
    """Tests for AnomalyType enum."""

    def test_metric_drift_value(self):
        assert AnomalyType.METRIC_DRIFT.value == "metric-drift"

    def test_correlation_breakdown_value(self):
        assert AnomalyType.CORRELATION_BREAKDOWN.value == "correlation-breakdown"

    def test_threshold_compression_value(self):
        assert AnomalyType.THRESHOLD_COMPRESSION.value == "threshold-compression"

    def test_seasonal_value(self):
        assert AnomalyType.SEASONAL.value == "seasonal"

    def test_gaming_value(self):
        assert AnomalyType.GAMING.value == "gaming"

    def test_process_decay_value(self):
        assert AnomalyType.PROCESS_DECAY.value == "process-decay"

    def test_all_anomaly_types_exist(self):
        assert len(AnomalyType) == 6


class TestAnomalySeverity:
    """Tests for AnomalySeverity enum."""

    def test_none_value(self):
        assert AnomalySeverity.NONE.value == "none"

    def test_low_value(self):
        assert AnomalySeverity.LOW.value == "low"

    def test_moderate_value(self):
        assert AnomalySeverity.MODERATE.value == "moderate"

    def test_high_value(self):
        assert AnomalySeverity.HIGH.value == "high"

    def test_critical_value(self):
        assert AnomalySeverity.CRITICAL.value == "critical"

    def test_all_severities_exist(self):
        assert len(AnomalySeverity) == 5


class TestDetectorID:
    """Tests for DetectorID enum."""

    def test_d01_value(self):
        assert DetectorID.D01.value == "D-01"

    def test_d02_value(self):
        assert DetectorID.D02.value == "D-02"

    def test_d03_value(self):
        assert DetectorID.D03.value == "D-03"

    def test_all_detectors_exist(self):
        assert len(DetectorID) == 3


class TestMetricID:
    """Tests for MetricID enum."""

    def test_m01_value(self):
        assert MetricID.M01.value == "M-01"

    def test_m07_value(self):
        assert MetricID.M07.value == "M-07"

    def test_all_metrics_exist(self):
        assert len(MetricID) == 7


class TestTrendType:
    """Tests for TrendType enum."""

    def test_stable_value(self):
        assert TrendType.STABLE.value == "stable"

    def test_increasing_value(self):
        assert TrendType.INCREASING.value == "increasing"

    def test_decreasing_value(self):
        assert TrendType.DECREASING.value == "decreasing"

    def test_shift_value(self):
        assert TrendType.SHIFT.value == "shift"

    def test_periodic_value(self):
        assert TrendType.PERIODIC.value == "periodic"

    def test_all_trends_exist(self):
        assert len(TrendType) == 5


class TestProvenance:
    """Tests for Provenance dataclass."""

    def test_create_minimal(self):
        p = Provenance(
            source="generated",
            methodology="test",
            reproducibility="run test",
        )
        assert p.source == "generated"
        assert p.methodology == "test"
        assert p.tools == []
        assert p.parameters == {}
        assert p.parent_dataset is None

    def test_create_full(self):
        p = Provenance(
            source="generated",
            methodology="BenchmarkDatasetGenerator",
            reproducibility="Run with seed=42",
            tools=["miie-generator"],
            parameters={"drift_magnitude": 0.5},
            parent_dataset=None,
        )
        assert p.source == "generated"
        assert p.tools == ["miie-generator"]
        assert p.parameters == {"drift_magnitude": 0.5}

    def test_immutable(self):
        p = Provenance(
            source="generated",
            methodology="test",
            reproducibility="run test",
        )
        with pytest.raises(AttributeError):
            p.source = "changed"


class TestDetectorOutput:
    """Tests for DetectorOutput dataclass."""

    def test_create_minimal(self):
        d = DetectorOutput(detected=True)
        assert d.detected is True
        assert d.severity == AnomalySeverity.NONE
        assert d.p_value_max is None
        assert d.confidence_min is None

    def test_create_full(self):
        d = DetectorOutput(
            detected=True,
            severity=AnomalySeverity.HIGH,
            p_value_max=0.03,
            confidence_min=0.8,
        )
        assert d.detected is True
        assert d.severity == AnomalySeverity.HIGH
        assert d.p_value_max == 0.03
        assert d.confidence_min == 0.8

    def test_not_detected(self):
        d = DetectorOutput(detected=False)
        assert d.detected is False
        assert d.severity == AnomalySeverity.NONE


class TestExpectedScores:
    """Tests for ExpectedScores dataclass."""

    def test_create_empty(self):
        e = ExpectedScores()
        assert e.integrity_score_range is None
        assert e.confidence_score_range is None

    def test_create_with_ranges(self):
        e = ExpectedScores(
            integrity_score_range=(0.3, 0.7),
            confidence_score_range=(0.5, 0.9),
        )
        assert e.integrity_score_range == (0.3, 0.7)
        assert e.confidence_score_range == (0.5, 0.9)


class TestGroundTruth:
    """Tests for GroundTruth dataclass."""

    def test_create_minimal(self):
        gt = GroundTruth(
            anomaly_present=False,
            expected_detector_outputs={},
            expected_metric_values={},
            expected_scores=ExpectedScores(),
        )
        assert gt.anomaly_present is False
        assert gt.anomaly_type is None
        assert gt.anomaly_severity == AnomalySeverity.NONE

    def test_create_with_anomaly(self):
        gt = GroundTruth(
            anomaly_present=True,
            anomaly_type=AnomalyType.METRIC_DRIFT,
            anomaly_severity=AnomalySeverity.MODERATE,
            anomaly_window_start=5,
            anomaly_window_end=10,
            expected_detector_outputs={
                DetectorID.D01: DetectorOutput(
                    detected=True, severity=AnomalySeverity.HIGH
                ),
                DetectorID.D02: DetectorOutput(detected=False),
                DetectorID.D03: DetectorOutput(detected=False),
            },
            expected_metric_values={
                MetricID.M01: {"range": [0.0, 1.0], "trend": "stable"},
            },
            expected_scores=ExpectedScores(
                integrity_score_range=(0.3, 0.7),
                confidence_score_range=(0.5, 0.9),
            ),
        )
        assert gt.anomaly_present is True
        assert gt.anomaly_type == AnomalyType.METRIC_DRIFT
        assert gt.anomaly_window_start == 5
        assert gt.anomaly_window_end == 10
        assert DetectorID.D01 in gt.expected_detector_outputs
        assert gt.expected_detector_outputs[DetectorID.D01].detected is True


class TestAcceptanceCriteria:
    """Tests for AcceptanceCriteria dataclass."""

    def test_create_default(self):
        ac = AcceptanceCriteria()
        assert ac.d01_sensitivity_min is None
        assert ac.metric_computation_tolerance == 0.01
        assert ac.determinism_required is True

    def test_create_custom(self):
        ac = AcceptanceCriteria(
            d01_sensitivity_min=0.80,
            d01_specificity_min=0.90,
            d02_sensitivity_min=0.75,
            d02_specificity_min=0.85,
            d03_sensitivity_min=0.85,
            d03_specificity_min=0.90,
            metric_computation_tolerance=0.001,
            determinism_required=True,
        )
        assert ac.d01_sensitivity_min == 0.80
        assert ac.d01_specificity_min == 0.90
        assert ac.metric_computation_tolerance == 0.001


class TestVersioning:
    """Tests for Versioning dataclass."""

    def test_create(self):
        v = Versioning(
            changelog=["Initial release"],
            compatibility="backward-compatible",
        )
        assert v.changelog == ["Initial release"]
        assert v.compatibility == "backward-compatible"
        assert v.supersedes is None

    def test_create_with_supersedes(self):
        v = Versioning(
            changelog=["Bug fix"],
            compatibility="backward-compatible",
            supersedes="GT-SYN-DRIFT-001",
        )
        assert v.supersedes == "GT-SYN-DRIFT-001"


class TestCertification:
    """Tests for Certification dataclass."""

    def test_create_minimal(self):
        c = Certification(
            certified_by="scientific-board",
            criteria="all-expected-outputs-verified",
        )
        assert c.certified_by == "scientific-board"
        assert c.certified_at is None
        assert c.certificate_id is None

    def test_create_full(self):
        now = datetime.now(timezone.utc)
        c = Certification(
            certified_by="scientific-board",
            certified_at=now,
            criteria="all-expected-outputs-verified",
            certificate_id="CERT-GT-SYN-001-1.0.0",
        )
        assert c.certified_at == now
        assert c.certificate_id == "CERT-GT-SYN-001-1.0.0"


class TestLicensing:
    """Tests for Licensing dataclass."""

    def test_create_default(self):
        l = Licensing()
        assert l.license == "MIT"
        assert l.attribution is None
        assert l.usage_restrictions is None

    def test_create_custom(self):
        l = Licensing(
            license="Apache-2.0",
            attribution="MIIE Benchmark",
            usage_restrictions="research-only",
        )
        assert l.license == "Apache-2.0"
        assert l.usage_restrictions == "research-only"


class TestGroundTruthDataset:
    """Tests for GroundTruthDataset dataclass."""

    def _make_dataset(
        self,
        status: DatasetStatus = DatasetStatus.DRAFT,
    ) -> GroundTruthDataset:
        return GroundTruthDataset(
            dataset_id="GT-SYN-DRIFT-001",
            dataset_name="Test Dataset",
            dataset_version="1.0.0",
            dataset_type=DatasetType.SYNTHETIC,
            status=status,
            created_by="test",
            created_at=datetime.now(timezone.utc),
            description="Test dataset",
            repository_classification=RepositoryClassification.SYNTHETIC,
            provenance=Provenance(
                source="generated",
                methodology="test",
                reproducibility="run test",
            ),
            ground_truth=GroundTruth(
                anomaly_present=False,
                expected_detector_outputs={},
                expected_metric_values={},
                expected_scores=ExpectedScores(),
            ),
            acceptance_criteria=AcceptanceCriteria(),
            versioning=Versioning(changelog=["Initial"]),
            certification=Certification(
                certified_by="test",
                criteria="test",
            ),
            licensing=Licensing(),
        )

    def test_create_dataset(self):
        ds = self._make_dataset()
        assert ds.dataset_id == "GT-SYN-DRIFT-001"
        assert ds.dataset_type == DatasetType.SYNTHETIC
        assert ds.status == DatasetStatus.DRAFT

    def test_is_certified_true(self):
        ds = self._make_dataset(status=DatasetStatus.CERTIFIED)
        assert ds.is_certified() is True

    def test_is_certified_published(self):
        ds = self._make_dataset(status=DatasetStatus.PUBLISHED)
        assert ds.is_certified() is True

    def test_is_certified_false(self):
        ds = self._make_dataset(status=DatasetStatus.DRAFT)
        assert ds.is_certified() is False

    def test_is_usable_true(self):
        ds = self._make_dataset(status=DatasetStatus.DRAFT)
        assert ds.is_usable() is True

    def test_is_usable_false(self):
        ds = self._make_dataset(status=DatasetStatus.DEPRECATED)
        assert ds.is_usable() is False

    def test_to_dict_structure(self):
        ds = self._make_dataset()
        d = ds.to_dict()
        assert "dataset_id" in d
        assert "dataset_name" in d
        assert "dataset_type" in d
        assert "status" in d
        assert "provenance" in d
        assert "ground_truth" in d
        assert "acceptance_criteria" in d
        assert "versioning" in d
        assert "certification" in d
        assert "licensing" in d

    def test_to_dict_json_serializable(self):
        ds = self._make_dataset()
        d = ds.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)

    def test_to_dict_enum_values(self):
        ds = self._make_dataset()
        d = ds.to_dict()
        assert d["dataset_type"] == "synthetic"
        assert d["status"] == "draft"
        assert d["repository_classification"] == "synthetic"

    def test_to_dict_nested_enum_values(self):
        ds = self._make_dataset()
        d = ds.to_dict()
        gt = d["ground_truth"]
        assert gt["anomaly_severity"] == "none"

    def test_immutable(self):
        ds = self._make_dataset()
        with pytest.raises(AttributeError):
            ds.dataset_id = "changed"


class TestGroundTruthEntry:
    """Tests for GroundTruthEntry dataclass."""

    def test_create_minimal(self):
        e = GroundTruthEntry(
            entry_id="GT-E-0001",
            dataset_id="GT-SYN-DRIFT-001",
            window_index=0,
            expected_values={"M-01": 0.5},
        )
        assert e.entry_id == "GT-E-0001"
        assert e.confidence == 1.0
        assert e.source == "automated"

    def test_create_full(self):
        e = GroundTruthEntry(
            entry_id="GT-E-0001",
            dataset_id="GT-SYN-DRIFT-001",
            window_index=0,
            expected_values={"M-01": 0.5},
            annotations={"anomaly_present": True},
            confidence=0.95,
            source="expert",
        )
        assert e.confidence == 0.95
        assert e.source == "expert"
        assert e.annotations == {"anomaly_present": True}

    def test_to_dict(self):
        e = GroundTruthEntry(
            entry_id="GT-E-0001",
            dataset_id="GT-SYN-DRIFT-001",
            window_index=0,
            expected_values={"M-01": 0.5},
        )
        d = e.to_dict()
        assert d["entry_id"] == "GT-E-0001"
        assert d["window_index"] == 0
        assert d["expected_values"] == {"M-01": 0.5}

    def test_to_dict_json_serializable(self):
        e = GroundTruthEntry(
            entry_id="GT-E-0001",
            dataset_id="GT-SYN-DRIFT-001",
            window_index=0,
            expected_values={"M-01": 0.5},
        )
        serialized = json.dumps(e.to_dict())
        assert isinstance(serialized, str)


class TestGroundTruthDatasetFull:
    """Integration tests for GroundTruthDataset with full data."""

    def test_full_dataset_roundtrip(self):
        now = datetime.now(timezone.utc)
        ds = GroundTruthDataset(
            dataset_id="GT-SYN-DRIFT-003",
            dataset_name="Medium Drift Test",
            dataset_version="1.0.0",
            dataset_type=DatasetType.SYNTHETIC,
            status=DatasetStatus.CERTIFIED,
            created_by="miie-benchmark",
            created_at=now,
            description="Synthetic repository with moderate metric drift",
            repository_classification=RepositoryClassification.SYNTHETIC,
            provenance=Provenance(
                source="generated",
                methodology="BenchmarkDatasetGenerator",
                reproducibility="Run with seed=42, drift_magnitude=0.5",
                tools=["miie-benchmark-generator"],
                parameters={"drift_magnitude": 0.5, "drift_onset": 100},
            ),
            ground_truth=GroundTruth(
                anomaly_present=True,
                anomaly_type=AnomalyType.METRIC_DRIFT,
                anomaly_severity=AnomalySeverity.MODERATE,
                anomaly_window_start=5,
                anomaly_window_end=10,
                expected_detector_outputs={
                    DetectorID.D01: DetectorOutput(
                        detected=True,
                        severity=AnomalySeverity.HIGH,
                        p_value_max=0.05,
                    ),
                    DetectorID.D02: DetectorOutput(detected=False),
                    DetectorID.D03: DetectorOutput(detected=False),
                },
                expected_metric_values={
                    MetricID.M01: {"range": [0.0, 1.0], "trend": "stable"},
                    MetricID.M02: {"range": [0, 500], "trend": "stable"},
                    MetricID.M03: {"range": [0.0, 1.0], "trend": "shift_at_window_5"},
                },
                expected_scores=ExpectedScores(
                    integrity_score_range=(0.3, 0.7),
                    confidence_score_range=(0.5, 0.9),
                ),
            ),
            acceptance_criteria=AcceptanceCriteria(
                d01_sensitivity_min=0.80,
                d01_specificity_min=0.90,
                metric_computation_tolerance=0.01,
                determinism_required=True,
            ),
            versioning=Versioning(
                changelog=["Initial release"],
                compatibility="backward-compatible",
            ),
            certification=Certification(
                certified_by="scientific-board",
                certified_at=now,
                criteria="all-expected-outputs-verified",
                certificate_id="CERT-GT-SYN-DRIFT-003-1.0.0",
            ),
            licensing=Licensing(
                license="MIT",
                attribution="MIIE Benchmark Dataset",
            ),
            language="python",
            commit_count=200,
            contributor_count=5,
            time_span_days=365,
            tags=["drift", "moderate", "synthetic"],
        )

        assert ds.is_certified() is True
        assert ds.is_usable() is True

        d = ds.to_dict()
        assert d["dataset_id"] == "GT-SYN-DRIFT-003"
        assert d["status"] == "certified"
        assert d["ground_truth"]["anomaly_present"] is True
        assert d["ground_truth"]["anomaly_type"] == "metric-drift"
        assert d["commit_count"] == 200
        assert d["tags"] == ["drift", "moderate", "synthetic"]

        serialized = json.dumps(d)
        assert isinstance(serialized, str)
        assert len(serialized) > 100

    def test_dataset_with_all_anomaly_types(self):
        """Test creating datasets for each anomaly type."""
        for anomaly_type in AnomalyType:
            gt = GroundTruth(
                anomaly_present=True,
                anomaly_type=anomaly_type,
                anomaly_severity=AnomalySeverity.MODERATE,
                expected_detector_outputs={},
                expected_metric_values={},
                expected_scores=ExpectedScores(),
            )
            assert gt.anomaly_type == anomaly_type

    def test_dataset_with_all_severity_levels(self):
        """Test creating datasets for each severity level."""
        for severity in AnomalySeverity:
            gt = GroundTruth(
                anomaly_present=severity != AnomalySeverity.NONE,
                anomaly_severity=severity,
                expected_detector_outputs={},
                expected_metric_values={},
                expected_scores=ExpectedScores(),
            )
            assert gt.anomaly_severity == severity
