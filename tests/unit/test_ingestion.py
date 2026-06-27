"""
Tests for the ingestion module.
"""

import pytest

from miie.contracts.errors import IngestionError
from miie.processing.ingestion import RepositoryIngestionEngine, validate_repository


def test_validate_repository_valid_git_repo(tmp_path):
    """Test that a valid Git repository passes validation."""
    # Create a temporary directory and initialize a git repo
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()  # Create .git directory to simulate a git repo

    # Should not raise an exception
    validate_repository(repo_path)


def test_validate_repository_missing_path(tmp_path):
    """Test that a missing path raises IngestionError."""
    missing_path = tmp_path / "non_existent"
    with pytest.raises(IngestionError, match="Repository path does not exist"):
        validate_repository(missing_path)


def test_validate_repository_not_a_directory(tmp_path):
    """Test that a file (not a directory) raises IngestionError."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a repo")
    with pytest.raises(IngestionError, match="Repository path is not a directory"):
        validate_repository(file_path)


def test_validate_repository_no_git_directory(tmp_path):
    """Test that a directory without .git raises IngestionError."""
    dir_path = tmp_path / "empty_dir"
    dir_path.mkdir()
    with pytest.raises(IngestionError, match="Repository path does not contain a .git directory"):
        validate_repository(dir_path)


def test_validate_repository_path_traversal(tmp_path):
    """Test that path traversal is handled safely via resolution."""
    # Create a git repo inside tmp_path
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()

    # Create a subdirectory
    subdir = tmp_path / "sub"
    subdir.mkdir()

    # Test a relative path that goes up and then down to the repo (should resolve to the repo)
    traversal_path = subdir / ".." / "repo"
    # This should pass because it resolves to a valid git repo
    validate_repository(traversal_path)  # Should not raise

    # Test a traversal that attempts to escape but resolves to a non-existent path
    bad_traversal = subdir / ".." / "nonexistent"
    with pytest.raises(IngestionError, match="Repository path does not exist"):
        validate_repository(bad_traversal)

    # Test a traversal that attempts to escape but resolves to a non-git directory
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    bad_traversal2 = subdir / ".." / "empty"
    with pytest.raises(IngestionError, match="Repository path does not contain a .git directory"):
        validate_repository(bad_traversal2)


def test_RepositoryIngestionEngine_validate_with_valid_context(tmp_path):
    """Test that RepositoryIngestionEngine.validate returns True for a valid context."""
    # Create a git repo
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()

    # We need to create a RepositoryContext. We can use the RepositoryIngestionEngine to create one via ingest?
    # But the validate method just calls validate_repository on the local_path.
    # So we can create a RepositoryContext with the local_path set to our repo.
    import datetime

    from miie.schemas.models import RepositoryContext

    context = RepositoryContext(
        repo_id="test",
        local_path=repo_path.resolve(),
        is_remote=False,
        total_commits=10,  # Minimum required by schema
        first_commit_date=datetime.datetime.now(datetime.timezone.utc),
        last_commit_date=datetime.datetime.now(datetime.timezone.utc),
        contributor_count=1,
        is_shallow=False,
        is_fork=False,
    )

    engine = RepositoryIngestionEngine()
    assert engine.validate(context) is True


def test_RepositoryIngestionEngine_validate_with_invalid_context(tmp_path):
    """Test that RepositoryIngestionEngine.validate returns False for an invalid context."""
    # Create a RepositoryContext with a non-existent path
    import datetime

    from miie.schemas.models import RepositoryContext

    context = RepositoryContext(
        repo_id="test",
        local_path=tmp_path / "non_existent",
        is_remote=False,
        total_commits=10,  # Must be at least 10 to pass schema validation
        first_commit_date=datetime.datetime.now(datetime.timezone.utc),
        last_commit_date=datetime.datetime.now(datetime.timezone.utc),
        contributor_count=1,
        is_shallow=False,
        is_fork=False,
    )

    engine = RepositoryIngestionEngine()
    # The validate method should return False because the local_path does not exist
    assert engine.validate(context) is False
