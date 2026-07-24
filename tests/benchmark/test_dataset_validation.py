"""
Unit tests for MIIE Ground Truth Dataset Validation Service.

Tests validation, registry, and schema compliance for ground truth datasets.

Resolves SDV Critical Finding CF-03 (G-09: No ground truth datasets).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from miie.benchmark.dataset_validation import (
    DatasetRegistry,
    DatasetValidationError,
    DatasetValidationResult,
    DatasetValidator,
)
from miie.benchmark.ground_truth import (
    AcceptanceCriteria,
    Certification,
    DatasetStatus,
    DatasetType,
    ExpectedScores,
    GroundTruth,
    GroundTruthDataset,
    Licensing,
    Provenance,
    RepositoryClassification,
    Versioning,
)


def _make_valid_dataset(
    dataset_id: str = "GT-SYN-DRIFT-001",
    status: DatasetStatus = DatasetStatus.CERTIFIED,
) -> GroundTruthDataset:
    return GroundTruthDataset(
        dataset_id=dataset_id,
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
            certified_by="scientific-board",
            criteria="all-expected-outputs-verified",
        ),
        licensing=Licensing(),
    )


class TestDatasetValidationError:
    def test_create(self):
        e = DatasetValidationError("field", "message", "error")
        assert e.field == "field"
        assert e.message == "message"
        assert e.severity == "error"

    def test_to_dict(self):
        e = DatasetValidationError("field", "message", "warning")
        d = e.to_dict()
        assert d["field"] == "field"
        assert d["severity"] == "warning"

    def test_str(self):
        e = DatasetValidationError("field", "message", "error")
        assert "[ERROR]" in str(e)


class TestDatasetValidationResult:
    def test_create(self):
        r = DatasetValidationResult("GT-SYN-001")
        assert r.dataset_id == "GT-SYN-001"
        assert r.is_valid is True

    def test_add_error(self):
        r = DatasetValidationResult("GT-SYN-001")
        r.add_error("field", "msg")
        assert r.is_valid is False
        assert len(r.errors) == 1

    def test_add_warning(self):
        r = DatasetValidationResult("GT-SYN-001")
        r.add_warning("field", "msg")
        assert r.is_valid is True
        assert len(r.warnings) == 1

    def test_to_dict(self):
        r = DatasetValidationResult("GT-SYN-001")
        r.add_error("f", "m")
        r.add_warning("f2", "m2")
        d = r.to_dict()
        assert d["error_count"] == 1
        assert d["warning_count"] == 1


class TestDatasetValidator:
    def setup_method(self):
        self.validator = DatasetValidator()

    def test_valid_dataset(self):
        ds = _make_valid_dataset()
        result = self.validator.validate_dataset(ds)
        assert result.is_valid

    def test_empty_dataset_id(self):
        ds = _make_valid_dataset()
        ds = GroundTruthDataset(
            dataset_id="",
            dataset_name="Test",
            dataset_version="1.0.0",
            dataset_type=DatasetType.SYNTHETIC,
            status=DatasetStatus.DRAFT,
            created_by="test",
            created_at=datetime.now(timezone.utc),
            description="Test",
            repository_classification=RepositoryClassification.SYNTHETIC,
            provenance=Provenance(source="t", methodology="t", reproducibility="t"),
            ground_truth=GroundTruth(
                anomaly_present=False,
                expected_detector_outputs={},
                expected_metric_values={},
                expected_scores=ExpectedScores(),
            ),
            acceptance_criteria=AcceptanceCriteria(),
            versioning=Versioning(changelog=[]),
            certification=Certification(certified_by="t", criteria="t"),
            licensing=Licensing(),
        )
        result = self.validator.validate_dataset(ds)
        assert not result.is_valid
        assert any("dataset_id" in e.field for e in result.errors)

    def test_invalid_dataset_id_format(self):
        ds = _make_valid_dataset(dataset_id="INVALID-ID")
        result = self.validator.validate_dataset(ds)
        assert not result.is_valid

    def test_valid_dataset_id_formats(self):
        for ds_id in ["GT-SYN-DRIFT-001", "GT-REAL-HEALTHY-001", "GT-ADV-DRIFT-001"]:
            ds = _make_valid_dataset(dataset_id=ds_id)
            result = self.validator.validate_dataset(ds)
            assert result.is_valid, f"Failed for {ds_id}"

    def test_invalid_version(self):
        ds = _make_valid_dataset()
        ds = GroundTruthDataset(
            dataset_id="GT-SYN-DRIFT-001",
            dataset_name="Test",
            dataset_version="invalid",
            dataset_type=DatasetType.SYNTHETIC,
            status=DatasetStatus.DRAFT,
            created_by="test",
            created_at=datetime.now(timezone.utc),
            description="Test",
            repository_classification=RepositoryClassification.SYNTHETIC,
            provenance=Provenance(source="t", methodology="t", reproducibility="t"),
            ground_truth=GroundTruth(
                anomaly_present=False,
                expected_detector_outputs={},
                expected_metric_values={},
                expected_scores=ExpectedScores(),
            ),
            acceptance_criteria=AcceptanceCriteria(),
            versioning=Versioning(changelog=[]),
            certification=Certification(certified_by="t", criteria="t"),
            licensing=Licensing(),
        )
        result = self.validator.validate_dataset(ds)
        assert not result.is_valid

    def test_anomaly_present_requires_type(self):
        ds = _make_valid_dataset()
        ds = GroundTruthDataset(
            dataset_id="GT-SYN-DRIFT-001",
            dataset_name="Test",
            dataset_version="1.0.0",
            dataset_type=DatasetType.SYNTHETIC,
            status=DatasetStatus.DRAFT,
            created_by="test",
            created_at=datetime.now(timezone.utc),
            description="Test",
            repository_classification=RepositoryClassification.SYNTHETIC,
            provenance=Provenance(source="t", methodology="t", reproducibility="t"),
            ground_truth=GroundTruth(
                anomaly_present=True,
                anomaly_type=None,
                expected_detector_outputs={},
                expected_metric_values={},
                expected_scores=ExpectedScores(),
            ),
            acceptance_criteria=AcceptanceCriteria(),
            versioning=Versioning(changelog=[]),
            certification=Certification(certified_by="t", criteria="t"),
            licensing=Licensing(),
        )
        result = self.validator.validate_dataset(ds)
        assert not result.is_valid
        assert any("anomaly_type" in e.field for e in result.errors)

    def test_validate_dict_valid(self):
        data = {
            "dataset_id": "GT-SYN-DRIFT-001",
            "dataset_name": "Test",
            "dataset_version": "1.0.0",
            "dataset_type": "synthetic",
            "status": "certified",
            "created_by": "test",
            "created_at": "2026-07-05T00:00:00Z",
            "description": "Test",
            "repository_classification": "synthetic",
            "provenance": {"source": "g", "methodology": "m", "reproducibility": "r"},
            "ground_truth": {
                "anomaly_present": False,
                "expected_detector_outputs": {},
                "expected_metric_values": {},
                "expected_scores": {},
            },
            "acceptance_criteria": {},
            "versioning": {"changelog": []},
            "certification": {"certified_by": "board", "criteria": "c"},
            "licensing": {"license": "MIT"},
        }
        result = self.validator.validate_dict(data)
        assert result.is_valid

    def test_validate_dict_missing_fields(self):
        result = self.validator.validate_dict({})
        assert not result.is_valid
        assert len(result.errors) > 5


class TestDatasetRegistry:
    def setup_method(self):
        self.registry = DatasetRegistry(base_path=Path("benchmarks/ground_truth"))

    def test_load_index(self):
        index = self.registry.load_index()
        assert "datasets" in index
        assert index["total_datasets"] > 0

    def test_list_datasets_all(self):
        datasets = self.registry.list_datasets()
        assert len(datasets) > 0

    def test_list_datasets_by_type(self):
        synthetic = self.registry.list_datasets(dataset_type="synthetic")
        assert len(synthetic) > 0
        assert all(d["type"] == "synthetic" for d in synthetic)

    def test_list_datasets_by_detector(self):
        d01 = self.registry.list_datasets(detector="D-01")
        assert len(d01) > 0

    def test_get_dataset(self):
        ds = self.registry.get_dataset("GT-SYN-DRIFT-001")
        assert ds is not None
        assert ds.dataset_id == "GT-SYN-DRIFT-001"

    def test_get_nonexistent_dataset(self):
        ds = self.registry.get_dataset("GT-NONEXISTENT-000")
        assert ds is None

    def test_validate_all(self):
        results = self.registry.validate_all()
        assert len(results) > 0
        valid_count = sum(1 for r in results if r.is_valid)
        assert valid_count > 0


class TestSchemaCompliance:
    """Test that all dataset JSON files comply with the schema."""

    def _load_all_datasets(self):
        base = Path("benchmarks/ground_truth/datasets")
        datasets = []
        for subdir in ["synthetic", "real", "adversarial"]:
            dir_path = base / subdir
            if dir_path.exists():
                for d in dir_path.iterdir():
                    if d.is_dir():
                        json_path = d / "dataset.json"
                        if json_path.exists():
                            with open(json_path, "r") as f:
                                datasets.append((d.name, json.load(f)))
        return datasets

    def test_all_datasets_have_required_fields(self):
        required = [
            "dataset_id",
            "dataset_name",
            "dataset_version",
            "dataset_type",
            "status",
            "created_by",
            "created_at",
            "description",
            "repository_classification",
            "provenance",
            "ground_truth",
            "acceptance_criteria",
            "versioning",
            "certification",
            "licensing",
        ]
        datasets = self._load_all_datasets()
        assert len(datasets) > 0
        for name, data in datasets:
            for field in required:
                assert field in data, f"{name}: missing '{field}'"

    def test_all_datasets_have_valid_id(self):
        import re

        pattern = r"^GT-(SYN|REAL|ADV)-[A-Z_]+-\d{3}$"
        datasets = self._load_all_datasets()
        for name, data in datasets:
            assert re.match(pattern, data["dataset_id"]), f"{name}: invalid dataset_id"

    def test_all_datasets_have_valid_version(self):
        import re

        datasets = self._load_all_datasets()
        for name, data in datasets:
            assert re.match(r"^\d+\.\d+\.\d+$", data["dataset_version"]), f"{name}: invalid version"

    def test_all_datasets_are_certified(self):
        datasets = self._load_all_datasets()
        for name, data in datasets:
            assert data["status"] == "certified", f"{name}: not certified"

    def test_all_datasets_have_provenance(self):
        datasets = self._load_all_datasets()
        for name, data in datasets:
            p = data["provenance"]
            assert p.get("source"), f"{name}: missing provenance.source"
            assert p.get("methodology"), f"{name}: missing provenance.methodology"
            assert p.get("reproducibility"), f"{name}: missing provenance.reproducibility"

    def test_detector_cross_independence(self):
        """Verify that D-01 drift datasets don't trigger D-02/D-03."""
        datasets = self._load_all_datasets()
        for name, data in datasets:
            gt = data.get("ground_truth", {})
            detectors = gt.get("expected_detector_outputs", {})
            if "D-01" in detectors and detectors["D-01"].get("detected"):
                assert detectors.get("D-02", {}).get("detected") is not True, f"{name}: D-01 drift triggers D-02"
                assert detectors.get("D-03", {}).get("detected") is not True, f"{name}: D-01 drift triggers D-03"

    def test_index_json_matches_datasets(self):
        index_path = Path("benchmarks/ground_truth/index.json")
        with open(index_path, "r") as f:
            index = json.load(f)

        datasets = self._load_all_datasets()
        dataset_ids = {name for name, _ in datasets}
        index_ids = {d["id"] for d in index["datasets"]}

        assert dataset_ids == index_ids, f"Mismatch: {dataset_ids.symmetric_difference(index_ids)}"
