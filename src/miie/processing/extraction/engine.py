"""
ExtractionEngine — orchestrates CommitExtractor and MetricExtractor.

Orchestrates the two-phase extraction pipeline:
  1. CommitExtractor extracts observations from git history
  2. MetricExtractor translates observations to MetricDataFrame

Optionally stores the ObservationCollection in an ObservationStore.

Implements IMS Phase 3: ExtractionEngine.

Reference: IMS-v1.0 Phase 3
"""

from __future__ import annotations

import datetime
from typing import List, Optional, Tuple

from miie.contracts.errors import ExtractionError
from miie.processing.extraction.commit_extractor import CommitExtractor
from miie.processing.extraction.metric_extractor import MetricExtractor
from miie.processing.observation.models import ObservationCollection
from miie.processing.observation.store import ObservationStore
from miie.schemas.models import MetricDataFrame, RepositoryContext


class ExtractionEngine:
    """Orchestrate the observation-centric extraction pipeline.

    Coordinates CommitExtractor (git → observations) and MetricExtractor
    (observations → MetricDataFrame) to produce both data products from
    a single extraction pass.

    Usage:
        engine = ExtractionEngine()
        collection, mdf = engine.extract(context, ["M-02", "M-06"])
    """

    def __init__(
        self,
        *,
        store: Optional[ObservationStore] = None,
        commit_extractor: Optional[CommitExtractor] = None,
        metric_extractor: Optional[MetricExtractor] = None,
    ) -> None:
        """Initialize the extraction engine.

        Args:
            store: Optional ObservationStore for persisting collections.
            commit_extractor: Optional custom CommitExtractor instance.
            metric_extractor: Optional custom MetricExtractor instance.
        """
        self._store = store
        self._commit_extractor = commit_extractor or CommitExtractor()
        self._metric_extractor = metric_extractor or MetricExtractor()

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

        Phase 1: CommitExtractor produces ObservationCollection from git.
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
        # --- Phase 1: Extract observations from git ---
        try:
            collection = self._commit_extractor.extract_commits(
                context,
                since=since,
                until=until,
                exclude_bots=exclude_bots,
                seed=seed,
            )
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError(f"CommitExtractor failed: {exc}") from exc

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
