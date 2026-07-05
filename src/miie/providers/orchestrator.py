"""
MIIE v1.6 Observation Provider Framework — Multi-Provider Orchestrator.

Coordinates multiple observation providers (Git, GitHub PR, etc.) as a
single deterministic scientific observation platform.  Discovers providers
via the DeterministicRegistry, plans execution, isolates failures, merges
results, and tracks diagnostics.

Implements OPR §6, §12 — multi-provider orchestration.

Reference: PR-11C specification.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from miie.providers.context import (
    ExtractionResult,
    PriorityLevel,
    ProviderContext,
    ProviderState,
    QualityState,
)
from miie.providers.registry import DeterministicRegistry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ORCHESTRATOR_VERSION: str = "1.0.0"


# ---------------------------------------------------------------------------
# Dataclasses — Execution Plan
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderTask:
    """A single provider execution task in the orchestration plan.

    Attributes:
        provider_id: The provider to execute.
        metric_ids: Which metrics this provider should extract.
        priority: Execution priority (lower = earlier).
        is_fallback: Whether this is a fallback provider.
    """

    provider_id: str
    metric_ids: Tuple[str, ...]
    priority: PriorityLevel
    is_fallback: bool = False


@dataclass(frozen=True)
class ExecutionPlan:
    """Deterministic execution plan for multi-provider extraction.

    Attributes:
        tasks: Ordered list of provider tasks to execute.
        metric_coverage: Mapping of metric_id → provider_ids that serve it.
        total_providers: Total number of unique providers.
    """

    tasks: Tuple[ProviderTask, ...]
    metric_coverage: Dict[str, Tuple[str, ...]]
    total_providers: int

    @property
    def task_count(self) -> int:
        """Number of tasks in the plan."""
        return len(self.tasks)


# ---------------------------------------------------------------------------
# Dataclasses — Provider Execution Result
# ---------------------------------------------------------------------------


@dataclass
class ProviderExecutionResult:
    """Result of executing a single provider within the orchestration.

    Attributes:
        provider_id: The provider that was executed.
        result: The extraction result (None if provider failed).
        success: Whether execution succeeded.
        error: Error message if execution failed.
        execution_time_ms: Wall-clock time for this provider.
        observations_produced: Number of observations produced.
    """

    provider_id: str
    result: Optional[ExtractionResult]
    success: bool
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    observations_produced: int = 0


# ---------------------------------------------------------------------------
# Dataclasses — Merge Conflict
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MergeConflict:
    """Records a conflict detected during observation merging.

    Attributes:
        observation_id: The conflicting observation ID.
        source_provider: Provider that produced the conflicting observation.
        conflicting_provider: Provider that produced the other version.
        conflict_type: Description of the conflict.
        resolution: How the conflict was resolved.
    """

    observation_id: str
    source_provider: str
    conflicting_provider: str
    conflict_type: str
    resolution: str


# ---------------------------------------------------------------------------
# Dataclasses — Orchestrator Diagnostics
# ---------------------------------------------------------------------------


@dataclass
class OrchestratorDiagnostics:
    """Diagnostics snapshot from an orchestration run.

    Tracks which providers executed, observations produced, conflicts
    resolved, and overall quality assessment.
    """

    providers_attempted: int = 0
    providers_succeeded: int = 0
    providers_failed: int = 0
    providers_skipped: int = 0
    total_observations: int = 0
    duplicate_observations_removed: int = 0
    merge_conflicts_detected: int = 0
    merge_conflicts_resolved: int = 0
    execution_time_ms: float = 0.0
    overall_quality: QualityState = QualityState.COMPLETE
    overall_confidence: float = 1.0
    warnings: List[str] = field(default_factory=list)
    provider_results: List[ProviderExecutionResult] = field(default_factory=list)
    conflicts: List[MergeConflict] = field(default_factory=list)

    @property
    def is_deterministic(self) -> bool:
        """Diagnostics are always deterministic (no random state)."""
        return True

    @property
    def success_rate(self) -> float:
        """Ratio of succeeded to attempted providers."""
        if self.providers_attempted == 0:
            return 1.0
        return self.providers_succeeded / self.providers_attempted


# ---------------------------------------------------------------------------
# Dataclasses — Orchestrator Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OrchestratorConfig:
    """Configuration for the observation orchestrator.

    Attributes:
        max_parallel_providers: Maximum providers to execute in parallel
            (currently unused — execution is sequential for determinism).
        provider_timeout_seconds: Timeout per provider execution.
        enable_partial_execution: Whether to continue if a provider fails.
        deduplicate_observations: Whether to remove duplicate observations.
        merge_policy: How to resolve duplicate observations
            ('highest_priority' | 'latest' | 'all').
    """

    max_parallel_providers: int = 1
    provider_timeout_seconds: float = 60.0
    enable_partial_execution: bool = True
    deduplicate_observations: bool = True
    merge_policy: str = "highest_priority"


# ---------------------------------------------------------------------------
# ObservationOrchestrator (OPR §12)
# ---------------------------------------------------------------------------


class ObservationOrchestrator:
    """OPR §12 — Multi-provider observation orchestrator.

    Coordinates multiple observation providers to produce a unified set of
    observations.  Follows deterministic execution ordering and provides
    full diagnostic tracing.

    Usage::

        registry = DeterministicRegistry()
        registry.register(git_provider, git_capabilities(), PriorityLevel.HIGH)
        registry.register(github_provider, github_capabilities(), PriorityLevel.MEDIUM)

        orchestrator = ObservationOrchestrator(registry)
        collection, diagnostics = orchestrator.orchestrate(
            context,
            metric_ids=["M-02", "M-05", "M-06"],
        )

    Determinism guarantee: for the same registry state and context, the
    orchestrator always produces the same execution plan, merge order, and
    diagnostics.
    """

    def __init__(
        self,
        registry: DeterministicRegistry,
        config: Optional[OrchestratorConfig] = None,
    ) -> None:
        """Initialize the orchestrator.

        Args:
            registry: Deterministic provider registry.
            config: Optional orchestrator configuration.
        """
        self._registry = registry
        self._config = config or OrchestratorConfig()

    @property
    def registry(self) -> DeterministicRegistry:
        """Return the underlying provider registry."""
        return self._registry

    @property
    def config(self) -> OrchestratorConfig:
        """Return the orchestrator configuration."""
        return self._config

    # ------------------------------------------------------------------
    # Public API — Orchestrate
    # ------------------------------------------------------------------

    def orchestrate(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> Tuple[ExtractionResult, OrchestratorDiagnostics]:
        """Execute all providers and merge results into a single ExtractionResult.

        This is the main entry point.  It:
        1. Builds an execution plan from the registry
        2. Executes each provider in deterministic order
        3. Merges observations, deduplicating as needed
        4. Produces diagnostics

        Args:
            context: Shared extraction context.
            metric_ids: Metrics to extract.

        Returns:
            Tuple of (merged ExtractionResult, OrchestratorDiagnostics).

        Raises:
            PartialExtractionError: If all providers fail and
                ``enable_partial_execution`` is False.
        """
        start_time = time.monotonic()
        diagnostics = OrchestratorDiagnostics()

        # --- Phase 1: Build execution plan ---
        plan = self.build_execution_plan(metric_ids)
        diagnostics.providers_attempted = plan.total_providers

        if plan.task_count == 0:
            diagnostics.providers_skipped = len(metric_ids)
            diagnostics.overall_quality = QualityState.MISSING
            diagnostics.overall_confidence = 0.0
            diagnostics.execution_time_ms = (time.monotonic() - start_time) * 1000.0
            return self._empty_result(context, metric_ids), diagnostics

        # --- Phase 2: Execute providers ---
        all_results: List[ProviderExecutionResult] = []

        for task in plan.tasks:
            provider_result = self._execute_provider(task, context)
            all_results.append(provider_result)
            diagnostics.provider_results.append(provider_result)

            if provider_result.success:
                diagnostics.providers_succeeded += 1
                diagnostics.total_observations += provider_result.observations_produced
            else:
                diagnostics.providers_failed += 1
                diagnostics.warnings.append(f"Provider {task.provider_id} failed: {provider_result.error}")

        # --- Phase 3: Merge observations ---
        merged_observations, conflicts = self._merge_results(all_results, plan)
        diagnostics.merge_conflicts_detected = len(conflicts)
        diagnostics.conflicts = conflicts

        # Deduplication
        if self._config.deduplicate_observations:
            deduped, removed_count = self._deduplicate(merged_observations)
            merged_observations = deduped
            diagnostics.duplicate_observations_removed = removed_count

        # --- Phase 4: Quality assessment ---
        quality, confidence = self._assess_overall_quality(all_results, merged_observations)
        diagnostics.overall_quality = quality
        diagnostics.overall_confidence = confidence

        # --- Phase 5: Build merged result ---
        primary_metric = metric_ids[0] if metric_ids else "M-02"
        extraction_time_ms = (time.monotonic() - start_time) * 1000.0
        diagnostics.execution_time_ms = extraction_time_ms

        merged_result = ExtractionResult(
            provider_id=_ORCHESTRATOR_ID,
            metric_id=primary_metric,
            observations=tuple(merged_observations),
            quality_state=quality,
            confidence=confidence,
            extraction_time_ms=extraction_time_ms,
            is_partial=diagnostics.providers_failed > 0 and diagnostics.providers_succeeded > 0,
            warnings=diagnostics.warnings,
            metadata={
                "orchestrator_version": _ORCHESTRATOR_VERSION,
                "providers_attempted": diagnostics.providers_attempted,
                "providers_succeeded": diagnostics.providers_succeeded,
                "providers_failed": diagnostics.providers_failed,
                "total_observations": diagnostics.total_observations,
                "duplicates_removed": diagnostics.duplicate_observations_removed,
                "conflicts_detected": diagnostics.merge_conflicts_detected,
                "metric_ids": sorted(metric_ids),
            },
        )

        return merged_result, diagnostics

    # ------------------------------------------------------------------
    # Execution Plan Builder
    # ------------------------------------------------------------------

    def build_execution_plan(self, metric_ids: List[str]) -> ExecutionPlan:
        """Build a deterministic execution plan for the requested metrics.

        Discovers providers for each metric via the registry, orders them
        by priority (via DeterministicRegistry), and produces a flat list
        of ProviderTasks.

        The plan is fully deterministic: for the same registry state and
        metric_ids, the same plan is always produced.

        Args:
            metric_ids: Metrics to extract.

        Returns:
            ExecutionPlan with ordered tasks and coverage mapping.
        """
        metric_coverage: Dict[str, List[str]] = {}
        seen_providers: Dict[str, ProviderTask] = {}

        for metric_id in sorted(metric_ids):
            providers = self._registry.discover(metric_id)
            metric_coverage[metric_id] = []

            for provider in providers:
                pid = provider.provider_id
                metric_coverage[metric_id].append(pid)

                if pid in seen_providers:
                    # Extend existing task with additional metric
                    existing = seen_providers[pid]
                    new_metrics = tuple(sorted(set(existing.metric_ids + (metric_id,))))
                    updated = ProviderTask(
                        provider_id=pid,
                        metric_ids=new_metrics,
                        priority=existing.priority,
                        is_fallback=existing.is_fallback,
                    )
                    seen_providers[pid] = updated
                else:
                    # Determine priority from registry
                    entry = self._registry.get_entry(pid)
                    priority = entry.priority if entry else PriorityLevel.MEDIUM
                    task = ProviderTask(
                        provider_id=pid,
                        metric_ids=(metric_id,),
                        priority=priority,
                    )
                    seen_providers[pid] = task

        # Sort tasks deterministically: by priority (ascending), then by provider_id
        tasks = sorted(
            seen_providers.values(),
            key=lambda t: (t.priority.value, t.provider_id),
        )

        # Finalize coverage (tuples for immutability)
        final_coverage = {mid: tuple(pids) for mid, pids in metric_coverage.items()}

        return ExecutionPlan(
            tasks=tuple(tasks),
            metric_coverage=final_coverage,
            total_providers=len(tasks),
        )

    # ------------------------------------------------------------------
    # Provider Execution
    # ------------------------------------------------------------------

    def _execute_provider(
        self,
        task: ProviderTask,
        context: ProviderContext,
    ) -> ProviderExecutionResult:
        """Execute a single provider with isolation and error handling.

        Provider isolation: if one provider fails, others continue.
        All exceptions are caught and converted to ProviderExecutionResult.

        Args:
            task: The provider task to execute.
            context: Shared extraction context.

        Returns:
            ProviderExecutionResult with result or error.
        """
        provider = self._registry.get_provider(task.provider_id)
        if provider is None:
            return ProviderExecutionResult(
                provider_id=task.provider_id,
                result=None,
                success=False,
                error=f"Provider '{task.provider_id}' not found in registry",
            )

        # Check provider state
        if provider.state in (ProviderState.DISPOSED, ProviderState.FAILED):
            return ProviderExecutionResult(
                provider_id=task.provider_id,
                result=None,
                success=False,
                error=f"Provider '{task.provider_id}' is in state {provider.state.value}",
            )

        # Initialize if needed
        if provider.state == ProviderState.UNINITIALIZED:
            try:
                provider.initialize(context)
            except Exception as exc:
                return ProviderExecutionResult(
                    provider_id=task.provider_id,
                    result=None,
                    success=False,
                    error=f"Initialization failed: {exc}",
                )

        # Execute extraction
        start_time = time.monotonic()
        try:
            result = provider.extract_observations(context, list(task.metric_ids))
            elapsed_ms = (time.monotonic() - start_time) * 1000.0

            return ProviderExecutionResult(
                provider_id=task.provider_id,
                result=result,
                success=True,
                execution_time_ms=elapsed_ms,
                observations_produced=result.observation_count,
            )

        except Exception as exc:
            elapsed_ms = (time.monotonic() - start_time) * 1000.0
            logger.warning(
                "Provider %s failed during extraction: %s",
                task.provider_id,
                exc,
            )
            return ProviderExecutionResult(
                provider_id=task.provider_id,
                result=None,
                success=False,
                error=str(exc),
                execution_time_ms=elapsed_ms,
            )

    # ------------------------------------------------------------------
    # Observation Merging
    # ------------------------------------------------------------------

    def _merge_results(
        self,
        results: List[ProviderExecutionResult],
        plan: ExecutionPlan,
    ) -> Tuple[List[Any], List[MergeConflict]]:
        """Merge observations from all successful provider results.

        Merge strategy:
        1. Collect observations from each provider in task order
        2. Track observation IDs to detect duplicates
        3. For duplicates, apply merge policy (highest priority wins)

        Args:
            results: All provider execution results.
            plan: The execution plan with priority information.

        Returns:
            Tuple of (merged observations list, list of conflicts).
        """
        merged: List[Any] = []
        conflicts: List[MergeConflict] = []
        seen_ids: Dict[str, Tuple[str, Any]] = {}  # obs_id → (provider_id, observation)

        for provider_result in results:
            if not provider_result.success or provider_result.result is None:
                continue

            for obs in provider_result.result.observations:
                obs_id = obs.observation_id

                if obs_id in seen_ids:
                    # Conflict detected
                    existing_provider, existing_obs = seen_ids[obs_id]
                    conflict_result = self._resolve_conflict(
                        obs_id,
                        existing_provider,
                        existing_obs,
                        provider_result.provider_id,
                        obs,
                    )
                    conflicts.append(conflict_result[0])
                    if conflict_result[1] == "new":
                        seen_ids[obs_id] = (provider_result.provider_id, obs)
                else:
                    seen_ids[obs_id] = (provider_result.provider_id, obs)

        # Build final list in deterministic order (by observation_id)
        merged = [obs for obs_id, (_, obs) in sorted(seen_ids.items())]

        return merged, conflicts

    def _resolve_conflict(
        self,
        obs_id: str,
        existing_provider: str,
        existing_obs: Any,
        new_provider: str,
        new_obs: Any,
    ) -> Tuple[MergeConflict, str]:
        """Resolve a conflict between two observations with the same ID.

        Resolution strategies:
        - 'highest_priority': Provider with lower priority value wins
        - 'latest': Observation with later timestamp wins
        - 'all': Keep both (not applicable here — we pick one)

        Returns:
            Tuple of (MergeConflict, winner: 'existing' | 'new').
        """
        policy = self._config.merge_policy

        if policy == "highest_priority":
            existing_entry = self._registry.get_entry(existing_provider)
            new_entry = self._registry.get_entry(new_provider)

            existing_priority = existing_entry.priority.value if existing_entry else PriorityLevel.MEDIUM.value
            new_priority = new_entry.priority.value if new_entry else PriorityLevel.MEDIUM.value

            if new_priority < existing_priority:
                winner = "new"
                resolution = f"Higher priority provider '{new_provider}' (priority={new_priority}) wins over '{existing_provider}' (priority={existing_priority})"
            elif new_priority > existing_priority:
                winner = "existing"
                resolution = f"Higher priority provider '{existing_provider}' (priority={existing_priority}) wins over '{new_provider}' (priority={new_priority})"
            else:
                # Same priority — deterministic by provider_id
                if new_provider < existing_provider:
                    winner = "new"
                    resolution = f"Same priority, lower provider_id '{new_provider}' wins"
                else:
                    winner = "existing"
                    resolution = f"Same priority, lower provider_id '{existing_provider}' wins"

        elif policy == "latest":
            existing_ts = getattr(existing_obs, "timestamp", "")
            new_ts = getattr(new_obs, "timestamp", "")
            if new_ts > existing_ts:
                winner = "new"
                resolution = f"Later timestamp from '{new_provider}' wins"
            else:
                winner = "existing"
                resolution = f"Later timestamp from '{existing_provider}' wins"

        else:
            # Default: highest priority
            winner = "existing"
            resolution = "Default policy: kept existing observation"

        conflict = MergeConflict(
            observation_id=obs_id,
            source_provider=existing_provider if winner == "existing" else new_provider,
            conflicting_provider=new_provider if winner == "existing" else existing_provider,
            conflict_type="duplicate_observation_id",
            resolution=resolution,
        )

        return conflict, winner

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def _deduplicate(
        self,
        observations: List[Any],
    ) -> Tuple[List[Any], int]:
        """Remove duplicate observations by observation_id.

        Preserves the first occurrence (already sorted by ID from merge).

        Args:
            observations: List of observations to deduplicate.

        Returns:
            Tuple of (deduplicated list, count removed).
        """
        seen: set = set()
        deduped: List[Any] = []

        for obs in observations:
            if obs.observation_id not in seen:
                seen.add(obs.observation_id)
                deduped.append(obs)

        removed_count = len(observations) - len(deduped)
        return deduped, removed_count

    # ------------------------------------------------------------------
    # Quality Assessment
    # ------------------------------------------------------------------

    def _assess_overall_quality(
        self,
        results: List[ProviderExecutionResult],
        merged_observations: List[Any],
    ) -> Tuple[QualityState, float]:
        """Assess overall quality from provider results and merged observations.

        Quality logic:
        - If no providers succeeded → MISSING
        - If all providers succeeded with full observations → COMPLETE
        - If some providers failed → DEGRADED
        - If observations exist but confidence is low → DEGRADED

        Returns:
            Tuple of (QualityState, confidence).
        """
        if not merged_observations:
            return QualityState.MISSING, 0.0

        succeeded = sum(1 for r in results if r.success)
        total = len(results)

        if total == 0:
            return QualityState.MISSING, 0.0

        if succeeded == 0:
            return QualityState.MISSING, 0.0

        # Weighted confidence from each provider's result
        total_confidence = 0.0
        count = 0
        for r in results:
            if r.success and r.result is not None:
                total_confidence += r.result.confidence
                count += 1

        avg_confidence = total_confidence / count if count > 0 else 0.0

        if succeeded < total:
            # Partial failure → degraded
            degradation_factor = succeeded / total
            confidence = avg_confidence * degradation_factor
            return QualityState.DEGRADED, max(0.1, confidence)

        # All succeeded
        if avg_confidence >= 0.9:
            return QualityState.COMPLETE, avg_confidence
        elif avg_confidence >= 0.5:
            return QualityState.DEGRADED, avg_confidence
        else:
            return QualityState.DEGRADED, avg_confidence

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _empty_result(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Create an empty ExtractionResult for when no providers match."""
        return ExtractionResult(
            provider_id=_ORCHESTRATOR_ID,
            metric_id=metric_ids[0] if metric_ids else "M-02",
            observations=(),
            quality_state=QualityState.MISSING,
            confidence=0.0,
            warnings=["No providers found for requested metrics"],
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_diagnostics_summary(
        self,
        diagnostics: OrchestratorDiagnostics,
    ) -> Dict[str, Any]:
        """Convert diagnostics to a serializable summary dictionary.

        Useful for logging, debugging, and reporting.

        Args:
            diagnostics: Diagnostics from an orchestration run.

        Returns:
            Dictionary with key diagnostic fields.
        """
        return {
            "orchestrator_version": _ORCHESTRATOR_VERSION,
            "providers_attempted": diagnostics.providers_attempted,
            "providers_succeeded": diagnostics.providers_succeeded,
            "providers_failed": diagnostics.providers_failed,
            "providers_skipped": diagnostics.providers_skipped,
            "total_observations": diagnostics.total_observations,
            "duplicates_removed": diagnostics.duplicate_observations_removed,
            "conflicts_detected": diagnostics.merge_conflicts_detected,
            "conflicts_resolved": diagnostics.merge_conflicts_resolved,
            "execution_time_ms": round(diagnostics.execution_time_ms, 3),
            "overall_quality": diagnostics.overall_quality.value,
            "overall_confidence": round(diagnostics.overall_confidence, 4),
            "success_rate": round(diagnostics.success_rate, 4),
            "warnings": list(diagnostics.warnings),
        }


# ---------------------------------------------------------------------------
# Module-level constant
# ---------------------------------------------------------------------------

_ORCHESTRATOR_ID: str = "orchestrator.v1"
