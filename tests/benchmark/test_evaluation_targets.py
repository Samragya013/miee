"""Tests for benchmark evaluation scripts.

Covers:
- Evaluation script can run without errors
- Target validation logic
- Evaluation results have all required fields
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

BENCHMARKS_DIR = Path(__file__).resolve().parent.parent.parent / "benchmarks"
RESULTS_DIR = BENCHMARKS_DIR / "results"


def _run_evaluation(seed: int = 42) -> subprocess.CompletedProcess:
    """Run the evaluation script as a subprocess."""
    return subprocess.run(
        [
            sys.executable,
            str(BENCHMARKS_DIR / "run_evaluation.py"),
            "--seed",
            str(seed),
            "--output",
            str(RESULTS_DIR),
        ],
        capture_output=True,
        text=True,
        cwd=str(BENCHMARKS_DIR.parent),
    )


def _run_validation() -> subprocess.CompletedProcess:
    """Run the validation script as a subprocess."""
    return subprocess.run(
        [
            sys.executable,
            str(BENCHMARKS_DIR / "validate_targets.py"),
            "--results-dir",
            str(RESULTS_DIR),
        ],
        capture_output=True,
        text=True,
        cwd=str(BENCHMARKS_DIR.parent),
    )


# ---------------------------------------------------------------------------
# Test: evaluation script runs without errors
# ---------------------------------------------------------------------------
class TestEvaluationScript:
    """Tests that run_evaluation.py executes successfully."""

    def test_exits_zero(self):
        result = _run_evaluation(seed=42)
        assert result.returncode == 0, (
            f"run_evaluation.py exited with code {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_creates_output_files(self):
        _run_evaluation(seed=42)
        for fname in (
            "D-01_evaluation.json",
            "D-02_evaluation.json",
            "D-03_evaluation.json",
            "benchmark_summary.json",
        ):
            path = RESULTS_DIR / fname
            assert path.exists(), f"Expected output file not found: {path}"

    def test_deterministic_with_same_seed(self):
        _run_evaluation(seed=99)
        content_first = {}
        for fname in (
            "D-01_evaluation.json",
            "D-02_evaluation.json",
            "D-03_evaluation.json",
        ):
            content_first[fname] = (RESULTS_DIR / fname).read_text(encoding="utf-8")

        _run_evaluation(seed=99)
        for fname, first_content in content_first.items():
            second_content = (RESULTS_DIR / fname).read_text(encoding="utf-8")
            assert first_content == second_content, f"Results differ across runs with same seed for {fname}"

    def test_different_seeds_produce_different_results(self):
        _run_evaluation(seed=42)
        content_a = {}
        for fname in (
            "D-01_evaluation.json",
            "D-02_evaluation.json",
            "D-03_evaluation.json",
        ):
            content_a[fname] = (RESULTS_DIR / fname).read_text(encoding="utf-8")

        _run_evaluation(seed=123)
        any_different = False
        for fname in content_a:
            content_b = (RESULTS_DIR / fname).read_text(encoding="utf-8")
            if content_a[fname] != content_b:
                any_different = True
                break
        assert any_different, "Different seeds should produce different results"


# ---------------------------------------------------------------------------
# Test: validation script runs without errors
# ---------------------------------------------------------------------------
class TestValidationScript:
    """Tests that validate_targets.py executes successfully."""

    def test_exits_zero_when_targets_met(self):
        # First run evaluation to produce results
        _run_evaluation(seed=42)
        result = _run_validation()
        assert result.returncode == 0, (
            f"validate_targets.py exited with code {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_prints_pass_or_fail(self):
        _run_evaluation(seed=42)
        result = _run_validation()
        output = result.stdout
        assert "PASS" in output or "FAIL" in output, "Validation output should contain PASS or FAIL"

    def test_exits_one_when_results_missing(self):
        """Validation should fail if results directory is empty."""
        import shutil

        temp_dir = RESULTS_DIR / "_temp_empty"
        temp_dir.mkdir(exist_ok=True)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(BENCHMARKS_DIR / "validate_targets.py"),
                    "--results-dir",
                    str(temp_dir),
                ],
                capture_output=True,
                text=True,
                cwd=str(BENCHMARKS_DIR.parent),
            )
            assert result.returncode == 1
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Test: evaluation results have all required fields
# ---------------------------------------------------------------------------
class TestEvaluationResultSchema:
    """Tests that evaluation JSONs match the BSD §16 schema."""

    REQUIRED_FIELDS = (
        "suite_id",
        "detector_id",
        "detector_version",
        "metrics",
        "confusion_matrix",
        "per_dataset_results",
    )

    REQUIRED_METRICS = (
        "accuracy",
        "precision",
        "recall",
        "f1",
        "auc_roc",
        "auc_pr",
        "fpr",
        "fnr",
    )

    REQUIRED_CM_FIELDS = ("tp", "fp", "tn", "fn")

    DETECTOR_IDS = ("D-01", "D-02", "D-03")

    @pytest.fixture(autouse=True)
    def run_eval(self):
        """Ensure evaluation results exist before schema tests."""
        _run_evaluation(seed=42)

    @pytest.mark.parametrize("detector_id", DETECTOR_IDS)
    def test_has_required_top_level_fields(self, detector_id):
        path = RESULTS_DIR / f"{detector_id}_evaluation.json"
        assert path.exists(), f"Missing {detector_id} evaluation file"
        data = json.loads(path.read_text(encoding="utf-8"))
        for field in self.REQUIRED_FIELDS:
            assert field in data, f"{detector_id} missing required field: {field}"

    @pytest.mark.parametrize("detector_id", DETECTOR_IDS)
    def test_has_required_metrics(self, detector_id):
        path = RESULTS_DIR / f"{detector_id}_evaluation.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        metrics = data["metrics"]
        for metric in self.REQUIRED_METRICS:
            assert metric in metrics, f"{detector_id} metrics missing: {metric}"
            assert isinstance(metrics[metric], (int, float)), f"{detector_id} metrics['{metric}'] must be numeric"
            assert (
                0.0 <= metrics[metric] <= 1.0
            ), f"{detector_id} metrics['{metric}'] = {metrics[metric]}, expected [0, 1]"

    @pytest.mark.parametrize("detector_id", DETECTOR_IDS)
    def test_has_confusion_matrix_fields(self, detector_id):
        path = RESULTS_DIR / f"{detector_id}_evaluation.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        cm = data["confusion_matrix"]
        for field in self.REQUIRED_CM_FIELDS:
            assert field in cm, f"{detector_id} confusion_matrix missing: {field}"
            assert isinstance(cm[field], int), f"{detector_id} confusion_matrix['{field}'] must be int"
            assert cm[field] >= 0, f"{detector_id} confusion_matrix['{field}'] must be >= 0"

    @pytest.mark.parametrize("detector_id", DETECTOR_IDS)
    def test_detector_id_matches_filename(self, detector_id):
        path = RESULTS_DIR / f"{detector_id}_evaluation.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["detector_id"] == detector_id

    @pytest.mark.parametrize("detector_id", DETECTOR_IDS)
    def test_per_dataset_results_is_dict(self, detector_id):
        path = RESULTS_DIR / f"{detector_id}_evaluation.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data["per_dataset_results"], dict)

    def test_summary_has_all_detectors(self):
        path = RESULTS_DIR / "benchmark_summary.json"
        assert path.exists(), "benchmark_summary.json not found"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "hard_targets" in data
        assert "results" in data
        assert "targets_met" in data
        for det in self.DETECTOR_IDS:
            assert det in data["results"], f"Summary missing {det} in results"
            assert det in data["targets_met"], f"Summary missing {det} in targets_met"

    def test_summary_has_overall_pass(self):
        path = RESULTS_DIR / "benchmark_summary.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "overall_pass" in data
        assert isinstance(data["overall_pass"], bool)
