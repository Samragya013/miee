"""Tests for GitHub PR provider health reporting."""

from __future__ import annotations

import pytest

from miie.providers.context import HealthStatus
from miie.providers.github.health import GitHubProviderHealth


class TestGitHubProviderHealth:
    def test_initial_state(self):
        h = GitHubProviderHealth()
        snap = h.snapshot()
        assert snap.status == HealthStatus.UNKNOWN
        assert snap.health_score == 1.0
        assert snap.total_extractions == 0

    def test_record_success(self):
        h = GitHubProviderHealth()
        h.record_success(latency_ms=100.0)
        snap = h.snapshot()
        assert snap.status == HealthStatus.HEALTHY
        assert snap.total_extractions == 1
        assert snap.successful_extractions == 1
        assert snap.failed_extractions == 0
        assert snap.consecutive_failures == 0
        assert snap.average_latency_ms == pytest.approx(100.0)

    def test_record_failure(self):
        h = GitHubProviderHealth()
        h.record_failure("API error")
        snap = h.snapshot()
        assert snap.status == HealthStatus.UNHEALTHY
        assert snap.total_extractions == 1
        assert snap.failed_extractions == 1
        assert snap.consecutive_failures == 1
        assert snap.error_message == "API error"

    def test_consecutive_failures_resets_on_success(self):
        h = GitHubProviderHealth()
        h.record_failure("err1")
        h.record_failure("err2")
        h.record_success()
        snap = h.snapshot()
        assert snap.consecutive_failures == 0

    def test_degraded_after_mixed(self):
        h = GitHubProviderHealth()
        for _ in range(8):
            h.record_success()
        for _ in range(2):
            h.record_failure("err")
        snap = h.snapshot()
        # 8/10 = 80% success rate → DEGRADED
        assert snap.status == HealthStatus.DEGRADED

    def test_unhealthy_after_many_failures(self):
        h = GitHubProviderHealth()
        for _ in range(5):
            h.record_failure("err")
        snap = h.snapshot()
        assert snap.status == HealthStatus.UNHEALTHY

    def test_latency_tracking(self):
        h = GitHubProviderHealth()
        h.record_success(100.0)
        h.record_success(200.0)
        h.record_success(300.0)
        snap = h.snapshot()
        assert snap.average_latency_ms == pytest.approx(200.0)

    def test_update_rate_limit(self):
        h = GitHubProviderHealth()
        h.update_rate_limit(remaining=4500, total=5000)
        snap = h.snapshot()
        assert snap.metadata["rate_limit_remaining"] == 4500
        assert snap.metadata["rate_limit_total"] == 5000

    def test_health_score_formula(self):
        h = GitHubProviderHealth()
        for _ in range(10):
            h.record_success()
        snap = h.snapshot()
        assert snap.health_score == pytest.approx(1.0)

    def test_last_check_updated(self):
        h = GitHubProviderHealth()
        assert h._last_check is None
        h.record_success()
        assert h._last_check is not None
