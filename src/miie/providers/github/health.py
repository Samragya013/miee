"""
Health reporting for the GitHub Pull Request provider.

Tracks API availability, rate-limit status, and extraction success
to produce structured health snapshots.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional

from miie.providers.context import HealthStatus, ProviderHealth


@dataclass
class GitHubProviderHealth:
    """Mutable health tracker for the GitHub PR provider."""

    _status: HealthStatus = HealthStatus.UNKNOWN
    _health_score: float = 1.0
    _consecutive_failures: int = 0
    _total_extractions: int = 0
    _successful_extractions: int = 0
    _failed_extractions: int = 0
    _average_latency_ms: float = 0.0
    _last_error: Optional[str] = None
    _last_check: Optional[datetime.datetime] = None
    _rate_limit_remaining: Optional[int] = None
    _rate_limit_total: Optional[int] = None

    def record_success(self, latency_ms: float = 0.0) -> None:
        """Record a successful extraction."""
        self._total_extractions += 1
        self._successful_extractions += 1
        self._consecutive_failures = 0
        self._last_check = datetime.datetime.now(datetime.timezone.utc)
        self._last_error = None
        n = self._total_extractions
        self._average_latency_ms = (self._average_latency_ms * (n - 1) + latency_ms) / n
        self._recalculate()

    def record_failure(self, error_message: str) -> None:
        """Record a failed extraction."""
        self._total_extractions += 1
        self._failed_extractions += 1
        self._consecutive_failures += 1
        self._last_check = datetime.datetime.now(datetime.timezone.utc)
        self._last_error = error_message
        self._recalculate()

    def update_rate_limit(self, remaining: int, total: int) -> None:
        """Update rate-limit tracking."""
        self._rate_limit_remaining = remaining
        self._rate_limit_total = total

    def snapshot(self) -> ProviderHealth:
        """Produce a point-in-time health snapshot."""
        return ProviderHealth(
            status=self._status,
            health_score=self._health_score,
            last_check=self._last_check,
            consecutive_failures=self._consecutive_failures,
            total_extractions=self._total_extractions,
            successful_extractions=self._successful_extractions,
            failed_extractions=self._failed_extractions,
            average_latency_ms=self._average_latency_ms,
            error_message=self._last_error,
            metadata={
                "rate_limit_remaining": self._rate_limit_remaining,
                "rate_limit_total": self._rate_limit_total,
            },
        )

    def _recalculate(self) -> None:
        """Derive status and score from counters."""
        if self._total_extractions == 0:
            self._status = HealthStatus.UNKNOWN
            self._health_score = 1.0
            return

        success_rate = self._successful_extractions / self._total_extractions

        if success_rate >= 0.9 and self._consecutive_failures < 3:
            self._status = HealthStatus.HEALTHY
            self._health_score = min(success_rate, 1.0)
        elif success_rate >= 0.7 and self._consecutive_failures < 5:
            self._status = HealthStatus.DEGRADED
            self._health_score = success_rate * 0.8
        else:
            self._status = HealthStatus.UNHEALTHY
            self._health_score = max(success_rate * 0.5, 0.0)
