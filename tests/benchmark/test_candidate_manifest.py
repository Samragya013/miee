"""Tests for benchmark candidate manifest."""

import json
from pathlib import Path


def test_candidate_manifest_exists():
    """Test that the candidate manifest file exists."""
    manifest_path = Path("benchmarks/metadata/candidate_manifest.json")
    assert manifest_path.exists(), "Candidate manifest file should exist"


def test_candidate_manifest_is_valid_json():
    """Test that the candidate manifest contains valid JSON."""
    manifest_path = Path("benchmarks/metadata/candidate_manifest.json")
    with open(manifest_path, "r") as f:
        data = json.load(f)

    # Check required top-level keys
    assert "benchmark_info" in data
    assert "candidates" in data

    # Check benchmark info
    assert data["benchmark_info"]["total_candidates"] == 120
    assert data["benchmark_info"]["status"] == "candidate"

    # Check that we have exactly 120 candidates
    assert len(data["candidates"]) == 120

    # Check that candidate IDs are properly formatted
    for i in range(1, 121):
        expected_id = f"candidate_{i:03d}"
        assert expected_id in data["candidates"], f"Missing {expected_id}"

        candidate = data["candidates"][expected_id]
        assert candidate["id"] == expected_id
        assert "anomaly_present" in candidate
        assert "expected_metrics" in candidate
        assert isinstance(candidate["expected_metrics"], list)


def test_candidate_directories_exist():
    """Test that candidate directories that exist on disk match the manifest."""
    base_path = Path("benchmarks/datasets/candidates")
    assert base_path.exists(), "Candidates directory should exist"

    manifest_path = Path("benchmarks/metadata/candidate_manifest.json")
    with open(manifest_path, "r") as f:
        data = json.load(f)

    existing_dirs = [d.name for d in base_path.iterdir() if d.is_dir()]

    for candidate_id in data["candidates"]:
        candidate_path = base_path / candidate_id
        if candidate_id in existing_dirs:
            assert candidate_path.is_dir(), f"Path for {candidate_id} exists but is not a directory"

            metadata_path = candidate_path / "metadata.json"
            assert metadata_path.exists(), f"Metadata file for {candidate_id} should exist"


def test_annotation_directories_exist():
    """Test that annotation directory structure exists."""
    annotations_path = Path("benchmarks/annotations")
    assert annotations_path.exists(), "Annotations directory should exist"

    # Check reviewer directories
    assert (annotations_path / "reviewer_a").exists(), "Reviewer A directory should exist"
    assert (annotations_path / "reviewer_b").exists(), "Reviewer B directory should exist"
    assert (annotations_path / "adjudication").exists(), "Adjudication directory should exist"


def test_benchmark_readme_exists():
    """Test that benchmarks README exists."""
    readme_path = Path("benchmarks/README.md")
    assert readme_path.exists(), "Benchmarks README should exist"


def test_annotation_workflow_exists():
    """Test that annotation workflow document exists."""
    workflow_path = Path("benchmarks/annotations/annotation_workflow.md")
    assert workflow_path.exists(), "Annotation workflow document should exist"
