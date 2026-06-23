#!/usr/bin/env python3
"""
Test script for AnalysisPipeline with mock components.
"""

import sys
import tempfile
from pathlib import Path

# Add the current directory to Python path to allow importing from src
sys.path.insert(0, str(Path(__file__).parent))

from miie.orchestration.pipeline import AnalysisPipeline
from miie.processing.ingestion import MockIngestionEngine
from miie.processing.extraction import MockExtractionEngine
from miie.processing.segmentation import MockSegmentationEngine
from miie.processing.detection.mock_detectors import MockDetectorEngine
from miie.processing.scoring.engine import MockScoringEngine
from miie.processing.evidence import MockEvidenceEngine
from miie.processing.explanation.engine import MockExplanationEngine
from miie.processing.reporting.engine import MockReportGenerator
from miie.processing.benchmark.engine import MockBenchmarkEngine
from miie.processing.evaluation.engine import MockEvaluationEngine


def test_analysis_pipeline_with_mocks():
    """Test AnalysisPipeline with mock components."""
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)

        # Create mock components
        ingestion_engine = MockIngestionEngine()
        extraction_engine = MockExtractionEngine()
        segmentation_engine = MockSegmentationEngine()
        detection_engine = MockDetectorEngine()
        scoring_engine = MockScoringEngine()
        evidence_engine = MockEvidenceEngine()
        explanation_engine = MockExplanationEngine()
        report_generator = MockReportGenerator()
        benchmark_engine = MockBenchmarkEngine()
        evaluation_engine = MockEvaluationEngine()

        # Create pipeline
        pipeline = AnalysisPipeline(
            ingestion_engine=ingestion_engine,
            extraction_engine=extraction_engine,
            segmentation_engine=segmentation_engine,
            detection_engine=detection_engine,
            scoring_engine=scoring_engine,
            evidence_engine=evidence_engine,
            explanation_engine=explanation_engine,
            report_generator=report_generator,
            benchmark_engine=benchmark_engine,
            evaluation_engine=evaluation_engine
        )

        # Run analysis with default parameters (as CLI would use)
        # CLI uses: metric_list=["M-02", "M-06"], seed=42, dry_run=True
        # Windowing parameters use defaults: strategy="fixed", size=100, custom_boundaries=None
        report_output = pipeline.run_analysis(
            repo_path="dummy_repo_path",  # Not used by mock ingestion
            metric_list=["M-02", "M-06"],
            output_dir=output_dir,
            seed=42,
            dry_run=True
        )

        # Verify that we got a ReportOutput without errors
        assert report_output is not None, "ReportOutput should not be None"
        # Check that the output directory contains expected files (at least the manifest)
        # Since we are using dry_run=True, the mock report generator should have generated files.
        # We can check that the output directory is not empty.
        assert any(output_dir.iterdir()), "Output directory should not be empty"

        print("Test passed: AnalysisPipeline ran successfully with mock components.")
        print(f"Generated files in {output_dir}:")
        for file in sorted(output_dir.iterdir()):
            print(f"  - {file.name}")


if __name__ == "__main__":
    test_analysis_pipeline_with_mocks()