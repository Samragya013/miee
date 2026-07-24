"""
Repository Metadata Observation Provider — PR-11D.

Extracts long-lived repository characteristics (size, stars, forks,
language, license, timestamps, etc.) from GitHub repositories via
the REST API.

Becomes shared context for all future providers.

Reference: OPA-v1.0 §9, PR-11D specification.
"""

from __future__ import annotations

import datetime
import logging
from typing import Dict, List, Optional

from miie.processing.observation.models import (
    Observation,
    ObservationProvenance,
)
from miie.providers.base import BaseObservationProvider, ProviderMixin
from miie.providers.context import (
    CAPABILITY_API_REQUIRED,
    CAPABILITY_BATCH,
    CAPABILITY_REMOTE_ONLY,
    ExtractionResult,
    ProviderCapability,
    ProviderContext,
    ProviderHealth,
    ProviderState,
    QualityState,
)
from miie.providers.exceptions import ExtractionError
from miie.providers.github.api import GitHubAPIError, GitHubClient
from miie.providers.github.authentication import GitHubAuth
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
from miie.providers.repository.validation import (
    RepositoryProviderValidator,
    _parse_owner_repo,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROVIDER_ID: str = "repository.metadata.observation.v1"

_METRIC_UNITS: Dict[str, str] = {
    "M-02": "count",
    "M-05": "hours",
}

_SUPPORTED_METRICS: frozenset[str] = frozenset({"M-02", "M-05"})


# ---------------------------------------------------------------------------
# Capability factory
# ---------------------------------------------------------------------------


def repository_metadata_provider_capabilities() -> ProviderCapability:
    """Return the capability declaration for the Repository Metadata provider."""
    return ProviderCapability(
        supported_metrics=_SUPPORTED_METRICS,
        supported_source_types=frozenset({"repository"}),
        capabilities=frozenset({CAPABILITY_API_REQUIRED, CAPABILITY_REMOTE_ONLY, CAPABILITY_BATCH}),
        requires_network=True,
        requires_api_token=False,
    )


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------


class RepositoryMetadataProvider(BaseObservationProvider, ProviderMixin):
    """OPA §9 — Repository Metadata observation provider.

    Extracts repository-level characteristics from GitHub via the
    REST API.  Follows the same lifecycle pattern as other providers::

        provider = RepositoryMetadataProvider()
        provider.initialize(context)     # → READY
        result = provider.extract_observations(context, ["M-01", "M-02"])
        provider.dispose()               # → DISPOSED
    """

    def __init__(
        self,
        auth: Optional[GitHubAuth] = None,
        client: Optional[GitHubClient] = None,
    ) -> None:
        super().__init__(PROVIDER_ID, repository_metadata_provider_capabilities())
        self._auth = auth or GitHubAuth()
        self._client = client or GitHubClient(auth=self._auth)
        self._health = RepositoryProviderHealth()
        self._validator: Optional[RepositoryProviderValidator] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self, context: ProviderContext) -> None:
        """Validate repository accessibility and API health."""
        self._state: ProviderState
        if self._state == ProviderState.DISPOSED:
            from miie.providers.exceptions import ProviderDisposedError

            raise ProviderDisposedError(f"Provider {self._provider_id} has been disposed")

        self._state = ProviderState.ACTIVE
        self._validator = RepositoryProviderValidator(self._client)

        try:
            repo_result = self._validator.validate_repository(context)
            if not repo_result.is_valid:
                self._state = ProviderState.FAILED
                raise ExtractionError(
                    f"Repository validation failed: " f"{'; '.join(repo_result.violations)}",
                    error_code="INIT_FAILED",
                )

            rate_result = self._validator.validate_rate_limit()
            if not rate_result.is_valid:
                self._state = ProviderState.FAILED
                raise ExtractionError(
                    f"Rate limit check failed: " f"{'; '.join(rate_result.violations)}",
                    error_code="RATE_LIMIT_EXCEEDED",
                )
        except ExtractionError:
            raise
        except Exception as exc:
            self._state = ProviderState.FAILED
            raise ExtractionError(
                f"Initialization failed: {exc}",
                error_code="INIT_FAILED",
                cause=exc,
            ) from exc

        self._state = ProviderState.READY
        logger.info(
            "Provider %s initialized for %s",
            self._provider_id,
            context.repository_id,
        )

    def health_check(self) -> ProviderHealth:
        """Return current health snapshot."""
        return self._health.snapshot()

    def dispose(self) -> None:
        """Release resources."""
        self._state = ProviderState.DISPOSED
        logger.info("Provider %s disposed", self._provider_id)

    # ------------------------------------------------------------------
    # Core extraction
    # ------------------------------------------------------------------

    def extract(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Delegate to extract_observations (BaseObservationProvider ABC)."""
        return self.extract_observations(context, metric_ids)

    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract repository metadata observations from GitHub.

        Fetches repository metadata and normalizes it into MIIE
        Observations for supported metrics.
        """
        if self._state == ProviderState.DISPOSED:
            from miie.providers.exceptions import ProviderDisposedError

            raise ProviderDisposedError(f"Provider {self._provider_id} has been disposed")

        requested = [m for m in metric_ids if m in _SUPPORTED_METRICS]
        if not requested:
            return ExtractionResult(
                provider_id=self._provider_id,
                metric_id=metric_ids[0] if metric_ids else "M-01",
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
            )

        owner, repo = _parse_owner_repo(context.repository_id)
        if not owner or not repo:
            return ExtractionResult(
                provider_id=self._provider_id,
                metric_id=requested[0],
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
                warnings=[f"Cannot parse owner/repo from {context.repository_id}"],
            )

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        provenance = ObservationProvenance(
            extractor_id=self._provider_id,
            extraction_timestamp=now_iso,
        )

        try:
            raw_metadata = self._client.get_repository(owner, repo)
            metadata = RepositoryMetadata.from_api(raw_metadata)
        except GitHubAPIError as exc:
            self._health.record_failure(str(exc))
            return ExtractionResult(
                provider_id=self._provider_id,
                metric_id=requested[0],
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
                warnings=[f"GitHub API error: {str(exc)}"],
                metadata={"error": str(exc), "status_code": exc.status_code},
            )

        # Validate metadata
        if self._validator:
            meta_result = self._validator.validate_metadata(metadata)
            if not meta_result.is_valid:
                self._health.record_failure(f"Metadata validation failed: " f"{'; '.join(meta_result.violations)}")
                return ExtractionResult(
                    provider_id=self._provider_id,
                    metric_id=requested[0],
                    observations=(),
                    quality_state=QualityState.MISSING,
                    confidence=0.0,
                    warnings=meta_result.violations,
                )

        # Generate observations
        all_observations: List[Observation] = []
        warnings: List[str] = []

        for metric_id in requested:
            observations = self._generate_observations(metadata, provenance, metric_id)
            all_observations.extend(observations)

        # Quality assessment
        quality, confidence = self._assess_quality(metadata, all_observations)

        # Calculate completeness
        expected_fields = 14
        present_fields = sum(
            1
            for field in [
                metadata.name,
                metadata.description,
                metadata.homepage,
                metadata.primary_language,
                metadata.license,
                metadata.topics,
                metadata.pushed_at,
                metadata.default_branch,
            ]
            if field
        )
        completeness = present_fields / expected_fields

        self._health.record_success(metadata_completeness=completeness)

        return ExtractionResult(
            provider_id=self._provider_id,
            metric_id=requested[0],
            observations=tuple(all_observations),
            quality_state=quality,
            confidence=confidence,
            warnings=warnings,
            metadata={
                "repository_name": metadata.full_name,
                "total_observations": len(all_observations),
                "supported_metrics": sorted(requested),
                "metadata_completeness": completeness,
                "is_archived": metadata.is_archived,
                "is_fork": metadata.is_fork,
            },
        )

    # ------------------------------------------------------------------
    # Internal observation generation
    # ------------------------------------------------------------------

    def _generate_observations(
        self,
        metadata: RepositoryMetadata,
        provenance: ObservationProvenance,
        metric_id: str,
    ) -> List[Observation]:
        """Generate observations for a specific metric."""
        if metric_id == "M-02":
            return [
                normalize_stars_count(metadata, provenance),
                normalize_forks_count(metadata, provenance),
                normalize_watchers_count(metadata, provenance),
                normalize_open_issues_count(metadata, provenance),
            ]
        elif metric_id == "M-05":
            return [
                normalize_last_push_latency(metadata, provenance),
                normalize_last_update_latency(metadata, provenance),
            ]
        return []

    # ------------------------------------------------------------------
    # Quality assessment
    # ------------------------------------------------------------------

    def _assess_quality(
        self,
        metadata: RepositoryMetadata,
        observations: List[Observation],
    ) -> tuple[QualityState, float]:
        """Derive quality state and confidence from extraction results."""
        if not observations:
            return QualityState.MISSING, 0.0

        # Check metadata completeness
        required_fields = [
            metadata.name,
            metadata.full_name,
            metadata.default_branch,
        ]
        missing_required = sum(1 for f in required_fields if not f)

        if missing_required > 0:
            return QualityState.DEGRADED, 0.5

        # Check optional fields
        optional_fields = [
            metadata.description,
            metadata.primary_language,
            metadata.license,
            metadata.topics,
            metadata.pushed_at,
        ]
        present_optional = sum(1 for f in optional_fields if f)
        completeness = present_optional / len(optional_fields)

        if completeness >= 0.8:
            return QualityState.COMPLETE, 1.0
        elif completeness >= 0.4:
            return QualityState.DEGRADED, 0.5 + completeness * 0.5
        else:
            return QualityState.DEGRADED, max(0.3, completeness)
