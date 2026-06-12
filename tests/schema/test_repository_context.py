"""
Tests for RepositoryContext schema validation.
"""

import datetime
from pathlib import Path

import pytest

from miie.schemas.models import RepositoryContext
from miie.schemas.serialization import json_dumps, json_loads


def test_repository_context_creation():
    """Test creating a valid RepositoryContext."""
    ctx = RepositoryContext(
        repo_id="repo_001",
        local_path=Path("/path/to/repo"),
        is_remote=False,
        total_commits=100,
        first_commit_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        last_commit_date=datetime.datetime(2020, 12, 31, tzinfo=datetime.timezone.utc),
        contributor_count=5,
        is_shallow=False,
        is_fork=False,
        language_distribution={"Python": 10000, "JavaScript": 5000}
    )

    assert ctx.repo_id == "repo_001"
    assert ctx.local_path == Path("/path/to/repo")
    assert ctx.is_remote is False
    assert ctx.total_commits == 100
    assert ctx.contributor_count == 5


def test_repository_context_serialization():
    """Test deterministic serialization of RepositoryContext."""
    ctx = RepositoryContext(
        repo_id="repo_001",
        local_path=Path("/path/to/repo"),
        is_remote=True,
        remote_url="https://github.com/user/repo.git",
        total_commits=50,
        first_commit_date=datetime.datetime(2020, 6, 1, tzinfo=datetime.timezone.utc),
        last_commit_date=datetime.datetime(2020, 6, 30, tzinfo=datetime.timezone.utc),
        contributor_count=3,
        is_shallow=True,
        is_fork=True
    )

    # Convert to dict for JSON serialization (excluding Path which isn't JSON serializable)
    ctx_dict = {
        "repo_id": ctx.repo_id,
        "local_path": str(ctx.local_path),
        "is_remote": ctx.is_remote,
        "remote_url": ctx.remote_url,
        "total_commits": ctx.total_commits,
        "first_commit_date": ctx.first_commit_date.isoformat() if ctx.first_commit_date else None,
        "last_commit_date": ctx.last_commit_date.isoformat() if ctx.last_commit_date else None,
        "contributor_count": ctx.contributor_count,
        "is_shallow": ctx.is_shallow,
        "is_fork": ctx.is_fork,
        "language_distribution": ctx.language_distribution
    }

    # Serialize
    json_str = json_dumps(ctx_dict)

    # Deserialize
    parsed = json_loads(json_str)

    # Should be byte-identical on second serialization
    json_str2 = json_dumps(parsed)
    assert json_str == json_str2


def test_repository_context_invalid_total_commits():
    """Test that RepositoryContext rejects invalid total_commits."""
    with pytest.raises(ValueError):
        RepositoryContext(
            repo_id="repo_001",
            local_path=Path("/path/to/repo"),
            is_remote=False,
            total_commits=5,  # Less than minimum 10
            first_commit_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
            last_commit_date=datetime.datetime(2020, 12, 31, tzinfo=datetime.timezone.utc),
            contributor_count=5,
            is_shallow=False,
            is_fork=False
        )


def test_repository_context_invalid_contributor_count():
    """Test that RepositoryContext rejects invalid contributor_count."""
    with pytest.raises(ValueError):
        RepositoryContext(
            repo_id="repo_001",
            local_path=Path("/path/to/repo"),
            is_remote=False,
            total_commits=100,
            first_commit_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
            last_commit_date=datetime.datetime(2020, 12, 31, tzinfo=datetime.timezone.utc),
            contributor_count=0,  # Less than minimum 1
            is_shallow=False,
            is_fork=False
        )


def test_repository_context_optional_fields():
    """Test RepositoryContext with optional fields."""
    ctx = RepositoryContext(
        repo_id="repo_001",
        local_path=Path("/path/to/repo"),
        is_remote=False,
        total_commits=100,
        first_commit_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        last_commit_date=datetime.datetime(2020, 12, 31, tzinfo=datetime.timezone.utc),
        contributor_count=5,
        is_shallow=False,
        is_fork=False
        # language_distribution defaults to None
    )

    assert ctx.language_distribution is None