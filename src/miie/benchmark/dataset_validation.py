"""
MIIE v1.6 — Ground Truth Dataset Validation Service

Provides programmatic validation of ground truth datasets against
the schema and acceptance criteria defined in Doc 12.

Resolves SDV Critical Finding CF-03 (G-09: No ground truth datasets).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from miie.benchmark.ground_truth import (
    AcceptanceCriteria,
    AnomalySeverity,
    AnomalyType,
    Certification,
    DatasetStatus,
    DatasetType,
    DetectorID,
    DetectorOutput,
    ExpectedScores,
    GroundTruth,
    GroundTruthDataset,
    GroundTruthEntry,
    Licensing,
    MetricID,
    Provenance,
    RepositoryClassification,
    Versioning,
)


class DatasetValidationError:
    """A single validation error."""

    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity,
        }

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


class DatasetValidationResult:
    """Result of dataset validation."""

    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.errors: List[DatasetValidationError] = []
        self.warnings: List[DatasetValidationError] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field: str, message: str):
        self.errors.append(DatasetValidationError(field, message, "error"))

    def add_warning(self, field: str, message: str):
        self.warnings.append(DatasetValidationError(field, message, "warning"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
        }


class DatasetValidator:
    """Validates ground truth datasets against schema and criteria."""

    def validate_dataset(self, dataset: GroundTruthDataset) -> DatasetValidationResult:
        """Validate a GroundTruthDataset instance."""
        result = DatasetValidationResult(dataset.dataset_id)

        self._validate_required_fields(dataset, result)
        self._validate_dataset_id(dataset, result)
        self._validate_version(dataset, result)
        self._validate_ground_truth(dataset, result)
        self._validate_acceptance_criteria(dataset, result)
        self._validate_provenance(dataset, result)
        self._validate_certification(dataset, result)

        return result

    def validate_dict(self, data: Dict[str, Any]) -> DatasetValidationResult:
        """Validate a dictionary representation of a dataset."""
        dataset_id = data.get("dataset_id", "unknown")
        result = DatasetValidationResult(dataset_id)

        required = [
            "dataset_id", "dataset_name", "dataset_version",
            "dataset_type", "status", "created_by", "created_at",
            "description", "repository_classification", "provenance",
            "ground_truth", "acceptance_criteria", "versioning",
            "certification", "licensing",
        ]

        for field in required:
            if field not in data:
                result.add_error(field, f"Required field '{field}' is missing")

        if "dataset_id" in data:
            self._validate_dataset_id_dict(data, result)
        if "dataset_version" in data:
            self._validate_version_dict(data, result)
        if "ground_truth" in data:
            self._validate_ground_truth_dict(data["ground_truth"], result)

        return result

    def _validate_required_fields(
        self, dataset: GroundTruthDataset, result: DatasetValidationResult
    ):
        if not dataset.dataset_id:
            result.add_error("dataset_id", "dataset_id cannot be empty")
        if not dataset.dataset_name:
            result.add_error("dataset_name", "dataset_name cannot be empty")
        if not dataset.description:
            result.add_error("description", "description cannot be empty")

    def _validate_dataset_id(
        self, dataset: GroundTruthDataset, result: DatasetValidationResult
    ):
        import re
        pattern = r"^GT-(SYN|REAL|ADV)-[A-Z_]+-\d{3}$"
        if not re.match(pattern, dataset.dataset_id):
            result.add_error(
                "dataset_id",
                f"dataset_id '{dataset.dataset_id}' does not match pattern GT-{{SYN|REAL|ADV}}-CATEGORY-NNN",
            )

    def _validate_version(
        self, dataset: GroundTruthDataset, result: DatasetValidationResult
    ):
        import re
        if not re.match(r"^\d+\.\d+\.\d+$", dataset.dataset_version):
            result.add_error(
                "dataset_version",
                f"dataset_version '{dataset.dataset_version}' is not valid semantic version",
            )

    def _validate_ground_truth(
        self, dataset: GroundTruthDataset, result: DatasetValidationResult
    ):
        gt = dataset.ground_truth
        if not gt.expected_detector_outputs:
            result.add_warning(
                "ground_truth.expected_detector_outputs",
                "No expected detector outputs defined",
            )
        if not gt.expected_metric_values:
            result.add_warning(
                "ground_truth.expected_metric_values",
                "No expected metric values defined",
            )
        if gt.anomaly_present and gt.anomaly_type is None:
            result.add_error(
                "ground_truth.anomaly_type",
                "anomaly_type must be specified when anomaly_present is true",
            )

    def _validate_acceptance_criteria(
        self, dataset: GroundTruthDataset, result: DatasetValidationResult
    ):
        ac = dataset.acceptance_criteria
        if ac.d01_sensitivity_min is not None and not (0 <= ac.d01_sensitivity_min <= 1):
            result.add_error(
                "acceptance_criteria.d01_sensitivity_min",
                "Sensitivity must be between 0 and 1",
            )
        if ac.d01_specificity_min is not None and not (0 <= ac.d01_specificity_min <= 1):
            result.add_error(
                "acceptance_criteria.d01_specificity_min",
                "Specificity must be between 0 and 1",
            )

    def _validate_provenance(
        self, dataset: GroundTruthDataset, result: DatasetValidationResult
    ):
        p = dataset.provenance
        if not p.source:
            result.add_error("provenance.source", "source cannot be empty")
        if not p.methodology:
            result.add_error("provenance.methodology", "methodology cannot be empty")
        if not p.reproducibility:
            result.add_error("provenance.reproducibility", "reproducibility cannot be empty")

    def _validate_certification(
        self, dataset: GroundTruthDataset, result: DatasetValidationResult
    ):
        c = dataset.certification
        if not c.certified_by:
            result.add_error("certification.certified_by", "certified_by cannot be empty")
        if not c.criteria:
            result.add_error("certification.criteria", "criteria cannot be empty")

    def _validate_dataset_id_dict(self, data: Dict, result: DatasetValidationResult):
        import re
        pattern = r"^GT-(SYN|REAL|ADV)-[A-Z_]+-\d{3}$"
        if not re.match(pattern, data.get("dataset_id", "")):
            result.add_error("dataset_id", "Does not match expected pattern")

    def _validate_version_dict(self, data: Dict, result: DatasetValidationResult):
        import re
        if not re.match(r"^\d+\.\d+\.\d+$", data.get("dataset_version", "")):
            result.add_error("dataset_version", "Not valid semantic version")

    def _validate_ground_truth_dict(self, gt: Dict, result: DatasetValidationResult):
        if "anomaly_present" not in gt:
            result.add_error("ground_truth.anomaly_present", "Required field missing")
        if "expected_detector_outputs" not in gt:
            result.add_error("ground_truth.expected_detector_outputs", "Required field missing")
        if "expected_metric_values" not in gt:
            result.add_error("ground_truth.expected_metric_values", "Required field missing")
        if "expected_scores" not in gt:
            result.add_error("ground_truth.expected_scores", "Required field missing")


class DatasetRegistry:
    """Registry for managing ground truth datasets."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path("benchmarks/ground_truth")
        self._datasets: Dict[str, GroundTruthDataset] = {}
        self._validator = DatasetValidator()

    def load_index(self) -> Dict[str, Any]:
        """Load the dataset index."""
        index_path = self.base_path / "index.json"
        if index_path.exists():
            with open(index_path, "r") as f:
                return json.load(f)
        return {"datasets": [], "total_datasets": 0}

    def get_dataset(self, dataset_id: str) -> Optional[GroundTruthDataset]:
        """Get a dataset by ID."""
        if dataset_id in self._datasets:
            return self._datasets[dataset_id]

        dataset_path = self.base_path / "datasets" / self._find_dataset_dir(dataset_id)
        if dataset_path.exists():
            return self._load_dataset(dataset_path)
        return None

    def list_datasets(
        self,
        dataset_type: Optional[str] = None,
        detector: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List datasets with optional filtering."""
        index = self.load_index()
        datasets = index.get("datasets", [])

        if dataset_type:
            datasets = [d for d in datasets if d.get("type") == dataset_type]
        if detector:
            datasets = [d for d in datasets if d.get("detector") in (detector, "all")]
        if status:
            datasets = [d for d in datasets if d.get("status") == status]

        return datasets

    def validate_all(self) -> List[DatasetValidationResult]:
        """Validate all datasets in the registry."""
        results = []
        index = self.load_index()
        for ds_info in index.get("datasets", []):
            dataset = self.get_dataset(ds_info["id"])
            if dataset:
                results.append(self._validator.validate_dataset(dataset))
        return results

    def _find_dataset_dir(self, dataset_id: str) -> str:
        """Find the directory for a dataset ID."""
        for subdir in ["synthetic", "real", "adversarial"]:
            candidate = self.base_path / "datasets" / subdir / dataset_id
            if candidate.exists():
                return f"{subdir}/{dataset_id}"
        return f"synthetic/{dataset_id}"

    def _load_dataset(self, path: Path) -> Optional[GroundTruthDataset]:
        """Load a dataset from a directory."""
        dataset_file = path / "dataset.json"
        if not dataset_file.exists():
            return None

        with open(dataset_file, "r") as f:
            data = json.load(f)

        try:
            return self._dict_to_dataset(data)
        except Exception:
            return None

    def _dict_to_dataset(self, data: Dict[str, Any]) -> GroundTruthDataset:
        """Convert a dictionary to a GroundTruthDataset."""
        gt_data = data.get("ground_truth", {})

        expected_detectors = {}
        for det_id_str, det_out in gt_data.get("expected_detector_outputs", {}).items():
            try:
                det_id = DetectorID(det_id_str)
                expected_detectors[det_id] = DetectorOutput(
                    detected=det_out.get("detected", False),
                    severity=AnomalySeverity(det_out.get("severity", "none")),
                    p_value_max=det_out.get("p_value_max"),
                    confidence_min=det_out.get("confidence_min"),
                )
            except (ValueError, KeyError):
                continue

        expected_metrics = {}
        for met_id_str, met_vals in gt_data.get("expected_metric_values", {}).items():
            try:
                met_id = MetricID(met_id_str)
                expected_metrics[met_id] = met_vals
            except ValueError:
                continue

        scores_data = gt_data.get("expected_scores", {})
        integrity_range = scores_data.get("integrity_score_range")
        confidence_range = scores_data.get("confidence_score_range")

        anomaly_type = None
        if gt_data.get("anomaly_type"):
            try:
                anomaly_type = AnomalyType(gt_data["anomaly_type"])
            except ValueError:
                pass

        prov_data = data.get("provenance", {})
        cert_data = data.get("certification", {})
        ver_data = data.get("versioning", {})
        lic_data = data.get("licensing", {})
        ac_data = data.get("acceptance_criteria", {})

        return GroundTruthDataset(
            dataset_id=data["dataset_id"],
            dataset_name=data["dataset_name"],
            dataset_version=data["dataset_version"],
            dataset_type=DatasetType(data["dataset_type"]),
            status=DatasetStatus(data["status"]),
            created_by=data["created_by"],
            created_at=__import__("datetime").datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            description=data["description"],
            repository_classification=RepositoryClassification(data["repository_classification"]),
            provenance=Provenance(
                source=prov_data.get("source", ""),
                methodology=prov_data.get("methodology", ""),
                reproducibility=prov_data.get("reproducibility", ""),
                tools=prov_data.get("tools", []),
                parameters=prov_data.get("parameters", {}),
                parent_dataset=prov_data.get("parent_dataset"),
            ),
            ground_truth=GroundTruth(
                anomaly_present=gt_data.get("anomaly_present", False),
                anomaly_type=anomaly_type,
                anomaly_severity=AnomalySeverity(gt_data.get("anomaly_severity", "none")),
                anomaly_window_start=gt_data.get("anomaly_window_start"),
                anomaly_window_end=gt_data.get("anomaly_window_end"),
                expected_detector_outputs=expected_detectors,
                expected_metric_values=expected_metrics,
                expected_scores=ExpectedScores(
                    integrity_score_range=tuple(integrity_range) if integrity_range else None,
                    confidence_score_range=tuple(confidence_range) if confidence_range else None,
                ),
            ),
            acceptance_criteria=AcceptanceCriteria(
                d01_sensitivity_min=ac_data.get("D-01_sensitivity_min") or ac_data.get("d01_sensitivity_min"),
                d01_specificity_min=ac_data.get("D-01_specificity_min") or ac_data.get("d01_specificity_min"),
                d02_sensitivity_min=ac_data.get("D-02_sensitivity_min") or ac_data.get("d02_sensitivity_min"),
                d02_specificity_min=ac_data.get("D-02_specificity_min") or ac_data.get("d02_specificity_min"),
                d03_sensitivity_min=ac_data.get("D-03_sensitivity_min") or ac_data.get("d03_sensitivity_min"),
                d03_specificity_min=ac_data.get("D-03_specificity_min") or ac_data.get("d03_specificity_min"),
                metric_computation_tolerance=ac_data.get("metric_computation_tolerance", 0.01),
                determinism_required=ac_data.get("determinism_required", True),
            ),
            versioning=Versioning(
                changelog=ver_data.get("changelog", []),
                compatibility=ver_data.get("compatibility", "backward-compatible"),
                supersedes=ver_data.get("supersedes"),
            ),
            certification=Certification(
                certified_by=cert_data.get("certified_by", ""),
                certified_at=__import__("datetime").datetime.fromisoformat(
                    cert_data["certified_at"].replace("Z", "+00:00")
                ) if cert_data.get("certified_at") else None,
                criteria=cert_data.get("criteria", ""),
                certificate_id=cert_data.get("certificate_id"),
            ),
            licensing=Licensing(
                license=lic_data.get("license", "MIT"),
                attribution=lic_data.get("attribution"),
                usage_restrictions=lic_data.get("usage_restrictions"),
            ),
            language=data.get("language", "python"),
            commit_count=data.get("commit_count", 0),
            contributor_count=data.get("contributor_count", 0),
            time_span_days=data.get("time_span_days", 0),
            tags=data.get("tags", []),
        )
