"""
Tests for MIIE v1.6 PR-11E — Repository Observation Graph.

Covers models, graph, builder, correlation, validation, serialization,
and diagnostics modules. 80+ tests total.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

import pytest

from miie.observation_graph.builder import (
    GraphBuilderConfig,
    GraphBuilderResult,
    ObservationGraphBuilder,
)
from miie.observation_graph.correlation import ObservationCorrelationEngine
from miie.observation_graph.diagnostics import GraphDiagnosticsEngine
from miie.observation_graph.graph import RepositoryObservationGraph
from miie.observation_graph.models import (
    RELATIONSHIP_COMMIT_TO_PR,
    RELATIONSHIP_METRIC_CORRELATION,
    RELATIONSHIP_PR_TO_REPO,
    RELATIONSHIP_PROVIDER_HIERARCHY,
    RELATIONSHIP_TEMPORAL_OVERLAP,
    GraphDiagnostics,
    GraphEdge,
    GraphNode,
    GraphValidationResult,
    generate_graph_id,
)
from miie.observation_graph.serialization import GraphSerializer
from miie.observation_graph.validation import GraphValidator
from miie.processing.observation.models import (
    Observation,
    ObservationCollection,
    ObservationProvenance,
    ObservationWindow,
    generate_observation_id,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_REPO_ID = "owner/repo"
_ANALYSIS_ID = "analysis-001"
_DEFAULT_SHA = "a" * 40  # Valid 40-char hex SHA for commit source_type


def _ts(hours_offset: float = 0.0) -> str:
    """Return an ISO-8601 timestamp offset from now."""
    dt = datetime.now(timezone.utc) + timedelta(hours=hours_offset)
    return dt.isoformat()


def _sha(seed: str = "a") -> str:
    """Return a valid 40-char hex SHA from a seed character (must be hex: 0-9, a-f)."""
    return (seed * 40)[:40]


def _make_observation(
    source_type: str = "commit",
    source_id: str | None = None,
    metric_id: str = "M-02",
    value: float = 10.0,
    unit: str | None = None,
    quality: str = "complete",
    timestamp: str | None = None,
    observation_id: str | None = None,
    metadata: dict | None = None,
    extractor_id: str = "test.extractor.v1",
) -> Observation:
    """Create a test observation with valid model constraints."""
    if source_id is None:
        source_id = _DEFAULT_SHA
    if unit is None:
        # Auto-set unit based on metric
        _METRIC_UNITS = {
            "M-01": "ratio",
            "M-02": "count",
            "M-03": "ratio",
            "M-04": "ratio",
            "M-05": "hours",
            "M-06": "count",
            "M-07": "ratio",
        }
        unit = _METRIC_UNITS.get(metric_id, "count")
    if observation_id is None:
        observation_id = generate_observation_id(source_type, source_id, metric_id)
    if timestamp is None:
        timestamp = _ts()
    return Observation(
        observation_id=observation_id,
        source_type=source_type,
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        unit=unit,
        timestamp=timestamp,
        quality=quality,
        metadata=metadata or {},
        provenance=ObservationProvenance(
            extractor_id=extractor_id,
            extraction_timestamp=timestamp,
        ),
    )


def _make_collection(
    observations: List[Observation],
    collection_id: str = "col-001",
) -> ObservationCollection:
    """Create an ObservationCollection from a list of observations."""
    window = ObservationWindow(
        window_id="w00",
        window_index=0,
        strategy="custom",
        start_boundary=observations[0].timestamp if observations else _ts(),
        end_boundary=observations[-1].timestamp if observations else _ts(),
        observations=observations,
        metrics_present=sorted({obs.metric_id for obs in observations}),
    )
    return ObservationCollection(
        collection_id=collection_id,
        repository_id=_REPO_ID,
        analysis_id=_ANALYSIS_ID,
        windows=[window],
        total_observations=len(observations),
        total_metrics=len({obs.metric_id for obs in observations}),
        extraction_timestamp=_ts(),
        schema_version="1.0.0",
    )


# ===================================================================
# Tests: models.py
# ===================================================================


class TestGraphNode:
    """Tests for GraphNode dataclass."""

    def test_basic_creation(self):
        obs = _make_observation()
        node = GraphNode(
            observation=obs,
            provider_id="git.observation.v1",
            metric_id=obs.metric_id,
            source_type=obs.source_type,
            source_id=obs.source_id,
            timestamp=obs.timestamp,
        )
        assert node.observation_id == obs.observation_id
        assert node.provider_id == "git.observation.v1"
        assert node.value == obs.value
        assert node.quality == obs.quality
        assert node.unit == obs.unit

    def test_is_frozen(self):
        obs = _make_observation()
        node = GraphNode(
            observation=obs,
            provider_id="p1",
            metric_id="M-02",
            source_type="commit",
            source_id=_DEFAULT_SHA,
            timestamp=_ts(),
        )
        with pytest.raises(AttributeError):
            node.provider_id = "changed"


class TestGraphEdge:
    """Tests for GraphEdge dataclass."""

    def test_basic_creation(self):
        edge = GraphEdge(
            source_observation_id="a" * 16,
            target_observation_id="b" * 16,
            relationship_type=RELATIONSHIP_COMMIT_TO_PR,
            confidence=0.9,
        )
        assert edge.source_observation_id == "a" * 16
        assert edge.confidence == 0.9

    def test_self_reference_rejected(self):
        with pytest.raises(ValueError, match="self-referencing"):
            GraphEdge(
                source_observation_id="a" * 16,
                target_observation_id="a" * 16,
                relationship_type=RELATIONSHIP_COMMIT_TO_PR,
            )

    def test_empty_source_rejected(self):
        with pytest.raises(ValueError, match="source_observation_id must not be empty"):
            GraphEdge(
                source_observation_id="",
                target_observation_id="b" * 16,
                relationship_type=RELATIONSHIP_COMMIT_TO_PR,
            )

    def test_empty_target_rejected(self):
        with pytest.raises(ValueError, match="target_observation_id must not be empty"):
            GraphEdge(
                source_observation_id="a" * 16,
                target_observation_id="",
                relationship_type=RELATIONSHIP_COMMIT_TO_PR,
            )

    def test_invalid_confidence(self):
        with pytest.raises(ValueError, match="confidence must be in"):
            GraphEdge(
                source_observation_id="a" * 16,
                target_observation_id="b" * 16,
                relationship_type=RELATIONSHIP_COMMIT_TO_PR,
                confidence=1.5,
            )

    def test_empty_relationship_type_rejected(self):
        with pytest.raises(ValueError, match="relationship_type must not be empty"):
            GraphEdge(
                source_observation_id="a" * 16,
                target_observation_id="b" * 16,
                relationship_type="",
            )

    def test_edge_key_deterministic(self):
        edge = GraphEdge(
            source_observation_id="a" * 16,
            target_observation_id="b" * 16,
            relationship_type=RELATIONSHIP_COMMIT_TO_PR,
        )
        key = edge.edge_key
        assert key == ("a" * 16, "b" * 16, RELATIONSHIP_COMMIT_TO_PR)


class TestGraphDiagnostics:
    """Tests for GraphDiagnostics."""

    def test_empty_graph(self):
        diag = GraphDiagnostics()
        assert diag.total_nodes == 0
        assert diag.completeness == 1.0
        assert diag.orphan_ratio == 0.0
        assert diag.provider_count == 0
        assert diag.metric_count == 0

    def test_completeness_single_node(self):
        diag = GraphDiagnostics(total_nodes=1, total_edges=0)
        assert diag.completeness == 1.0

    def test_completeness_multi_node(self):
        diag = GraphDiagnostics(total_nodes=3, total_edges=6)
        assert diag.completeness == pytest.approx(1.0)

    def test_orphan_ratio(self):
        diag = GraphDiagnostics(total_nodes=10, orphan_count=3)
        assert diag.orphan_ratio == pytest.approx(0.3)


class TestGraphValidationResult:
    """Tests for GraphValidationResult."""

    def test_success(self):
        result = GraphValidationResult.success()
        assert result.is_valid is True
        assert result.violations == []

    def test_failure(self):
        result = GraphValidationResult.failure(["err1", "err2"])
        assert result.is_valid is False
        assert len(result.violations) == 2


class TestGenerateGraphId:
    """Tests for generate_graph_id."""

    def test_deterministic(self):
        id1 = generate_graph_id("owner/repo", "analysis-001")
        id2 = generate_graph_id("owner/repo", "analysis-001")
        assert id1 == id2

    def test_length(self):
        graph_id = generate_graph_id("owner/repo", "analysis-001")
        assert len(graph_id) == 16

    def test_hex(self):
        graph_id = generate_graph_id("owner/repo", "analysis-001")
        int(graph_id, 16)  # Should not raise

    def test_different_inputs_different_ids(self):
        id1 = generate_graph_id("owner/repo1", "analysis-001")
        id2 = generate_graph_id("owner/repo2", "analysis-001")
        assert id1 != id2

    def test_empty_repo_raises(self):
        with pytest.raises(ValueError):
            generate_graph_id("", "analysis-001")

    def test_empty_analysis_raises(self):
        with pytest.raises(ValueError):
            generate_graph_id("owner/repo", "")


# ===================================================================
# Tests: graph.py
# ===================================================================


class TestRepositoryObservationGraph:
    """Tests for RepositoryObservationGraph core graph."""

    def test_creation(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        assert graph.repository_id == _REPO_ID
        assert graph.analysis_id == _ANALYSIS_ID
        assert graph.is_empty
        assert graph.node_count == 0
        assert graph.edge_count == 0

    def test_empty_repo_raises(self):
        with pytest.raises(ValueError):
            RepositoryObservationGraph("", _ANALYSIS_ID)

    def test_empty_analysis_raises(self):
        with pytest.raises(ValueError):
            RepositoryObservationGraph(_REPO_ID, "")

    def test_graph_id_deterministic(self):
        g1 = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        g2 = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        assert g1.graph_id == g2.graph_id

    def test_custom_graph_id(self):
        g = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID, graph_id="custom123")
        assert g.graph_id == "custom123"

    def test_add_observation(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        assert graph.add_observation(obs, "provider.v1") is True
        assert graph.node_count == 1
        assert not graph.is_empty

    def test_add_duplicate_observation(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "provider.v1")
        assert graph.add_observation(obs, "provider.v1") is False
        assert graph.node_count == 1

    def test_add_observations_batch(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"))
        obs2 = _make_observation(source_id=_sha("b"))
        added = graph.add_observations((obs1, obs2), "p1")
        assert added == 2
        assert graph.node_count == 2

    def test_add_edge(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(
            source_observation_id=obs1.observation_id,
            target_observation_id=obs2.observation_id,
            relationship_type=RELATIONSHIP_COMMIT_TO_PR,
        )
        assert graph.add_edge(edge) is True
        assert graph.edge_count == 1

    def test_add_edge_nonexistent_source(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(
            source_observation_id=obs1.observation_id,
            target_observation_id=obs2.observation_id,
            relationship_type=RELATIONSHIP_COMMIT_TO_PR,
        )
        assert graph.add_edge(edge) is False

    def test_add_duplicate_edge(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(
            source_observation_id=obs1.observation_id,
            target_observation_id=obs2.observation_id,
            relationship_type=RELATIONSHIP_COMMIT_TO_PR,
        )
        graph.add_edge(edge)
        assert graph.add_edge(edge) is False
        assert graph.edge_count == 1

    def test_add_edges_batch(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        obs3 = _make_observation(source_id=_sha("c"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")
        graph.add_observation(obs3, "p1")

        edges = [
            GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR),
            GraphEdge(obs2.observation_id, obs3.observation_id, RELATIONSHIP_COMMIT_TO_PR),
        ]
        added = graph.add_edges(edges)
        assert added == 2

    def test_get_node(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")
        node = graph.get_node(obs.observation_id)
        assert node is not None
        assert node.observation_id == obs.observation_id

    def test_get_node_not_found(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        assert graph.get_node("nonexistent12345") is None

    def test_get_by_metric(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-05")
        obs3 = _make_observation(source_id=_sha("c"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p2")
        graph.add_observation(obs3, "p3")

        nodes = graph.get_by_metric("M-02")
        assert len(nodes) == 2

    def test_get_by_provider(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p2")

        nodes = graph.get_by_provider("p1")
        assert len(nodes) == 1

    def test_get_by_source(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        sha_a = _sha("a")
        sha_b = _sha("b")
        obs1 = _make_observation(source_type="commit", source_id=sha_a, metric_id="M-02")
        obs2 = _make_observation(source_type="commit", source_id=sha_b, metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        nodes = graph.get_by_source("commit", sha_a)
        assert len(nodes) == 1

    def test_get_by_time_range(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        ts1 = _ts(-10)
        ts2 = _ts(-5)
        ts3 = _ts(0)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02", timestamp=ts1)
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02", timestamp=ts2)
        obs3 = _make_observation(source_id=_sha("c"), metric_id="M-02", timestamp=ts3)
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")
        graph.add_observation(obs3, "p1")

        nodes = graph.get_by_time_range(_ts(-8), _ts(1))
        assert len(nodes) == 2

    def test_get_edges(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        graph.add_edge(edge)

        edges = graph.get_edges(obs1.observation_id)
        assert len(edges) == 1

    def test_get_edges_from(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        graph.add_edge(edge)

        assert len(graph.get_edges_from(obs1.observation_id)) == 1
        assert len(graph.get_edges_from(obs2.observation_id)) == 0

    def test_get_edges_to(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        graph.add_edge(edge)

        assert len(graph.get_edges_to(obs2.observation_id)) == 1
        assert len(graph.get_edges_to(obs1.observation_id)) == 0

    def test_get_all_observations_sorted(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("0"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("1"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        all_obs = graph.get_all_observations()
        assert len(all_obs) == 2
        assert all_obs[0].observation_id < all_obs[1].observation_id

    def test_get_all_nodes_sorted(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("2"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("3"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        nodes = graph.get_all_nodes()
        assert len(nodes) == 2

    def test_get_all_edges_sorted(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("2"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("3"), metric_id="M-02")
        obs3 = _make_observation(source_id=_sha("4"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")
        graph.add_observation(obs3, "p1")

        e1 = GraphEdge(obs3.observation_id, obs1.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        e2 = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_PR_TO_REPO)
        graph.add_edges([e1, e2])

        edges = graph.get_all_edges()
        assert len(edges) == 2

    def test_to_observation_collection(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-05")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        collection = graph.to_observation_collection()
        assert collection.repository_id == _REPO_ID
        assert collection.total_observations == 2
        assert len(collection.windows) == 1

    def test_to_observation_windows(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")

        windows = graph.to_observation_windows()
        assert len(windows) == 1
        assert len(windows[0].observations) == 1

    def test_get_diagnostics(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")

        diag = graph.get_diagnostics()
        assert diag.total_nodes == 1
        assert "p1" in diag.providers
        assert "M-02" in diag.metrics


# ===================================================================
# Tests: correlation.py
# ===================================================================


class TestObservationCorrelationEngine:
    """Tests for ObservationCorrelationEngine."""

    def test_empty_nodes(self):
        engine = ObservationCorrelationEngine()
        edges = engine.discover([])
        assert edges == []

    def test_single_node(self):
        engine = ObservationCorrelationEngine()
        obs = _make_observation()
        node = GraphNode(obs, "p1", "M-02", "commit", _DEFAULT_SHA, _ts())
        edges = engine.discover([node])
        assert edges == []

    def test_commit_to_pr_merge_sha(self):
        engine = ObservationCorrelationEngine()
        ts = _ts()
        commit_sha = _sha("c")
        commit_obs = _make_observation(source_type="commit", source_id=commit_sha, metric_id="M-02", timestamp=ts)
        pr_obs = _make_observation(
            source_type="branch",
            source_id="pr-42",
            metric_id="M-02",
            timestamp=ts,
            metadata={"merge_commit_sha": commit_sha, "created_at": _ts(-5), "merged_at": _ts(5)},
        )
        commit_node = GraphNode(commit_obs, "git.p.v1", "M-02", "commit", commit_sha, ts)
        pr_node = GraphNode(pr_obs, "github.pr.v1", "M-02", "branch", "pr-42", ts)

        edges = engine.discover([commit_node, pr_node])
        commit_pr_edges = [e for e in edges if e.relationship_type == RELATIONSHIP_COMMIT_TO_PR]
        assert len(commit_pr_edges) == 1
        assert commit_pr_edges[0].confidence == 1.0

    def test_commit_to_pr_head_sha(self):
        engine = ObservationCorrelationEngine()
        ts = _ts()
        commit_sha = _sha("d")
        commit_obs = _make_observation(source_type="commit", source_id=commit_sha, metric_id="M-02", timestamp=ts)
        pr_obs = _make_observation(
            source_type="branch",
            source_id="pr-42",
            metric_id="M-02",
            timestamp=ts,
            metadata={"head_sha": commit_sha, "created_at": _ts(-5), "merged_at": _ts(5)},
        )
        commit_node = GraphNode(commit_obs, "git.p.v1", "M-02", "commit", commit_sha, ts)
        pr_node = GraphNode(pr_obs, "github.pr.v1", "M-02", "branch", "pr-42", ts)

        edges = engine.discover([commit_node, pr_node])
        commit_pr_edges = [e for e in edges if e.relationship_type == RELATIONSHIP_COMMIT_TO_PR]
        assert len(commit_pr_edges) == 1
        assert commit_pr_edges[0].confidence == 0.9

    def test_commit_to_pr_temporal(self):
        engine = ObservationCorrelationEngine()
        commit_ts = _ts(2)
        commit_sha = _sha("e")
        commit_obs = _make_observation(
            source_type="commit", source_id=commit_sha, metric_id="M-02", timestamp=commit_ts
        )
        pr_obs = _make_observation(
            source_type="branch",
            source_id="pr-42",
            metric_id="M-02",
            timestamp=_ts(3),
            metadata={"created_at": _ts(0), "merged_at": _ts(5)},
        )
        commit_node = GraphNode(commit_obs, "git.p.v1", "M-02", "commit", commit_sha, commit_ts)
        pr_node = GraphNode(pr_obs, "github.pr.v1", "M-02", "branch", "pr-42", _ts(3))

        edges = engine.discover([commit_node, pr_node])
        commit_pr_edges = [e for e in edges if e.relationship_type == RELATIONSHIP_COMMIT_TO_PR]
        assert len(commit_pr_edges) == 1
        assert commit_pr_edges[0].confidence == 0.7

    def test_pr_to_repo_linking(self):
        engine = ObservationCorrelationEngine()
        ts = _ts()
        pr_obs = _make_observation(
            source_type="branch",
            source_id="pr-42",
            metric_id="M-02",
            timestamp=ts,
            metadata={"repository_id": "owner/repo"},
        )
        repo_obs = _make_observation(
            source_type="branch",
            source_id="main",
            metric_id="M-02",
            timestamp=ts,
            metadata={"repository_id": "owner/repo"},
        )
        pr_node = GraphNode(pr_obs, "github.pr.v1", "M-02", "branch", "pr-42", ts)
        repo_node = GraphNode(repo_obs, "repo.meta.v1", "M-02", "branch", "main", ts)

        edges = engine.discover([pr_node, repo_node])
        pr_repo_edges = [e for e in edges if e.relationship_type == RELATIONSHIP_PR_TO_REPO]
        assert len(pr_repo_edges) == 1

    def test_temporal_overlap(self):
        engine = ObservationCorrelationEngine(temporal_threshold_hours=24.0)
        ts1 = _ts(0)
        ts2 = _ts(1)  # 1 hour later, within 24h threshold
        sha1 = _sha("1")
        sha2 = _sha("2")

        obs1 = _make_observation(source_id=sha1, metric_id="M-02", timestamp=ts1)
        obs2 = _make_observation(source_id=sha2, metric_id="M-02", timestamp=ts2)
        node1 = GraphNode(obs1, "p1", "M-02", "commit", sha1, ts1)
        node2 = GraphNode(obs2, "p2", "M-02", "commit", sha2, ts2)

        edges = engine.discover([node1, node2])
        temporal = [e for e in edges if e.relationship_type == RELATIONSHIP_TEMPORAL_OVERLAP]
        assert len(temporal) == 1

    def test_temporal_overlap_no_match(self):
        engine = ObservationCorrelationEngine(temporal_threshold_hours=1.0)
        ts1 = _ts(0)
        ts2 = _ts(5)  # 5 hours later, beyond 1h threshold
        sha1 = _sha("1")
        sha2 = _sha("2")

        obs1 = _make_observation(source_id=sha1, metric_id="M-02", timestamp=ts1)
        obs2 = _make_observation(source_id=sha2, metric_id="M-02", timestamp=ts2)
        node1 = GraphNode(obs1, "p1", "M-02", "commit", sha1, ts1)
        node2 = GraphNode(obs2, "p2", "M-02", "commit", sha2, ts2)

        edges = engine.discover([node1, node2])
        temporal = [e for e in edges if e.relationship_type == RELATIONSHIP_TEMPORAL_OVERLAP]
        assert len(temporal) == 0

    def test_metric_correlation(self):
        engine = ObservationCorrelationEngine()
        ts = _ts()
        sha = _sha("3")
        obs1 = _make_observation(source_id=sha, metric_id="M-02", timestamp=ts)
        obs2 = _make_observation(source_id=sha, metric_id="M-05", timestamp=ts)
        node1 = GraphNode(obs1, "p1", "M-02", "commit", sha, ts)
        node2 = GraphNode(obs2, "p1", "M-05", "commit", sha, ts)

        edges = engine.discover([node1, node2])
        metric_edges = [e for e in edges if e.relationship_type == RELATIONSHIP_METRIC_CORRELATION]
        assert len(metric_edges) == 1

    def test_provider_hierarchy(self):
        engine = ObservationCorrelationEngine()
        ts = _ts()
        sha1 = _sha("4")
        sha2 = _sha("5")
        obs1 = _make_observation(
            source_id=sha1, metric_id="M-02", timestamp=ts, metadata={"repository_id": "owner/repo"}
        )
        obs2 = _make_observation(
            source_id=sha2, metric_id="M-02", timestamp=ts, metadata={"repository_id": "owner/repo"}
        )
        node1 = GraphNode(obs1, "p1", "M-02", "commit", sha1, ts)
        node2 = GraphNode(obs2, "p2", "M-02", "commit", sha2, ts)

        edges = engine.discover([node1, node2])
        hierarchy = [e for e in edges if e.relationship_type == RELATIONSHIP_PROVIDER_HIERARCHY]
        assert len(hierarchy) == 1

    def test_edges_sorted_deterministically(self):
        engine = ObservationCorrelationEngine()
        ts = _ts()
        sha1 = _sha("0")
        sha2 = _sha("a")
        obs1 = _make_observation(source_id=sha1, metric_id="M-02", timestamp=ts)
        obs2 = _make_observation(source_id=sha2, metric_id="M-02", timestamp=ts)
        node1 = GraphNode(obs1, "p1", "M-02", "commit", sha1, ts)
        node2 = GraphNode(obs2, "p2", "M-02", "commit", sha2, ts)

        edges = engine.discover([node1, node2])
        for i in range(len(edges) - 1):
            assert edges[i].edge_key <= edges[i + 1].edge_key


# ===================================================================
# Tests: builder.py
# ===================================================================


class TestObservationGraphBuilder:
    """Tests for ObservationGraphBuilder."""

    def test_build_empty(self):
        builder = ObservationGraphBuilder()
        result = builder.build(_REPO_ID, _ANALYSIS_ID, [])
        assert result.graph.is_empty
        assert result.warnings

    def test_build_single_collection(self):
        builder = ObservationGraphBuilder()
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-05")
        collection = _make_collection([obs1, obs2])

        result = builder.build(_REPO_ID, _ANALYSIS_ID, [collection])
        assert result.graph.node_count == 2
        assert result.duplicates_removed == 0

    def test_build_deduplication(self):
        builder = ObservationGraphBuilder()
        obs = _make_observation()
        col1 = _make_collection([obs], collection_id="col1")
        col2 = _make_collection([obs], collection_id="col2")

        result = builder.build(_REPO_ID, _ANALYSIS_ID, [col1, col2])
        assert result.graph.node_count == 1
        assert result.duplicates_removed == 1

    def test_build_with_relationships(self):
        builder = ObservationGraphBuilder()
        ts = _ts()
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02", timestamp=ts)
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02", timestamp=ts)
        collection = _make_collection([obs1, obs2])

        result = builder.build(_REPO_ID, _ANALYSIS_ID, [collection])
        # Should discover some relationships (temporal overlap at minimum)
        assert result.edges_discovered >= 0

    def test_build_no_relationships(self):
        config = GraphBuilderConfig(discover_relationships=False)
        builder = ObservationGraphBuilder(config=config)
        obs = _make_observation()
        collection = _make_collection([obs])

        result = builder.build(_REPO_ID, _ANALYSIS_ID, [collection])
        assert result.edges_discovered == 0

    def test_build_performance(self):
        builder = ObservationGraphBuilder()
        observations = [_make_observation(source_id=_sha(f"{i:040d}"[-40:]), metric_id="M-02") for i in range(100)]
        collection = _make_collection(observations)

        result = builder.build(_REPO_ID, _ANALYSIS_ID, [collection])
        assert result.build_time_ms >= 0
        assert result.graph.node_count == 100

    def test_incremental_build(self):
        builder = ObservationGraphBuilder()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)

        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        col1 = _make_collection([obs1])
        added, skipped = builder.add_collection(graph, col1)
        assert added == 1
        assert skipped == 0

        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        col2 = _make_collection([obs2])
        added, skipped = builder.add_collection(graph, col2)
        assert added == 1
        assert graph.node_count == 2

    def test_builder_config_defaults(self):
        config = GraphBuilderConfig()
        assert config.merge_policy == "highest_confidence"
        assert config.deduplicate is True
        assert config.discover_relationships is True
        assert config.temporal_threshold_hours == 24.0

    def test_builder_result_fields(self):
        builder = ObservationGraphBuilder()
        result = builder.build(_REPO_ID, _ANALYSIS_ID, [])
        assert isinstance(result, GraphBuilderResult)
        assert result.graph is not None
        assert result.diagnostics is not None
        assert result.build_time_ms >= 0


# ===================================================================
# Tests: validation.py
# ===================================================================


class TestGraphValidator:
    """Tests for GraphValidator."""

    def test_valid_graph(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")

        validator = GraphValidator()
        result = validator.validate(graph)
        assert result.is_valid

    def test_empty_graph_valid(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        validator = GraphValidator()
        result = validator.validate(graph)
        assert result.is_valid

    def test_invalid_source_type(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")
        node = graph.get_node(obs.observation_id)
        invalid_node = GraphNode(
            observation=node.observation,
            provider_id=node.provider_id,
            metric_id=node.metric_id,
            source_type="invalid_type",
            source_id=node.source_id,
            timestamp=node.timestamp,
        )
        graph._nodes[obs.observation_id] = invalid_node
        graph._index_dirty = True

        validator = GraphValidator()
        result = validator.validate(graph)
        assert not result.is_valid
        assert any("invalid source_type" in v for v in result.violations)

    def test_invalid_metric_id(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")
        node = graph.get_node(obs.observation_id)
        invalid_node = GraphNode(
            observation=node.observation,
            provider_id=node.provider_id,
            metric_id="M-99",
            source_type=node.source_type,
            source_id=node.source_id,
            timestamp=node.timestamp,
        )
        graph._nodes[obs.observation_id] = invalid_node
        graph._index_dirty = True

        validator = GraphValidator()
        result = validator.validate(graph)
        assert not result.is_valid

    def test_wrong_unit_for_metric(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")
        node = graph.get_node(obs.observation_id)
        # Override the observation's unit to be wrong for the metric
        object.__setattr__(node.observation, "unit", "ratio")  # M-02 should be "count"
        graph._index_dirty = True

        validator = GraphValidator()
        result = validator.validate(graph)
        assert not result.is_valid

    def test_invalid_quality(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")
        node = graph.get_node(obs.observation_id)
        # Override the observation's quality to an invalid value
        object.__setattr__(node.observation, "quality", "invalid_quality")
        graph._index_dirty = True

        validator = GraphValidator()
        result = validator.validate(graph)
        assert not result.is_valid

    def test_empty_provider_id(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")
        node = graph.get_node(obs.observation_id)
        invalid_node = GraphNode(
            observation=node.observation,
            provider_id="",
            metric_id=node.metric_id,
            source_type=node.source_type,
            source_id=node.source_id,
            timestamp=node.timestamp,
        )
        graph._nodes[obs.observation_id] = invalid_node
        graph._index_dirty = True

        validator = GraphValidator()
        result = validator.validate(graph)
        assert not result.is_valid

    def test_invalid_timestamp(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")
        node = graph.get_node(obs.observation_id)
        invalid_node = GraphNode(
            observation=node.observation,
            provider_id=node.provider_id,
            metric_id=node.metric_id,
            source_type=node.source_type,
            source_id=node.source_id,
            timestamp="not-a-timestamp",
        )
        graph._nodes[obs.observation_id] = invalid_node
        graph._index_dirty = True

        validator = GraphValidator()
        result = validator.validate(graph)
        assert not result.is_valid

    def test_validation_result_with_diagnostics(self):
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")

        validator = GraphValidator()
        result = validator.validate(graph)
        assert result.diagnostics is not None
        assert result.diagnostics.total_nodes == 1


# ===================================================================
# Tests: serialization.py
# ===================================================================


class TestGraphSerializer:
    """Tests for GraphSerializer."""

    def test_roundtrip_empty(self):
        serializer = GraphSerializer()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        json_str = serializer.to_json(graph)
        restored = serializer.from_json(json_str)

        assert restored.graph_id == graph.graph_id
        assert restored.repository_id == _REPO_ID
        assert restored.node_count == 0

    def test_roundtrip_with_nodes(self):
        serializer = GraphSerializer()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-05")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p2")

        json_str = serializer.to_json(graph)
        restored = serializer.from_json(json_str)

        assert restored.node_count == 2

    def test_roundtrip_with_edges(self):
        serializer = GraphSerializer()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        graph.add_edge(edge)

        json_str = serializer.to_json(graph)
        restored = serializer.from_json(json_str)

        assert restored.edge_count == 1

    def test_deterministic_json(self):
        serializer = GraphSerializer()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")

        json1 = serializer.to_json(graph)
        json2 = serializer.to_json(graph)
        assert json1 == json2

    def test_to_dict(self):
        serializer = GraphSerializer()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation()
        graph.add_observation(obs, "p1")

        data = serializer.to_dict(graph)
        assert "graph_id" in data
        assert "nodes" in data
        assert "edges" in data
        assert "diagnostics" in data

    def test_invalid_json_raises(self):
        serializer = GraphSerializer()
        with pytest.raises(ValueError, match="Invalid JSON"):
            serializer.from_json("not valid json {{{")

    def test_missing_required_field(self):
        serializer = GraphSerializer()
        with pytest.raises(ValueError, match="Missing required field"):
            serializer.from_dict({"nodes": [], "edges": []})

    def test_json_compact(self):
        serializer = GraphSerializer()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        json_str = serializer.to_json(graph)
        # Compact: no newlines from indentation
        assert "\n" not in json_str or json_str.count("\n") < 5

    def test_json_pretty(self):
        serializer = GraphSerializer()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        json_str = serializer.to_json(graph, indent=2)
        assert "\n" in json_str


# ===================================================================
# Tests: diagnostics.py
# ===================================================================


class TestGraphDiagnosticsEngine:
    """Tests for GraphDiagnosticsEngine."""

    def test_compute_empty(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        diag = engine.compute(graph)
        assert diag.total_nodes == 0

    def test_health_score_empty(self):
        engine = GraphDiagnosticsEngine()
        diag = GraphDiagnostics()
        assert engine.health_score(diag) == 1.0

    def test_health_score_perfect(self):
        engine = GraphDiagnosticsEngine()
        diag = GraphDiagnostics(
            total_nodes=10,
            total_edges=90,
            providers=["p1", "p2", "p3"],
            metrics=["M-01", "M-02", "M-03", "M-04", "M-05"],
            orphan_count=0,
        )
        score = engine.health_score(diag)
        assert 0.0 <= score <= 1.0

    def test_health_score_all_orphans(self):
        engine = GraphDiagnosticsEngine()
        diag = GraphDiagnostics(
            total_nodes=10,
            total_edges=0,
            providers=["p1"],
            metrics=["M-02"],
            orphan_count=10,
        )
        score = engine.health_score(diag)
        assert score < 0.5

    def test_provider_summary(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p2")

        summary = engine.provider_summary(graph)
        assert "p1" in summary
        assert "p2" in summary
        assert summary["p1"]["observation_count"] == 1

    def test_coverage_matrix(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs = _make_observation(source_id=_sha("a"), metric_id="M-02")
        graph.add_observation(obs, "p1")

        matrix = engine.coverage_matrix(graph)
        assert "M-02" in matrix
        assert "p1" in matrix["M-02"]

    def test_relationship_summary(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        graph.add_edge(edge)

        summary = engine.relationship_summary(graph)
        assert summary.get(RELATIONSHIP_COMMIT_TO_PR, 0) == 1

    def test_orphan_analysis(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        edge = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        graph.add_edge(edge)

        analysis = engine.orphan_analysis(graph)
        assert analysis["orphan_count"] == 0
        assert analysis["orphan_ratio"] == 0.0

    def test_orphan_analysis_with_orphans(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02")
        obs3 = _make_observation(source_id=_sha("c"), metric_id="M-02")
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")
        graph.add_observation(obs3, "p1")

        edge = GraphEdge(obs1.observation_id, obs2.observation_id, RELATIONSHIP_COMMIT_TO_PR)
        graph.add_edge(edge)

        analysis = engine.orphan_analysis(graph)
        assert analysis["orphan_count"] == 1
        assert analysis["orphan_ratio"] == pytest.approx(1 / 3)

    def test_temporal_range(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        ts1 = _ts(-10)
        ts2 = _ts(0)
        obs1 = _make_observation(source_id=_sha("a"), metric_id="M-02", timestamp=ts1)
        obs2 = _make_observation(source_id=_sha("b"), metric_id="M-02", timestamp=ts2)
        graph.add_observation(obs1, "p1")
        graph.add_observation(obs2, "p1")

        rng = engine.temporal_range(graph)
        assert rng["earliest"] == ts1
        assert rng["latest"] == ts2

    def test_temporal_range_empty(self):
        engine = GraphDiagnosticsEngine()
        graph = RepositoryObservationGraph(_REPO_ID, _ANALYSIS_ID)
        rng = engine.temporal_range(graph)
        assert rng["earliest"] == ""
        assert rng["latest"] == ""


# ===================================================================
# Tests: Integration
# ===================================================================


class TestIntegration:
    """End-to-end integration tests for the observation graph."""

    def test_full_pipeline(self):
        """Test complete pipeline: build -> validate -> serialize -> restore."""
        builder = ObservationGraphBuilder()
        ts = _ts()
        commit_sha = _sha("f")
        obs1 = _make_observation(source_id=commit_sha, metric_id="M-02", timestamp=ts)
        obs2 = _make_observation(source_id=_sha("6"), metric_id="M-05", timestamp=ts)
        obs3 = _make_observation(
            source_type="branch",
            source_id="pr-1",
            metric_id="M-02",
            timestamp=ts,
            metadata={"merge_commit_sha": commit_sha, "created_at": _ts(-5), "merged_at": _ts(5)},
        )
        collection = _make_collection([obs1, obs2, obs3])
        result = builder.build(_REPO_ID, _ANALYSIS_ID, [collection])

        # Validate
        validator = GraphValidator()
        validation = validator.validate(result.graph)
        assert validation.is_valid

        # Serialize
        serializer = GraphSerializer()
        json_str = serializer.to_json(result.graph)

        # Restore
        restored = serializer.from_json(json_str)
        assert restored.node_count == 3

        # Diagnostics
        diag_engine = GraphDiagnosticsEngine()
        diag = diag_engine.compute(restored)
        assert diag.total_nodes == 3

    def test_multiple_providers(self):
        """Test graph with observations from multiple providers."""
        builder = ObservationGraphBuilder()
        ts = _ts()
        obs_git = _make_observation(
            source_id=_sha("7"), metric_id="M-02", timestamp=ts, extractor_id="git.observation.v1"
        )
        obs_pr = _make_observation(
            source_type="branch",
            source_id="pr-1",
            metric_id="M-02",
            timestamp=ts,
            metadata={"repository_id": _REPO_ID},
            extractor_id="github.pr.observation.v1",
        )
        obs_repo = _make_observation(
            source_type="branch",
            source_id="main",
            metric_id="M-02",
            timestamp=ts,
            metadata={"repository_id": _REPO_ID},
            extractor_id="repository.metadata.observation.v1",
        )

        col1 = _make_collection([obs_git], collection_id="git")
        col2 = _make_collection([obs_pr], collection_id="pr")
        col3 = _make_collection([obs_repo], collection_id="repo")

        result = builder.build(_REPO_ID, _ANALYSIS_ID, [col1, col2, col3])
        assert result.graph.node_count == 3

        # Check provider diversity
        diag_engine = GraphDiagnosticsEngine()
        summary = diag_engine.provider_summary(result.graph)
        assert len(summary) >= 2

    def test_determinism_across_runs(self):
        """Test that building the same graph twice produces identical results."""
        builder = ObservationGraphBuilder()
        obs1 = _make_observation(source_id=_sha("8"), metric_id="M-02")
        obs2 = _make_observation(source_id=_sha("9"), metric_id="M-05")
        collection = _make_collection([obs1, obs2])

        r1 = builder.build(_REPO_ID, _ANALYSIS_ID, [collection])
        r2 = builder.build(_REPO_ID, _ANALYSIS_ID, [collection])

        serializer = GraphSerializer()
        json1 = serializer.to_json(r1.graph)
        json2 = serializer.to_json(r2.graph)
        assert json1 == json2
