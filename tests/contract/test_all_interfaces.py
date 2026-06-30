"""
Contract Tests: All 12 Protocol Interfaces
Verifies that every ACS v1.0 Protocol interface (INT-01..INT-18 subset)
has the required methods with correct signatures.

Implements: CT-01..CT-17 (contract test coverage for interface definitions)
"""

import inspect
from typing import Protocol

import pytest

from miie.contracts.interfaces import (
    IBenchmarkEngine,
    IDataExporter,
    IDatasetGenerator,
    IDetectorEngine,
    IEvaluationEngine,
    IEvidenceEngine,
    IExplanationEngine,
    IExtractionEngine,
    IIngestionEngine,
    IReportGenerator,
    IScoringEngine,
    ISegmentationEngine,
)

# ---------------------------------------------------------------------------
# Protocol → required methods mapping (from ACS §3 INT definitions)
# ---------------------------------------------------------------------------
PROTOCOL_METHODS: dict[type, dict[str, list[str]]] = {
    IIngestionEngine: {
        "ingest": ["repo_path", "cache_dir", "keep_cache", "shallow_depth"],
        "validate": ["context"],
    },
    IExtractionEngine: {
        "extract": ["context", "metric_list", "since", "until", "exclude_bots"],
    },
    ISegmentationEngine: {
        "segment": ["metric_dataframe", "strategy", "size", "custom_boundaries"],
    },
    IDetectorEngine: {
        "invoke": [
            "metric_dataframe",
            "windows",
            "detector_config",
            "enabled_detectors",
        ],
    },
    IScoringEngine: {
        "compute_integrity_score": [
            "detector_results",
            "metric_dataframe",
            "windows",
            "detector_weights",
        ],
    },
    IEvidenceEngine: {
        "generate": [
            "repository_context",
            "metric_dataframe",
            "windows",
            "detector_results",
            "score_package",
            "configuration",
        ],
    },
    IExplanationEngine: {
        "generate": [
            "evidence_package",
            "score_package",
            "metric_filter",
            "detector_filter",
        ],
    },
    IBenchmarkEngine: {
        "execute": ["suite_id", "detector_ids", "config", "seed"],
    },
    IEvaluationEngine: {
        "evaluate": ["benchmark_run", "ground_truth"],
    },
    IReportGenerator: {
        "generate": ["analysis_result", "output_formats", "output_dir"],
    },
    IDataExporter: {
        "export": ["data", "formats", "output_dir"],
    },
    IDatasetGenerator: {
        "generate": ["dataset_type", "count", "output_dir", "seed"],
    },
}

ALL_PROTOCOLS = list(PROTOCOL_METHODS.keys())

# ---------------------------------------------------------------------------
# Tests: existence & structure
# ---------------------------------------------------------------------------


class TestProtocolExistence:
    """CT-GEN: All 12 Protocol interfaces must be defined and importable."""

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS, ids=lambda p: p.__name__)
    def test_protocol_is_not_none(self, protocol):
        assert protocol is not None

    def test_total_protocol_count(self):
        assert len(ALL_PROTOCOLS) == 12, f"Expected 12 ACS protocols, got {len(ALL_PROTOCOLS)}"

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS, ids=lambda p: p.__name__)
    def test_protocol_inherits_from_protocol(self, protocol):
        assert issubclass(protocol, Protocol), f"{protocol.__name__} must inherit from typing.Protocol"

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS, ids=lambda p: p.__name__)
    def test_protocol_is_runtime_checkable(self, protocol):
        assert (
            getattr(protocol, "_is_runtime_protocol", False) is True
        ), f"{protocol.__name__} must be decorated with @runtime_checkable"


class TestProtocolMethods:
    """CT-GEN: Every Protocol must expose the required methods."""

    @pytest.mark.parametrize(
        "protocol, expected_methods",
        PROTOCOL_METHODS.items(),
    )
    def test_methods_exist(self, protocol, expected_methods):
        for method_name in expected_methods:
            assert hasattr(protocol, method_name), f"{protocol.__name__} missing method: {method_name}"
            method = getattr(protocol, method_name)
            assert callable(method), f"{protocol.__name__}.{method_name} must be callable"

    @pytest.mark.parametrize(
        "protocol, expected_methods",
        PROTOCOL_METHODS.items(),
    )
    def test_method_parameter_names(self, protocol, expected_methods):
        """Each method must accept the expected parameter names."""
        for method_name, param_names in expected_methods.items():
            method = getattr(protocol, method_name)
            sig = inspect.signature(method)
            actual_params = list(sig.parameters.keys())
            for pname in param_names:
                assert pname in actual_params, (
                    f"{protocol.__name__}.{method_name} missing parameter: {pname}; " f"found: {actual_params}"
                )


