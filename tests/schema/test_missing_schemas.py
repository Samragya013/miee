"""
Tests for the five newly added BSD schemas:
- AnalysisResult (BSD §12)
- BenchmarkDataset (BSD §13)
- Configuration (BSD §17)
- JobManifest (BSD §18)
- StateObject (BSD §19)
"""

import datetime
from pathlib import Path

import pytest

from miie.schemas.models import (
    AnalysisResult,
    BenchmarkDataset,
    ConfidenceScore,
    Configuration,
    DetectorConfig,
    DetectorResults,
    EvidencePackage,
    ExplanationReport,
    IntegrityScore,
    JobManifest,
    MetricDataFrame,
    PathologyMetadata,
    Provenance,
    RecoveryMetadata,
    RepositoryContext,
    RunMetadata,
    ScorePackage,
    StateObject,
    StateTransition,
    SyntheticRepositoryMetadata,
    WindowDefinition,
)
from miie.schemas.serialization import json_dumps, json_loads

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_repo(**overrides):
    defaults = dict(
        repo_id="repo_001",
        local_path=Path("/tmp/repo"),
        is_remote=False,
        total_commits=50,
        first_commit_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        last_commit_date=datetime.datetime(2020, 6, 30, tzinfo=datetime.timezone.utc),
        contributor_count=3,
    )
    defaults.update(overrides)
    return RepositoryContext(**defaults)


def _make_window(**overrides):
    defaults = dict(
        window_id="w01",
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2020, 3, 31),
        commits=25,
        strategy="time",
    )
    defaults.update(overrides)
    return WindowDefinition(**defaults)


def _make_metric_df(**overrides):
    defaults = dict(
        repo_id="repo_001",
        run_id="run_001",
        timestamp=datetime.datetime(2020, 7, 1, tzinfo=datetime.timezone.utc),
        metrics={"M-01": {"values": [1.0, 2.0, 3.0]}},
    )
    defaults.update(overrides)
    return MetricDataFrame(**defaults)


def _make_detector_results(**overrides):
    defaults = dict(detector_outputs={"D-01": {"flagged": False}})
    defaults.update(overrides)
    return DetectorResults(**defaults)


def _make_integrity_score(**overrides):
    defaults = dict(overall=0.85, per_metric={"M-01": 0.90}, formula_version="1.0.0")
    defaults.update(overrides)
    return IntegrityScore(**defaults)


def _make_confidence_score(**overrides):
    defaults = dict(overall=0.75, factors={"sample_size": 0.8}, band="medium")
    defaults.update(overrides)
    return ConfidenceScore(**defaults)


def _make_score_package(**overrides):
    defaults = dict(
        integrity=_make_integrity_score(),
        confidence=_make_confidence_score(),
        timestamp=datetime.datetime(2020, 7, 1, tzinfo=datetime.timezone.utc),
        config_hash="abc123",
    )
    defaults.update(overrides)
    return ScorePackage(**defaults)


def _make_provenance(**overrides):
    defaults = dict(
        miie_version="1.0.0",
        config_hash="abc123",
        timestamp="2020-07-01T00:00:00Z",
        seed=42,
        platform="linux",
        python_version="3.10.0",
        dependency_hash=None,
    )
    defaults.update(overrides)
    return Provenance(**defaults)


def _make_evidence_package(**overrides):
    defaults = dict(
        provenance=_make_provenance(),
        windows=[_make_window()],
        metrics={"M-01": {"count": 3}},
        detector_outputs=_make_detector_results(),
        scores=_make_score_package(),
        warnings=[],
    )
    defaults.update(overrides)
    return EvidencePackage(**defaults)


def _make_explanation_report(**overrides):
    defaults = dict(narratives=["All metrics stable"], recommendations=["No action needed"])
    defaults.update(overrides)
    return ExplanationReport(**defaults)


def _make_run_metadata(**overrides):
    defaults = dict(
        duration_seconds=12.5,
        memory_peak_mb=256.0,
        cpu_time_seconds=10.3,
        stage_timings={"ingestion": 2.0, "extraction": 5.0, "detection": 3.0},
    )
    defaults.update(overrides)
    return RunMetadata(**defaults)


