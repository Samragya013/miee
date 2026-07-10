"""Tests for MIIE package structure validation (v1.5)."""

from pathlib import Path

import pytest

# Root directory of the project
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "src" / "miie"

# Expected packages according to v1.5 architecture
# (common, detection, interface removed — empty legacy packages)
EXPECTED_PACKAGES = {
    "api",
    "benchmark",
    "cli",
    "config",
    "contracts",
    "experimental",
    "metrics",
    "observation_graph",
    "orchestration",
    "processing",
    "providers",
    "reporting",
    "sampling",
    "schemas",
    "scientific",
    "storage",
    "utils",
    "validation",
}


def test_src_miie_exists():
    """Test that src/miie directory exists."""
    assert SRC_DIR.exists() and SRC_DIR.is_dir(), f"Source directory {SRC_DIR} does not exist"


def test_all_expected_packages_exist():
    """Test that all expected packages exist as directories with __init__.py."""
    missing_packages = []

    for package in EXPECTED_PACKAGES:
        package_dir = SRC_DIR / package
        init_file = package_dir / "__init__.py"

        if not package_dir.exists() or not package_dir.is_dir():
            missing_packages.append(f"{package} (missing directory)")
        elif not init_file.exists():
            missing_packages.append(f"{package} (missing __init__.py)")

    assert not missing_packages, f"Missing or incomplete packages: {', '.join(missing_packages)}"


def test_no_unexpected_packages():
    """Test that no unexpected packages exist in src/miie."""
    actual_packages = {
        d.name for d in SRC_DIR.iterdir() if d.is_dir() and (d / "__init__.py").exists() and not d.name.startswith("__")
    }

    unexpected = actual_packages - EXPECTED_PACKAGES
    assert not unexpected, f"Unexpected packages found: {', '.join(unexpected)}"


def test_package_init_files():
    """Test that all package __init__.py files are valid Python files."""
    for package in EXPECTED_PACKAGES:
        init_file = SRC_DIR / package / "__init__.py"
        assert init_file.exists(), f"__init__.py missing for package {package}"

        # Basic validation - file should be readable and contain expected content
        content = init_file.read_text(encoding="utf-8").strip()
        assert content, f"__init__.py is empty for package {package}"
        # Should contain at least a docstring or comment
        assert (
            '"""' in content or "'''" in content or "#" in content
        ), f"__init__.py appears to be missing documentation for package {package}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
