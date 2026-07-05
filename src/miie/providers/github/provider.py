"""
GitHub Pull Request Observation Provider — PR-11B.

Extracts PR creation, merge, close, review, and participation
observations from GitHub repositories via the REST API.

Implements the Observation Provider Framework contracts exactly as
GitObservationProvider does, but for remote GitHub PR data.

Reference: OPA-v1.0 §9, PR-11B specification.
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
from miie.providers.github.health import GitHubProviderHealth
from miie.providers.github.models import (
    PullRequest,
    PullRequestState,
    Review,
)
from miie.providers.github.normalization import (
    normalize_pr_close,
    normalize_pr_creation,
    normalize_pr_draft,
    normalize_pr_merge,
    normalize_review,
    normalize_review_iterations,
    normalize_reviewer_count,
)
from miie.providers.github.validation import (
    GitHubProviderValidator,
    _parse_owner_repo,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROVIDER_ID: str = "github.pr.observation.v1"

_METRIC_UNITS: Dict[str, str] = {
    "M-02": "count",
    "M-05": "hours",
}

_SUPPORTED_METRICS: frozenset[str] = frozenset({"M-02", "M-05"})


# ---------------------------------------------------------------------------
# Capability factory
# ---------------------------------------------------------------------------


def github_pr_provider_capabilities() -> ProviderCapability:
    """Return the capability declaration for the GitHub PR provider."""
    return ProviderCapability(
        supported_metrics=_SUPPORTED_METRICS,
        supported_source_types=frozenset({"pull_request", "review"}),
        capabilities=frozenset({CAPABILITY_API_REQUIRED, CAPABILITY_REMOTE_ONLY, CAPABILITY_BATCH}),
        requires_network=True,
        requires_api_token=False,
    )


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------


class GitHubPullRequestProvider(BaseObservationProvider, ProviderMixin):
    """OPA §9 — GitHub Pull Request observation provider.

    Extracts PR and review observations from a GitHub repository via the
    REST API.  Follows the same lifecycle pattern as GitObservationProvider::

        provider = GitHubPullRequestProvider()
        provider.initialize(context)     # → READY
        result = provider.extract_observations(context, ["M-02", "M-05"])
        provider.dispose()               # → DISPOSED
    """

    def __init__(
        self,
        auth: Optional[GitHubAuth] = None,
        client: Optional[GitHubClient] = None,
    ) -> None:
        super().__init__(PROVIDER_ID, github_pr_provider_capabilities())
        self._auth = auth or GitHubAuth()
        self._client = client or GitHubClient(auth=self._auth)
        self._health = GitHubProviderHealth()
        self._validator: Optional[GitHubProviderValidator] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self, context: ProviderContext) -> None:
        """Validate repository accessibility and API health."""
        if self._state == ProviderState.DISPOSED:
            from miie.providers.exceptions import ProviderDisposedError

            raise ProviderDisposedError(f"Provider {self._provider_id} has been disposed")

        self._state = ProviderState.ACTIVE
        self._validator = GitHubProviderValidator(self._client)

        try:
            repo_result = self._validator.validate_repository(context)
            if not repo_result.is_valid:
                self._state = ProviderState.FAILED
                raise ExtractionError(
                    f"Repository validation failed: {'; '.join(repo_result.violations)}",
                    error_code="INIT_FAILED",
                )

            rate_result = self._validator.validate_rate_limit()
            if not rate_result.is_valid:
                self._state = ProviderState.FAILED
                raise ExtractionError(
                    f"Rate limit check failed: {'; '.join(rate_result.violations)}",
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
        logger.info("Provider %s initialized for %s", self._provider_id, context.repository_id)

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
        """Extract PR and review observations from GitHub.

        Fetches all pull requests, then fetches reviews for each PR,
        and normalizes everything into MIIE Observations.
        """
        if self._state == ProviderState.DISPOSED:
            from miie.providers.exceptions import ProviderDisposedError

            raise ProviderDisposedError(f"Provider {self._provider_id} has been disposed")

        requested = [m for m in metric_ids if m in _SUPPORTED_METRICS]
        if not requested:
            return ExtractionResult(
                provider_id=self._provider_id,
                metric_id=metric_ids[0] if metric_ids else "M-02",
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

        all_observations: List[Observation] = []
        warnings: List[str] = []

        try:
            prs = self._fetch_pull_requests(owner, repo, context)
            for pr in prs:
                pr_observations = self._process_pr(pr, owner, repo, provenance, requested)
                all_observations.extend(pr_observations)
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

        # Quality assessment
        quality, confidence = self._assess_quality(all_observations, prs)

        self._health.record_success()

        return ExtractionResult(
            provider_id=self._provider_id,
            metric_id=requested[0],
            observations=tuple(all_observations),
            quality_state=quality,
            confidence=confidence,
            warnings=warnings,
            metadata={
                "total_prs": len(prs),
                "total_observations": len(all_observations),
                "supported_metrics": sorted(requested),
            },
        )

    # ------------------------------------------------------------------
    # Internal fetching
    # ------------------------------------------------------------------

    def _fetch_pull_requests(
        self,
        owner: str,
        repo: str,
        context: ProviderContext,
    ) -> List[PullRequest]:
        """Fetch and normalize pull requests from GitHub."""
        raw_prs = self._client.list_pull_requests(
            owner,
            repo,
            state="all",
            since=context.since,
        )
        result: List[PullRequest] = []
        for raw in raw_prs:
            try:
                pr = PullRequest.from_api(raw)
                result.append(pr)
            except Exception as exc:
                logger.warning("Skipping malformed PR: %s", exc)
        return result

    def _process_pr(
        self,
        pr: PullRequest,
        owner: str,
        repo: str,
        provenance: ObservationProvenance,
        requested: List[str],
    ) -> List[Observation]:
        """Process a single PR into observations."""
        observations: List[Observation] = []

        # PR creation observation
        if "M-02" in requested:
            observations.append(normalize_pr_creation(pr, provenance))

        # PR state observations
        if pr.merged and "M-05" in requested:
            observations.append(normalize_pr_merge(pr, provenance))
        elif pr.state == PullRequestState.CLOSED and "M-05" in requested:
            observations.append(normalize_pr_close(pr, provenance))

        if pr.draft and "M-02" in requested:
            observations.append(normalize_pr_draft(pr, provenance))

        # Fetch reviews for this PR
        try:
            reviews = self._fetch_reviews(owner, repo, pr.number)
            if reviews and "M-05" in requested:
                unique_reviewers = {r.user.login for r in reviews}
                observations.append(normalize_reviewer_count(pr, len(unique_reviewers), provenance))
                observations.append(normalize_review_iterations(pr, len(reviews), provenance))
                for review in reviews:
                    observations.append(normalize_review(review, pr, provenance))
        except GitHubAPIError as exc:
            logger.warning("Cannot fetch reviews for PR #%d: %s", pr.number, str(exc))

        return observations

    def _fetch_reviews(
        self,
        owner: str,
        repo: str,
        pr_number: int,
    ) -> List[Review]:
        """Fetch and normalize reviews for a PR."""
        raw_reviews = self._client.list_pull_request_reviews(owner, repo, pr_number)
        result: List[Review] = []
        for raw in raw_reviews:
            try:
                review = Review.from_api(raw, pr_number)
                result.append(review)
            except Exception as exc:
                logger.warning("Skipping malformed review: %s", exc)
        return result

    # ------------------------------------------------------------------
    # Quality assessment
    # ------------------------------------------------------------------

    def _assess_quality(
        self,
        observations: List[Observation],
        prs: List[PullRequest],
    ) -> tuple[QualityState, float]:
        """Derive quality state and confidence from extraction results."""
        if not observations:
            return QualityState.MISSING, 0.0

        if len(prs) < 10:
            quality = QualityState.DEGRADED
            confidence = max(0.5, len(prs) / 10.0)
        else:
            quality = QualityState.COMPLETE
            confidence = 1.0

        return quality, confidence