# ===================================================================
# AnalysisResult (BSD §12)
# ===================================================================


class TestRunMetadata:
    def test_valid_construction(self):
        rm = _make_run_metadata()
        assert rm.duration_seconds == 12.5
        assert rm.memory_peak_mb == 256.0
        assert rm.cpu_time_seconds == 10.3
        assert "ingestion" in rm.stage_timings

    def test_invalid_negative_duration(self):
        with pytest.raises(ValueError, match="duration_seconds"):
            _make_run_metadata(duration_seconds=-1.0)

    def test_invalid_negative_memory(self):
        with pytest.raises(ValueError, match="memory_peak_mb"):
            _make_run_metadata(memory_peak_mb=-10.0)

    def test_invalid_negative_cpu_time(self):
        with pytest.raises(ValueError, match="cpu_time_seconds"):
            _make_run_metadata(cpu_time_seconds=-5.0)

    def test_invalid_negative_stage_timing(self):
        with pytest.raises(ValueError, match="stage_timings"):
            _make_run_metadata(stage_timings={"bad_stage": -1.0})

    def test_serialization_roundtrip(self):
        rm = _make_run_metadata()
        d = {
            "duration_seconds": rm.duration_seconds,
            "memory_peak_mb": rm.memory_peak_mb,
            "cpu_time_seconds": rm.cpu_time_seconds,
            "stage_timings": rm.stage_timings,
        }
        j1 = json_dumps(d)
        parsed = json_loads(j1)
        j2 = json_dumps(parsed)
        assert j1 == j2


class TestAnalysisResult:
    def _build(self, **overrides):
        defaults = dict(
            miie_version="1.0.0",
            generated_at="2020-07-01T00:00:00Z",
            config_hash="abc123",
            repository=_make_repo(),
            windows=[_make_window()],
            metrics=_make_metric_df(),
            detector_results=_make_detector_results(),
            scores=_make_score_package(),
            evidence=_make_evidence_package(),
            explanations=_make_explanation_report(),
            run_metadata=_make_run_metadata(),
        )
        defaults.update(overrides)
        return AnalysisResult(**defaults)

    def test_valid_construction(self):
        ar = self._build()
        assert ar.miie_version == "1.0.0"
        assert len(ar.windows) == 1
        assert isinstance(ar.run_metadata, RunMetadata)

    def test_empty_version_rejected(self):
        with pytest.raises(ValueError, match="miie_version"):
            self._build(miie_version="")

    def test_empty_generated_at_rejected(self):
        with pytest.raises(ValueError, match="generated_at"):
            self._build(generated_at="")

    def test_empty_config_hash_rejected(self):
        with pytest.raises(ValueError, match="config_hash"):
            self._build(config_hash="")

    def test_invalid_repository_type(self):
        with pytest.raises(ValueError, match="repository"):
            self._build(repository="not_a_repo")

    def test_invalid_window_type(self):
        with pytest.raises(ValueError, match=r"windows\[0\]"):
            self._build(windows=["not_a_window"])

    def test_invalid_metrics_type(self):
        with pytest.raises(ValueError, match="metrics"):
            self._build(metrics="not_metrics")

    def test_invalid_detector_results_type(self):
        with pytest.raises(ValueError, match="detector_results"):
            self._build(detector_results="not_dr")

    def test_invalid_scores_type(self):
        with pytest.raises(ValueError, match="scores"):
            self._build(scores="not_scores")

    def test_invalid_evidence_type(self):
        with pytest.raises(ValueError, match="evidence"):
            self._build(evidence="not_evidence")

    def test_invalid_explanations_type(self):
        with pytest.raises(ValueError, match="explanations"):
            self._build(explanations="not_explanations")

    def test_invalid_run_metadata_type(self):
        with pytest.raises(ValueError, match="run_metadata"):
            self._build(run_metadata="not_rm")


# ===================================================================
# BenchmarkDataset (BSD §13)
# ===================================================================


