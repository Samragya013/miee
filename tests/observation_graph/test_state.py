"""
SR-04: Tests for Unified Graph State Model

Tests for GraphSnapshot, GraphEvent, GraphVersion, WorkingGraph,
and GraphStateManager classes.
"""

import pytest
from datetime import datetime, timezone

from miie.observation_graph.models import GraphEdge, GraphNode
from miie.observation_graph.state import (
    GraphEvent,
    GraphSnapshot,
    GraphStateManager,
    GraphVersion,
    StateType,
    WorkingGraph,
)


@pytest.fixture
def sample_nodes():
    """Create sample graph nodes for testing."""
    from miie.processing.observation.models import (
        Observation,
        ObservationProvenance,
        ObservationQuality,
    )

    nodes = []
    for i in range(5):
        provenance = ObservationProvenance(
            extractor_id="git.observation.v1",
            extraction_timestamp=f"2026-01-01T00:00:{i:02d}Z",
        )
        obs = Observation(
            observation_id=f"{i:016x}",
            metric_id="M-01",
            source_type="commit",
            source_id=f"{'a' * 38}{i:02x}",
            value=float(i),
            unit="ratio",
            timestamp=f"2026-01-01T00:00:{i:02d}Z",
            quality=ObservationQuality.COMPLETE.value,
            provenance=provenance,
        )
        node = GraphNode(
            observation=obs,
            provider_id="git.observation.v1",
            metric_id="M-01",
            source_type="commit",
            source_id=f"{'a' * 38}{i:02x}",
            timestamp=f"2026-01-01T00:00:{i:02d}Z",
        )
        nodes.append(node)
    return nodes


@pytest.fixture
def sample_edges(sample_nodes):
    """Create sample graph edges for testing."""
    edges = []
    for i in range(len(sample_nodes) - 1):
        edge = GraphEdge(
            source_observation_id=sample_nodes[i].observation_id,
            target_observation_id=sample_nodes[i + 1].observation_id,
            relationship_type="temporal_precedes",
            confidence=0.9,
        )
        edges.append(edge)
    return edges


@pytest.fixture
def sample_node_dict(sample_nodes):
    """Create sample node dict keyed by observation_id."""
    return {n.observation_id: n for n in sample_nodes}


@pytest.fixture
def sample_edge_dict(sample_edges):
    """Create sample edge dict keyed by edge_key tuple."""
    return {e.edge_key: e for e in sample_edges}


class TestStateType:
    """Test StateType enum."""

    def test_state_types(self):
        """Test all state types exist."""
        assert StateType.SNAPSHOT.value == "snapshot"
        assert StateType.WORKING.value == "working"
        assert StateType.EVENT.value == "event"
        assert StateType.VERSION.value == "version"


class TestGraphSnapshot:
    """Test GraphSnapshot immutable dataclass."""

    def test_creation(self, sample_node_dict, sample_edge_dict):
        """Test snapshot creation."""
        snapshot = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )

        assert snapshot.graph_id == "graph-001"
        assert snapshot.version == 1
        assert len(snapshot.nodes) == 5
        assert len(snapshot.edges) == 4
        assert snapshot.snapshot_id is not None
        assert snapshot.timestamp is not None

    def test_deterministic_id(self, sample_node_dict, sample_edge_dict):
        """Test that same content produces same ID."""
        snapshot1 = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )
        snapshot2 = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )

        assert snapshot1.snapshot_id == snapshot2.snapshot_id

    def test_frozen(self, sample_node_dict, sample_edge_dict):
        """Test that snapshot is immutable."""
        snapshot = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )

        with pytest.raises(AttributeError):
            snapshot.version = 2

    def test_node_count(self, sample_node_dict, sample_edge_dict):
        """Test node_count method."""
        snapshot = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )

        assert snapshot.node_count() == 5

    def test_edge_count(self, sample_node_dict, sample_edge_dict):
        """Test edge_count method."""
        snapshot = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )

        assert snapshot.edge_count() == 4

    def test_contains_node(self, sample_node_dict, sample_edge_dict):
        """Test contains_node method."""
        snapshot = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )

        assert snapshot.contains_node("0000000000000000")
        assert not snapshot.contains_node("f" * 16)

    def test_contains_edge(self, sample_node_dict, sample_edge_dict, sample_edges):
        """Test contains_edge method."""
        snapshot = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=sample_node_dict,
            edges=sample_edge_dict,
        )

        assert snapshot.contains_edge(sample_edges[0])

    def test_diff(self, sample_nodes, sample_edges):
        """Test diff between snapshots."""
        nodes3 = {n.observation_id: n for n in sample_nodes[:3]}
        edges2 = {e.edge_key: e for e in sample_edges[:2]}
        nodes14 = {n.observation_id: n for n in sample_nodes[1:]}
        edges14 = {e.edge_key: e for e in sample_edges[1:]}

        snapshot1 = GraphSnapshot.create(
            graph_id="graph-001",
            version=1,
            nodes=nodes3,
            edges=edges2,
        )
        snapshot2 = GraphSnapshot.create(
            graph_id="graph-001",
            version=2,
            nodes=nodes14,
            edges=edges14,
        )

        diff = snapshot1.diff(snapshot2)

        assert "0000000000000000" in diff["removed_nodes"]
        assert "0000000000000003" in diff["added_nodes"]
        assert "0000000000000004" in diff["added_nodes"]


