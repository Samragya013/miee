"""Unit tests for MIIE v1.5 Observation Core models.

Covers:
  - DeterministicObservationID generation
  - Observation dataclass (creation, validation, immutability)
  - ObservationWindow (creation, validation, observation_count)
  - ObservationCollection (creation, indexing, lookup)
  - Supporting types (ObservationProvenance, ObservationStatistics, etc.)
  - create_observation factory

Reference: ODSS-v1.0, IMS-v1.0 Phase 1
"""

import pytest

from miie.processing.observation.models import (
    _METRIC_UNITS,
    ODSS_SCHEMA_VERSION,
    Observation,
    ObservationCollection,
    ObservationProvenance,
    ObservationQuality,
    ObservationRelationship,
    ObservationStatistics,
    ObservationWindow,
    RelationshipType,
    SourceType,
    create_observation,
    generate_observation_id,
)

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
    timestamp: str = SAMPLE_TIMESTAMP,
    quality: str = "complete",
) -> Observation:
    """Helper: create a valid Observation (auto-resolves unit from metric_id)."""
    unit = _METRIC_UNITS[metric_id]
    obs_id = generate_observation_id(source_type, source_id, metric_id)
    return Observation(
        observation_id=obs_id,
        source_type=source_type,
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        unit=unit,
        timestamp=timestamp,
        quality=quality,
        provenance=SAMPLE_PROVENANCE,
    )


def _make_window(
    *,
    window_id: str = "w00",
    window_index: int = 0,
    observations: list | None = None,
) -> ObservationWindow:
    """Helper: create a valid ObservationWindow."""
    obs = observations or [_make_observation()]
    return ObservationWindow(
        window_id=window_id,
        window_index=window_index,
        strategy="temporal",
        start_boundary="2026-01-01T00:00:00Z",
        end_boundary="2026-01-31T23:59:59Z",
        observations=obs,
    )


# ---------------------------------------------------------------------------
# DeterministicObservationID Tests
# ---------------------------------------------------------------------------


