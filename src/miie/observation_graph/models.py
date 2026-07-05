"""
MIIE v1.6 Repository Observation Graph — Supporting Data Models.

Defines the node, edge, and index structures for the unified observation
graph that organizes observations from every provider into one coherent,
deterministic, traceable structure.

Reference: PR-11E specification.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

from miie.processing.observation.models import Observation

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRAPH_VERSION: str = "1.0.0"


# ---------------------------------------------------------------------------
# Graph Node (ODSS §9 wrapper)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphNode:
    """A node in the observation graph wrapping an Observation.

    Adds provider context and query-friendly fields while preserving
    the original immutable Observation.

    Attributes:
        observation: The original Observation dataclass.
        provider_id: Identifier of the provider that produced this observation.
        metric_id: Metric identifier (M-01 .. M-07), cached for indexing.
        source_type: Source type (commit, file, branch, tag), cached for indexing.
        source_id: Source identifier, cached for indexing.
        timestamp: ISO-8601 timestamp, cached for indexing.
    """

    observation: Observation
    provider_id: str
    metric_id: str
    source_type: str
    source_id: str
    timestamp: str

    @property
    def observation_id(self) -> str:
        """Observation ID (delegated to wrapped observation)."""
        return self.observation.observation_id

    @property
    def value(self) -> float:
        """Numeric value (delegated to wrapped observation)."""
        return self.observation.value

    @property
    def quality(self) -> str:
        """Quality indicator (delegated to wrapped observation)."""
        return self.observation.quality

    @property
    def unit(self) -> str:
        """Unit of measurement (delegated to wrapped observation)."""
        return self.observation.unit


# ---------------------------------------------------------------------------
# Graph Edge (Cross-provider relationships)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphEdge:
    """A directed edge between two observations in the graph.

    Represents a discovered relationship between observations, potentially
    across different providers. Edges are immutable after creation.

    Attributes:
        source_observation_id: ID of the source observation.
        target_observation_id: ID of the target observation.
        relationship_type: Type of relationship (e.g., 'commit_to_pr').
        confidence: Confidence in this relationship (0.0 - 1.0).
        metadata: Additional context about the relationship.
    """

    source_observation_id: str
    target_observation_id: str
    relationship_type: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate edge constraints."""
        if not self.source_observation_id:
            raise ValueError("source_observation_id must not be empty")
        if not self.target_observation_id:
            raise ValueError("target_observation_id must not be empty")
        if self.source_observation_id == self.target_observation_id:
            raise ValueError("self-referencing edges are not allowed")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")
        if not self.relationship_type:
            raise ValueError("relationship_type must not be empty")

    @property
    def edge_key(self) -> Tuple[str, str, str]:
        """Deterministic key for this edge."""
        return (
            self.source_observation_id,
            self.target_observation_id,
            self.relationship_type,
        )


# ---------------------------------------------------------------------------
# Relationship Type Constants
# ---------------------------------------------------------------------------

# Cross-provider relationship types discovered by the correlation engine
RELATIONSHIP_COMMIT_TO_PR: str = "commit_to_pr"
RELATIONSHIP_PR_TO_REPO: str = "pr_to_repo"
RELATIONSHIP_TEMPORAL_OVERLAP: str = "temporal_overlap"
RELATIONSHIP_METRIC_CORRELATION: str = "metric_correlation"
RELATIONSHIP_PROVIDER_HIERARCHY: str = "provider_hierarchy"

# All valid relationship types
VALID_RELATIONSHIP_TYPES: FrozenSet[str] = frozenset(
    {
        RELATIONSHIP_COMMIT_TO_PR,
        RELATIONSHIP_PR_TO_REPO,
        RELATIONSHIP_TEMPORAL_OVERLAP,
        RELATIONSHIP_METRIC_CORRELATION,
        RELATIONSHIP_PROVIDER_HIERARCHY,
    }
)


# ---------------------------------------------------------------------------
# Graph Index (Efficient query structure)
# ---------------------------------------------------------------------------


