"""Unit tests for MIIE v1.5 ObservationStore.

Covers:
  - IObservationStore protocol compliance
  - ObservationStore add/get/query/count/clear/list_collections
  - Duplicate detection, type checking, query filtering
  - Edge cases (empty store, multiple windows, multiple collections)

Reference: IMS-v1.0 Phase 2, ODSS-v1.0 §12
"""

import pytest

from miie.contracts.errors import ObservationStoreError
from miie.processing.observation.models import (
    Observation,
    ObservationCollection,
    ObservationProvenance,
    ObservationWindow,
    generate_observation_id,
)
from miie.processing.observation.store import ObservationStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_COMMIT_SHA = "a" * 40
SAMPLE_TIMESTAMP = "2026-01-15T10:30:00Z"
SAMPLE_PROVENANCE = ObservationProvenance(
    extractor_id="test-extractor",
    extraction_timestamp="2026-06-29T12:00:00Z",
    seed=42,
)


def _make_observation(
    *,
    source_type: str = "commit",
    source_id: str = SAMPLE_COMMIT_SHA,
    metric_id: str = "M-02",
    value: float = 100.0,
) -> Observation:
    """Helper: create a valid Observation."""
    from miie.processing.observation.models import _METRIC_UNITS

    unit = _METRIC_UNITS[metric_id]
    obs_id = generate_observation_id(source_type, source_id, metric_id)
    return Observation(
        observation_id=obs_id,
        source_type=source_type,
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        unit=unit,
        timestamp=SAMPLE_TIMESTAMP,
        quality="complete",
        provenance=SAMPLE_PROVENANCE,
    )


def _make_collection(
    *,
    collection_id: str = "a" * 16,
    repository_id: str = "test-repo",
    analysis_id: str = "analysis-1",
    windows: list | None = None,
) -> ObservationCollection:
    """Helper: create a valid ObservationCollection."""
    obs = windows  # avoid default mutable
    if obs is None:
        obs = [_make_window()]
    return ObservationCollection(
        collection_id=collection_id,
        repository_id=repository_id,
        analysis_id=analysis_id,
        windows=obs,
    )


def _make_window(
    *,
    window_id: str = "w00",
    window_index: int = 0,
    observations: list | None = None,
    strategy: str = "temporal",
) -> ObservationWindow:
    """Helper: create a valid ObservationWindow."""
    obs = observations or [_make_observation()]
    return ObservationWindow(
        window_id=window_id,
        window_index=window_index,
        strategy=strategy,
        start_boundary="2026-01-01T00:00:00Z",
        end_boundary="2026-01-31T23:59:59Z",
        observations=obs,
    )


# ---------------------------------------------------------------------------
# Basic Operations
# ---------------------------------------------------------------------------


