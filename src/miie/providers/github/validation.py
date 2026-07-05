"""
Provider-specific validation for the GitHub Pull Request provider.

Validates repository accessibility, API availability, and observation
quality before and after extraction.
"""

from __future__ import annotations

import logging
from typing import List

from miie.providers.context import ProviderContext, ValidationResult
from miie.providers.github.api import GitHubAPIError, GitHubClient

logger = logging.getLogger(__name__)


def _parse_owner_repo(repo_id: str) -> tuple[str, str]:
    """Extract owner/repo from a repository ID or URL.

    Accepts formats:
      - ``owner/repo``
      - ``https://github.com/owner/repo``
      - ``https://github.com/owner/repo.git``
    """
    rid = repo_id.strip().rstrip("/")
    if "github.com/" in rid:
        parts = rid.split("github.com/")[-1]
    else:
        parts = rid
    parts = parts.removesuffix(".git")
    segments = parts.split("/")
    if len(segments) >= 2:
        return segments[0], segments[1]
    return "", ""


class GitHubProviderValidator:
    """Validates GitHub repository accessibility and API health."""

    def __init__(self, client: GitHubClient) -> None:
        self._client = client

    def validate_repository(
        self,
        context: ProviderContext,
    ) -> ValidationResult:
        """Check that the repository exists and is accessible via the API."""
        owner, repo = _parse_owner_repo(context.repository_id)
        if not owner or not repo:
            return ValidationResult.failure(
                violations=[f"Cannot parse owner/repo from repository_id: {context.repository_id}"],
                rule_id="GITHUB_REPO_PARSE",
            )

        try:
            repo_data = self._client.get_repository(owner, repo)
        except GitHubAPIError as exc:
            violations = [f"GitHub API error: {str(exc)}"]
            if exc.status_code == 404:
                violations = [f"Repository not found: {owner}/{repo}"]
            elif exc.status_code == 403:
                violations = [f"Access denied: {owner}/{repo} (check token permissions)"]
            return ValidationResult.failure(
                violations=violations,
                rule_id="GITHUB_REPO_ACCESS",
            )

        warnings: List[str] = []

        if repo_data.get("archived"):
            warnings.append(f"Repository {owner}/{repo} is archived")

        if repo_data.get("fork"):
            warnings.append(f"Repository {owner}/{repo} is a fork")

        if not repo_data.get("has_pull_requests", True):
            warnings.append(f"Pull requests may be disabled for {owner}/{repo}")

        if warnings:
            return ValidationResult.with_warnings(warnings=warnings)
        return ValidationResult.success()

    def validate_rate_limit(self) -> ValidationResult:
        """Check current API rate limit status."""
        try:
            info = self._client.get_rate_limit()
        except GitHubAPIError as exc:
            return ValidationResult.failure(
                violations=[f"Cannot check rate limit: {str(exc)}"],
                rule_id="GITHUB_RATE_LIMIT",
            )

        if info.is_exhausted:
            reset_str = info.reset_at.isoformat() if info.reset_at else "unknown"
            return ValidationResult.failure(
                violations=[f"Rate limit exhausted (resets at {reset_str})"],
                rule_id="GITHUB_RATE_LIMIT",
            )

        warnings: List[str] = []
        if info.remaining < info.limit * 0.1:
            warnings.append(f"Rate limit low: {info.remaining}/{info.limit} remaining")

        if warnings:
            return ValidationResult.with_warnings(warnings=warnings)
        return ValidationResult.success()

    def validate_pr_access(
        self,
        owner: str,
        repo: str,
    ) -> ValidationResult:
        """Check that pull requests are accessible."""
        try:
            prs = self._client.list_pull_requests(owner, repo, per_page=1)
        except GitHubAPIError as exc:
            return ValidationResult.failure(
                violations=[f"Cannot list pull requests: {str(exc)}"],
                rule_id="GITHUB_PR_ACCESS",
            )

        if not isinstance(prs, list):
            return ValidationResult.failure(
                violations=["Unexpected response format for pull requests"],
                rule_id="GITHUB_PR_FORMAT",
            )

        return ValidationResult.success()