class TestSyntheticRepositoryMetadata:
    def test_valid_construction(self):
        srm = SyntheticRepositoryMetadata(
            repo_id="repo_001",
            category="synthetic_healthy",
            language="Python",
            parameters={"duration_days": 90, "total_commits": 100},
        )
        assert srm.repo_id == "repo_001"
        assert srm.category == "synthetic_healthy"

    def test_invalid_repo_id_pattern(self):
        with pytest.raises(ValueError, match="repo_id"):
            SyntheticRepositoryMetadata(
                repo_id="bad_id",
                category="real_world",
                language="Python",
                parameters={},
            )

    def test_invalid_category(self):
        with pytest.raises(ValueError, match="category"):
            SyntheticRepositoryMetadata(
                repo_id="repo_001",
                category="unknown",
                language="Python",
                parameters={},
            )

    def test_empty_language_rejected(self):
        with pytest.raises(ValueError, match="language"):
            SyntheticRepositoryMetadata(
                repo_id="repo_001",
                category="real_world",
                language="",
                parameters={},
            )

    def test_serialization_roundtrip(self):
        srm = SyntheticRepositoryMetadata(
            repo_id="repo_042",
            category="synthetic_pathological",
            language="JavaScript",
            parameters={"duration_days": 60},
        )
        d = {
            "repo_id": srm.repo_id,
            "category": srm.category,
            "language": srm.language,
            "parameters": srm.parameters,
        }
        j1 = json_dumps(d)
        parsed = json_loads(j1)
        j2 = json_dumps(parsed)
        assert j1 == j2


class TestPathologyMetadata:
    def test_valid_construction(self):
        pm = PathologyMetadata(
            event_type="MDE-01",
            metric_id="M-01",
            target_window="w01",
            severity=0.75,
        )
        assert pm.event_type == "MDE-01"
        assert pm.severity == 0.75

    def test_invalid_event_type(self):
        with pytest.raises(ValueError, match="event_type"):
            PathologyMetadata(
                event_type="MDE-99",
                metric_id="M-01",
                target_window="w01",
                severity=0.5,
            )

    def test_empty_metric_id_rejected(self):
        with pytest.raises(ValueError, match="metric_id"):
            PathologyMetadata(
                event_type="MDE-02",
                metric_id="",
                target_window="w01",
                severity=0.5,
            )

    def test_empty_target_window_rejected(self):
        with pytest.raises(ValueError, match="target_window"):
            PathologyMetadata(
                event_type="MDE-01",
                metric_id="M-01",
                target_window="",
                severity=0.5,
            )

    def test_severity_out_of_range(self):
        with pytest.raises(ValueError, match="severity"):
            PathologyMetadata(
                event_type="MDE-01",
                metric_id="M-01",
                target_window="w01",
                severity=1.5,
            )

    def test_negative_drift_magnitude_rejected(self):
        with pytest.raises(ValueError, match="drift_magnitude"):
            PathologyMetadata(
                event_type="MDE-01",
                metric_id="M-01",
                target_window="w01",
                severity=0.5,
                drift_magnitude=-0.1,
            )

    def test_correlation_change_out_of_range(self):
        with pytest.raises(ValueError, match="correlation_change"):
            PathologyMetadata(
                event_type="MDE-02",
                metric_id="M-01",
                target_window="w01",
                severity=0.5,
                correlation_change=1.5,
            )

    def test_optional_fields_default_none(self):
        pm = PathologyMetadata(
            event_type="MDE-03",
            metric_id="M-02",
            target_window="w02",
            severity=0.3,
        )
        assert pm.drift_direction is None
        assert pm.drift_magnitude is None
        assert pm.metric_pair is None
        assert pm.breakdown_type is None
        assert pm.correlation_change is None
        assert pm.threshold is None
        assert pm.compression_ratio is None