class TestObservationStoreBasicOps:
    """Core add/get/count/clear/list_collections operations."""

    def test_empty_store(self) -> None:
        store = ObservationStore()
        assert store.count() == 0
        assert store.list_collections() == []

    def test_add_collection(self) -> None:
        store = ObservationStore()
        coll = _make_collection()
        store.add(coll)
        assert store.count() == 1

    def test_get_collection(self) -> None:
        store = ObservationStore()
        coll = _make_collection()
        store.add(coll)
        retrieved = store.get(coll.collection_id)
        assert retrieved is coll

    def test_get_nonexistent(self) -> None:
        store = ObservationStore()
        assert store.get("nonexistent") is None

    def test_list_collections(self) -> None:
        store = ObservationStore()
        coll1 = _make_collection(collection_id="a" * 16)
        coll2 = _make_collection(collection_id="b" * 16)
        store.add(coll1)
        store.add(coll2)
        ids = store.list_collections()
        assert len(ids) == 2
        assert "a" * 16 in ids
        assert "b" * 16 in ids

    def test_clear(self) -> None:
        store = ObservationStore()
        store.add(_make_collection())
        assert store.count() == 1
        store.clear()
        assert store.count() == 0
        assert store.list_collections() == []

    def test_add_duplicate_raises(self) -> None:
        store = ObservationStore()
        coll = _make_collection()
        store.add(coll)
        with pytest.raises(ObservationStoreError, match="Duplicate collection_id"):
            store.add(coll)

    def test_add_wrong_type_raises(self) -> None:
        store = ObservationStore()
        with pytest.raises(ObservationStoreError, match="must be an ObservationCollection"):
            store.add("not a collection")  # type: ignore[arg-type]

    def test_add_invalid_collection_raises(self) -> None:
        store = ObservationStore()
        with pytest.raises(ObservationStoreError, match="must be an ObservationCollection"):
            store.add(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Query Operations
# ---------------------------------------------------------------------------


class TestObservationStoreQuery:
    """Query filtering operations."""

    def test_query_no_filters(self) -> None:
        store = ObservationStore()
        store.add(_make_collection(collection_id="a" * 16))
        store.add(_make_collection(collection_id="b" * 16))
        results = store.query()
        assert len(results) == 2

    def test_query_by_repository_id(self) -> None:
        store = ObservationStore()
        store.add(
            _make_collection(
                collection_id="a" * 16,
                repository_id="repo-a",
            )
        )
        store.add(
            _make_collection(
                collection_id="b" * 16,
                repository_id="repo-b",
            )
        )
        results = store.query(repository_id="repo-a")
        assert len(results) == 1
        assert results[0].repository_id == "repo-a"

    def test_query_by_analysis_id(self) -> None:
        store = ObservationStore()
        store.add(
            _make_collection(
                collection_id="a" * 16,
                analysis_id="analysis-1",
            )
        )
        store.add(
            _make_collection(
                collection_id="b" * 16,
                analysis_id="analysis-2",
            )
        )
        results = store.query(analysis_id="analysis-1")
        assert len(results) == 1
        assert results[0].analysis_id == "analysis-1"

    def test_query_by_metric_id(self) -> None:
        store = ObservationStore()
        obs_m01 = _make_observation(metric_id="M-01")
        obs_m02 = _make_observation(metric_id="M-02")
        w1 = _make_window(observations=[obs_m01])
        w2 = _make_window(window_id="w01", window_index=1, observations=[obs_m02])
        coll1 = _make_collection(collection_id="a" * 16, windows=[w1])
        coll2 = _make_collection(collection_id="b" * 16, windows=[w2])
        store.add(coll1)
        store.add(coll2)
        results = store.query(metric_id="M-01")
        assert len(results) == 1
        assert results[0].collection_id == "a" * 16

    def test_query_by_window_id(self) -> None:
        store = ObservationStore()
        w1 = _make_window(window_id="w00")
        w2 = _make_window(window_id="w99", window_index=1)
        coll1 = _make_collection(collection_id="a" * 16, windows=[w1])
        coll2 = _make_collection(collection_id="b" * 16, windows=[w2])
        store.add(coll1)
        store.add(coll2)
        results = store.query(window_id="w00")
        assert len(results) == 1
        assert results[0].collection_id == "a" * 16

    def test_query_multiple_filters(self) -> None:
        store = ObservationStore()
        store.add(
            _make_collection(
                collection_id="a" * 16,
                repository_id="repo-a",
                analysis_id="analysis-1",
            )
        )
        store.add(
            _make_collection(
                collection_id="b" * 16,
                repository_id="repo-a",
                analysis_id="analysis-2",
            )
        )
        store.add(
            _make_collection(
                collection_id="c" * 16,
                repository_id="repo-b",
                analysis_id="analysis-1",
            )
        )
        results = store.query(repository_id="repo-a", analysis_id="analysis-1")
        assert len(results) == 1
        assert results[0].collection_id == "a" * 16

    def test_query_no_match(self) -> None:
        store = ObservationStore()
        store.add(_make_collection(repository_id="repo-a"))
        results = store.query(repository_id="repo-b")
        assert len(results) == 0

    def test_query_empty_store(self) -> None:
        store = ObservationStore()
        results = store.query(repository_id="any")
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Protocol Compliance
# ---------------------------------------------------------------------------


class TestObservationStoreProtocol:
    """IObservationStore protocol check."""

    def test_is_protocol_instance(self) -> None:
        from miie.contracts.interfaces import IObservationStore

        store = ObservationStore()
        assert isinstance(store, IObservationStore)

    def test_has_add(self) -> None:
        store = ObservationStore()
        assert callable(getattr(store, "add", None))

    def test_has_get(self) -> None:
        store = ObservationStore()
        assert callable(getattr(store, "get", None))

    def test_has_query(self) -> None:
        store = ObservationStore()
        assert callable(getattr(store, "query", None))

    def test_has_count(self) -> None:
        store = ObservationStore()
        assert callable(getattr(store, "count", None))

    def test_has_clear(self) -> None:
        store = ObservationStore()
        assert callable(getattr(store, "clear", None))

    def test_has_list_collections(self) -> None:
        store = ObservationStore()
        assert callable(getattr(store, "list_collections", None))


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


class TestObservationStoreEdgeCases:
    """Edge cases and multi-collection scenarios."""

    def test_multiple_windows_in_collection(self) -> None:
        store = ObservationStore()
        w1 = _make_window(window_id="w00")
        w2 = _make_window(window_id="w01", window_index=1)
        coll = _make_collection(windows=[w1, w2])
        store.add(coll)
        retrieved = store.get(coll.collection_id)
        assert retrieved is not None
        assert len(retrieved.windows) == 2

    def test_collection_with_empty_windows(self) -> None:
        store = ObservationStore()
        coll = ObservationCollection(
            collection_id="a" * 16,
            repository_id="repo",
            analysis_id="analysis",
        )
        store.add(coll)
        assert store.count() == 1
        assert store.get("a" * 16) is coll

    def test_clear_then_add(self) -> None:
        store = ObservationStore()
        store.add(_make_collection())
        store.clear()
        store.add(_make_collection(collection_id="b" * 16))
        assert store.count() == 1
        assert store.get("b" * 16) is not None

    def test_query_after_clear(self) -> None:
        store = ObservationStore()
        store.add(_make_collection(repository_id="repo"))
        store.clear()
        results = store.query(repository_id="repo")
        assert len(results) == 0

    def test_list_after_multiple_adds(self) -> None:
        store = ObservationStore()
        ids = [f"{i:016d}" for i in range(5)]
        for cid in ids:
            store.add(_make_collection(collection_id=cid))
        listed = store.list_collections()
        assert len(listed) == 5
        for cid in ids:
            assert cid in listed

    def test_get_returns_same_reference(self) -> None:
        store = ObservationStore()
        coll = _make_collection()
        store.add(coll)
        retrieved = store.get(coll.collection_id)
        assert retrieved is coll  # same object, not a copy
