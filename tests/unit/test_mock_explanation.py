"""Unit tests for mock explanation engines."""

import datetime

from miie.processing.explanation.mock_explanation import (
    MockDetailedExplanationEngine,
    MockExplanationEngine,
    MockZeroExplanationEngine,
)
from miie.schemas.models import (
    ConfidenceScore,
    DetectorResults,
    EvidencePackage,
    IntegrityScore,
    Provenance,
    ScorePackage,
    WindowDefinition,
)


def create_test_evidence_package():
    """Create a test evidence package."""
    window = WindowDefinition(
        window_id="w01",
        start_date=datetime.datetime(2026, 1, 1),
        end_date=datetime.datetime(2026, 1, 31),
        commits=10,
        strategy="fixed_size",
    )

    return EvidencePackage(
        provenance=Provenance(
            miie_version="1.0.0",
            config_hash="test-config-hash",
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            seed=42,
            platform="test-platform",
            python_version="3.9.0",
            dependency_hash="test-dep-hash",
        ),
        windows=[window],
        metrics=["M-01", "M-02"],
        detector_outputs=DetectorResults(
            detector_outputs={
                "D-01": {"anomaly_score": 0.3},
                "D-02": {"drift_detected": False},
                "D-03": {"correlation_breakdown": True},
            }
        ),
        scores=ScorePackage(
            integrity=IntegrityScore(
                overall=0.75,
                per_metric={"M-01": 0.80, "M-02": 0.70},
                formula_version="1.0.0",
            ),
            confidence=ConfidenceScore(
                overall=0.85,
                factors={
                    "sample_size": 0.9,
                    "data_quality": 0.8,
                    "temporal_coverage": 0.85,
                },
                band="medium",
            ),
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
            config_hash="test",
        ),
    )


def create_test_score_package():
    """Create a test score package."""
    return ScorePackage(
        integrity=IntegrityScore(
            overall=0.75,
            per_metric={"M-01": 0.80, "M-02": 0.70},
            formula_version="1.0.0",
        ),
        confidence=ConfidenceScore(
            overall=0.85,
            factors={
                "sample_size": 0.9,
                "data_quality": 0.8,
                "temporal_coverage": 0.85,
            },
            band="medium",
        ),
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        config_hash="test",
    )


def test_mock_explanation_engine_returns_expected_structure():
    """Test that MockExplanationEngine returns expected ExplanationReport structure."""
    engine = MockExplanationEngine()
    evidence = create_test_evidence_package()
    scores = create_test_score_package()

    report = engine.generate(evidence, scores)

    assert report is not None
    assert hasattr(report, "narratives")
    assert hasattr(report, "recommendations")
    assert isinstance(report.narratives, list)
    assert isinstance(report.recommendations, list)
    assert len(report.narratives) == 4
    assert len(report.recommendations) == 3
    assert "Integrity score indicates moderate data consistency." in report.narratives
    assert "Consider increasing analysis window count for better statistical significance." in report.recommendations


def test_mock_zero_explanation_engine_returns_minimal_explanation():
    """Test that MockZeroExplanationEngine returns minimal explanations."""
    engine = MockZeroExplanationEngine()
    evidence = create_test_evidence_package()
    scores = create_test_score_package()

    report = engine.generate(evidence, scores)

    assert report is not None
    assert len(report.narratives) == 1
    assert len(report.recommendations) == 1
    assert report.narratives[0] == "Basic analysis completed."
    assert report.recommendations[0] == "No specific recommendations at this time."


def test_mock_detailed_explanation_engine_returns_detailed_explanation():
    """Test that MockDetailedExplanationEngine returns detailed explanations."""
    engine = MockDetailedExplanationEngine()
    evidence = create_test_evidence_package()
    scores = create_test_score_package()

    report = engine.generate(evidence, scores)

    assert report is not None
    assert len(report.narratives) >= 8
    assert len(report.recommendations) >= 8

    # Check that narratives contain score information
    narratives_text = " ".join(report.narratives)
    assert "Integrity overall score:" in narratives_text
    assert "Confidence overall score:" in narratives_text
    assert "Per-metric integrity scores:" in narratives_text
    assert "Confidence factors:" in narratives_text

    # Check that recommendations contain detailed advice
    recommendations_text = " ".join(report.recommendations)
    assert "Increase sampling frequency" in recommendations_text
    assert "Consider ensemble methods" in recommendations_text
    assert "Implement real-time monitoring" in recommendations_text


def test_mock_explanation_engines_respect_filters():
    """Test that mock explanation engines accept filter parameters."""
    engine = MockExplanationEngine()
    evidence = create_test_evidence_package()
    scores = create_test_score_package()

    # Test with metric filter
    report = engine.generate(evidence, scores, metric_filter="M-01")
    assert report is not None

    # Test with detector filter
    report = engine.generate(evidence, scores, detector_filter="D-01")
    assert report is not None

    # Test with both filters
    report = engine.generate(evidence, scores, metric_filter="M-01", detector_filter="D-01")
    assert report is not None
