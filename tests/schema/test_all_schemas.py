"""
Schema Validation Tests: All BSD v1.0 Schemas
Validates that every schema model enforces the constraints defined in
BSD-Engineering §5..§19.

Implements: ST-01..ST-10 (schema test coverage for output artifacts)
"""

import datetime
import pytest
from pathlib import Path
from dataclasses import FrozenInstanceError

from miie.schemas.models import (
    RepositoryContext,
    MetricDataFrame,
    WindowDefinition,
    D01Output,
    D02Output,
    D03Output,
    DetectorResults,
    IntegrityScore,
    ConfidenceScore,
    ScorePackage,
    Provenance,
    WarningItem,
    EvidencePackage,
    Explanation,
    ExplanationReport,
    BenchmarkRun,
    ConfusionMatrix,
    EvaluationResult,
    ReportOutput,
    GroundTruthLabel,
    GroundTruthInput,
    Annotation,
    RunMetadata,
    AnalysisResult,
    SyntheticRepositoryMetadata,
    PathologyMetadata,
    BenchmarkDataset,
    DetectorConfig,
    Configuration,
    JobManifest,
    StateTransition,
    RecoveryMetadata,
    StateObject,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def _today():
    return datetime.date.today()


def _valid_repo_ctx(**overrides):
    defaults = dict(
        repo_id="repo_001",
        local_path=Path("/tmp/repo"),
        is_remote=False,
        total_commits=50,
        contributor_count=3,
    )
    defaults.update(overrides)
    return RepositoryContext(**defaults)


def _valid_metric_df(**overrides):
    defaults = dict(
        repo_id="repo_001",
        run_id="run_001",
        timestamp=_utcnow(),
        metrics={"M-01": {"commits_per_week": [10.0, 12.0]}},
    )
    defaults.update(overrides)
    return MetricDataFrame(**defaults)


def _valid_window(**overrides):
    defaults = dict(
        window_id="w01",
        start_date=datetime.date(2024, 1, 1),
        end_date=datetime.date(2024, 3, 31),
        commits=10,
        strategy="time",
    )
    defaults.update(overrides)
    return WindowDefinition(**defaults)


def _valid_detector_results():
    return DetectorResults()


def _valid_integrity_score(**overrides):
    defaults = dict(
        overall=0.85,
        per_metric={"M-01": 0.90},
        formula_version="1.0.0",
    )
    defaults.update(overrides)
    return IntegrityScore(**defaults)


def _valid_confidence_score(**overrides):
    defaults = dict(
        overall=0.80,
        factors={"sample_size": 0.9},
        band="high",
    )
    defaults.update(overrides)
    return ConfidenceScore(**defaults)


def _valid_score_package():
    return ScorePackage(
        integrity=_valid_integrity_score(),
        confidence=_valid_confidence_score(),
        timestamp=_utcnow(),
        config_hash="abc123",
    )


def _valid_provenance():
    return Provenance(
        miie_version="1.0.0",
        config_hash="abc123",
        timestamp=_utcnow().isoformat(),
        seed=42,
        platform="linux",
        python_version="3.10.12",
        dependency_hash="def456",
    )


# ---------------------------------------------------------------------------
# ST-01: RepositoryContext
# ---------------------------------------------------------------------------


class TestRepositoryContextSchema:
    """ST-01: RepositoryContext (BSD §5.3)"""

    def test_valid_creation(self):
        ctx = _valid_repo_ctx()
        assert ctx.repo_id == "repo_001"
        assert ctx.total_commits >= 10

    def test_min_commits_enforced(self):
        with pytest.raises(ValueError, match="total_commits must be >= 10"):
            _valid_repo_ctx(total_commits=5)

    def test_min_contributors_enforced(self):
        with pytest.raises(ValueError, match="contributor_count must be >= 1"):
            _valid_repo_ctx(contributor_count=0)


# ---------------------------------------------------------------------------
# ST-02: MetricDataFrame
# ---------------------------------------------------------------------------


class TestMetricDataFrameSchema:
    """ST-02: MetricDataFrame (BSD §6.3)"""

    def test_valid_creation(self):
        mdf = _valid_metric_df()
        assert "M-01" in mdf.metrics

    def test_rejects_invalid_metric_id(self):
        with pytest.raises(ValueError, match="Invalid metric ID"):
            _valid_metric_df(metrics={"M-99": {}})

    def test_accepts_all_frozen_metrics(self):
        for i in range(1, 8):
            mdf = _valid_metric_df(metrics={f"M-{i:02d}": {}})
            assert f"M-{i:02d}" in mdf.metrics


# ---------------------------------------------------------------------------
# ST-03: WindowDefinition
# ---------------------------------------------------------------------------


class TestWindowDefinitionSchema:
    """ST-03: WindowDefinition (ACS §6.2)"""

    def test_valid_creation(self):
        w = _valid_window()
        assert w.window_id == "w01"

    def test_window_id_pattern(self):
        with pytest.raises(ValueError, match="window_id must match pattern"):
            WindowDefinition(
                window_id="invalid",
                start_date=datetime.date(2024, 1, 1),
                end_date=datetime.date(2024, 3, 31),
                commits=10,
                strategy="time",
            )

    def test_start_before_end(self):
        with pytest.raises(ValueError, match="start_date must be before end_date"):
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2024, 6, 1),
                end_date=datetime.date(2024, 1, 1),
                commits=10,
                strategy="time",
            )

    def test_min_commits(self):
        with pytest.raises(ValueError, match="commits must be >= 1"):
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2024, 1, 1),
                end_date=datetime.date(2024, 3, 31),
                commits=0,
                strategy="time",
            )