class TestDeterministicObservationID:
    """ODSS §10 — Deterministic observation ID generation."""

    def test_returns_16_char_hex(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        assert len(obs_id) == 16
        assert all(c in "0123456789abcdef" for c in obs_id)

    def test_deterministic_same_input(self) -> None:
        id1 = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        id2 = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        assert id1 == id2

    def test_different_source_type_different_id(self) -> None:
        id1 = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        id2 = generate_observation_id("file", "src/main.py", "M-02")
        assert id1 != id2

    def test_different_source_id_different_id(self) -> None:
        id1 = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        id2 = generate_observation_id("commit", "b" * 40, "M-02")
        assert id1 != id2

    def test_different_metric_different_id(self) -> None:
        id1 = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-01")
        id2 = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        assert id1 != id2

    def test_file_source_type(self) -> None:
        obs_id = generate_observation_id("file", "src/main.py", "M-07")
        assert len(obs_id) == 16

    def test_branch_source_type(self) -> None:
        obs_id = generate_observation_id("branch", "main", "M-03")
        assert len(obs_id) == 16

    def test_tag_source_type(self) -> None:
        obs_id = generate_observation_id("tag", "v1.0.0", "M-05")
        assert len(obs_id) == 16

    def test_invalid_source_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid source_type"):
            generate_observation_id("invalid", SAMPLE_COMMIT_SHA, "M-02")

    def test_empty_source_id_raises(self) -> None:
        with pytest.raises(ValueError, match="source_id must be non-empty"):
            generate_observation_id("commit", "", "M-02")

    def test_invalid_metric_id_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid metric_id"):
            generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-99")


# ---------------------------------------------------------------------------
# Observation Tests
# ---------------------------------------------------------------------------


class TestObservation:
    """ODSS §9 — Observation canonical object."""

    def test_creation_valid(self) -> None:
        obs = _make_observation()
        assert obs.source_type == "commit"
        assert obs.metric_id == "M-02"
        assert obs.value == 100.0
        assert obs.quality == "complete"

    def test_immutable(self) -> None:
        obs = _make_observation()
        with pytest.raises(AttributeError):
            obs.value = 200.0  # type: ignore[misc]

    def test_observation_id_format(self) -> None:
        obs = _make_observation()
        assert len(obs.observation_id) == 16
        assert all(c in "0123456789abcdef" for c in obs.observation_id)

    def test_observation_id_matches_formula(self) -> None:
        obs = _make_observation()
        expected = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        assert obs.observation_id == expected

    def test_all_metric_ids_valid(self) -> None:
        for i in range(1, 8):
            metric_id = f"M-{i:02d}"
            obs = _make_observation(metric_id=metric_id)
            assert obs.metric_id == metric_id

    def test_quality_complete(self) -> None:
        obs = _make_observation(quality="complete")
        assert obs.quality == "complete"

    def test_quality_estimated(self) -> None:
        obs = _make_observation(quality="estimated")
        assert obs.quality == "estimated"

    def test_quality_missing(self) -> None:
        obs = _make_observation(quality="missing")
        assert obs.quality == "missing"

    def test_quality_derived(self) -> None:
        obs = _make_observation(quality="derived")
        assert obs.quality == "derived"

    def test_invalid_observation_id_format(self) -> None:
        with pytest.raises(ValueError, match="observation_id must match"):
            Observation(
                observation_id="invalid",
                source_type="commit",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=1.0,
                unit="count",
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_invalid_source_type(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="source_type must be one of"):
            Observation(
                observation_id=obs_id,
                source_type="invalid",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=1.0,
                unit="count",
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_empty_source_id_raises(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="source_id must be non-empty"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id="",
                metric_id="M-02",
                value=1.0,
                unit="count",
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_commit_source_id_must_be_40_char_hex(self) -> None:
        obs_id = generate_observation_id("commit", "abc", "M-02")
        with pytest.raises(ValueError, match="40-char hex SHA"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id="abc",
                metric_id="M-02",
                value=1.0,
                unit="count",
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_nan_value_raises(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="value must be finite"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=float("nan"),
                unit="count",
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_inf_value_raises(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="value must be finite"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=float("inf"),
                unit="count",
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_invalid_unit_raises(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="unit must be one of"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=1.0,
                unit="invalid",
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_unit_metric_inconsistency_raises(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="inconsistent with metric"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=1.0,
                unit="ratio",  # M-02 expects "count"
                timestamp=SAMPLE_TIMESTAMP,
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_invalid_timestamp_raises(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="valid ISO-8601 datetime"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=1.0,
                unit="count",
                timestamp="not-a-timestamp",
                quality="complete",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_invalid_quality_raises(self) -> None:
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        with pytest.raises(ValueError, match="quality must be one of"):
            Observation(
                observation_id=obs_id,
                source_type="commit",
                source_id=SAMPLE_COMMIT_SHA,
                metric_id="M-02",
                value=1.0,
                unit="count",
                timestamp=SAMPLE_TIMESTAMP,
                quality="invalid",
                provenance=SAMPLE_PROVENANCE,
            )

    def test_metadata_optional(self) -> None:
        obs = _make_observation()
        assert obs.metadata == {}

    def test_metadata_populated(self) -> None:
        obs = _make_observation()
        # Observation is frozen, so we test creation with metadata
        obs_id = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        obs2 = Observation(
            observation_id=obs_id,
            source_type="commit",
            source_id=SAMPLE_COMMIT_SHA,
            metric_id="M-02",
            value=100.0,
            unit="count",
            timestamp=SAMPLE_TIMESTAMP,
            quality="complete",
            provenance=SAMPLE_PROVENANCE,
            metadata={"commit_message": "feat: add feature"},
        )
        assert obs2.metadata["commit_message"] == "feat: add feature"

    def test_relationships_optional(self) -> None:
        obs = _make_observation()
        assert obs.relationships == []

    def test_extensions_optional(self) -> None:
        obs = _make_observation()
        assert obs.extensions == {}


# ---------------------------------------------------------------------------
# ObservationProvenance Tests
# ---------------------------------------------------------------------------


class TestObservationProvenance:
    """ODSS §19 — Provenance tracking."""

    def test_creation(self) -> None:
        p = ObservationProvenance(
            extractor_id="commit-extractor",
            extraction_timestamp="2026-06-29T12:00:00Z",
            seed=42,
        )
        assert p.extractor_id == "commit-extractor"
        assert p.seed == 42

    def test_immutable(self) -> None:
        p = ObservationProvenance(
            extractor_id="test",
            extraction_timestamp="2026-06-29T12:00:00Z",
        )
        with pytest.raises(AttributeError):
            p.extractor_id = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ObservationStatistics Tests
# ---------------------------------------------------------------------------


class TestObservationStatistics:
    """ODSS §18 — Aggregated statistics."""

    def test_creation(self) -> None:
        stats = ObservationStatistics(mean=50.0, std=10.0, min_value=0.0, max_value=100.0, n=50)
        assert stats.mean == 50.0
        assert stats.n == 50

    def test_negative_n_raises(self) -> None:
        with pytest.raises(ValueError, match="n must be non-negative"):
            ObservationStatistics(mean=0.0, std=0.0, min_value=0.0, max_value=0.0, n=-1)

    def test_nan_mean_raises(self) -> None:
        with pytest.raises(ValueError, match="mean must be finite"):
            ObservationStatistics(mean=float("nan"), std=0.0, min_value=0.0, max_value=0.0, n=0)

    def test_inf_std_raises(self) -> None:
        with pytest.raises(ValueError, match="std must be finite"):
            ObservationStatistics(mean=0.0, std=float("inf"), min_value=0.0, max_value=0.0, n=0)


# ---------------------------------------------------------------------------
# ObservationRelationship Tests
# ---------------------------------------------------------------------------


class TestObservationRelationship:
    """ODSS §20 — Observation relationships."""

    def test_creation(self) -> None:
        rel = ObservationRelationship(
            relationship_type=RelationshipType.DERIVED_FROM,
            target_observation_id="a" * 16,
        )
        assert rel.relationship_type == RelationshipType.DERIVED_FROM

    def test_file_of_commit(self) -> None:
        rel = ObservationRelationship(
            relationship_type=RelationshipType.FILE_OF_COMMIT,
            target_observation_id="b" * 16,
        )
        assert rel.relationship_type == RelationshipType.FILE_OF_COMMIT


# ---------------------------------------------------------------------------
# ObservationWindow Tests
# ---------------------------------------------------------------------------


class TestObservationWindow:
    """ODSS §8 — Observation window."""

    def test_creation(self) -> None:
        w = _make_window()
        assert w.window_id == "w00"
        assert w.observation_count == 1

    def test_observation_count_property(self) -> None:
        obs = [_make_observation(), _make_observation()]
        w = _make_window(observations=obs)
        assert w.observation_count == 2

    def test_window_id_format(self) -> None:
        w = _make_window(window_id="w100")
        assert w.window_id == "w100"

    def test_invalid_window_id_raises(self) -> None:
        with pytest.raises(ValueError, match="window_id must match"):
            _make_window(window_id="invalid")

    def test_negative_index_raises(self) -> None:
        with pytest.raises(ValueError, match="window_index must be non-negative"):
            _make_window(window_index=-1)

    def test_invalid_strategy_raises(self) -> None:
        with pytest.raises(ValueError, match="strategy must be one of"):
            ObservationWindow(
                window_id="w00",
                window_index=0,
                strategy="invalid",
                start_boundary="2026-01-01T00:00:00Z",
                end_boundary="2026-01-31T23:59:59Z",
            )

    def test_start_after_end_raises(self) -> None:
        with pytest.raises(ValueError, match="start_boundary.*must be <="):
            ObservationWindow(
                window_id="w00",
                window_index=0,
                strategy="temporal",
                start_boundary="2026-02-01T00:00:00Z",
                end_boundary="2026-01-01T00:00:00Z",
            )

    def test_empty_observations(self) -> None:
        w = ObservationWindow(
            window_id="w00",
            window_index=0,
            strategy="temporal",
            start_boundary="2026-01-01T00:00:00Z",
            end_boundary="2026-01-31T23:59:59Z",
        )
        assert w.observation_count == 0

    def test_metrics_present(self) -> None:
        obs = [_make_observation(metric_id="M-01"), _make_observation(metric_id="M-02")]
        w = _make_window(observations=obs)
        assert len(w.observations) == 2


# ---------------------------------------------------------------------------
# ObservationCollection Tests
# ---------------------------------------------------------------------------


class TestObservationCollection:
    """ODSS §7 — Observation collection."""

    def test_creation(self) -> None:
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
        )
        assert c.repository_id == "test-repo"
        assert c.total_observations == 0

    def test_with_windows(self) -> None:
        w = _make_window()
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
            windows=[w],
        )
        assert c.total_observations == 1

    def test_get_window(self) -> None:
        w = _make_window(window_id="w00")
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
            windows=[w],
        )
        assert c.get_window("w00") is w
        assert c.get_window("w99") is None

    def test_get_observations_by_metric(self) -> None:
        obs1 = _make_observation(metric_id="M-01")
        obs2 = _make_observation(metric_id="M-02")
        w = _make_window(observations=[obs1, obs2])
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
            windows=[w],
        )
        m01_obs = c.get_observations_by_metric("M-01")
        assert len(m01_obs) == 1
        assert m01_obs[0].metric_id == "M-01"

    def test_get_observations_by_source(self) -> None:
        obs = _make_observation()
        w = _make_window(observations=[obs])
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
            windows=[w],
        )
        result = c.get_observations_by_source("commit", SAMPLE_COMMIT_SHA)
        assert len(result) == 1

    def test_get_all_observations(self) -> None:
        obs1 = _make_observation()
        obs2 = _make_observation()
        w1 = _make_window(window_id="w00", observations=[obs1])
        w2 = _make_window(window_id="w01", window_index=1, observations=[obs2])
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
            windows=[w1, w2],
        )
        all_obs = c.get_all_observations()
        assert len(all_obs) == 2

    def test_total_metrics_computed(self) -> None:
        obs1 = _make_observation(metric_id="M-01")
        obs2 = _make_observation(metric_id="M-02")
        w = _make_window(observations=[obs1, obs2])
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
            windows=[w],
        )
        assert c.total_metrics == 2

    def test_schema_version(self) -> None:
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test-repo",
            analysis_id="analysis-1",
        )
        assert c.schema_version == ODSS_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# create_observation Factory Tests
# ---------------------------------------------------------------------------


class TestCreateObservation:
    """Convenience factory for creating observations."""

    def test_creates_valid_observation(self) -> None:
        obs = create_observation(
            source_type="commit",
            source_id=SAMPLE_COMMIT_SHA,
            metric_id="M-02",
            value=100.0,
            timestamp=SAMPLE_TIMESTAMP,
        )
        assert obs.source_type == "commit"
        assert obs.value == 100.0
        assert obs.quality == "complete"

    def test_auto_generates_id(self) -> None:
        obs = create_observation(
            source_type="commit",
            source_id=SAMPLE_COMMIT_SHA,
            metric_id="M-02",
            value=1.0,
            timestamp=SAMPLE_TIMESTAMP,
        )
        expected = generate_observation_id("commit", SAMPLE_COMMIT_SHA, "M-02")
        assert obs.observation_id == expected

    def test_auto_assigns_unit(self) -> None:
        obs = create_observation(
            source_type="commit",
            source_id=SAMPLE_COMMIT_SHA,
            metric_id="M-02",
            value=1.0,
            timestamp=SAMPLE_TIMESTAMP,
        )
        assert obs.unit == "count"

    def test_custom_metadata(self) -> None:
        obs = create_observation(
            source_type="commit",
            source_id=SAMPLE_COMMIT_SHA,
            metric_id="M-02",
            value=1.0,
            timestamp=SAMPLE_TIMESTAMP,
            metadata={"commit_message": "test"},
        )
        assert obs.metadata["commit_message"] == "test"

    def test_provenance_included(self) -> None:
        obs = create_observation(
            source_type="commit",
            source_id=SAMPLE_COMMIT_SHA,
            metric_id="M-02",
            value=1.0,
            timestamp=SAMPLE_TIMESTAMP,
            seed=42,
        )
        assert obs.provenance.seed == 42
        assert obs.provenance.extractor_id == "test-extractor"


# ---------------------------------------------------------------------------
# Enum Tests
# ---------------------------------------------------------------------------


class TestEnums:
    """ODSS enums."""

    def test_source_types(self) -> None:
        assert SourceType.COMMIT.value == "commit"
        assert SourceType.FILE.value == "file"
        assert SourceType.BRANCH.value == "branch"
        assert SourceType.TAG.value == "tag"

    def test_quality_values(self) -> None:
        assert ObservationQuality.COMPLETE.value == "complete"
        assert ObservationQuality.ESTIMATED.value == "estimated"
        assert ObservationQuality.MISSING.value == "missing"
        assert ObservationQuality.DERIVED.value == "derived"

    def test_relationship_types(self) -> None:
        assert RelationshipType.DERIVED_FROM.value == "derived_from"
        assert RelationshipType.FILE_OF_COMMIT.value == "file_of_commit"


# ---------------------------------------------------------------------------
# Schema Version Test
# ---------------------------------------------------------------------------


class TestSchemaVersion:
    """ODSS schema versioning."""

    def test_schema_version_format(self) -> None:
        assert ODSS_SCHEMA_VERSION == "1.0.0"

    def test_collection_has_schema_version(self) -> None:
        c = ObservationCollection(
            collection_id="a" * 16,
            repository_id="test",
            analysis_id="test",
        )
        assert c.schema_version == "1.0.0"
