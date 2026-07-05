"""Tests for miie.providers.health module."""

from datetime import datetime, timezone

import pytest

from miie.providers.context import HealthStatus, ProviderHealth
from miie.providers.health import (
    Availability,
    CapabilityCoverage,
    ErrorHistory,
    ExecutionMetrics,
    LastExecution,
    LatencyTracker,
    ProviderHealthMonitor,
)


class TestExecutionMetrics:
    def test_initial_state(self):
        metrics = ExecutionMetrics()
        assert metrics.total_executions == 0
        assert metrics.success_rate == 1.0
        assert metrics.average_latency() == 0.0

    def test_record_latency(self):
        metrics = ExecutionMetrics()
        metrics.record_latency(100.0)
        assert metrics.total_executions == 0  # record_latency doesn't increment
        assert metrics.average_latency() == 100.0

    def test_success_rate_mixed(self):
        metrics = ExecutionMetrics()
        metrics.total_executions = 10
        metrics.successful_executions = 7
        metrics.failed_executions = 3
        assert metrics.success_rate == 0.7

    def test_failure_rate(self):
        metrics = ExecutionMetrics()
        metrics.total_executions = 10
        metrics.failed_executions = 3
        assert metrics.failure_rate == 0.3

    def test_latency_percentiles(self):
        metrics = ExecutionMetrics()
        for i in range(100):
            metrics.record_latency(float(i))
        assert metrics.p95_latency() > 0
        assert metrics.p99_latency() > 0


class TestLastExecution:
    def test_initial_state(self):
        last = LastExecution()
        assert last.timestamp is None
        assert last.success is False

    def test_creation(self):
        now = datetime.now(timezone.utc)
        last = LastExecution(
            timestamp=now,
            success=True,
            latency_ms=50.0,
            observation_count=10,
        )
        assert last.timestamp == now
        assert last.success is True
        assert last.latency_ms == 50.0
        assert last.observation_count == 10


class TestAvailability:
    def test_initial_state(self):
        avail = Availability()
        assert avail.consecutive_unavailable == 0
        assert avail.availability_score == 1.0

    def test_mark_unavailable(self):
        avail = Availability()
        avail.mark_unavailable()
        assert avail.consecutive_unavailable == 1
        assert avail.state == HealthStatus.DEGRADED

    def test_mark_unavailable_repeatedly(self):
        avail = Availability()
        for _ in range(5):
            avail.mark_unavailable()
        assert avail.consecutive_unavailable == 5
        assert avail.state == HealthStatus.UNHEALTHY

    def test_mark_available_resets(self):
        avail = Availability()
        avail.mark_unavailable()
        avail.mark_available()
        assert avail.consecutive_unavailable == 0

    def test_recalculate_score(self):
        avail = Availability()
        avail.recalculate_score(10)
        assert avail.availability_score == 1.0


class TestErrorHistory:
    def test_record_error(self):
        history = ErrorHistory()
        record = history.record_error("ConnectionError", "connection failed")
        assert len(history.records) == 1
        assert record.error_type == "ConnectionError"

    def test_get_recent_errors(self):
        history = ErrorHistory()
        for i in range(5):
            history.record_error("Error", f"error {i}")
        recent = history.get_recent_errors(3)
        assert len(recent) == 3

    def test_get_errors_by_type(self):
        history = ErrorHistory()
        history.record_error("ConnectionError", "conn failed")
        history.record_error("TimeoutError", "timeout")
        history.record_error("ConnectionError", "conn failed 2")
        conn_errors = history.get_errors_by_type("ConnectionError")
        assert len(conn_errors) == 2

    def test_clear(self):
        history = ErrorHistory()
        history.record_error("Error", "error")
        history.clear()
        assert len(history.records) == 0


