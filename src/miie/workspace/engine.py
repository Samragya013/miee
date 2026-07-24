"""Workspace Engine — Persistent scientific analysis workspace.

Manages workspace state after analysis completes. Consumes frozen
scientific core outputs and provides structured access to all analysis
results without re-running any analysis.

All operations are deterministic: same inputs → same outputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..application.workflow import WorkflowResult


@dataclass
class WorkspaceState:
    """Persistent workspace state."""

    workspace_id: str = ""
    created_at: str = ""
    repo_path: str = ""
    repo_id: str = ""

    # Analysis results (frozen scientific outputs)
    repository_context: Optional[Any] = None
    metric_dataframe: Optional[Any] = None
    windows: Optional[Any] = None
    detector_results: Optional[Any] = None
    score_package: Optional[Any] = None
    evidence_package: Optional[Any] = None
    explanation_report: Optional[Any] = None
    workflow_result: Optional[WorkflowResult] = None

    # Configuration used for this analysis
    config: Dict[str, Any] = field(default_factory=dict)

    # Workspace metadata
    total_commits: int = 0
    contributor_count: int = 0
    window_count: int = 0
    metrics_analyzed: List[str] = field(default_factory=list)
    detectors_run: List[str] = field(default_factory=list)

    # Navigation state
    current_section: str = "overview"
    section_history: List[str] = field(default_factory=list)

    # Bookmarks
    bookmarks: List[Dict[str, Any]] = field(default_factory=list)

    # Export history
    export_history: List[Dict[str, Any]] = field(default_factory=list)


class WorkspaceEngine:
    """Persistent scientific analysis workspace.

    After analysis completes, the workspace provides:
    - Executive summary with all key findings
    - Exploration views for each scientific domain
    - Scientific traceability (conclusion → evidence → detector → metric → observation)
    - Deterministic recommendations from scientific outputs
    - Session comparison
    - Export in multiple formats

    The workspace consumes ONLY frozen scientific core outputs.
    """

    def __init__(self) -> None:
        self.state = WorkspaceState()
        self._initialized = False

    def initialize_from_workflow(
        self,
        workflow_result: WorkflowResult,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> None:
        """Initialize workspace from completed workflow results.

        Args:
            workflow_result: The completed workflow result
            context: The workflow context containing all step outputs
            config: The analysis configuration
        """
        import uuid

        self.state.workspace_id = uuid.uuid4().hex[:12]
        self.state.created_at = datetime.now(timezone.utc).isoformat()
        self.state.workflow_result = workflow_result
        self.state.config = dict(config)

        # Extract results from context
        self.state.repository_context = context.get("repository_context")
        self.state.metric_dataframe = context.get("metric_dataframe")
        self.state.windows = context.get("windows")
        self.state.detector_results = context.get("detector_results")
        self.state.score_package = context.get("score_package")
        self.state.evidence_package = context.get("evidence_package")
        self.state.explanation_report = context.get("explanation_report")

        # Extract summary metadata
        repo_ctx = self.state.repository_context
        if repo_ctx is not None:
            self.state.repo_path = getattr(repo_ctx, "local_path", "") or ""
            self.state.repo_id = getattr(repo_ctx, "repo_id", "") or ""
            self.state.total_commits = getattr(repo_ctx, "total_commits", 0) or 0
            self.state.contributor_count = getattr(repo_ctx, "contributor_count", 0) or 0

        if self.state.windows is not None:
            self.state.window_count = len(self.state.windows)

        self.state.metrics_analyzed = list(config.get("metrics", []))
        self.state.detectors_run = list(config.get("detectors", []))

        self.state.current_section = "overview"
        self.state.section_history = []
        self._initialized = True

    def initialize_from_cache(self, cache_data: Dict[str, Any]) -> bool:
        """Initialize workspace from cached results (for session restore).

        Args:
            cache_data: Cached result data from session

        Returns:
            True if initialization succeeded
        """
        import uuid

        try:
            self.state.workspace_id = cache_data.get("workspace_id", uuid.uuid4().hex[:12])
            self.state.created_at = cache_data.get("created_at", datetime.now(timezone.utc).isoformat())
            self.state.repo_path = cache_data.get("repo_path", "")
            self.state.repo_id = cache_data.get("repo_id", "")
            self.state.config = cache_data.get("config", {})
            self.state.total_commits = cache_data.get("total_commits", 0)
            self.state.contributor_count = cache_data.get("contributor_count", 0)
            self.state.window_count = cache_data.get("window_count", 0)
            self.state.metrics_analyzed = cache_data.get("metrics_analyzed", [])
            self.state.detectors_run = cache_data.get("detectors_run", [])

            # Restore full context if available
            full_context = cache_data.get("full_context", {})
            self.state.repository_context = full_context.get("repository_context")
            self.state.metric_dataframe = full_context.get("metric_dataframe")
            self.state.windows = full_context.get("windows")
            self.state.detector_results = full_context.get("detector_results")
            self.state.score_package = full_context.get("score_package")
            self.state.evidence_package = full_context.get("evidence_package")
            self.state.explanation_report = full_context.get("explanation_report")

            self.state.current_section = "overview"
            self._initialized = True
            return True
        except Exception:
            return False

    @property
    def is_initialized(self) -> bool:
        """Check if workspace is initialized."""
        return self._initialized

    def navigate_to(self, section: str) -> bool:
        """Navigate to a workspace section.

        Args:
            section: Section name to navigate to

        Returns:
            True if navigation succeeded
        """
        valid_sections = {
            "overview",
            "repository",
            "metrics",
            "detectors",
            "evidence",
            "confidence",
            "integrity",
            "validation",
            "benchmark",
            "recommendations",
            "traceability",
            "reports",
            "session",
            "export",
        }
        if section not in valid_sections:
            return False

        self.state.section_history.append(self.state.current_section)
        self.state.current_section = section
        return True

    def navigate_back(self) -> bool:
        """Navigate to previous section."""
        if self.state.section_history:
            self.state.current_section = self.state.section_history.pop()
            return True
        return False

    def add_bookmark(self, name: str, section: str, detail: Optional[str] = None) -> None:
        """Add a bookmark to the current view."""
        self.state.bookmarks.append(
            {
                "name": name,
                "section": section,
                "detail": detail,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_bookmarks(self) -> List[Dict[str, Any]]:
        """Get all bookmarks."""
        return list(self.state.bookmarks)

    def remove_bookmark(self, index: int) -> bool:
        """Remove a bookmark by index."""
        if 0 <= index < len(self.state.bookmarks):
            self.state.bookmarks.pop(index)
            return True
        return False

    def add_export_record(self, format_type: str, path: str, sections: List[str]) -> None:
        """Record an export operation."""
        self.state.export_history.append(
            {
                "format": format_type,
                "path": path,
                "sections": sections,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get export history."""
        return list(self.state.export_history)

    def to_cache_data(self) -> Dict[str, Any]:
        """Serialize workspace state for persistence.

        Returns:
            Dict suitable for session caching
        """
        # Serialize scientific objects that may not be JSON-safe
        full_context = {}
        for key in (
            "repository_context",
            "metric_dataframe",
            "windows",
            "detector_results",
            "score_package",
            "evidence_package",
            "explanation_report",
        ):
            value = getattr(self.state, key, None)
            if value is not None:
                try:
                    json.dumps(value, default=str)
                    full_context[key] = value
                except (TypeError, ValueError):
                    full_context[key] = str(value)

        return {
            "workspace_id": self.state.workspace_id,
            "created_at": self.state.created_at,
            "repo_path": self.state.repo_path,
            "repo_id": self.state.repo_id,
            "config": self.state.config,
            "total_commits": self.state.total_commits,
            "contributor_count": self.state.contributor_count,
            "window_count": self.state.window_count,
            "metrics_analyzed": self.state.metrics_analyzed,
            "detectors_run": self.state.detectors_run,
            "bookmarks": self.state.bookmarks,
            "export_history": self.state.export_history,
            "full_context": full_context,
        }