class TestGraphEvent:
    """Test GraphEvent immutable dataclass."""

    def test_creation(self):
        """Test event creation."""
        event = GraphEvent.create(
            event_type="observation_added",
            snapshot_before=None,
            snapshot_after="snap-001",
        )

        assert event.event_type == "observation_added"
        assert event.snapshot_before is None
        assert event.snapshot_after == "snap-001"
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_deterministic_id(self):
        """Test that same content produces same ID."""
        event1 = GraphEvent.create(
            event_type="observation_added",
            snapshot_before=None,
            snapshot_after="snap-001",
        )
        event2 = GraphEvent.create(
            event_type="observation_added",
            snapshot_before=None,
            snapshot_after="snap-001",
        )

        assert event1.event_id == event2.event_id

    def test_frozen(self):
        """Test that event is immutable."""
        event = GraphEvent.create(
            event_type="observation_added",
            snapshot_before=None,
            snapshot_after="snap-001",
        )

        with pytest.raises(AttributeError):
            event.event_type = "different"


class TestGraphVersion:
    """Test GraphVersion immutable dataclass."""

    def test_creation(self):
        """Test version creation."""
        version = GraphVersion.create(
            snapshot_id="snap-001",
            parent_version=None,
        )

        assert version.snapshot_id == "snap-001"
        assert version.parent_version is None
        assert version.version_id is not None
        assert version.timestamp is not None

    def test_with_parent(self):
        """Test version with parent."""
        version = GraphVersion.create(
            snapshot_id="snap-002",
            parent_version="ver-001",
        )

        assert version.parent_version == "ver-001"

    def test_frozen(self):
        """Test that version is immutable."""
        version = GraphVersion.create(
            snapshot_id="snap-001",
            parent_version=None,
        )

        with pytest.raises(AttributeError):
            version.snapshot_id = "different"


