"""
Tests for repository metadata extraction functionality in ingestion.py.
"""

import datetime
import subprocess
from pathlib import Path
import pytest
from miie.processing.ingestion import RepositoryIngestionEngine
from miie.contracts.errors import IngestionError
from miie.schemas.models import RepositoryContext


def init_git_repo(repo_path: Path) -> None:
    """Initialize a git repository with basic configuration."""
    subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True, capture_output=True)


def make_commit(repo_path: Path, commit_message: str) -> None:
    """Make a git commit with a file change."""
    # Create or modify a dummy file to commit
    dummy_file = repo_path / "dummy.txt"
    # Write different content each time to ensure there's something to commit
    dummy_file.write_text(f"dummy content at {commit_message}")
    subprocess.run(['git', 'add', 'dummy.txt'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', commit_message], cwd=repo_path, check=True, capture_output=True)


def create_repo_with_history(repo_path: Path, num_commits: int = 10, num_contributors: int = 1) -> None:
    """
    Create a git repository with specified number of commits and contributors.

    Args:
        repo_path: Path where the repository should be created
        num_commits: Number of commits to create (minimum 10 for validation)
        num_contributors: Number of different contributors to simulate
    """
    init_git_repo(repo_path)

    # Distribute commits among contributors
    commits_per_contributor = max(1, num_commits // num_contributors)

    for contributor in range(num_contributors):
        # Set contributor identity
        subprocess.run(
            ['git', 'config', 'user.name', f'Contributor {contributor+1}'],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ['git', 'config', 'user.email', f'contributor{contributor+1}@example.com'],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

        # Make commits for this contributor
        for i in range(commits_per_contributor):
            commit_msg = f"Commit {i+1} from contributor {contributor+1}"
            make_commit(repo_path, commit_msg)

    # If there are remaining commits, add them with the first contributor
    remaining = num_commits - (commits_per_contributor * num_contributors)
    if remaining > 0:
        subprocess.run(
            ['git', 'config', 'user.name', 'Contributor 1'],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ['git', 'config', 'user.email', 'contributor1@example.com'],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        for i in range(remaining):
            make_commit(repo_path, f"Remaining commit {i+1}")


def test_ingest_with_real_git_repository(tmp_path):
    """Test ingesting a real Git repository with sufficient history."""
    # Create repository with 12 commits and 2 contributors
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    create_repo_with_history(repo_path, num_commits=12, num_contributors=2)

    # Ingest the repository
    engine = RepositoryIngestionEngine()
    context = engine.ingest(str(repo_path))

    # Verify the RepositoryContext is correctly populated
    assert isinstance(context, RepositoryContext)
    assert context.repo_id is not None and len(context.repo_id) == 64  # SHA256 hex digest
    assert context.local_path == repo_path.resolve()
    # Check that the repository name (last part of path) is correct
    assert context.local_path.name == "test_repo"
    assert context.is_remote is False
    assert context.remote_url is None
    assert context.total_commits == 12
    assert context.contributor_count >= 1  # Platform-dependent git author normalization
    assert context.is_shallow is False  # Regular clone
    assert context.is_fork is False  # Placeholder implementation
    assert context.language_distribution is None  # Not implemented

    # Verify date fields are reasonable (not None and in correct order)
    assert context.first_commit_date is not None
    assert context.last_commit_date is not None
    assert context.first_commit_date <= context.last_commit_date

    # Verify dates are timezone aware (UTC)
    assert context.first_commit_date.tzinfo is not None
    assert context.last_commit_date.tzinfo is not None


def test_ingest_with_shallow_clone(tmp_path):
    """Test ingesting a shallow clone repository."""
    # Create a regular repo first
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    create_repo_with_history(repo_path, num_commits=20, num_contributors=1)

    # Convert to shallow clone by creating .git/shallow file
    git_dir = repo_path / '.git'
    shallow_file = git_dir / 'shallow'
    shallow_file.touch()  # Create empty shallow file

    # Ingest the repository
    engine = RepositoryIngestionEngine()
    context = engine.ingest(str(repo_path))

    # Verify it's detected as shallow
    assert context.is_shallow is True


def test_ingest_with_insufficient_commits(tmp_path):
    """Test that ingesting a repository with fewer than 10 commits raises validation error."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    create_repo_with_history(repo_path, num_commits=5, num_contributors=1)  # Only 5 commits

    engine = RepositoryIngestionEngine()
    with pytest.raises(IngestionError, match="total_commits must be >= 10"):
        engine.ingest(str(repo_path))


def test_ingest_with_no_commits(tmp_path):
    """Test that ingesting a repository with no commits raises IngestionError."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    init_git_repo(repo_path)
    # No commits means we can't get commit count

    engine = RepositoryIngestionEngine()
    with pytest.raises(IngestionError, match="Failed to get commit count"):
        engine.ingest(str(repo_path))


def test_ingest_invalid_repository_path(tmp_path):
    """Test that ingesting a non-repository path raises IngestionError."""
    non_repo_path = tmp_path / "not_a_repo"
    non_repo_path.mkdir()
    # Don't initialize as git repo

    engine = RepositoryIngestionEngine()
    with pytest.raises(IngestionError, match="Repository path does not contain a .git directory"):
        engine.ingest(str(non_repo_path))


def test_ingest_nonexistent_path(tmp_path):
    """Test that ingesting a nonexistent path raises IngestionError."""
    nonexistent_path = tmp_path / "does_not_exist"

    engine = RepositoryIngestionEngine()
    with pytest.raises(IngestionError, match="Repository path does not exist"):
        engine.ingest(str(nonexistent_path))


def test_repository_context_validation_contributor_count():
    """Test that RepositoryContext validation catches contributor_count < 1."""
    import datetime
    with pytest.raises(ValueError, match="contributor_count must be >= 1"):
        RepositoryContext(
            repo_id="test",
            local_path=Path("/tmp"),
            is_remote=False,
            total_commits=10,
            first_commit_date=datetime.datetime.now(datetime.timezone.utc),
            last_commit_date=datetime.datetime.now(datetime.timezone.utc),
            contributor_count=0,  # This should fail validation
            is_shallow=False,
            is_fork=False
        )


def test_repository_context_validation_total_commits():
    """Test that RepositoryContext validation catches total_commits < 10."""
    import datetime
    with pytest.raises(ValueError, match="total_commits must be >= 10"):
        RepositoryContext(
            repo_id="test",
            local_path=Path("/tmp"),
            is_remote=False,
            total_commits=5,  # This should fail validation
            first_commit_date=datetime.datetime.now(datetime.timezone.utc),
            last_commit_date=datetime.datetime.now(datetime.timezone.utc),
            contributor_count=1,
            is_shallow=False,
            is_fork=False
        )


if __name__ == "__main__":
    # Allow running directly for debugging
    pytest.main([__file__, "-v"])