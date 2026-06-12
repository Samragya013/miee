"""
Contract Layer DTO Tests
Tests for Data Transfer Objects in the contracts layer.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from miie.contracts.dataclasses import (
    IngestionInputDTO,
    ExtractionInputDTO,
    SegmentationInputDTO,
    DetectionInputDTO,
    D01InputDTO,
    D01OutputDTO,
    D02InputDTO,
    D02OutputDTO,
    D03InputDTO,
    D03OutputDTO,
    ScoringInputDTO,
    EvidenceInputDTO,
    ExplanationInputDTO,
    BenchmarkInputDTO,
    EvaluationInputDTO,
    ReportInputDTO,
    IngestionOutputDTO,
    AnalyzeOutputDTO,
    DetectOutputDTO,
    BenchmarkOutputDTO,
    EvaluateOutputDTO,
    ExplainOutputDTO,
    ExportOutputDTO,
    GenerateOutputDTO,
    CLIErrorInfo
)
from miie.contracts.errors import ValidationError, IngestionError


def test_ingestion_input_dto():
    """Test IngestionInputDTO creation and fields."""
    dto = IngestionInputDTO(
        repo_path="/path/to/repo",
        cache_dir=Path("/tmp/cache"),
        keep_cache=True,
        shallow_depth=5
    )

    assert dto.repo_path == "/path/to/repo"
    assert dto.cache_dir == Path("/tmp/cache")
    assert dto.keep_cache is True
    assert dto.shallow_depth == 5


def test_extraction_input_dto():
    """Test ExtractionInputDTO creation and fields."""
    # Create a minimal RepositoryContext for testing
    from miie.schemas.models import RepositoryContext
    repo_context = RepositoryContext(
        repo_id="test-repo",
        local_path=Path("/path/to/repo"),
        is_remote=True,
        remote_url="https://github.com/test/repo.git",
        total_commits=100,
        contributor_count=10,
        language_distribution={"Python": 1000}
    )

    # Capture datetime values to avoid timing issues in assertions
    since_dt = datetime.now() - timedelta(days=30)
    until_dt = datetime.now()

    dto = ExtractionInputDTO(
        repository_context=repo_context,
        metric_list=["M-01", "M-02"],
        since=since_dt,
        until=until_dt,
        exclude_bots=True
    )

    assert dto.repository_context == repo_context
    assert dto.metric_list == ["M-01", "M-02"]
    assert dto.since == since_dt
    assert dto.until == until_dt
    assert dto.exclude_bots is True


def test_segmentation_input_dto():
    """Test SegmentationInputDTO creation and fields."""
    from miie.schemas.models import MetricDataFrame, WindowDefinition
    import pandas as pd

    # Create minimal MetricDataFrame for testing
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)]
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict
    )

    dto = SegmentationInputDTO(
        metric_dataframe=metric_df,
        strategy="time",
        size=7
    )

    assert dto.metric_dataframe == metric_df
    assert dto.strategy == "time"
    assert dto.size == 7
    assert dto.custom_boundaries is None


def test_d01_dto_creation():
    """Test D-01 DTO creation."""
    input_dto = D01InputDTO(
        metric_values_window_a=[1.0, 2.0, 3.0, 4.0, 5.0],
        metric_values_window_b=[2.0, 3.0, 4.0, 5.0, 6.0],
        metric_id="M-01",
        window_pair=("w01", "w02")
    )

    assert input_dto.metric_values_window_a == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert input_dto.metric_values_window_b == [2.0, 3.0, 4.0, 5.0, 6.0]
    assert input_dto.metric_id == "M-01"
    assert input_dto.window_pair == ("w01", "w02")

    output_dto = D01OutputDTO(
        detected=True,
        ks_statistic=0.8,
        ks_p_value=0.01,
        psi_value=0.3,
        direction="mean_shift",
        severity=0.8,
        mean_shift=1.0,
        variance_ratio=1.2,
        sample_sizes=[5, 5],
        metric_id="M-01",
        window_pair=["w01", "w02"]
    )

    assert output_dto.detected is True
    assert output_dto.ks_statistic == 0.8
    assert output_dto.ks_p_value == 0.01
    assert output_dto.psi_value == 0.3
    assert output_dto.direction == "mean_shift"
    assert output_dto.severity == 0.8


def test_cli_error_info():
    """Test CLIErrorInfo creation."""
    error_info = CLIErrorInfo(
        error_code="INVALID-REPO",
        message="Repository path does not exist",
        suggestion="Provide a valid repository path"
    )

    assert error_info.error_code == "INVALID-REPO"
    assert error_info.message == "Repository path does not exist"
    assert error_info.suggestion == "Provide a valid repository path"


def test_imports_work():
    """Test that all contract modules can be imported."""
    # This test passes if we reach this point without ImportError
    from miie.contracts import dataclasses, validators, errors, interfaces
    assert dataclasses is not None
    assert validators is not None
    assert errors is not None
    assert interfaces is not None