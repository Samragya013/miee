"""
Integration tests for evidence generation.
Tests the complete pipeline from detection through scoring to evidence generation.
"""

import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

import pytest

from src.miie.processing.evidence import MockEvidenceEngine
from src.miie.processing.scoring import MockScoringEngine
from src.miie.processing.detection.mock_detectors import (
    MockDistributionDriftDetector,
    MockCorrelationBreakdownDetector,
    MockThresholdCompressionDetector
)
from src.miie.processing.detection.registry import DetectorRegistry
from src.miie.processing.detection.dispatcher import DetectorDispatcherEngine
from src.miie.processing.detection.runner import DetectorRunner
from src.miie.processing.extraction import MetricExtractionEngine
from src.miie.schemas.models import (
    MetricDataFrame,
    WindowDefinition,
    DetectorResults,
    ScorePackage,
    IntegrityScore,
    ConfidenceScore,
    EvidencePackage,
    RepositoryContext,
    Provenance
)


class TestEvidenceIntegration:
    """Test cases for evidence generation integration."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create detector framework components
        self.registry = DetectorRegistry()
        self.dispatcher = DetectorDispatcherEngine(self.registry)
        self.runner = DetectorRunner(self.registry)

        # Create and register mock detectors
        self.dist_drift_detector = MockDistributionDriftDetector()
        self.correlation_detector = MockCorrelationBreakdownDetector()
        self.threshold_detector = MockThresholdCompressionDetector()

        self.registry.register(self.dist_drift_detector)
        self.registry.register(self.correlation_detector)
        self.registry.register(self.threshold_detector)

        # Create scoring and evidence engines
        self.scoring_engine = MockScoringEngine()
        self.evidence_engine = MockEvidenceEngine()

        # Create extraction engine
        self.extraction_engine = MetricExtractionEngine()

    def test_detection_to_scoring_to_evidence_flow(self):
        """Test flow: detection -> scoring -> evidence generation."""
        # Create extracted metrics (simulating Day 7 output)
        extracted_metrics = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-integration",
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            metrics={
                "M-02": {"default": [8.0, 9.0, 7.0, 6.0, 10.0]},  # Commit Frequency
                "M-06": {"default": [3.0, 4.0, 2.0, 5.0, 3.0]}   # Code Churn
            }
        )

        # Verify extraction output
        assert "M-02" in extracted_metrics.metrics
        assert "M-06" in extracted_metrics.metrics

        # Create windows for analysis
        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2026, 6, 1),
                end_date=datetime.date(2026, 6, 5),
                commits=3,
                strategy="fixed_size"
            ),
            WindowDefinition(
                window_id="w02",
                start_date=datetime.date(2026, 6, 6),
                end_date=datetime.date(2026, 6, 10),
                commits=2,
                strategy="fixed_size"
            )
        ]

        # Process through detector framework (dispatcher)
        detection_results = self.dispatcher.invoke(
            metric_dataframe=extracted_metrics,
            windows=windows
        )

        # Verify detection results
        assert isinstance(detection_results.detector_outputs, dict)
        assert len(detection_results.detector_outputs) == 3
        assert "D-01" in detection_results.detector_outputs
        assert "D-02" in detection_results.detector_outputs
        assert "D-03" in detection_results.detector_outputs

        # Process through scoring engine
        score_package = self.scoring_engine.compute_integrity_score(
            detector_results=detection_results,
            metric_dataframe=extracted_metrics,
            windows=windows
        )

        # Verify scoring results
        assert isinstance(score_package, ScorePackage)
        assert "integrity" in score_package.__dict__
        assert "confidence" in score_package.__dict__
        assert 0.0 <= score_package.integrity.overall <= 1.0
        assert 0.0 <= score_package.confidence.overall <= 1.0

        # Create repository context
        repository_context = RepositoryContext(
            repo_id="test-repo",
            local_path=Path("/tmp/test-repo"),
            is_remote=False,
            total_commits=50,
            contributor_count=3
        )

        # Process through evidence engine
        evidence_package = self.evidence_engine.generate(
            repository_context=repository_context,
            metric_dataframe=extracted_metrics,
            windows=windows,
            detector_results=detection_results,
            score_package=score_package,
            configuration={"seed": 42}
        )

        # Verify evidence results
        assert isinstance(evidence_package, EvidencePackage)
        assert evidence_package.provenance is not None
        assert len(evidence_package.detector_outputs.detector_outputs) == 3
        assert len(evidence_package.metrics) == 2
        assert len(evidence_package.windows) == 2

        # Verify traceability
        assert "D-01" in evidence_package.detector_outputs.detector_outputs
        assert "D-02" in evidence_package.detector_outputs.detector_outputs
        assert "D-03" in evidence_package.detector_outputs.detector_outputs
        assert "M-02" in evidence_package.metrics
        assert "M-06" in evidence_package.metrics
        assert "w01" in [w.window_id for w in evidence_package.windows]
        assert "w02" in [w.window_id for w in evidence_package.windows]

        # Verify scores are properly linked through
        assert evidence_package.scores.integrity.overall == score_package.integrity.overall
        assert evidence_package.scores.confidence.overall == score_package.confidence.overall

    def test_evidence_generation_with_empty_detection_results(self):
        """Test evidence generation with empty detection results."""
        # Create extracted metrics
        extracted_metrics = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-empty-detection",
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            metrics={
                "M-02": {"default": [5.0, 6.0, 4.0]}
            }
        )

        # Create empty windows
        windows = []

        # Create empty detector results
        empty_detector_results = DetectorResults(detector_outputs={})

        # Create score package (would normally come from scoring engine)
        score_package = ScorePackage(
            integrity=IntegrityScore(
                overall=0.5,
                per_metric={"M-02": 0.5},
                formula_version="1.0.0"
            ),
            confidence=ConfidenceScore(
                overall=0.5,
                factors={"sample_size": 0.5},
                band="medium"
            ),
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            config_hash="test-hash",
            formula_version="TFS_v1.0"
        )

        # Create repository context
        repository_context = RepositoryContext(
            repo_id="test-repo",
            local_path=Path("/tmp/test-repo"),
            is_remote=False,
            total_commits=10,
            contributor_count=1
        )

        # Generate evidence with empty detection results
        evidence_package = self.evidence_engine.generate(
            repository_context=repository_context,
            metric_dataframe=extracted_metrics,
            windows=windows,
            detector_results=empty_detector_results,
            score_package=score_package,
            configuration={"seed": 99}
        )

        # Should still produce valid evidence package
        assert isinstance(evidence_package, EvidencePackage)
        assert len(evidence_package.detector_outputs.detector_outputs) == 0
        assert len(evidence_package.metrics) == 1
        assert len(evidence_package.windows) == 0
        assert "M-02" in evidence_package.metrics

    def test_deterministic_evidence_generation_in_pipeline(self):
        """Test that evidence generation is deterministic when inputs are identical."""
        # Create identical metric dataframes
        metrics_data = {
            "M-02": {"default": [10.0, 11.0, 9.0]},
            "M-06": {"default": [5.0, 6.0, 4.0]}
        }

        metric_df1 = MetricDataFrame(
            repo_id="det-repo",
            run_id="run-001",
            timestamp=datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc),
            metrics=metrics_data.copy()
        )

        metric_df2 = MetricDataFrame(
            repo_id="det-repo",
            run_id="run-002",  # Different run ID
            timestamp=datetime.datetime(2026, 1, 1, 12, 0, 1, tzinfo=datetime.timezone.utc),  # Different timestamp
            metrics=metrics_data.copy()
        )

        # Create identical windows
        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2026, 1, 1),
                end_date=datetime.date(2026, 1, 10),
                commits=5,
                strategy="fixed_size"
            )
        ]

        # Run detection on both
        runner_results1 = self.runner.run_all(metric_df1)
        runner_results2 = self.runner.run_all(metric_df2)

        # Wrap runner results in DetectorResults (runner returns List[DetectorResult])
        detection_results1 = DetectorResults(
            detector_outputs={list(r.detector_outputs.keys())[0]: list(r.detector_outputs.values())[0]
                              for r in runner_results1}
        )
        detection_results2 = DetectorResults(
            detector_outputs={list(r.detector_outputs.keys())[0]: list(r.detector_outputs.values())[0]
                              for r in runner_results2}
        )

        # Create score packages (using mock scoring for deterministic results)
        score_package1 = self.scoring_engine.compute_integrity_score(
            detector_results=detection_results1,
            metric_dataframe=metric_df1,
            windows=windows
        )

        score_package2 = self.scoring_engine.compute_integrity_score(
            detector_results=detection_results2,
            metric_dataframe=metric_df2,
            windows=windows
        )

        # Create repository context
        repository_context = RepositoryContext(
            repo_id="test-repo",
            local_path=Path("/tmp/test-repo"),
            is_remote=False,
            total_commits=20,
            contributor_count=2
        )

        # Generate evidence for both
        evidence_package1 = self.evidence_engine.generate(
            repository_context=repository_context,
            metric_dataframe=metric_df1,
            windows=windows,
            detector_results=detection_results1,
            score_package=score_package1,
            configuration={"seed": 777}
        )

        evidence_package2 = self.evidence_engine.generate(
            repository_context=repository_context,
            metric_dataframe=metric_df2,
            windows=windows,
            detector_results=detection_results2,
            score_package=score_package2,
            configuration={"seed": 777}
        )

        # Evidence should be structurally identical (same detector IDs and output structure)
        assert len(evidence_package1.detector_outputs.detector_outputs) == len(evidence_package2.detector_outputs.detector_outputs)
        assert len(evidence_package1.metrics) == len(evidence_package2.metrics)
        assert len(evidence_package1.windows) == len(evidence_package2.windows)

        # With mock engines and same seeds, core IDs should match
        assert "D-01" in evidence_package1.detector_outputs.detector_outputs
        assert "D-01" in evidence_package2.detector_outputs.detector_outputs

    def test_evidence_package_validation_integration(self):
        """Test that generated evidence packages pass schema validation."""
        # Create test data
        extracted_metrics = MetricDataFrame(
            repo_id="validation-test",
            run_id="validation-run-001",
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            metrics={
                "M-01": {"default": [100.0, 110.0, 90.0]},  # Lines of Code
                "M-03": {"default": [50.0, 45.0, 55.0]}     # Issue Count
            }
        )

        windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2026, 6, 1),
                end_date=datetime.date(2026, 6, 15),
                commits=10,
                strategy="fixed_size"
            )
        ]

        # Get detection results
        detection_results = self.dispatcher.invoke(
            metric_dataframe=extracted_metrics,
            windows=windows
        )

        # Get score package
        score_package = self.scoring_engine.compute_integrity_score(
            detector_results=detection_results,
            metric_dataframe=extracted_metrics,
            windows=windows
        )

        # Create repository context
        repository_context = RepositoryContext(
            repo_id="validation-test",
            local_path=Path("/tmp/validation-repo"),
            is_remote=False,
            total_commits=100,
            contributor_count=5
        )

        # Generate evidence
        evidence_package = self.evidence_engine.generate(
            repository_context=repository_context,
            metric_dataframe=extracted_metrics,
            windows=windows,
            detector_results=detection_results,
            score_package=score_package,
            configuration={"seed": 12345}
        )

        # The evidence package should be valid (no exceptions thrown during construction)
        # Accessing various attributes should not raise validation errors
        assert evidence_package.provenance is not None
        assert isinstance(evidence_package.detector_outputs.detector_outputs, dict)
        assert isinstance(evidence_package.metrics, dict)
        assert isinstance(evidence_package.windows, list)
        assert isinstance(evidence_package.provenance, Provenance)

        # Verify provenance has required fields
        assert evidence_package.provenance.miie_version is not None
        assert evidence_package.provenance.config_hash is not None
        assert evidence_package.provenance.timestamp is not None
        assert evidence_package.provenance.seed is not None

        # Verify scores structure
        assert isinstance(evidence_package.scores, ScorePackage)
        assert isinstance(evidence_package.scores.integrity, IntegrityScore)
        assert isinstance(evidence_package.scores.confidence, ConfidenceScore)
        assert 0.0 <= evidence_package.scores.integrity.overall <= 1.0
        assert 0.0 <= evidence_package.scores.confidence.overall <= 1.0

    def test_evidence_engine_handles_missing_attributes_gracefully(self):
        """Test that evidence engine handles objects with missing attributes gracefully."""
        # Create metric dataframe without metrics attribute (edge case)
        class IncompleteMetricDataFrame:
            def __init__(self):
                self.repo_id = "test"
                self.run_id = "test-run"
                self.timestamp = datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc)
                # Intentionally not setting metrics attribute

        incomplete_metric_df = IncompleteMetricDataFrame()

        # Create minimal detector results
        minimal_detector_results = DetectorResults(detector_outputs={"D-01": {}})

        # Create minimal score package
        minimal_score_package = ScorePackage(
            integrity=IntegrityScore(
                overall=0.5,
                per_metric={},
                formula_version="1.0.0"
            ),
            confidence=ConfidenceScore(
                overall=0.5,
                factors={},
                band="medium"
            ),
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            config_hash="test",
            formula_version="TFS_v1.0"
        )

        # Create repository context
        repository_context = RepositoryContext(
            repo_id="test-repo",
            local_path=Path("/tmp/test-repo"),
            is_remote=False,
            total_commits=10,
            contributor_count=1
        )

        # Create empty windows
        empty_windows = []

        # This should not crash - evidence engine should handle missing attributes gracefully
        evidence_package = self.evidence_engine.generate(
            repository_context=repository_context,
            metric_dataframe=incomplete_metric_df,
            windows=empty_windows,
            detector_results=minimal_detector_results,
            score_package=minimal_score_package,
            configuration={"seed": 999}
        )

        # Should still produce valid evidence package
        assert isinstance(evidence_package, EvidencePackage)
        assert len(evidence_package.metrics) == 0  # Should handle missing metrics
        assert len(evidence_package.windows) == 0
        assert len(evidence_package.detector_outputs.detector_outputs) == 1


if __name__ == "__main__":
    pytest.main([__file__])