"""
Unit tests for the MetricExtractionEngine implementation.
"""

import datetime
import subprocess
from pathlib import Path

import pytest

from miie.contracts.errors import ExtractionError
from miie.processing.extraction import MetricExtractionEngine
from miie.schemas.models import MetricDataFrame


def init_git_repo(repo_path: Path) -> None:
    """Initialize a git repository with basic configuration."""
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def make_commit(repo_path: Path, commit_message: str) -> None:
    """Make a git commit with a file change."""
    # Create or modify a dummy file to commit
    dummy_file = repo_path / "dummy.txt"
    # Write different content each time to ensure there's something to commit
    dummy_file.write_text(f"dummy content at {commit_message}")
    subprocess.run(["git", "add", "dummy.txt"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def create_repo_with_history(repo_path: Path, num_commits: int = 15) -> None:
    """
    Create a git repository with specified number of commits.

    Args:
        repo_path: Path where the repository should be created
        num_commits: Number of commits to create
    """
    init_git_repo(repo_path)

    for i in range(num_commits):
        make_commit(repo_path, f"Commit {i+1}")


def test_metric_extraction_engine_initialization():
    """Test that MetricExtractionEngine can be instantiated."""
    engine = MetricExtractionEngine()
    assert isinstance(engine, MetricExtractionEngine)


def test_extract_with_valid_repo_and_metrics(tmp_path):
    """Test extraction with valid repository and M-02/M-06 metrics."""
    # Create a test repository with sufficient history
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    create_repo_with_history(repo_path, num_commits=15)

    # First, ingest the repository to get RepositoryContext
    from miie.processing.ingestion import RepositoryIngestionEngine

    ingestion_engine = RepositoryIngestionEngine()
    context = ingestion_engine.ingest(str(repo_path))

    # Create extraction engine
    engine = MetricExtractionEngine()

    # Extract M-02 and M-06 metrics
    metric_list = ["M-02", "M-06"]
    result = engine.extract(context, metric_list)

    # Verify result is a MetricDataFrame
    assert isinstance(result, MetricDataFrame)
    assert result.repo_id == context.repo_id
    assert result.run_id is not None
    assert result.timestamp is not None

    # Verify that M-02 and M-06 are present in metrics
    assert "M-02" in result.metrics
    assert "M-06" in result.metrics

    # Verify that the values are not None (since we have commits)
    assert result.metrics["M-02"] is not None
    assert result.metrics["M-06"] is not None

    # Verify the structure: dict with window IDs mapping to lists of values
    assert isinstance(result.metrics["M-02"], dict)
    assert isinstance(result.metrics["M-06"], dict)

    # For foundation implementation, we expect a single window w00
    assert "w00" in result.metrics["M-02"]
    assert "w00" in result.metrics["M-06"]

    # Verify the values are positive numbers
    assert len(result.metrics["M-02"]["w00"]) == 1
    assert len(result.metrics["M-06"]["w00"]) == 1
    assert result.metrics["M-02"]["w00"][0] == 15.0  # 15 commits
    assert result.metrics["M-06"]["w00"][0] >= 0.0  # Churn should be non-negative


def test_extract_with_unavailable_metrics(tmp_path):
    """Test that unavailable metrics return None per missing data policy."""
    # Create a test repository
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    create_repo_with_history(repo_path, num_commits=10)

    # Ingest the repository
    from miie.processing.ingestion import RepositoryIngestionEngine

    ingestion_engine = RepositoryIngestionEngine()
    context = ingestion_engine.ingest(str(repo_path))

    # Create extraction engine
    engine = MetricExtractionEngine()

    # Extract mix of available and unavailable metrics
    metric_list = ["M-02", "M-01", "M-06"]  # M-01 is unavailable (coverage)
    result = engine.extract(context, metric_list)

    # Verify result
    assert isinstance(result, MetricDataFrame)

    # M-02 and M-06 should have values (not None)
    assert result.metrics["M-02"] is not None
    assert result.metrics["M-06"] is not None

    # M-01 should be None (unavailable)
    assert result.metrics["M-01"] is None


def test_extract_with_invalid_metric_ids():
    """Test that invalid metric IDs raise ExtractionError."""
    engine = MetricExtractionEngine()

    # Create a minimal valid RepositoryContext for testing
    import datetime

    from miie.schemas.models import RepositoryContext

    context = RepositoryContext(
        repo_id="test",
        local_path=Path("/tmp"),
        is_remote=False,
        total_commits=10,
        first_commit_date=datetime.datetime.now(datetime.timezone.utc),
        last_commit_date=datetime.datetime.now(datetime.timezone.utc),
        contributor_count=1,
        is_shallow=False,
        is_fork=False,
    )

    # Test invalid metric ID
    with pytest.raises(ExtractionError, match="Invalid metric IDs: \['M-08'\]"):
        engine.extract(context, ["M-08"])

    # Test mix of valid and invalid
    with pytest.raises(ExtractionError) as exc_info:
        engine.extract(context, ["M-02", "M-08", "M-06"])

    error_msg = str(exc_info.value)
    assert "Invalid metric IDs:" in error_msg
    assert "M-08" in error_msg
    # The error message includes the full frozen registry, so valid metrics will appear there
    # We should only check that the invalid metrics are mentioned


def test_extract_with_since_until_parameters(tmp_path):
    """Test extraction with since/until time parameters."""
    # Create a test repository
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    create_repo_with_history(repo_path, num_commits=20)

    # Ingest the repository
    from miie.processing.ingestion import RepositoryIngestionEngine

    ingestion_engine = RepositoryIngestionEngine()
    context = ingestion_engine.ingest(str(repo_path))

    # Create extraction engine
    engine = MetricExtractionEngine()

    # Define time range (last 7 days)
    until = datetime.datetime.now(datetime.timezone.utc)
    since = until - datetime.timedelta(days=7)

    # Extract metrics with time range
    metric_list = ["M-02", "M-06"]
    result = engine.extract(context, metric_list, since=since, until=until)

    # Verify result
    assert isinstance(result, MetricDataFrame)
    assert result.metrics["M-02"] is not None
    assert result.metrics["M-06"] is not None

    # Values should be <= total commits (20) since we're filtering by time
    assert result.metrics["M-02"]["w00"][0] <= 20.0
    assert result.metrics["M-06"]["w00"][0] >= 0.0


def test_extract_with_exclude_bots_parameter(tmp_path):
    """Test extraction with exclude_bots parameter."""
    # Create a test repository
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    create_repo_with_history(repo_path, num_commits=10)

    # Ingest the repository
    from miie.processing.ingestion import RepositoryIngestionEngine

    ingestion_engine = RepositoryIngestionEngine()
    context = ingestion_engine.ingest(str(repo_path))

    # Create extraction engine
    engine = MetricExtractionEngine()

    # Extract with bot exclusion
    metric_list = ["M-02", "M-06"]
    result = engine.extract(context, metric_list, exclude_bots=True)

    # Verify result
    assert isinstance(result, MetricDataFrame)
    assert result.metrics["M-02"] is not None
    assert result.metrics["M-06"] is not None


def test_extract_empty_metric_list():
    """Test extraction with empty metric list."""
    engine = MetricExtractionEngine()

    # Create a minimal valid RepositoryContext for testing
    import datetime

    from miie.schemas.models import RepositoryContext

    context = RepositoryContext(
        repo_id="test",
        local_path=Path("/tmp"),
        is_remote=False,
        total_commits=10,
        first_commit_date=datetime.datetime.now(datetime.timezone.utc),
        last_commit_date=datetime.datetime.now(datetime.timezone.utc),
        contributor_count=1,
        is_shallow=False,
        is_fork=False,
    )

    # Extract with empty list
    result = engine.extract(context, [])

    # Verify result is valid but empty
    assert isinstance(result, MetricDataFrame)
    assert result.metrics == {}


def test_extract_none_repo_context():
    """Test extraction with None repository context."""
    engine = MetricExtractionEngine()

    with pytest.raises(AttributeError):
        engine.extract(None, ["M-02"])


def test_extract_none_metric_list():
    """Test extraction with None metric list."""
    engine = MetricExtractionEngine()

    # Create a minimal valid RepositoryContext for testing
    import datetime

    from miie.schemas.models import RepositoryContext

    context = RepositoryContext(
        repo_id="test",
        local_path=Path("/tmp"),
        is_remote=False,
        total_commits=10,
        first_commit_date=datetime.datetime.now(datetime.timezone.utc),
        last_commit_date=datetime.datetime.now(datetime.timezone.utc),
        contributor_count=1,
        is_shallow=False,
        is_fork=False,
    )

    with pytest.raises(TypeError):
        engine.extract(context, None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
