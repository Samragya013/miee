"""
Data schemas for MIIE v1.0 core entities.

Implements the four core schemas needed for Day 10 dry-run slice:
- RepositoryContext
- MetricDataFrame
- DetectorResult
- EvidencePackage
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

from miie.schemas.serialization import json_dumps, json_loads


@dataclass
class RepositoryContext:
    """
    Repository context extracted during ingestion (M-01).

    Source: BSD-Engineering Section 5.3
    """
    repo_id: str
    local_path: Path
    is_remote: bool
    remote_url: Optional[str] = None
    total_commits: int = 0
    first_commit_date: Optional[datetime.datetime] = None
    last_commit_date: Optional[datetime.datetime] = None
    contributor_count: int = 0
    is_shallow: bool = False
    is_fork: bool = False
    language_distribution: Optional[Dict[str, int]] = None

    def __post_init__(self):
        """Validate RepositoryContext constraints."""
        if self.total_commits < 10:
            raise ValueError(f"total_commits must be >= 10, got {self.total_commits}")
        if self.contributor_count < 1:
            raise ValueError(f"contributor_count must be >= 1, got {self.contributor_count}")


@dataclass
class MetricDataFrame:
    """
    Container for extracted metrics (M-02 output).

    Source: BSD-Engineering Section 6
    Represents metric data as defined in BSD Section 6.3 JSON serialization.
    """
    repo_id: str
    run_id: str
    timestamp: datetime.datetime
    metrics: Dict[str, Dict[str, List[Optional[float]]]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate that only frozen metrics are present."""
        allowed_metrics = {f"M-{i:02d}" for i in range(1, 8)}  # M-01 through M-07
        for metric_id in self.metrics:
            if metric_id not in allowed_metrics:
                raise ValueError(f"Invalid metric ID: {metric_id}. Must be one of {allowed_metrics}")


@dataclass
class DetectorResult:
    """
    Container for detector results (D-01 through D-03 output).

    Source: BSD-Engineering Section 8 and class DetectorResults
    """
    detector_outputs: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        """Validate that only frozen detectors are present."""
        allowed_detectors = {f"D-{i:02d}" for i in range(1, 4)}  # D-01 through D-03
        for detector_id in self.detector_outputs:
            if detector_id not in allowed_detectors:
                raise ValueError(f"Invalid detector ID: {detector_id}. Must be one of {allowed_detectors}")


@dataclass
class EvidencePackage:
    """
    Container for traceable evidence (M-09 Evidence Aggregator output).

    Source: BSD-Engineering Section 10.1 and TFS Appendix A
    """
    provenance: Dict
    windows: List[Dict]
    metrics: Dict[str, Dict[str, List[Optional[float]]]]
    detector_outputs: Dict[str, Dict]
    scores: Dict[str, Dict]
    warnings: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        """Validate EvidencePackage structure."""
        # Validate provenance
        required_provenance = {"miie_version", "config_hash", "timestamp", "seed", "platform", "python_version", "dependency_hash"}
        if not all(key in self.provenance for key in required_provenance):
            raise ValueError(f"Provenance missing required fields: {required_provenance}")

        # Validate windows structure
        for window in self.windows:
            required_window = {"id", "start", "end", "commits"}
            if not all(key in window for key in required_window):
                raise ValueError(f"Window missing required fields: {required_window}")

        # Validate metrics structure (same as MetricDataFrame)
        allowed_metrics = {f"M-{i:02d}" for i in range(1, 8)}
        for metric_id in self.metrics:
            if metric_id not in allowed_metrics:
                raise ValueError(f"Invalid metric ID in evidence: {metric_id}")

        # Validate detector outputs
        allowed_detectors = {f"D-{i:02d}" for i in range(1, 4)}
        for detector_id in self.detector_outputs:
            if detector_id not in allowed_detectors:
                raise ValueError(f"Invalid detector ID in evidence: {detector_id}")


# TODO: These are placeholder implementations for deferred schema classes.
# According to the operating plan, these schemas are deferred with reasons documented.
# They are implemented here as minimal placeholders to allow contracts layer development.
# In a full implementation, these would be replaced with the complete ACS v1.0 schema definitions.

