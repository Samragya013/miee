"""
Git enhancements for MIIE — submodule and LFS awareness.

Provides utilities to:
  - Detect and enumerate git submodules
  - Detect Git LFS tracked patterns
  - Filter out submodule pointer changes from line-change metrics
  - Filter out LFS pointer files from metrics

Scalability: prevents submodule pointer files and LFS pointers from
inflating M-01/M-07 metrics in repos that use these features.

Reference: MIIE Scalability Phase 6c
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Submodule detection
# ---------------------------------------------------------------------------


def detect_submodules(repo_path: Path) -> List[str]:
    """Detect git submodules in a repository.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of submodule paths (e.g., ["lib/external", "vendor/deps"]).
    """
    gitmodules = repo_path / ".gitmodules"
    if not gitmodules.exists():
        return []

    submodules: List[str] = []
    try:
        content = gitmodules.read_text(encoding="utf-8")
        in_submodule = False
        current_path = None

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("[submodule"):
                if current_path:
                    submodules.append(current_path)
                in_submodule = True
                current_path = None
                continue
            if in_submodule and stripped.startswith("path"):
                # path = lib/external
                parts = stripped.split("=", 1)
                if len(parts) == 2:
                    current_path = parts[1].strip()
            if stripped.startswith("[") and in_submodule:
                if current_path:
                    submodules.append(current_path)
                in_submodule = False
                current_path = None

        if current_path:
            submodules.append(current_path)

    except Exception as e:
        logger.debug("Failed to parse .gitmodules: %s", e)

    return submodules


def get_submodule_files(repo_path: Path) -> Set[str]:
    """Get all file paths belonging to submodules.

    Args:
        repo_path: Path to the repository root.

    Returns:
        Set of file paths that are inside submodule directories.
    """
    submodules = detect_submodules(repo_path)
    if not submodules:
        return set()

    submodule_files: Set[str] = set()
    for sub_path in submodules:
        # All files under the submodule directory
        full_path = repo_path / sub_path
        if full_path.is_dir():
            try:
                for file in full_path.rglob("*"):
                    if file.is_file():
                        rel = file.relative_to(repo_path)
                        submodule_files.add(str(rel).replace("\\", "/"))
            except (PermissionError, OSError):
                pass

    return submodule_files


def is_submodule_change(file_path: str, submodule_paths: List[str]) -> bool:
    """Check if a file path is a submodule pointer change.

    Submodule pointer changes appear as single-line diffs with a SHA
    reference (e.g., "-Subproject commit abc123\n+Subproject commit def456").

    Args:
        file_path: Relative file path in the repo.
        submodule_paths: List of submodule directory paths.

    Returns:
        True if the file is a submodule pointer.
    """
    for sub_path in submodule_paths:
        if file_path == sub_path or file_path.startswith(sub_path + "/"):
            return True
    return False


# ---------------------------------------------------------------------------
# Git LFS detection
# ---------------------------------------------------------------------------


def detect_lfs_patterns(repo_path: Path) -> List[str]:
    """Detect Git LFS tracked patterns from .gitattributes.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of LFS glob patterns (e.g., ["*.psd", "assets/**"]).
    """
    gitattributes = repo_path / ".gitattributes"
    if not gitattributes.exists():
        return []

    patterns: List[str] = []
    try:
        content = gitattributes.read_text(encoding="utf-8")
        for line in content.splitlines():
            stripped = line.strip()
            if "filter=lfs" in stripped:
                # Parse: *.psd filter=lfs diff=lfs merge=lfs -text
                parts = stripped.split()
                if parts:
                    patterns.append(parts[0])
    except Exception as e:
        logger.debug("Failed to parse .gitattributes: %s", e)

    return patterns


def is_lfs_pointer(file_path: str, lfs_patterns: List[str]) -> bool:
    """Check if a file matches LFS tracking patterns.

    Args:
        file_path: Relative file path in the repo.
        lfs_patterns: List of LFS glob patterns.

    Returns:
        True if the file matches an LFS pattern.
    """
    import fnmatch

    for pattern in lfs_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False


def get_lfs_files(repo_path: Path) -> Set[str]:
    """Get all files currently tracked by LFS in the repository.

    Uses `git lfs ls-files` to get the actual list.

    Args:
        repo_path: Path to the repository root.

    Returns:
        Set of file paths tracked by LFS.
    """
    try:
        result = subprocess.run(
            ["git", "lfs", "ls-files", "--name-only"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if result.returncode == 0:
            return {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return set()


# ---------------------------------------------------------------------------
# Combined filtering
# ---------------------------------------------------------------------------


def filter_files_for_metrics(
    file_paths: List[str],
    submodule_files: Optional[Set[str]] = None,
    lfs_files: Optional[Set[str]] = None,
    lfs_patterns: Optional[List[str]] = None,
) -> Tuple[List[str], Dict[str, int]]:
    """Filter file paths to exclude submodule and LFS files from metrics.

    Args:
        file_paths: Original list of file paths.
        submodule_files: Set of submodule file paths to exclude.
        lfs_files: Set of LFS-tracked file paths to exclude.
        lfs_patterns: LFS glob patterns for additional matching.

    Returns:
        Tuple of (filtered_paths, stats_dict) where stats_dict contains
        counts of excluded files by reason.
    """
    stats = {"submodule": 0, "lfs": 0}
    filtered: List[str] = []

    for path in file_paths:
        if submodule_files and path in submodule_files:
            stats["submodule"] += 1
            continue
        if lfs_files and path in lfs_files:
            stats["lfs"] += 1
            continue
        if lfs_patterns and is_lfs_pointer(path, lfs_patterns):
            stats["lfs"] += 1
            continue
        filtered.append(path)

    return filtered, stats
