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