@dataclass
class WindowDefinition:
    """
    Definition of an analysis window (deferred schema placeholder).

    Source: ACS v1.0 Section 6.2 (Window Definition)
    TODO: Implement full WindowDefinition schema per ACS v1.0 specification
    """
    start_date: datetime.datetime
    end_date: datetime.datetime

    def __post_init__(self):
        """Validate WindowDefinition constraints."""
        if self.start_date >= self.end_date:
            raise ValueError(f"start_date must be before end_date, got start_date={self.start_date}, end_date={self.end_date}")


@dataclass
class DetectorResults:
    """
    Container for results from multiple detectors (deferred schema placeholder).

    Source: ACS v1.0 Section 8.3 (Detector Results Aggregation)
    TODO: Implement full DetectorResults schema per ACS v1.0 specification
    """
    detector_outputs: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        """Validate DetectorResults constraints."""
        # Placeholder validation - full validation TBD
        pass


@dataclass
class ScorePackage:
    """
    Container for computed integrity and confidence scores (deferred schema placeholder).

    Source: ACS v1.0 Section 9.2 (Score Package)
    TODO: Implement full ScorePackage schema per ACS v1.0 specification
    """
    scores: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Validate ScorePackage constraints."""
        # Placeholder validation - full validation TBD
        pass


@dataclass
class ExplanationReport:
    """
    Container for explanation narratives and recommendations (deferred schema placeholder).

    Source: ACS v1.0 Section 10.3 (Explanation Report)
    TODO: Implement full ExplanationReport schema per ACS v1.0 specification
    """
    narratives: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate ExplanationReport constraints."""
        # Placeholder validation - full validation TBD
        pass


@dataclass
class BenchmarkRun:
    """
    Container for benchmark execution results (deferred schema placeholder).

    Source: ACS v1.0 Section 11.2 (Benchmark Run)
    TODO: Implement full BenchmarkRun schema per ACS v1.0 specification
    """
    predictions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate BenchmarkRun constraints."""
        # Placeholder validation - full validation TBD
        pass


@dataclass
class EvaluationResult:
    """
    Container for evaluation metrics (deferred schema placeholder).

    Source: ACS v1.0 Section 12.2 (Evaluation Result)
    TODO: Implement full EvaluationResult schema per ACS v1.0 specification
    """
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0

    def __post_init__(self):
        """Validate EvaluationResult constraints."""
        # Placeholder validation - full validation TBD
        if not (0.0 <= self.accuracy <= 1.0):
            raise ValueError(f"accuracy must be between 0.0 and 1.0, got {self.accuracy}")
        if not (0.0 <= self.precision <= 1.0):
            raise ValueError(f"precision must be between 0.0 and 1.0, got {self.precision}")
        if not (0.0 <= self.recall <= 1.0):
            raise ValueError(f"recall must be between 0.0 and 1.0, got {self.recall}")
        if not (0.0 <= self.f1_score <= 1.0):
            raise ValueError(f"f1_score must be between 0.0 and 1.0, got {self.f1_score}")


@dataclass
class ReportOutput:
    """
    Container for generated report output paths (deferred schema placeholder).

    Source: ACS v1.0 Section 13.2 (Report Output)
    TODO: Implement full ReportOutput schema per ACS v1.0 specification
    """
    report_paths: Dict[str, Path] = field(default_factory=dict)

    def __post_init__(self):
        """Validate ReportOutput constraints."""
        # Placeholder validation - full validation TBD
        pass


@dataclass
class GroundTruthInput:
    """
    Container for ground truth input data (deferred schema placeholder).

    Source: ACS v1.0 Section 14.2 (Ground Truth Input)
    TODO: Implement full GroundTruthInput schema per ACS v1.0 specification
    """
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate GroundTruthInput constraints."""
        # Placeholder validation - full validation TBD
        pass


@dataclass
class Annotation:
    """
    Container for individual annotations (deferred schema placeholder).

    Source: ACS v1.0 Section 15.2 (Annotation)
    TODO: Implement full Annotation schema per ACS v1.0 specification
    """
    label: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate Annotation constraints."""
        # Placeholder validation - full validation TBD
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")