"""Tests for manifest provenance completeness (BSD §20)."""

import json
import hashlib
import os
import tempfile
from pathlib import Path

import pytest

from miie.utils.hashing import (
    compute_config_hash,
    compute_file_hash,
    compute_dependency_hash,
    get_git_commit,
    get_platform_info,
    get_python_version,
)


REQUIRED_MANIFEST_FIELDS = [
    "manifest_version",
    "miie_version",
    "git_commit",
    "python_version",
    "dependency_hash",
    "config_hash",
    "seed",
    "timestamp",
    "platform",
    "artifact_checksums",
]


class TestManifestProvenance:
    """Test that manifest.json contains all 10 required provenance fields (BSD §20.5)."""

    def test_manifest_has_all_required_fields(self, tmp_path):
        """Manifest must contain every field listed in BSD §20.5 required array."""
        from miie.processing.reporting.engine import ReportGenerator

        gen = ReportGenerator()
        result = {"integrity": {"overall": 1.0}, "confidence": {"overall": 1.0}}

        # Use a config hash and seed
        config = {"seed": 42, "metrics": ["M-02"]}
        config_hash = compute_config_hash(config)

        report_out = gen.generate(
            analysis_result=result,
            output_formats=["json"],
            output_dir=tmp_path,
            config_hash=config_hash,
            seed=42,
        )

        manifest_path = report_out.manifest_path
        assert manifest_path.exists(), "manifest.json was not created"

        with open(manifest_path) as f:
            manifest = json.load(f)

        for field in REQUIRED_MANIFEST_FIELDS:
            assert field in manifest, f"Missing required manifest field: {field}"

    def test_manifest_manifest_version_is_1_0_0(self, tmp_path):
        from miie.processing.reporting.engine import ReportGenerator

        gen = ReportGenerator()
        report_out = gen.generate(
            analysis_result={"test": True},
            output_formats=["json"],
            output_dir=tmp_path,
        )
        with open(report_out.manifest_path) as f:
            manifest = json.load(f)
        assert manifest["manifest_version"] == "1.0.0"

    def test_manifest_miie_version_is_1_0_0(self, tmp_path):
        from miie.processing.reporting.engine import ReportGenerator

        gen = ReportGenerator()
        report_out = gen.generate(
            analysis_result={"test": True},
            output_formats=["json"],
            output_dir=tmp_path,
        )
        with open(report_out.manifest_path) as f:
            manifest = json.load(f)
        assert manifest["miie_version"] == "1.0.0"

    def test_manifest_timestamp_is_utc_iso8601(self, tmp_path):
        from miie.processing.reporting.engine import ReportGenerator

        gen = ReportGenerator()
        report_out = gen.generate(
            analysis_result={"test": True},
            output_formats=["json"],
            output_dir=tmp_path,
        )
        with open(report_out.manifest_path) as f:
            manifest = json.load(f)
        ts = manifest["timestamp"]
        assert ts.endswith("Z"), f"Timestamp must end with Z suffix, got: {ts}"
        assert "T" in ts, f"Timestamp must be ISO 8601, got: {ts}"

    def test_manifest_seed_matches_input(self, tmp_path):
        from miie.processing.reporting.engine import ReportGenerator

        gen = ReportGenerator()
        report_out = gen.generate(
            analysis_result={"test": True},
            output_formats=["json"],
            output_dir=tmp_path,
            seed=123,
        )
        with open(report_out.manifest_path) as f:
            manifest = json.load(f)
        assert manifest["seed"] == 123

    def test_manifest_platform_is_nonempty(self, tmp_path):
        from miie.processing.reporting.engine import ReportGenerator

        gen = ReportGenerator()
        report_out = gen.generate(
            analysis_result={"test": True},
            output_formats=["json"],
            output_dir=tmp_path,
        )
        with open(report_out.manifest_path) as f:
            manifest = json.load(f)
        assert isinstance(manifest["platform"], str)
        assert len(manifest["platform"]) > 0

    def test_manifest_artifact_checksums_match_actual_files(self, tmp_path):
        from miie.processing.reporting.engine import ReportGenerator

        gen = ReportGenerator()
        report_out = gen.generate(
            analysis_result={"test": True},
            output_formats=["json", "md"],
            output_dir=tmp_path,
        )
        with open(report_out.manifest_path) as f:
            manifest = json.load(f)

        checksums = manifest["artifact_checksums"]
        for fmt_name, file_path in report_out.report_paths.items():
            if file_path.exists():
                expected = compute_file_hash(str(file_path))
                # Checksums in manifest should match re-computed checksums
                if fmt_name in checksums:
                    assert checksums[fmt_name] == expected, (
                        f"Checksum mismatch for {fmt_name}: "
                        f"manifest={checksums[fmt_name]}, actual={expected}"
                    )


class TestConfigHashDeterministic:
    """Test that config hash computation is deterministic."""

    def test_same_config_same_hash(self):
        config = {"seed": 42, "metrics": ["M-02", "M-06"], "window_size": 7}
        h1 = compute_config_hash(config)
        h2 = compute_config_hash(config)
        assert h1 == h2

    def test_sorted_keys_produce_same_hash(self):
        """Dict insertion order should not matter."""
        config_a = {"seed": 42, "metrics": ["M-02"]}
        config_b = {"metrics": ["M-02"], "seed": 42}
        assert compute_config_hash(config_a) == compute_config_hash(config_b)

    def test_different_configs_different_hashes(self):
        config_a = {"seed": 42}
        config_b = {"seed": 99}
        assert compute_config_hash(config_a) != compute_config_hash(config_b)

    def test_hash_is_sha256_hex(self):
        h = compute_config_hash({"x": 1})
        assert len(h) == 64, f"SHA-256 hex should be 64 chars, got {len(h)}"
        assert all(c in "0123456789abcdef" for c in h)


class TestDependencyHash:
    """Test dependency hash computation."""

    def test_dependency_hash_matches_poetry_lock(self):
        lock_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'poetry.lock'
        )
        lock_path = os.path.normpath(lock_path)
        if os.path.exists(lock_path):
            expected = compute_file_hash(lock_path)
            actual = compute_dependency_hash()
            assert actual == expected
        else:
            # If no poetry.lock, should return "unknown"
            assert compute_dependency_hash() == "unknown"

    def test_dependency_hash_is_deterministic(self):
        h1 = compute_dependency_hash()
        h2 = compute_dependency_hash()
        assert h1 == h2


class TestFileHash:
    """Test file hash utility."""

    def test_file_hash_matches_manual_sha256(self, tmp_path):
        content = b"hello world"
        fpath = tmp_path / "test.txt"
        fpath.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        actual = compute_file_hash(str(fpath))
        assert actual == expected

    def test_file_hash_empty_file(self, tmp_path):
        fpath = tmp_path / "empty.txt"
        fpath.write_bytes(b"")
        expected = hashlib.sha256(b"").hexdigest()
        actual = compute_file_hash(str(fpath))
        assert actual == expected


class TestGitCommit:
    """Test git commit retrieval."""

    def test_get_git_commit_returns_string(self):
        result = get_git_commit()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_git_commit_deterministic(self):
        r1 = get_git_commit()
        r2 = get_git_commit()
        assert r1 == r2


class TestPlatformInfo:
    """Test platform info utility."""

    def test_platform_contains_system(self):
        info = get_platform_info()
        import platform
        assert platform.system() in info

    def test_platform_contains_machine(self):
        info = get_platform_info()
        import platform
        assert platform.machine() in info


class TestPythonVersion:
    """Test Python version utility."""

    def test_python_version_format(self):
        import sys
        ver = get_python_version()
        expected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert ver == expected