# ---------------------------------------------------------------------------
# ST-04: D01Output / D02Output / D03Output
# ---------------------------------------------------------------------------


class TestDetectorOutputSchemas:
    """ST-04: Detector output schemas (BSD §8.2..§8.4)"""

    def test_d01_valid_directions(self):
        for direction in ("mean_shift", "variance_collapse", "shape_change"):
            out = D01Output(
                ks_statistic=0.3, ks_p_value=0.01, psi_value=0.15,
                direction=direction, severity=0.5, flagged=True,
            )
            assert out.direction == direction

    def test_d01_invalid_direction(self):
        with pytest.raises(ValueError, match="direction must be one of"):
            D01Output(
                ks_statistic=0.3, ks_p_value=0.01, psi_value=0.15,
                direction="invalid", severity=0.5, flagged=True,
            )

    def test_d01_severity_bounds(self):
        with pytest.raises(ValueError, match="severity must be between"):
            D01Output(
                ks_statistic=0.3, ks_p_value=0.01, psi_value=0.15,
                direction="mean_shift", severity=1.5, flagged=True,
            )

    def test_d02_valid_breakdown_types(self):
        for btype in ("sudden_drop", "sign_reversal", "gradual_erosion", "confidence_exclusion"):
            out = D02Output(
                pearson_r=0.5, spearman_r=0.4, fisher_z_ci=(0.3, 0.7),
                breakdown_type=btype, delta_r=0.35, severity=0.6, flagged=True,
            )
            assert out.breakdown_type == btype

    def test_d02_none_breakdown_type(self):
        out = D02Output(
            pearson_r=0.5, spearman_r=0.4, fisher_z_ci=(0.3, 0.7),
            breakdown_type=None, delta_r=0.1, severity=0.1, flagged=False,
        )
        assert out.breakdown_type is None

    def test_d03_severity_bounds(self):
        with pytest.raises(ValueError, match="severity must be between"):
            D03Output(
                excess_mass_z=2.0, excess_mass_flag=True,
                dip_test_p_value=0.01, multimodal_flag=True,
                compression_index=0.4, threshold=50.0,
                severity=-0.1, flagged=True,
            )


