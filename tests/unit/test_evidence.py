"""
Unit tests for EvidenceEngine.
"""

import datetime
from typing import List, Dict, Any
from pathlib import Path

import pytest

from miie.processing.evidence import EvidenceEngine, MockEvidenceEngine
from miie.schemas.models import (
    RepositoryContext,
    MetricDataFrame,
    WindowDefinition,
    DetectorResults,
    ScorePackage,
    EvidencePackage,
    Provenance,
    IntegrityScore,
    ConfidenceScore,
    WarningItem
)


class TestEvidenceEngine:
    """Test cases for EvidenceEngine."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.evidence_engine = EvidenceEngine()
        self.mock_evidence_engine = MockEvidenceEngine()

        # Create test data
        self.repository_context = RepositoryContext(
            repo_id="test-repo",
            local_path=Path("/tmp/test-repo"),
            is_remote=False,
            total_commits=100,
            contributor_count=5
        )

        self.metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-123",
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            metrics={
                "M-02": {"default": [10.0, 12.0, 11.0, 9.0, 13.0]},  # Commit Frequency
                "M-06": {"default": [5.0, 8.0, 6.0, 4.0, 7.0]}      # Code Churn
            }
        )

        self.windows = [
            WindowDefinition(
                window_id="w01",
                start_date=datetime.date(2026, 6, 1),
                end_date=datetime.date(2026, 6, 10),
                commits=5,
                strategy="time",
                size_config={"size": 10}
            ),
            WindowDefinition(
                window_id="w02",
                start_date=datetime.date(2026, 6, 11),
                end_date=datetime.date(2026, 6, 20),
                commits=8,
                strategy="time",
                size_config={"size": 10}
            )
        ]

        self.detector_results = DetectorResults(
            detector_outputs={
                "D-01": {"drift_detected": True, "drift_magnitude": 0.5},
                "D-02": {"correlation_breakdown": True, "correlation_change": 0.3},
                "D-03": {"threshold_compressed": False, "compression_ratio": 1.0}
            }
        )

        self.score_package = ScorePackage(
            integrity=IntegrityScore(
                overall=0.75,
                per_metric={
                    "M-02": 0.80,
                    "M-06": 0.70
                },
                formula_version="TFS_v1.0"
            ),
            confidence=ConfidenceScore(
                overall=0.85,
                factors={
                    "sample_size": 0.9,
                    "variance": 0.8,
                    "missing_data": 0.7,
                    "window_balance": 0.9,
                    "detector_success": 0.95
                },
                band="high"
            ),
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            config_hash="test-config-hash",
            formula_version="TFS_v1.0"
        )

        self.configuration = {
            "seed": 42,
            "config_hash": "test-config-hash",
            "platform": "test",
            "python_version": "3.9.0",
            "dependency_hash": "test-dep-hash"
        }

    def test_evidence_engine_generate_returns_evidence_package(self):
        """Test that EvidenceEngine.generate returns a valid EvidencePackage."""
        evidence_package = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        assert isinstance(evidence_package, EvidencePackage)
        assert isinstance(evidence_package.provenance, Provenance)
        assert evidence_package.windows == self.windows
        assert evidence_package.metrics == self.metric_dataframe.metrics
        assert evidence_package.detector_outputs == self.detector_results
        assert evidence_package.scores == self.score_package
        assert evidence_package.warnings == []

    def test_mock_evidence_engine_returns_deterministic_evidence_package(self):
        """Test that MockEvidenceEngine returns deterministic EvidencePackage."""
        evidence_package1 = self.mock_evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        evidence_package2 = self.mock_evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        # Should be identical due to deterministic mock
        assert evidence_package1.provenance == evidence_package2.provenance
        assert evidence_package1.windows == evidence_package2.windows
        assert evidence_package1.metrics == evidence_package2.metrics

    def test_evidence_engine_traceability_links(self):
        """Test that evidence package maintains traceability links."""
        evidence_package = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        # Check that detector results IDs are captured
        assert "D-01" in evidence_package.detector_outputs.detector_outputs
        assert "D-02" in evidence_package.detector_outputs.detector_outputs
        assert "D-03" in evidence_package.detector_outputs.detector_outputs

        # Check that metric IDs are captured
        assert "M-02" in evidence_package.metrics
        assert "M-06" in evidence_package.metrics

        # Check that window IDs are captured
        assert "w01" in [w.window_id for w in evidence_package.windows]
        assert "w02" in [w.window_id for w in evidence_package.windows]

        # Check that scores are properly linked
        assert evidence_package.scores.integrity.overall == 0.75
        assert evidence_package.scores.confidence.overall == 0.85

    def test_evidence_engine_handles_empty_inputs(self):
        """Test that EvidenceEngine handles empty inputs gracefully."""
        empty_metric_dataframe = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-empty",
            timestamp=datetime.datetime(2026, 6, 17, tzinfo=datetime.timezone.utc),
            metrics={}
        )

        empty_detector_results = DetectorResults(detector_outputs={})

        evidence_package = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=empty_metric_dataframe,
            windows=[],  # Empty windows
            detector_results=empty_detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        assert isinstance(evidence_package, EvidencePackage)
        assert len(evidence_package.metrics) == 0
        assert len(evidence_package.detector_outputs.detector_outputs) == 0
        assert len(evidence_package.windows) == 0

    def test_evidence_engine_provenance_fields(self):
        """Test that evidence package contains all required provenance fields."""
        evidence_package = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        required_provenance = {
            "miie_version", "config_hash", "timestamp", "seed",
            "platform", "python_version", "dependency_hash"
        }

        prov = evidence_package.provenance
        assert all(hasattr(prov, key) for key in required_provenance)
        assert prov.miie_version == "1.0.0"
        assert prov.config_hash == "test-config-hash"
        assert isinstance(prov.seed, int)
        assert prov.platform == "test"
        assert prov.python_version == "3.9.0"
        assert prov.dependency_hash == "test-dep-hash"

    def test_evidence_engine_provenance_contains_seed(self):
        """Test that provenance contains the configured seed."""
        evidence_package = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        assert evidence_package.provenance.seed == self.configuration["seed"]

    def test_evidence_engine_warnings_initialization(self):
        """Test that warnings list is properly initialized."""
        evidence_package = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=self.configuration
        )

        assert isinstance(evidence_package.warnings, list)
        assert len(evidence_package.warnings) == 0  # Should be empty by default

    def test_evidence_engine_with_different_seeds(self):
        """Test that different seeds produce different evidence IDs."""
        config1 = self.configuration.copy()
        config1["seed"] = 42

        config2 = self.configuration.copy()
        config2["seed"] = 123

        evidence_package1 = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=config1
        )

        evidence_package2 = self.evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=config2
        )

        # Different seeds should produce different evidence packages
        assert evidence_package1 is not evidence_package2
        assert evidence_package1.provenance.seed == 42
        assert evidence_package2.provenance.seed == 123

    def test_evidence_engine_mock_deterministic_with_seed(self):
        """Test that MockEvidenceEngine is deterministic with same seed."""
        config1 = self.configuration.copy()
        config1["seed"] = 999

        config2 = self.configuration.copy()
        config2["seed"] = 999

        evidence_package1 = self.mock_evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=config1
        )

        evidence_package2 = self.mock_evidence_engine.generate(
            repository_context=self.repository_context,
            metric_dataframe=self.metric_dataframe,
            windows=self.windows,
            detector_results=self.detector_results,
            score_package=self.score_package,
            configuration=config2
        )

        # Same seed should produce identical evidence packages
        assert evidence_package1.provenance == evidence_package2.provenance
        assert evidence_package1.windows == evidence_package2.windows
        assert evidence_package1.metrics == evidence_package2.metrics


if __name__ == "__main__":
    pytest.main([__file__])