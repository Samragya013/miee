"""
MIIE v1.6 Scientific Metric Completion Framework — Registry.

Manages registration, lookup, dependency resolution, and execution
ordering for metric computers.

Reference: PR-12 specification.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Dict, List

from miie.metrics.contracts import MetricComputer
from miie.metrics.models import MetricDefinition

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Registry Errors
# ---------------------------------------------------------------------------


class MetricRegistrationError(Exception):
    """Raised when metric registration fails."""


class MetricNotFoundError(Exception):
    """Raised when a requested metric is not registered."""


class CyclicDependencyError(Exception):
    """Raised when metric dependencies form a cycle."""


# ---------------------------------------------------------------------------
# Metric Registry
# ---------------------------------------------------------------------------


class MetricRegistry:
    """Central registry for metric computers.

    Provides registration, lookup, dependency resolution, execution
    ordering, and validation of the metric computation pipeline.

    The registry is the single source of truth for which metrics exist,
    how they depend on each other, and in what order they must execute.
    """

    def __init__(self) -> None:
        self._computers: Dict[str, MetricComputer] = {}
        self._definitions: Dict[str, MetricDefinition] = {}
        self._version: str = "1.0.0"

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, computer: MetricComputer) -> None:
        """Register a metric computer.

        Args:
            computer: The MetricComputer implementation.

        Raises:
            MetricRegistrationError: If registration fails (duplicate, bad definition).
        """
        definition = computer.metric_definition
        metric_id = definition.metric_id

        if metric_id in self._computers:
            raise MetricRegistrationError(f"Metric {metric_id} already registered")

        if metric_id not in {f"M-{i:02d}" for i in range(1, 8)}:
            raise MetricRegistrationError(f"Invalid metric ID: {metric_id}. Expected M-01 through M-07.")

        if definition.aggregation not in ("sum", "mean"):
            raise MetricRegistrationError(
                f"Invalid aggregation '{definition.aggregation}' for {metric_id}. " f"Expected 'sum' or 'mean'."
            )

        self._computers[metric_id] = computer
        self._definitions[metric_id] = definition
        logger.info("Registered metric computer: %s (%s)", metric_id, definition.name)

    def register_all(self, computers: List[MetricComputer]) -> None:
        """Register multiple metric computers.

        Args:
            computers: List of MetricComputer implementations.

        Raises:
            MetricRegistrationError: If any registration fails.
        """
        for computer in computers:
            self.register(computer)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_computer(self, metric_id: str) -> MetricComputer:
        """Get the computer for a metric.

        Args:
            metric_id: Metric identifier (e.g. "M-01").

        Returns:
            The MetricComputer implementation.

        Raises:
            MetricNotFoundError: If metric is not registered.
        """
        if metric_id not in self._computers:
            raise MetricNotFoundError(f"Metric {metric_id} not registered")
        return self._computers[metric_id]

    def get_definition(self, metric_id: str) -> MetricDefinition:
        """Get the definition for a metric.

        Args:
            metric_id: Metric identifier.

        Returns:
            The MetricDefinition.

        Raises:
            MetricNotFoundError: If metric is not registered.
        """
        if metric_id not in self._definitions:
            raise MetricNotFoundError(f"Metric {metric_id} not registered")
        return self._definitions[metric_id]

    def has_metric(self, metric_id: str) -> bool:
        """Check if a metric is registered."""
        return metric_id in self._computers

    def registered_ids(self) -> List[str]:
        """Return sorted list of registered metric IDs."""
        return sorted(self._computers.keys())

    def registered_count(self) -> int:
        """Return number of registered metrics."""
        return len(self._computers)

    # ------------------------------------------------------------------
    # Dependency Resolution
    # ------------------------------------------------------------------

    def dependency_graph(self) -> Dict[str, List[str]]:
        """Return the dependency graph for all registered metrics.

        Returns:
            Dict mapping metric_id to list of dependency metric_ids.
        """
        graph: Dict[str, List[str]] = {}
        for metric_id, definition in self._definitions.items():
            graph[metric_id] = list(definition.dependencies)
        return graph

    def execution_order(self) -> List[str]:
        """Compute topological execution order for registered metrics.

        Uses Kahn's algorithm for topological sorting.

        Returns:
            List of metric IDs in dependency-safe execution order.

        Raises:
            CyclicDependencyError: If dependencies form a cycle.
        """
        graph = self.dependency_graph()
        all_metrics = set(graph.keys())

        # Build in-degree map
        in_degree: Dict[str, int] = {m: 0 for m in all_metrics}
        dependents: Dict[str, List[str]] = defaultdict(list)

        for metric_id, deps in graph.items():
            for dep in deps:
                if dep in all_metrics:
                    in_degree[metric_id] += 1
                    dependents[dep].append(metric_id)

        # Start with metrics that have no dependencies
        queue: deque[str] = deque(sorted(mid for mid, deg in in_degree.items() if deg == 0))
        order: List[str] = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for dependent in sorted(dependents[current]):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(all_metrics):
            missing = all_metrics - set(order)
            raise CyclicDependencyError(f"Cyclic dependency detected among metrics: {sorted(missing)}")

        return order

    def missing_dependencies(self) -> Dict[str, List[str]]:
        """Find dependencies that are not registered.

        Returns:
            Dict mapping metric_id to list of unregistered dependency IDs.
        """
        all_registered = set(self._definitions.keys())
        missing: Dict[str, List[str]] = {}

        for metric_id, definition in self._definitions.items():
            unregistered = [d for d in definition.dependencies if d not in all_registered]
            if unregistered:
                missing[metric_id] = unregistered

        return missing

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_registry(self) -> List[str]:
        """Validate the registry state.

        Returns:
            List of error messages (empty if valid).
        """
        errors: List[str] = []

        # Check all 7 metrics registered
        expected = {f"M-{i:02d}" for i in range(1, 8)}
        registered = set(self._definitions.keys())
        missing = expected - registered
        if missing:
            errors.append(f"Missing metrics: {sorted(missing)}")

        # Check dependency validity
        all_ids = set(self._definitions.keys())
        for metric_id, definition in self._definitions.items():
            for dep in definition.dependencies:
                if dep not in all_ids:
                    errors.append(f"{metric_id} depends on unregistered metric {dep}")

        # Check no self-dependencies
        for metric_id, definition in self._definitions.items():
            if metric_id in definition.dependencies:
                errors.append(f"{metric_id} has self-dependency")

        return errors

    # ------------------------------------------------------------------
    # Version
    # ------------------------------------------------------------------

    @property
    def version(self) -> str:
        """Registry version."""
        return self._version

    def __len__(self) -> int:
        return len(self._computers)

    def __contains__(self, metric_id: str) -> bool:
        return metric_id in self._computers