class TestLatencyTracker:
    def test_record(self):
        tracker = LatencyTracker()
        tracker.record(100.0)
        tracker.record(200.0)
        assert tracker.average() == 150.0

    def test_percentiles(self):
        tracker = LatencyTracker()
        for i in range(100):
            tracker.record(float(i))
        assert tracker.p50() >= 0
        assert tracker.p95() >= 0
        assert tracker.p99() >= 0

    def test_reset(self):
        tracker = LatencyTracker()
        tracker.record(100.0)
        tracker.reset()
        assert tracker.average() == 0.0

    def test_sample_count(self):
        tracker = LatencyTracker()
        assert tracker.sample_count == 0
        tracker.record(100.0)
        assert tracker.sample_count == 1


class TestCapabilityCoverage:
    def test_metric_coverage(self):
        cap = CapabilityCoverage()
        cap.recalculate(
            used_metrics={"M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"},
            declared_metrics=frozenset(
                ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07", "M-08", "M-09", "M-10"]
            ),
            used_source_types=set(),
            declared_source_types=frozenset(),
        )
        assert cap.metric_coverage == 0.7

    def test_source_type_coverage(self):
        cap = CapabilityCoverage()
        cap.recalculate(
            used_metrics=set(),
            declared_metrics=frozenset(),
            used_source_types={"commit"},
            declared_source_types=frozenset(["commit", "file", "ci"]),
        )
        assert cap.source_type_coverage == pytest.approx(1 / 3)

    def test_overall_coverage(self):
        cap = CapabilityCoverage()
        cap.recalculate(
            used_metrics={"M-01"},
            declared_metrics=frozenset(["M-01", "M-02"]),
            used_source_types=set(),
            declared_source_types=frozenset(),
        )
        assert cap.metric_coverage == 0.5
        assert cap.overall_coverage == pytest.approx(0.5 * 0.7)


class TestProviderHealthMonitor:
    def test_register_provider(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        health = monitor.get_health("git")
        assert health is not None
        assert health.status == HealthStatus.UNKNOWN

    def test_unregister_provider(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        monitor.unregister_provider("git")
        with pytest.raises(KeyError):
            monitor.get_health("git")

    def test_report_health(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        health = ProviderHealth(status=HealthStatus.HEALTHY, health_score=0.95)
        monitor.report_health("git", health)
        assert monitor.get_health("git").status == HealthStatus.HEALTHY

    def test_record_execution(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        monitor.record_execution("git", 100.0, True, observation_count=5)
        metrics = monitor.get_execution_metrics("git")
        assert metrics is not None
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 1

    def test_record_error(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        monitor.record_error("git", "ConnectionError", "connection failed")
        history = monitor.get_error_history("git")
        assert history is not None
        assert len(history.records) == 1

    def test_health_status_derivation_healthy(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        for _ in range(10):
            monitor.record_execution("git", 100.0, True)
        health = monitor.get_health("git")
        assert health.status == HealthStatus.HEALTHY

    def test_health_status_derivation_unhealthy(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        for _ in range(10):
            monitor.record_execution("git", 100.0, False)
        health = monitor.get_health("git")
        assert health.status == HealthStatus.UNHEALTHY

    def test_reset_health(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        monitor.record_execution("git", 100.0, True)
        monitor.reset_health("git")
        health = monitor.get_health("git")
        assert health.status == HealthStatus.UNKNOWN

    def test_get_latency_tracker(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        monitor.record_execution("git", 100.0, True)
        tracker = monitor.get_latency_tracker("git")
        assert tracker is not None

    def test_get_availability(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        avail = monitor.get_availability("git")
        assert avail is not None
        assert avail.consecutive_unavailable == 0

    def test_get_registered_providers(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        monitor.register_provider("coverage")
        providers = monitor.get_registered_providers()
        assert len(providers) == 2

    def test_get_capability_coverage(self):
        monitor = ProviderHealthMonitor()
        monitor.register_provider("git")
        coverage = monitor.get_capability_coverage("git")
        assert coverage is not None
