"""
Repository Metadata Observation Provider — PR-11D.

Provides RepositoryMetadataProvider for extracting repository-level
characteristics (size, stars, forks, language, license, timestamps)
from GitHub repositories via the REST API.
"""

from miie.providers.repository.health import RepositoryProviderHealth
from miie.providers.repository.models import RepositoryMetadata
from miie.providers.repository.normalization import (
    normalize_forks_count,
    normalize_last_push_latency,
    normalize_last_update_latency,
    normalize_open_issues_count,
    normalize_stars_count,
    normalize_watchers_count,
)
from miie.providers.repository.provider import PROVIDER_ID as REPO_METADATA_PROVIDER_ID
from miie.providers.repository.provider import (
    RepositoryMetadataProvider,
    repository_metadata_provider_capabilities,
)
from miie.providers.repository.validation import RepositoryProviderValidator

__all__ = [
    "RepositoryMetadataProvider",
    "RepositoryProviderHealth",
    "RepositoryProviderValidator",
    "RepositoryMetadata",
    "REPO_METADATA_PROVIDER_ID",
    "repository_metadata_provider_capabilities",
    "normalize_stars_count",
    "normalize_forks_count",
    "normalize_watchers_count",
    "normalize_open_issues_count",
    "normalize_last_push_latency",
    "normalize_last_update_latency",
]
