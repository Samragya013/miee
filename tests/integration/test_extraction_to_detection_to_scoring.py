"""Integration tests for extraction to detection to scoring flow.

Tests the complete pipeline from MetricDataFrame through detector framework to scoring.
"""
import pytest
from miie.processing.extraction import MetricExtractionEngine
from miie.processing.detection.registry import DetectorRegistry
from miie.processing.detection.dispatcher import DetectorDispatcherEngine
from miie.processing.detection.runner import DetectorRunner
from miie.processing.detection.mock_detectors import (
    MockDistributionDriftDetector,
    MockCorrelationBreakdownDetector,
    MockThresholdCompressionDetector
)
from miie.processing.scoring.engine import ScoringEngine
from miie.processing.scoring.mock_scoring import MockScoringEngine
from miie.schemas.models import MetricDataFrame
import datetime


class TestExtractionToDetectionToScoringFlow:
    """Test cases for extraction to detection to scoring integration."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create extraction engine (Day 7 component)
        self.extraction_engine = MetricExtractionEngine()

        # Create detector framework components (Day 8 components)
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

        # Create scoring engine (Day 9 component)
        self.scoring_engine = ScoringEngine()
        self.mock_scoring_engine = MockScoringEngine()

    def test_extraction_to_detection_to_scoring_flow(self):
        """Test flow: extraction -> detector framework -> scoring."""
        # Extract metrics (simulating Day 7 functionality)
        # Create a metric dataframe that simulates what extraction would produce
        extracted_metrics = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-123",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-02": {"default": [10.0, 12.0, 11.0, 9.0, 13.0]},  # Commit Frequency
                "M-06": {"default": [5.0, 8.0, 6.0, 4.0, 7.0]}       # Code Churn
                # Note: M-01, M-03, M-04, M-05, M-07 would be None per missing data policy
            }
        )

        # Verify we have the expected metrics from extraction
        assert "M-02" in extracted_metrics.metrics
        assert "M-06" in extracted_metrics.metrics

        # Process through detector framework (dispatcher) - Day 8
        detection_results = self.dispatcher.invoke(metric_dataframe=extracted_metrics, windows=[])

        # Verify detection results
        assert isinstance(detection_results.detector_outputs, dict)
        assert len(detection_results.detector_outputs) == 3
        assert "D-01" in detection_results.detector_outputs
        assert "D-02" in detection_results.detector_outputs
        assert "D-03" in detection_results.detector_outputs

        # Process through scoring engine - Day 9
        # For this test, we need to create window definitions
        # In a real pipeline, these would come from segmentation engine
        windows = [
            # Simple window covering the entire time range
            # In practice, segmentation would create multiple windows
        ]

        # Use the actual scoring engine
        score_package = self.scoring_engine.compute_integrity_score(
            detector_results=detection_results,
            metric_dataframe=extracted_metrics,
            windows=windows  # Empty windows for simplicity in this test
        )

        # Verify scoring results
        assert isinstance(score_package, dict) or hasattr(score_package, 'integrity')

        # If it's a ScorePackage object
        if hasattr(score_package, 'integrity'):
            integrity = score_package.integrity
            confidence = score_package.confidence

            # Check integrity structure
            assert "overall" in integrity
            assert "per_metric" in integrity
            assert isinstance(integrity["overall"], (int, float))
            assert 0.0 <= integrity["overall"] <= 1.0

            # Check confidence structure
            assert "overall" in confidence
            assert "factors" in confidence
            assert isinstance(confidence["overall"], (int, float))
            assert 0.0 <= confidence["overall"] <= 1.0
            assert isinstance(confidence["factors"], dict)

        # If it's a dict (older format)
        else:
            assert "integrity" in score_package
            assert "confidence" in score_package
            integrity = score_package["integrity"]
            confidence = score_package["confidence"]

            assert "overall" in integrity
            assert "per_metric" in integrity
            assert "overall" in confidence
            assert "factors" in confidence

    def test_extraction_to_detection_to_scoring_with_mock_scoring(self):
        """Test flow using mock scoring engine for predictable results."""
        # Extract metrics
        extracted_metrics = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-456",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={
                "M-02": {"default": [8.0, 9.0, 7.0]},  # Commit Frequency
                "M-06": {"default": [3.0, 4.0, 2.0]}   # Code Churn
            }
        )

        # Process through detector framework
        detection_results = self.dispatcher.invoke(metric_dataframe=extracted_metrics, windows=[])

        # Process through MOCK scoring engine (for predictable test results)
        windows = []  # Simplified for test

        score_package = self.mock_scoring_engine.compute_integrity_score(
            detector_results=detection_results,
            metric_dataframe=extracted_metrics,
            windows=windows
        )

        # Verify we get the expected mock scores
        if hasattr(score_package, 'integrity'):
            integrity = score_package.integrity
            confidence = score_package.confidence

            # These are the exact values returned by MockScoringEngine
            assert integrity.overall == 0.75
            assert integrity.per_metric["M-02"] == 0.80
            assert confidence.overall == 0.85
            assert confidence.factors["sample_size"] == 0.9
            assert confidence.factors["variance"] == 0.8
        else:
            assert score_package["integrity"]["overall"] == 0.75
            assert score_package["integrity"]["per_metric"]["M-02"] == 0.80
            assert score_package["confidence"]["overall"] == 0.85
            assert score_package["confidence"]["factors"]["sample_size"] == 0.9
            assert score_package["confidence"]["factors"]["variance"] == 0.8

    def test_empty_inputs_handling(self):
        """Test handling of empty or minimal inputs."""
        # Create minimal inputs
        extracted_metrics = MetricDataFrame(
            repo_id="test-repo",
            run_id="test-run-789",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            metrics={}  # No metrics
        )

        # Process through detector framework (will still produce outputs from mock detectors)
        detection_results = self.dispatcher.invoke(metric_dataframe=extracted_metrics, windows=[])

        # Process through scoring
        windows = []
        score_package = self.scoring_engine.compute_integrity_score(
            detector_results=detection_results,
            metric_dataframe=extracted_metrics,
            windows=windows
        )

        # Should still produce valid ScorePackage structure
        assert hasattr(score_package, 'integrity') or isinstance(score_package, dict)
        if hasattr(score_package, 'integrity'):
            assert hasattr(score_package, 'confidence')
            assert isinstance(score_package.integrity, dict)
            assert isinstance(score_package.confidence, dict)
            assert "overall" in score_package.integrity
            assert "overall" in score_package.confidence