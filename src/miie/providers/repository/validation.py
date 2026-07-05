"""
Provider-specific validation for the Repository Metadata provider.

Validates repository accessibility, metadata completeness, field
consistency, and timestamp validity.
"""

from __future__ import annotations

import logging
from typing import List

from miie.providers.context import ProviderContext, ValidationResult
from miie.providers.github.api import GitHubAPIError, GitHubClient
from miie.providers.repository.models import RepositoryMetadata

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


class RepositoryProviderValidator:
    """Validates GitHub repository accessibility and metadata quality."""

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
                violations=[f"Cannot parse owner/repo from repository_id: " f"{context.repository_id}"],
                rule_id="REPO_METADATA_PARSE",
            )

        try:
            self._client.get_repository(owner, repo)
        except GitHubAPIError as exc:
            violations = [f"GitHub API error: {str(exc)}"]
            if exc.status_code == 404:
                violations = [f"Repository not found: {owner}/{repo}"]
            elif exc.status_code == 403:
                violations = [f"Access denied: {owner}/{repo} (check token permissions)"]
            return ValidationResult.failure(
                violations=violations,
                rule_id="REPO_METADATA_ACCESS",
            )

        return ValidationResult.success()

    def validate_rate_limit(self) -> ValidationResult:
        """Check current API rate limit status."""
        try:
            info = self._client.get_rate_limit()
        except GitHubAPIError as exc:
            return ValidationResult.failure(
                violations=[f"Cannot check rate limit: {str(exc)}"],
                rule_id="REPO_METADATA_RATE_LIMIT",
            )

        if info.is_exhausted:
            reset_str = info.reset_at.isoformat() if info.reset_at else "unknown"
            return ValidationResult.failure(
                violations=[f"Rate limit exhausted (resets at {reset_str})"],
                rule_id="REPO_METADATA_RATE_LIMIT",
            )

        warnings: List[str] = []
        if info.remaining < info.limit * 0.1:
            warnings.append(f"Rate limit low: {info.remaining}/{info.limit} remaining")

        if warnings:
            return ValidationResult.with_warnings(warnings=warnings)
        return ValidationResult.success()

    def validate_metadata(
        self,
        metadata: RepositoryMetadata,
    ) -> ValidationResult:
        """Validate repository metadata completeness and consistency."""
        warnings: List[str] = []
        violations: List[str] = []

        if not metadata.name:
            violations.append("Repository name is empty")

        if not metadata.full_name:
            violations.append("Repository full_name is empty")

        if metadata.stars < 0:
            violations.append(f"Invalid stars count: {metadata.stars}")

        if metadata.fork_count < 0:
            violations.append(f"Invalid fork count: {metadata.fork_count}")

        if metadata.open_issues < 0:
            violations.append(f"Invalid open issues count: {metadata.open_issues}")

        if metadata.size < 0:
            violations.append(f"Invalid repository size: {metadata.size}")

        if metadata.is_archived:
            warnings.append(f"Repository {metadata.full_name} is archived")

        if metadata.is_fork:
            warnings.append(f"Repository {metadata.full_name} is a fork")

        if not metadata.primary_language:
            warnings.append("Primary language not set")

        if not metadata.license:
            warnings.append("License not detected")

        if not metadata.description:
            warnings.append("Repository description is empty")

        if not metadata.topics:
            warnings.append("No topics configured")

        if violations:
            return ValidationResult.failure(
                violations=violations,
                rule_id="REPO_METADATA_VALIDATION",
            )

        if warnings:
            return ValidationResult.with_warnings(warnings=warnings)
        return ValidationResult.success()

    def validate_timestamps(
        self,
        metadata: RepositoryMetadata,
    ) -> ValidationResult:
        """Validate timestamp consistency."""
        warnings: List[str] = []

        if metadata.pushed_at and metadata.pushed_at > metadata.updated_at:
            warnings.append("Last push is after last update (unusual ordering)")

        if metadata.updated_at < metadata.created_at:
            warnings.append("Last update is before creation date (clock skew?)")

        if warnings:
            return ValidationResult.with_warnings(warnings=warnings)
        return ValidationResult.success()