class TestWorkingGraph:
    """Test WorkingGraph mutable container."""

    def test_initialization(self):
        """Test working graph initialization."""
        wg = WorkingGraph("graph-001")

        assert wg.graph_id == "graph-001"
        assert wg.version == 0
        assert wg.node_count == 0
        assert wg.edge_count == 0

    def test_add_node(self, sample_nodes):
        """Test adding nodes."""
        wg = WorkingGraph("graph-001")

        result = wg.add_node(sample_nodes[0])

        assert result is True
        assert wg.node_count == 1
        assert wg.version == 1

    def test_add_duplicate_node(self, sample_nodes):
        """Test adding duplicate node."""
        wg = WorkingGraph("graph-001")

        wg.add_node(sample_nodes[0])
        result = wg.add_node(sample_nodes[0])

        assert result is False
        assert wg.node_count == 1

    def test_add_edge(self, sample_nodes, sample_edges):
        """Test adding edges."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)

        result = wg.add_edge(sample_edges[0])

        assert result is True
        assert wg.edge_count == 1

    def test_add_duplicate_edge(self, sample_nodes, sample_edges):
        """Test adding duplicate edge."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)

        wg.add_edge(sample_edges[0])
        result = wg.add_edge(sample_edges[0])

        assert result is False
        assert wg.edge_count == 1

    def test_remove_node(self, sample_nodes, sample_edges):
        """Test removing node."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)
        for edge in sample_edges:
            wg.add_edge(edge)

        result = wg.remove_node("0000000000000000")

        assert result is True
        assert wg.node_count == 4
        # Edge FROM 0000000000000000 removed (0000000000000000→0000000000000001)
        assert wg.edge_count == 3

    def test_remove_nonexistent_node(self):
        """Test removing nonexistent node."""
        wg = WorkingGraph("graph-001")

        result = wg.remove_node("obs-999")

        assert result is False

    def test_remove_edge(self, sample_nodes, sample_edges):
        """Test removing edge."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)
        wg.add_edge(sample_edges[0])

        result = wg.remove_edge(sample_edges[0])

        assert result is True
        assert wg.edge_count == 0

    def test_remove_nonexistent_edge(self):
        """Test removing nonexistent edge."""
        wg = WorkingGraph("graph-001")

        edge = GraphEdge(
            source_observation_id="obs-000",
            target_observation_id="obs-001",
            relationship_type="temporal_precedes",
            confidence=0.9,
        )

        result = wg.remove_edge(edge)

        assert result is False

    def test_get_node(self, sample_nodes):
        """Test getting node."""
        wg = WorkingGraph("graph-001")

        wg.add_node(sample_nodes[0])

        node = wg.get_node("0000000000000000")

        assert node is not None
        assert node.observation_id == "0000000000000000"

    def test_get_nonexistent_node(self):
        """Test getting nonexistent node."""
        wg = WorkingGraph("graph-001")

        node = wg.get_node("f" * 16)

        assert node is None

    def test_get_all_nodes(self, sample_nodes):
        """Test getting all nodes."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)

        nodes = wg.get_all_nodes()

        assert len(nodes) == 5

    def test_get_all_edges(self, sample_nodes, sample_edges):
        """Test getting all edges."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)
        for edge in sample_edges:
            wg.add_edge(edge)

        edges = wg.get_all_edges()

        assert len(edges) == 4

    def test_get_edges_from(self, sample_nodes, sample_edges):
        """Test getting edges from node."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)
        for edge in sample_edges:
            wg.add_edge(edge)

        edges = wg.get_edges_from("0000000000000000")

        assert len(edges) == 1
        assert edges[0].source_observation_id == "0000000000000000"

    def test_get_edges_to(self, sample_nodes, sample_edges):
        """Test getting edges to node."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)
        for edge in sample_edges:
            wg.add_edge(edge)

        edges = wg.get_edges_to("0000000000000001")

        assert len(edges) == 1
        assert edges[0].target_observation_id == "0000000000000001"

    def test_snapshot(self, sample_nodes, sample_edges):
        """Test creating snapshot."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)
        for edge in sample_edges:
            wg.add_edge(edge)

        snapshot = wg.snapshot()

        assert snapshot.graph_id == "graph-001"
        assert snapshot.node_count() == 5
        assert snapshot.edge_count() == 4
        assert wg.last_snapshot_id == snapshot.snapshot_id
        assert wg.event_count == 1

    def test_restore(self, sample_nodes, sample_edges):
        """Test restoring from snapshot."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)
        for edge in sample_edges:
            wg.add_edge(edge)

        snapshot = wg.snapshot()

        # Modify working graph
        wg.remove_node("0000000000000000")
        assert wg.node_count == 4

        # Restore
        wg.restore(snapshot)
        assert wg.node_count == 5

    def test_to_snapshot(self, sample_nodes, sample_edges):
        """Test to_snapshot (read-only)."""
        wg = WorkingGraph("graph-001")

        for node in sample_nodes:
            wg.add_node(node)

        snapshot = wg.to_snapshot()

        assert snapshot.node_count() == 5
        # Should not affect working graph state
        assert wg.event_count == 0