class TestBenchmarkDataset:
    def _build(self, **overrides):
        defaults = dict(
            suite_id="bench_001",
            version="1.0",
            description="Test benchmark",
            num_datasets=5,
            metrics_included=["M-01", "M-02"],
            detector_target="D-01",
            window_strategy="time",
            window_size_days=90,
            random_seed=42,
            pathology_ratio=0.3,
            datasets=[
                SyntheticRepositoryMetadata(
                    repo_id="repo_001",
                    category="synthetic_healthy",
                    language="Python",
                    parameters={},
                )
            ],
            pathologies=[
                PathologyMetadata(
                    event_type="MDE-01",
                    metric_id="M-01",
                    target_window="w01",
                    severity=0.5,
                )
            ],
        )
        defaults.update(overrides)
        return BenchmarkDataset(**defaults)

    def test_valid_construction(self):
        bd = self._build()
        assert bd.suite_id == "bench_001"
        assert bd.num_datasets == 5
        assert len(bd.datasets) == 1
        assert len(bd.pathologies) == 1

    def test_empty_suite_id_rejected(self):
        with pytest.raises(ValueError, match="suite_id"):
            self._build(suite_id="")

    def test_empty_version_rejected(self):
        with pytest.raises(ValueError, match="version"):
            self._build(version="")

    def test_empty_description_rejected(self):
        with pytest.raises(ValueError, match="description"):
            self._build(description="")

    def test_zero_num_datasets_rejected(self):
        with pytest.raises(ValueError, match="num_datasets"):
            self._build(num_datasets=0)

    def test_empty_metrics_included_rejected(self):
        with pytest.raises(ValueError, match="metrics_included"):
            self._build(metrics_included=[])

    def test_empty_detector_target_rejected(self):
        with pytest.raises(ValueError, match="detector_target"):
            self._build(detector_target="")

    def test_zero_window_size_rejected(self):
        with pytest.raises(ValueError, match="window_size_days"):
            self._build(window_size_days=0)

    def test_pathology_ratio_out_of_range(self):
        with pytest.raises(ValueError, match="pathology_ratio"):
            self._build(pathology_ratio=1.5)

    def test_annotation_kappa_out_of_range(self):
        with pytest.raises(ValueError, match="annotation_kappa"):
            self._build(annotation_kappa=-0.1)

    def test_invalid_dataset_type(self):
        with pytest.raises(ValueError, match=r"datasets\[0\]"):
            self._build(datasets=["not_a_dataset"])

    def test_invalid_pathology_type(self):
        with pytest.raises(ValueError, match=r"pathologies\[0\]"):
            self._build(pathologies=["not_a_pathology"])

    def test_defaults_empty_lists(self):
        bd = BenchmarkDataset(
            suite_id="s1",
            version="1.0",
            description="d",
            num_datasets=1,
            metrics_included=["M-01"],
            detector_target="D-01",
            window_strategy="time",
            window_size_days=30,
            random_seed=1,
            pathology_ratio=0.0,
        )
        assert bd.datasets == []
        assert bd.pathologies == []
        assert bd.annotation_kappa is None


# ===================================================================
# Configuration (BSD §17)
# ===================================================================


class TestDetectorConfig:
    def test_valid_construction(self):
        dc = DetectorConfig()
        assert dc.alpha == 0.05
        assert dc.psi_threshold == 0.25
        assert dc.correlation_threshold == 0.3
        assert dc.margin == 0.02
        assert dc.bootstrap_iterations == 1000
        assert dc.bootstrap_seed == 42

    def test_custom_values(self):
        dc = DetectorConfig(alpha=0.01, psi_threshold=0.5, bootstrap_iterations=500)
        assert dc.alpha == 0.01
        assert dc.psi_threshold == 0.5
        assert dc.bootstrap_iterations == 500

    def test_invalid_alpha_zero(self):
        with pytest.raises(ValueError, match="alpha"):
            DetectorConfig(alpha=0.0)

    def test_invalid_alpha_one(self):
        with pytest.raises(ValueError, match="alpha"):
            DetectorConfig(alpha=1.0)

    def test_invalid_alpha_negative(self):
        with pytest.raises(ValueError, match="alpha"):
            DetectorConfig(alpha=-0.1)

    def test_invalid_psi_threshold(self):
        with pytest.raises(ValueError, match="psi_threshold"):
            DetectorConfig(psi_threshold=-0.1)

    def test_invalid_correlation_threshold(self):
        with pytest.raises(ValueError, match="correlation_threshold"):
            DetectorConfig(correlation_threshold=1.5)

    def test_invalid_margin(self):
        with pytest.raises(ValueError, match="margin"):
            DetectorConfig(margin=-0.01)

    def test_invalid_bootstrap_iterations(self):
        with pytest.raises(ValueError, match="bootstrap_iterations"):
            DetectorConfig(bootstrap_iterations=0)


