"""
MIIE v1.6 Scientific Metric Completion Framework — Diagnostics.

Reports metric coverage, missing observations, derived metrics,
confidence, uncertainty, execution time, and dependency graph.

Reference: PR-12 specification.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from miie.metrics.models import (
    ComputationDiagnostics,
    MetricCollection,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Diagnostics Engine
# ---------------------------------------------------------------------------


class MetricDiagnosticsEngine:
    """Collects and reports diagnostics during metric computation.

    Tracks observation counts, computation times, validation failures,
    and produces summary reports.
    """

    def __init__(self) -> None:
        self._total_observations: int = 0
        self._by_metric: Dict[str, int] = {}
        self._by_provider: Dict[str, int] = {}
        self._validation_failures: List[str] = []
        self._computation_times_ms: Dict[str, float] = {}
        self._warnings: List[str] = []
        self._timers: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_observation_count(
        self,
        metric_id: str,
        count: int,
    ) -> None:
        """Record observation count for a metric."""
        self._by_metric[metric_id] = count
        self._total_observations += count

    def record_provider_count(
        self,
        provider_id: str,
        count: int,
    ) -> None:
        """Record observation count for a provider."""
        self._by_provider[provider_id] = count

    def record_computation_time(
        self,
        metric_id: str,
        time_ms: float,
    ) -> None:
        """Record computation time for a metric."""
        self._computation_times_ms[metric_id] = time_ms

    def record_validation_failure(
        self,
        message: str,
    ) -> None:
        """Record a validation failure."""
        self._validation_failures.append(message)

    def record_warning(
        self,
        message: str,
    ) -> None:
        """Record a warning."""
        self._warnings.append(message)

    def start_timer(self, metric_id: str) -> None:
        """Start a computation timer."""
        self._timers[metric_id] = time.perf_counter()

    def stop_timer(self, metric_id: str) -> float:
        """Stop a computation timer and record elapsed time.

        Returns:
            Elapsed time in milliseconds.
        """
        if metric_id not in self._timers:
            return 0.0
        elapsed_ms = (time.perf_counter() - self._timers.pop(metric_id)) * 1000.0
        self._computation_times_ms[metric_id] = elapsed_ms
        return elapsed_ms

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def coverage_report(
        self,
        collection: MetricCollection,
    ) -> Dict[str, Any]:
        """Generate a coverage report for a metric collection.

        Args:
            collection: The MetricCollection to analyze.

        Returns:
            Dict with coverage metrics.
        """
        expected = set(f"M-{i:02d}" for i in range(1, 8))
        computed = set(collection.results.keys())
        missing = sorted(expected - computed)
        present = sorted(expected & computed)

        confidences = {mid: collection.results[mid].confidence for mid in present}
        avg_confidence = sum(confidences.values()) / len(confidences) if confidences else 0.0

        return {
            "expected_metrics": sorted(expected),
            "computed_metrics": present,
            "missing_metrics": missing,
            "coverage_fraction": len(computed) / len(expected),
            "coverage_percent": 100.0 * len(computed) / len(expected),
            "confidences": confidences,
            "average_confidence": avg_confidence,
            "overall_confidence": collection.overall_confidence,
        }

    def missing_observations_report(
        self,
        observations_by_metric: Dict[str, int],
    ) -> Dict[str, Any]:
        """Report on missing or insufficient observations.

        Args:
            observations_by_metric: Count of observations per metric.

        Returns:
            Dict with missing observation analysis.
        """
        expected_min = {
            "M-01": 1,
            "M-02": 1,
            "M-03": 5,
            "M-04": 1,
            "M-05": 2,
            "M-06": 1,
            "M-07": 1,
        }
        insufficient = {}
        adequate = {}

        for metric_id, min_count in expected_min.items():
            actual = observations_by_metric.get(metric_id, 0)
            if actual < min_count:
                insufficient[metric_id] = {
                    "actual": actual,
                    "required": min_count,
                    "deficit": min_count - actual,
                }
            else:
                adequate[metric_id] = actual

        return {
            "total_metrics": 7,
            "adequate_count": len(adequate),
            "insufficient_count": len(insufficient),
            "adequate": adequate,
            "insufficient": insufficient,
        }

    def confidence_report(
        self,
        collection: MetricCollection,
    ) -> Dict[str, Any]:
        """Generate a confidence report.

        Args:
            collection: The MetricCollection to analyze.

        Returns:
            Dict with confidence analysis.
        """
        high = []
        medium = []
        low = []

        for mid, result in collection.results.items():
            entry = {
                "metric_id": mid,
                "confidence": result.confidence,
                "observation_count": result.observation_count,
                "uncertainty": result.uncertainty,
            }
            if result.confidence >= 0.8:
                high.append(entry)
            elif result.confidence >= 0.5:
                medium.append(entry)
            else:
                low.append(entry)

        return {
            "high_confidence": high,
            "medium_confidence": medium,
            "low_confidence": low,
            "high_count": len(high),
            "medium_count": len(medium),
            "low_count": len(low),
            "overall": collection.overall_confidence,
        }

    def dependency_graph_report(
        self,
        dependency_graph: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Report on the metric dependency graph.

        Args:
            dependency_graph: Dict mapping metric_id to dependency list.

        Returns:
            Dict with dependency analysis.
        """
        roots = [mid for mid, deps in dependency_graph.items() if not deps]
        leaves = [mid for mid in dependency_graph if mid not in {d for deps in dependency_graph.values() for d in deps}]
        max_depth = self._max_depth(dependency_graph)

        return {
            "metrics": sorted(dependency_graph.keys()),
            "roots": sorted(roots),
            "leaves": sorted(leaves),
            "total_edges": sum(len(deps) for deps in dependency_graph.values()),
            "max_depth": max_depth,
        }

    def execution_time_report(self) -> Dict[str, Any]:
        """Report on computation times.

        Returns:
            Dict with timing analysis.
        """
        if not self._computation_times_ms:
            return {"total_ms": 0.0, "per_metric": {}, "slowest": None}

        total = sum(self._computation_times_ms.values())
        slowest = max(self._computation_times_ms, key=self._computation_times_ms.get)

        return {
            "total_ms": total,
            "per_metric": dict(self._computation_times_ms),
            "slowest": slowest,
            "slowest_ms": self._computation_times_ms[slowest],
        }

    def full_diagnostics(
        self,
        collection: MetricCollection,
        dependency_graph: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete diagnostics report.

        Args:
            collection: The MetricCollection to analyze.
            dependency_graph: Optional dependency graph.

        Returns:
            Dict with all diagnostics.
        """
        report: Dict[str, Any] = {
            "coverage": self.coverage_report(collection),
            "confidence": self.confidence_report(collection),
            "execution_time": self.execution_time_report(),
            "validation_failures": self._validation_failures,
            "warnings": self._warnings,
        }

        if dependency_graph:
            report["dependency_graph"] = self.dependency_graph_report(dependency_graph)

        return report

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _max_depth(self, graph: Dict[str, List[str]]) -> int:
        """Compute maximum dependency depth via DFS."""
        memo: Dict[str, int] = {}

        def depth(metric_id: str) -> int:
            if metric_id in memo:
                return memo[metric_id]
            deps = graph.get(metric_id, [])
            valid_deps = [d for d in deps if d in graph]
            if not valid_deps:
                memo[metric_id] = 0
                return 0
            result = 1 + max(depth(d) for d in valid_deps)
            memo[metric_id] = result
            return result

        for mid in graph:
            depth(mid)

        return max(memo.values()) if memo else 0

    def to_diagnostics(self) -> ComputationDiagnostics:
        """Convert to ComputationDiagnostics model."""
        return ComputationDiagnostics(
            total_observations_processed=self._total_observations,
            observations_by_metric=dict(self._by_metric),
            observations_by_provider=dict(self._by_provider),
            validation_failures=list(self._validation_failures),
            computation_times_ms=dict(self._computation_times_ms),
            warnings=list(self._warnings),
        )
