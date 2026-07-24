"""MIIE Scientific Workspace — Persistent analysis environment.

Provides a deterministic workspace that remains after analysis completes,
allowing users to explore, explain, validate, compare, and export results
without re-running the analysis.

The workspace consumes ONLY the frozen scientific core outputs.
No scientific logic is introduced.
"""

from .comparison import ComparisonEngine
from .engine import WorkspaceEngine
from .export import WorkspaceExporter
from .persistence import WorkspacePersistence
from .recommendations import RecommendationEngine
from .traceability import TraceabilityChain
from .views import (
    AssuranceView,
    BenchmarkView,
    ConfidenceView,
    DetectorView,
    DiagnosticsView,
    EvidenceView,
    ExecutiveSummary,
    ExplorationView,
    IntegrityView,
    MetricView,
    RecommendationView,
    SessionInfoView,
    ValidationView,
)

__all__ = [
    "WorkspaceEngine",
    "ExecutiveSummary",
    "ExplorationView",
    "MetricView",
    "DetectorView",
    "EvidenceView",
    "ConfidenceView",
    "IntegrityView",
    "ValidationView",
    "DiagnosticsView",
    "AssuranceView",
    "BenchmarkView",
    "RecommendationView",
    "SessionInfoView",
    "TraceabilityChain",
    "RecommendationEngine",
    "ComparisonEngine",
    "WorkspacePersistence",
    "WorkspaceExporter",
]
