"""Tests for GitHub PR provider authentication."""

from __future__ import annotations

from miie.providers.github.authentication import GitHubAuth


class TestGitHubAuth:
    def test_anonymous_by_default(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        auth = GitHubAuth()
        assert auth.is_anonymous is True
        assert auth.is_authenticated is False
        assert auth.source == "none"

    def test_explicit_token(self):
        auth = GitHubAuth(token="ghp_test123", source="config")
        assert auth.is_authenticated is True
        assert auth.is_anonymous is False
        assert auth.token == "ghp_test123"

    def test_from_config_explicit_token(self):
        auth = GitHubAuth.from_config({"token": "ghp_abc"})
        assert auth.is_authenticated is True
        assert auth.token == "ghp_abc"

    def test_from_config_github_token_key(self):
        auth = GitHubAuth.from_config({"github_token": "ghp_xyz"})
        assert auth.is_authenticated is True
        assert auth.token == "ghp_xyz"

    def test_from_config_no_token(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        auth = GitHubAuth.from_config({})
        assert auth.is_anonymous is True

    def test_from_config_prefers_token(self):
        auth = GitHubAuth.from_config({"token": "first", "github_token": "second"})
        assert auth.token == "first"

    def test_to_header_dict_authenticated(self):
        auth = GitHubAuth(token="ghp_test")
        headers = auth.to_header_dict()
        assert headers["Authorization"] == "Bearer ghp_test"
        assert "Accept" in headers
        assert "X-GitHub-Api-Version" in headers

    def test_to_header_dict_anonymous(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        auth = GitHubAuth()
        headers = auth.to_header_dict()
        assert "Authorization" not in headers
        assert headers["Accept"] == "application/vnd.github+json"

    def test_validate_permissions_ok(self):
        auth = GitHubAuth()
        result = auth.validate_permissions({"x-ratelimit-remaining": "5000"})
        assert result is None

    def test_validate_permissions_exhausted(self):
        auth = GitHubAuth()
        result = auth.validate_permissions({"x-ratelimit-remaining": "0"})
        assert result is not None
        assert "rate limit" in result.lower()

    def test_env_var_fallback(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_env_token")
        auth = GitHubAuth()
        assert auth.is_authenticated is True
        assert auth.token == "ghp_env_token"
        assert auth.source == "env:GITHUB_TOKEN"

    def test_empty_token_is_anonymous(self):
        auth = GitHubAuth(token="")
        assert auth.is_anonymous is True
