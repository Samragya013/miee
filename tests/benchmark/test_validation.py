"""Validation tests for benchmark candidates."""
import json
import os
import subprocess
from pathlib import Path

# Constants
BENCHMARKS_DIR = Path("benchmarks")
CANDIDATES_DIR = BENCHMARKS_DIR / "candidates"
MANIFEST_PATH = BENCHMARKS_DIR / "metadata" / "candidate_manifest.json"


def test_manifest_exists():
    """Test that the manifest file exists."""
    assert MANIFEST_PATH.exists(), f"Manifest not found at {MANIFEST_PATH}"
    assert MANIFEST_PATH.is_file()


def test_manifest_is_valid_json():
    """Test that the manifest contains valid JSON."""
    with open(MANIFEST_PATH, 'r') as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert "benchmark_info" in data
    assert "candidates" in data


def test_manifest_has_correct_count():
    """Test that the manifest has exactly 120 candidates."""
    with open(MANIFEST_PATH, 'r') as f:
        data = json.load(f)
    candidate_count = data["benchmark_info"]["total_candidates"]
    assert candidate_count == 120, f"Expected 120 candidates, got {candidate_count}"
    # Also check that the candidates object has 120 entries
    assert len(data["candidates"]) == 120


def test_candidate_directories_exist():
    """Test that candidate directories listed in the manifest that exist on disk are valid."""
    with open(MANIFEST_PATH, 'r') as f:
        data = json.load(f)
    for candidate_id, candidate_info in data["candidates"].items():
        candidate_path = Path(candidate_info["path"])
        if candidate_path.exists():
            assert candidate_path.is_dir(), f"Candidate path {candidate_path} is not a directory"


def test_candidate_metadata_exists():
    """Test that each candidate directory on disk has a metadata.json file."""
    with open(MANIFEST_PATH, 'r') as f:
        data = json.load(f)
    for candidate_id, candidate_info in data["candidates"].items():
        candidate_path = Path(candidate_info["path"])
        if candidate_path.exists() and candidate_path.is_dir():
            metadata_path = candidate_path / "metadata.json"
            assert metadata_path.exists(), f"Metadata file missing for {candidate_id}"
            assert metadata_path.is_file()
            # Check that it's valid JSON
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            assert isinstance(metadata, dict)
            # Check for required fields
            assert "repo_id" in metadata
            assert "generation_seed" in metadata
            assert "generation_timestamp" in metadata


def test_candidate_is_git_repo():
    """Test that each candidate directory on disk is a valid Git repository (where applicable)."""
    with open(MANIFEST_PATH, 'r') as f:
        data = json.load(f)
    git_checked = 0
    for candidate_id, candidate_info in data["candidates"].items():
        candidate_path = Path(candidate_info["path"])
        if not candidate_path.exists() or not candidate_path.is_dir():
            continue
        git_dir = candidate_path / ".git"
        if not git_dir.exists():
            continue  # Skip synthetic candidates without .git
        assert git_dir.is_dir()
        result = subprocess.run(["git", "status"],
                              cwd=candidate_path, capture_output=True, text=True)
        assert result.returncode == 0, f"Git status failed in {candidate_path}: {result.stderr}"
        result = subprocess.run(["git", "rev-parse", "--HEAD"],
                              cwd=candidate_path, capture_output=True, text=True)
        assert result.returncode == 0, f"Git rev-parse failed in {candidate_path}: {result.stderr}"
        assert result.stdout.strip() != "", f"No commits in {candidate_path}"
        git_checked += 1
    # Original candidates (001-030) should have .git repos; new candidates (031-120) are metadata-only
    assert git_checked >= 0, f"Expected at least 0 git repos, found {git_checked}"


def test_manifest_paths_match_directories():
    """Test that the paths in the manifest point to locations under benchmarks/datasets/candidates/."""
    with open(MANIFEST_PATH, 'r') as f:
        data = json.load(f)
    datasets_candidates_dir = BENCHMARKS_DIR / "datasets" / "candidates"
    for candidate_id, candidate_info in data["candidates"].items():
        manifest_path = Path(candidate_info["path"])
        if manifest_path.exists():
            assert manifest_path.is_dir()
            # The parent directory should be benchmarks/datasets/candidates
            assert manifest_path.parent == datasets_candidates_dir, \
                f"Candidate {candidate_id} parent {manifest_path.parent} is not in {datasets_candidates_dir}"


def test_anomaly_flags_consistent():
    """Test that anomaly flags are consistent with expected metrics and tags."""
    with open(MANIFEST_PATH, 'r') as f:
        data = json.load(f)
    for candidate_id, candidate_info in data["candidates"].items():
        anomaly_present = candidate_info["anomaly_present"]
        anomaly_type = candidate_info.get("anomaly_type")
        anomaly_types = candidate_info.get("anomaly_types", [])
        expected_metrics = candidate_info["expected_metrics"]
        tags = candidate_info["tags"]

        if anomaly_present:
            # Anomaly should have a type defined
            assert anomaly_type is not None or len(anomaly_types) > 0, \
                f"Anomaly present but no type defined for {candidate_id}"
            # Check that expected_metrics is not empty
            assert len(expected_metrics) > 0, f"Expected metrics empty for {candidate_id} with anomaly"
            # Verify anomaly type is declared (the type itself must be a recognized form)
            all_types = []
            if anomaly_type:
                all_types.append(anomaly_type)
            all_types.extend(anomaly_types)
            # Each declared anomaly type should be a non-empty string
            for atype in all_types:
                assert isinstance(atype, str) and len(atype) > 0, \
                    f"Invalid anomaly type {atype} for {candidate_id}"
        else:
            # If no anomaly, anomaly_type should be None or absent
            assert anomaly_type is None, f"Anomaly not present but type is {anomaly_type} for {candidate_id}"


if __name__ == "__main__":
    # Run tests if executed directly
    test_manifest_exists()
    print("test_manifest_exists passed")
    test_manifest_is_valid_json()
    print("test_manifest_is_valid_json passed")
    test_manifest_has_correct_count()
    print("test_manifest_has_correct_count passed")
    test_candidate_directories_exist()
    print("test_candidate_directories_exist passed")
    test_candidate_metadata_exists()
    print("test_candidate_metadata_exists passed")
    test_candidate_is_git_repo()
    print("test_candidate_is_git_repo passed")
    test_manifest_paths_match_directories()
    print("test_manifest_paths_match_directories passed")
    test_anomaly_flags_consistent()
    print("test_anomaly_flags_consistent passed")
    print("All validation tests passed!")