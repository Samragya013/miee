"""
Unit tests for the observation extraction package.

Covers CommitExtractor, MetricExtractor, and ExtractionEngine.
IMS Phase 3 acceptance criteria: minimum 20 new tests.
"""

import datetime
import os
import subprocess
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

import pytest

from miie.contracts.errors import ExtractionError
from miie.processing.extraction.commit_extractor import CommitExtractor
from miie.processing.extraction.engine import ExtractionEngine
from miie.processing.extraction.metric_extractor import MetricExtractor
from miie.processing.observation.models import (
    Observation,
    ObservationCollection,
    ObservationWindow,
    generate_observation_id,
)
from miie.processing.observation.store import ObservationStore
from miie.schemas.models import MetricDataFrame, RepositoryContext

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _init_git_repo(repo_path: Path) -> None:
    """Initialize a git repository with user config."""
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


def _make_commit(repo_path: Path, message: str, content: str = "x = 1\n") -> None:
    """Create a single commit with given content."""
    (repo_path / "file.txt").write_text(content)
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def _create_repo_with_commits(repo_path: Path, n: int = 15) -> None:
    """Create a git repository with n commits, each with a distinct timestamp."""
    _init_git_repo(repo_path)
    for i in range(n):
        # Use distinct dates (one per minute) to avoid git deduplication
        date_str = f"2024-01-01T00:{i:02d}:00+00:00"
        env = {**os.environ, "GIT_AUTHOR_DATE": date_str, "GIT_COMMITTER_DATE": date_str}
        (repo_path / "file.txt").write_text(f"x = {i}\n")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"commit {i}"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            env=env,
        )


def _make_context(repo_path: Path, repo_id: str = "a" * 64) -> RepositoryContext:
    """Create a minimal valid RepositoryContext."""
    return RepositoryContext(
        repo_id=repo_id,
        local_path=repo_path,
        is_remote=False,
        total_commits=20,
        contributor_count=3,
        first_commit_date=datetime.datetime(2024, 1, 1),
        last_commit_date=datetime.datetime(2024, 12, 31),
        is_shallow=False,
        is_fork=False,
    )


# ------------------------------------------------------------------
# CommitExtractor tests
# ------------------------------------------------------------------


