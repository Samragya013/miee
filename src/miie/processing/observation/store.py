"""In-memory ObservationStore implementation.

Implements IObservationStore protocol (IMS Phase 2).
Provides add/get/query/count/clear/list_collections operations
on ObservationCollection objects.

Reference: IMS-v1.0 Phase 2, ODSS-v1.0 §12
"""

from typing import Dict, List, Optional

from miie.contracts.errors import ObservationStoreError
from miie.processing.observation.models import (
    ObservationCollection,
)


class ObservationStore:
    """In-memory store for ObservationCollections.

    Stores ObservationCollection objects indexed by collection_id.
    Provides query methods for filtering by repository, analysis,
    metric, and window.

    Performance target: query latency < 10ms for 10,000 observations
    (IMS Phase 2 acceptance criteria).
    """

    def __init__(self) -> None:
        """Initialize an empty ObservationStore."""
        self._collections: Dict[str, ObservationCollection] = {}

    # ------------------------------------------------------------------
    # IObservationStore protocol methods
    # ------------------------------------------------------------------

    def add(self, collection: ObservationCollection) -> None:
        """Add an ObservationCollection to the store.

        Args:
            collection: An ObservationCollection to store.

        Raises:
            ObservationStoreError: If the collection ID already exists
                or the collection is invalid.
        """
        if not isinstance(collection, ObservationCollection):
            raise ObservationStoreError("collection must be an ObservationCollection instance")

        cid = collection.collection_id
        if cid in self._collections:
            raise ObservationStoreError(f"Duplicate collection_id: {cid!r} already in store")

        self._collections[cid] = collection

    def get(self, collection_id: str) -> Optional[ObservationCollection]:
        """Retrieve a collection by its ID.

        Args:
            collection_id: The collection identifier.

        Returns:
            The ObservationCollection, or None if not found.
        """
        return self._collections.get(collection_id)

    def query(
        self,
        *,
        repository_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        metric_id: Optional[str] = None,
        window_id: Optional[str] = None,
    ) -> List[ObservationCollection]:
        """Query collections with optional filters.

        All filters are AND-combined. An omitted filter means "match any".

        Args:
            repository_id: Filter by repository ID.
            analysis_id: Filter by analysis ID.
            metric_id: Filter by metric ID (must appear in at least one window).
            window_id: Filter by window ID (must exist in at least one window).

        Returns:
            List of matching ObservationCollections.
        """
        results: List[ObservationCollection] = []

        for coll in self._collections.values():
            # Repository filter
            if repository_id is not None and coll.repository_id != repository_id:
                continue

            # Analysis filter
            if analysis_id is not None and coll.analysis_id != analysis_id:
                continue

            # Metric filter: check if metric_id appears in any window
            if metric_id is not None:
                has_metric = False
                for window in coll.windows:
                    if any(obs.metric_id == metric_id for obs in window.observations):
                        has_metric = True
                        break
                if not has_metric:
                    continue

            # Window filter: check if window_id exists in any window
            if window_id is not None:
                has_window = any(w.window_id == window_id for w in coll.windows)
                if not has_window:
                    continue

            results.append(coll)

        return results

    def count(self) -> int:
        """Return the number of stored collections."""
        return len(self._collections)

    def clear(self) -> None:
        """Remove all stored collections."""
        self._collections.clear()

    def list_collections(self) -> List[str]:
        """Return IDs of all stored collections."""
        return list(self._collections.keys())
