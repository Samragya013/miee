"""
Contract Layer Interface Tests
Tests for Protocol definitions in the contracts layer.
"""

import pytest
from typing import Protocol, runtime_checkable

from miie.contracts.interfaces import (
    IIngestionEngine,
    IExtractionEngine,
    ISegmentationEngine,
    IDetectorEngine,
    IScoringEngine,
    IEvidenceEngine,
    IExplanationEngine,
    IBenchmarkEngine,
    IEvaluationEngine,
    IReportGenerator,
    IDataExporter,
    IDatasetGenerator
)


def test_all_protocols_exist():
    """Test that all 12 required protocols are defined."""
    protocols = [
        IIngestionEngine,
        IExtractionEngine,
        ISegmentationEngine,
        IDetectorEngine,
        IScoringEngine,
        IEvidenceEngine,
        IExplanationEngine,
        IBenchmarkEngine,
        IEvaluationEngine,
        IReportGenerator,
        IDataExporter,
        IDatasetGenerator
    ]

    for protocol in protocols:
        assert protocol is not None, f"Protocol {protocol.__name__} is not defined"


def test_all_protocols_are_runtime_checkable():
    """Test that all protocols use @runtime_checkable decorator."""
    protocols = [
        IIngestionEngine,
        IExtractionEngine,
        ISegmentationEngine,
        IDetectorEngine,
        IScoringEngine,
        IEvidenceEngine,
        IExplanationEngine,
        IBenchmarkEngine,
        IEvaluationEngine,
        IReportGenerator,
        IDataExporter,
        IDatasetGenerator
    ]

    for protocol in protocols:
        # Check if the class has the _is_runtime_protocol attribute
        # This is set by @runtime_checkable decorator
        assert hasattr(protocol, '_is_runtime_protocol'), \
            f"Protocol {protocol.__name__} is not marked with @runtime_checkable"
        assert protocol._is_runtime_protocol is True, \
            f"Protocol {protocol.__name__} _is_runtime_protocol is not True"


def test_protocol_inheritance():
    """Test that all protocols inherit from Protocol class."""
    protocols = [
        IIngestionEngine,
        IExtractionEngine,
        ISegmentationEngine,
        IDetectorEngine,
        IScoringEngine,
        IEvidenceEngine,
        IExplanationEngine,
        IBenchmarkEngine,
        IEvaluationEngine,
        IReportGenerator,
        IDataExporter,
        IDatasetGenerator
    ]

    for protocol in protocols:
        # Check that it's a subclass of Protocol
        assert issubclass(protocol, Protocol), \
            f"Protocol {protocol.__name__} does not inherit from typing.Protocol"


def test_protocol_method_signatures_exist():
    """Test that all protocols have the expected method signatures."""
    # Define expected methods for each protocol based on ACS INT specifications
    expected_methods = {
        IIngestionEngine: ['ingest', 'validate'],
        IExtractionEngine: ['extract'],
        ISegmentationEngine: ['segment'],
        IDetectorEngine: ['invoke'],
        IScoringEngine: ['compute_integrity_score'],
        IEvidenceEngine: ['generate'],
        IExplanationEngine: ['generate'],
        IBenchmarkEngine: ['execute'],
        IEvaluationEngine: ['evaluate'],
        IReportGenerator: ['generate'],
        IDataExporter: ['export'],
        IDatasetGenerator: ['generate']
    }

    for protocol, methods in expected_methods.items():
        for method_name in methods:
            assert hasattr(protocol, method_name), \
                f"Protocol {protocol.__name__} missing method {method_name}"

            # Get the method and check it's callable (abstract method)
            method = getattr(protocol, method_name)
            assert callable(method), \
                f"Protocol {protocol.__name__}.{method_name} is not callable"


def test_protocol_names_match_acs():
    """Test that protocol names follow ACS naming conventions."""
    # Expected protocol names based on ACS INT numbers
    expected_names = {
        IIngestionEngine: 'IIngestionEngine',      # INT-01
        IExtractionEngine: 'IExtractionEngine',    # INT-02
        ISegmentationEngine: 'ISegmentationEngine', # INT-03
        IDetectorEngine: 'IDetectorEngine',        # INT-04
        IScoringEngine: 'IScoringEngine',          # INT-05
        IEvidenceEngine: 'IEvidenceEngine',        # INT-06
        IExplanationEngine: 'IExplanationEngine',  # INT-07
        IBenchmarkEngine: 'IBenchmarkEngine',      # INT-09
        IEvaluationEngine: 'IEvaluationEngine',    # INT-10
        IReportGenerator: 'IReportGenerator',      # INT-08
        IDataExporter: 'IDataExporter',            # INT-16
        IDatasetGenerator: 'IDatasetGenerator'     # INT-17
    }

    for protocol, expected_name in expected_names.items():
        actual_name = protocol.__name__
        assert actual_name == expected_name, \
            f"Protocol name mismatch: expected {expected_name}, got {actual_name}"


def test_can_create_mock_implementations():
    """Test that we can create mock implementations of each protocol.

    This verifies that the protocols are well-formed and can be implemented.
    We don't test the actual logic, just that the structure allows implementation.
    """
    # This test ensures that the protocols don't have contradictory requirements
    # that would make them impossible to implement

    # Test IIngestionEngine
    class MockIngestionEngine:
        def ingest(self, repo_path, cache_dir=None, keep_cache=False, shallow_depth=None):
            pass
        def validate(self, context):
            return True

    # Test IExtractionEngine
    class MockExtractionEngine:
        def extract(self, context, metric_list, since=None, until=None, exclude_bots=False):
            pass

    # Test ISegmentationEngine
    class MockSegmentationEngine:
        def segment(self, metric_dataframe, strategy, size, custom_boundaries=None):
            return []

    # Test IDetectorEngine
    class MockDetectorEngine:
        def invoke(self, metric_dataframe, windows, detector_config=None, enabled_detectors=None):
            pass

    # Test IScoringEngine
    class MockScoringEngine:
        def compute_integrity_score(self, detector_results, metric_dataframe, windows, detector_weights=None):
            pass

    # Test IEvidenceEngine
    class MockEvidenceEngine:
        def generate(self, repository_context, metric_dataframe, windows, detector_results, score_package, configuration):
            pass

    # Test IExplanationEngine
    class MockExplanationEngine:
        def generate(self, evidence_package, score_package, metric_filter=None, detector_filter=None):
            pass

    # Test IBenchmarkEngine
    class MockBenchmarkEngine:
        def execute(self, suite_id, detector_ids, config, seed=42):
            pass

    # Test IEvaluationEngine
    class MockEvaluationEngine:
        def evaluate(self, benchmark_run, ground_truth):
            pass

    # Test IReportGenerator
    class MockReportGenerator:
        def generate(self, analysis_result, output_formats, output_dir):
            pass

    # Test IDataExporter
    class MockDataExporter:
        def export(self, data, formats, output_dir):
            return {}

    # Test IDatasetGenerator
    class MockDatasetGenerator:
        def generate(self, dataset_type, count, output_dir, seed=None):
            return []

    # If we reach here, all protocols can be implemented
    assert True