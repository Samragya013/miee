"""Mock Scoring Implementations for Testing.

Provides deterministic mock scoring engines for testing purposes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from miie.schemas.models import ScorePackage, DetectorResults, MetricDataFrame, WindowDefinition, IntegrityScore, ConfidenceScore
from miie.contracts.interfaces import IScoringEngine


class MockScoringEngine(IScoringEngine):
    """Mock scoring engine that returns deterministic scores."""

    def compute_integrity_score(self, detector_results: DetectorResults,
                                metric_dataframe: MetricDataFrame,
                                windows: List[WindowDefinition],
                                detector_weights: Optional[Dict[str, float]] = None) -> ScorePackage:
        """Compute mock integrity and confidence scores.

        Returns deterministic scores for testing purposes.
        """
        # Return fixed scores that match the expected structure from evidence package tests
        return ScorePackage(
            integrity=IntegrityScore(
                overall=0.75,
                per_metric={
                    "M-02": 0.80
                },
                formula_version="1.0.0"
            ),
            confidence=ConfidenceScore(
                overall=0.85,
                factors={
                    "sample_size": 0.9,
                    "variance": 0.8,
                    "missing_data": 0.9,
                    "window_balance": 0.85,
                    "detector_success": 0.95
                },
                band="medium"
            ),
            timestamp=datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
            config_hash="mock-config-hash",
            formula_version="TFS_v1.0"
        )


class MockZeroScoringEngine(IScoringEngine):
    """Mock scoring engine that returns zero scores."""

    def compute_integrity_score(self, detector_results: DetectorResults,
                                metric_dataframe: MetricDataFrame,
                                windows: List[WindowDefinition],
                                detector_weights: Optional[Dict[str, float]] = None) -> ScorePackage:
        """Compute zero integrity and confidence scores."""
        return ScorePackage(
            integrity=IntegrityScore(
                overall=0.0,
                per_metric={},
                formula_version="1.0.0"
            ),
            confidence=ConfidenceScore(
                overall=0.0,
                factors={
                    "sample_size": 0.0,
                    "variance": 0.0,
                    "missing_data": 0.0,
                    "window_balance": 0.0,
                    "detector_success": 0.0
                },
                band="low"
            ),
            timestamp=datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
            config_hash="mock-config-hash",
            formula_version="TFS_v1.0"
        )


class MockPerfectScoringEngine(IScoringEngine):
    """Mock scoring engine that returns perfect scores."""

    def compute_integrity_score(self, detector_results: DetectorResults,
                                metric_dataframe: MetricDataFrame,
                                windows: List[WindowDefinition],
                                detector_weights: Optional[Dict[str, float]] = None) -> ScorePackage:
        """Compute perfect integrity and confidence scores."""
        # Get all metrics from metric_dataframe
        per_metric = {}
        for metric_id in metric_dataframe.metrics:
            per_metric[metric_id] = 1.0

        # Get all possible factors
        factors = {
            "sample_size": 1.0,
            "variance": 1.0,
            "missing_data": 1.0,
            "window_balance": 1.0,
            "detector_success": 1.0
        }

        return ScorePackage(
            integrity=IntegrityScore(
                overall=1.0,
                per_metric=per_metric,
                formula_version="1.0.0"
            ),
            confidence=ConfidenceScore(
                overall=1.0,
                factors=factors,
                band="high"
            ),
            timestamp=datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
            config_hash="mock-config-hash",
            formula_version="TFS_v1.0"
        )