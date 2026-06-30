"""
Unit tests for PR-5: Observation-level evidence in EvidencePackage.

Tests cover:
- DetectorResult observation metadata fields
- EvidencePackage observation provenance fields
- EvidenceEngine observation evidence extraction
- Deterministic serialization
- Observation trace extraction
- Evidence completeness assessment
"""

import datetime
from pathlib import Path

from miie.processing.evidence import EvidenceEngine, MockEvidenceEngine
from miie.schemas.models import (
    ConfidenceScore,
    DetectorResult,
    DetectorResults,
    EvidencePackage,
    IntegrityScore,
    MetricDataFrame,
    Provenance,
    RepositoryContext,
    ScorePackage,
    WindowDefinition,
)


class TestDetectorResultObservationMetadata:
    """Test DetectorResult observation metadata fields."""

    def test_detector_result_observation_fields(self):
        """Test that DetectorResult has observation metadata fields."""
        result = DetectorResult(
            detector_outputs={"D-01": {"drift_detected": True}},
            observation_counts={"M-02": 100},
            window_ids=["w01", "w02"],
            sample_sizes={"M-02": 50},
            statistical_summaries={"M-02": {"mean": 10.0, "std": 2.0}},
            threshold_metadata={"alpha": 0.05},
            execution_timing={"D-01": 0.123},
            scientific_provenance={"method": "ks_test"},
        )

        assert result.observation_counts == {"M-02": 100}
        assert result.window_ids == ["w01", "w02"]
        assert result.sample_sizes == {"M-02": 50}
        assert result.statistical_summaries == {"M-02": {"mean": 10.0, "std": 2.0}}
        assert result.threshold_metadata == {"alpha": 0.05}
        assert result.execution_timing == {"D-01": 0.123}
        assert result.scientific_provenance == {"method": "ks_test"}

    def test_detector_result_defaults(self):
        """Test that DetectorResult has correct defaults."""
        result = DetectorResult()

        assert result.observation_counts == {}
        assert result.window_ids == []
        assert result.sample_sizes == {}
        assert result.statistical_summaries == {}
        assert result.threshold_metadata == {}
        assert result.execution_timing == {}
        assert result.scientific_provenance == {}

    def test_get_observation_metadata(self):
        """Test get_observation_metadata method."""
        result = DetectorResult(
            detector_outputs={
                "D-01": {
                    "drift_detected": True,
                    "observation_counts": {"M-02": 100},
                    "window_pairs_analyzed": [["w01", "w02"]],
                    "ks_statistics": {"M-02_w01_w02": 0.2},
                    "psi_values": {"M-02_w01_w02": 0.35},
                    "drift_events": [{"metric": "M-02"}],
                    "confidence_intervals": {"M-02": [0.1, 0.3]},
                }
            }
        )

        metadata = result.get_observation_metadata("D-01")
        assert metadata["observation_counts"] == {"M-02": 100}
        assert metadata["window_pairs"] == [["w01", "w02"]]
        assert metadata["ks_statistics"] == {"M-02_w01_w02": 0.2}
        assert metadata["psi_values"] == {"M-02_w01_w02": 0.35}
        assert metadata["drift_events"] == [{"metric": "M-02"}]
        assert metadata["confidence_intervals"] == {"M-02": [0.1, 0.3]}

    def test_get_observation_metadata_nonexistent_detector(self):
        """Test get_observation_metadata for non-existent detector."""
        result = DetectorResult()
        metadata = result.get_observation_metadata("D-99")
        assert metadata == {}

    def test_get_all_observation_counts(self):
        """Test get_all_observation_counts method."""
        result = DetectorResult(
            detector_outputs={
                "D-01": {"observation_counts": {"M-02": 100, "M-06": 50}},
                "D-02": {"observation_counts": {"M-02": 80, "M-03": 30}},
            }
        )

        counts = result.get_all_observation_counts()
        assert counts["M-02"] == 100  # max(100, 80)
        assert counts["M-06"] == 50
        assert counts["M-03"] == 30

    def test_get_execution_timing_summary(self):
        """Test get_execution_timing_summary method."""
        result = DetectorResult(execution_timing={"D-01": 0.1, "D-02": 0.2, "D-03": 0.15})

        summary = result.get_execution_timing_summary()
        assert abs(summary["total_time"] - 0.45) < 1e-10
        assert summary["detectors"] == {"D-01": 0.1, "D-02": 0.2, "D-03": 0.15}


