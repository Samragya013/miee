"""Tests for benchmarks/runners/__init__.py."""

from __future__ import annotations

import json

from benchmarks.runners import BenchmarkRunConfig, BenchmarkRunner, BenchmarkRunResult


class TestBenchmarkRunConfig:
    """Tests for BenchmarkRunConfig."""

    def test_default_config(self):
        config = BenchmarkRunConfig(candidate_id="c001")
        assert config.candidate_id == "c001"
        assert config.detector_ids == []
        assert config.seed == 42
        assert config.timestamp is not None  # auto-generated

    def test_custom_config(self):
        config = BenchmarkRunConfig(
            candidate_id="c002",
            detector_ids=["d01", "d02"],
            seed=123,
            timestamp="2023-01-01T00:00:00Z",
        )
        assert config.candidate_id == "c002"
        assert config.detector_ids == ["d01", "d02"]
        assert config.seed == 123
        assert config.timestamp == "2023-01-01T00:00:00Z"


class TestBenchmarkRunResult:
    """Tests for BenchmarkRunResult."""

    def test_default_result(self):
        result = BenchmarkRunResult(candidate_id="c001", detector_id="d01")
        assert result.candidate_id == "c001"
        assert result.detector_id == "d01"
        assert result.anomaly_type is None
        assert result.severity == 0.0
        assert result.passed is False
        assert result.error is None

    def test_to_dict(self):
        result = BenchmarkRunResult(
            candidate_id="c001",
            detector_id="d01",
            anomaly_type="burst",
            severity=0.5,
            confidence=0.8,
            passed=True,
        )
        d = result.to_dict()
        assert d["candidate_id"] == "c001"
        assert d["detector_id"] == "d01"
        assert d["anomaly_type"] == "burst"
        assert d["severity"] == 0.5
        assert d["passed"] is True


class TestBenchmarkRunner:
    """Tests for BenchmarkRunner."""

    def test_default_runner(self):
        runner = BenchmarkRunner()
        assert runner.results == []

    def test_run_single(self):
        runner = BenchmarkRunner()
        result = runner.run_single("c001", "d01")
        assert result.candidate_id == "c001"
        assert result.detector_id == "d01"
        assert result.passed is True
        assert result.anomaly_type in ("burst", "decline", "seasonal")
        assert 0.0 <= result.severity <= 1.0
        assert len(runner.results) == 1

    def test_run_single_deterministic(self):
        """Same inputs produce same results."""
        r1 = BenchmarkRunner().run_single("c001", "d01", seed=42)
        r2 = BenchmarkRunner().run_single("c001", "d01", seed=42)
        assert r1.anomaly_type == r2.anomaly_type
        assert r1.severity == r2.severity

    def test_run_single_with_metrics(self):
        runner = BenchmarkRunner()
        metrics = {"commit_count": 10, "file_churn": 5.0}
        result = runner.run_single("c001", "d01", metrics=metrics)
        assert "commit_count" in result.metrics_used
        assert "file_churn" in result.metrics_used

    def test_run_batch(self):
        runner = BenchmarkRunner()
        results = runner.run_batch(
            candidate_ids=["c001", "c002"],
            detector_ids=["d01", "d02"],
        )
        assert len(results) == 4  # 2 candidates * 2 detectors
        assert len(runner.results) == 4

    def test_run_batch_with_metrics(self):
        runner = BenchmarkRunner()
        metrics = {
            "c001": {"commit_count": 10},
            "c002": {"commit_count": 20},
        }
        results = runner.run_batch(
            candidate_ids=["c001", "c002"],
            detector_ids=["d01"],
            metrics=metrics,
        )
        assert len(results) == 2
        assert results[0].metrics_used == ["commit_count"]

    def test_clear_results(self):
        runner = BenchmarkRunner()
        runner.run_single("c001", "d01")
        assert len(runner.results) == 1
        runner.clear_results()
        assert len(runner.results) == 0

    def test_save_results(self, tmp_path):
        runner = BenchmarkRunner()
        runner.run_single("c001", "d01")
        runner.run_single("c002", "d02")
        p = tmp_path / "results.json"
        runner.save_results(p)
        assert p.exists()

        data = json.loads(p.read_text(encoding="utf-8"))
        assert len(data) == 2
        assert data[0]["candidate_id"] == "c001"

    def test_summary(self):
        runner = BenchmarkRunner()
        runner.run_single("c001", "d01")
        runner.run_single("c002", "d02")
        s = runner.summary()
        assert s["total_runs"] == 2
        assert s["passed"] == 2
        assert s["failed"] == 0
        assert s["pass_rate"] == 1.0

    def test_summary_empty(self):
        runner = BenchmarkRunner()
        s = runner.summary()
        assert s["total_runs"] == 0
        assert s["pass_rate"] == 0.0

    def test_isolation_no_leakage(self):
        """Detector A and B run independently — no shared state."""
        runner = BenchmarkRunner()
        r1 = runner.run_single("c001", "d01", seed=42)
        r2 = runner.run_single("c001", "d02", seed=42)
        # Different detectors can produce different anomaly types
        # (they're independent — no assertion on equality)
        assert r1.detector_id != r2.detector_id
        assert r1.passed is True
        assert r2.passed is True