class TestConfiguration:
    def test_valid_construction(self):
        c = Configuration(repo="/path/to/repo")
        assert c.repo == "/path/to/repo"
        assert c.window_size == 90
        assert c.seed == 42
        assert c.verbose is False
        assert c.keep_cache is False
        assert c.shallow_depth == 1
        assert c.output_dir == "./output"
        assert isinstance(c.detector_config, DetectorConfig)

    def test_defaults_correct(self):
        c = Configuration(repo="test")
        assert c.metrics == ["all"]
        assert c.window_strategy == "time"
        assert c.detectors == ["all"]
        assert c.output_formats == ["json"]
        assert c.exclude_bots is False
        assert c.thresholds == {}
        assert c.detector_weights == {"D-01": 0.40, "D-02": 0.35, "D-03": 0.25}

    def test_empty_repo_rejected(self):
        with pytest.raises(ValueError, match="repo"):
            Configuration(repo="")

    def test_zero_window_size_rejected(self):
        with pytest.raises(ValueError, match="window_size"):
            Configuration(repo="test", window_size=0)

    def test_empty_output_formats_rejected(self):
        with pytest.raises(ValueError, match="output_formats"):
            Configuration(repo="test", output_formats=[])

    def test_detector_weights_not_summing_to_one(self):
        with pytest.raises(ValueError, match="detector_weights"):
            Configuration(
                repo="test",
                detector_weights={"D-01": 0.5, "D-02": 0.5, "D-03": 0.5},
            )

    def test_zero_shallow_depth_rejected(self):
        with pytest.raises(ValueError, match="shallow_depth"):
            Configuration(repo="test", shallow_depth=0)

    def test_invalid_detector_config_type(self):
        with pytest.raises(ValueError, match="detector_config"):
            Configuration(repo="test", detector_config="not_dc")

    def test_serialization_roundtrip(self):
        c = Configuration(repo="/repo")
        d = {
            "repo": c.repo,
            "since": c.since,
            "until": c.until,
            "metrics": c.metrics,
            "window_strategy": c.window_strategy,
            "window_size": c.window_size,
            "detectors": c.detectors,
            "output_formats": c.output_formats,
            "exclude_bots": c.exclude_bots,
            "thresholds": c.thresholds,
            "detector_weights": c.detector_weights,
            "seed": c.seed,
            "output_dir": c.output_dir,
            "verbose": c.verbose,
            "keep_cache": c.keep_cache,
            "shallow_depth": c.shallow_depth,
        }
        j1 = json_dumps(d)
        parsed = json_loads(j1)
        j2 = json_dumps(parsed)
        assert j1 == j2


# ===================================================================
# JobManifest (BSD §18)
# ===================================================================


