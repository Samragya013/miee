"""
MIIE v1.6 Repository Observation Graph — Serialization.

Deterministic JSON serialization and deserialization of the observation
graph for persistence, transmission, and audit trail.

Reference: PR-11E §7 specification.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from miie.observation_graph.graph import RepositoryObservationGraph
from miie.observation_graph.models import (
    GRAPH_VERSION,
    GraphDiagnostics,
    GraphEdge,
    GraphNode,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GraphSerializer (PR-11E §7)
# ---------------------------------------------------------------------------


class GraphSerializer:
    """PR-11E §7 — Deterministic JSON serialization for the observation graph.

    Produces and parses JSON-serializable representations of the graph
    with deterministic key ordering for reproducibility.

    Usage::

        serializer = GraphSerializer()
        json_str = serializer.to_json(graph)
        graph = serializer.from_json(json_str)
    """

    def to_json(
        self,
        graph: RepositoryObservationGraph,
        indent: Optional[int] = None,
    ) -> str:
        """Serialize the graph to a JSON string.

        Deterministic: same graph always produces same JSON (keys sorted).

        Args:
            graph: The RepositoryObservationGraph to serialize.
            indent: Optional JSON indentation (None for compact).

        Returns:
            JSON string representation.
        """
        serialized = self.to_dict(graph)
        return json.dumps(
            serialized,
            indent=indent,
            sort_keys=True,
            ensure_ascii=False,
        )

    def to_dict(
        self,
        graph: RepositoryObservationGraph,
    ) -> Dict[str, Any]:
        """Serialize the graph to a dict.

        Args:
            graph: The RepositoryObservationGraph to serialize.

        Returns:
            Dict representation of the graph.
        """
        nodes = graph.get_all_nodes()
        edges = graph.get_all_edges()
        diagnostics = graph.get_diagnostics()

        serialized_nodes = [self._serialize_node(node) for node in nodes]
        serialized_edges = [self._serialize_edge(edge) for edge in edges]

        return {
            "schema_version": GRAPH_VERSION,
            "graph_id": graph.graph_id,
            "repository_id": graph.repository_id,
            "analysis_id": graph.analysis_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": serialized_nodes,
            "edges": serialized_edges,
            "diagnostics": self._serialize_diagnostics(diagnostics),
        }

    def from_json(
        self,
        json_str: str,
    ) -> RepositoryObservationGraph:
        """Deserialize a graph from a JSON string.

        Args:
            json_str: JSON string representation.

        Returns:
            Reconstructed RepositoryObservationGraph.

        Raises:
            ValueError: If the JSON is invalid or missing required fields.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

        return self.from_dict(data)

    def from_dict(
        self,
        data: Dict[str, Any],
    ) -> RepositoryObservationGraph:
        """Deserialize a graph from a dict.

        Args:
            data: Dict representation of the graph.

        Returns:
            Reconstructed RepositoryObservationGraph.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = ["graph_id", "repository_id", "analysis_id"]
        for field_name in required_fields:
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")

        graph = RepositoryObservationGraph(
            repository_id=data["repository_id"],
            analysis_id=data["analysis_id"],
            graph_id=data["graph_id"],
        )

        # Reconstruct nodes
        for node_data in data.get("nodes", []):
            node = self._deserialize_node(node_data)
            graph.add_observation(node.observation, node.provider_id)

        # Reconstruct edges
        for edge_data in data.get("edges", []):
            edge = self._deserialize_edge(edge_data)
            graph.add_edge(edge)

        return graph

    # ------------------------------------------------------------------
    # Node Serialization
    # ------------------------------------------------------------------

    def _serialize_node(self, node: GraphNode) -> Dict[str, Any]:
        """Serialize a GraphNode to a dict.

        Args:
            node: The GraphNode to serialize.

        Returns:
            Dict representation.
        """
        return {
            "observation_id": node.observation_id,
            "provider_id": node.provider_id,
            "metric_id": node.metric_id,
            "source_type": node.source_type,
            "source_id": node.source_id,
            "timestamp": node.timestamp,
            "value": node.value,
            "unit": node.unit,
            "quality": node.quality,
            "metadata": node.observation.metadata or {},
            "relationships": [
                {
                    "type": r.type,
                    "target": r.target,
                    "confidence": r.confidence,
                }
                for r in node.observation.relationships
            ],
            "provenance": {
                "extractor_id": node.observation.provenance.extractor_id,
                "extraction_timestamp": node.observation.provenance.extraction_timestamp,
                "seed": node.observation.provenance.seed,
            },
        }

    def _deserialize_node(
        self,
        data: Dict[str, Any],
    ) -> GraphNode:
        """Deserialize a dict to a GraphNode.

        Args:
            data: Dict representation.

        Returns:
            Reconstructed GraphNode.
        """
        from miie.processing.observation.models import (
            Observation,
            ObservationProvenance,
            ObservationRelationship,
        )

        # Reconstruct relationships
        relationships = []
        for rel_data in data.get("relationships", []):
            relationships.append(
                ObservationRelationship(
                    type=rel_data["type"],
                    target=rel_data["target"],
                    confidence=rel_data.get("confidence", 1.0),
                )
            )

        # Reconstruct provenance
        prov_data = data.get("provenance", {})
        provenance = ObservationProvenance(
            extractor_id=prov_data.get("extractor_id", ""),
            extraction_timestamp=prov_data.get("extraction_timestamp", ""),
            seed=prov_data.get("seed"),
        )

        observation = Observation(
            observation_id=data["observation_id"],
            source_type=data["source_type"],
            source_id=data["source_id"],
            metric_id=data["metric_id"],
            value=data["value"],
            unit=data["unit"],
            timestamp=data["timestamp"],
            quality=data["quality"],
            metadata=data.get("metadata", {}),
            relationships=relationships,
            provenance=provenance,
        )

        return GraphNode(
            observation=observation,
            provider_id=data["provider_id"],
            metric_id=data["metric_id"],
            source_type=data["source_type"],
            source_id=data["source_id"],
            timestamp=data["timestamp"],
        )

    # ------------------------------------------------------------------
    # Edge Serialization
    # ------------------------------------------------------------------

    def _serialize_edge(self, edge: GraphEdge) -> Dict[str, Any]:
        """Serialize a GraphEdge to a dict.

        Args:
            edge: The GraphEdge to serialize.

        Returns:
            Dict representation.
        """
        return {
            "source_observation_id": edge.source_observation_id,
            "target_observation_id": edge.target_observation_id,
            "relationship_type": edge.relationship_type,
            "confidence": edge.confidence,
            "metadata": edge.metadata or {},
        }

    def _deserialize_edge(
        self,
        data: Dict[str, Any],
    ) -> GraphEdge:
        """Deserialize a dict to a GraphEdge.

        Args:
            data: Dict representation.

        Returns:
            Reconstructed GraphEdge.
        """
        return GraphEdge(
            source_observation_id=data["source_observation_id"],
            target_observation_id=data["target_observation_id"],
            relationship_type=data["relationship_type"],
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
        )

    # ------------------------------------------------------------------
    # Diagnostics Serialization
    # ------------------------------------------------------------------

    def _serialize_diagnostics(
        self,
        diagnostics: GraphDiagnostics,
    ) -> Dict[str, Any]:
        """Serialize GraphDiagnostics to a dict.

        Args:
            diagnostics: The GraphDiagnostics to serialize.

        Returns:
            Dict representation.
        """
        return {
            "total_nodes": diagnostics.total_nodes,
            "total_edges": diagnostics.total_edges,
            "providers": diagnostics.providers,
            "metrics": diagnostics.metrics,
            "duplicate_count": diagnostics.duplicate_count,
            "orphan_count": diagnostics.orphan_count,
            "relationship_counts": diagnostics.relationship_counts,
            "graph_id": diagnostics.graph_id,
            "schema_version": diagnostics.schema_version,
        }
