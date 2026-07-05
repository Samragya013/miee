"""
SR-04: Unified Graph State Model

Resolves CF-04 (Graph Immutability Contradiction) by distinguishing:
- Immutable Snapshots (scientific record)
- Mutable Working State (streaming/operational)
- Event History (audit trail)
- Version Lineage (version tracking)

This module provides the canonical state model that reconciles:
- Doc 03/06: "Graph is immutable after construction" (scientific immutability)
- Doc 07: "Graph is updated incrementally" (operational mutability)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from miie.observation_graph.models import GraphEdge, GraphNode


class StateType(Enum):
    """Types of graph state."""
    SNAPSHOT = "snapshot"          # Immutable scientific record
    WORKING = "working"            # Mutable operational state
    EVENT = "event"                # Audit trail entry
    VERSION = "version"            # Version lineage node


@dataclass(frozen=True)
class GraphSnapshot:
    """
    Immutable snapshot of graph state at a specific point in time.

    This is the scientific record — once created, it never changes.
    Snapshots capture the complete graph state for reproducibility,
    audit, and verification.

    Uses Dict[str, GraphNode] and Dict[Tuple[str,str,str], GraphEdge]
    instead of FrozenSet to avoid hashability issues with mutable
    dict fields in Observation. The frozen=True prevents reassignment
    of the dicts themselves, maintaining immutability.

    Attributes:
        snapshot_id: Unique identifier (SHA-256 of content)
        graph_id: Parent graph identifier
        version: Monotonic version number
        timestamp: ISO-8601 creation timestamp
        nodes: Immutable dict of graph nodes keyed by observation_id
        edges: Immutable dict of graph edges keyed by edge_key tuple
        metadata: Snapshot metadata (provider counts, metrics, etc.)
        parent_snapshot: Previous snapshot ID (for lineage)
    """
    snapshot_id: str
    graph_id: str
    version: int
    timestamp: str
    nodes: Dict[str, GraphNode]
    edges: Dict[Tuple[str, str, str], GraphEdge]
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_snapshot: Optional[str] = None

    @classmethod
    def create(
        cls,
        graph_id: str,
        version: int,
        nodes: Dict[str, GraphNode],
        edges: Dict[Tuple[str, str, str], GraphEdge],
        metadata: Optional[Dict[str, Any]] = None,
        parent_snapshot: Optional[str] = None,
    ) -> GraphSnapshot:
        """Create a new snapshot with deterministic ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        snapshot_id = cls._compute_id(graph_id, version, nodes, edges)
        return cls(
            snapshot_id=snapshot_id,
            graph_id=graph_id,
            version=version,
            timestamp=timestamp,
            nodes=nodes,
            edges=edges,
            metadata=metadata or {},
            parent_snapshot=parent_snapshot,
        )

    @staticmethod
    def _compute_id(
        graph_id: str,
        version: int,
        nodes: Dict[str, GraphNode],
        edges: Dict[Tuple[str, str, str], GraphEdge],
    ) -> str:
        """Compute deterministic snapshot ID from content."""
        content = {
            "graph_id": graph_id,
            "version": version,
            "nodes": sorted(nodes.keys()),
            "edges": sorted([list(k) for k in edges.keys()]),
        }
        content_bytes = json.dumps(content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(content_bytes).hexdigest()[:16]

    def node_count(self) -> int:
        """Number of nodes in snapshot."""
        return len(self.nodes)

    def edge_count(self) -> int:
        """Number of edges in snapshot."""
        return len(self.edges)

    def contains_node(self, observation_id: str) -> bool:
        """Check if snapshot contains a specific node."""
        return observation_id in self.nodes

    def contains_edge(self, edge: GraphEdge) -> bool:
        """Check if snapshot contains a specific edge."""
        return edge.edge_key in self.edges

    def diff(self, other: GraphSnapshot) -> Dict[str, Any]:
        """Compute diff between two snapshots."""
        self_node_ids = set(self.nodes.keys())
        other_node_ids = set(other.nodes.keys())

        self_edge_keys = set(self.edges.keys())
        other_edge_keys = set(other.edges.keys())

        return {
            "added_nodes": other_node_ids - self_node_ids,
            "removed_nodes": self_node_ids - other_node_ids,
            "added_edges": other_edge_keys - self_edge_keys,
            "removed_edges": self_edge_keys - other_edge_keys,
        }


@dataclass(frozen=True)
class GraphEvent:
    """
    Immutable audit trail entry for graph state transitions.

    Events record what changed, when, and why. They form an
    append-only log that enables replay and debugging.

    Attributes:
        event_id: Unique event identifier
        event_type: Type of event (observation_added, edge_added, etc.)
        timestamp: ISO-8601 event timestamp
        snapshot_before: Previous snapshot ID (None for first event)
        snapshot_after: New snapshot ID
        payload: Event-specific data
        metadata: Event metadata (provider, source, etc.)
    """
    event_id: str
    event_type: str
    timestamp: str
    snapshot_before: Optional[str]
    snapshot_after: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: str,
        snapshot_before: Optional[str],
        snapshot_after: str,
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphEvent:
        """Create a new event with deterministic ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        event_id = cls._compute_id(event_type, timestamp, snapshot_before, snapshot_after)
        return cls(
            event_id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            snapshot_before=snapshot_before,
            snapshot_after=snapshot_after,
            payload=payload or {},
            metadata=metadata or {},
        )

    @staticmethod
    def _compute_id(
        event_type: str,
        timestamp: str,
        snapshot_before: Optional[str],
        snapshot_after: str,
    ) -> str:
        """Compute deterministic event ID."""
        content = {
            "event_type": event_type,
            "timestamp": timestamp,
            "snapshot_before": snapshot_before,
            "snapshot_after": snapshot_after,
        }
        content_bytes = json.dumps(content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(content_bytes).hexdigest()[:16]


@dataclass(frozen=True)
class GraphVersion:
    """
    Version lineage node for tracking graph evolution.

    Versions form a directed acyclic graph (DAG) representing
    the evolution of graph snapshots over time.

    Attributes:
        version_id: Unique version identifier
        snapshot_id: Associated snapshot
        parent_version: Parent version ID (None for root)
        timestamp: ISO-8601 creation timestamp
        metadata: Version metadata (changes, reason, etc.)
    """
    version_id: str
    snapshot_id: str
    parent_version: Optional[str]
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        snapshot_id: str,
        parent_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphVersion:
        """Create a new version with deterministic ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        version_id = cls._compute_id(snapshot_id, parent_version, timestamp)
        return cls(
            version_id=version_id,
            snapshot_id=snapshot_id,
            parent_version=parent_version,
            timestamp=timestamp,
            metadata=metadata or {},
        )

    @staticmethod
    def _compute_id(
        snapshot_id: str,
        parent_version: Optional[str],
        timestamp: str,
    ) -> str:
        """Compute deterministic version ID."""
        content = {
            "snapshot_id": snapshot_id,
            "parent_version": parent_version,
            "timestamp": timestamp,
        }
        content_bytes = json.dumps(content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(content_bytes).hexdigest()[:16]


class WorkingGraph:
    """
    Mutable graph container for streaming/operational use.

    This is the working state that gets modified during processing.
    It can be snapshotted at any point to create an immutable record.

    The working graph maintains:
- Current nodes and edges
- Version counter
- Last snapshot ID
- Event history reference

    Design principle: The working graph is mutable, but snapshots
    taken from it are immutable. This satisfies both:
- Doc 03/06: "Graph is immutable after construction" (via snapshots)
- Doc 07: "Graph is updated incrementally" (via working state)
    """

    def __init__(self, graph_id: str):
        """
        Initialize working graph.

        Args:
            graph_id: Unique graph identifier
        """
        self._graph_id = graph_id
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
        self._version = 0
        self._last_snapshot_id: Optional[str] = None
        self._event_history: List[GraphEvent] = []
        self._versions: List[GraphVersion] = []

    @property
    def graph_id(self) -> str:
        """Graph identifier."""
        return self._graph_id

    @property
    def version(self) -> int:
        """Current version number."""
        return self._version

    @property
    def node_count(self) -> int:
        """Number of nodes."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Number of edges."""
        return len(self._edges)

    @property
    def last_snapshot_id(self) -> Optional[str]:
        """ID of the last snapshot."""
        return self._last_snapshot_id

    @property
    def event_count(self) -> int:
        """Number of events in history."""
        return len(self._event_history)

    def add_node(self, node: GraphNode) -> bool:
        """
        Add a node to the working graph.

        Args:
            node: Graph node to add

        Returns:
            True if added, False if duplicate
        """
        if node.observation_id in self._nodes:
            return False

        self._nodes[node.observation_id] = node
        self._version += 1
        return True

    def add_edge(self, edge: GraphEdge) -> bool:
        """
        Add an edge to the working graph.

        Args:
            edge: Graph edge to add

        Returns:
            True if added, False if duplicate
        """
        if edge in self._edges:
            return False

        self._edges.append(edge)
        self._version += 1
        return True

    def remove_node(self, observation_id: str) -> bool:
        """
        Remove a node and its edges from the working graph.

        Args:
            observation_id: ID of node to remove

        Returns:
            True if removed, False if not found
        """
        if observation_id not in self._nodes:
            return False

        del self._nodes[observation_id]
        self._edges = [
            e for e in self._edges
            if e.source_observation_id != observation_id
            and e.target_observation_id != observation_id
        ]
        self._version += 1
        return True

    def remove_edge(self, edge: GraphEdge) -> bool:
        """
        Remove an edge from the working graph.

        Args:
            edge: Graph edge to remove

        Returns:
            True if removed, False if not found
        """
        try:
            self._edges.remove(edge)
            self._version += 1
            return True
        except ValueError:
            return False

    def get_node(self, observation_id: str) -> Optional[GraphNode]:
        """Get a node by observation ID."""
        return self._nodes.get(observation_id)

    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes."""
        return list(self._nodes.values())

    def get_all_edges(self) -> List[GraphEdge]:
        """Get all edges."""
        return list(self._edges)

    def get_edges_from(self, observation_id: str) -> List[GraphEdge]:
        """Get all edges from a node."""
        return [e for e in self._edges if e.source_observation_id == observation_id]

    def get_edges_to(self, observation_id: str) -> List[GraphEdge]:
        """Get all edges to a node."""
        return [e for e in self._edges if e.target_observation_id == observation_id]

    def snapshot(self, metadata: Optional[Dict[str, Any]] = None) -> GraphSnapshot:
        """
        Create an immutable snapshot of the current state.

        This is the key operation that bridges mutable working state
        with immutable scientific record.

        Args:
            metadata: Optional metadata for the snapshot

        Returns:
            Immutable snapshot of current state
        """
        # Build edge dict keyed by edge_key tuple
        edge_dict: Dict[Tuple[str, str, str], GraphEdge] = {}
        for edge in self._edges:
            edge_dict[edge.edge_key] = edge

        snapshot = GraphSnapshot.create(
            graph_id=self._graph_id,
            version=self._version,
            nodes=dict(self._nodes),  # copy
            edges=edge_dict,
            metadata=metadata,
            parent_snapshot=self._last_snapshot_id,
        )

        # Record event
        event = GraphEvent.create(
            event_type="snapshot_created",
            snapshot_before=self._last_snapshot_id,
            snapshot_after=snapshot.snapshot_id,
            metadata={"node_count": len(self._nodes), "edge_count": len(self._edges)},
        )
        self._event_history.append(event)

        # Update state
        self._last_snapshot_id = snapshot.snapshot_id

        return snapshot

    def restore(self, snapshot: GraphSnapshot) -> None:
        """
        Restore working state from an immutable snapshot.

        This enables rollback and replay operations.

        Args:
            snapshot: Snapshot to restore from
        """
        self._nodes = dict(snapshot.nodes)
        self._edges = list(snapshot.edges.values())
        self._version = snapshot.version

        # Record event
        event = GraphEvent.create(
            event_type="snapshot_restored",
            snapshot_before=self._last_snapshot_id,
            snapshot_after=snapshot.snapshot_id,
            metadata={"node_count": len(snapshot.nodes), "edge_count": len(snapshot.edges)},
        )
        self._event_history.append(event)

        self._last_snapshot_id = snapshot.snapshot_id

    def get_event_history(self) -> List[GraphEvent]:
        """Get the event history."""
        return list(self._event_history)

    def get_versions(self) -> List[GraphVersion]:
        """Get the version lineage."""
        return list(self._versions)

    def to_snapshot(self) -> GraphSnapshot:
        """
        Create a snapshot without recording in history.

        Useful for read-only inspection.
        """
        edge_dict: Dict[Tuple[str, str, str], GraphEdge] = {}
        for edge in self._edges:
            edge_dict[edge.edge_key] = edge

        return GraphSnapshot.create(
            graph_id=self._graph_id,
            version=self._version,
            nodes=dict(self._nodes),
            edges=edge_dict,
        )


class GraphStateManager:
    """
    Manages graph state transitions and version lineage.

    This is the top-level coordinator that ensures:
- Snapshots are immutable after creation
- Events form an append-only log
- Versions form a DAG
- Working state can be snapshotted and restored
    """

    def __init__(self, graph_id: str):
        """
        Initialize state manager.

        Args:
            graph_id: Unique graph identifier
        """
        self._graph_id = graph_id
        self._working = WorkingGraph(graph_id)
        self._snapshots: Dict[str, GraphSnapshot] = {}
        self._versions: Dict[str, GraphVersion] = {}
        self._events: List[GraphEvent] = []
        self._current_version = 0

    @property
    def graph_id(self) -> str:
        """Graph identifier."""
        return self._graph_id

    @property
    def working(self) -> WorkingGraph:
        """Access the mutable working graph."""
        return self._working

    @property
    def current_version(self) -> int:
        """Current version number."""
        return self._current_version

    def add_node(self, node: GraphNode) -> bool:
        """Add a node to working state."""
        return self._working.add_node(node)

    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to working state."""
        return self._working.add_edge(edge)

    def remove_node(self, observation_id: str) -> bool:
        """Remove a node from working state."""
        return self._working.remove_node(observation_id)

    def remove_edge(self, edge: GraphEdge) -> bool:
        """Remove an edge from working state."""
        return self._working.remove_edge(edge)

    def create_snapshot(self, metadata: Optional[Dict[str, Any]] = None) -> GraphSnapshot:
        """
        Create an immutable snapshot and record version.

        Args:
            metadata: Optional metadata

        Returns:
            The created snapshot
        """
        # Create snapshot from working state
        snapshot = self._working.snapshot(metadata)

        # Store snapshot
        self._snapshots[snapshot.snapshot_id] = snapshot

        # Create version
        parent_version = None
        if self._versions:
            parent_version = list(self._versions.keys())[-1]

        version = GraphVersion.create(
            snapshot_id=snapshot.snapshot_id,
            parent_version=parent_version,
            metadata=metadata,
        )
        self._versions[version.version_id] = version

        # Update version counter
        self._current_version += 1

        # Record event
        event = GraphEvent.create(
            event_type="snapshot_created",
            snapshot_before=self._working.last_snapshot_id,
            snapshot_after=snapshot.snapshot_id,
            metadata={"version": self._current_version},
        )
        self._events.append(event)

        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Optional[GraphSnapshot]:
        """Get a snapshot by ID."""
        return self._snapshots.get(snapshot_id)

    def get_version(self, version_id: str) -> Optional[GraphVersion]:
        """Get a version by ID."""
        return self._versions.get(version_id)

    def get_all_snapshots(self) -> List[GraphSnapshot]:
        """Get all snapshots."""
        return list(self._snapshots.values())

    def get_all_versions(self) -> List[GraphVersion]:
        """Get all versions."""
        return list(self._versions.values())

    def get_event_history(self) -> List[GraphEvent]:
        """Get the event history."""
        return list(self._events)

    def restore_from_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore working state from a snapshot.

        Args:
            snapshot_id: ID of snapshot to restore

        Returns:
            True if restored, False if not found
        """
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot is None:
            return False

        self._working.restore(snapshot)

        # Record event
        event = GraphEvent.create(
            event_type="snapshot_restored",
            snapshot_before=self._working.last_snapshot_id,
            snapshot_after=snapshot_id,
        )
        self._events.append(event)

        return True
