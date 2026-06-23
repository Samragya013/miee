"""Mock Explanation Implementations for Testing.

Provides deterministic mock explanation engines for testing purposes.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.miie.schemas.models import EvidencePackage, ExplanationReport, ScorePackage
from src.miie.contracts.interfaces import IExplanationEngine


class MockExplanationEngine(IExplanationEngine):
    """Mock explanation engine that returns deterministic explanations."""

    def generate(self, evidence_package: EvidencePackage,
                 score_package: ScorePackage,
                 metric_filter: Optional[str] = None,
                 detector_filter: Optional[str] = None) -> ExplanationReport:
        """Generate mock explanation report.

        Returns deterministic explanations for testing purposes.
        """
        # Return fixed explanations that match expected test structure
        return ExplanationReport(
            narratives=[
                "Integrity score indicates moderate data consistency.",
                "Confidence score reflects reasonable data quality and coverage.",
                "Analysis performed across 2 temporal windows.",
                "Results based on outputs from 3 detectors: D-01, D-02, D-03."
            ],
            recommendations=[
                "Consider increasing analysis window count for better statistical significance.",
                "Review data ingestion processes to improve data completeness.",
                "Monitor trends over time for early detection of changes."
            ]
        )


class MockZeroExplanationEngine(IExplanationEngine):
    """Mock explanation engine that returns minimal explanations."""

    def generate(self, evidence_package: EvidencePackage,
                 score_package: ScorePackage,
                 metric_filter: Optional[str] = None,
                 detector_filter: Optional[str] = None) -> ExplanationReport:
        """Generate minimal explanation report."""
        return ExplanationReport(
            narratives=["Basic analysis completed."],
            recommendations=["No specific recommendations at this time."]
        )


class MockDetailedExplanationEngine(IExplanationEngine):
    """Mock explanation engine that returns detailed explanations."""

    def generate(self, evidence_package: EvidencePackage,
                 score_package: ScorePackage,
                 metric_filter: Optional[str] = None,
                 detector_filter: Optional[str] = None) -> ExplanationReport:
        """Generate detailed explanation report."""
        integrity = score_package.integrity
        confidence = score_package.confidence
        if isinstance(integrity, dict):
            int_overall = integrity.get('overall', 0.0)
            int_per_metric = integrity.get('per_metric', {})
        else:
            int_overall = getattr(integrity, 'overall', 0.0)
            int_per_metric = getattr(integrity, 'per_metric', {})
        if isinstance(confidence, dict):
            conf_overall = confidence.get('overall', 0.0)
            conf_factors = confidence.get('factors', {})
        else:
            conf_overall = getattr(confidence, 'overall', 0.0)
            conf_factors = getattr(confidence, 'factors', {})
        det_outputs = getattr(evidence_package, 'detector_outputs', {})
        if isinstance(det_outputs, dict):
            det_count = len(det_outputs)
        else:
            det_count = len(getattr(det_outputs, 'detector_outputs', {}))
        metrics = getattr(evidence_package, 'metrics', {})
        if isinstance(metrics, dict):
            metrics_keys = list(metrics.keys())
        else:
            metrics_keys = list(metrics) if isinstance(metrics, list) else []
        return ExplanationReport(
            narratives=[
                f"Integrity overall score: {int_overall:.3f}",
                f"Confidence overall score: {conf_overall:.3f}",
                f"Per-metric integrity scores: {int_per_metric}",
                f"Confidence factors: {conf_factors}",
                f"Evidence package contains {len(getattr(evidence_package, 'windows', []))} windows",
                f"Evidence package contains {det_count} detector outputs",
                f"Metrics available: {metrics_keys}",
                "Temporal analysis shows stable trends across all windows",
                "Detector consensus indicates reliable anomaly detection",
                "Data quality assessment complete for all metric-window pairs"
            ],
            recommendations=[
                "Increase sampling frequency for better temporal resolution",
                "Consider ensemble methods for improved detector accuracy",
                "Implement real-time monitoring for immediate anomaly detection",
                "Schedule weekly validation reports for trend analysis",
                "Cross-validate results with external data sources when available",
                "Set up alert thresholds based on historical score patterns",
                "Document analysis parameters for reproducibility",
                "Consider multi-resolution analysis for scale-invariant features"
            ]
        )