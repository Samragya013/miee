"""
MIIE v1.6 Repository Observation Graph — Unified Observation Graph.

Provides a coherent, deterministic, traceable structure that organizes
observations from every provider into a single graph consumed by
sampling, windowing, detectors, evidence, scoring, and reporting.

Modules:
    models: GraphNode, GraphEdge, GraphIndex, GraphDiagnostics
    graph: RepositoryObservationGraph
    builder: ObservationGraphBuilder
    correlation: ObservationCorrelationEngine
    validation: GraphValidator
    serialization: GraphSerializer
    diagnostics: GraphDiagnosticsEngine
    state: GraphSnapshot, GraphEvent, GraphVersion, WorkingGraph, GraphStateManager

Reference: PR-11E specification.
SR-04: Unified State Model for Graph Immutability Resolution.
"""

from miie.observation_graph.builder import (
    GraphBuilderConfig,
    GraphBuilderResult,
    ObservationGraphBuilder,
)
from miie.observation_graph.correlation import ObservationCorrelationEngine
from miie.observation_graph.diagnostics import GraphDiagnosticsEngine
from miie.observation_graph.graph import RepositoryObservationGraph
from miie.observation_graph.models import (
    GRAPH_VERSION,
    RELATIONSHIP_COMMIT_TO_PR,
    RELATIONSHIP_METRIC_CORRELATION,
    RELATIONSHIP_PR_TO_REPO,
    RELATIONSHIP_PROVIDER_HIERARCHY,
    RELATIONSHIP_TEMPORAL_OVERLAP,
    VALID_RELATIONSHIP_TYPES,
    GraphDiagnostics,
    GraphEdge,
    GraphIndex,
    GraphNode,
    GraphValidationResult,
    SerializedEdge,
    SerializedGraph,
    SerializedNode,
    generate_graph_id,
)
from miie.observation_graph.serialization import GraphSerializer
from miie.observation_graph.state import (
    GraphEvent,
    GraphSnapshot,
    GraphStateManager,
    GraphVersion,
    StateType,
    WorkingGraph,
)
from miie.observation_graph.validation import GraphValidator

__all__ = [
    # Version
    "GRAPH_VERSION",
    # Constants
    "RELATIONSHIP_COMMIT_TO_PR",
    "RELATIONSHIP_PR_TO_REPO",
    "RELATIONSHIP_TEMPORAL_OVERLAP",
    "RELATIONSHIP_METRIC_CORRELATION",
    "RELATIONSHIP_PROVIDER_HIERARCHY",
    "VALID_RELATIONSHIP_TYPES",
    # Models
    "GraphNode",
    "GraphEdge",
    "GraphIndex",
    "GraphDiagnostics",
    "GraphValidationResult",
    "SerializedNode",
    "SerializedEdge",
    "SerializedGraph",
    "generate_graph_id",
    # Core
    "RepositoryObservationGraph",
    # Builder
    "GraphBuilderConfig",
    "GraphBuilderResult",
    "ObservationGraphBuilder",
    # Correlation
    "ObservationCorrelationEngine",
    # Validation
    "GraphValidator",
    # Serialization
    "GraphSerializer",
    # Diagnostics
    "GraphDiagnosticsEngine",
    # SR-04: State Model
    "StateType",
    "GraphSnapshot",
    "GraphEvent",
    "GraphVersion",
    "WorkingGraph",
    "GraphStateManager",
]
