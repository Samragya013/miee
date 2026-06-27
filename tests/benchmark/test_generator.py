"""Unit tests for BenchmarkDatasetGenerator."""

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

from miie.benchmark.generator import BenchmarkDatasetGenerator


def remove_readonly(func, path, exc):
    """Error handler for shutil.rmtree to remove read-only files on Windows."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def test_generator_creation():
    """Test creating a BenchmarkDatasetGenerator instance."""
    generator = BenchmarkDatasetGenerator()
    assert isinstance(generator, BenchmarkDatasetGenerator)


@pytest.mark.skip(reason="Slow: creates real git repos with 1000+ commits; tested in CI nightly")
def test_generate_single_candidate():
    """Test generating a single candidate."""
    generator = BenchmarkDatasetGenerator()
    output_dir = Path("test_output_single")
    # Clean up if exists
    if output_dir.exists():
        shutil.rmtree(output_dir, onerror=remove_readonly)

    try:
        paths = generator.generate("metric-drift", 1, output_dir, seed=42)
        assert len(paths) == 1
        candidate_dir = paths[0]
        assert candidate_dir.exists()
        assert candidate_dir.is_dir()

        # Check that metadata.json exists
        metadata_path = candidate_dir / "metadata.json"
        assert metadata_path.exists()
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        assert "repo_id" in metadata
        assert metadata["repo_id"] == "repo_001"
        assert "generation_seed" in metadata
        assert isinstance(metadata["generation_seed"], int)

        # Check that it's a git repo
        git_dir = candidate_dir / ".git"
        assert git_dir.exists()
        assert git_dir.is_dir()

        # Check that we have at least one commit
        result = subprocess.run(
            ["git", "rev-parse", "--HEAD"],
            cwd=candidate_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() != ""

    finally:
        # Clean up
        if output_dir.exists():
            shutil.rmtree(output_dir, onerror=remove_readonly)


@pytest.mark.skip(reason="Slow: creates real git repos with 1000+ commits each; tested in CI nightly")
def test_generate_multiple_candidates():
    """Test generating multiple candidates."""
    generator = BenchmarkDatasetGenerator()
    output_dir = Path("test_output_multiple")
    # Clean up if exists
    if output_dir.exists():
        shutil.rmtree(output_dir, onerror=remove_readonly)

    try:
        count = 5
        paths = generator.generate("correlation-breakdown", count, output_dir, seed=123)
        assert len(paths) == count
        for i, path in enumerate(paths):
            expected_id = f"candidate_{i+1:03d}"
            assert path.name == expected_id
            assert path.exists()
            assert path.is_dir()

            # Check metadata
            metadata_path = path / "metadata.json"
            assert metadata_path.exists()
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            assert metadata["repo_id"] == f"repo_{i+1:03d}"
            # The seed should be derived from base seed and index
            # We can't easily predict the derived seed, but we can check it's an integer
            assert isinstance(metadata["generation_seed"], int)

    finally:
        if output_dir.exists():
            shutil.rmtree(output_dir, onerror=remove_readonly)


@pytest.mark.skip(reason="Slow: creates real git repos with 1000+ commits each; tested in CI nightly")
def test_deterministic_generation():
    """Test that same seed produces same repositories."""
    generator = BenchmarkDatasetGenerator()
    output_dir1 = Path("test_output_det1")
    output_dir2 = Path("test_output_det2")
    # Clean up
    for d in [output_dir1, output_dir2]:
        if d.exists():
            shutil.rmtree(d, onerror=remove_readonly)

    try:
        # Generate first set
        paths1 = generator.generate("threshold-compression", 3, output_dir1, seed=999)
        # Generate second set
        paths2 = generator.generate("threshold-compression", 3, output_dir2, seed=999)

        # Compare metadata.json files
        for p1, p2 in zip(paths1, paths2):
            meta1_path = p1 / "metadata.json"
            meta2_path = p2 / "metadata.json"
            assert meta1_path.exists()
            assert meta2_path.exists()
            with open(meta1_path, "r") as f1, open(meta2_path, "r") as f2:
                meta1 = json.load(f1)
                meta2 = json.load(f2)
                # The generation_seed should be the same
                assert meta1["generation_seed"] == meta2["generation_seed"]
                # The repo_id should be the same
                assert meta1["repo_id"] == meta2["repo_id"]
                # We could compare the entire metadata, but some fields like timestamp may differ
                # Instead, we'll check that the parameters are the same (since they are deterministic)
                assert meta1["parameters"] == meta2["parameters"]

    finally:
        for d in [output_dir1, output_dir2]:
            if d.exists():
                shutil.rmtree(d, onerror=remove_readonly)


@pytest.mark.skip(reason="Slow: creates real git repos with 1000+ commits each; tested in CI nightly")
def test_git_repo_validity():
    """Test that generated directories are valid Git repositories."""
    generator = BenchmarkDatasetGenerator()
    output_dir = Path("test_output_git")
    # Clean up
    if output_dir.exists():
        shutil.rmtree(output_dir, onerror=remove_readonly)

    try:
        paths = generator.generate("metric-drift", 2, output_dir, seed=555)
        for path in paths:
            # Check that .git directory exists
            git_dir = path / ".git"
            assert git_dir.exists()
            # Check that we can run git status
            result = subprocess.run(["git", "status"], cwd=path, capture_output=True, text=True)
            assert result.returncode == 0
            # Check that we have at least one commit
            result = subprocess.run(["git", "log", "--oneline"], cwd=path, capture_output=True, text=True)
            assert result.returncode == 0
            lines = result.stdout.strip().split("\n")
            assert len(lines) >= 1
            # Each line should be a commit hash and message
            for line in lines:
                assert len(line) > 0

    finally:
        if output_dir.exists():
            shutil.rmtree(output_dir, onerror=remove_readonly)


if __name__ == "__main__":
    # Run tests if executed directly
    test_generator_creation()
    print("test_generator_creation passed")
    test_generate_single_candidate()
    print("test_generate_single_candidate passed")
    test_generate_multiple_candidates()
    print("test_generate_multiple_candidates passed")
    test_deterministic_generation()
    print("test_deterministic_generation passed")
    test_git_repo_validity()
    print("test_git_repo_validity passed")
    print("All tests passed!")
