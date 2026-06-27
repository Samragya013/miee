import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "test_repo"
        repo_dir.mkdir()
        os.system(f"cd {repo_dir} && git init")
        # Create some commits
        for i in range(15):
            (repo_dir / f"file_{i}.py").write_text(f"# commit {i}\nx = {i}\n")
            os.system(f"cd {repo_dir} && git add . && git commit -m 'commit {i}' --allow-empty")
        yield repo_dir


@pytest.fixture
def sample_config():
    """Return a minimal valid Configuration."""
    from miie.schemas.models import Configuration

    return Configuration(repo="/tmp/test")


@pytest.fixture
def sample_repository_context():
    """Return a minimal valid RepositoryContext."""
    from miie.schemas.models import RepositoryContext

    return RepositoryContext(
        repo_id="a" * 64,
        local_path="/tmp/test",
        is_remote=False,
        total_commits=20,
        contributor_count=3,
        first_commit_date="2024-01-01",
        last_commit_date="2024-06-01",
        is_shallow=False,
        is_fork=False,
    )