class TestJobManifest:
    def test_valid_construction(self):
        jm = JobManifest(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            job_type="analyze",
            job_params={"repo": "/path"},
            output_dir="./output",
            created_at="2020-07-01T00:00:00Z",
            status="created",
        )
        assert jm.job_id == "550e8400-e29b-41d4-a716-446655440000"
        assert jm.job_type == "analyze"
        assert jm.status == "created"
        assert jm.progress == 0.0

    def test_defaults(self):
        jm = JobManifest(
            job_id="j1",
            job_type="benchmark",
            job_params={},
            output_dir="./out",
            created_at="2020-01-01T00:00:00Z",
            status="queued",
        )
        assert jm.progress == 0.0
        assert jm.current_stage is None
        assert jm.result_paths == {}
        assert jm.error_metadata is None

    def test_empty_job_id_rejected(self):
        with pytest.raises(ValueError, match="job_id"):
            JobManifest(
                job_id="",
                job_type="analyze",
                job_params={},
                output_dir="./out",
                created_at="2020-01-01T00:00:00Z",
                status="created",
            )

    def test_invalid_job_type(self):
        with pytest.raises(ValueError, match="job_type"):
            JobManifest(
                job_id="j1",
                job_type="unknown",
                job_params={},
                output_dir="./out",
                created_at="2020-01-01T00:00:00Z",
                status="created",
            )

    def test_empty_created_at_rejected(self):
        with pytest.raises(ValueError, match="created_at"):
            JobManifest(
                job_id="j1",
                job_type="explain",
                job_params={},
                output_dir="./out",
                created_at="",
                status="created",
            )

    def test_invalid_status(self):
        with pytest.raises(ValueError, match="status"):
            JobManifest(
                job_id="j1",
                job_type="export",
                job_params={},
                output_dir="./out",
                created_at="2020-01-01T00:00:00Z",
                status="unknown_status",
            )

    def test_progress_out_of_range(self):
        with pytest.raises(ValueError, match="progress"):
            JobManifest(
                job_id="j1",
                job_type="generate",
                job_params={},
                output_dir="./out",
                created_at="2020-01-01T00:00:00Z",
                status="running",
                progress=1.5,
            )

    def test_all_valid_job_types(self):
        for jtype in ("analyze", "benchmark", "explain", "export", "generate"):
            jm = JobManifest(
                job_id="j1",
                job_type=jtype,
                job_params={},
                output_dir="./out",
                created_at="2020-01-01T00:00:00Z",
                status="created",
            )
            assert jm.job_type == jtype

    def test_all_valid_statuses(self):
        for status in (
            "created",
            "queued",
            "running",
            "completed",
            "failed",
            "cancelled",
        ):
            jm = JobManifest(
                job_id="j1",
                job_type="analyze",
                job_params={},
                output_dir="./out",
                created_at="2020-01-01T00:00:00Z",
                status=status,
            )
            assert jm.status == status

    def test_serialization_roundtrip(self):
        jm = JobManifest(
            job_id="j1",
            job_type="analyze",
            job_params={"key": "value"},
            output_dir="./out",
            created_at="2020-07-01T00:00:00Z",
            status="completed",
            progress=1.0,
            current_stage="done",
            result_paths={"json": "./out/result.json"},
        )
        d = {
            "job_id": jm.job_id,
            "job_type": jm.job_type,
            "job_params": jm.job_params,
            "output_dir": jm.output_dir,
            "created_at": jm.created_at,
            "status": jm.status,
            "progress": jm.progress,
            "current_stage": jm.current_stage,
            "result_paths": jm.result_paths,
            "error_metadata": jm.error_metadata,
        }
        j1 = json_dumps(d)
        parsed = json_loads(j1)
        j2 = json_dumps(parsed)
        assert j1 == j2


# ===================================================================
# StateObject (BSD §19)
# ===================================================================


class TestStateTransition:
    def test_valid_construction(self):
        st = StateTransition(
            status="running",
            timestamp="2020-07-01T00:00:00Z",
            stage="extraction",
            progress=0.5,
        )
        assert st.status == "running"
        assert st.stage == "extraction"
        assert st.progress == 0.5

    def test_defaults(self):
        st = StateTransition(status="created", timestamp="2020-01-01T00:00:00Z")
        assert st.stage is None
        assert st.progress == 0.0

    def test_invalid_status(self):
        with pytest.raises(ValueError, match="status"):
            StateTransition(status="bogus", timestamp="2020-01-01T00:00:00Z")

    def test_empty_timestamp_rejected(self):
        with pytest.raises(ValueError, match="timestamp"):
            StateTransition(status="running", timestamp="")

    def test_progress_out_of_range(self):
        with pytest.raises(ValueError, match="progress"):
            StateTransition(status="running", timestamp="2020-01-01T00:00:00Z", progress=2.0)

    def test_all_valid_statuses(self):
        for status in (
            "created",
            "queued",
            "running",
            "completed",
            "failed",
            "cancelled",
        ):
            st = StateTransition(status=status, timestamp="2020-01-01T00:00:00Z")
            assert st.status == status


