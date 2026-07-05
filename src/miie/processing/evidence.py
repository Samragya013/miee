"""Evidence Engine for MIIE v1.0.

Implements INT-04: Evidence Engine interface.
Builds traceable evidence packages from scores and detector results.

Extended: IMS Phase 6 (Evidence Refactor) for observation-level provenance.
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
    """INT-04: Evidence Engine

    Generates evidence packages with complete observation-level provenance,
    including observation summaries, detector execution metadata, statistical
    artifacts, and configuration snapshots.
    """

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
            EvidencePackage: Traceable evidence package with observation-level provenance
        """
        now = datetime.now(timezone.utc)
        seed = configuration.get("seed", 42)

        # Generate provenance
        provenance = self._generate_provenance(
            configuration=configuration,
            seed=seed,
            timestamp=now,
        )

        # Extract observation summary
        observation_summary = self._extract_observation_summary(
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
        )

        # Extract detector execution metadata
        detector_execution_metadata = self._extract_detector_execution_metadata(
            detector_results=detector_results,
            configuration=configuration,
        )

        # Extract statistical artifacts
        statistical_artifacts = self._extract_statistical_artifacts(
            detector_results=detector_results,
        )

        # Create configuration snapshot
        configuration_snapshot = self._create_configuration_snapshot(
            configuration=configuration,
        )

        return EvidencePackage(
            provenance=provenance,
            windows=windows,
            metrics=(metric_dataframe.metrics if hasattr(metric_dataframe, "metrics") else {}),
            detector_outputs=detector_results,
            scores=score_package,
            warnings=[],
            # Observation-level provenance fields (IMS Phase 6)
            observation_summary=observation_summary,
            detector_execution_metadata=detector_execution_metadata,
            statistical_artifacts=statistical_artifacts,
            configuration_snapshot=configuration_snapshot,
            # Sampling framework diagnostics (PR-7B)
            sampling_diagnostics=configuration.get("sampling_diagnostics", {}),
        )

    def generate_observation_evidence(
        self,
        repository_context: RepositoryContext,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_results: DetectorResults,
        configuration: Dict[str, Any],
    ) -> EvidencePackage:
        """Generate partial evidence package with observation-level metadata only.

        This method generates an EvidencePackage without scores, which can be
        passed to the scoring engine for observation-aware scoring. The scores
        field will be None.

        Args:
            repository_context: Repository context from ingestion
            metric_dataframe: Container for extracted metrics
            windows: List of window definitions used for analysis
            detector_results: Raw detector outputs
            configuration: Analysis configuration used

        Returns:
            EvidencePackage: Partial evidence package with observation-level metadata
        """
        now = datetime.now(timezone.utc)
        seed = configuration.get("seed", 42)

        # Generate provenance
        provenance = self._generate_provenance(
            configuration=configuration,
            seed=seed,
            timestamp=now,
        )

        # Extract observation summary
        observation_summary = self._extract_observation_summary(
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
        )

        # Extract detector execution metadata
        detector_execution_metadata = self._extract_detector_execution_metadata(
            detector_results=detector_results,
            configuration=configuration,
        )

        # Extract statistical artifacts
        statistical_artifacts = self._extract_statistical_artifacts(
            detector_results=detector_results,
        )

        # Create configuration snapshot
        configuration_snapshot = self._create_configuration_snapshot(
            configuration=configuration,
        )

        return EvidencePackage(
            provenance=provenance,
            windows=windows,
            metrics=(metric_dataframe.metrics if hasattr(metric_dataframe, "metrics") else {}),
            detector_outputs=detector_results,
            scores=None,  # No scores yet - will be added after scoring
            warnings=[],
            # Observation-level provenance fields (IMS Phase 6)
            observation_summary=observation_summary,
            detector_execution_metadata=detector_execution_metadata,
            statistical_artifacts=statistical_artifacts,
            configuration_snapshot=configuration_snapshot,
        )

    def _generate_provenance(
        self,
        configuration: Dict[str, Any],
        seed: int,
        timestamp: datetime,
    ) -> Provenance:
        """Generate provenance information."""
        # Deterministic evidence_id: hash of seed + config_hash (no timestamp)
        _hash_input = f"{seed}:{configuration.get('config_hash', 'foundation')}"
        _hash_suffix = hashlib.sha256(_hash_input.encode()).hexdigest()[:8]

        return Provenance(
            miie_version="1.0.0",
            config_hash=configuration.get("config_hash", "foundation"),
            timestamp=timestamp.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            seed=seed,
            platform=configuration.get("platform", "test"),
            python_version=configuration.get("python_version", "3.9.0"),
            dependency_hash=configuration.get("dependency_hash", "foundation"),
        )

    def _extract_observation_summary(
        self,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_results: DetectorResults,
    ) -> Dict[str, Any]:
        """Extract observation summary from metric data and detector results."""
        summary: Dict[str, Any] = {
            "total_observations": 0,
            "per_metric": {},
            "observation_quality": {"complete": 0, "partial": 0, "estimated": 0},
        }

        # Count observations from metric_dataframe
        if hasattr(metric_dataframe, "metrics"):
            for metric_id, metric_data in metric_dataframe.metrics.items():
                if isinstance(metric_data, dict) and "default" in metric_data:
                    values = metric_data["default"]
                    if isinstance(values, list):
                        count = len(values)
                        summary["total_observations"] += count

                        # Calculate value range
                        try:
                            value_range = [min(values), max(values)] if values else [0, 0]
                        except (TypeError, ValueError):
                            value_range = [0, 0]

                        summary["per_metric"][metric_id] = {
                            "count": count,
                            "window_count": len(windows),
                            "value_range": value_range,
                        }

                        # Assume complete quality for now
                        summary["observation_quality"]["complete"] += count

        # Add detector-specific observation counts
        for detector_id, output in detector_results.detector_outputs.items():
            if "observation_counts" in output:
                for metric_id, count in output["observation_counts"].items():
                    if metric_id in summary["per_metric"]:
                        summary["per_metric"][metric_id]["detector_observations"] = count
                    else:
                        summary["per_metric"][metric_id] = {
                            "count": count,
                            "window_count": len(windows),
                            "value_range": [0, 0],
                            "detector_observations": count,
                        }

        return summary

    def _extract_detector_execution_metadata(
        self,
        detector_results: DetectorResults,
        configuration: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """Extract per-detector execution metadata."""
        metadata: Dict[str, Dict[str, Any]] = {}

        detector_config = configuration.get("detector_config", {})

        for detector_id, output in detector_results.detector_outputs.items():
            detector_metadata: Dict[str, Any] = {
                "windows_analyzed": len(output.get("window_pairs_analyzed", [])),
                "observations_consumed": sum((output.get("observation_counts") or {}).values()),
            }

            # Add detector-specific parameters
            if detector_id in detector_config:
                detector_metadata["parameters"] = detector_config[detector_id]

            # Add method information based on detector type
            if detector_id == "D-01":
                detector_metadata["method"] = "kolmogorov_smirnov"
                detector_metadata["scientific_reference"] = "KS test for distribution drift"
            elif detector_id == "D-02":
                detector_metadata["method"] = "pearson_correlation"
                detector_metadata["scientific_reference"] = "Pearson correlation with Fisher z-transformation"
            elif detector_id == "D-03":
                detector_metadata["method"] = "dip_test_excess_mass"
                detector_metadata["scientific_reference"] = "Dip test for unimodality with excess mass"

            metadata[detector_id] = detector_metadata

        return metadata

    def _extract_statistical_artifacts(
        self,
        detector_results: DetectorResults,
    ) -> Dict[str, Any]:
        """Extract statistical artifacts from detector outputs."""
        artifacts: Dict[str, Any] = {
            "drift_statistics": {},
            "correlation_artifacts": {},
            "compression_artifacts": {},
        }

        for detector_id, output in detector_results.detector_outputs.items():
            if detector_id == "D-01":
                # Extract drift statistics
                drift_stats: Dict[str, Any] = {}
                if "ks_statistics" in output:
                    drift_stats["ks_statistics"] = output["ks_statistics"]
                if "psi_values" in output:
                    drift_stats["psi_values"] = output["psi_values"]
                if "drift_events" in output:
                    drift_stats["drift_events"] = output["drift_events"]
                artifacts["drift_statistics"][detector_id] = drift_stats

            elif detector_id == "D-02":
                # Extract correlation artifacts
                corr_artifacts: Dict[str, Any] = {}
                if "correlation_changes" in output:
                    corr_artifacts["correlation_changes"] = output["correlation_changes"]
                if "fisher_z_scores" in output:
                    corr_artifacts["fisher_z_scores"] = output["fisher_z_scores"]
                artifacts["correlation_artifacts"][detector_id] = corr_artifacts

            elif detector_id == "D-03":
                # Extract compression artifacts
                comp_artifacts: Dict[str, Any] = {}
                if "dip_statistics" in output:
                    comp_artifacts["dip_statistics"] = output["dip_statistics"]
                if "excess_mass_statistics" in output:
                    comp_artifacts["excess_mass_statistics"] = output["excess_mass_statistics"]
                artifacts["compression_artifacts"][detector_id] = comp_artifacts

        return artifacts

    def _create_configuration_snapshot(
        self,
        configuration: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a snapshot of the configuration used."""
        snapshot: Dict[str, Any] = {
            "metric_list": configuration.get("metric_list", []),
            "segmentation_strategy": configuration.get("segmentation_strategy", "temporal"),
            "segmentation_size": configuration.get("segmentation_size", 100),
            "detector_config": configuration.get("detector_config", {}),
            "enabled_detectors": configuration.get("enabled_detectors", ["D-01", "D-02", "D-03"]),
            "extraction_params": {
                "since": configuration.get("since"),
                "until": configuration.get("until"),
                "exclude_bots": configuration.get("exclude_bots", True),
            },
        }

        return snapshot


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

        # Extract observation summary
        observation_summary: Dict[str, Any] = {
            "total_observations": 0,
            "per_metric": {},
            "observation_quality": {"complete": 0, "partial": 0, "estimated": 0},
        }
        if hasattr(metric_dataframe, "metrics"):
            for metric_id, metric_data in metric_dataframe.metrics.items():
                if isinstance(metric_data, dict) and "default" in metric_data:
                    values = metric_data["default"]
                    if isinstance(values, list):
                        count = len(values)
                        observation_summary["total_observations"] += count
                        observation_summary["per_metric"][metric_id] = {
                            "count": count,
                            "window_count": len(windows),
                            "value_range": [min(values), max(values)] if values else [0, 0],
                        }
                        observation_summary["observation_quality"]["complete"] += count

        # Extract detector execution metadata
        detector_execution_metadata: Dict[str, Dict[str, Any]] = {}
        for detector_id, output in detector_results.detector_outputs.items():
            detector_execution_metadata[detector_id] = {
                "windows_analyzed": len(output.get("window_pairs_analyzed", [])),
                "observations_consumed": sum((output.get("observation_counts") or {}).values()),
                "method": f"mock_{detector_id.lower()}",
                "scientific_reference": f"Mock method for {detector_id}",
            }

        # Extract statistical artifacts
        statistical_artifacts: Dict[str, Any] = {
            "drift_statistics": {},
            "correlation_artifacts": {},
            "compression_artifacts": {},
        }
        for detector_id, output in detector_results.detector_outputs.items():
            if detector_id == "D-01":
                statistical_artifacts["drift_statistics"][detector_id] = {
                    k: v for k, v in output.items() if k in ["ks_statistics", "psi_values", "drift_events"]
                }
            elif detector_id == "D-02":
                statistical_artifacts["correlation_artifacts"][detector_id] = {
                    k: v for k, v in output.items() if k in ["correlation_changes", "fisher_z_scores"]
                }
            elif detector_id == "D-03":
                statistical_artifacts["compression_artifacts"][detector_id] = {
                    k: v for k, v in output.items() if k in ["dip_statistics", "excess_mass_statistics"]
                }

        # Create configuration snapshot
        configuration_snapshot: Dict[str, Any] = {
            "metric_list": configuration.get("metric_list", []),
            "segmentation_strategy": configuration.get("segmentation_strategy", "temporal"),
            "segmentation_size": configuration.get("segmentation_size", 100),
            "detector_config": configuration.get("detector_config", {}),
            "enabled_detectors": configuration.get("enabled_detectors", ["D-01", "D-02", "D-03"]),
            "extraction_params": {
                "since": configuration.get("since"),
                "until": configuration.get("until"),
                "exclude_bots": configuration.get("exclude_bots", True),
            },
        }

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
            # Observation-level provenance fields (IMS Phase 6)
            observation_summary=observation_summary,
            detector_execution_metadata=detector_execution_metadata,
            statistical_artifacts=statistical_artifacts,
            configuration_snapshot=configuration_snapshot,
        )

    def generate_observation_evidence(
        self,
        repository_context: RepositoryContext,
        metric_dataframe: MetricDataFrame,
        windows: List[WindowDefinition],
        detector_results: DetectorResults,
        configuration: Dict[str, Any],
    ) -> EvidencePackage:
        """Generate partial evidence package with observation-level metadata only."""
        fixed_timestamp = datetime(2023, 6, 15, tzinfo=timezone.utc)
        seed = configuration.get("seed", 42)

        # Extract observation summary
        observation_summary: Dict[str, Any] = {
            "total_observations": 0,
            "per_metric": {},
            "observation_quality": {"complete": 0, "partial": 0, "estimated": 0},
        }
        if hasattr(metric_dataframe, "metrics"):
            for metric_id, metric_data in metric_dataframe.metrics.items():
                if isinstance(metric_data, dict) and "default" in metric_data:
                    values = metric_data["default"]
                    if isinstance(values, list):
                        count = len(values)
                        observation_summary["total_observations"] += count
                        observation_summary["per_metric"][metric_id] = {
                            "count": count,
                            "window_count": len(windows),
                            "value_range": [min(values), max(values)] if values else [0, 0],
                        }
                        observation_summary["observation_quality"]["complete"] += count

        # Extract detector execution metadata
        detector_execution_metadata: Dict[str, Dict[str, Any]] = {}
        for detector_id, output in detector_results.detector_outputs.items():
            detector_execution_metadata[detector_id] = {
                "windows_analyzed": len(output.get("window_pairs_analyzed", [])),
                "observations_consumed": sum((output.get("observation_counts") or {}).values()),
                "method": f"mock_{detector_id.lower()}",
                "scientific_reference": f"Mock method for {detector_id}",
            }

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
            scores=None,
            warnings=[],
            observation_summary=observation_summary,
            detector_execution_metadata=detector_execution_metadata,
        )
