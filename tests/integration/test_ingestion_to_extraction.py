"""
Integration Tests for MIIE v1.0 Pipeline: Ingestion to Extraction
Tests the connection between RepositoryIngestionEngine and MetricExtractionEngine.
"""

import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from miie.processing.extraction import MetricExtractionEngine
from miie.processing.ingestion import RepositoryIngestionEngine
from miie.schemas.models import MetricDataFrame, RepositoryContext


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


def create_repo_with_history(repo_path: Path, num_commits: int = 15, num_contributors: int = 2) -> None:
    """
    Create a git repository with specified number of commits and contributors.

    Args:
        repo_path: Path where the repository should be created
        num_commits: Number of commits to create (minimum 10 for validation)
        num_contributors: Number of different contributors to simulate
    """
    init_git_repo(repo_path)

    # Distribute commits among contributors
    base_commits_per_contributor = num_commits // num_contributors
    remainder = num_commits % num_contributors

    for contributor in range(num_contributors):
        # Set contributor identity
        subprocess.run(
            ["git", "config", "user.name", f"Contributor {contributor+1}"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", f"contributor{contributor+1}@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        # Calculate commits for this contributor
        commits_for_this_contributor = base_commits_per_contributor + (1 if contributor < remainder else 0)

        # Make commits for this contributor
        for i in range(commits_for_this_contributor):
            commit_msg = f"Commit {i+1} from contributor {contributor+1}"
            make_commit(repo_path, commit_msg)


class TestIngestionToExtractionIntegration:
    """Test the integration between ingestion and extraction engines."""

    @pytest.fixture
    def sample_repo(self, tmp_path):
        """Create a sample Git repository for testing with sufficient history."""
        repo_path = tmp_path / "sample-repo"
        repo_path.mkdir()

        # Create repository with history using helper function
        create_repo_with_history(repo_path, num_commits=15, num_contributors=2)

        return str(repo_path)

    def test_ingestion_extraction_pipeline_with_real_repo(self, sample_repo):
        """Test that ingestion followed by extraction works with a real Git repository."""
        # Step 1: Ingest the repository
        ingestion_engine = RepositoryIngestionEngine()
        context = ingestion_engine.ingest(sample_repo)

        # Verify we got a valid RepositoryContext
        assert isinstance(context, RepositoryContext)
        assert context.repo_id is not None and len(context.repo_id) == 64  # SHA256
        assert context.local_path == Path(sample_repo).resolve()
        assert context.total_commits == 15  # We created 15 commits
        assert context.contributor_count == 2  # We used 2 contributors

        # Step 2: Extract metrics from the context
        extraction_engine = MetricExtractionEngine()
        metric_list = ["M-02", "M-06"]  # Commit Frequency and Code Churn
        result = extraction_engine.extract(context, metric_list)

        # Verify we got a valid MetricDataFrame
        assert isinstance(result, MetricDataFrame)
        assert result.repo_id == context.repo_id
        assert result.run_id is not None
        assert result.timestamp is not None

        # Verify that M-02 and M-06 were extracted
        assert "M-02" in result.metrics
        assert "M-06" in result.metrics

        # Verify the values are not None (we have data)
        assert result.metrics["M-02"] is not None
        assert result.metrics["M-06"] is not None

        # Verify the structure: dict with window IDs mapping to lists of values
        assert isinstance(result.metrics["M-02"], dict)
        assert isinstance(result.metrics["M-06"], dict)

        # For foundation implementation, we expect a single window w00
        assert "w00" in result.metrics["M-02"]
        assert "w00" in result.metrics["M-06"]

        # Verify commit frequency equals our commit count
        assert len(result.metrics["M-02"]["w00"]) == 1
        assert result.metrics["M-02"]["w00"][0] == 15.0

        # Verify code churn is non-negative (we added content in each commit)
        assert len(result.metrics["M-06"]["w00"]) == 1
        assert result.metrics["M-06"]["w00"][0] > 0.0

    def test_ingestion_extraction_with_time_filters(self, sample_repo):
        """Test ingestion and extraction with since/until time parameters."""
        # Ingest the repository
        ingestion_engine = RepositoryIngestionEngine()
        context = ingestion_engine.ingest(sample_repo)

        # Define time range (last 2 days)
        until = datetime.now(timezone.utc)
        since = until - timedelta(days=2)

        # Extract metrics with time range
        extraction_engine = MetricExtractionEngine()
        metric_list = ["M-02", "M-06"]
        result = extraction_engine.extract(context, metric_list, since=since, until=until)

        # Verify result
        assert isinstance(result, MetricDataFrame)
        assert result.metrics["M-02"] is not None
        assert result.metrics["M-06"] is not None

        # Values should be <= total commits since we're filtering by time
        assert result.metrics["M-02"]["w00"][0] <= 15.0
        assert result.metrics["M-06"]["w00"][0] >= 0.0

    def test_ingestion_extraction_with_bot_exclusion(self, sample_repo):
        """Test ingestion and extraction with exclude_bots parameter."""
        # Ingest the repository
        ingestion_engine = RepositoryIngestionEngine()
        context = ingestion_engine.ingest(sample_repo)

        # Extract with bot exclusion
        extraction_engine = MetricExtractionEngine()
        metric_list = ["M-02", "M-06"]
        result = extraction_engine.extract(context, metric_list, exclude_bots=True)

        # Verify result
        assert isinstance(result, MetricDataFrame)
        assert result.metrics["M-02"] is not None
        assert result.metrics["M-06"] is not None

    def test_ingestion_extraction_with_unavailable_metrics(self, sample_repo):
        """Test that unavailable metrics are handled correctly per missing data policy."""
        # Ingest the repository
        ingestion_engine = RepositoryIngestionEngine()
        context = ingestion_engine.ingest(sample_repo)

        # Extract a mix of metrics — M-05 requires external PR data (always unavailable locally)
        # M-01 through M-04, M-06-M-07 are available via git provider
        extraction_engine = MetricExtractionEngine()
        metric_list = ["M-01", "M-02", "M-03", "M-05", "M-06"]
        result = extraction_engine.extract(context, metric_list)

        # Verify result
        assert isinstance(result, MetricDataFrame)

        # M-05 is now a provider metric — returns zeros without GitHub API
        assert result.metrics["M-05"] is not None
        assert result.metrics["M-05"]["w00"] == [0.0]

    def test_ingestion_extraction_with_unavailable_context(self):
        """Test that extraction handles unavailable repositories gracefully per missing data policy."""
        # Create extraction engine
        extraction_engine = MetricExtractionEngine()

        # Create a RepositoryContext pointing to a non-existent repository
        from datetime import datetime, timezone

        from miie.schemas.models import RepositoryContext

        context = RepositoryContext(
            repo_id="test",
            local_path=Path("/tmp/nonexistent"),
            is_remote=False,
            total_commits=10,
            first_commit_date=datetime.now(timezone.utc),
            last_commit_date=datetime.now(timezone.utc),
            contributor_count=1,
            is_shallow=False,
            is_fork=False,
        )

        # Extract metrics - should succeed but return None for unavailable repo per missing data policy
        result = extraction_engine.extract(context, ["M-02"])

        # Verify result is a valid MetricDataFrame
        assert isinstance(result, MetricDataFrame)
        assert result.repo_id == "test"

        # Verify that M-02 is present but None (unavailable metric)
        assert "M-02" in result.metrics
        assert result.metrics["M-02"] is None

    def test_ingestion_extraction_deterministic_behavior(self, sample_repo):
        """Test that the same inputs produce the same outputs (deterministic behavior)."""
        # Ingest the repository twice
        ingestion_engine = RepositoryIngestionEngine()
        context1 = ingestion_engine.ingest(sample_repo)
        context2 = ingestion_engine.ingest(sample_repo)

        # Contexts should be identical (same repo_id, same metrics)
        assert context1.repo_id == context2.repo_id
        assert context1.total_commits == context2.total_commits
        assert context1.contributor_count == context2.contributor_count

        # Extract metrics twice with same parameters
        extraction_engine = MetricExtractionEngine()
        metric_list = ["M-02", "M-06"]

        result1 = extraction_engine.extract(context1, metric_list)
        result2 = extraction_engine.extract(context2, metric_list)

        # Results should be identical
        assert result1.repo_id == result2.repo_id
        assert result1.metrics["M-02"] == result2.metrics["M-02"]
        assert result1.metrics["M-06"] == result2.metrics["M-06"]

        # Run IDs will be different (UUIDs), but that's expected
        assert result1.run_id != result2.run_id

        # Timestamps will be very close but not identical, but values should be same
        assert result1.metrics["M-02"]["w00"][0] == result2.metrics["M-02"]["w00"][0]
        assert result1.metrics["M-06"]["w00"][0] == result2.metrics["M-06"]["w00"][0]

    def test_ingestion_extraction_empty_repo_edge_case(self, tmp_path):
        """Test handling of edge case with minimal valid repository."""
        # Create a minimal valid git repo (10 commits minimum for validation)
        repo_path = tmp_path / "minimal_repo"
        repo_path.mkdir()
        create_repo_with_history(repo_path, num_commits=10, num_contributors=1)

        # Ingest the repository
        ingestion_engine = RepositoryIngestionEngine()
        context = ingestion_engine.ingest(str(repo_path))

        # Extract metrics
        extraction_engine = MetricExtractionEngine()
        metric_list = ["M-02", "M-06"]
        result = extraction_engine.extract(context, metric_list)

        # Verify result
        assert isinstance(result, MetricDataFrame)
        assert result.metrics["M-02"] is not None
        assert result.metrics["M-06"] is not None

        # Should have exactly 10 commits
        assert result.metrics["M-02"]["w00"][0] == 10.0
        assert result.metrics["M-06"]["w00"][0] >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
