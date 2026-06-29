"""
MIIE v1.5 Observation Core — Canonical Observation Data Model.

Implements the ODSS v1.0 schema hierarchy:
  Repository → ObservationCollection → ObservationWindow → Observation

Reference: ODSS-v1.0, IMS-v1.0 Phase 1, PRD-v1.5 §20

This module is the single source of truth for observation domain objects.
Detectors, adapters, scoring engines, and evidence generators all consume
these types.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ODSS_SCHEMA_VERSION: str = "1.0.0"

_VALID_METRIC_IDS: frozenset[str] = frozenset(f"M-{i:02d}" for i in range(1, 8))

_SOURCE_TYPES: frozenset[str] = frozenset({"commit", "file", "branch", "tag"})

_QUALITY_VALUES: frozenset[str] = frozenset({"complete", "estimated", "missing", "derived"})

_UNIT_VALUES: frozenset[str] = frozenset({"count", "ratio", "percentage", "score", "hours", "lines", "bytes"})

# Per-metric unit mapping (ODSS §9.2.6)
_METRIC_UNITS: Dict[str, str] = {
    "M-01": "ratio",
    "M-02": "count",
    "M-03": "ratio",
    "M-04": "ratio",
    "M-05": "hours",
    "M-06": "ratio",
    "M-07": "ratio",
}

_COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_OBSERVATION_ID_RE = re.compile(r"^[0-9a-f]{16}$")
_WINDOW_ID_RE = re.compile(r"^w[0-9]+$")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SourceType(str, Enum):
    """ODSS §11 — Observation source classification."""

    COMMIT = "commit"
    FILE = "file"
    BRANCH = "branch"
    TAG = "tag"


class ObservationQuality(str, Enum):
    """ODSS §14 — Data quality indicator."""

    COMPLETE = "complete"
    ESTIMATED = "estimated"
    MISSING = "missing"
    DERIVED = "derived"


class RelationshipType(str, Enum):
    """ODSS §20 — Observation relationship types."""

    DERIVED_FROM = "derived_from"
    FILE_OF_COMMIT = "file_of_commit"
    BRANCH_OF_COMMIT = "branch_of_commit"
    TAG_OF_COMMIT = "tag_of_commit"


# ---------------------------------------------------------------------------
# Deterministic Observation ID
# ---------------------------------------------------------------------------


def generate_observation_id(source_type: str, source_id: str, metric_id: str) -> str:
    """Compute a deterministic 16-character hex observation ID.

    Formula (ODSS §10.2):
        observation_id = sha256(f"{source_type}:{source_id}:{metric_id}")[:16]

    Args:
        source_type: One of 'commit', 'file', 'branch', 'tag'.
        source_id: The source identifier (SHA, path, name).
        metric_id: Metric identifier (M-01 .. M-07).

    Returns:
        16-character lowercase hex string.

    Raises:
        ValueError: If inputs are invalid.
    """
    if source_type not in _SOURCE_TYPES:
        raise ValueError(f"Invalid source_type: {source_type!r}. Must be one of {_SOURCE_TYPES}")
    if not source_id:
        raise ValueError("source_id must be non-empty")
    if metric_id not in _VALID_METRIC_IDS:
        raise ValueError(f"Invalid metric_id: {metric_id!r}. Must be one of {_VALID_METRIC_IDS}")

    payload = f"{source_type}:{source_id}:{metric_id}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Supporting Data Classes (ODSS §19, §20, §18)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObservationProvenance:
    """ODSS §19 — How this observation was produced.

    Attributes:
        extractor_id: Identifier of the extractor that produced this observation.
        extraction_timestamp: When extraction occurred (ISO-8601).
        seed: Random seed used for deterministic extraction.
    """

    extractor_id: str
    extraction_timestamp: str
    seed: Optional[int] = None


@dataclass(frozen=True)
class ObservationStatistics:
    """ODSS §18 — Aggregated statistics for a window or collection.

    Attributes:
        mean: Arithmetic mean of observation values.
        std: Standard deviation of observation values.
        min_value: Minimum observation value.
        max_value: Maximum observation value.
        n: Number of observations.
    """

    mean: float
    std: float
    min_value: float
    max_value: float
    n: int

    def __post_init__(self) -> None:
        if self.n < 0:
            raise ValueError(f"n must be non-negative, got {self.n}")
        if not math.isfinite(self.mean):
            raise ValueError(f"mean must be finite, got {self.mean}")
        if not math.isfinite(self.std):
            raise ValueError(f"std must be finite, got {self.std}")


@dataclass(frozen=True)
class ObservationRelationship:
    """ODSS §20 — Link to a related observation.

    Attributes:
        relationship_type: Type of relationship.
        target_observation_id: ID of the related observation.
    """

    relationship_type: RelationshipType
    target_observation_id: str


# ---------------------------------------------------------------------------
# Core Observation (ODSS §9)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Observation:
    """ODSS §9 — The atomic data unit of the MIIE Observation Engine.

    Every observation represents a single data point extracted from a single
    source at a single point in time. Observations are immutable after creation.

    Attributes:
        observation_id: Deterministic 16-char hex ID (SHA-256-based).
        source_type: Classification of the source (commit, file, branch, tag).
        source_id: Specific source identifier (SHA, path, name).
        metric_id: Metric identifier (M-01 .. M-07).
        value: The numeric measurement.
        unit: Unit of measurement (count, ratio, percentage, etc.).
        timestamp: When the source was created (ISO-8601).
        quality: Data quality indicator (complete, estimated, missing, derived).
        metadata: Extractor-specific contextual information (optional).
        provenance: How this observation was produced.
        relationships: Links to related observations (optional).
        extensions: Future extension points (optional).
    """

    observation_id: str
    source_type: str
    source_id: str
    metric_id: str
    value: float
    unit: str
    timestamp: str
    quality: str
    provenance: ObservationProvenance
    metadata: Dict[str, Any] = field(default_factory=dict)
    relationships: List[ObservationRelationship] = field(default_factory=list)
    extensions: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate observation constraints per ODSS §9.2."""
        # observation_id
        if not _OBSERVATION_ID_RE.match(self.observation_id):
            raise ValueError(f"observation_id must match ^[0-9a-f]{{16}}$, got {self.observation_id!r}")

        # source_type
        if self.source_type not in _SOURCE_TYPES:
            raise ValueError(f"source_type must be one of {_SOURCE_TYPES}, got {self.source_type!r}")

        # source_id
        if not self.source_id:
            raise ValueError("source_id must be non-empty")

        # source_id format by type
        if self.source_type == "commit" and not _COMMIT_SHA_RE.match(self.source_id):
            raise ValueError(f"source_id for 'commit' must be a 40-char hex SHA, got {self.source_id!r}")

        # metric_id
        if self.metric_id not in _VALID_METRIC_IDS:
            raise ValueError(f"metric_id must be one of {_VALID_METRIC_IDS}, got {self.metric_id!r}")

        # value
        if not math.isfinite(self.value):
            raise ValueError(f"value must be finite (not NaN, not Inf), got {self.value}")

        # unit
        if self.unit not in _UNIT_VALUES:
            raise ValueError(f"unit must be one of {_UNIT_VALUES}, got {self.unit!r}")

        # unit-metric consistency
        expected_unit = _METRIC_UNITS.get(self.metric_id)
        if expected_unit and self.unit != expected_unit:
            raise ValueError(
                f"unit {self.unit!r} inconsistent with metric {self.metric_id!r}; " f"expected {expected_unit!r}"
            )

        # timestamp
        try:
            datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"timestamp must be a valid ISO-8601 datetime, got {self.timestamp!r}") from exc

        # quality
        if self.quality not in _QUALITY_VALUES:
            raise ValueError(f"quality must be one of {_QUALITY_VALUES}, got {self.quality!r}")


