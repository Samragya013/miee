"""Explanation Engine Implementation.

Implements the IExplanationEngine interface for generating explanation reports.
"""

from typing import Optional

from miie.contracts.interfaces import IExplanationEngine
from miie.schemas.models import EvidencePackage, ExplanationReport, ScorePackage


class ExplanationEngine(IExplanationEngine):
    """Explanation Engine implementation that generates explanation reports."""

    def generate(
        self,
        evidence_package: EvidencePackage,
        score_package: ScorePackage,
        metric_filter: Optional[str] = None,
        detector_filter: Optional[str] = None,
    ) -> ExplanationReport:
        """Generate explanation report from evidence and scores.

        Args:
            evidence_package: Container for traceable evidence
            score_package: Container for integrity and confidence scores
            metric_filter: Specific metric ID to explain (None for all)
            detector_filter: Specific detector ID to explain (None for all)

        Returns:
            ExplanationReport: Container for explanation narratives and recommendations
        """
        narratives = []
        recommendations = []

        # Generate integrity explanation
        if isinstance(score_package.integrity, dict):
            integrity_overall = score_package.integrity.get("overall", 0.0)
        else:
            integrity_overall = getattr(score_package.integrity, "overall", 0.0)
        if integrity_overall >= 0.8:
            narratives.append(
                f"Integrity score is high ({integrity_overall:.2f}), indicating strong data consistency and reliability."
            )
        elif integrity_overall >= 0.5:
            narratives.append(
                f"Integrity score is moderate ({integrity_overall:.2f}), suggesting acceptable data quality with some inconsistencies."
            )
        else:
            narratives.append(
                f"Integrity score is low ({integrity_overall:.2f}), indicating potential data quality issues or anomalies."
            )

        # Generate confidence explanation
        if isinstance(score_package.confidence, dict):
            confidence_overall = score_package.confidence.get("overall", 0.0)
            confidence_factors = score_package.confidence.get("factors", {})
        else:
            confidence_overall = getattr(score_package.confidence, "overall", 0.0)
            confidence_factors = getattr(score_package.confidence, "factors", {})

        if confidence_overall >= 0.8:
            narratives.append(
                f"Confidence score is high ({confidence_overall:.2f}), indicating reliable assessment based on sufficient data quality and coverage."
            )
        elif confidence_overall >= 0.5:
            narratives.append(
                f"Confidence score is moderate ({confidence_overall:.2f}), suggesting reasonable assessment but could benefit from more data."
            )
        else:
            narratives.append(
                f"Confidence score is low ({confidence_overall:.2f}), indicating limited data quality, sample size, or temporal coverage."
            )

        # Add factor-specific explanations
        # TFS §7.5 factors: sample_size, variance, missing_data, window_balance, detector_success
        sample_size = confidence_factors.get("sample_size", 0.0)
        missing_data = confidence_factors.get("missing_data", 0.0)
        window_balance = confidence_factors.get("window_balance", 0.0)

        if sample_size < 0.5:
            narratives.append(
                f"Sample size factor is low ({sample_size:.2f}), indicating limited number of analysis windows."
            )
            recommendations.append(
                "Consider increasing analysis window count or adjusting window segmentation parameters."
            )

        if missing_data < 0.5:
            narratives.append(
                f"Missing data factor is low ({missing_data:.2f}), indicating missing or invalid data in metric-window pairs."
            )
            recommendations.append("Investigate data ingestion and extraction processes to improve data completeness.")

        if window_balance < 0.5:
            narratives.append(f"Window balance factor is low ({window_balance:.2f}), indicating uneven window sizes.")
            recommendations.append("Consider adjusting window size for more balanced analysis windows.")

        # Add evidence-based insights if available
        if hasattr(evidence_package, "windows") and evidence_package.windows:
            narratives.append(f"Analysis performed across {len(evidence_package.windows)} temporal windows.")

        if hasattr(evidence_package, "detector_outputs") and evidence_package.detector_outputs:
            detector_outputs = evidence_package.detector_outputs
            if isinstance(detector_outputs, dict):
                detector_list = list(detector_outputs.keys())
            else:
                detector_list = (
                    list(detector_outputs.detector_outputs.keys())
                    if hasattr(detector_outputs, "detector_outputs")
                    else []
                )
            detector_count = len(detector_list)
            narratives.append(
                f"Results based on outputs from {detector_count} detectors: {', '.join(detector_list[:3])}{'...' if detector_count > 3 else ''}."
            )

        # Add metric-specific insights if metric_filter is provided
        if metric_filter and hasattr(evidence_package, "metrics"):
            metrics = evidence_package.metrics
            if isinstance(metrics, dict) and metric_filter in metrics:
                metric_data = metrics[metric_filter]
                if isinstance(metric_data, dict):
                    data_points = sum(len(v) for v in metric_data.values() if v is not None)
                else:
                    data_points = 1
                narratives.append(f"Metric {metric_filter} has {data_points} data points across analysis windows.")
            elif isinstance(metrics, list) and metric_filter in metrics:
                narratives.append(f"Metric {metric_filter} is included in the analysis.")

        # Add detector-specific insights if detector_filter is provided
        if detector_filter and hasattr(evidence_package, "detector_outputs"):
            det_out = evidence_package.detector_outputs
            if isinstance(det_out, dict):
                det_dict = det_out
            else:
                det_dict = getattr(det_out, "detector_outputs", {})
            if detector_filter in det_dict:
                det_output = det_dict[detector_filter]
                narratives.append(
                    f"Detector {detector_filter} output: {list(det_output.keys())[:5]}{'...' if len(det_output) > 5 else ''}."
                )

        # Default recommendations if none were generated
        if not recommendations:
            if integrity_overall < 0.7 or confidence_overall < 0.7:
                recommendations.append("Review data quality and consider additional validation steps.")
                recommendations.append("Consider running analysis with different detector configurations.")
            else:
                recommendations.append("Analysis results appear reliable. Consider periodic re-validation.")
                recommendations.append("Monitor trends over time for early detection of changes.")

        return ExplanationReport(narratives=narratives, recommendations=recommendations)


class MockExplanationEngine(IExplanationEngine):
    """Mock explanation engine that returns deterministic explanations."""

    def generate(
        self,
        evidence_package: EvidencePackage,
        score_package: ScorePackage,
        metric_filter: Optional[str] = None,
        detector_filter: Optional[str] = None,
    ) -> ExplanationReport:
        """Generate mock explanation report.

        Returns deterministic explanations for testing purposes.
        """
        # Return fixed explanations that match expected test structure
        return ExplanationReport(
            narratives=[
                "Integrity score indicates moderate data consistency.",
                "Confidence score reflects reasonable data quality and coverage.",
                "Analysis performed across 2 temporal windows.",
                "Results based on outputs from 3 detectors: D-01, D-02, D-03.",
            ],
            recommendations=[
                "Consider increasing analysis window count for better statistical significance.",
                "Review data ingestion processes to improve data completeness.",
                "Monitor trends over time for early detection of changes.",
            ],
        )
