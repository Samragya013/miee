"""
MIIE v1.6 Repository Observation Graph — Graph Builder.

Builds a RepositoryObservationGraph from multiple ObservationCollections,
handling merging, deduplication, and relationship discovery.

Reference: PR-11E §4 specification.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from miie.observation_graph.correlation import ObservationCorrelationEngine
from miie.observation_graph.graph import RepositoryObservationGraph
from miie.observation_graph.models import GraphDiagnostics
from miie.processing.observation.models import Observation, ObservationCollection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Builder Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphBuilderConfig:
    """Configuration for the observation graph builder.

    Attributes:
        merge_policy: How to resolve duplicate observations
            ('highest_confidence' | 'latest' | 'first').
        deduplicate: Whether to remove duplicate observations.
        discover_relationships: Whether to run the correlation engine.
        temporal_threshold_hours: Threshold for temporal overlap detection.
        enable_diagnostics: Whether to compute diagnostics during build.
    """

    merge_policy: str = "highest_confidence"
    deduplicate: bool = True
    discover_relationships: bool = True
    temporal_threshold_hours: float = 24.0
    enable_diagnostics: bool = True


# ---------------------------------------------------------------------------
# Builder Result
# ---------------------------------------------------------------------------


@dataclass
class GraphBuilderResult:
    """Result of building an observation graph.

    Attributes:
        graph: The built RepositoryObservationGraph.
        diagnostics: Diagnostics from the build process.
        duplicates_removed: Number of duplicate observations removed.
        edges_discovered: Number of relationships discovered.
        warnings: Any warnings from the build process.
        build_time_ms: Wall-clock time for the build.
    """

    graph: RepositoryObservationGraph
    diagnostics: GraphDiagnostics
    duplicates_removed: int = 0
    edges_discovered: int = 0
    warnings: List[str] = field(default_factory=list)
    build_time_ms: float = 0.0


# ---------------------------------------------------------------------------
# ObservationGraphBuilder (PR-11E §4)
# ---------------------------------------------------------------------------


class ObservationGraphBuilder:
    """PR-11E §4 — Builds a RepositoryObservationGraph from collections.

    Supports:
    - Building from multiple ObservationCollections
    - Incremental building (add collections one at a time)
    - Provider merging (combine observations from same provider)
    - Duplicate removal (keep highest confidence)
    - Relationship discovery (cross-provider correlation)
    - Graph diagnostics (statistics at each step)

    Usage::

        builder = ObservationGraphBuilder()
        result = builder.build(
            repository_id="owner/repo",
            analysis_id="analysis-001",
            collections=[git_collection, pr_collection, repo_collection],
        )
        graph = result.graph
    """

    def __init__(
        self,
        config: Optional[GraphBuilderConfig] = None,
    ) -> None:
        """Initialize the graph builder.

        Args:
            config: Optional builder configuration.
        """
        self._config = config or GraphBuilderConfig()
        self._correlation_engine = ObservationCorrelationEngine(
            temporal_threshold_hours=self._config.temporal_threshold_hours,
        )

    @property
    def config(self) -> GraphBuilderConfig:
        """Return the builder configuration."""
        return self._config

    # ------------------------------------------------------------------
    # Build Entry Point
    # ------------------------------------------------------------------

    def build(
        self,
        repository_id: str,
        analysis_id: str,
        collections: List[ObservationCollection],
    ) -> GraphBuilderResult:
        """Build a graph from multiple ObservationCollections.

        This is the main entry point. It:
        1. Creates an empty graph
        2. Flattens all observations from all collections
        3. Merges observations, handling duplicates
        4. Adds observations to the graph
        5. Discovers cross-provider relationships
        6. Validates the graph
        7. Computes diagnostics

        Args:
            repository_id: Repository identifier (e.g., 'owner/repo').
            analysis_id: Analysis run identifier.
            collections: List of ObservationCollections to merge.

        Returns:
            GraphBuilderResult with the built graph and diagnostics.
        """
        start_time = time.monotonic()
        warnings: List[str] = []

        # Create empty graph
        graph = RepositoryObservationGraph(
            repository_id=repository_id,
            analysis_id=analysis_id,
        )

        if not collections:
            diagnostics = graph.get_diagnostics()
            return GraphBuilderResult(
                graph=graph,
                diagnostics=diagnostics,
                warnings=["No collections provided"],
                build_time_ms=(time.monotonic() - start_time) * 1000.0,
            )

        # Flatten and merge observations
        all_observations, duplicates_removed = self._merge_observations(collections)
        if duplicates_removed > 0:
            warnings.append(f"Removed {duplicates_removed} duplicate observations")

        # Add observations to graph
        self._add_observations_to_graph(graph, all_observations)

        # Discover relationships
        edges_discovered = 0
        if self._config.discover_relationships:
            edges_discovered = self._discover_and_add_edges(graph)

        # Compute diagnostics
        diagnostics = graph.get_diagnostics() if self._config.enable_diagnostics else GraphDiagnostics()
        diagnostics.duplicate_count = duplicates_removed

        build_time_ms = (time.monotonic() - start_time) * 1000.0

        return GraphBuilderResult(
            graph=graph,
            diagnostics=diagnostics,
            duplicates_removed=duplicates_removed,
            edges_discovered=edges_discovered,
            warnings=warnings,
            build_time_ms=build_time_ms,
        )

    # ------------------------------------------------------------------
    # Incremental Building
    # ------------------------------------------------------------------

    def add_collection(
        self,
        graph: RepositoryObservationGraph,
        collection: ObservationCollection,
    ) -> Tuple[int, int]:
        """Add a single collection to an existing graph (incremental build).

        Args:
            graph: The graph to add to.
            collection: The ObservationCollection to add.

        Returns:
            Tuple of (observations_added, duplicates_skipped).
        """
        added = 0
        skipped = 0

        for window in collection.windows:
            for obs in window.observations:
                if graph.add_observation(obs, provider_id=self._extract_provider_id(obs)):
                    added += 1
                else:
                    skipped += 1

        return added, skipped

    def _extract_provider_id(self, obs: Observation) -> str:
        """Extract provider_id from observation provenance."""
        return obs.provenance.extractor_id

    # ------------------------------------------------------------------
    # Merge Observations
    # ------------------------------------------------------------------

    def _merge_observations(
        self,
        collections: List[ObservationCollection],
    ) -> Tuple[List[Observation], int]:
        """Flatten and merge observations from all collections.

        Applies merge policy to resolve duplicates.

        Args:
            collections: List of ObservationCollections.

        Returns:
            Tuple of (merged observations, duplicates removed).
        """
        # Flatten all observations
        all_observations: List[Observation] = []
        for collection in collections:
            for window in collection.windows:
                all_observations.extend(window.observations)

        if self._config.deduplicate:
            return self._deduplicate_with_policy(all_observations)

        return all_observations, 0

    def _deduplicate_with_policy(
        self,
        observations: List[Observation],
    ) -> Tuple[List[Observation], int]:
        """Remove duplicates according to the merge policy.

        Args:
            observations: All observations (may contain duplicates).

        Returns:
            Tuple of (deduplicated observations, count removed).
        """
        # Group by observation_id
        by_id: Dict[str, List[Observation]] = {}
        for obs in observations:
            if obs.observation_id not in by_id:
                by_id[obs.observation_id] = []
            by_id[obs.observation_id].append(obs)

        # Apply merge policy
        merged: List[Observation] = []
        total_removed = 0

        for obs_id in sorted(by_id.keys()):
            candidates = by_id[obs_id]
            if len(candidates) == 1:
                merged.append(candidates[0])
            else:
                winner = self._select_winner(candidates)
                merged.append(winner)
                total_removed += len(candidates) - 1

        return merged, total_removed

    def _select_winner(self, candidates: List[Observation]) -> Observation:
        """Select the winning observation from duplicates.

        Args:
            candidates: List of observations with the same ID.

        Returns:
            The winning observation.
        """
        if self._config.merge_policy == "highest_confidence":
            # Quality-based selection: complete > estimated > derived > missing
            quality_order = {"complete": 0, "estimated": 1, "derived": 2, "missing": 3}
            return min(
                candidates,
                key=lambda obs: (
                    quality_order.get(obs.quality, 4),
                    obs.observation_id,  # Tiebreak by ID
                ),
            )
        elif self._config.merge_policy == "latest":
            return max(candidates, key=lambda obs: obs.timestamp)
        else:  # "first"
            return candidates[0]

    # ------------------------------------------------------------------
    # Add Observations to Graph
    # ------------------------------------------------------------------

    def _add_observations_to_graph(
        self,
        graph: RepositoryObservationGraph,
        observations: List[Observation],
    ) -> None:
        """Add all observations to the graph.

        Args:
            graph: The graph to add to.
            observations: Observations to add.
        """
        for obs in observations:
            provider_id = self._extract_provider_id(obs)
            graph.add_observation(obs, provider_id)

    # ------------------------------------------------------------------
    # Relationship Discovery
    # ------------------------------------------------------------------

    def _discover_and_add_edges(
        self,
        graph: RepositoryObservationGraph,
    ) -> int:
        """Discover relationships and add edges to the graph.

        Args:
            graph: The graph to add edges to.

        Returns:
            Number of edges discovered and added.
        """
        nodes = graph.get_all_nodes()
        edges = self._correlation_engine.discover(nodes)
        return graph.add_edges(edges)