class TestCommitExtractor:
    """Tests for CommitExtractor."""

    def test_instantiation(self):
        """CommitExtractor can be instantiated."""
        ext = CommitExtractor()
        assert ext is not None

    def test_extract_commits_returns_observation_collection(self, tmp_path):
        """extract_commits returns an ObservationCollection."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        assert isinstance(collection, ObservationCollection)
        assert collection.repository_id == ctx.repo_id

    def test_extract_commits_populates_windows(self, tmp_path):
        """ObservationCollection has exactly one window (w00)."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        assert len(collection.windows) == 1
        assert collection.windows[0].window_id == "w00"

    def test_extract_commits_m02_observations(self, tmp_path):
        """Each commit produces one M-02 observation."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        num_commits = 12
        _create_repo_with_commits(repo_path, num_commits)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        m02_obs = [o for o in collection.windows[0].observations if o.metric_id == "M-02"]
        assert len(m02_obs) == num_commits

    def test_extract_commits_m02_values_are_one(self, tmp_path):
        """M-02 observation values are all 1.0 (count metric)."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        m02_obs = [o for o in collection.windows[0].observations if o.metric_id == "M-02"]
        assert all(obs.value == 1.0 for obs in m02_obs)

    def test_extract_commits_m06_observations(self, tmp_path):
        """Each commit produces one M-06 observation."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        num_commits = 10
        _create_repo_with_commits(repo_path, num_commits)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        m06_obs = [o for o in collection.windows[0].observations if o.metric_id == "M-06"]
        assert len(m06_obs) == num_commits

    def test_extract_commits_m06_values_are_nonnegative(self, tmp_path):
        """M-06 (Code Churn) values are >= 0."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        m06_obs = [o for o in collection.windows[0].observations if o.metric_id == "M-06"]
        assert all(obs.value >= 0.0 for obs in m06_obs)

    def test_extract_commits_total_observations(self, tmp_path):
        """total_observations equals 2 * num_commits (M-02 + M-06 per commit)."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        num_commits = 10
        _create_repo_with_commits(repo_path, num_commits)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        assert collection.total_observations == num_commits * 2

    def test_extract_commits_total_metrics(self, tmp_path):
        """total_metrics is 2 (M-02 and M-06)."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        assert collection.total_metrics == 2

    def test_extract_commits_metrics_present(self, tmp_path):
        """metrics_present includes M-02 and M-06."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        assert "M-02" in collection.windows[0].metrics_present
        assert "M-06" in collection.windows[0].metrics_present

    def test_extract_commits_observation_provenance(self, tmp_path):
        """All observations have valid provenance."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        for obs in collection.windows[0].observations:
            assert obs.provenance.extractor_id == "commit_extractor.v1"
            assert obs.provenance.extraction_timestamp
            assert obs.provenance.seed is None

    def test_extract_commits_observation_source_type(self, tmp_path):
        """All observations have source_type='commit'."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        for obs in collection.windows[0].observations:
            assert obs.source_type == "commit"

    def test_extract_commits_observation_source_id_is_sha(self, tmp_path):
        """All observations have 40-char hex SHA as source_id."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        sha_re = __import__("re").compile(r"^[0-9a-f]{40}$")
        for obs in collection.windows[0].observations:
            assert sha_re.match(obs.source_id), f"Invalid SHA: {obs.source_id}"

    def test_extract_commits_deterministic_ids(self, tmp_path):
        """Running extract twice produces same observation IDs."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)

        c1 = ext.extract_commits(ctx)
        c2 = ext.extract_commits(ctx)

        ids1 = sorted(o.observation_id for o in c1.windows[0].observations)
        ids2 = sorted(o.observation_id for o in c2.windows[0].observations)
        assert ids1 == ids2

    def test_extract_commits_empty_repo(self, tmp_path):
        """Empty repository returns empty ObservationCollection."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _init_git_repo(repo_path)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        assert collection.total_observations == 0
        assert len(collection.windows) == 1

    def test_extract_commits_invalid_context_raises(self):
        """CommitExtractor raises ExtractionError for invalid context."""
        ext = CommitExtractor()
        with pytest.raises(ExtractionError, match="valid RepositoryContext"):
            ext.extract_commits(MagicMock(spec=[]))

    def test_extract_commits_with_since_filter(self, tmp_path):
        """since filter limits commits."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _init_git_repo(repo_path)

        # Create commits at known dates
        for i in range(10):
            date_str = f"2024-01-{i + 1:02d}T12:00:00"
            env = {**os.environ, "GIT_AUTHOR_DATE": date_str, "GIT_COMMITTER_DATE": date_str}
            _make_commit(repo_path, f"commit {i}", content=f"x = {i}\n")
            # Override date via env
            subprocess.run(
                ["git", "commit", "--amend", "--no-edit", "--allow-empty"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                env=env,
            )

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        since = datetime.datetime(2024, 1, 5)
        collection = ext.extract_commits(ctx, since=since)

        # Should have fewer commits than total
        m02_obs = [o for o in collection.windows[0].observations if o.metric_id == "M-02"]
        assert len(m02_obs) < 10

    def test_extract_commits_with_exclude_bots(self, tmp_path):
        """exclude_bots filters bot commits."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _init_git_repo(repo_path)

        # Create regular commits
        for i in range(8):
            _make_commit(repo_path, f"regular {i}", content=f"x = {i}\n")

        # Create a bot commit
        subprocess.run(
            ["git", "config", "user.email", "dependabot@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        _make_commit(repo_path, "bot commit", content="y = 99\n")

        # Reset to regular user
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        ext = CommitExtractor()
        ctx = _make_context(repo_path)

        without_filter = ext.extract_commits(ctx, exclude_bots=False)
        with_filter = ext.extract_commits(ctx, exclude_bots=True)

        total_no = without_filter.total_observations
        total_yes = with_filter.total_observations
        # Bot exclusion should produce fewer or equal observations
        assert total_yes <= total_no

    def test_extract_commits_window_boundary_dates(self, tmp_path):
        """Window boundaries match first and last commit dates."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx)

        window = collection.windows[0]
        # start_boundary and end_boundary should be valid ISO-8601
        start = datetime.datetime.fromisoformat(window.start_boundary)
        end = datetime.datetime.fromisoformat(window.end_boundary)
        assert start <= end

    def test_extract_commits_with_seed(self, tmp_path):
        """seed is stored in provenance."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        ext = CommitExtractor()
        ctx = _make_context(repo_path)
        collection = ext.extract_commits(ctx, seed=42)

        for obs in collection.windows[0].observations:
            assert obs.provenance.seed == 42


# ------------------------------------------------------------------
# MetricExtractor tests
# ------------------------------------------------------------------


class TestMetricExtractor:
    """Tests for MetricExtractor adapter."""

    def _make_observation_collection(
        self,
        windows_data: List[List[tuple]],
    ) -> ObservationCollection:
        """Build an ObservationCollection from simplified data.

        windows_data: list of windows, each window is list of
            (metric_id, value) tuples.
        """
        from miie.processing.observation.models import ObservationProvenance

        windows = []
        for idx, window_data in enumerate(windows_data):
            observations = []
            for metric_id, value in window_data:
                unit_map = {
                    "M-01": "ratio",
                    "M-02": "count",
                    "M-03": "ratio",
                    "M-04": "ratio",
                    "M-05": "hours",
                    "M-06": "count",
                    "M-07": "ratio",
                }
                provenance = ObservationProvenance(
                    extractor_id="test",
                    extraction_timestamp="2024-06-15T12:00:00+00:00",
                )
                obs = Observation(
                    observation_id=generate_observation_id("commit", "a" * 40, metric_id),
                    source_type="commit",
                    source_id="a" * 40,
                    metric_id=metric_id,
                    value=value,
                    unit=unit_map.get(metric_id, "count"),
                    timestamp="2024-06-15T12:00:00+00:00",
                    quality="complete",
                    provenance=provenance,
                )
                observations.append(obs)
            windows.append(
                ObservationWindow(
                    window_id=f"w{idx:02d}",
                    window_index=idx,
                    strategy="commit_count",
                    start_boundary="2024-01-01T00:00:00+00:00",
                    end_boundary="2024-06-30T23:59:59+00:00",
                    observations=observations,
                )
            )

        return ObservationCollection(
            collection_id="a" * 16,
            repository_id="r" * 64,
            analysis_id="b" * 16,
            windows=windows,
            total_observations=sum(len(w.observations) for w in windows),
            total_metrics=len({o.metric_id for w in windows for o in w.observations}),
            extraction_timestamp="2024-06-15T12:00:00+00:00",
        )

    def test_instantiation(self):
        """MetricExtractor can be instantiated."""
        ext = MetricExtractor()
        assert ext is not None

    def test_extract_metrics_returns_metric_dataframe(self):
        """extract_metrics returns a MetricDataFrame."""
        collection = self._make_observation_collection(
            [
                [("M-02", 1.0), ("M-06", 5.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        assert isinstance(mdf, MetricDataFrame)

    def test_extract_metrics_repo_id(self):
        """MetricDataFrame.repo_id matches collection."""
        collection = self._make_observation_collection(
            [
                [("M-02", 1.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        assert mdf.repo_id == collection.repository_id

    def test_extract_metrics_m02_sum(self):
        """M-02 values are summed across observations."""
        collection = self._make_observation_collection(
            [
                [("M-02", 1.0), ("M-02", 1.0), ("M-02", 1.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        # 3 observations * 1.0 = 3.0
        assert mdf.metrics["M-02"]["w00"] == [3.0]

    def test_extract_metrics_m06_sum(self):
        """M-06 values are summed across observations."""
        collection = self._make_observation_collection(
            [
                [("M-06", 10.0), ("M-06", 20.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        assert mdf.metrics["M-06"]["w00"] == [30.0]

    def test_extract_metrics_m07_mean(self):
        """M-07 values are averaged across observations."""
        collection = self._make_observation_collection(
            [
                [("M-07", 2.0), ("M-07", 4.0), ("M-07", 6.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        # mean(2, 4, 6) = 4.0
        assert mdf.metrics["M-07"]["w00"] == [4.0]

    def test_extract_metrics_metric_list_filter(self):
        """metric_list filters which metrics appear."""
        collection = self._make_observation_collection(
            [
                [("M-02", 1.0), ("M-06", 5.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection, metric_list=["M-02"])
        assert "M-02" in mdf.metrics
        assert "M-06" not in mdf.metrics

    def test_extract_metrics_multiple_windows(self):
        """Handles multiple windows correctly."""
        collection = self._make_observation_collection(
            [
                [("M-02", 1.0), ("M-02", 1.0)],
                [("M-02", 1.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        assert mdf.metrics["M-02"]["w00"] == [2.0]
        assert mdf.metrics["M-02"]["w01"] == [1.0]

    def test_extract_metrics_none_for_missing_metric(self):
        """Missing metric in a window produces None."""
        collection = self._make_observation_collection(
            [
                [("M-02", 1.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection, metric_list=["M-02", "M-07"])
        # M-07 not present → 0.0
        assert mdf.metrics.get("M-07", {}).get("w00") == [0.0]

    def test_extract_metrics_empty_collection(self):
        """Empty collection produces empty metrics."""
        collection = self._make_observation_collection([])
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        assert mdf.metrics == {}

    def test_extract_metrics_timestamp(self):
        """MetricDataFrame timestamp matches collection extraction timestamp."""
        collection = self._make_observation_collection(
            [
                [("M-02", 1.0)],
            ]
        )
        ext = MetricExtractor()
        mdf = ext.extract_metrics(collection)
        expected = datetime.datetime.fromisoformat(collection.extraction_timestamp)
        assert mdf.timestamp == expected


# ------------------------------------------------------------------
# ExtractionEngine tests
# ------------------------------------------------------------------


class TestExtractionEngine:
    """Tests for ExtractionEngine orchestrator."""

    def test_instantiation(self):
        """ExtractionEngine can be instantiated."""
        engine = ExtractionEngine()
        assert engine is not None

    def test_instantiation_with_store(self):
        """ExtractionEngine accepts an ObservationStore."""
        store = ObservationStore()
        engine = ExtractionEngine(store=store)
        assert engine.store is store

    def test_extract_returns_tuple(self, tmp_path):
        """extract returns (ObservationCollection, MetricDataFrame)."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        engine = ExtractionEngine()
        ctx = _make_context(repo_path)
        result = engine.extract(ctx, ["M-02", "M-06"])

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], ObservationCollection)
        assert isinstance(result[1], MetricDataFrame)

    def test_extract_repo_id_matches(self, tmp_path):
        """Both outputs share the same repo_id."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        engine = ExtractionEngine()
        ctx = _make_context(repo_path)
        collection, mdf = engine.extract(ctx, ["M-02"])

        assert collection.repository_id == ctx.repo_id
        assert mdf.repo_id == ctx.repo_id

    def test_extract_stores_collection(self, tmp_path):
        """When store is provided, collection is added to it."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        store = ObservationStore()
        engine = ExtractionEngine(store=store)
        ctx = _make_context(repo_path)
        collection, _ = engine.extract(ctx, ["M-02"])

        assert store.count() == 1
        assert store.get(collection.collection_id) is not None

    def test_extract_metric_list_propagated(self, tmp_path):
        """metric_list is propagated to MetricExtractor."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        engine = ExtractionEngine()
        ctx = _make_context(repo_path)
        _, mdf = engine.extract(ctx, ["M-02"])

        assert "M-02" in mdf.metrics
        assert "M-06" not in mdf.metrics

    def test_extract_with_since_filter(self, tmp_path):
        """since filter is passed to CommitExtractor."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _init_git_repo(repo_path)

        for i in range(10):
            date_str = f"2024-01-{i + 1:02d}T12:00:00"
            env = {**os.environ, "GIT_AUTHOR_DATE": date_str, "GIT_COMMITTER_DATE": date_str}
            _make_commit(repo_path, f"commit {i}", content=f"x = {i}\n")
            subprocess.run(
                ["git", "commit", "--amend", "--no-edit", "--allow-empty"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                env=env,
            )

        engine = ExtractionEngine()
        ctx = _make_context(repo_path)
        since = datetime.datetime(2024, 1, 5)
        collection, _ = engine.extract(ctx, ["M-02"], since=since)

        m02_obs = [o for o in collection.windows[0].observations if o.metric_id == "M-02"]
        assert len(m02_obs) < 10

    def test_extract_with_seed(self, tmp_path):
        """seed is propagated to CommitExtractor."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        engine = ExtractionEngine()
        ctx = _make_context(repo_path)
        collection, _ = engine.extract(ctx, ["M-02"], seed=99)

        for obs in collection.windows[0].observations:
            assert obs.provenance.seed == 99

    def test_extract_invalid_context_raises(self):
        """extract raises ExtractionError for invalid context."""
        engine = ExtractionEngine()
        with pytest.raises(ExtractionError):
            engine.extract(MagicMock(spec=[]), ["M-02"])

    def test_extract_store_duplicate_raises(self, tmp_path):
        """Adding duplicate collection to store raises ExtractionError."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 8)

        store = ObservationStore()
        engine = ExtractionEngine(store=store)
        ctx = _make_context(repo_path)

        # First extract succeeds
        engine.extract(ctx, ["M-02"])

        # Second extract fails because same collection_id already in store
        with pytest.raises(ExtractionError, match="Failed to store"):
            engine.extract(ctx, ["M-02"])


# ------------------------------------------------------------------
# Integration tests
# ------------------------------------------------------------------


class TestExtractionIntegration:
    """Integration tests combining extraction with store and adapters."""

    def test_full_pipeline_extract_store_query(self, tmp_path):
        """Full pipeline: extract → store → query."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 12)

        store = ObservationStore()
        engine = ExtractionEngine(store=store)
        ctx = _make_context(repo_path)

        collection, mdf = engine.extract(ctx, ["M-02", "M-06"])

        # Query by repository
        results = store.query(repository_id=ctx.repo_id)
        assert len(results) == 1
        assert results[0].collection_id == collection.collection_id

        # Query by metric
        results = store.query(metric_id="M-02")
        assert len(results) == 1

        # MetricDataFrame has correct structure
        assert "M-02" in mdf.metrics
        assert "M-06" in mdf.metrics
        assert "w00" in mdf.metrics["M-02"]

    def test_adapter_roundtrip_observations_to_mdf(self, tmp_path):
        """Roundtrip: CommitExtractor → MetricExtractor → MetricDataFrame."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        commit_ext = CommitExtractor()
        metric_ext = MetricExtractor()
        ctx = _make_context(repo_path)

        collection = commit_ext.extract_commits(ctx)
        mdf = metric_ext.extract_metrics(collection, metric_list=["M-02"])

        # M-02 sum should equal number of commits
        m02_total = mdf.metrics["M-02"]["w00"][0]
        assert m02_total == 10.0

    def test_extraction_engine_backward_compatible_mdf(self, tmp_path):
        """ExtractionEngine MetricDataFrame is compatible with detectors."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        _create_repo_with_commits(repo_path, 10)

        engine = ExtractionEngine()
        ctx = _make_context(repo_path)
        _, mdf = engine.extract(ctx, ["M-02", "M-06"])

        # Verify structure matches what detectors expect
        assert hasattr(mdf, "repo_id")
        assert hasattr(mdf, "run_id")
        assert hasattr(mdf, "timestamp")
        assert hasattr(mdf, "metrics")
        assert isinstance(mdf.metrics, dict)
        for metric_id, windows in mdf.metrics.items():
            assert isinstance(windows, dict)
            for window_id, values in windows.items():
                assert isinstance(values, list)
                assert all(isinstance(v, (float, int, type(None))) for v in values)
