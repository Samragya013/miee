#!/usr/bin/env python3
"""
Reproducibility test for MIIE v1.0 components.
Tests that identical inputs produce identical outputs.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from miie.processing.segmentation import MockSegmentationEngine
from miie.processing.scoring.engine import ScoringEngine
from miie.processing.scoring.mock_scoring import MockScoringEngine
from miie.processing.evidence import MockEvidenceEngine
from miie.processing.reporting.engine import MockReportGenerator
from miie.schemas.models import (
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


def test_mock_evidence_reproducibility():
    """Test that MockEvidenceEngine produces deterministic outputs."""
    print("Testing MockEvidenceEngine reproducibility...")

    engine = MockEvidenceEngine()

    # Create test input
    repo_context = RepositoryContext(
        repo_id="test-repo",
        local_path=str(Path("/tmp/test-repo")),
        is_remote=False,
        total_commits=100,
        contributor_count=5,
        first_commit_date=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        last_commit_date=datetime.datetime(2023, 6, 15, tzinfo=datetime.timezone.utc),
        is_shallow=False,
        is_fork=False
    )

    mdf = MetricDataFrame(
        repo_id='test-repo',
        run_id='test-run-123',
        timestamp='2023-06-15T10:30:00Z',
        metrics={
            'M-02': {'default': [10.0, 12.0, 11.0, 9.0, 13.0]},
            'M-06': {'default': [5.0, 8.0, 6.0, 4.0, 7.0]}
        }
    )

    windows = [
        WindowDefinition(
            id='w01',
            start_date=datetime.date(2023, 6, 1),
            end_date=datetime.date(2023, 6, 10),
            commit_count=5
        ),
        WindowDefinition(
            id='w02',
            start_date=datetime.date(2023, 6, 11),
            end_date=datetime.date(2023, 6, 20),
            commit_count=8
        )
    ]

    detector_results = DetectorResults(
        detector_outputs={
            'D-01': {'drift_detected': True, 'drift_magnitude': 0.5},
            'D-02': {'correlation_breakdown': True, 'correlation_change': 0.3},
            'D-03': {'threshold_compressed': False, 'compression_ratio': 1.0}
        }
    )

    score_package = ScorePackage(
        integrity={
            'overall': 0.75,
            'per_metric': {
                'M-02': 0.80,
                'M-06': 0.70
            }
        },
        confidence={
            'overall': 0.85,
            'factors': {
                'sample_size': 0.9,
                'variance': 0.8,
                'missing_data': 0.7,
                'window_balance': 0.9,
                'detector_success': 0.95
            }
        },
        timestamp=datetime.datetime(2023, 6, 15, 10, 30, 0, tzinfo=datetime.timezone.utc),
        config_hash='test-config-hash',
        formula_version='TFS_v1.0'
    )

    configuration = {
        'seed': 42,
        'config_hash': 'test-config-hash',
        'platform': 'test',
        'python_version': '3.9.0',
        'dependency_hash': 'test-dep-hash'
    }

    # Run multiple times with same inputs
    result1 = engine.generate(repo_context, mdf, windows, detector_results, score_package, configuration)
    result2 = engine.generate(repo_context, mdf, windows, detector_results, score_package, configuration)

    # Compare results
    assert result1.evidence_id == result2.evidence_id
    assert result1.provenance["timestamp"] == result2.provenance["timestamp"]
    assert result1.score_package_id == result2.score_package_id
    assert result1.detector_results_ids == result2.detector_results_ids
    assert result1.metrics_used == result2.metrics_used
    assert result1.windows_analyzed == result2.windows_analyzed
    assert result1.provenance == result2.provenance
    assert result1.das_notation == result2.das_notation

    print("PASS: MockEvidenceEngine is reproducible")
    return True


def test_mock_reporting_reproducibility():
    """Test that MockReportGenerator produces deterministic outputs."""
    print("Testing MockReportGenerator reproducibility...")

    engine = MockReportGenerator()

    # Create test input
    analysis_result = {
        "integrity_score": 0.85,
        "confidence_score": 0.92,
        "metrics_processed": 5,
        "detectors_used": ["D-01", "D-02", "D-03"]
    }
    output_formats = ["json"]

    # Create temporary directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)

        # Run multiple times with same inputs
        result1 = engine.generate(analysis_result, output_formats, output_dir)
        output_dir2 = Path(temp_dir) / "output2"
        output_dir2.mkdir()
        result2 = engine.generate(analysis_result, output_formats, output_dir2)

        # Compare the generated files
        json_file1 = result1.file_paths["json"]
        json_file2 = result2.file_paths["json"]

        assert json_file1.exists() and json_file2.exists()

        # Read and compare file contents
        with open(json_file1, 'r') as f1, open(json_file2, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()
            assert content1 == content2, "Generated JSON files should be identical"

        # Compare manifest files
        manifest1 = result1.manifest_path
        manifest2 = result2.manifest_path
        assert manifest1.exists() and manifest2.exists()

        with open(manifest1, 'r') as f1, open(manifest2, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()
            assert content1 == content2, "Generated manifests should be identical"

    print("PASS: MockReportGenerator is reproducible")
    return True


def main():
    """Run all reproducibility tests."""
    print("=" * 60)
    print("MIIE v1.0 Reproducibility Verification")
    print("=" * 60)

    try:
        test_mock_segmentation_reproducibility()
        test_mock_scoring_reproducibility()
        test_mock_evidence_reproducibility()
        test_mock_reporting_reproducibility()

        print("=" * 60)
        print("PASS: ALL REPRODUCIBILITY TESTS PASSED")
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