# ---------------------------------------------------------------------------
# ST-05: DetectorResults
# ---------------------------------------------------------------------------


class TestDetectorResultsSchema:
    """ST-05: DetectorResults (BSD §8.5)"""

    def test_valid_creation(self):
        dr = DetectorResults()
        assert dr.d_01 == {}

    def test_rejects_invalid_detector_id_in_legacy(self):
        from miie.schemas.models import DetectorResult as LegacyDetectorResult
        with pytest.raises(ValueError, match="Invalid detector ID"):
            LegacyDetectorResult(detector_outputs={"D-04": {}})


# ---------------------------------------------------------------------------
# ST-06: ScorePackage (IntegrityScore + ConfidenceScore)
# ---------------------------------------------------------------------------


class TestScorePackageSchema:
    """ST-06: ScorePackage (ACS §9.2)"""

    def test_integrity_score_bounds(self):
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            IntegrityScore(overall=1.5, per_metric={}, formula_version="1.0")

    def test_integrity_per_metric_bounds(self):
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            IntegrityScore(overall=0.8, per_metric={"M-01": -0.1}, formula_version="1.0")

    def test_confidence_score_bounds(self):
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            ConfidenceScore(overall=0.8, factors={"x": 1.5}, band="high")

    def test_confidence_band_valid(self):
        for band in ("high", "medium", "low", "critical"):
            cs = ConfidenceScore(overall=0.8, factors={}, band=band)
            assert cs.band == band

    def test_confidence_band_invalid(self):
        with pytest.raises(ValueError, match="confidence.band must be one of"):
            ConfidenceScore(overall=0.8, factors={}, band="ultra")

    def test_score_package_requires_tz_aware_timestamp(self):
        with pytest.raises(ValueError, match="timezone-aware"):
            ScorePackage(
                integrity=_valid_integrity_score(),
                confidence=_valid_confidence_score(),
                timestamp=datetime.datetime(2024, 1, 1),  # naive!
                config_hash="x",
            )


# ---------------------------------------------------------------------------
# ST-07: EvidencePackage
# ---------------------------------------------------------------------------


class TestEvidencePackageSchema:
    """ST-07: EvidencePackage (ACS §10.1)"""

    def test_valid_creation(self):
        ep = EvidencePackage(
            provenance=_valid_provenance(),
            windows=[_valid_window()],
            metrics={},
            detector_outputs=_valid_detector_results(),
            scores=_valid_score_package(),
        )
        assert len(ep.windows) == 1

    def test_requires_provenance(self):
        with pytest.raises(ValueError, match="provenance must be a Provenance"):
            EvidencePackage(
                provenance="not_a_provenance",
                windows=[],
                metrics={},
                detector_outputs=_valid_detector_results(),
                scores=_valid_score_package(),
            )

    def test_requires_score_package(self):
        with pytest.raises(ValueError, match="scores must be a ScorePackage"):
            EvidencePackage(
                provenance=_valid_provenance(),
                windows=[],
                metrics={},
                detector_outputs=_valid_detector_results(),
                scores="not_a_score_package",
            )


# ---------------------------------------------------------------------------
# ST-08: ExplanationReport
# ---------------------------------------------------------------------------


class TestExplanationReportSchema:
    """ST-08: ExplanationReport (BSD §11.1)"""

    def test_valid_creation(self):
        er = ExplanationReport()
        assert er.explanations == []

    def test_explanation_severity_valid(self):
        for sev in ("mild", "moderate", "severe"):
            exp = Explanation(
                metric_id="M-01", detector_id="D-01",
                narrative="test", severity=sev,
                evidence_refs=[], confidence="high", rule_fired="R-01",
            )
            assert exp.severity == sev

    def test_explanation_severity_invalid(self):
        with pytest.raises(ValueError, match="severity must be one of"):
            Explanation(
                metric_id="M-01", detector_id="D-01",
                narrative="test", severity="critical",
                evidence_refs=[], confidence="high", rule_fired="R-01",
            )


