#!/usr/bin/env python3
"""
Reproducibility test for MIIE v1.0 reporting component.
Tests that identical inputs produce identical outputs.
"""

import sys
import os
import json
import hashlib
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from miie.processing.reporting.engine import MockReportGenerator
import tempfile
from pathlib import Path


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
    """Run reproducibility test for reporting."""
    print("=" * 60)
    print("MIIE v1.0 Reproducibility Verification (Reporting)")
    print("=" * 60)

    try:
        test_mock_reporting_reproducibility()

        print("=" * 60)
        print("PASS: REPORTING REPRODUCIBILITY TEST PASSED")
        print("PASS: MockReportGenerator produces deterministic outputs")
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