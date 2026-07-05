"""Tests for GitHub PR provider validation."""

from __future__ import annotations

from unittest.mock import MagicMock

from miie.providers.context import ProviderContext
from miie.providers.github.api import GitHubAPIError, GitHubClient
from miie.providers.github.models import RateLimitInfo
from miie.providers.github.validation import (
    GitHubProviderValidator,
    _parse_owner_repo,
)


def _context(**overrides) -> ProviderContext:
    defaults = dict(
        repo_path="/tmp/test",
        repository_id="owner/repo",
        analysis_id="test-analysis",
    )
    defaults.update(overrides)
    return ProviderContext(**defaults)


class TestParseOwnerRepo:
    def test_owner_repo(self):
        assert _parse_owner_repo("owner/repo") == ("owner", "repo")

    def test_full_url(self):
        assert _parse_owner_repo("https://github.com/owner/repo") == ("owner", "repo")

    def test_full_url_with_git(self):
        assert _parse_owner_repo("https://github.com/owner/repo.git") == ("owner", "repo")

    def test_trailing_slash(self):
        assert _parse_owner_repo("owner/repo/") == ("owner", "repo")

    def test_invalid(self):
        assert _parse_owner_repo("invalid") == ("", "")


class TestGitHubProviderValidator:
    def test_validate_repository_success(self):
        client = MagicMock(spec=GitHubClient)
        client.get_repository.return_value = {"full_name": "owner/repo", "archived": False}
        validator = GitHubProviderValidator(client)
        result = validator.validate_repository(_context())
        assert result.is_valid is True

    def test_validate_repository_not_found(self):
        client = MagicMock(spec=GitHubClient)
        client.get_repository.side_effect = GitHubAPIError("Not Found", status_code=404)
        validator = GitHubProviderValidator(client)
        result = validator.validate_repository(_context())
        assert result.is_valid is False
        assert "not found" in result.violations[0].lower()

    def test_validate_repository_access_denied(self):
        client = MagicMock(spec=GitHubClient)
        client.get_repository.side_effect = GitHubAPIError("Forbidden", status_code=403)
        validator = GitHubProviderValidator(client)
        result = validator.validate_repository(_context())
        assert result.is_valid is False
        assert "access denied" in result.violations[0].lower()

    def test_validate_repository_archived(self):
        client = MagicMock(spec=GitHubClient)
        client.get_repository.return_value = {"full_name": "owner/repo", "archived": True}
        validator = GitHubProviderValidator(client)
        result = validator.validate_repository(_context())
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert "archived" in result.warnings[0].lower()

    def test_validate_repository_fork(self):
        client = MagicMock(spec=GitHubClient)
        client.get_repository.return_value = {"full_name": "owner/repo", "fork": True}
        validator = GitHubProviderValidator(client)
        result = validator.validate_repository(_context())
        assert result.is_valid is True
        assert any("fork" in w.lower() for w in result.warnings)

    def test_validate_repository_invalid_id(self):
        client = MagicMock(spec=GitHubClient)
        validator = GitHubProviderValidator(client)
        ctx = _context(repository_id="invalid")
        result = validator.validate_repository(ctx)
        assert result.is_valid is False
        assert "parse" in result.violations[0].lower()

    def test_validate_rate_limit_ok(self):
        client = MagicMock(spec=GitHubClient)
        info = RateLimitInfo(limit=5000, remaining=4999, reset_at=None)
        client.get_rate_limit.return_value = info
        validator = GitHubProviderValidator(client)
        result = validator.validate_rate_limit()
        assert result.is_valid is True

    def test_validate_rate_limit_exhausted(self):
        client = MagicMock(spec=GitHubClient)
        info = RateLimitInfo(limit=5000, remaining=0, reset_at=None)
        client.get_rate_limit.return_value = info
        validator = GitHubProviderValidator(client)
        result = validator.validate_rate_limit()
        assert result.is_valid is False
        assert "rate limit" in result.violations[0].lower()

    def test_validate_rate_limit_low(self):
        client = MagicMock(spec=GitHubClient)
        info = RateLimitInfo(limit=5000, remaining=100, reset_at=None)
        client.get_rate_limit.return_value = info
        validator = GitHubProviderValidator(client)
        result = validator.validate_rate_limit()
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert "low" in result.warnings[0].lower()

    def test_validate_rate_limit_api_error(self):
        client = MagicMock(spec=GitHubClient)
        client.get_rate_limit.side_effect = GitHubAPIError("Error")
        validator = GitHubProviderValidator(client)
        result = validator.validate_rate_limit()
        assert result.is_valid is False
