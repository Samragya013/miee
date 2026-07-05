"""Tests for GitHubPullRequestProvider — lifecycle, extraction, registry."""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from miie.providers.context import (
    ExtractionResult,
    HealthStatus,
    ProviderCapability,
    ProviderContext,
    ProviderState,
    QualityState,
)
from miie.providers.github.api import GitHubAPIError, GitHubClient
from miie.providers.github.authentication import GitHubAuth
from miie.providers.github.models import (
    RateLimitInfo,
)
from miie.providers.github.provider import (
    PROVIDER_ID,
    GitHubPullRequestProvider,
    github_pr_provider_capabilities,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _context(**overrides) -> ProviderContext:
    defaults = dict(
        repo_path="/tmp/test",
        repository_id="owner/repo",
        analysis_id="test-analysis",
    )
    defaults.update(overrides)
    return ProviderContext(**defaults)


def _mock_client(**overrides) -> MagicMock:
    """Create a mocked GitHubClient."""
    client = MagicMock(spec=GitHubClient)
    client._auth = GitHubAuth(token="ghp_test")
    client.list_pull_requests.return_value = []
    client.list_pull_request_reviews.return_value = []
    client.get_repository.return_value = {"full_name": "owner/repo"}
    info = RateLimitInfo(limit=5000, remaining=4999, reset_at=None)
    client.get_rate_limit.return_value = info
    for k, v in overrides.items():
        setattr(client, k, v)
    return client


def _raw_pr(**overrides) -> Dict[str, Any]:
    """Minimal raw PR dict for API responses."""
    base = {
        "number": 1,
        "state": "open",
        "title": "Test PR",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T12:00:00Z",
        "merged": False,
        "merged_at": None,
        "merged_by": None,
        "closed_at": None,
        "user": {"login": "author", "id": 1, "type": "User"},
        "head": {"sha": "abc123"},
        "base": {"ref": "main"},
        "draft": False,
        "changed_files": 5,
        "additions": 100,
        "deletions": 30,
        "review_comments": 3,
        "commits": 2,
        "mergeable": True,
        "merge_method": "merge",
        "labels": [],
        "requested_reviewers": [],
        "body": "Test body",
    }
    base.update(overrides)
    return base


def _raw_review(**overrides) -> Dict[str, Any]:
    base = {
        "id": 100,
        "state": "APPROVED",
        "user": {"login": "reviewer1", "id": 2, "type": "User"},
        "submitted_at": "2025-01-15T14:00:00Z",
        "body": "LGTM",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Capability tests
# ---------------------------------------------------------------------------


class TestProviderCapabilities:
    def test_capability_factory(self):
        caps = github_pr_provider_capabilities()
        assert isinstance(caps, ProviderCapability)
        assert "M-02" in caps.supported_metrics
        assert "M-05" in caps.supported_metrics
        assert caps.requires_network is True
        assert caps.requires_api_token is False

    def test_provider_id(self):
        assert PROVIDER_ID == "github.pr.observation.v1"


# ---------------------------------------------------------------------------
# Lifecycle tests
# ---------------------------------------------------------------------------


class TestProviderLifecycle:
    def test_initial_state(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        assert provider.provider_id == PROVIDER_ID
        assert provider.state == ProviderState.UNINITIALIZED

    def test_initialize_success(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        assert provider.state == ProviderState.READY

    def test_initialize_repo_not_found(self):
        client = _mock_client()
        client.get_repository.side_effect = GitHubAPIError("Not Found", 404)
        provider = GitHubPullRequestProvider(client=client)
        with pytest.raises(Exception):
            provider.initialize(_context())
        assert provider.state == ProviderState.FAILED

    def test_initialize_rate_limit_exhausted(self):
        client = _mock_client()
        rl_info = RateLimitInfo(limit=5000, remaining=0, reset_at=None)
        client.get_rate_limit.return_value = rl_info
        provider = GitHubPullRequestProvider(client=client)
        with pytest.raises(Exception):
            provider.initialize(_context())
        assert provider.state == ProviderState.FAILED

    def test_dispose(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.dispose()
        assert provider.state == ProviderState.DISPOSED

    def test_initialize_after_dispose(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.dispose()
        with pytest.raises(Exception):
            provider.initialize(_context())

    def test_health_check(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        health = provider.health_check()
        assert health.status == HealthStatus.UNKNOWN

    def test_supports_metric(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        assert provider.supports_metric("M-02") is True
        assert provider.supports_metric("M-05") is True
        assert provider.supports_metric("M-01") is False

    def test_get_capabilities(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        caps = provider.get_capabilities()
        assert "M-02" in caps.supported_metrics
        assert caps.requires_network is True


# ---------------------------------------------------------------------------
# Extraction tests
# ---------------------------------------------------------------------------


class TestProviderExtraction:
    def test_extract_observations_empty(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        assert isinstance(result, ExtractionResult)
        assert result.provider_id == PROVIDER_ID
        assert result.observations == ()
        assert result.quality_state == QualityState.MISSING

    def test_extract_unsupported_metrics(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-01"])
        assert result.quality_state == QualityState.MISSING
        assert result.confidence == 0.0

    def test_extract_with_prs(self):
        client = _mock_client()
        prs = [_raw_pr(number=i) for i in range(1, 12)]
        client.list_pull_requests.return_value = prs
        client.list_pull_request_reviews.return_value = []

        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        assert len(result.observations) > 0
        assert result.quality_state == QualityState.COMPLETE
        assert result.confidence == 1.0

    def test_extract_few_prs_degraded(self):
        client = _mock_client()
        prs = [_raw_pr(number=i) for i in range(1, 5)]
        client.list_pull_requests.return_value = prs
        client.list_pull_request_reviews.return_value = []

        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        assert result.quality_state == QualityState.DEGRADED
        assert result.confidence < 1.0

    def test_extract_merged_pr(self):
        client = _mock_client()
        prs = [
            _raw_pr(
                number=1,
                merged=True,
                merged_at="2025-01-16T10:00:00Z",
            )
        ]
        client.list_pull_requests.return_value = prs
        client.list_pull_request_reviews.return_value = []

        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-05"])
        merge_obs = [o for o in result.observations if o.metadata.get("event_type") == "merge"]
        assert len(merge_obs) == 1

    def test_extract_with_reviews(self):
        client = _mock_client()
        prs = [_raw_pr(number=1)]
        reviews = [_raw_review(), _raw_review(id=101, state="COMMENTED")]
        client.list_pull_requests.return_value = prs
        client.list_pull_request_reviews.return_value = reviews

        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        # Should have: 1 creation + 1 reviewer_count + 1 review_iterations + 2 review events
        assert len(result.observations) >= 5

    def test_extract_api_error(self):
        client = _mock_client()
        client.list_pull_requests.side_effect = GitHubAPIError("Error", 500)
        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02"])
        assert result.quality_state == QualityState.MISSING
        assert len(result.warnings) > 0

    def test_extract_invalid_repo_id(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        ctx = _context(repository_id="invalid")
        result = provider.extract_observations(ctx, ["M-02"])
        assert result.quality_state == QualityState.MISSING

    def test_extract_after_dispose(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.dispose()
        with pytest.raises(Exception):
            provider.extract_observations(_context(), ["M-02"])

    def test_extract_delegates_to_extract_observations(self):
        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        provider.initialize(_context())
        result = provider.extract(_context(), ["M-02"])
        assert isinstance(result, ExtractionResult)


# ---------------------------------------------------------------------------
# Registry integration tests
# ---------------------------------------------------------------------------


class TestProviderRegistry:
    def test_register_and_discover(self):
        from miie.providers.registry import DeterministicRegistry

        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        registry = DeterministicRegistry()
        caps = provider.get_capabilities()

        registry.register(provider, caps)
        providers = registry.discover("M-02")
        assert len(providers) >= 1
        assert any(p.provider_id == PROVIDER_ID for p in providers)

    def test_select_provider(self):
        from miie.providers.registry import DeterministicRegistry

        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        registry = DeterministicRegistry()
        caps = provider.get_capabilities()

        registry.register(provider, caps)
        selected = registry.select_provider("M-02")
        assert selected is not None
        assert selected.provider_id == PROVIDER_ID

    def test_unsupported_metric_not_discovered(self):
        from miie.providers.registry import DeterministicRegistry

        client = _mock_client()
        provider = GitHubPullRequestProvider(client=client)
        registry = DeterministicRegistry()
        caps = provider.get_capabilities()

        registry.register(provider, caps)
        providers = registry.discover("M-03")
        assert len([p for p in providers if p.provider_id == PROVIDER_ID]) == 0
