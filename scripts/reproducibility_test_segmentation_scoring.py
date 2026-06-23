#!/usr/bin/env python3
"""
Reproducibility test for MIIE v1.0 segmentation and scoring components.
Tests that identical inputs produce identical outputs.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from src.miie.processing.segmentation import MockSegmentationEngine
from src.miie.processing.scoring.engine import ScoringEngine
from src.miie.processing.scoring.mock_scoring import MockScoringEngine
from src.miie.schemas.models import (
    RepositoryContext, MetricDataFrame, WindowDefinition,
    DetectorResults, ScorePackage, EvidencePackage
)
import datetime
from pathlib import Path


def test_mock_segmentation_reproducibility():
    """Test that MockSegmentationEngine produces deterministic outputs."""
    print("Testing MockSegmentationEngine reproducibility...")

    engine = MockSegmentationEngine()

    # Create test input
    mdf = MetricDataFrame(
        repo_id="test_repo",
        run_id="test_run",
        timestamp="2023-06-15T10:30:00Z",
        metrics={'M-02': {'w01': [10.0, 12.0, 15.0]}}
    )

    # Run multiple times with same inputs
    result1 = engine.segment(mdf, "time", 7)
    result2 = engine.segment(mdf, "time", 7)

    # Compare results
    assert len(result1) == len(result2)
    for w1, w2 in zip(result1, result2):
        assert w1.id == w2.id
        assert w1.start_date == w2.start_date
        assert w1.end_date == w2.end_date
        assert w1.commit_count == w2.commit_count
        assert w1.strategy == w2.strategy
        assert w1.size_config == w2.size_config

    print("PASS: MockSegmentationEngine is reproducible")
    return True


def test_mock_scoring_reproducibility():
    """Test that MockScoringEngine produces deterministic outputs."""
    print("Testing MockScoringEngine reproducibility...")

    engine = MockScoringEngine()

    # Create test input
    detector_results = DetectorResults(detector_outputs={"D-01": {}, "D-02": {}, "D-03": {}})
    mdf = MetricDataFrame(
        repo_id="test",
        run_id="test_run",
        timestamp="2023-06-15T10:30:00Z",
        metrics={"M-02": {"w01": [1.0, 2.0, 3.0]}}
    )
    windows = [
        WindowDefinition(
            id="w00",
            start_date=datetime.date(2020, 1, 1),
            end_date=datetime.date(2020, 1, 31),
            commit_count=1
        )
    ]

    # Run multiple times with same inputs
    result1 = engine.compute_integrity_score(detector_results, mdf, windows)
    result2 = engine.compute_integrity_score(detector_results, mdf, windows)

    # Compare results
    assert result1.integrity["overall"] == result2.integrity["overall"]
    assert result1.confidence["overall"] == result2.confidence["overall"]
    assert result1.integrity["per_metric"] == result2.integrity["per_metric"]
    assert result1.confidence["factors"] == result2.confidence["factors"]

    print("PASS: MockScoringEngine is reproducible")
    return True


def main():
    """Run reproducibility tests for segmentation and scoring."""
    print("=" * 60)
    print("MIIE v1.0 Reproducibility Verification (Segmentation & Scoring)")
    print("=" * 60)

    try:
        test_mock_segmentation_reproducibility()
        test_mock_scoring_reproducibility()

        print("=" * 60)
        print("PASS: SEGMENTATION AND SCORING REPRODUCIBILITY TESTS PASSED")
        print("PASS: Mock components produce deterministic outputs")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"FAIL: REPRODUCIBILITY TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)