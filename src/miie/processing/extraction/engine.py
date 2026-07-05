"""
ExtractionEngine — orchestrates GitObservationProvider and MetricExtractor.

Orchestrates the two-phase extraction pipeline:
  1. GitObservationProvider (or IGitProvider) extracts observations from git
  2. MetricExtractor translates observations to MetricDataFrame

The provider is injected via dependency injection; when none is provided
the default GitObservationProvider is used.

Optionally stores the ObservationCollection in an ObservationStore.

Implements IMS Phase 3: ExtractionEngine.

Reference: IMS-v1.0 Phase 3, PR-11A.2
"""

from __future__ import annotations

import datetime
from typing import Any, List, Optional, Tuple

from miie.contracts.errors import ExtractionError
from miie.processing.extraction.metric_extractor import MetricExtractor
from miie.processing.observation.models import (
    ODSS_SCHEMA_VERSION,
    Observation,
    ObservationCollection,
    ObservationProvenance,
    ObservationWindow,
    generate_observation_id,
)
from miie.processing.observation.store import ObservationStore
from miie.schemas.models import MetricDataFrame, RepositoryContext


class ExtractionEngine:
    """Orchestrate the observation-centric extraction pipeline.

    Coordinates GitObservationProvider (git → observations) and MetricExtractor
    (observations → MetricDataFrame) to produce both data products from
    a single extraction pass.

    Usage::

        engine = ExtractionEngine()
        collection, mdf = engine.extract(context, ["M-02", "M-06"])

    With custom provider::

        engine = ExtractionEngine(provider=my_git_provider)
        collection, mdf = engine.extract(context, ["M-02", "M-06"])
    """

    def __init__(
        self,
        *,
        store: Optional[ObservationStore] = None,
        provider: Optional[Any] = None,
        metric_extractor: Optional[MetricExtractor] = None,
    ) -> None:
        """Initialize the extraction engine.

        Args:
            store: Optional ObservationStore for persisting collections.
            provider: An IGitProvider / IObservationProvider instance.
                When ``None`` (the default), a fresh
                ``GitObservationProvider`` is created and used.
            metric_extractor: Optional custom MetricExtractor instance.
        """
        self._store = store
        self._provider = provider
        self._metric_extractor = metric_extractor or MetricExtractor()

    # ------------------------------------------------------------------
    # Core extraction
    # ------------------------------------------------------------------

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        exclude_bots: bool = False,
        seed: Optional[int] = None,
    ) -> Tuple[ObservationCollection, MetricDataFrame]:
        """Extract observations and metrics from a repository.

        Phase 1: GitObservationProvider produces observations from git.
        Phase 2: MetricExtractor translates observations to MetricDataFrame.

        Args:
            context: RepositoryContext from ingestion.
            metric_list: List of metric IDs to extract.
            since: Inclusive start date filter.
            until: Inclusive end date filter.
            exclude_bots: Whether to exclude bot commits.
            seed: Optional seed for deterministic provenance.

        Returns:
            Tuple of (ObservationCollection, MetricDataFrame).

        Raises:
            ExtractionError: If extraction fails.
        """
        # Lazily create the default provider on first call
        provider = self._resolve_provider()

        # --- Phase 1: Extract observations via provider ---
        try:
            provider_ctx = self._build_provider_context(context, since=since, until=until, exclude_bots=exclude_bots)
            result = provider.extract_observations(provider_ctx, metric_list)
        except Exception as exc:
            raise ExtractionError(f"GitObservationProvider failed: {exc}") from exc

        # --- Apply seed to observations if provided ---
        if seed is not None and result.observations:
            adjusted: List[Observation] = []
            for obs in result.observations:
                new_prov = ObservationProvenance(
                    extractor_id=obs.provenance.extractor_id,
                    extraction_timestamp=obs.provenance.extraction_timestamp,
                    seed=seed,
                )
                adjusted.append(
                    Observation(
                        observation_id=obs.observation_id,
                        source_type=obs.source_type,
                        source_id=obs.source_id,
                        metric_id=obs.metric_id,
                        value=obs.value,
                        unit=obs.unit,
                        timestamp=obs.timestamp,
                        quality=obs.quality,
                        provenance=new_prov,
                        metadata=obs.metadata,
                        relationships=list(obs.relationships),
                    )
                )
            # Re-create result with adjusted observations
            from miie.providers.context import ExtractionResult

            result = ExtractionResult(
                provider_id=result.provider_id,
                metric_id=result.metric_id,
                observations=tuple(adjusted),
                quality_state=result.quality_state,
                confidence=result.confidence,
                extraction_time_ms=result.extraction_time_ms,
                is_partial=result.is_partial,
                warnings=list(result.warnings),
                metadata=dict(result.metadata),
            )

        # --- Build ObservationCollection from ExtractionResult ---
        try:
            collection = self._build_collection(result, context)
        except Exception as exc:
            raise ExtractionError(f"Failed to build ObservationCollection: {exc}") from exc

        # --- Phase 2: Translate observations to MetricDataFrame ---
        try:
            mdf = self._metric_extractor.extract_metrics(
                collection,
                metric_list=metric_list,
            )
        except Exception as exc:
            raise ExtractionError(f"MetricExtractor failed: {exc}") from exc

        # --- Optional: Persist to store ---
        if self._store is not None:
            try:
                self._store.add(collection)
            except Exception as exc:
                raise ExtractionError(f"Failed to store ObservationCollection: {exc}") from exc

        return collection, mdf

    @property
    def store(self) -> Optional[ObservationStore]:
        """Return the attached ObservationStore, if any."""
        return self._store

    # ------------------------------------------------------------------
    # Provider resolution
    # ------------------------------------------------------------------

    def _resolve_provider(self) -> Any:
        """Return the configured provider, creating a default if needed."""
        if self._provider is not None:
            return self._provider

        # Import here to avoid circular imports at module level
        from miie.providers.git import GitObservationProvider

        self._provider = GitObservationProvider()
        return self._provider

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_provider_context(
        context: RepositoryContext,
        *,
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        exclude_bots: bool = False,
    ) -> Any:
        """Build a ProviderContext from a RepositoryContext."""
        import hashlib
        import uuid

        from miie.providers.context import ProviderContext

        # Generate a deterministic-ish analysis ID
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        analysis_id = hashlib.sha256(f"{context.repo_id}:{uuid.uuid4().hex[:8]}:{now_iso}".encode()).hexdigest()[:16]

        return ProviderContext(
            repo_path=str(context.local_path),
            repository_id=context.repo_id,
            analysis_id=analysis_id,
            since=since,
            until=until,
            exclude_bots=exclude_bots,
        )

    # ------------------------------------------------------------------
    # ObservationCollection builder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_collection(
        result: Any,
        context: RepositoryContext,
    ) -> ObservationCollection:
        """Build an ObservationCollection from an ExtractionResult.

        Groups all observations into a single window so that the
        downstream MetricExtractor adapter works unchanged.
        """
        observations: List[Observation] = list(result.observations)

        if not observations:
            # Empty result → empty collection
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            import hashlib

            analysis_id = hashlib.sha256(f"{context.repo_id}:empty:{now_iso}".encode()).hexdigest()[:16]

            empty_window = ObservationWindow(
                window_id="w00",
                window_index=0,
                strategy="commit_count",
                start_boundary=now_iso,
                end_boundary=now_iso,
                observations=[],
                metadata={"total_commits": "0"},
            )

            return ObservationCollection(
                collection_id=generate_observation_id("commit", "empty", "M-02"),
                repository_id=context.repo_id,
                analysis_id=analysis_id,
                windows=[empty_window],
                total_observations=0,
                total_metrics=0,
                extraction_timestamp=now_iso,
                schema_version=ODSS_SCHEMA_VERSION,
            )

        # Determine time boundaries from observations
        timestamps: List[str] = [o.timestamp for o in observations if o.timestamp]
        if timestamps:
            start_boundary = min(timestamps)
            end_boundary = max(timestamps)
        else:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            start_boundary = now_iso
            end_boundary = now_iso

        # Unique source SHAs (newest first is already the provider order)
        source_shas = []
        seen_shas: set = set()
        for obs in observations:
            if obs.source_id not in seen_shas:
                seen_shas.add(obs.source_id)
                source_shas.append(obs.source_id)

        metrics_present = sorted({obs.metric_id for obs in observations})

        # Deterministic collection ID
        first_sha = source_shas[0] if source_shas else "empty"
        last_sha = source_shas[-1] if source_shas else "empty"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        import hashlib

        analysis_payload = f"{context.repo_id}:{first_sha}:{last_sha}:{now_iso}"
        analysis_id = hashlib.sha256(analysis_payload.encode()).hexdigest()[:16]

        window = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="commit_count",
            start_boundary=start_boundary,
            end_boundary=end_boundary,
            observations=observations,
            start_commit=last_sha,
            end_commit=first_sha,
            metrics_present=metrics_present,
            metadata={"total_commits": str(len(source_shas))},
        )

        return ObservationCollection(
            collection_id=generate_observation_id("commit", first_sha, "M-02"),
            repository_id=context.repo_id,
            analysis_id=analysis_id,
            windows=[window],
            total_observations=len(observations),
            total_metrics=len(metrics_present),
            extraction_timestamp=now_iso,
            schema_version=ODSS_SCHEMA_VERSION,
        )
