"""
MIIE v1.6 Observation Provider Framework — Provider registration metadata.

Defines metadata structures for provider registration and registry-level
summary reporting. Implements OPR §6.1 and OPR §7.1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, FrozenSet, List, Sequence

from miie.providers.context import (
    CAPABILITY_GIT_NATIVE,
    CAPABILITY_LOCAL_ONLY,
    METRIC_ID_M01,
    METRIC_ID_M02,
    METRIC_ID_M03,
    METRIC_ID_M06,
    METRIC_ID_M07,
)

# ---------------------------------------------------------------------------
# Dataclasses — Provider Metadata (OPR §6.1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderMetadata:
    """OPR §6.1 — Immutable metadata describing a registered provider.

    Carries identity, capability declarations, and operational requirements
    for a provider. Used for registry indexing, discovery, and display.
    """

    provider_id: str
    name: str
    description: str
    version: str
    author: str
    supported_metrics: FrozenSet[str]
    supported_source_types: FrozenSet[str]
    capabilities: FrozenSet[str]
    requires_network: bool
    requires_api_token: bool
    tags: FrozenSet[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id must not be empty")
        if not self.name:
            raise ValueError("name must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")

    @property
    def is_local_only(self) -> bool:
        """Check if provider operates without network access."""
        return not self.requires_network

    @property
    def metric_count(self) -> int:
        """Return the number of supported metrics."""
        return len(self.supported_metrics)

    def supports_metric(self, metric_id: str) -> bool:
        """Check if this provider supports a given metric."""
        return metric_id in self.supported_metrics

    def supports_source_type(self, source_type: str) -> bool:
        """Check if this provider supports a given source type."""
        return source_type in self.supported_source_types

    def has_capability(self, capability: str) -> bool:
        """Check if this provider has a specific capability."""
        return capability in self.capabilities

    def has_tag(self, tag: str) -> bool:
        """Check if this provider has a specific tag."""
        return tag in self.tags


# ---------------------------------------------------------------------------
# Dataclasses — Registry Metadata (OPR §7.1)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegistryMetadata:
    """OPR §7.1 — Metadata for the provider registry itself.

    Tracks registry versioning, provider count, and temporal information
    about registration activity.
    """

    registry_version: str
    provider_count: int
    registered_at: datetime
    last_updated: datetime

    def __post_init__(self) -> None:
        if not self.registry_version:
            raise ValueError("registry_version must not be empty")
        if self.provider_count < 0:
            raise ValueError("provider_count must not be negative")
        if self.last_updated < self.registered_at:
            raise ValueError("last_updated must not be before registered_at")

    @property
    def age_seconds(self) -> float:
        """Return seconds elapsed since registration."""
        now = datetime.now(timezone.utc)
        return (now - self.registered_at).total_seconds()

    @property
    def staleness_seconds(self) -> float:
        """Return seconds elapsed since last update."""
        now = datetime.now(timezone.utc)
        return (now - self.last_updated).total_seconds()


# ---------------------------------------------------------------------------
# Factory Functions
# ---------------------------------------------------------------------------


def create_git_provider_metadata() -> ProviderMetadata:
    """Create metadata for the built-in Git observation provider.

    Returns:
        ProviderMetadata configured for git-native commit, branch, and
        tag observation extraction.
    """
    return ProviderMetadata(
        provider_id="git-native",
        name="Git Observation Provider",
        description=(
            "Extracts commit, branch, and tag observations directly from "
            "local Git repositories via command-line interface."
        ),
        version="1.6.0",
        author="MIIE Core Team",
        supported_metrics=frozenset(
            {
                METRIC_ID_M01,
                METRIC_ID_M02,
                METRIC_ID_M03,
                METRIC_ID_M06,
                METRIC_ID_M07,
            }
        ),
        supported_source_types=frozenset(
            {
                "git-repository",
                "git-log",
                "git-branch",
                "git-tag",
            }
        ),
        capabilities=frozenset(
            {
                CAPABILITY_GIT_NATIVE,
                CAPABILITY_LOCAL_ONLY,
            }
        ),
        requires_network=False,
        requires_api_token=False,
        tags=frozenset({"builtin", "git", "local"}),
    )


def create_metadata_summary(
    entries: Sequence[ProviderMetadata],
) -> Dict[str, Any]:
    """Create a summary dict of all registered provider metadata.

    Aggregates counts, collects unique values across providers, and
    produces a machine-readable summary suitable for logging or API
    responses.

    Args:
        entries: Sequence of ProviderMetadata to summarize.

    Returns:
        Dict with keys: provider_count, total_metrics, total_source_types,
        total_capabilities, all_tags, providers (list of id/name/version
        triples), requires_network_count, requires_api_token_count.
    """
    all_metrics: set[str] = set()
    all_source_types: set[str] = set()
    all_capabilities: set[str] = set()
    all_tags: set[str] = set()
    provider_summaries: List[Dict[str, str]] = []
    network_count = 0
    token_count = 0

    for entry in entries:
        all_metrics.update(entry.supported_metrics)
        all_source_types.update(entry.supported_source_types)
        all_capabilities.update(entry.capabilities)
        all_tags.update(entry.tags)
        provider_summaries.append(
            {
                "provider_id": entry.provider_id,
                "name": entry.name,
                "version": entry.version,
            }
        )
        if entry.requires_network:
            network_count += 1
        if entry.requires_api_token:
            token_count += 1

    return {
        "provider_count": len(entries),
        "total_metrics": len(all_metrics),
        "total_source_types": len(all_source_types),
        "total_capabilities": len(all_capabilities),
        "all_tags": sorted(all_tags),
        "providers": provider_summaries,
        "requires_network_count": network_count,
        "requires_api_token_count": token_count,
    }
