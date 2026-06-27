"""Hashing utilities for reproducibility and manifest provenance (BSD §20)."""

import hashlib
import json
import os
import platform
import subprocess
import sys


def compute_config_hash(config: dict) -> str:
    """SHA-256 of JSON-serialized config with sorted keys."""
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def compute_file_hash(filepath: str) -> str:
    """SHA-256 of file contents."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def compute_dependency_hash() -> str:
    """SHA-256 of poetry.lock."""
    lock_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "poetry.lock")
    lock_path = os.path.normpath(lock_path)
    if os.path.exists(lock_path):
        return compute_file_hash(lock_path)
    return "unknown"


def get_git_commit() -> str:
    """Get current git commit hash, or 'unknown' if not in a git repo."""
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return "unknown"


def get_platform_info() -> str:
    """Get platform identifier: system + machine."""
    return f"{platform.system()}-{platform.machine()}"


def get_python_version() -> str:
    """Get Python version string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