class TestEvidencePackageObservationProvenance:
    """Test EvidencePackage observation provenance fields."""

    def test_evidence_package_observation_fields(self):
        """Test that EvidencePackage has observation provenance fields."""
        ep = EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123",
                timestamp="2025-01-01T00:00:00Z",
                seed=42,
                platform="linux",
                python_version="3.10.0",
                dependency_hash="def456",
            ),
            windows=[],
            metrics={},
            detector_outputs=DetectorResults(),
            scores=ScorePackage(
                integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
                confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
                timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
                config_hash="abc123",
            ),
            observation_summary={"total_observations": 100},
            detector_execution_metadata={"D-01": {"method": "ks"}},
            statistical_artifacts={"drift_statistics": {}},
            configuration_snapshot={"metric_list": ["M-02"]},
        )

        assert ep.observation_summary == {"total_observations": 100}
        assert ep.detector_execution_metadata == {"D-01": {"method": "ks"}}
        assert ep.statistical_artifacts == {"drift_statistics": {}}
        assert ep.configuration_snapshot == {"metric_list": ["M-02"]}

    def test_evidence_package_defaults(self):
        """Test that EvidencePackage has correct defaults."""
        ep = EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123",
                timestamp="2025-01-01T00:00:00Z",
                seed=42,
                platform="linux",
                python_version="3.10.0",
                dependency_hash="def456",
            ),
            windows=[],
            metrics={},
            detector_outputs=DetectorResults(),
            scores=ScorePackage(
                integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
                confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
                timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
                config_hash="abc123",
            ),
        )

        assert ep.observation_summary == {}
        assert ep.detector_execution_metadata == {}
        assert ep.statistical_artifacts == {}
        assert ep.configuration_snapshot == {}

    def test_get_observation_trace(self):
        """Test get_observation_trace method."""
        ep = EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123",
                timestamp="2025-01-01T00:00:00Z",
                seed=42,
                platform="linux",
                python_version="3.10.0",
                dependency_hash="def456",
            ),
            windows=[
                WindowDefinition(
                    window_id="w01",
                    start_date=datetime.date(2025, 1, 1),
                    end_date=datetime.date(2025, 1, 15),
                    commits=5,
                    strategy="time",
                )
            ],
            metrics={"M-02": {"default": [1.0, 2.0, 3.0]}},
            detector_outputs=DetectorResults(detector_outputs={"D-01": {"drift_detected": True}}),
            scores=ScorePackage(
                integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
                confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
                timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
                config_hash="abc123",
            ),
            observation_summary={"per_metric": {"M-02": {"count": 3, "window_count": 1}}},
        )

        trace = ep.get_observation_trace("M-02")
        assert trace["metric_id"] == "M-02"
        assert "windows" in trace
        assert "detectors" in trace
        assert trace["summary"] == {"count": 3, "window_count": 1}

    def test_get_observation_trace_nonexistent_metric(self):
        """Test get_observation_trace for non-existent metric."""
        ep = EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123",
                timestamp="2025-01-01T00:00:00Z",
                seed=42,
                platform="linux",
                python_version="3.10.0",
                dependency_hash="def456",
            ),
            windows=[],
            metrics={},
            detector_outputs=DetectorResults(),
            scores=ScorePackage(
                integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
                confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
                timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
                config_hash="abc123",
            ),
        )

        trace = ep.get_observation_trace("M-99")
        assert trace["metric_id"] == "M-99"
        assert trace["summary"] == {}

    def test_get_evidence_completeness(self):
        """Test get_evidence_completeness method."""
        ep = EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123",
                timestamp="2025-01-01T00:00:00Z",
                seed=42,
                platform="linux",
                python_version="3.10.0",
                dependency_hash="def456",
            ),
            windows=[
                WindowDefinition(
                    window_id="w01",
                    start_date=datetime.date(2025, 1, 1),
                    end_date=datetime.date(2025, 1, 15),
                    commits=5,
                    strategy="time",
                )
            ],
            metrics={"M-02": {"default": [1.0, 2.0]}},
            detector_outputs=DetectorResults(detector_outputs={"D-01": {"drift_detected": True}}),
            scores=ScorePackage(
                integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
                confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
                timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
                config_hash="abc123",
            ),
            observation_summary={"total_observations": 2},
            detector_execution_metadata={"D-01": {"method": "ks"}},
            statistical_artifacts={"drift_statistics": {}},
            configuration_snapshot={"metric_list": ["M-02"]},
        )

        completeness = ep.get_evidence_completeness()
        assert completeness["has_provenance"] is True
        assert completeness["has_windows"] is True
        assert completeness["has_metrics"] is True
        assert completeness["has_detector_outputs"] is True
        assert completeness["has_scores"] is True
        assert completeness["has_observation_summary"] is True
        assert completeness["has_detector_execution_metadata"] is True
        assert completeness["has_statistical_artifacts"] is True
        assert completeness["has_configuration_snapshot"] is True
        assert completeness["required_completeness"] == 1.0
        assert completeness["optional_completeness"] == 1.0
        assert completeness["overall_completeness"] == 1.0

    def test_to_dict_deterministic(self):
        """Test that to_dict() is deterministic."""
        ep = EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123",
                timestamp="2025-01-01T00:00:00Z",
                seed=42,
                platform="linux",
                python_version="3.10.0",
                dependency_hash="def456",
            ),
            windows=[
                WindowDefinition(
                    window_id="w01",
                    start_date=datetime.date(2025, 1, 1),
                    end_date=datetime.date(2025, 1, 15),
                    commits=5,
                    strategy="time",
                )
            ],
            metrics={"M-02": {"default": [1.0, 2.0]}},
            detector_outputs=DetectorResults(detector_outputs={"D-01": {"drift_detected": True}}),
            scores=ScorePackage(
                integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
                confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
                timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
                config_hash="abc123",
            ),
            observation_summary={"total_observations": 2},
            detector_execution_metadata={"D-01": {"method": "ks"}},
            statistical_artifacts={"drift_statistics": {}},
            configuration_snapshot={"metric_list": ["M-02"]},
        )

        d1 = ep.to_dict()
        d2 = ep.to_dict()
        assert d1 == d2

    def test_to_dict_includes_observation_fields(self):
        """Test that to_dict() includes observation-level fields."""
        ep = EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash="abc123",
                timestamp="2025-01-01T00:00:00Z",
                seed=42,
                platform="linux",
                python_version="3.10.0",
                dependency_hash="def456",
            ),
            windows=[],
            metrics={},
            detector_outputs=DetectorResults(),
            scores=ScorePackage(
                integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
                confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
                timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
                config_hash="abc123",
            ),
            observation_summary={"total_observations": 100},
            detector_execution_metadata={"D-01": {"method": "ks"}},
            statistical_artifacts={"drift_statistics": {}},
            configuration_snapshot={"metric_list": ["M-02"]},
        )

        d = ep.to_dict()
        assert "observation_summary" in d
        assert "detector_execution_metadata" in d
        assert "statistical_artifacts" in d
        assert "configuration_snapshot" in d
        assert d["observation_summary"] == {"total_observations": 100}
        assert d["detector_execution_metadata"] == {"D-01": {"method": "ks"}}


