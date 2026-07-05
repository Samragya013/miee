"""Tests for GitHub PR provider API client (mocked, no network)."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

from miie.providers.github.api import GitHubAPIError, GitHubClient
from miie.providers.github.authentication import GitHubAuth

# ---------------------------------------------------------------------------
# Mock HTTP helpers
# ---------------------------------------------------------------------------


def _mock_response(
    data: Any,
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
) -> MagicMock:
    """Create a mock urllib response."""
    resp = MagicMock()
    resp.status = status
    resp.headers = headers or {
        "x-ratelimit-limit": "5000",
        "x-ratelimit-remaining": "4999",
        "x-ratelimit-used": "1",
    }
    raw = json.dumps(data).encode("utf-8") if data is not None else b""
    resp.read.return_value = raw
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _mock_error(status: int, message: str = "Not Found") -> MagicMock:
    """Create a mock HTTP error."""
    import urllib.error

    resp = MagicMock()
    resp.code = status
    resp.reason = message
    resp.read.return_value = json.dumps({"message": message}).encode("utf-8")
    return urllib.error.HTTPError(
        url="https://api.github.com/test",
        code=status,
        msg=message,
        hdrs={},
        fp=resp,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGitHubClientInit:
    def test_default_auth(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        client = GitHubClient()
        assert client._auth.is_anonymous is True

    def test_custom_auth(self):
        auth = GitHubAuth(token="ghp_test")
        client = GitHubClient(auth=auth)
        assert client._auth.is_authenticated is True

    def test_custom_timeout(self):
        client = GitHubClient(timeout=60.0)
        assert client._timeout == 60.0


class TestGitHubClientRepository:
    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_get_repository(self, mock_urlopen):
        repo_data = {"full_name": "owner/repo", "default_branch": "main"}
        mock_urlopen.return_value = _mock_response(repo_data)
        client = GitHubClient()
        result = client.get_repository("owner", "repo")
        assert result["full_name"] == "owner/repo"
        assert result["default_branch"] == "main"

    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_get_default_branch(self, mock_urlopen):
        repo_data = {"default_branch": "develop"}
        mock_urlopen.return_value = _mock_response(repo_data)
        client = GitHubClient()
        branch = client.get_default_branch("owner", "repo")
        assert branch == "develop"


class TestGitHubClientPullRequests:
    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_list_pull_requests(self, mock_urlopen):
        prs = [{"number": 1, "state": "open"}, {"number": 2, "state": "closed"}]
        mock_urlopen.return_value = _mock_response(prs)
        client = GitHubClient()
        result = client.list_pull_requests("owner", "repo")
        assert len(result) == 2
        assert result[0]["number"] == 1

    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_list_pull_requests_empty(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response([])
        client = GitHubClient()
        result = client.list_pull_requests("owner", "repo")
        assert len(result) == 0

    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_get_pull_request(self, mock_urlopen):
        pr_data = {"number": 42, "state": "open", "title": "Test PR"}
        mock_urlopen.return_value = _mock_response(pr_data)
        client = GitHubClient()
        result = client.get_pull_request("owner", "repo", 42)
        assert result["number"] == 42

    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_list_pull_request_reviews(self, mock_urlopen):
        reviews = [{"id": 1, "state": "APPROVED"}, {"id": 2, "state": "COMMENTED"}]
        mock_urlopen.return_value = _mock_response(reviews)
        client = GitHubClient()
        result = client.list_pull_request_reviews("owner", "repo", 42)
        assert len(result) == 2


class TestGitHubClientPagination:
    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_pagination_multi_page(self, mock_urlopen):
        page1 = [{"number": i} for i in range(100)]
        page2 = [{"number": i} for i in range(100, 105)]
        empty = []

        responses = [
            _mock_response(page1),
            _mock_response(page2),
            _mock_response(empty),
        ]
        mock_urlopen.side_effect = responses

        client = GitHubClient()
        result = client.list_pull_requests("owner", "repo", per_page=100)
        assert len(result) == 105

    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_pagination_single_page(self, mock_urlopen):
        prs = [{"number": 1}, {"number": 2}]
        mock_urlopen.return_value = _mock_response(prs)
        client = GitHubClient()
        result = client.list_pull_requests("owner", "repo", per_page=100)
        assert len(result) == 2


class TestGitHubClientErrors:
    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_404_raises_error(self, mock_urlopen):
        mock_urlopen.side_effect = _mock_error(404)
        client = GitHubClient()
        with pytest.raises(GitHubAPIError) as exc_info:
            client.get_repository("owner", "nonexistent")
        assert exc_info.value.status_code == 404

    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_403_raises_error(self, mock_urlopen):
        mock_urlopen.side_effect = _mock_error(403, "Forbidden")
        client = GitHubClient()
        with pytest.raises(GitHubAPIError) as exc_info:
            client.get_repository("owner", "private-repo")
        assert exc_info.value.status_code == 403


class TestGitHubClientRateLimit:
    @patch("miie.providers.github.api.urllib.request.urlopen")
    def test_get_rate_limit(self, mock_urlopen):
        rl_data = {"resources": {"core": {"limit": 5000, "remaining": 4999, "used": 1}}}
        mock_urlopen.return_value = _mock_response(rl_data)
        client = GitHubClient()
        info = client.get_rate_limit()
        assert info.limit == 5000
