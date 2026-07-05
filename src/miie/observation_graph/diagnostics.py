"""
MIIE v1.6 Repository Observation Graph — Graph Diagnostics Engine.

Computes comprehensive statistics about the observation graph structure,
provider contributions, relationship discovery, and graph health.

Reference: PR-11E §8 specification.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from miie.observation_graph.graph import RepositoryObservationGraph
from miie.observation_graph.models import GraphDiagnostics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GraphDiagnosticsEngine (PR-11E §8)
# ---------------------------------------------------------------------------


class GraphDiagnosticsEngine:
    """PR-11E §8 — Comprehensive graph diagnostics and health analysis.

    Computes statistics across multiple dimensions:
    - Provider contribution analysis
    - Metric coverage matrix
    - Relationship health (orphan ratio, connectivity)
    - Graph completeness metrics
    - Temporal range analysis

    Usage::

        engine = GraphDiagnosticsEngine()
        diagnostics = engine.compute(graph)
        print(f"Health score: {engine.health_score(diagnostics)}")
    """

    def compute(
        self,
        graph: RepositoryObservationGraph,
    ) -> GraphDiagnostics:
        """Compute full diagnostics for the graph.

        Args:
            graph: The RepositoryObservationGraph to analyze.

        Returns:
            GraphDiagnostics with complete statistics.
        """
        return graph.get_diagnostics()

    def health_score(
        self,
        diagnostics: GraphDiagnostics,
    ) -> float:
        """Compute a health score (0.0 - 1.0) for the graph.

        Factors:
        - Orphan ratio (lower is better)
        - Edge connectivity (more edges is better)
        - Provider diversity (more providers is better)
        - Metric coverage (more metrics is better)

        Args:
            diagnostics: GraphDiagnostics to score.

        Returns:
            Health score from 0.0 (unhealthy) to 1.0 (healthy).
        """
        if diagnostics.total_nodes == 0:
            return 1.0

        scores: List[float] = []

        # Factor 1: Orphan ratio (0.0 = all orphans, 1.0 = no orphans)
        orphan_score = 1.0 - diagnostics.orphan_ratio
        scores.append(orphan_score)

        # Factor 2: Edge connectivity
        max_edges = diagnostics.total_nodes * (diagnostics.total_nodes - 1)
        if max_edges > 0:
            connectivity = min(diagnostics.total_edges / max_edges, 1.0)
        else:
            connectivity = 1.0
        scores.append(connectivity)

        # Factor 3: Provider diversity (normalize: 3+ providers = full score)
        provider_score = min(diagnostics.provider_count / 3.0, 1.0)
        scores.append(provider_score)

        # Factor 4: Metric coverage (normalize: 5+ metrics = full score)
        metric_score = min(diagnostics.metric_count / 5.0, 1.0)
        scores.append(metric_score)

        return sum(scores) / len(scores) if scores else 1.0

    def provider_summary(
        self,
        graph: RepositoryObservationGraph,
    ) -> Dict[str, Dict[str, Any]]:
        """Summarize contribution per provider.

        Args:
            graph: The graph to analyze.

        Returns:
            Dict mapping provider_id to summary stats.
        """
        nodes = graph.get_all_nodes()
        summary: Dict[str, Dict[str, Any]] = {}

        for node in nodes:
            pid = node.provider_id
            if pid not in summary:
                summary[pid] = {
                    "observation_count": 0,
                    "metrics": set(),
                    "sources": set(),
                    "quality_counts": {"complete": 0, "estimated": 0, "derived": 0, "missing": 0},
                }

            summary[pid]["observation_count"] += 1
            summary[pid]["metrics"].add(node.metric_id)
            summary[pid]["sources"].add(node.source_type)
            quality = node.observation.quality
            if quality in summary[pid]["quality_counts"]:
                summary[pid]["quality_counts"][quality] += 1

        # Convert sets to sorted lists for JSON serialization
        for pid in summary:
            summary[pid]["metrics"] = sorted(summary[pid]["metrics"])
            summary[pid]["sources"] = sorted(summary[pid]["sources"])

        return summary

    def coverage_matrix(
        self,
        graph: RepositoryObservationGraph,
    ) -> Dict[str, Dict[str, int]]:
        """Compute metric-provider coverage matrix.

        Args:
            graph: The graph to analyze.

        Returns:
            Dict mapping metric_id to provider_id to observation count.
        """
        diagnostics = graph.get_diagnostics()
        return diagnostics.coverage

    def relationship_summary(
        self,
        graph: RepositoryObservationGraph,
    ) -> Dict[str, int]:
        """Summarize edges by relationship type.

        Args:
            graph: The graph to analyze.

        Returns:
            Dict mapping relationship_type to count.
        """
        diagnostics = graph.get_diagnostics()
        return diagnostics.relationship_counts

    def orphan_analysis(
        self,
        graph: RepositoryObservationGraph,
    ) -> Dict[str, Any]:
        """Analyze orphaned nodes (nodes with no edges).

        Args:
            graph: The graph to analyze.

        Returns:
            Dict with orphan count, ratio, and list of orphan observation IDs.
        """
        nodes = graph.get_all_nodes()
        edges = graph.get_all_edges()

        nodes_with_edges = set()
        for edge in edges:
            nodes_with_edges.add(edge.source_observation_id)
            nodes_with_edges.add(edge.target_observation_id)

        orphan_ids = [node.observation_id for node in nodes if node.observation_id not in nodes_with_edges]

        total = len(nodes)
        orphan_count = len(orphan_ids)
        orphan_ratio = orphan_count / total if total > 0 else 0.0

        return {
            "orphan_count": orphan_count,
            "total_nodes": total,
            "orphan_ratio": orphan_ratio,
            "orphan_ids": sorted(orphan_ids),
        }

    def temporal_range(
        self,
        graph: RepositoryObservationGraph,
    ) -> Dict[str, str]:
        """Compute the temporal range of the graph.

        Args:
            graph: The graph to analyze.

        Returns:
            Dict with earliest and latest timestamps.
        """
        nodes = graph.get_all_nodes()
        if not nodes:
            return {"earliest": "", "latest": ""}

        timestamps = [node.timestamp for node in nodes]
        return {
            "earliest": min(timestamps),
            "latest": max(timestamps),
        }
