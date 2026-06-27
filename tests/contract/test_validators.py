"""
Contract Layer Validator Tests
Tests for validation logic in the contracts layer.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from miie.contracts.validators import (
    ValidationError,
    validate_benchmark_inputs,
    validate_cli_analyze_inputs,
    validate_cli_ingest_inputs,
    validate_d01_input,
    validate_d02_input,
    validate_d03_input,
    validate_detection_inputs,
    validate_evaluation_inputs,
    validate_evidence_inputs,
    validate_explanation_inputs,
    validate_extraction_inputs,
    validate_report_inputs,
    validate_repository_inputs,
    validate_scoring_inputs,
    validate_segmentation_inputs,
)
from miie.schemas.models import (
    BenchmarkRun,
    ConfidenceScore,
    DetectorResults,
    EvidencePackage,
    IntegrityScore,
    MetricDataFrame,
    Provenance,
    RepositoryContext,
    ScorePackage,
    WindowDefinition,
)


def _make_score_package():
    """Create a minimal valid ScorePackage for testing."""
    return ScorePackage(
        integrity=IntegrityScore(overall=0.9, per_metric={"M-01": 0.9}, formula_version="1.0.0"),
        confidence=ConfidenceScore(overall=0.8, factors={"sample_size": 0.8}, band="high"),
        timestamp=datetime.now(tz=timezone.utc),
        config_hash="abc123",
    )


def test_validate_repository_inputs_valid_local():
    """Test validation of valid local repository path."""
    # This would normally pass if we had a real git repo
    # For testing, we'll expect it to fail because the path doesn't exist
    # but we're testing that the function is called correctly
    with pytest.raises(ValidationError):
        validate_repository_inputs("/non/existent/path")


def test_validate_repository_inputs_invalid_url():
    """Test validation of invalid URL scheme."""
    with pytest.raises(ValidationError) as exc_info:
        validate_repository_inputs("ftp://example.com/repo.git")
    assert "Repository URL scheme must be https:// or ssh://" in str(exc_info.value)


def test_validate_extraction_inputs_valid():
    """Test validation of valid extraction inputs."""
    # Create a minimal RepositoryContext for testing
    repo_context = RepositoryContext(
        repo_id="test-repo",
        local_path=Path("/path/to/repo"),
        is_remote=True,
        remote_url="https://github.com/test/repo.git",
        total_commits=100,
        contributor_count=10,
        language_distribution={"Python": 1000},
    )

    # This should not raise an exception
    validate_extraction_inputs(
        repository_context=repo_context,
        metric_list=["M-01", "M-02"],
        since=datetime.now() - timedelta(days=30),
        until=datetime.now(),
        exclude_bots=True,
    )


def test_validate_extraction_inputs_invalid_metric():
    """Test validation with invalid metric ID."""
    repo_context = RepositoryContext(
        repo_id="test-repo",
        local_path=Path("/path/to/repo"),
        is_remote=True,
        remote_url="https://github.com/test/repo.git",
        total_commits=100,
        contributor_count=10,
        language_distribution={"Python": 1000},
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_extraction_inputs(
            repository_context=repo_context,
            metric_list=["M-01", "INVALID-METRIC"],
            since=datetime.now() - timedelta(days=30),
            until=datetime.now(),
            exclude_bots=True,
        )
    assert "Invalid metric ID" in str(exc_info.value)


def test_validate_segmentation_inputs_valid():
    """Test validation of valid segmentation inputs."""
    # Create minimal MetricDataFrame for testing
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    # This should not raise an exception
    validate_segmentation_inputs(metric_dataframe=metric_df, strategy="time", size=7)


def test_validate_segmentation_inputs_invalid_strategy():
    """Test validation with invalid strategy."""
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_segmentation_inputs(metric_dataframe=metric_df, strategy="invalid-strategy", size=7)
    assert "strategy must be one of" in str(exc_info.value)


def test_validate_d01_input_valid():
    """Test validation of valid D-01 input."""
    # This should not raise an exception
    validate_d01_input(
        values_a=[1.0, 2.0, 3.0, 4.0, 5.0],
        values_b=[2.0, 3.0, 4.0, 5.0, 6.0],
        metric_id="M-01",
        window_pair=("w01", "w02"),
        config={"alpha": 0.05, "psi_threshold": 0.25},
    )


def test_validate_d01_input_invalid_alpha():
    """Test validation with invalid alpha value."""
    with pytest.raises(ValidationError) as exc_info:
        validate_d01_input(
            values_a=[1.0, 2.0, 3.0, 4.0, 5.0],
            values_b=[2.0, 3.0, 4.0, 5.0, 6.0],
            metric_id="M-01",
            window_pair=("w01", "w02"),
            config={"alpha": 0.1, "psi_threshold": 0.25},
        )
    assert "alpha must be 0.05" in str(exc_info.value)


def test_validate_d02_input_valid():
    """Test validation of valid D-02 input."""
    # This should not raise an exception
    validate_d02_input(
        values_a=[1.0, 2.0, 3.0, 4.0, 5.0],
        values_b=[2.0, 3.0, 4.0, 5.0, 6.0],
        metric_a="M-01",
        metric_b="M-02",
        window_history=[
            WindowDefinition(
                window_id="w01",
                start_date=datetime.now() - timedelta(days=14),
                end_date=datetime.now() - timedelta(days=7),
                commits=10,
                strategy="fixed_size",
            )
        ],
        config={"correlation_threshold": 0.3},
    )


def test_validate_d02_input_same_metrics():
    """Test validation with same metrics for D-02."""
    with pytest.raises(ValidationError) as exc_info:
        validate_d02_input(
            values_a=[1.0, 2.0, 3.0, 4.0, 5.0],
            values_b=[2.0, 3.0, 4.0, 5.0, 6.0],
            metric_a="M-01",
            metric_b="M-01",  # Same as metric_a
            window_history=[
                WindowDefinition(
                    window_id="w02",
                    start_date=datetime.now() - timedelta(days=14),
                    end_date=datetime.now() - timedelta(days=7),
                    commits=10,
                    strategy="fixed_size",
                )
            ],
            config={"correlation_threshold": 0.3},
        )
    assert "metric_a and metric_b must be different" in str(exc_info.value)


def test_validate_cli_ingest_inputs_valid():
    """Test validation of valid CLI ingest inputs."""
    # This would normally fail because the path doesn't exist, but we're testing
    # that the validation logic is called
    with pytest.raises(ValidationError):
        validate_cli_ingest_inputs("/non/existent/path")


def test_validate_cli_ingest_inputs_invalid_shallow():
    """Test validation with invalid shallow depth."""
    with pytest.raises(ValidationError) as exc_info:
        validate_cli_ingest_inputs(".", shallow=-1)
    assert "shallow_depth must be an integer ≥ 1" in str(exc_info.value)


def test_validate_detection_inputs_valid():
    """Test validation of valid detection inputs."""
    # Create minimal MetricDataFrame for testing
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    # Create window definitions (non-overlapping)
    now = datetime.now()
    windows = [
        WindowDefinition(
            window_id="w03",
            start_date=now - timedelta(days=14),
            end_date=now - timedelta(days=8),  # End 1 day before next window starts
            commits=10,
            strategy="fixed_size",
        ),
        WindowDefinition(
            window_id="w04",
            start_date=now - timedelta(days=7),  # Start 1 day after previous window ends,
            end_date=now,
            commits=10,
            strategy="fixed_size",
        ),
    ]

    # This should not raise an exception
    validate_detection_inputs(
        metric_dataframe=metric_df,
        windows=windows,
        detector_config={"D-01": {"threshold": 0.5}},
        enabled_detectors=["D-01"],
    )


def test_validate_detection_inputs_invalid_enabled_detector():
    """Test validation with invalid enabled detector ID."""
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    windows = [
        WindowDefinition(
            window_id="w05",
            start_date=datetime.now() - timedelta(days=14),
            end_date=datetime.now() - timedelta(days=7),
            commits=10,
            strategy="fixed_size",
        )
    ]

    with pytest.raises(ValidationError) as exc_info:
        validate_detection_inputs(
            metric_dataframe=metric_df,
            windows=windows,
            enabled_detectors=["D-04"],  # Invalid detector ID
        )
    assert "Invalid detector ID" in str(exc_info.value)


def test_validate_detection_inputs_invalid_config_detector():
    """Test validation with invalid detector ID in detector_config."""
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    windows = [
        WindowDefinition(
            window_id="w06",
            start_date=datetime.now() - timedelta(days=14),
            end_date=datetime.now() - timedelta(days=7),
            commits=10,
            strategy="fixed_size",
        )
    ]

    with pytest.raises(ValidationError) as exc_info:
        validate_detection_inputs(
            metric_dataframe=metric_df,
            windows=windows,
            detector_config={"D-04": {"threshold": 0.5}},  # Invalid detector ID
        )
    assert "Invalid detector ID in detector_config" in str(exc_info.value)


def test_validate_detection_inputs_empty_windows():
    """Test validation with empty windows list."""
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_detection_inputs(
            metric_dataframe=metric_df,
            windows=[],  # Empty windows list
            detector_config={"D-01": {"threshold": 0.5}},
            enabled_detectors=["D-01"],
        )
    assert "windows must be a non-empty list" in str(exc_info.value)


def test_validate_d03_input_valid():
    """Test validation of valid D-03 input."""
    # This should not raise an exception
    validate_d03_input(
        metric_values=[1.0, 2.0, 3.0, 4.0, 5.0] * 4,  # 20 values (≥20 required)
        thresholds=[0.5, 1.0, 1.5, 2.0, 2.5],
        metric_id="M-01",
        window_id="w01",
        config={"margin": 0.02, "bootstrap_iterations": 1000, "bootstrap_seed": 42},
    )


def test_validate_d03_input_invalid_bootstrap_iterations():
    """Test validation with invalid bootstrap_iterations."""
    with pytest.raises(ValidationError) as exc_info:
        validate_d03_input(
            metric_values=[1.0, 2.0, 3.0, 4.0, 5.0] * 4,  # 20 values
            thresholds=[0.5, 1.0, 1.5, 2.0, 2.5],
            metric_id="M-01",
            window_id="w01",
            config={
                "margin": 0.02,
                "bootstrap_iterations": 500,  # Invalid - should be 1000
                "bootstrap_seed": 42,
            },
        )
    assert "bootstrap_iterations must be 1000 (frozen)" in str(exc_info.value)


def test_validate_d03_input_invalid_bootstrap_seed():
    """Test validation with invalid bootstrap_seed."""
    with pytest.raises(ValidationError) as exc_info:
        validate_d03_input(
            metric_values=[1.0, 2.0, 3.0, 4.0, 5.0] * 4,  # 20 values
            thresholds=[0.5, 1.0, 1.5, 2.0, 2.5],
            metric_id="M-01",
            window_id="w01",
            config={
                "margin": 0.02,
                "bootstrap_iterations": 1000,
                "bootstrap_seed": 99,  # Invalid - should be 42
            },
        )
    assert "bootstrap_seed must be 42 (frozen)" in str(exc_info.value)


def test_validate_scoring_inputs_valid():
    """Test validation of valid scoring inputs."""
    # Create minimal objects for testing
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    windows = [
        WindowDefinition(
            window_id="w07",
            start_date=datetime.now() - timedelta(days=14),
            end_date=datetime.now() - timedelta(days=7),
            commits=10,
            strategy="fixed_size",
        )
    ]

    # This should not raise an exception
    validate_scoring_inputs(
        detector_results=DetectorResults(),  # Proper DetectorResults object
        metric_dataframe=metric_df,
        windows=windows,
        detector_weights={"D-01": 0.5, "D-02": 0.3, "D-03": 0.2},
    )


def test_validate_scoring_inputs_invalid_weight_negative():
    """Test validation with negative detector weight."""
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    windows = [
        WindowDefinition(
            window_id="w08",
            start_date=datetime.now() - timedelta(days=14),
            end_date=datetime.now() - timedelta(days=7),
            commits=10,
            strategy="fixed_size",
        )
    ]

    with pytest.raises(ValidationError) as exc_info:
        validate_scoring_inputs(
            detector_results=DetectorResults(),
            metric_dataframe=metric_df,
            windows=windows,
            detector_weights={
                "D-01": -0.1,
                "D-02": 0.6,
                "D-03": 0.5,
            },  # Negative weight
        )
    assert "Weight for D-01 must be non-negative number" in str(exc_info.value)


def test_validate_scoring_inputs_invalid_detector_id():
    """Test validation with invalid detector ID in weights."""
    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(10)],
            "values": [float(i) for i in range(10)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    windows = [
        WindowDefinition(
            window_id="w09",
            start_date=datetime.now() - timedelta(days=14),
            end_date=datetime.now() - timedelta(days=7),
            commits=10,
            strategy="fixed_size",
        )
    ]

    with pytest.raises(ValidationError) as exc_info:
        validate_scoring_inputs(
            detector_results=DetectorResults(),
            metric_dataframe=metric_df,
            windows=windows,
            detector_weights={"D-01": 0.5, "D-04": 0.5},  # Invalid detector ID
        )
    assert "Invalid detector ID in detector_weights" in str(exc_info.value)


def test_validate_evidence_inputs_valid():
    """Test validation of valid evidence inputs."""
    # Create minimal valid objects for testing
    repo_context = RepositoryContext(
        repo_id="test-repo",
        local_path=Path("/path/to/repo"),
        is_remote=True,
        total_commits=100,
        contributor_count=10,
    )

    metrics_dict = {
        "M-01": {
            "timestamps": [datetime.now() - timedelta(days=i) for i in range(5)],
            "values": [float(i) for i in range(5)],
        }
    }
    metric_df = MetricDataFrame(
        repo_id="test-repo",
        run_id="test-run",
        timestamp=datetime.now(),
        metrics=metrics_dict,
    )

    windows = [
        WindowDefinition(
            window_id="w10",
            start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now() - timedelta(days=5),
            commits=10,
            strategy="fixed_size",
        )
    ]

    detector_results = DetectorResults()
    score_package = _make_score_package()

    # Minimal valid provenance with required fields
    provenance = {
        "miie_version": "1.0.0",
        "config_hash": "abc123",
        "timestamp": datetime.now().isoformat() + "Z",
        "seed": 42,
        "platform": "test-platform",
        "python_version": "3.11.9",
        "dependency_hash": "def456",
    }

    # This should not raise an exception
    validate_evidence_inputs(
        repository_context=repo_context,
        metric_dataframe=metric_df,
        windows=windows,
        detector_results=detector_results,
        score_package=score_package,
        configuration={"test": "config"},
    )


def test_validate_evidence_inputs_invalid_repo_context():
    """Test validation with invalid repository_context."""
    with pytest.raises(ValidationError) as exc_info:
        validate_evidence_inputs(
            repository_context="not-a-dict",  # Invalid type
            metric_dataframe={},
            windows=[],
            detector_results={},
            score_package={},
            configuration={},
        )
    assert "repository_context must be a valid RepositoryContext object" in str(exc_info.value)


def test_validate_evidence_inputs_invalid_windows():
    """Test validation with invalid windows list."""
    with pytest.raises(ValidationError) as exc_info:
        validate_evidence_inputs(
            repository_context=RepositoryContext(
                repo_id="test-repo",
                local_path=Path("/path/to/repo"),
                is_remote=True,
                total_commits=100,
                contributor_count=10,
            ),
            metric_dataframe=MetricDataFrame(
                repo_id="test-repo",
                run_id="test-run",
                timestamp=datetime.now(),
                metrics={"M-01": {"timestamps": [datetime.now()], "values": [1.0]}},
            ),
            windows="not-a-list",  # Invalid type
            detector_results=DetectorResults(),
            score_package=_make_score_package(),
            configuration={"test": "config"},
        )
    assert "windows must be a list" in str(exc_info.value)


def test_validate_explanation_inputs_valid():
    """Test validation of valid explanation inputs."""
    # Create minimal valid objects for testing
    provenance = Provenance(
        miie_version="1.0.0",
        config_hash="abc123",
        timestamp=datetime.now().isoformat() + "Z",
        seed=42,
        platform="test-platform",
        python_version="3.11.9",
        dependency_hash="def456",
    )
    evidence_package = EvidencePackage(
        provenance=provenance,
        windows=[
            WindowDefinition(
                window_id="w01",
                start_date=datetime.now().date() - timedelta(days=7),
                end_date=datetime.now().date(),
                commits=5,
                strategy="time",
            )
        ],
        metrics={
            "M-01": {
                "timestamps": [datetime.now() - timedelta(days=i) for i in range(5)],
                "values": [float(i) for i in range(5)],
            }
        },
        detector_outputs=DetectorResults(detector_outputs={"D-01": {"result": "test"}}),
        scores=ScorePackage(
            integrity=IntegrityScore(overall=0.5, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.5, factors={}, band=None),
            timestamp=datetime.now(tz=timezone.utc),
            config_hash="abc123",
        ),
    )
    score_package = _make_score_package()

    # This should not raise an exception
    validate_explanation_inputs(
        evidence_package=evidence_package,
        score_package=score_package,
        metric_filter="M-01",
        detector_filter="D-01",
    )


def test_validate_explanation_inputs_invalid_metric_filter():
    """Test validation with invalid metric filter."""
    # Create minimal valid objects for testing
    provenance = Provenance(
        miie_version="1.0.0",
        config_hash="abc123",
        timestamp=datetime.now().isoformat() + "Z",
        seed=42,
        platform="test-platform",
        python_version="3.11.9",
        dependency_hash="def456",
    )
    evidence_package = EvidencePackage(
        provenance=provenance,
        windows=[
            WindowDefinition(
                window_id="w01",
                start_date=datetime.now().date() - timedelta(days=7),
                end_date=datetime.now().date(),
                commits=5,
                strategy="time",
            )
        ],
        metrics={
            "M-01": {
                "timestamps": [datetime.now() - timedelta(days=i) for i in range(5)],
                "values": [float(i) for i in range(5)],
            }
        },
        detector_outputs=DetectorResults(detector_outputs={"D-01": {"result": "test"}}),
        scores=ScorePackage(
            integrity=IntegrityScore(overall=0.5, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.5, factors={}, band=None),
            timestamp=datetime.now(tz=timezone.utc),
            config_hash="abc123",
        ),
    )
    score_package = _make_score_package()

    with pytest.raises(ValidationError) as exc_info:
        validate_explanation_inputs(
            evidence_package=evidence_package,
            score_package=score_package,
            metric_filter="M-08",  # Invalid metric ID
            detector_filter="D-01",
        )
    assert "metric_filter must be one of" in str(exc_info.value)


def test_validate_explanation_inputs_invalid_detector_filter():
    """Test validation with invalid detector filter."""
    # Create minimal valid objects for testing
    provenance = Provenance(
        miie_version="1.0.0",
        config_hash="abc123",
        timestamp=datetime.now().isoformat() + "Z",
        seed=42,
        platform="test-platform",
        python_version="3.11.9",
        dependency_hash="def456",
    )
    evidence_package = EvidencePackage(
        provenance=provenance,
        windows=[
            WindowDefinition(
                window_id="w01",
                start_date=datetime.now().date() - timedelta(days=7),
                end_date=datetime.now().date(),
                commits=5,
                strategy="time",
            )
        ],
        metrics={
            "M-01": {
                "timestamps": [datetime.now() - timedelta(days=i) for i in range(5)],
                "values": [float(i) for i in range(5)],
            }
        },
        detector_outputs=DetectorResults(detector_outputs={"D-01": {"result": "test"}}),
        scores=ScorePackage(
            integrity=IntegrityScore(overall=0.5, per_metric={}, formula_version="1.0.0"),
            confidence=ConfidenceScore(overall=0.5, factors={}, band=None),
            timestamp=datetime.now(tz=timezone.utc),
            config_hash="abc123",
        ),
    )
    score_package = _make_score_package()

    with pytest.raises(ValidationError) as exc_info:
        validate_explanation_inputs(
            evidence_package=evidence_package,
            score_package=score_package,
            metric_filter="M-01",
            detector_filter="D-04",  # Invalid detector ID
        )
    assert "detector_filter must be one of" in str(exc_info.value)


def test_validate_benchmark_inputs_valid():
    """Test validation of valid benchmark inputs."""
    # This should not raise an exception
    validate_benchmark_inputs(
        suite_id="suite-1",
        detector_ids=["D-01", "D-02"],
        config={"setting": "value"},
        seed=42,
    )


def test_validate_benchmark_inputs_invalid_detector():
    """Test validation with invalid detector ID in benchmark."""
    with pytest.raises(ValidationError) as exc_info:
        validate_benchmark_inputs(
            suite_id="suite-1",
            detector_ids=["D-01", "D-04"],  # Invalid detector ID
            config={"setting": "value"},
            seed=42,
        )
    assert "Invalid detector ID" in str(exc_info.value)


def test_validate_benchmark_inputs_invalid_seed():
    """Test validation with non-integer seed."""
    with pytest.raises(ValidationError) as exc_info:
        validate_benchmark_inputs(
            suite_id="suite-1",
            detector_ids=["D-01"],
            config={"setting": "value"},
            seed="not-an-integer",  # Invalid seed type
        )
    assert "seed must be an integer" in str(exc_info.value)


def test_validate_evaluation_inputs_valid():
    """Test validation of valid evaluation inputs."""
    # Create minimal valid objects for testing
    benchmark_run = BenchmarkRun(
        predictions={"test": "prediction"},
        metadata={"benchmark_id": "test-benchmark", "run_id": "test-run"},
    )

    # This should not raise an exception
    validate_evaluation_inputs(benchmark_run=benchmark_run, ground_truth={"accuracy": 0.95})


def test_validate_evaluation_inputs_invalid_benchmark_run():
    """Test validation with invalid benchmark_run."""
    with pytest.raises(ValidationError) as exc_info:
        validate_evaluation_inputs(benchmark_run="not-a-dict", ground_truth={})  # Invalid type
    assert "benchmark_run must be a valid BenchmarkRun object" in str(exc_info.value)


def test_validate_report_inputs_valid():
    """Test validation of valid report inputs."""
    # This should not raise an exception
    validate_report_inputs(
        analysis_result={"test": "result"},
        output_formats=["json", "md"],
        output_dir=Path("/tmp/output"),
    )


def test_validate_report_inputs_invalid_format():
    """Test validation with invalid output format."""
    with pytest.raises(ValidationError) as exc_info:
        validate_report_inputs(
            analysis_result={},
            output_formats=["json", "invalid-format"],  # Invalid format
            output_dir=Path("/tmp/output"),
        )
    assert "Invalid output format: invalid-format" in str(exc_info.value)


def test_validate_cli_analyze_inputs_valid():
    """Test validation of valid CLI analyze inputs."""
    # This should not raise an exception
    validate_cli_analyze_inputs(
        repo_path="/path/to/repo",
        since="2023-01-01T00:00:00Z",
        until="2023-12-31T23:59:59Z",
        metrics=["M-01", "M-02"],
        window_strategy="time",
        window_size=7,
        output_dir=Path("/tmp/output"),
        detectors=["D-01", "D-02"],
        format=["json", "md"],
        exclude_bots=True,
    )


def test_validate_cli_analyze_inputs_invalid_metric():
    """Test validation with invalid metric ID in CLI analyze."""
    with pytest.raises(ValidationError) as exc_info:
        validate_cli_analyze_inputs(
            repo_path="/path/to/repo",
            metrics=["M-01", "M-08"],  # Invalid metric ID
            exclude_bots=True,
        )
    assert "Invalid metric ID: M-08" in str(exc_info.value)


def test_validate_cli_analyze_inputs_invalid_detector():
    """Test validation with invalid detector ID in CLI analyze."""
    with pytest.raises(ValidationError) as exc_info:
        validate_cli_analyze_inputs(
            repo_path="/path/to/repo",
            detectors=["D-01", "D-04"],  # Invalid detector ID
            exclude_bots=True,
        )
    assert "Invalid detector ID: D-04" in str(exc_info.value)


def test_import_validators():
    """Test that validator functions can be imported."""
    # This test passes if we reach this point without ImportError
    assert validate_repository_inputs is not None
    assert validate_extraction_inputs is not None
    assert validate_segmentation_inputs is not None
    assert validate_detection_inputs is not None
    assert validate_d01_input is not None
    assert validate_d02_input is not None
    assert validate_d03_input is not None
    assert validate_scoring_inputs is not None
    assert validate_evidence_inputs is not None
    assert validate_explanation_inputs is not None
    assert validate_benchmark_inputs is not None
    assert validate_evaluation_inputs is not None
    assert validate_report_inputs is not None
    assert validate_cli_ingest_inputs is not None
    assert validate_cli_analyze_inputs is not None
