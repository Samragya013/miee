"""
MIIE v1.6 Repository Observation Graph — Graph Validation.

Validates graph structure, integrity, and compliance with MIIE v1.6
requirements. Checks node integrity, edge references, provider
consistency, metric compliance, and timestamp ordering.

Reference: PR-11E §6 specification.
"""

from __future__ import annotations

import logging
from typing import List

from miie.observation_graph.graph import RepositoryObservationGraph
from miie.observation_graph.models import (
    GraphValidationResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_SOURCE_TYPES = frozenset({"commit", "file", "branch", "tag"})
VALID_METRIC_IDS = frozenset({"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"})
VALID_QUALITY_LEVELS = frozenset({"complete", "estimated", "derived", "missing"})
METRIC_UNITS = {
    "M-01": "ratio",
    "M-02": "count",
    "M-03": "count",
    "M-04": "count",
    "M-05": "hours",
    "M-06": "count",
    "M-07": "ratio",
}


# ---------------------------------------------------------------------------
# GraphValidator (PR-11E §6)
# ---------------------------------------------------------------------------


class GraphValidator:
    """PR-11E §6 — Validates graph structure and integrity.

    Checks performed:
    - Node integrity: observation_id non-empty, source_type valid,
      metric_id valid, quality valid
    - Edge references: both source and target nodes exist, no self-refs
    - Provider consistency: each node has a non-empty provider_id
    - Metric compliance: metric_id in M-01..M-07, unit matches expected
    - Timestamp ordering: timestamps are valid ISO-8601
    - Graph structure: no duplicate observation_ids, no duplicate edges

    Usage::

        validator = GraphValidator()
        result = validator.validate(graph)
        if not result.is_valid:
            for violation in result.violations:
                print(violation)
    """

    def validate(
        self,
        graph: RepositoryObservationGraph,
    ) -> GraphValidationResult:
        """Validate the graph and return a structured result.

        Args:
            graph: The RepositoryObservationGraph to validate.

        Returns:
            GraphValidationResult with is_valid, violations, and warnings.
        """
        violations: List[str] = []
        warnings: List[str] = []

        nodes = graph.get_all_nodes()
        edges = graph.get_all_edges()
        diagnostics = graph.get_diagnostics()

        # Check 1: Node integrity
        self._check_node_integrity(nodes, violations)

        # Check 2: Edge references
        self._check_edge_references(graph, edges, violations)

        # Check 3: Provider consistency
        self._check_provider_consistency(nodes, violations)

        # Check 4: Metric compliance
        self._check_metric_compliance(nodes, violations, warnings)

        # Check 5: Timestamp ordering
        self._check_timestamps(nodes, violations)

        # Check 6: Graph structure
        self._check_graph_structure(nodes, edges, violations, warnings)

        is_valid = len(violations) == 0

        if is_valid:
            return GraphValidationResult.success(diagnostics=diagnostics)

        return GraphValidationResult.failure(
            violations=violations,
            diagnostics=diagnostics,
        )

    # ------------------------------------------------------------------
    # Check 1: Node Integrity
    # ------------------------------------------------------------------

    def _check_node_integrity(
        self,
        nodes: list,
        violations: List[str],
    ) -> None:
        """Validate each node has required fields with valid values."""
        for node in nodes:
            obs = node.observation

            if not obs.observation_id:
                violations.append(f"Node has empty observation_id (provider={node.provider_id})")

            if node.source_type not in VALID_SOURCE_TYPES:
                violations.append(
                    f"Node {obs.observation_id} has invalid source_type: "
                    f"'{node.source_type}' (expected one of {sorted(VALID_SOURCE_TYPES)})"
                )

            if obs.quality not in VALID_QUALITY_LEVELS:
                violations.append(
                    f"Node {obs.observation_id} has invalid quality: "
                    f"'{obs.quality}' (expected one of {sorted(VALID_QUALITY_LEVELS)})"
                )

    # ------------------------------------------------------------------
    # Check 2: Edge References
    # ------------------------------------------------------------------

    def _check_edge_references(
        self,
        graph: RepositoryObservationGraph,
        edges: list,
        violations: List[str],
    ) -> None:
        """Validate all edges reference existing nodes."""
        for edge in edges:
            src_node = graph.get_node(edge.source_observation_id)
            if src_node is None:
                violations.append(f"Edge references non-existent source node: " f"{edge.source_observation_id}")

            tgt_node = graph.get_node(edge.target_observation_id)
            if tgt_node is None:
                violations.append(f"Edge references non-existent target node: " f"{edge.target_observation_id}")

    # ------------------------------------------------------------------
    # Check 3: Provider Consistency
    # ------------------------------------------------------------------

    def _check_provider_consistency(
        self,
        nodes: list,
        violations: List[str],
    ) -> None:
        """Validate each node has a non-empty provider_id."""
        for node in nodes:
            if not node.provider_id:
                violations.append(f"Node {node.observation_id} has empty provider_id")

    # ------------------------------------------------------------------
    # Check 4: Metric Compliance
    # ------------------------------------------------------------------

    def _check_metric_compliance(
        self,
        nodes: list,
        violations: List[str],
        warnings: List[str],
    ) -> None:
        """Validate metric_id is in M-01..M-07 and unit matches."""
        for node in nodes:
            obs = node.observation

            if node.metric_id not in VALID_METRIC_IDS:
                violations.append(
                    f"Node {obs.observation_id} has invalid metric_id: "
                    f"'{node.metric_id}' (expected one of {sorted(VALID_METRIC_IDS)})"
                )
            else:
                expected_unit = METRIC_UNITS.get(node.metric_id)
                if expected_unit and obs.unit != expected_unit:
                    violations.append(
                        f"Node {obs.observation_id} has wrong unit for "
                        f"metric {node.metric_id}: '{obs.unit}' "
                        f"(expected '{expected_unit}')"
                    )

            if obs.value < 0:
                warnings.append(f"Node {obs.observation_id} has negative value: {obs.value}")

    # ------------------------------------------------------------------
    # Check 5: Timestamp Ordering
    # ------------------------------------------------------------------

    def _check_timestamps(
        self,
        nodes: list,
        violations: List[str],
    ) -> None:
        """Validate timestamps are valid ISO-8601 strings."""
        from datetime import datetime

        for node in nodes:
            try:
                datetime.fromisoformat(node.timestamp.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                violations.append(
                    f"Node {node.observation.observation_id} has invalid " f"timestamp: '{node.timestamp}'"
                )

    # ------------------------------------------------------------------
    # Check 6: Graph Structure
    # ------------------------------------------------------------------

    def _check_graph_structure(
        self,
        nodes: list,
        edges: list,
        violations: List[str],
        warnings: List[str],
    ) -> None:
        """Check for duplicate observation_ids and duplicate edges."""
        # Check for duplicate observation_ids
        seen_ids = set()
        for node in nodes:
            if node.observation_id in seen_ids:
                violations.append(f"Duplicate observation_id: {node.observation_id}")
            seen_ids.add(node.observation_id)

        # Check for duplicate edges
        seen_edges = set()
        for edge in edges:
            key = edge.edge_key
            if key in seen_edges:
                violations.append(f"Duplicate edge: {key}")
            seen_edges.add(key)

        # Warn about disconnected nodes
        if nodes and not edges:
            warnings.append("Graph has nodes but no edges")