class TestEvidenceEngineObservationExtraction:
    """Test EvidenceEngine observation evidence extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = EvidenceEngine()
        self.repo_context = RepositoryContext(
            repo_id="test-repo",
            local_path=Path("/tmp/test"),
            is_remote=False,
            total_commits=100,
            contributor_count=5,
        )

    def test_observation_summary_extraction(self):
        """Test that observation summary is extracted correctly."""
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            metrics={
                "M-02": {"default": [10.0, 12.0, 11.0]},
                "M-06": {"default": [5.0, 8.0]},
            },
        )

        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2025, 1, 15),
                commits=5,
                strategy="time",
            ),
        ]

        detector_results = DetectorResults(detector_outputs={"D-01": {"drift_detected": False}})

        score_package = ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        )

        configuration = {
            "metric_list": ["M-02", "M-06"],
            "detector_config": {},
            "enabled_detectors": ["D-01"],
        }

        evidence = self.engine.generate(
            repository_context=self.repo_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            score_package=score_package,
            configuration=configuration,
        )

        assert evidence.observation_summary["total_observations"] == 5  # 3 + 2
        assert "M-02" in evidence.observation_summary["per_metric"]
        assert "M-06" in evidence.observation_summary["per_metric"]
        assert evidence.observation_summary["per_metric"]["M-02"]["count"] == 3
        assert evidence.observation_summary["per_metric"]["M-06"]["count"] == 2
        assert evidence.observation_summary["observation_quality"]["complete"] == 5

    def test_detector_execution_metadata_extraction(self):
        """Test that detector execution metadata is extracted correctly."""
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            metrics={"M-02": {"default": [10.0, 12.0]}},
        )

        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2025, 1, 15),
                commits=5,
                strategy="time",
            ),
        ]

        detector_results = DetectorResults(
            detector_outputs={
                "D-01": {
                    "drift_detected": False,
                    "window_pairs_analyzed": [["w01", "w02"]],
                    "observation_counts": {"M-02": 10},
                }
            }
        )

        score_package = ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        )

        configuration = {
            "metric_list": ["M-02"],
            "detector_config": {"D-01": {"alpha": 0.05}},
            "enabled_detectors": ["D-01"],
        }

        evidence = self.engine.generate(
            repository_context=self.repo_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            score_package=score_package,
            configuration=configuration,
        )

        assert "D-01" in evidence.detector_execution_metadata
        assert evidence.detector_execution_metadata["D-01"]["method"] == "kolmogorov_smirnov"
        assert evidence.detector_execution_metadata["D-01"]["windows_analyzed"] == 1
        assert evidence.detector_execution_metadata["D-01"]["observations_consumed"] == 10
        assert evidence.detector_execution_metadata["D-01"]["parameters"] == {"alpha": 0.05}

    def test_statistical_artifacts_extraction(self):
        """Test that statistical artifacts are extracted correctly."""
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            metrics={"M-02": {"default": [10.0, 12.0]}},
        )

        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2025, 1, 15),
                commits=5,
                strategy="time",
            ),
        ]

        detector_results = DetectorResults(
            detector_outputs={
                "D-01": {
                    "drift_detected": True,
                    "ks_statistics": {"M-02_w01_w02": 0.2},
                    "psi_values": {"M-02_w01_w02": 0.35},
                    "drift_events": [{"metric": "M-02"}],
                }
            }
        )

        score_package = ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        )

        configuration = {
            "metric_list": ["M-02"],
            "detector_config": {},
            "enabled_detectors": ["D-01"],
        }

        evidence = self.engine.generate(
            repository_context=self.repo_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            score_package=score_package,
            configuration=configuration,
        )

        assert "D-01" in evidence.statistical_artifacts["drift_statistics"]
        assert "ks_statistics" in evidence.statistical_artifacts["drift_statistics"]["D-01"]
        assert "psi_values" in evidence.statistical_artifacts["drift_statistics"]["D-01"]
        assert "drift_events" in evidence.statistical_artifacts["drift_statistics"]["D-01"]

    def test_configuration_snapshot_extraction(self):
        """Test that configuration snapshot is extracted correctly."""
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            metrics={"M-02": {"default": [10.0, 12.0]}},
        )

        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2025, 1, 15),
                commits=5,
                strategy="time",
            ),
        ]

        detector_results = DetectorResults(detector_outputs={"D-01": {"drift_detected": False}})

        score_package = ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        )

        configuration = {
            "metric_list": ["M-02"],
            "since": "2025-01-01",
            "until": "2025-01-31",
            "exclude_bots": True,
            "segmentation_strategy": "time",
            "segmentation_size": 14,
            "detector_config": {"D-01": {"alpha": 0.05}},
            "enabled_detectors": ["D-01"],
        }

        evidence = self.engine.generate(
            repository_context=self.repo_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            score_package=score_package,
            configuration=configuration,
        )

        assert evidence.configuration_snapshot["metric_list"] == ["M-02"]
        assert evidence.configuration_snapshot["segmentation_strategy"] == "time"
        assert evidence.configuration_snapshot["segmentation_size"] == 14
        assert evidence.configuration_snapshot["detector_config"] == {"D-01": {"alpha": 0.05}}
        assert evidence.configuration_snapshot["enabled_detectors"] == ["D-01"]
        assert evidence.configuration_snapshot["extraction_params"]["since"] == "2025-01-01"
        assert evidence.configuration_snapshot["extraction_params"]["until"] == "2025-01-31"
        assert evidence.configuration_snapshot["extraction_params"]["exclude_bots"] is True


class TestMockEvidenceEngineObservation:
    """Test MockEvidenceEngine observation evidence extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MockEvidenceEngine()
        self.repo_context = RepositoryContext(
            repo_id="test-repo",
            local_path=Path("/tmp/test"),
            is_remote=False,
            total_commits=100,
            contributor_count=5,
        )

    def test_mock_observation_summary(self):
        """Test that MockEvidenceEngine extracts observation summary."""
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            metrics={"M-02": {"default": [10.0, 12.0, 11.0]}},
        )

        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2025, 1, 15),
                commits=5,
                strategy="time",
            ),
        ]

        detector_results = DetectorResults(detector_outputs={"D-01": {"drift_detected": False}})

        score_package = ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        )

        configuration = {
            "metric_list": ["M-02"],
            "detector_config": {},
            "enabled_detectors": ["D-01"],
        }

        evidence = self.engine.generate(
            repository_context=self.repo_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            score_package=score_package,
            configuration=configuration,
        )

        assert evidence.observation_summary["total_observations"] == 3
        assert "M-02" in evidence.observation_summary["per_metric"]
        assert evidence.observation_summary["observation_quality"]["complete"] == 3

    def test_mock_detector_execution_metadata(self):
        """Test that MockEvidenceEngine extracts detector execution metadata."""
        metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run",
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            metrics={"M-02": {"default": [10.0, 12.0]}},
        )

        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2025, 1, 1),
                end_date=datetime.date(2025, 1, 15),
                commits=5,
                strategy="time",
            ),
        ]

        detector_results = DetectorResults(
            detector_outputs={
                "D-01": {
                    "drift_detected": False,
                    "window_pairs_analyzed": [["w01", "w02"]],
                    "observation_counts": {"M-02": 10},
                }
            }
        )

        score_package = ScorePackage(
            integrity=IntegrityScore(overall=0.75, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.85, factors={}, band="high"),
            timestamp=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
            config_hash="abc123",
        )

        configuration = {
            "metric_list": ["M-02"],
            "detector_config": {},
            "enabled_detectors": ["D-01"],
        }

        evidence = self.engine.generate(
            repository_context=self.repo_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            score_package=score_package,
            configuration=configuration,
        )

        assert "D-01" in evidence.detector_execution_metadata
        assert evidence.detector_execution_metadata["D-01"]["windows_analyzed"] == 1
        assert evidence.detector_execution_metadata["D-01"]["observations_consumed"] == 10