# ---------------------------------------------------------------------------
# ST-09: BenchmarkRun / EvaluationResult
# ---------------------------------------------------------------------------


class TestBenchmarkSchemas:
    """ST-09: BenchmarkRun (BSD §15.1) and EvaluationResult (BSD §16.1)"""

    def test_benchmark_run_valid(self):
        br = BenchmarkRun(suite_id="B-01", detector_id="D-01")
        assert br.detector_id == "D-01"

    def test_benchmark_run_invalid_detector(self):
        with pytest.raises(ValueError, match="detector_id must be one of"):
            BenchmarkRun(detector_id="D-99")

    def test_confusion_matrix_non_negative(self):
        with pytest.raises(ValueError, match="must be >= 0"):
            ConfusionMatrix(tp=-1)

    def test_evaluation_result_bounds(self):
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            EvaluationResult(accuracy=2.0)


# ---------------------------------------------------------------------------
# ST-10: Configuration / JobManifest / StateObject
# ---------------------------------------------------------------------------


class TestConfigAndStateSchemas:
    """ST-10: Configuration (BSD §17), JobManifest (BSD §18), StateObject (BSD §19)"""

    def test_configuration_valid(self):
        cfg = Configuration(repo="https://github.com/test/repo")
        assert cfg.repo == "https://github.com/test/repo"
        assert cfg.seed == 42

    def test_configuration_empty_repo(self):
        with pytest.raises(ValueError, match="repo must not be empty"):
            Configuration(repo="")

    def test_configuration_weights_sum(self):
        with pytest.raises(ValueError, match="detector_weights must sum to 1.0"):
            Configuration(
                repo="x",
                detector_weights={"D-01": 0.5, "D-02": 0.5, "D-03": 0.5},
            )

    def test_detector_config_valid(self):
        dc = DetectorConfig()
        assert dc.alpha == 0.05

    def test_detector_config_invalid_alpha(self):
        with pytest.raises(ValueError, match="alpha must be between"):
            DetectorConfig(alpha=0.0)

    def test_job_manifest_valid(self):
        jm = JobManifest(
            job_id="test-uuid", job_type="analyze",
            job_params={}, output_dir="/tmp",
            created_at=_utcnow().isoformat(),
            status="created",
        )
        assert jm.status == "created"

    def test_job_manifest_invalid_type(self):
        with pytest.raises(ValueError, match="job_type must be one of"):
            JobManifest(
                job_id="x", job_type="invalid",
                job_params={}, output_dir="/tmp",
                created_at="2024-01-01T00:00:00Z",
                status="created",
            )

    def test_job_manifest_invalid_status(self):
        with pytest.raises(ValueError, match="status must be one of"):
            JobManifest(
                job_id="x", job_type="analyze",
                job_params={}, output_dir="/tmp",
                created_at="2024-01-01T00:00:00Z",
                status="pending",
            )

    def test_state_transition_valid(self):
        st = StateTransition(status="running", timestamp="2024-01-01T00:00:00Z")
        assert st.status == "running"

    def test_state_object_valid(self):
        so = StateObject(
            job_id="test-uuid",
            current_status="created",
            history=[],
        )
        assert so.job_id == "test-uuid"

    def test_recovery_metadata_non_negative_retry(self):
        with pytest.raises(ValueError, match="retry_count must be >= 0"):
            RecoveryMetadata(retry_count=-1)


# ---------------------------------------------------------------------------
# Additional BSD schemas: GroundTruth, BenchmarkDataset, AnalysisResult
# ---------------------------------------------------------------------------


