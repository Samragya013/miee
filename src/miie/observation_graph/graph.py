"""
MIIE v1.6 Repository Observation Graph — Core Graph Structure.

The RepositoryObservationGraph is the canonical repository representation
that organizes observations from every provider into one coherent,
deterministic, traceable structure.

Reference: PR-11E specification.
"""

from __future__ import annotations

import datetime
import logging
from typing import Dict, List, Optional, Tuple

from miie.observation_graph.models import (
    GraphDiagnostics,
    GraphEdge,
    GraphIndex,
    GraphNode,
    generate_graph_id,
)
from miie.processing.observation.models import (
    Observation,
    ObservationCollection,
    ObservationWindow,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RepositoryObservationGraph (PR-11E §3)
# ---------------------------------------------------------------------------


class RepositoryObservationGraph:
    """PR-11E §3 — Unified observation graph for a repository.

    Stores observations from all providers in a single coherent structure
    with deterministic ordering, full provenance, and cross-provider
    relationship tracking.

    The graph is the canonical repository representation consumed by
    sampling, windowing, detectors, evidence, scoring, and reporting.

    Usage::

        graph = RepositoryObservationGraph(
            repository_id="owner/repo",
            analysis_id="analysis-001",
        )
        graph.add_observation(obs, provider_id="git.observation.v1")
        graph.add_edge(edge)

        # Query
        nodes = graph.get_by_metric("M-02")
        edges = graph.get_edges("abc123def456")

        # Convert for downstream consumers
        collection = graph.to_observation_collection()
        windows = graph.to_observation_windows()

    Determinism guarantee: for the same set of observations and edges,
    the graph always produces the same indices, ordering, and serialization.
    """

    def __init__(
        self,
        repository_id: str,
        analysis_id: str,
        graph_id: Optional[str] = None,
    ) -> None:
        """Initialize an empty observation graph.

        Args:
            repository_id: Repository identifier (e.g., 'owner/repo').
            analysis_id: Analysis run identifier.
            graph_id: Optional pre-computed graph ID. If None, computed deterministically.
        """
        if not repository_id:
            raise ValueError("repository_id must not be empty")
        if not analysis_id:
            raise ValueError("analysis_id must not be empty")

        self._repository_id = repository_id
        self._analysis_id = analysis_id
        self._graph_id = graph_id or generate_graph_id(repository_id, analysis_id)

        # Core storage
        self._nodes: Dict[str, GraphNode] = {}  # observation_id -> GraphNode
        self._edges: List[GraphEdge] = []

        # Indices (rebuilt on query or explicit rebuild)
        self._index = GraphIndex()
        self._index_dirty = True

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def graph_id(self) -> str:
        """Deterministic graph identifier."""
        return self._graph_id

    @property
    def repository_id(self) -> str:
        """Repository identifier."""
        return self._repository_id

    @property
    def analysis_id(self) -> str:
        """Analysis run identifier."""
        return self._analysis_id

    @property
    def node_count(self) -> int:
        """Number of observations in the graph."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Number of relationships in the graph."""
        return len(self._edges)

    @property
    def is_empty(self) -> bool:
        """Check if the graph has no observations."""
        return len(self._nodes) == 0

    # ------------------------------------------------------------------
    # Index Management
    # ------------------------------------------------------------------

    def _ensure_index(self) -> None:
        """Rebuild indices if they are stale."""
        if self._index_dirty:
            self._rebuild_indices()

    def _rebuild_indices(self) -> None:
        """Rebuild all internal indices from current nodes and edges."""
        self._index = GraphIndex()

        # Index nodes by observation_id, metric_id, provider_id, source
        for node in self._nodes.values():
            self._index.by_observation_id[node.observation_id] = node

            if node.metric_id not in self._index.by_metric_id:
                self._index.by_metric_id[node.metric_id] = []
            self._index.by_metric_id[node.metric_id].append(node)

            if node.provider_id not in self._index.by_provider_id:
                self._index.by_provider_id[node.provider_id] = []
            self._index.by_provider_id[node.provider_id].append(node)

            source_key = (node.source_type, node.source_id)
            if source_key not in self._index.by_source:
                self._index.by_source[source_key] = []
            self._index.by_source[source_key].append(node)

        # Sort by timestamp for time-range queries
        self._index.by_timestamp = sorted(
            self._nodes.values(),
            key=lambda n: n.timestamp,
        )

        # Index edges by source and target
        for edge in self._edges:
            if edge.source_observation_id not in self._index.edges_by_source:
                self._index.edges_by_source[edge.source_observation_id] = []
            self._index.edges_by_source[edge.source_observation_id].append(edge)

            if edge.target_observation_id not in self._index.edges_by_target:
                self._index.edges_by_target[edge.target_observation_id] = []
            self._index.edges_by_target[edge.target_observation_id].append(edge)

        self._index_dirty = False

    # ------------------------------------------------------------------
    # Add Observations
    # ------------------------------------------------------------------

    def add_observation(self, observation: Observation, provider_id: str) -> bool:
        """Add a single observation to the graph.

        Args:
            observation: The Observation to add.
            provider_id: Identifier of the provider that produced it.

        Returns:
            True if added, False if duplicate (same observation_id).
        """
        obs_id = observation.observation_id
        if obs_id in self._nodes:
            return False

        node = GraphNode(
            observation=observation,
            provider_id=provider_id,
            metric_id=observation.metric_id,
            source_type=observation.source_type,
            source_id=observation.source_id,
            timestamp=observation.timestamp,
        )
        self._nodes[obs_id] = node
        self._index_dirty = True
        return True

    def add_observations(
        self,
        observations: Tuple[Observation, ...],
        provider_id: str,
    ) -> int:
        """Add a batch of observations to the graph.

        Args:
            observations: Tuple of Observations to add.
            provider_id: Identifier of the provider that produced them.

        Returns:
            Number of observations actually added (excluding duplicates).
        """
        added = 0
        for obs in observations:
            if self.add_observation(obs, provider_id):
                added += 1
        return added

    # ------------------------------------------------------------------
    # Add Edges
    # ------------------------------------------------------------------

    def add_edge(self, edge: GraphEdge) -> bool:
        """Add a single edge to the graph.

        Args:
            edge: The GraphEdge to add.

        Returns:
            True if added, False if duplicate edge.
        """
        edge_key = edge.edge_key
        for existing in self._edges:
            if existing.edge_key == edge_key:
                return False

        # Validate that both nodes exist
        if edge.source_observation_id not in self._nodes:
            logger.warning(
                "Edge references non-existent source node: %s",
                edge.source_observation_id,
            )
            return False
        if edge.target_observation_id not in self._nodes:
            logger.warning(
                "Edge references non-existent target node: %s",
                edge.target_observation_id,
            )
            return False

        self._edges.append(edge)
        self._index_dirty = True
        return True

    def add_edges(self, edges: List[GraphEdge]) -> int:
        """Add a batch of edges to the graph.

        Args:
            edges: List of GraphEdges to add.

        Returns:
            Number of edges actually added (excluding duplicates).
        """
        added = 0
        for edge in edges:
            if self.add_edge(edge):
                added += 1
        return added

    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------

    def get_node(self, observation_id: str) -> Optional[GraphNode]:
        """Get a node by observation ID.

        Args:
            observation_id: The observation identifier.

        Returns:
            The GraphNode, or None if not found.
        """
        self._ensure_index()
        return self._index.by_observation_id.get(observation_id)

    def get_by_metric(self, metric_id: str) -> List[GraphNode]:
        """Get all nodes for a specific metric.

        Args:
            metric_id: The metric identifier (e.g., 'M-02').

        Returns:
            List of GraphNodes, sorted by observation_id.
        """
        self._ensure_index()
        nodes = self._index.by_metric_id.get(metric_id, [])
        return sorted(nodes, key=lambda n: n.observation_id)

    def get_by_provider(self, provider_id: str) -> List[GraphNode]:
        """Get all nodes from a specific provider.

        Args:
            provider_id: The provider identifier.

        Returns:
            List of GraphNodes, sorted by observation_id.
        """
        self._ensure_index()
        nodes = self._index.by_provider_id.get(provider_id, [])
        return sorted(nodes, key=lambda n: n.observation_id)

    def get_by_source(self, source_type: str, source_id: str) -> List[GraphNode]:
        """Get all nodes for a specific source.

        Args:
            source_type: The source type (e.g., 'commit').
            source_id: The source identifier.

        Returns:
            List of GraphNodes, sorted by observation_id.
        """
        self._ensure_index()
        key = (source_type, source_id)
        nodes = self._index.by_source.get(key, [])
        return sorted(nodes, key=lambda n: n.observation_id)

    def get_by_time_range(self, start: str, end: str) -> List[GraphNode]:
        """Get all nodes within a time range.

        Args:
            start: Inclusive start ISO-8601 timestamp.
            end: Inclusive end ISO-8601 timestamp.

        Returns:
            List of GraphNodes, sorted by timestamp.
        """
        self._ensure_index()
        result = []
        for node in self._index.by_timestamp:
            if start <= node.timestamp <= end:
                result.append(node)
        return result

    def get_edges(self, observation_id: str) -> List[GraphEdge]:
        """Get all edges where this observation is source or target.

        Args:
            observation_id: The observation identifier.

        Returns:
            List of GraphEdges, sorted by (source, target, type).
        """
        self._ensure_index()
        source_edges = self._index.edges_by_source.get(observation_id, [])
        target_edges = self._index.edges_by_target.get(observation_id, [])
        all_edges = source_edges + target_edges
        return sorted(all_edges, key=lambda e: e.edge_key)

    def get_edges_from(self, observation_id: str) -> List[GraphEdge]:
        """Get edges where this observation is the source.

        Args:
            observation_id: The source observation identifier.

        Returns:
            List of GraphEdges, sorted by edge key.
        """
        self._ensure_index()
        edges = self._index.edges_by_source.get(observation_id, [])
        return sorted(edges, key=lambda e: e.edge_key)

    def get_edges_to(self, observation_id: str) -> List[GraphEdge]:
        """Get edges where this observation is the target.

        Args:
            observation_id: The target observation identifier.

        Returns:
            List of GraphEdges, sorted by edge key.
        """
        self._ensure_index()
        edges = self._index.edges_by_target.get(observation_id, [])
        return sorted(edges, key=lambda e: e.edge_key)

    def get_all_observations(self) -> List[Observation]:
        """Get all observations in deterministic order.

        Order: sorted by observation_id.

        Returns:
            Flat list of all observations.
        """
        self._ensure_index()
        return [
            node.observation
            for node in sorted(
                self._nodes.values(),
                key=lambda n: n.observation_id,
            )
        ]

    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes in deterministic order.

        Order: sorted by observation_id.

        Returns:
            List of all GraphNodes.
        """
        self._ensure_index()
        return sorted(
            self._nodes.values(),
            key=lambda n: n.observation_id,
        )

    def get_all_edges(self) -> List[GraphEdge]:
        """Get all edges in deterministic order.

        Order: sorted by (source_observation_id, target_observation_id, relationship_type).

        Returns:
            List of all GraphEdges.
        """
        return sorted(self._edges, key=lambda e: e.edge_key)

    # ------------------------------------------------------------------
    # Conversion for Downstream Consumers
    # ------------------------------------------------------------------

    def to_observation_collection(self) -> ObservationCollection:
        """Convert graph to an ObservationCollection for downstream consumers.

        Creates a single-window collection containing all observations,
        compatible with detectors, sampling, and scoring.

        Returns:
            ObservationCollection with all graph observations.
        """
        observations = self.get_all_observations()

        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="custom",
            start_boundary=self._compute_start_boundary(observations),
            end_boundary=self._compute_end_boundary(observations),
            observations=observations,
            metrics_present=sorted({obs.metric_id for obs in observations}),
        )

        return ObservationCollection(
            collection_id=self._graph_id,
            repository_id=self._repository_id,
            analysis_id=self._analysis_id,
            windows=[window],
            total_observations=len(observations),
            total_metrics=len({obs.metric_id for obs in observations}),
            extraction_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            schema_version="1.0.0",
        )

    def to_observation_windows(self) -> List[ObservationWindow]:
        """Convert graph to a list of ObservationWindows for detectors.

        Creates a single window containing all observations, compatible
        with D-01, D-02, D-03 detectors.

        Returns:
            List containing one ObservationWindow with all observations.
        """
        observations = self.get_all_observations()

        return [
            ObservationWindow(
                window_id="w00",
                window_index=0,
                strategy="custom",
                start_boundary=self._compute_start_boundary(observations),
                end_boundary=self._compute_end_boundary(observations),
                observations=observations,
                metrics_present=sorted({obs.metric_id for obs in observations}),
            )
        ]

    def _compute_start_boundary(self, observations: List[Observation]) -> str:
        """Compute the earliest timestamp from observations."""
        if not observations:
            return datetime.datetime.now(datetime.timezone.utc).isoformat()
        return min(obs.timestamp for obs in observations)

    def _compute_end_boundary(self, observations: List[Observation]) -> str:
        """Compute the latest timestamp from observations."""
        if not observations:
            return datetime.datetime.now(datetime.timezone.utc).isoformat()
        return max(obs.timestamp for obs in observations)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_diagnostics(self) -> GraphDiagnostics:
        """Compute comprehensive graph diagnostics.

        Returns:
            GraphDiagnostics with full statistics.
        """
        self._ensure_index()

        providers = sorted(self._index.by_provider_id.keys())
        metrics = sorted(self._index.by_metric_id.keys())
        sources = sorted(self._index.by_source.keys())

        # Compute coverage: metric -> provider -> count
        coverage: Dict[str, Dict[str, int]] = {}
        for metric_id in metrics:
            coverage[metric_id] = {}
            for provider_id in providers:
                count = sum(
                    1 for node in self._index.by_metric_id.get(metric_id, []) if node.provider_id == provider_id
                )
                if count > 0:
                    coverage[metric_id][provider_id] = count

        # Count relationships by type
        relationship_counts: Dict[str, int] = {}
        for edge in self._edges:
            rel_type = edge.relationship_type
            relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1

        # Count orphans (nodes with no edges)
        nodes_with_edges = set()
        for edge in self._edges:
            nodes_with_edges.add(edge.source_observation_id)
            nodes_with_edges.add(edge.target_observation_id)
        orphan_count = sum(1 for obs_id in self._nodes if obs_id not in nodes_with_edges)

        return GraphDiagnostics(
            total_nodes=len(self._nodes),
            total_edges=len(self._edges),
            providers=providers,
            metrics=metrics,
            sources=sources,
            duplicate_count=0,  # Set during build
            orphan_count=orphan_count,
            relationship_counts=relationship_counts,
            coverage=coverage,
            graph_id=self._graph_id,
        )