class TestProtocolReturnTypes:
    """CT-GEN: Every Protocol method must have a return-type annotation."""

    @pytest.mark.parametrize(
        "protocol",
        ALL_PROTOCOLS,
        ids=lambda p: p.__name__,
    )
    def test_methods_have_return_annotation(self, protocol):
        for method_name in PROTOCOL_METHODS[protocol]:
            method = getattr(protocol, method_name)
            sig = inspect.signature(method)
            assert (
                sig.return_annotation is not inspect.Parameter.empty
            ), f"{protocol.__name__}.{method_name} must have a return type annotation"


class TestProtocolNamesMatchACS:
    """CT-GEN: Protocol class names must match ACS INT definitions."""

    EXPECTED_NAMES = {
        IIngestionEngine: "IIngestionEngine",
        IExtractionEngine: "IExtractionEngine",
        ISegmentationEngine: "ISegmentationEngine",
        IDetectorEngine: "IDetectorEngine",
        IScoringEngine: "IScoringEngine",
        IEvidenceEngine: "IEvidenceEngine",
        IExplanationEngine: "IExplanationEngine",
        IBenchmarkEngine: "IBenchmarkEngine",
        IEvaluationEngine: "IEvaluationEngine",
        IReportGenerator: "IReportGenerator",
        IDataExporter: "IDataExporter",
        IDatasetGenerator: "IDatasetGenerator",
    }

    @pytest.mark.parametrize(
        "protocol, expected_name",
        EXPECTED_NAMES.items(),
    )
    def test_name_matches(self, protocol, expected_name):
        assert protocol.__name__ == expected_name


class TestMockImplementations:
    """CT-GEN: Every Protocol must be implementable without error."""

    def test_ingestion_engine(self):
        class Impl:
            def ingest(self, repo_path, cache_dir=None, keep_cache=False, shallow_depth=None):
                pass

            def validate(self, context):
                return True

        assert isinstance(Impl(), IIngestionEngine)

    def test_extraction_engine(self):
        class Impl:
            def extract(
                self,
                context,
                metric_list,
                since=None,
                until=None,
                exclude_bots=False,
                windows=None,
            ):
                pass

        assert isinstance(Impl(), IExtractionEngine)

    def test_segmentation_engine(self):
        class Impl:
            def segment(self, metric_dataframe, strategy, size, custom_boundaries=None):
                return []

        assert isinstance(Impl(), ISegmentationEngine)

    def test_detector_engine(self):
        class Impl:
            def invoke(
                self,
                metric_dataframe,
                windows,
                detector_config=None,
                enabled_detectors=None,
            ):
                pass

        assert isinstance(Impl(), IDetectorEngine)

    def test_scoring_engine(self):
        class Impl:
            def compute_integrity_score(self, detector_results, metric_dataframe, windows, detector_weights=None):
                pass

        assert isinstance(Impl(), IScoringEngine)

    def test_evidence_engine(self):
        class Impl:
            def generate(
                self,
                repository_context,
                metric_dataframe,
                windows,
                detector_results,
                score_package,
                configuration,
            ):
                pass

            def generate_observation_evidence(
                self,
                repository_context,
                metric_dataframe,
                windows,
                detector_results,
                configuration,
            ):
                pass

        assert isinstance(Impl(), IEvidenceEngine)

    def test_explanation_engine(self):
        class Impl:
            def generate(
                self,
                evidence_package,
                score_package,
                metric_filter=None,
                detector_filter=None,
            ):
                pass

        assert isinstance(Impl(), IExplanationEngine)

    def test_benchmark_engine(self):
        class Impl:
            def execute(self, suite_id, detector_ids, config, seed=42):
                pass

        assert isinstance(Impl(), IBenchmarkEngine)

    def test_evaluation_engine(self):
        class Impl:
            def evaluate(self, benchmark_run, ground_truth):
                pass

        assert isinstance(Impl(), IEvaluationEngine)

    def test_report_generator(self):
        class Impl:
            def generate(self, analysis_result, output_formats, output_dir):
                pass

        assert isinstance(Impl(), IReportGenerator)

    def test_data_exporter(self):
        class Impl:
            def export(self, data, formats, output_dir):
                return {}

        assert isinstance(Impl(), IDataExporter)

    def test_dataset_generator(self):
        class Impl:
            def generate(self, dataset_type, count, output_dir, seed=None):
                return []

        assert isinstance(Impl(), IDatasetGenerator)
