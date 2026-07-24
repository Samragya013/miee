"""
MIIE v1.6 Scientific Metric Completion Framework — Metric Engine.

Orchestrates metric computation from the Observation Graph.
Consumes RepositoryObservationGraph, produces MetricCollection.

Reference: PR-12 specification.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from miie.metrics.computation import create_all_computers
from miie.metrics.diagnostics import MetricDiagnosticsEngine
from miie.metrics.models import (
    MetricCollection,
    MetricResult,
    ObservationInput,
    generate_metric_collection_id,
)
from miie.metrics.registry import MetricRegistry
from miie.metrics.validation import MetricCollectionValidator, ObservationValidator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Metric Engine
# ---------------------------------------------------------------------------


class MetricEngine:
    """Orchestrates the full metric computation pipeline.

    Pipeline:
    1. Extract observations from ROG (or ObservationCollection)
    2. Group observations by metric_id
    3. Validate observations per metric
    4. Execute metric computers in dependency order
    5. Validate results
    6. Assemble MetricCollection
    7. Run diagnostics

    The engine is deterministic: same inputs always produce same outputs.
    """

    EXPECTED_METRICS = tuple(f"M-{i:02d}" for i in range(1, 8))

    def __init__(
        self,
        registry: Optional[MetricRegistry] = None,
    ) -> None:
        """Initialize the metric engine.

        Args:
            registry: Optional pre-configured registry. If None, creates
                      a default registry with all 7 metric computers.
        """
        if registry is None:
            self._registry = MetricRegistry()
            self._registry.register_all(create_all_computers())
        else:
            self._registry = registry

        self._obs_validator = ObservationValidator()
        self._collection_validator = MetricCollectionValidator()
        self._diagnostics = MetricDiagnosticsEngine()

    # ------------------------------------------------------------------
    # Primary Interface
    # ------------------------------------------------------------------

    def compute_from_graph(
        self,
        graph: Any,
        repository_id: str,
        analysis_id: str,
    ) -> MetricCollection:
        """Compute metrics from a RepositoryObservationGraph.

        Args:
            graph: RepositoryObservationGraph instance.
            repository_id: Repository identifier.
            analysis_id: Analysis run identifier.

        Returns:
            MetricCollection with all computed metrics.
        """
        observations = graph.get_all_observations()
        inputs = self._observations_to_inputs(observations, graph)
        return self._compute_metrics(inputs, repository_id, analysis_id)

    def compute_from_observations(
        self,
        observations: List[Any],
        provider_map: Optional[Dict[str, str]] = None,
        repository_id: str = "unknown",
        analysis_id: str = "unknown",
    ) -> MetricCollection:
        """Compute metrics from a list of Observation objects.

        Args:
            observations: List of Observation instances.
            provider_map: Optional mapping from observation_id to provider_id.
            repository_id: Repository identifier.
            analysis_id: Analysis run identifier.

        Returns:
            MetricCollection with all computed metrics.
        """
        inputs = self._observations_to_inputs(observations, provider_map=provider_map)
        return self._compute_metrics(inputs, repository_id, analysis_id)

    def compute_single(
        self,
        metric_id: str,
        observations: List[ObservationInput],
    ) -> MetricResult:
        """Compute a single metric from observations.

        Args:
            metric_id: Which metric to compute (e.g. "M-01").
            observations: Observations for this metric.

        Returns:
            MetricResult.
        """
        computer = self._registry.get_computer(metric_id)
        return computer.compute(observations)

    # ------------------------------------------------------------------
    # Internal Pipeline
    # ------------------------------------------------------------------

    def _compute_metrics(
        self,
        inputs: List[ObservationInput],
        repository_id: str,
        analysis_id: str,
    ) -> MetricCollection:
        """Execute the full computation pipeline."""
        start_time = time.perf_counter()

        # Group by metric_id
        by_metric: Dict[str, List[ObservationInput]] = {}
        for inp in inputs:
            by_metric.setdefault(inp.metric_id, []).append(inp)

        # Record diagnostics
        for metric_id, obs_list in by_metric.items():
            self._diagnostics.record_observation_count(metric_id, len(obs_list))

        providers = {inp.provider_id for inp in inputs}
        for pid in providers:
            count = sum(1 for inp in inputs if inp.provider_id == pid)
            self._diagnostics.record_provider_count(pid, count)

        # Execute in dependency order
        execution_order = self._registry.execution_order()
        results: Dict[str, MetricResult] = {}
        all_warnings: List[str] = []

        for metric_id in execution_order:
            obs_list = by_metric.get(metric_id, [])

            if not obs_list:
                self._diagnostics.record_warning(f"No observations for {metric_id}")
                continue

            try:
                computer = self._registry.get_computer(metric_id)

                # Validate
                validation = self._obs_validator.validate_input_observations(obs_list, computer.metric_definition)
                if not validation.is_valid:
                    for error in validation.errors:
                        self._diagnostics.record_validation_failure(error)
                    all_warnings.extend(validation.errors)
                    continue

                # Compute with timing
                self._diagnostics.start_timer(metric_id)
                result = computer.compute(obs_list)
                _elapsed = self._diagnostics.stop_timer(metric_id)

                # Validate result
                result_validation = self._obs_validator.validate_metric_result(result, computer.metric_definition)
                if not result_validation.is_valid:
                    for error in result_validation.errors:
                        self._diagnostics.record_validation_failure(error)
                    all_warnings.extend(result_validation.errors)
                    continue

                results[metric_id] = result
                all_warnings.extend(result.warnings)

            except Exception as e:
                self._diagnostics.record_validation_failure(f"{metric_id}: computation failed: {e}")
                all_warnings.append(f"{metric_id}: computation failed: {e}")
                logger.exception("Failed to compute %s", metric_id)

        # Assemble collection
        collection_id = generate_metric_collection_id(repository_id, analysis_id)
        overall_confidence = self._compute_overall_confidence(results)
        coverage = len(results) / len(self.EXPECTED_METRICS)

        elapsed_total = (time.perf_counter() - start_time) * 1000.0

        collection = MetricCollection(
            collection_id=collection_id,
            repository_id=repository_id,
            analysis_id=analysis_id,
            results=results,
            overall_confidence=overall_confidence,
            coverage=coverage,
            computation_timestamp=str(round(elapsed_total, 3)),
            warnings=all_warnings,
        )

        logger.info(
            "Metric computation complete: %d/%d metrics, confidence=%.3f, " "coverage=%.1f%%, time=%.1fms",
            len(results),
            len(self.EXPECTED_METRICS),
            overall_confidence,
            coverage * 100,
            elapsed_total,
        )

        return collection

    def _observations_to_inputs(
        self,
        observations: List[Any],
        graph: Any = None,
        provider_map: Optional[Dict[str, str]] = None,
    ) -> List[ObservationInput]:
        """Convert Observation objects to ObservationInput."""
        inputs: List[ObservationInput] = []

        for obs in observations:
            # Determine provider_id
            pid = "unknown"
            if provider_map and obs.observation_id in provider_map:
                pid = provider_map[obs.observation_id]
            elif graph is not None:
                # Try to get from graph node
                try:
                    node = graph.get_node(obs.observation_id)
                    if node:
                        pid = node.provider_id
                except (AttributeError, KeyError):
                    pass

            inputs.append(
                ObservationInput(
                    observation_id=obs.observation_id,
                    metric_id=obs.metric_id,
                    value=obs.value,
                    unit=obs.unit,
                    quality=obs.quality,
                    source_type=obs.source_type,
                    source_id=obs.source_id,
                    timestamp=obs.timestamp,
                    provider_id=pid,
                    metadata=obs.metadata if hasattr(obs, "metadata") else {},
                )
            )

        return inputs

    def _compute_overall_confidence(
        self,
        results: Dict[str, MetricResult],
    ) -> float:
        """Compute weighted overall confidence."""
        if not results:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for metric_id, result in results.items():
            # Weight by observation count (more data = higher weight)
            weight = max(1, result.observation_count)
            weighted_sum += result.confidence * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def registry(self) -> MetricRegistry:
        """The metric registry."""
        return self._registry

    @property
    def diagnostics(self) -> MetricDiagnosticsEngine:
        """The diagnostics engine."""
        return self._diagnostics

    def get_diagnostics_summary(self) -> Dict[str, Any]:
        """Get a summary of computation diagnostics."""
        return self._diagnostics.to_diagnostics().__dict__
