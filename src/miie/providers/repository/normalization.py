"""
Normalizes repository metadata into MIIE Observation objects.

Every observation produced by the RepositoryMetadataProvider passes
through this module to ensure consistent structure and provenance.
"""

from __future__ import annotations

import datetime
from typing import Dict, Optional

from miie.processing.observation.models import (
    Observation,
    ObservationProvenance,
    generate_observation_id,
)
from miie.providers.repository.models import RepositoryMetadata


def _ts(dt: Optional[datetime.datetime]) -> str:
    """Return ISO-8601 string for a datetime, or current time."""
    if dt is not None:
        return dt.isoformat()
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _hours_between(
    earlier: Optional[datetime.datetime],
    later: Optional[datetime.datetime],
) -> float:
    """Hours between two datetimes (always positive)."""
    if earlier is None or later is None:
        return 0.0
    delta = later - earlier
    return max(delta.total_seconds() / 3600.0, 0.0)


# ------------------------------------------------------------------
# Metadata observations
# ------------------------------------------------------------------


def normalize_repository_size(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-01: Repository size in bytes."""
    return Observation(
        observation_id=generate_observation_id("branch", metadata.full_name, "M-01"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-01",
        value=float(metadata.size),
        unit="bytes",
        timestamp=_ts(metadata.updated_at),
        quality="complete",
        provenance=provenance,
        metadata=_repo_metadata(metadata),
    )


def normalize_stars_count(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-02: Repository stars count."""
    return Observation(
        observation_id=generate_observation_id("branch", f"{metadata.full_name}-stars", "M-02"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-02",
        value=float(metadata.stars),
        unit="count",
        timestamp=_ts(metadata.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_repo_metadata(metadata),
            "metric_type": "stars",
        },
    )


def normalize_forks_count(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-02: Repository forks count."""
    return Observation(
        observation_id=generate_observation_id("branch", f"{metadata.full_name}-forks", "M-02"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-02",
        value=float(metadata.fork_count),
        unit="count",
        timestamp=_ts(metadata.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_repo_metadata(metadata),
            "metric_type": "forks",
        },
    )


def normalize_watchers_count(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-02: Repository watchers count."""
    return Observation(
        observation_id=generate_observation_id("branch", f"{metadata.full_name}-watchers", "M-02"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-02",
        value=float(metadata.watchers),
        unit="count",
        timestamp=_ts(metadata.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_repo_metadata(metadata),
            "metric_type": "watchers",
        },
    )


def normalize_open_issues_count(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-02: Repository open issues count."""
    return Observation(
        observation_id=generate_observation_id("branch", f"{metadata.full_name}-issues", "M-02"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-02",
        value=float(metadata.open_issues),
        unit="count",
        timestamp=_ts(metadata.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_repo_metadata(metadata),
            "metric_type": "open_issues",
        },
    )


def normalize_last_push_latency(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-05: Time since last push in hours."""
    now = datetime.datetime.now(datetime.timezone.utc)
    latency = _hours_between(metadata.pushed_at, now)
    return Observation(
        observation_id=generate_observation_id("branch", f"{metadata.full_name}-last-push", "M-05"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-05",
        value=latency,
        unit="hours",
        timestamp=_ts(metadata.pushed_at),
        quality="complete" if metadata.pushed_at else "estimated",
        provenance=provenance,
        metadata={
            **_repo_metadata(metadata),
            "metric_type": "last_push_latency",
            "last_push_timestamp": _ts(metadata.pushed_at),
        },
    )


def normalize_last_update_latency(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-05: Time since last update in hours."""
    now = datetime.datetime.now(datetime.timezone.utc)
    latency = _hours_between(metadata.updated_at, now)
    return Observation(
        observation_id=generate_observation_id("branch", f"{metadata.full_name}-last-update", "M-05"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-05",
        value=latency,
        unit="hours",
        timestamp=_ts(metadata.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_repo_metadata(metadata),
            "metric_type": "last_update_latency",
            "last_update_timestamp": _ts(metadata.updated_at),
        },
    )


def normalize_repository_age(
    metadata: RepositoryMetadata,
    provenance: ObservationProvenance,
) -> Observation:
    """M-07: Repository age in hours since creation."""
    now = datetime.datetime.now(datetime.timezone.utc)
    age = _hours_between(metadata.created_at, now)
    return Observation(
        observation_id=generate_observation_id("branch", f"{metadata.full_name}-age", "M-07"),
        source_type="branch",
        source_id=metadata.full_name,
        metric_id="M-07",
        value=age,
        unit="hours",
        timestamp=_ts(metadata.created_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_repo_metadata(metadata),
            "metric_type": "repository_age",
            "created_timestamp": _ts(metadata.created_at),
        },
    )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _repo_metadata(metadata: RepositoryMetadata) -> Dict[str, str]:
    """Build common repository metadata dict."""
    languages_str = "; ".join(f"{lang}:{bytes_val}" for lang, bytes_val in metadata.languages.items())
    topics_str = ", ".join(sorted(metadata.topics))

    result: Dict[str, str] = {
        "repository_name": metadata.name,
        "full_name": metadata.full_name,
        "default_branch": metadata.default_branch,
        "visibility": metadata.visibility,
        "is_archived": str(metadata.is_archived).lower(),
        "is_fork": str(metadata.is_fork).lower(),
        "stars": str(metadata.stars),
        "fork_count": str(metadata.fork_count),
        "watchers": str(metadata.watchers),
        "open_issues": str(metadata.open_issues),
        "size": str(metadata.size),
    }

    if metadata.description:
        result["description"] = metadata.description
    if metadata.homepage:
        result["homepage"] = metadata.homepage
    if metadata.primary_language:
        result["primary_language"] = metadata.primary_language
    if languages_str:
        result["languages"] = languages_str
    if metadata.license:
        result["license"] = metadata.license
    if topics_str:
        result["topics"] = topics_str
    if metadata.default_branch_protection is not None:
        result["default_branch_protection"] = str(metadata.default_branch_protection).lower()

    return result