# ---------------------------------------------------------------------------
# ObservationWindow (ODSS §8)
# ---------------------------------------------------------------------------


@dataclass
class ObservationWindow:
    """ODSS §8 — Time-bounded or commit-bounded group of observations.

    Windows are the unit of analysis for detectors. Each window contains
    enough observations to support statistical inference.

    Attributes:
        window_id: Unique window identifier (e.g., 'w00', 'w01').
        window_index: Zero-based index of this window in the collection.
        strategy: Windowing strategy ('temporal', 'commit_count', 'hybrid').
        start_boundary: Inclusive start of the window (ISO-8601).
        end_boundary: Inclusive end of the window (ISO-8601).
        observations: Observations in this window.
        start_commit: First commit SHA (optional, for commit-based windows).
        end_commit: Last commit SHA (optional, for commit-based windows).
        metrics_present: Distinct metric IDs in this window.
        statistics: Aggregated statistics for this window (optional).
        metadata: Window-specific metadata (optional).
    """

    window_id: str
    window_index: int
    strategy: str
    start_boundary: str
    end_boundary: str
    observations: List[Observation] = field(default_factory=list)
    start_commit: Optional[str] = None
    end_commit: Optional[str] = None
    metrics_present: List[str] = field(default_factory=list)
    statistics: Optional[ObservationStatistics] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def observation_count(self) -> int:
        """Number of observations in this window."""
        return len(self.observations)

    def __post_init__(self) -> None:
        """Validate window constraints per ODSS §8.4."""
        # window_id format
        if not _WINDOW_ID_RE.match(self.window_id):
            raise ValueError(f"window_id must match ^w[0-9]+$, got {self.window_id!r}")

        # window_index
        if self.window_index < 0:
            raise ValueError(f"window_index must be non-negative, got {self.window_index}")

        # strategy
        valid_strategies = {"temporal", "commit_count", "hybrid"}
        if self.strategy not in valid_strategies:
            raise ValueError(f"strategy must be one of {valid_strategies}, got {self.strategy!r}")

        # boundaries
        try:
            start = datetime.fromisoformat(self.start_boundary.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.end_boundary.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as exc:
            raise ValueError("start_boundary and end_boundary must be valid ISO-8601 datetimes") from exc

        if start > end:
            raise ValueError(
                f"start_boundary ({self.start_boundary}) must be <= " f"end_boundary ({self.end_boundary})"
            )

        # observation_count consistency
        if len(self.observations) != self.observation_count:
            raise ValueError(
                f"observation_count ({self.observation_count}) != " f"len(observations) ({len(self.observations)})"
            )


# ---------------------------------------------------------------------------
# ObservationCollection (ODSS §7)
# ---------------------------------------------------------------------------


@dataclass
class ObservationCollection:
    """ODSS §7 — Indexed container for all observations in a repository analysis.

    Provides lookup by window, by metric, and by source.

    Attributes:
        collection_id: Deterministic ID (SHA-256-based).
        repository_id: Reference to parent repository.
        analysis_id: Reference to analysis run.
        windows: Ordered list of observation windows.
        total_observations: Total count across all windows.
        total_metrics: Count of distinct metric IDs.
        extraction_timestamp: When extraction completed (ISO-8601).
        schema_version: ODSS schema version.
    """

    collection_id: str
    repository_id: str
    analysis_id: str
    windows: List[ObservationWindow] = field(default_factory=list)
    total_observations: int = 0
    total_metrics: int = 0
    extraction_timestamp: str = ""
    schema_version: str = ODSS_SCHEMA_VERSION

    # Internal indices
    _window_index: Dict[str, ObservationWindow] = field(default_factory=dict, repr=False)
    _metric_index: Dict[str, List[Observation]] = field(default_factory=dict, repr=False)
    _source_index: Dict[Tuple[str, str], List[Observation]] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Build internal indices."""
        self._rebuild_indices()

    def _rebuild_indices(self) -> None:
        """Rebuild all internal indices from current windows."""
        self._window_index.clear()
        self._metric_index.clear()
        self._source_index.clear()

        for window in self.windows:
            self._window_index[window.window_id] = window
            for obs in window.observations:
                # By metric
                if obs.metric_id not in self._metric_index:
                    self._metric_index[obs.metric_id] = []
                self._metric_index[obs.metric_id].append(obs)

                # By source
                key = (obs.source_type, obs.source_id)
                if key not in self._source_index:
                    self._source_index[key] = []
                self._source_index[key].append(obs)

        # Recompute totals
        self.total_observations = sum(w.observation_count for w in self.windows)
        self.total_metrics = len(self._metric_index)

    # -- Lookup methods ---------------------------------------------------

    def get_window(self, window_id: str) -> Optional[ObservationWindow]:
        """Get a window by its ID.

        Args:
            window_id: The window identifier (e.g., 'w00').

        Returns:
            The ObservationWindow, or None if not found.
        """
        return self._window_index.get(window_id)

    def get_observations_by_metric(self, metric_id: str) -> List[Observation]:
        """Get all observations for a specific metric across all windows.

        Args:
            metric_id: The metric identifier (e.g., 'M-02').

        Returns:
            List of observations for that metric.
        """
        return list(self._metric_index.get(metric_id, []))

    def get_observations_by_source(self, source_type: str, source_id: str) -> List[Observation]:
        """Get all observations for a specific source across all windows.

        Args:
            source_type: The source type (e.g., 'commit').
            source_id: The source identifier (e.g., commit SHA).

        Returns:
            List of observations for that source.
        """
        return list(self._source_index.get((source_type, source_id), []))

    def get_all_observations(self) -> List[Observation]:
        """Get all observations across all windows, sorted by timestamp.

        Returns:
            Flat list of all observations.
        """
        result: List[Observation] = []
        for window in self.windows:
            result.extend(window.observations)
        return result


# ---------------------------------------------------------------------------
# Helper: Create a minimal valid observation (for testing)
# ---------------------------------------------------------------------------


def create_observation(
    source_type: str,
    source_id: str,
    metric_id: str,
    value: float,
    timestamp: str,
    *,
    quality: str = "complete",
    extractor_id: str = "test-extractor",
    seed: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Observation:
    """Create a valid Observation with auto-generated ID and provenance.

    This is a convenience factory for tests and prototyping.

    Args:
        source_type: One of 'commit', 'file', 'branch', 'tag'.
        source_id: The source identifier.
        metric_id: Metric identifier (M-01 .. M-07).
        value: The numeric measurement.
        timestamp: ISO-8601 datetime string.
        quality: Data quality indicator.
        extractor_id: Identifier of the extractor.
        seed: Random seed.
        metadata: Optional metadata dict.

    Returns:
        A fully validated Observation instance.
    """
    obs_id = generate_observation_id(source_type, source_id, metric_id)
    unit = _METRIC_UNITS.get(metric_id, "count")
    provenance = ObservationProvenance(
        extractor_id=extractor_id,
        extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        seed=seed,
    )
    return Observation(
        observation_id=obs_id,
        source_type=source_type,
        source_id=source_id,
        metric_id=metric_id,
        value=value,
        unit=unit,
        timestamp=timestamp,
        quality=quality,
        provenance=provenance,
        metadata=metadata or {},
    )
