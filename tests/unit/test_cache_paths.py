from pathlib import Path
from unittest.mock import patch

import pytest

from miie.processing.ingestion import cache_path_for_repository


def test_cache_path_for_repository_returns_correct_structure():
    """Test that the function returns a Path under ~/.miie/cache/repos/{repo_id}."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        repo_id = "abc123"
        result = cache_path_for_repository(repo_id)
        expected = Path("/fake/home/.miie/cache/repos/abc123").resolve()
        assert result == expected
        assert isinstance(result, Path)


def test_cache_path_for_repository_is_deterministic():
    """Test that the same repo_id always yields the same path."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        repo_id = "same-id"
        path1 = cache_path_for_repository(repo_id)
        path2 = cache_path_for_repository(repo_id)
        assert path1 == path2


def test_cache_path_for_repository_is_normalized():
    """Test that the returned path is resolved (normalized)."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        repo_id = "test-repo"
        result = cache_path_for_repository(repo_id)
        # The result should be resolved (no symlinks, no . or .. components)
        assert result == result.resolve()


def test_cache_path_for_repository_allows_parent_dot_dot_equals_cache_root():
    """Test that repo_id='..' results in cache root (allowed, not escape)."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        repo_id = ".."
        result = cache_path_for_repository(repo_id)
        expected = Path("/fake/home/.miie/cache").resolve()
        assert result == expected


def test_cache_path_for_repository_prevents_escape_via_relative_path():
    """Test that repo_id with enough '..' to escape cache root raises ValueError."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        # cache_root = /fake/home/.miie/cache
        # repo_id = '../../..' leads to /fake/home (escape)
        repo_id = "../../.."
        with pytest.raises(ValueError, match=r"Attempted to escape cache root"):
            cache_path_for_repository(repo_id)


def test_cache_path_for_repository_prevents_escape_via_absolute_path():
    """Test that an absolute repo_id (though unlikely) is still contained."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        repo_id = "/etc/passwd"
        with pytest.raises(ValueError, match=r"Attempted to escape cache root"):
            cache_path_for_repository(repo_id)


def test_cache_path_for_repository_handles_normal_repo_id():
    """Test with a typical repo ID."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        repo_id = "my-repo_1"
        result = cache_path_for_repository(repo_id)
        expected = Path("/fake/home/.miie/cache/repos/my-repo_1").resolve()
        assert result == expected


def test_cache_path_for_repository_raises_on_escape_attempt():
    """Test that any attempt to escape via normalized path raises."""
    with patch("pathlib.Path.home", return_value=Path("/fake/home")):
        # Using a repo_id that after joining and resolving goes outside
        repo_id = "../../../.."  # more ups
        with pytest.raises(ValueError):
            cache_path_for_repository(repo_id)


if __name__ == "__main__":
    pytest.main([__file__])