@dataclass
class GraphIndex:
    """Internal index for efficient graph queries.

    Maintains multiple views of the graph data for O(1) or O(log n) lookups.
    Indices are rebuilt when the graph changes.

    Attributes:
        by_observation_id: Map from observation_id to GraphNode.
        by_metric_id: Map from metric_id to list of GraphNodes.
        by_provider_id: Map from provider_id to list of GraphNodes.
        by_source: Map from (source_type, source_id) to list of GraphNodes.
        by_timestamp: All nodes sorted by timestamp (ISO-8601 string sort).
        edges_by_source: Map from source_observation_id to list of GraphEdges.
        edges_by_target: Map from target_observation_id to list of GraphEdges.
    """

    by_observation_id: Dict[str, GraphNode] = field(default_factory=dict)
    by_metric_id: Dict[str, List[GraphNode]] = field(default_factory=dict)
    by_provider_id: Dict[str, List[GraphNode]] = field(default_factory=dict)
    by_source: Dict[Tuple[str, str], List[GraphNode]] = field(default_factory=dict)
    by_timestamp: List[GraphNode] = field(default_factory=list)
    edges_by_source: Dict[str, List[GraphEdge]] = field(default_factory=dict)
    edges_by_target: Dict[str, List[GraphEdge]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Graph Diagnostics
# ---------------------------------------------------------------------------


@dataclass
class GraphDiagnostics:
    """Diagnostics snapshot from graph construction or validation.

    Tracks comprehensive statistics about the graph structure,
    provider contributions, and relationship discovery.
    """

    total_nodes: int = 0
    total_edges: int = 0
    providers: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    sources: List[Tuple[str, str]] = field(default_factory=list)
    duplicate_count: int = 0
    orphan_count: int = 0
    relationship_counts: Dict[str, int] = field(default_factory=dict)
    coverage: Dict[str, Dict[str, int]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    graph_id: str = ""
    schema_version: str = GRAPH_VERSION

    @property
    def completeness(self) -> float:
        """Graph completeness as a ratio of edges to possible edges.

        Returns 0.0 for single-node graphs, ratio for multi-node graphs.
        """
        if self.total_nodes < 2:
            return 1.0
        max_edges = self.total_nodes * (self.total_nodes - 1)
        return self.total_edges / max_edges if max_edges > 0 else 0.0

    @property
    def provider_count(self) -> int:
        """Number of distinct providers."""
        return len(self.providers)

    @property
    def metric_count(self) -> int:
        """Number of distinct metrics."""
        return len(self.metrics)

    @property
    def orphan_ratio(self) -> float:
        """Ratio of orphaned nodes to total nodes."""
        if self.total_nodes == 0:
            return 0.0
        return self.orphan_count / self.total_nodes


# ---------------------------------------------------------------------------
# Validation Result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphValidationResult:
    """Result of graph validation.

    Attributes:
        is_valid: Whether the graph passed all validation checks.
        violations: List of validation errors (must-fix).
        warnings: List of validation warnings (informational).
        diagnostics: Graph diagnostics at validation time.
    """

    is_valid: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    diagnostics: Optional[GraphDiagnostics] = None

    @classmethod
    def success(cls, diagnostics: Optional[GraphDiagnostics] = None) -> GraphValidationResult:
        """Create a successful validation result."""
        return cls(is_valid=True, diagnostics=diagnostics)

    @classmethod
    def failure(
        cls,
        violations: List[str],
        diagnostics: Optional[GraphDiagnostics] = None,
    ) -> GraphValidationResult:
        """Create a failed validation result."""
        return cls(is_valid=False, violations=violations, diagnostics=diagnostics)


# ---------------------------------------------------------------------------
# Serialization Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SerializedNode:
    """JSON-serializable node representation."""

    observation_id: str
    provider_id: str
    metric_id: str
    source_type: str
    source_id: str
    timestamp: str
    value: float
    unit: str
    quality: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SerializedEdge:
    """JSON-serializable edge representation."""

    source_observation_id: str
    target_observation_id: str
    relationship_type: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SerializedGraph:
    """JSON-serializable graph representation."""

    graph_id: str
    repository_id: str
    analysis_id: str
    schema_version: str
    nodes: Tuple[SerializedNode, ...]
    edges: Tuple[SerializedEdge, ...]
    diagnostics: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Graph ID Generation
# ---------------------------------------------------------------------------


def generate_graph_id(repository_id: str, analysis_id: str) -> str:
    """Compute a deterministic 16-character hex graph ID.

    Formula:
        graph_id = sha256(f"rog:{repository_id}:{analysis_id}")[:16]

    Args:
        repository_id: Repository identifier (e.g., 'owner/repo').
        analysis_id: Analysis run identifier.

    Returns:
        16-character lowercase hex string.
    """
    if not repository_id:
        raise ValueError("repository_id must not be empty")
    if not analysis_id:
        raise ValueError("analysis_id must not be empty")
    payload = f"rog:{repository_id}:{analysis_id}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
