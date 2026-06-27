"""Evidence Engine for MIIE v1.0.

Implements INT-04: Evidence Engine interface.
Builds traceable evidence packages from scores and detector results.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List

from miie.schemas.models import MetricDataFrame, RepositoryContext

from ..schemas.models import (
    DetectorResults,
    EvidencePackage,
    Provenance,
    ScorePackage,
    WindowDefinition,
)


class EvidenceEngine:
    """INT-04: Evidence Engine"""

    def generate(
        self,
        repository_context: RepositoryContext,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_results: DetectorResults,
        score_package: ScorePackage,
        configuration: Dict[str, Any],
    ) -> EvidencePackage:
        """Generate evidence package from scores and detector results.

        Args:
            repository_context: Repository context from ingestion
            metric_dataframe: Container for extracted metrics
            windows: List of window definitions used for analysis
            detector_results: Raw detector outputs
            score_package: Container for integrity and confidence scores
            configuration: Analysis configuration used

        Returns:
            EvidencePackage: Traceable evidence package
        """
        # For Day 9 foundation, we create a basic evidence package
        # In future versions, this would include detailed evidence construction
        now = datetime.now(timezone.utc)
        seed = configuration.get("seed", 42)
        # Deterministic evidence_id: hash of seed + config_hash (no timestamp)
        _hash_input = f"{seed}:{configuration.get('config_hash', 'foundation')}"
        _hash_suffix = hashlib.sha256(_hash_input.encode()).hexdigest()[:8]
        evidence_id = f"evidence_{seed}_{_hash_suffix}"
        score_package_id = f"score_package_{seed}"
        detector_results_ids = list(detector_results.detector_outputs.keys())
        metrics_used = list(metric_dataframe.metrics.keys()) if hasattr(metric_dataframe, "metrics") else []
        windows_analyzed = [w.window_id for w in windows] if windows and hasattr(windows[0], "window_id") else ["w00"]
        integrity_verification = {"verified": True, "method": "foundation"}
        confidence_indicators = (
            score_package.confidence.get("factors", {})
            if isinstance(score_package.confidence, dict)
            else score_package.confidence.factors
        )
        reproducibility_info = {"seed": seed, "deterministic": True}
        das_notation = f"DAS:{seed}:{_hash_suffix}"

        # Convert WindowDefinition objects to dict format expected by EvidencePackage
        windows_as_dicts = []
        for w in windows:
            windows_as_dicts.append(
                {
                    "id": w.window_id,
                    "start": w.start_date.isoformat() + "T00:00:00Z",
                    "end": w.end_date.isoformat() + "T00:00:00Z",
                    "commits": w.commits,
                }
            )

        return EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash=configuration.get("config_hash", "foundation"),
                timestamp=now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                seed=seed,
                platform=configuration.get("platform", "test"),
                python_version=configuration.get("python_version", "3.9.0"),
                dependency_hash=configuration.get("dependency_hash", "foundation"),
            ),
            windows=windows,
            metrics=(metric_dataframe.metrics if hasattr(metric_dataframe, "metrics") else {}),
            detector_outputs=detector_results,
            scores=score_package,
            warnings=[],
        )


class MockEvidenceEngine:
    """Mock evidence engine that returns deterministic evidence package."""

    def generate(
        self,
        repository_context: RepositoryContext,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_results: DetectorResults,
        score_package: ScorePackage,
        configuration: Dict[str, Any],
    ) -> EvidencePackage:
        """Return a fixed EvidencePackage for testing."""
        fixed_timestamp = datetime(2023, 6, 15, tzinfo=timezone.utc)
        seed = configuration.get("seed", 42)
        evidence_id = f"mock_evidence_{seed}"
        score_package_id = f"mock_score_package_{seed}"
        detector_results_ids = list(detector_results.detector_outputs.keys())
        metrics_used = list(metric_dataframe.metrics.keys()) if hasattr(metric_dataframe, "metrics") else []
        windows_analyzed = [w.window_id for w in windows] if windows and hasattr(windows[0], "window_id") else ["w00"]
        integrity_verification = {"verified": True, "method": "mock"}
        confidence_indicators = (
            score_package.confidence.get("factors", {})
            if isinstance(score_package.confidence, dict)
            else score_package.confidence.factors
        )
        reproducibility_info = {"seed": seed, "deterministic": True}
        das_notation = f"DAS:mock:{seed}"

        # Convert WindowDefinition objects to dict format expected by EvidencePackage
        windows_as_dicts = []
        for w in windows:
            windows_as_dicts.append(
                {
                    "id": w.window_id,
                    "start": w.start_date.isoformat() + "T00:00:00Z",
                    "end": w.end_date.isoformat() + "T00:00:00Z",
                    "commits": w.commits,
                }
            )

        return EvidencePackage(
            provenance=Provenance(
                miie_version="1.0.0",
                config_hash=configuration.get("config_hash", "mock"),
                timestamp=fixed_timestamp.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                seed=seed,
                platform=configuration.get("platform", "test"),
                python_version=configuration.get("python_version", "3.9.0"),
                dependency_hash=configuration.get("dependency_hash", "mock"),
            ),
            windows=windows,
            metrics=(metric_dataframe.metrics if hasattr(metric_dataframe, "metrics") else {}),
            detector_outputs=detector_results,
            scores=score_package,
            warnings=[],
        )
