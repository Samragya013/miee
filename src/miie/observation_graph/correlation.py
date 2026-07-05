"""
MIIE v1.6 Repository Observation Graph — Cross-Provider Correlation Engine.

Discovers relationships between observations from different providers
without statistical inference. Relationship discovery only.

Reference: PR-11E §5 specification.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Set, Tuple

from miie.observation_graph.models import (
    RELATIONSHIP_COMMIT_TO_PR,
    RELATIONSHIP_METRIC_CORRELATION,
    RELATIONSHIP_PR_TO_REPO,
    RELATIONSHIP_PROVIDER_HIERARCHY,
    RELATIONSHIP_TEMPORAL_OVERLAP,
    GraphEdge,
    GraphNode,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Temporal overlap threshold: observations within this many hours are
# considered temporally overlapping
TEMPORAL_OVERLAP_HOURS: float = 24.0

# PR source_id prefix used by GitHubPullRequestProvider
_PR_SOURCE_PREFIX: str = "pr-"


# ---------------------------------------------------------------------------
# ObservationCorrelationEngine (PR-11E §5)
# ---------------------------------------------------------------------------


class ObservationCorrelationEngine:
    """PR-11E §5 — Cross-provider relationship discovery engine.

    Identifies related observations across providers, linking:
    - Git commits to GitHub PRs
    - GitHub PRs to repository metadata
    - Observations with temporal overlap
    - Observations for the same source across metrics
    - Observations from the same repository across providers

    No statistical inference is performed. Relationships are discovered
    through metadata matching and temporal analysis.

    Usage::

        engine = ObservationCorrelationEngine()
        edges = engine.discover(nodes)
        graph.add_edges(edges)
    """

    def __init__(
        self,
        temporal_threshold_hours: float = TEMPORAL_OVERLAP_HOURS,
    ) -> None:
        """Initialize the correlation engine.

        Args:
            temporal_threshold_hours: Maximum hours between observations
                to consider them temporally overlapping.
        """
        self._temporal_threshold_hours = temporal_threshold_hours

    @property
    def temporal_threshold_hours(self) -> float:
        """Temporal overlap threshold in hours."""
        return self._temporal_threshold_hours

    # ------------------------------------------------------------------
    # Main Discovery Entry Point
    # ------------------------------------------------------------------

    def discover(self, nodes: List[GraphNode]) -> List[GraphEdge]:
        """Discover all cross-provider relationships among the given nodes.

        Runs all correlation strategies and returns a deduplicated list
        of edges sorted deterministically.

        Args:
            nodes: List of GraphNodes to analyze.

        Returns:
            List of discovered GraphEdges, sorted by edge key.
        """
        if len(nodes) < 2:
            return []

        edges: List[GraphEdge] = []

        # Strategy 1: Commit-to-PR linking
        edges.extend(self._discover_commit_to_pr(nodes))

        # Strategy 2: PR-to-repo linking
        edges.extend(self._discover_pr_to_repo(nodes))

        # Strategy 3: Temporal overlap
        edges.extend(self._discover_temporal_overlap(nodes))

        # Strategy 4: Metric correlation (same source, different metrics)
        edges.extend(self._discover_metric_correlation(nodes))

        # Strategy 5: Provider hierarchy (same repo, different providers)
        edges.extend(self._discover_provider_hierarchy(nodes))

        # Deduplicate by edge key
        deduped = self._deduplicate_edges(edges)

        # Sort deterministically
        return sorted(deduped, key=lambda e: e.edge_key)

    # ------------------------------------------------------------------
    # Strategy 1: Commit-to-PR Linking
    # ------------------------------------------------------------------

    def _discover_commit_to_pr(self, nodes: List[GraphNode]) -> List[GraphEdge]:
        """Link git commits to GitHub PRs.

        A commit is linked to a PR if:
        - The commit source_type is "commit"
        - The PR source_type is "branch" with source_id starting with "pr-"
        - The commit SHA appears in the PR's metadata (merge_commit_sha, head_sha)
        - OR the commit timestamp falls within the PR's created_at to merged_at window

        Args:
            nodes: All graph nodes.

        Returns:
            List of commit_to_pr edges.
        """
        edges: List[GraphEdge] = []

        # Group by provider
        commit_nodes = [n for n in nodes if n.source_type == "commit"]
        pr_nodes = [n for n in nodes if n.source_type == "branch" and n.source_id.startswith(_PR_SOURCE_PREFIX)]

        if not commit_nodes or not pr_nodes:
            return []

        # Build PR lookup by metadata
        pr_by_merge_sha: Dict[str, GraphNode] = {}
        pr_by_head_sha: Dict[str, GraphNode] = {}
        pr_by_time_range: List[Tuple[str, str, GraphNode]] = []

        for pr_node in pr_nodes:
            meta = pr_node.observation.metadata
            merge_sha = meta.get("merge_commit_sha", "")
            head_sha = meta.get("head_sha", "")
            created_at = meta.get("created_at", "")
            merged_at = meta.get("merged_at", "")

            if merge_sha:
                pr_by_merge_sha[merge_sha] = pr_node
            if head_sha:
                pr_by_head_sha[head_sha] = pr_node
            if created_at and merged_at:
                pr_by_time_range.append((created_at, merged_at, pr_node))

        # Match commits to PRs
        for commit_node in commit_nodes:
            commit_sha = commit_node.source_id

            # Direct SHA match (merge commit)
            if commit_sha in pr_by_merge_sha:
                pr_node = pr_by_merge_sha[commit_sha]
                edges.append(
                    GraphEdge(
                        source_observation_id=commit_node.observation_id,
                        target_observation_id=pr_node.observation_id,
                        relationship_type=RELATIONSHIP_COMMIT_TO_PR,
                        confidence=1.0,
                        metadata={"match_type": "merge_commit_sha"},
                    )
                )
                continue

            # Direct SHA match (head commit)
            if commit_sha in pr_by_head_sha:
                pr_node = pr_by_head_sha[commit_sha]
                edges.append(
                    GraphEdge(
                        source_observation_id=commit_node.observation_id,
                        target_observation_id=pr_node.observation_id,
                        relationship_type=RELATIONSHIP_COMMIT_TO_PR,
                        confidence=0.9,
                        metadata={"match_type": "head_sha"},
                    )
                )
                continue

            # Temporal match (commit within PR time range)
            commit_ts = commit_node.timestamp
            for created_at, merged_at, pr_node in pr_by_time_range:
                if created_at <= commit_ts <= merged_at:
                    edges.append(
                        GraphEdge(
                            source_observation_id=commit_node.observation_id,
                            target_observation_id=pr_node.observation_id,
                            relationship_type=RELATIONSHIP_COMMIT_TO_PR,
                            confidence=0.7,
                            metadata={"match_type": "temporal_range"},
                        )
                    )
                    break  # One match per commit

        return edges

    # ------------------------------------------------------------------
    # Strategy 2: PR-to-Repo Linking
    # ------------------------------------------------------------------

    def _discover_pr_to_repo(self, nodes: List[GraphNode]) -> List[GraphEdge]:
        """Link GitHub PRs to repository metadata.

        A PR is linked to repository metadata if both come from the same
        repository (matching repository_id in metadata).

        Args:
            nodes: All graph nodes.

        Returns:
            List of pr_to_repo edges.
        """
        edges: List[GraphEdge] = []

        pr_nodes = [n for n in nodes if n.source_type == "branch" and n.source_id.startswith(_PR_SOURCE_PREFIX)]
        repo_nodes = [n for n in nodes if n.source_type == "branch" and not n.source_id.startswith(_PR_SOURCE_PREFIX)]

        if not pr_nodes or not repo_nodes:
            return []

        # Match by repository_id in metadata
        for pr_node in pr_nodes:
            pr_repo_id = pr_node.observation.metadata.get("repository_id", "")
            if not pr_repo_id:
                continue

            for repo_node in repo_nodes:
                repo_repo_id = repo_node.observation.metadata.get("repository_id", "")
                if pr_repo_id == repo_repo_id:
                    edges.append(
                        GraphEdge(
                            source_observation_id=pr_node.observation_id,
                            target_observation_id=repo_node.observation_id,
                            relationship_type=RELATIONSHIP_PR_TO_REPO,
                            confidence=1.0,
                            metadata={"repository_id": pr_repo_id},
                        )
                    )

        return edges

    # ------------------------------------------------------------------
    # Strategy 3: Temporal Overlap
    # ------------------------------------------------------------------

    def _discover_temporal_overlap(self, nodes: List[GraphNode]) -> List[GraphEdge]:
        """Link observations from different providers that overlap temporally.

        Two observations are temporally overlapping if their timestamps
        are within the configured threshold.

        Args:
            nodes: All graph nodes.

        Returns:
            List of temporal_overlap edges.
        """
        edges: List[GraphEdge] = []

        if len(nodes) < 2:
            return []

        # Group by provider to only cross-provider links
        by_provider: Dict[str, List[GraphNode]] = {}
        for node in nodes:
            if node.provider_id not in by_provider:
                by_provider[node.provider_id] = []
            by_provider[node.provider_id].append(node)

        provider_ids = sorted(by_provider.keys())
        if len(provider_ids) < 2:
            return []

        # Compare across providers
        for i, pid_a in enumerate(provider_ids):
            for pid_b in provider_ids[i + 1 :]:
                for node_a in by_provider[pid_a]:
                    for node_b in by_provider[pid_b]:
                        if self._timestamps_overlap(node_a.timestamp, node_b.timestamp):
                            # Ensure deterministic edge direction
                            if node_a.observation_id < node_b.observation_id:
                                src, tgt = node_a, node_b
                            else:
                                src, tgt = node_b, node_a

                            edges.append(
                                GraphEdge(
                                    source_observation_id=src.observation_id,
                                    target_observation_id=tgt.observation_id,
                                    relationship_type=RELATIONSHIP_TEMPORAL_OVERLAP,
                                    confidence=0.8,
                                    metadata={
                                        "threshold_hours": self._temporal_threshold_hours,
                                    },
                                )
                            )

        return edges

    def _timestamps_overlap(self, ts_a: str, ts_b: str) -> bool:
        """Check if two ISO-8601 timestamps are within the threshold."""
        try:
            from datetime import datetime

            dt_a = datetime.fromisoformat(ts_a.replace("Z", "+00:00"))
            dt_b = datetime.fromisoformat(ts_b.replace("Z", "+00:00"))
            diff_hours = abs((dt_a - dt_b).total_seconds()) / 3600.0
            return diff_hours <= self._temporal_threshold_hours
        except (ValueError, AttributeError):
            return False

    # ------------------------------------------------------------------
    # Strategy 4: Metric Correlation
    # ------------------------------------------------------------------

    def _discover_metric_correlation(self, nodes: List[GraphNode]) -> List[GraphEdge]:
        """Link observations for the same source across different metrics.

        When the same source (source_type + source_id) has observations
        for multiple metrics, those observations are correlated.

        Args:
            nodes: All graph nodes.

        Returns:
            List of metric_correlation edges.
        """
        edges: List[GraphEdge] = []

        # Group by source
        by_source: Dict[Tuple[str, str], List[GraphNode]] = {}
        for node in nodes:
            key = (node.source_type, node.source_id)
            if key not in by_source:
                by_source[key] = []
            by_source[key].append(node)

        # For each source with multiple metrics, create edges
        for source_key, source_nodes in by_source.items():
            if len(source_nodes) < 2:
                continue

            # Group by metric
            by_metric: Dict[str, List[GraphNode]] = {}
            for node in source_nodes:
                if node.metric_id not in by_metric:
                    by_metric[node.metric_id] = []
                by_metric[node.metric_id].append(node)

            if len(by_metric) < 2:
                continue

            # Create edges between different metrics for same source
            metric_ids = sorted(by_metric.keys())
            for i, mid_a in enumerate(metric_ids):
                for mid_b in metric_ids[i + 1 :]:
                    for node_a in by_metric[mid_a]:
                        for node_b in by_metric[mid_b]:
                            # Ensure deterministic direction
                            if node_a.observation_id < node_b.observation_id:
                                src, tgt = node_a, node_b
                            else:
                                src, tgt = node_b, node_a

                            edges.append(
                                GraphEdge(
                                    source_observation_id=src.observation_id,
                                    target_observation_id=tgt.observation_id,
                                    relationship_type=RELATIONSHIP_METRIC_CORRELATION,
                                    confidence=1.0,
                                    metadata={
                                        "source_type": source_key[0],
                                        "source_id": source_key[1],
                                    },
                                )
                            )

        return edges

    # ------------------------------------------------------------------
    # Strategy 5: Provider Hierarchy
    # ------------------------------------------------------------------

    def _discover_provider_hierarchy(self, nodes: List[GraphNode]) -> List[GraphEdge]:
        """Link observations from the same repository across providers.

        When multiple providers contribute observations for the same
        repository, those observations form a provider hierarchy.

        Args:
            nodes: All graph nodes.

        Returns:
            List of provider_hierarchy edges.
        """
        edges: List[GraphEdge] = []

        # Group by repository_id (from metadata)
        by_repo: Dict[str, List[GraphNode]] = {}
        for node in nodes:
            repo_id = node.observation.metadata.get("repository_id", "")
            if repo_id:
                if repo_id not in by_repo:
                    by_repo[repo_id] = []
                by_repo[repo_id].append(node)

        # For each repo with multiple providers, create edges
        for repo_id, repo_nodes in by_repo.items():
            if len(repo_nodes) < 2:
                continue

            # Group by provider
            by_provider: Dict[str, List[GraphNode]] = {}
            for node in repo_nodes:
                if node.provider_id not in by_provider:
                    by_provider[node.provider_id] = []
                by_provider[node.provider_id].append(node)

            if len(by_provider) < 2:
                continue

            # Create edges between providers (one representative per provider)
            provider_ids = sorted(by_provider.keys())
            representatives: List[GraphNode] = []
            for pid in provider_ids:
                # Pick the node with lowest observation_id as representative
                rep = min(by_provider[pid], key=lambda n: n.observation_id)
                representatives.append(rep)

            for i, rep_a in enumerate(representatives):
                for rep_b in representatives[i + 1 :]:
                    if rep_a.observation_id < rep_b.observation_id:
                        src, tgt = rep_a, rep_b
                    else:
                        src, tgt = rep_b, rep_a

                    edges.append(
                        GraphEdge(
                            source_observation_id=src.observation_id,
                            target_observation_id=tgt.observation_id,
                            relationship_type=RELATIONSHIP_PROVIDER_HIERARCHY,
                            confidence=1.0,
                            metadata={"repository_id": repo_id},
                        )
                    )

        return edges

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def _deduplicate_edges(self, edges: List[GraphEdge]) -> List[GraphEdge]:
        """Remove duplicate edges by edge key.

        Preserves the first occurrence.

        Args:
            edges: List of edges to deduplicate.

        Returns:
            Deduplicated list.
        """
        seen: Set[Tuple[str, str, str]] = set()
        deduped: List[GraphEdge] = []

        for edge in edges:
            key = edge.edge_key
            if key not in seen:
                seen.add(key)
                deduped.append(edge)

        return deduped
