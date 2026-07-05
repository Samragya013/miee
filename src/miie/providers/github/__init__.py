"""
GitHub Pull Request Observation Provider — PR-11B.

Provides GitHubPullRequestProvider for extracting pull request and
review observations from GitHub repositories via the REST API.
"""

from miie.providers.github.api import GitHubAPIError, GitHubClient
from miie.providers.github.authentication import GitHubAuth
from miie.providers.github.health import GitHubProviderHealth
from miie.providers.github.models import (
    MergeStrategy,
    PullRequest,
    PullRequestState,
    RateLimitInfo,
    Review,
    ReviewState,
)
from miie.providers.github.normalization import (
    normalize_pr_close,
    normalize_pr_creation,
    normalize_pr_draft,
    normalize_pr_merge,
    normalize_pr_reopened,
    normalize_review,
    normalize_review_iterations,
    normalize_reviewer_count,
)
from miie.providers.github.provider import PROVIDER_ID as GITHUB_PR_PROVIDER_ID
from miie.providers.github.provider import (
    GitHubPullRequestProvider,
    github_pr_provider_capabilities,
)
from miie.providers.github.validation import GitHubProviderValidator

__all__ = [
    "GitHubPullRequestProvider",
    "GitHubClient",
    "GitHubAPIError",
    "GitHubAuth",
    "GitHubProviderHealth",
    "GitHubProviderValidator",
    "PullRequest",
    "PullRequestState",
    "Review",
    "ReviewState",
    "MergeStrategy",
    "RateLimitInfo",
    "GITHUB_PR_PROVIDER_ID",
    "github_pr_provider_capabilities",
    "normalize_pr_creation",
    "normalize_pr_merge",
    "normalize_pr_close",
    "normalize_pr_draft",
    "normalize_pr_reopened",
    "normalize_review",
    "normalize_review_iterations",
    "normalize_reviewer_count",
]
