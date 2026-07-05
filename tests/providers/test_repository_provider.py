"""Tests for RepositoryMetadataProvider — models, normalization, validation, health, provider, registry."""

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
from miie.providers.github.models import RateLimitInfo
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
from miie.providers.repository.provider import (
    PROVIDER_ID,
    RepositoryMetadataProvider,
    repository_metadata_provider_capabilities,
)
from miie.providers.repository.validation import (
    RepositoryProviderValidator,
    _parse_owner_repo,
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
    client.get_repository.return_value = _raw_repo()
    info = RateLimitInfo(limit=5000, remaining=4999, reset_at=None)
    client.get_rate_limit.return_value = info
    for k, v in overrides.items():
        setattr(client, k, v)
    return client


def _raw_repo(**overrides) -> Dict[str, Any]:
    """Minimal raw repo dict for API responses."""
    base = {
        "name": "repo",
        "full_name": "owner/repo",
        "description": "A test repository",
        "homepage": "https://example.com",
        "default_branch": "main",
        "language": "Python",
        "languages": {"Python": 5000, "JavaScript": 3000},
        "license": {"key": "mit", "name": "MIT"},
        "visibility": "public",
        "archived": False,
        "fork": False,
        "forks_count": 10,
        "stargazers_count": 100,
        "watchers_count": 50,
        "open_issues_count": 5,
        "size": 1024,
        "topics": ["python", "testing"],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-06-15T12:00:00Z",
        "pushed_at": "2025-06-14T10:00:00Z",
    }
    base.update(overrides)
    return base


def _make_metadata(**overrides) -> RepositoryMetadata:
    """Create a RepositoryMetadata instance with defaults."""
    from datetime import datetime, timezone

    defaults = dict(
        name="repo",
        full_name="owner/repo",
        description="A test repository",
        homepage="https://example.com",
        default_branch="main",
        primary_language="Python",
        languages={"Python": 5000, "JavaScript": 3000},
        license="mit",
        visibility="public",
        is_archived=False,
        is_fork=False,
        fork_count=10,
        stars=100,
        watchers=50,
        open_issues=5,
        size=1024,
        topics=frozenset({"python", "testing"}),
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        pushed_at=datetime(2025, 6, 14, 10, 0, 0, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    return RepositoryMetadata(**defaults)


# ===================================================================
# Model tests
# ===================================================================


class TestRepositoryMetadata:
    def test_from_api_full(self):
        raw = _raw_repo()
        meta = RepositoryMetadata.from_api(raw)
        assert meta.name == "repo"
        assert meta.full_name == "owner/repo"
        assert meta.description == "A test repository"
        assert meta.homepage == "https://example.com"
        assert meta.default_branch == "main"
        assert meta.primary_language == "Python"
        assert meta.languages == {"Python": 5000, "JavaScript": 3000}
        assert meta.license == "mit"
        assert meta.visibility == "public"
        assert meta.is_archived is False
        assert meta.is_fork is False
        assert meta.fork_count == 10
        assert meta.stars == 100
        assert meta.watchers == 50
        assert meta.open_issues == 5
        assert meta.size == 1024
        assert meta.topics == frozenset({"python", "testing"})
        assert meta.created_at.year == 2025
        assert meta.updated_at.year == 2025
        assert meta.pushed_at is not None

    def test_from_api_minimal(self):
        raw = {
            "name": "minimal",
            "full_name": "owner/minimal",
            "default_branch": "main",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-06-15T12:00:00Z",
        }
        meta = RepositoryMetadata.from_api(raw)
        assert meta.name == "minimal"
        assert meta.description is None
        assert meta.homepage is None
        assert meta.primary_language is None
        assert meta.languages == {}
        assert meta.license is None
        assert meta.is_archived is False
        assert meta.is_fork is False
        assert meta.fork_count == 0
        assert meta.stars == 0
        assert meta.topics == frozenset()

    def test_from_api_archived(self):
        raw = _raw_repo(archived=True)
        meta = RepositoryMetadata.from_api(raw)
        assert meta.is_archived is True

    def test_from_api_fork(self):
        raw = _raw_repo(fork=True, forks_count=5)
        meta = RepositoryMetadata.from_api(raw)
        assert meta.is_fork is True
        assert meta.fork_count == 5

    def test_from_api_no_license(self):
        raw = _raw_repo(license=None)
        meta = RepositoryMetadata.from_api(raw)
        assert meta.license is None

    def test_from_api_language_fallback(self):
        raw = _raw_repo(language="Go", languages={})
        meta = RepositoryMetadata.from_api(raw)
        assert meta.primary_language == "Go"
        assert meta.languages == {"Go": 1024}

    def test_from_api_topics_from_list(self):
        raw = _raw_repo(topics=["a", "b", "c"])
        meta = RepositoryMetadata.from_api(raw)
        assert meta.topics == frozenset({"a", "b", "c"})


# ===================================================================
# Normalization tests
# ===================================================================


class TestNormalization:
    def test_normalize_stars_count(self):
        meta = _make_metadata(stars=250)
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        obs = normalize_stars_count(meta, prov)
        assert obs.metric_id == "M-02"
        assert obs.value == 250.0
        assert obs.unit == "count"
        assert obs.metadata["metric_type"] == "stars"

    def test_normalize_forks_count(self):
        meta = _make_metadata(fork_count=30)
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        obs = normalize_forks_count(meta, prov)
        assert obs.metric_id == "M-02"
        assert obs.value == 30.0
        assert obs.metadata["metric_type"] == "forks"

    def test_normalize_watchers_count(self):
        meta = _make_metadata(watchers=75)
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        obs = normalize_watchers_count(meta, prov)
        assert obs.metric_id == "M-02"
        assert obs.value == 75.0
        assert obs.metadata["metric_type"] == "watchers"

    def test_normalize_open_issues_count(self):
        meta = _make_metadata(open_issues=12)
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        obs = normalize_open_issues_count(meta, prov)
        assert obs.metric_id == "M-02"
        assert obs.value == 12.0
        assert obs.metadata["metric_type"] == "open_issues"

    def test_normalize_last_push_latency(self):
        from datetime import datetime, timezone

        meta = _make_metadata(pushed_at=datetime(2025, 6, 14, 10, 0, 0, tzinfo=timezone.utc))
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        obs = normalize_last_push_latency(meta, prov)
        assert obs.metric_id == "M-05"
        assert obs.unit == "hours"
        assert obs.value >= 0
        assert obs.metadata["metric_type"] == "last_push_latency"

    def test_normalize_last_push_latency_no_push(self):
        meta = _make_metadata(pushed_at=None)
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        obs = normalize_last_push_latency(meta, prov)
        assert obs.quality == "estimated"

    def test_normalize_last_update_latency(self):
        from datetime import datetime, timezone

        meta = _make_metadata(updated_at=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc))
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        obs = normalize_last_update_latency(meta, prov)
        assert obs.metric_id == "M-05"
        assert obs.unit == "hours"
        assert obs.value >= 0
        assert obs.metadata["metric_type"] == "last_update_latency"

    def test_all_observations_have_provenance(self):
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        meta = _make_metadata()
        functions = [
            normalize_stars_count,
            normalize_forks_count,
            normalize_watchers_count,
            normalize_open_issues_count,
            normalize_last_push_latency,
            normalize_last_update_latency,
        ]
        for func in functions:
            obs = func(meta, prov)
            assert obs.provenance == prov

    def test_all_observations_have_deterministic_ids(self):
        from miie.processing.observation.models import ObservationProvenance

        prov = ObservationProvenance(extractor_id="test", extraction_timestamp="2025-06-15T12:00:00Z")
        meta = _make_metadata()
        obs1 = normalize_stars_count(meta, prov)
        obs2 = normalize_stars_count(meta, prov)
        assert obs1.observation_id == obs2.observation_id


# ===================================================================
# Validation tests
# ===================================================================


class TestValidation:
    def test_parse_owner_repo_simple(self):
        owner, repo = _parse_owner_repo("owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_owner_repo_url(self):
        owner, repo = _parse_owner_repo("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_owner_repo_url_with_git(self):
        owner, repo = _parse_owner_repo("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_owner_repo_invalid(self):
        owner, repo = _parse_owner_repo("invalid")
        assert owner == ""
        assert repo == ""

    def test_parse_owner_repo_empty(self):
        owner, repo = _parse_owner_repo("")
        assert owner == ""
        assert repo == ""

    def test_validate_repository_success(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        ctx = _context()
        result = validator.validate_repository(ctx)
        assert result.is_valid

    def test_validate_repository_not_found(self):
        client = _mock_client()
        client.get_repository.side_effect = GitHubAPIError("Not Found", 404)
        validator = RepositoryProviderValidator(client)
        ctx = _context()
        result = validator.validate_repository(ctx)
        assert not result.is_valid
        assert any("not found" in v.lower() for v in result.violations)

    def test_validate_repository_access_denied(self):
        client = _mock_client()
        client.get_repository.side_effect = GitHubAPIError("Forbidden", 403)
        validator = RepositoryProviderValidator(client)
        ctx = _context()
        result = validator.validate_repository(ctx)
        assert not result.is_valid
        assert any("access denied" in v.lower() for v in result.violations)

    def test_validate_repository_invalid_id(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        ctx = _context(repository_id="invalid")
        result = validator.validate_repository(ctx)
        assert not result.is_valid

    def test_validate_rate_limit_success(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        result = validator.validate_rate_limit()
        assert result.is_valid

    def test_validate_rate_limit_exhausted(self):
        rl_info = RateLimitInfo(limit=5000, remaining=0, reset_at=None)
        client = _mock_client()
        client.get_rate_limit.return_value = rl_info
        validator = RepositoryProviderValidator(client)
        result = validator.validate_rate_limit()
        assert not result.is_valid

    def test_validate_rate_limit_low(self):
        rl_info = RateLimitInfo(limit=5000, remaining=100, reset_at=None)
        client = _mock_client()
        client.get_rate_limit.return_value = rl_info
        validator = RepositoryProviderValidator(client)
        result = validator.validate_rate_limit()
        assert result.is_valid
        assert len(result.warnings) > 0

    def test_validate_metadata_success(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata()
        result = validator.validate_metadata(meta)
        assert result.is_valid

    def test_validate_metadata_archived_warning(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(is_archived=True)
        result = validator.validate_metadata(meta)
        assert result.is_valid
        assert any("archived" in w.lower() for w in result.warnings)

    def test_validate_metadata_fork_warning(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(is_fork=True)
        result = validator.validate_metadata(meta)
        assert result.is_valid
        assert any("fork" in w.lower() for w in result.warnings)

    def test_validate_metadata_no_description_warning(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(description=None)
        result = validator.validate_metadata(meta)
        assert result.is_valid
        assert any("description" in w.lower() for w in result.warnings)

    def test_validate_metadata_invalid_stars(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(stars=-1)
        result = validator.validate_metadata(meta)
        assert not result.is_valid

    def test_validate_metadata_invalid_forks(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(fork_count=-1)
        result = validator.validate_metadata(meta)
        assert not result.is_valid

    def test_validate_metadata_invalid_issues(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(open_issues=-1)
        result = validator.validate_metadata(meta)
        assert not result.is_valid

    def test_validate_metadata_invalid_size(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(size=-1)
        result = validator.validate_metadata(meta)
        assert not result.is_valid

    def test_validate_metadata_empty_name(self):
        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(name="")
        result = validator.validate_metadata(meta)
        assert not result.is_valid

    def test_validate_timestamps_success(self):
        from datetime import datetime, timezone

        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(
            created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2025, 6, 15, tzinfo=timezone.utc),
            pushed_at=datetime(2025, 6, 14, tzinfo=timezone.utc),
        )
        result = validator.validate_timestamps(meta)
        assert result.is_valid

    def test_validate_timestamps_push_after_update(self):
        from datetime import datetime, timezone

        client = _mock_client()
        validator = RepositoryProviderValidator(client)
        meta = _make_metadata(
            created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2025, 6, 14, tzinfo=timezone.utc),
            pushed_at=datetime(2025, 6, 15, tzinfo=timezone.utc),
        )
        result = validator.validate_timestamps(meta)
        assert result.is_valid
        assert len(result.warnings) > 0


# ===================================================================
# Health tests
# ===================================================================


class TestHealth:
    def test_initial_state(self):
        health = RepositoryProviderHealth()
        snapshot = health.snapshot()
        assert snapshot.status == HealthStatus.UNKNOWN
        assert snapshot.health_score == 1.0

    def test_record_success(self):
        health = RepositoryProviderHealth()
        health.record_success(latency_ms=100.0, metadata_completeness=0.9)
        snapshot = health.snapshot()
        assert snapshot.status == HealthStatus.HEALTHY
        assert snapshot.total_extractions == 1
        assert snapshot.successful_extractions == 1
        assert snapshot.failed_extractions == 0
        assert snapshot.consecutive_failures == 0

    def test_record_failure(self):
        health = RepositoryProviderHealth()
        health.record_failure("API error")
        snapshot = health.snapshot()
        assert snapshot.status == HealthStatus.UNHEALTHY
        assert snapshot.total_extractions == 1
        assert snapshot.failed_extractions == 1
        assert snapshot.consecutive_failures == 1

    def test_record_multiple_successes(self):
        health = RepositoryProviderHealth()
        for _ in range(10):
            health.record_success()
        snapshot = health.snapshot()
        assert snapshot.status == HealthStatus.HEALTHY
        assert snapshot.total_extractions == 10

    def test_record_failure_then_success_resets(self):
        health = RepositoryProviderHealth()
        health.record_failure("error")
        health.record_success()
        snapshot = health.snapshot()
        assert snapshot.consecutive_failures == 0

    def test_degraded_status(self):
        health = RepositoryProviderHealth()
        for _ in range(7):
            health.record_success()
        for _ in range(3):
            health.record_failure("error")
        snapshot = health.snapshot()
        assert snapshot.status == HealthStatus.DEGRADED

    def test_update_rate_limit(self):
        health = RepositoryProviderHealth()
        health.update_rate_limit(remaining=4500, total=5000)
        snapshot = health.snapshot()
        assert snapshot.metadata["rate_limit_remaining"] == 4500
        assert snapshot.metadata["rate_limit_total"] == 5000

    def test_metadata_completeness_tracked(self):
        health = RepositoryProviderHealth()
        health.record_success(metadata_completeness=0.85)
        snapshot = health.snapshot()
        assert snapshot.metadata["metadata_completeness"] == 0.85


# ===================================================================
# Provider capability tests
# ===================================================================


class TestProviderCapabilities:
    def test_capability_factory(self):
        caps = repository_metadata_provider_capabilities()
        assert isinstance(caps, ProviderCapability)
        assert "M-02" in caps.supported_metrics
        assert "M-05" in caps.supported_metrics
        assert caps.requires_network is True
        assert caps.requires_api_token is False

    def test_provider_id(self):
        assert PROVIDER_ID == "repository.metadata.observation.v1"

    def test_source_types(self):
        caps = repository_metadata_provider_capabilities()
        assert "repository" in caps.supported_source_types


# ===================================================================
# Provider lifecycle tests
# ===================================================================


class TestProviderLifecycle:
    def test_initial_state(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        assert provider.provider_id == PROVIDER_ID
        assert provider.state == ProviderState.UNINITIALIZED

    def test_initialize_success(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        assert provider.state == ProviderState.READY

    def test_initialize_repo_not_found(self):
        client = _mock_client()
        client.get_repository.side_effect = GitHubAPIError("Not Found", 404)
        provider = RepositoryMetadataProvider(client=client)
        with pytest.raises(Exception):
            provider.initialize(_context())
        assert provider.state == ProviderState.FAILED

    def test_initialize_rate_limit_exhausted(self):
        client = _mock_client()
        rl_info = RateLimitInfo(limit=5000, remaining=0, reset_at=None)
        client.get_rate_limit.return_value = rl_info
        provider = RepositoryMetadataProvider(client=client)
        with pytest.raises(Exception):
            provider.initialize(_context())
        assert provider.state == ProviderState.FAILED

    def test_dispose(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.dispose()
        assert provider.state == ProviderState.DISPOSED

    def test_initialize_after_dispose(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.dispose()
        with pytest.raises(Exception):
            provider.initialize(_context())

    def test_health_check(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        health = provider.health_check()
        assert health.status == HealthStatus.UNKNOWN

    def test_supports_metric(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        assert provider.supports_metric("M-02") is True
        assert provider.supports_metric("M-05") is True
        assert provider.supports_metric("M-01") is False
        assert provider.supports_metric("M-03") is False

    def test_get_capabilities(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        caps = provider.get_capabilities()
        assert "M-02" in caps.supported_metrics
        assert caps.requires_network is True


# ===================================================================
# Provider extraction tests
# ===================================================================


class TestProviderExtraction:
    def test_extract_observations_empty_metrics(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-03"])
        assert isinstance(result, ExtractionResult)
        assert result.provider_id == PROVIDER_ID
        assert result.observations == ()
        assert result.quality_state == QualityState.MISSING

    def test_extract_unsupported_metrics(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-03", "M-04"])
        assert result.quality_state == QualityState.MISSING
        assert result.confidence == 0.0

    def test_extract_m02(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02"])
        assert len(result.observations) == 4
        metric_types = {o.metadata.get("metric_type") for o in result.observations}
        assert metric_types == {"stars", "forks", "watchers", "open_issues"}

    def test_extract_m05(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-05"])
        assert len(result.observations) == 2
        metric_types = {o.metadata.get("metric_type") for o in result.observations}
        assert metric_types == {"last_push_latency", "last_update_latency"}

    def test_extract_all_metrics(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        # 4 (M-02) + 2 (M-05) = 6
        assert len(result.observations) == 6

    def test_extract_api_error(self):
        client = _mock_client()
        # First call (initialize validation) succeeds, second call (extract) fails
        client.get_repository.side_effect = [
            _raw_repo(),
            GitHubAPIError("Error", 500),
        ]
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02"])
        assert result.quality_state == QualityState.MISSING
        assert len(result.warnings) > 0

    def test_extract_invalid_repo_id(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        ctx = _context(repository_id="invalid")
        result = provider.extract_observations(ctx, ["M-02"])
        assert result.quality_state == QualityState.MISSING

    def test_extract_after_dispose(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.dispose()
        with pytest.raises(Exception):
            provider.extract_observations(_context(), ["M-02"])

    def test_extract_delegates_to_extract_observations(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract(_context(), ["M-02"])
        assert isinstance(result, ExtractionResult)

    def test_extract_quality_complete(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02"])
        assert result.quality_state == QualityState.COMPLETE
        assert result.confidence == 1.0

    def test_extract_metadata_completeness(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02"])
        assert "metadata_completeness" in result.metadata

    def test_extract_archived_repo(self):
        client = _mock_client()
        client.get_repository.return_value = _raw_repo(archived=True)
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02"])
        assert result.metadata["is_archived"] is True

    def test_extract_fork_repo(self):
        client = _mock_client()
        client.get_repository.return_value = _raw_repo(fork=True)
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02"])
        assert result.metadata["is_fork"] is True


# ===================================================================
# Registry integration tests
# ===================================================================


class TestProviderRegistry:
    def test_register_and_discover(self):
        from miie.providers.registry import DeterministicRegistry

        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        registry = DeterministicRegistry()
        caps = provider.get_capabilities()

        registry.register(provider, caps)
        providers = registry.discover("M-02")
        assert len(providers) >= 1
        assert any(p.provider_id == PROVIDER_ID for p in providers)

    def test_select_provider(self):
        from miie.providers.registry import DeterministicRegistry

        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        registry = DeterministicRegistry()
        caps = provider.get_capabilities()

        registry.register(provider, caps)
        selected = registry.select_provider("M-02")
        assert selected is not None
        assert selected.provider_id == PROVIDER_ID

    def test_unsupported_metric_not_discovered(self):
        from miie.providers.registry import DeterministicRegistry

        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        registry = DeterministicRegistry()
        caps = provider.get_capabilities()

        registry.register(provider, caps)
        providers = registry.discover("M-03")
        assert len([p for p in providers if p.provider_id == PROVIDER_ID]) == 0

    def test_discover_m05(self):
        from miie.providers.registry import DeterministicRegistry

        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        registry = DeterministicRegistry()
        caps = provider.get_capabilities()

        registry.register(provider, caps)
        providers = registry.discover("M-05")
        assert any(p.provider_id == PROVIDER_ID for p in providers)


# ===================================================================
# Deterministic observation ID tests
# ===================================================================


class TestObservationIds:
    def test_observation_ids_are_deterministic(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        r1 = provider.extract_observations(_context(), ["M-02"])
        r2 = provider.extract_observations(_context(), ["M-02"])
        ids1 = sorted(o.observation_id for o in r1.observations)
        ids2 = sorted(o.observation_id for o in r2.observations)
        assert ids1 == ids2

    def test_different_metrics_have_different_ids(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        all_ids = [o.observation_id for o in result.observations]
        assert len(all_ids) == len(set(all_ids))

    def test_all_observations_have_provenance(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        for obs in result.observations:
            assert obs.provenance.extractor_id == PROVIDER_ID

    def test_all_observations_have_valid_source_type(self):
        client = _mock_client()
        provider = RepositoryMetadataProvider(client=client)
        provider.initialize(_context())
        result = provider.extract_observations(_context(), ["M-02", "M-05"])
        for obs in result.observations:
            assert obs.source_type == "branch"
            assert obs.source_id == "owner/repo"