class TestGroundTruthSchema:
    """BSD §14.1: GroundTruthLabel and GroundTruthInput"""

    def test_valid_label(self):
        lbl = GroundTruthLabel(
            repo_id="repo_001", metric_id="M-01",
            label=True, event_type="MDE-01",
        )
        assert lbl.label is True

    def test_invalid_repo_id_pattern(self):
        with pytest.raises(ValueError, match="repo_id must match pattern"):
            GroundTruthLabel(
                repo_id="bad_id", metric_id="M-01",
                label=True, event_type="MDE-01",
            )

    def test_invalid_event_type(self):
        with pytest.raises(ValueError, match="event_type must be one of"):
            GroundTruthLabel(
                repo_id="repo_001", metric_id="M-01",
                label=True, event_type="MDE-99",
            )

    def test_ground_truth_input_valid(self):
        gti = GroundTruthInput(suite_id="B-01", version="1.0.0")
        assert gti.suite_id == "B-01"


class TestBenchmarkDatasetSchema:
    """BSD §13: BenchmarkDataset"""

    def test_valid_dataset(self):
        bd = BenchmarkDataset(
            suite_id="B-01", version="1.0.0",
            description="test", num_datasets=50,
            metrics_included=["M-01"], detector_target="D-01",
            window_strategy="time", window_size_days=90,
            random_seed=42, pathology_ratio=0.3,
        )
        assert bd.num_datasets == 50

    def test_empty_suite_id(self):
        with pytest.raises(ValueError, match="suite_id must not be empty"):
            BenchmarkDataset(
                suite_id="", version="1.0",
                description="x", num_datasets=1,
                metrics_included=["M-01"], detector_target="D-01",
                window_strategy="time", window_size_days=90,
                random_seed=42, pathology_ratio=0.3,
            )

    def test_num_datasets_minimum(self):
        with pytest.raises(ValueError, match="num_datasets must be >= 1"):
            BenchmarkDataset(
                suite_id="B-01", version="1.0",
                description="x", num_datasets=0,
                metrics_included=["M-01"], detector_target="D-01",
                window_strategy="time", window_size_days=90,
                random_seed=42, pathology_ratio=0.3,
            )


class TestSyntheticRepositoryMetadataSchema:
    """BSD §13: SyntheticRepositoryMetadata"""

    def test_valid(self):
        srm = SyntheticRepositoryMetadata(
            repo_id="repo_001", category="real_world",
            language="python", parameters={"duration_days": 365},
        )
        assert srm.category == "real_world"

    def test_invalid_repo_id(self):
        with pytest.raises(ValueError, match="repo_id must match pattern"):
            SyntheticRepositoryMetadata(
                repo_id="bad", category="real_world",
                language="python", parameters={},
            )

    def test_invalid_category(self):
        with pytest.raises(ValueError, match="category must be one of"):
            SyntheticRepositoryMetadata(
                repo_id="repo_001", category="invalid",
                language="python", parameters={},
            )


class TestPathologyMetadataSchema:
    """BSD §13: PathologyMetadata"""

    def test_valid(self):
        pm = PathologyMetadata(
            event_type="MDE-01", metric_id="M-01",
            target_window="w01", severity=0.5,
        )
        assert pm.event_type == "MDE-01"

    def test_invalid_event_type(self):
        with pytest.raises(ValueError, match="event_type must be one of"):
            PathologyMetadata(
                event_type="MDE-99", metric_id="M-01",
                target_window="w01", severity=0.5,
            )

    def test_severity_bounds(self):
        with pytest.raises(ValueError, match="severity must be between"):
            PathologyMetadata(
                event_type="MDE-01", metric_id="M-01",
                target_window="w01", severity=1.5,
            )


class TestRunMetadataSchema:
    """BSD §12: RunMetadata"""

    def test_valid(self):
        rm = RunMetadata(
            duration_seconds=1.0, memory_peak_mb=100.0,
            cpu_time_seconds=0.8, stage_timings={"ingest": 0.5},
        )
        assert rm.duration_seconds == 1.0

    def test_negative_duration(self):
        with pytest.raises(ValueError, match="duration_seconds must be >= 0"):
            RunMetadata(
                duration_seconds=-1.0, memory_peak_mb=100.0,
                cpu_time_seconds=0.8, stage_timings={},
            )