class TestRecoveryMetadata:
    def test_valid_construction(self):
        rm = RecoveryMetadata(
            last_completed_stage="extraction",
            checkpoint_path="/tmp/checkpoint.pkl",
            retry_count=2,
        )
        assert rm.last_completed_stage == "extraction"
        assert rm.retry_count == 2

    def test_defaults(self):
        rm = RecoveryMetadata()
        assert rm.last_completed_stage is None
        assert rm.checkpoint_path is None
        assert rm.retry_count == 0

    def test_negative_retry_count_rejected(self):
        with pytest.raises(ValueError, match="retry_count"):
            RecoveryMetadata(retry_count=-1)


class TestStateObject:
    def test_valid_construction(self):
        so = StateObject(
            job_id="j1",
            current_status="running",
            history=[
                StateTransition(status="created", timestamp="2020-07-01T00:00:00Z"),
                StateTransition(status="running", timestamp="2020-07-01T00:01:00Z"),
            ],
        )
        assert so.job_id == "j1"
        assert so.current_status == "running"
        assert len(so.history) == 2

    def test_with_recovery_metadata(self):
        rm = RecoveryMetadata(last_completed_stage="ingestion", retry_count=1)
        so = StateObject(
            job_id="j1",
            current_status="failed",
            history=[
                StateTransition(status="created", timestamp="2020-07-01T00:00:00Z"),
                StateTransition(status="running", timestamp="2020-07-01T00:01:00Z"),
                StateTransition(status="failed", timestamp="2020-07-01T00:02:00Z"),
            ],
            recovery_metadata=rm,
        )
        assert so.recovery_metadata.last_completed_stage == "ingestion"
        assert so.recovery_metadata.retry_count == 1

    def test_empty_job_id_rejected(self):
        with pytest.raises(ValueError, match="job_id"):
            StateObject(
                job_id="",
                current_status="created",
                history=[],
            )

    def test_invalid_current_status(self):
        with pytest.raises(ValueError, match="current_status"):
            StateObject(
                job_id="j1",
                current_status="unknown",
                history=[],
            )

    def test_invalid_history_item_type(self):
        with pytest.raises(ValueError, match=r"history\[0\]"):
            StateObject(
                job_id="j1",
                current_status="running",
                history=["not_a_transition"],
            )

    def test_invalid_recovery_metadata_type(self):
        with pytest.raises(ValueError, match="recovery_metadata"):
            StateObject(
                job_id="j1",
                current_status="running",
                history=[],
                recovery_metadata="not_rm",
            )

    def test_recovery_metadata_none_allowed(self):
        so = StateObject(
            job_id="j1",
            current_status="completed",
            history=[],
            recovery_metadata=None,
        )
        assert so.recovery_metadata is None

    def test_serialization_roundtrip(self):
        so = StateObject(
            job_id="j1",
            current_status="completed",
            history=[
                StateTransition(status="created", timestamp="2020-07-01T00:00:00Z"),
                StateTransition(status="completed", timestamp="2020-07-01T00:05:00Z", progress=1.0),
            ],
            recovery_metadata=RecoveryMetadata(retry_count=0),
        )
        d = {
            "job_id": so.job_id,
            "current_status": so.current_status,
            "history": [
                {
                    "status": t.status,
                    "timestamp": t.timestamp,
                    "stage": t.stage,
                    "progress": t.progress,
                }
                for t in so.history
            ],
            "recovery_metadata": (
                {
                    "last_completed_stage": so.recovery_metadata.last_completed_stage,
                    "checkpoint_path": so.recovery_metadata.checkpoint_path,
                    "retry_count": so.recovery_metadata.retry_count,
                }
                if so.recovery_metadata
                else None
            ),
        }
        j1 = json_dumps(d)
        parsed = json_loads(j1)
        j2 = json_dumps(parsed)
        assert j1 == j2