class TestGraphStateManager:
    """Test GraphStateManager coordinator."""

    def test_initialization(self):
        """Test state manager initialization."""
        sm = GraphStateManager("graph-001")

        assert sm.graph_id == "graph-001"
        assert sm.current_version == 0
        assert sm.working is not None

    def test_add_node(self, sample_nodes):
        """Test adding node through manager."""
        sm = GraphStateManager("graph-001")

        result = sm.add_node(sample_nodes[0])

        assert result is True
        assert sm.working.node_count == 1

    def test_add_edge(self, sample_nodes, sample_edges):
        """Test adding edge through manager."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)

        result = sm.add_edge(sample_edges[0])

        assert result is True
        assert sm.working.edge_count == 1

    def test_create_snapshot(self, sample_nodes, sample_edges):
        """Test creating snapshot through manager."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)
        for edge in sample_edges:
            sm.add_edge(edge)

        snapshot = sm.create_snapshot()

        assert sm.current_version == 1
        # snapshot.version reflects total mutations (5 add_node + 4 add_edge = 9)
        assert snapshot.version == 9
        assert len(sm.get_all_snapshots()) == 1
        assert len(sm.get_all_versions()) == 1
        assert len(sm.get_event_history()) == 1

    def test_get_snapshot(self, sample_nodes, sample_edges):
        """Test getting snapshot by ID."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)

        snapshot = sm.create_snapshot()
        retrieved = sm.get_snapshot(snapshot.snapshot_id)

        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id

    def test_get_nonexistent_snapshot(self):
        """Test getting nonexistent snapshot."""
        sm = GraphStateManager("graph-001")

        retrieved = sm.get_snapshot("nonexistent")

        assert retrieved is None

    def test_get_version(self, sample_nodes, sample_edges):
        """Test getting version by ID."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)

        snapshot = sm.create_snapshot()
        versions = sm.get_all_versions()

        retrieved = sm.get_version(versions[0].version_id)

        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id

    def test_get_all_snapshots(self, sample_nodes, sample_edges):
        """Test getting all snapshots."""
        from miie.processing.observation.models import (
            Observation,
            ObservationProvenance,
            ObservationQuality,
        )

        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)

        sm.create_snapshot()

        # Add a new node so second snapshot has different content
        provenance = ObservationProvenance(
            extractor_id="git.observation.v1",
            extraction_timestamp="2026-01-02T00:00:00Z",
        )
        obs = Observation(
            observation_id="1" * 16,
            metric_id="M-01",
            source_type="commit",
            source_id="c" * 40,
            value=99.0,
            unit="ratio",
            timestamp="2026-01-02T00:00:00Z",
            quality=ObservationQuality.COMPLETE.value,
            provenance=provenance,
        )
        new_node = GraphNode(
            observation=obs,
            provider_id="git.observation.v1",
            metric_id="M-01",
            source_type="commit",
            source_id="c" * 40,
            timestamp="2026-01-02T00:00:00Z",
        )
        sm.add_node(new_node)
        sm.create_snapshot()

        snapshots = sm.get_all_snapshots()

        assert len(snapshots) == 2

    def test_get_all_versions(self, sample_nodes, sample_edges):
        """Test getting all versions."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)

        sm.create_snapshot()
        sm.create_snapshot()

        versions = sm.get_all_versions()

        assert len(versions) == 2

    def test_get_event_history(self, sample_nodes, sample_edges):
        """Test getting event history."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)

        sm.create_snapshot()
        sm.create_snapshot()

        events = sm.get_event_history()

        assert len(events) == 2

    def test_restore_from_snapshot(self, sample_nodes, sample_edges):
        """Test restoring from snapshot."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)
        for edge in sample_edges:
            sm.add_edge(edge)

        snapshot = sm.create_snapshot()

        # Modify working state
        sm.remove_node("0000000000000000")
        assert sm.working.node_count == 4

        # Restore
        result = sm.restore_from_snapshot(snapshot.snapshot_id)

        assert result is True
        assert sm.working.node_count == 5

    def test_restore_from_nonexistent_snapshot(self):
        """Test restoring from nonexistent snapshot."""
        sm = GraphStateManager("graph-001")

        result = sm.restore_from_snapshot("nonexistent")

        assert result is False

    def test_version_lineage(self, sample_nodes, sample_edges):
        """Test version lineage forms DAG."""
        sm = GraphStateManager("graph-001")

        for node in sample_nodes:
            sm.add_node(node)

        snapshot1 = sm.create_snapshot()
        snapshot2 = sm.create_snapshot()
        snapshot3 = sm.create_snapshot()

        versions = sm.get_all_versions()

        # Version 1 has no parent
        assert versions[0].parent_version is None

        # Version 2 has version 1 as parent
        assert versions[1].parent_version == versions[0].version_id

        # Version 3 has version 2 as parent
        assert versions[2].parent_version == versions[1].version_id
