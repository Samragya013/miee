"""
Shared test configuration for contract layer tests.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from miie.schemas.models import MetricDataFrame, RepositoryContext, WindowDefinition


@pytest.fixture
def sample_repository_context():
    """Fixture providing a sample RepositoryContext for testing."""
    return RepositoryContext(
        repo_id="test-repo",
        local_path=Path("/path/to/repo"),
        is_remote=True,
        remote_url="https://github.com/test/repo.git",
        total_commits=1000,
        contributor_count=50,
        language_distribution={"Python": 670, "JavaScript": 330},
    )


@pytest.fixture
def sample_metric_dataframe():
    """Fixture providing a sample MetricDataFrame for testing."""
    timestamps = [datetime.now() - timedelta(days=i) for i in range(30)]
    metrics_dict = {
        "M-01": {"timestamps": timestamps, "values": [float(i) for i in range(30)]},
        "M-02": {"timestamps": timestamps, "values": [float(i * 2) for i in range(30)]},
        "M-03": {
            "timestamps": timestamps,
            "values": [float(i * 0.5) for i in range(30)],
        },
    }
    return MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )


@pytest.fixture
def sample_window_definitions():
    """Fixture providing sample WindowDefinition objects for testing."""
    now = datetime.now()
    return [
        WindowDefinition(
            id="w01",
            start_date=now - timedelta(days=30),
            end_date=now - timedelta(days=15),
        ),
        WindowDefinition(id="w02", start_date=now - timedelta(days=15), end_date=now),
    ]


@pytest.fixture
def sample_detector_results():
    """Fixture providing sample DetectorResults for testing."""
    from miie.schemas.models import DetectorResults

    # This would normally be populated with actual detector results
    return DetectorResults()


# Note: For a complete test suite, we would need to create proper fixtures
# for all the schema objects, but for basic contract testing, the above
# should suffice to verify the DTOs, validators, and errors work correctly.
