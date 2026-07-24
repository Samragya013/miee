"""
Threshold Compression Detector implementation for MIIE v1.0.
Implements D-03 detector per TFS Section 5.3.

Extended in v1.5 with detect_observations() that consumes ObservationWindow
data directly, using true per-commit observation samples for excess mass
and dip test computations.

Reference: DES-v2.0 §16.5, §23, IMS-v1.0 Phase 5
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from miie.processing.detection.base import BaseDetector
from miie.processing.detection.diagnostics import d03_diagnostics
from miie.processing.detection.inference import StatisticalInferenceEngine
from miie.processing.detection.statistics import (
    auto_thresholds,
    compute_epsilon,
    dip_test,
    excess_mass_test,
)
from miie.schemas.models import DetectorResult, MetricDataFrame


class ThresholdCompressionDetector(BaseDetector):
    """
    D-03: Threshold Compression Detector

    Detects artificial clustering of values around thresholds using
    Excess Mass test and Hartigans' Dip test (supporting).
    """

    def __init__(self):
        super().__init__(
            detector_id="D-03",
            detector_name="Threshold Compression Detector",
            supported_metrics=[f"M-{i:02d}" for i in range(1, 8)],  # M-01 through M-07
        )

        # Detection thresholds from TFS Section 5.3
        self.excess_mass_z_threshold = 1.0  # PR-16D: calibrated from 1.645
        self.dip_test_p_threshold = 0.05
        self.dip_test_bootstrap_samples = 1000
        self.dip_test_random_seed = 42

        # Auto-threshold detection parameters from TFS Section 5.3
        self.auto_threshold_candidates = [
            1,
            5,
            10,
            20,
            25,
            50,
            75,
            80,
            90,
            95,
            100,
            1000,
        ]
        self.auto_threshold_percentiles = [10, 25, 50, 75, 90]

    # ------------------------------------------------------------------
    # v1.5 Observation-Window Path
    # ------------------------------------------------------------------

    def detect_observations(
        self,
        windows: List[Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> DetectorResult:
        """Execute threshold compression detection on ObservationWindows.

        Args:
            windows: List of ObservationWindow objects.
            config: Optional overrides for detection thresholds.

        Returns:
            DetectorResult with compression analysis.
        """
        detector_outputs: Dict[str, Any] = {}

        # Apply config overrides
        em_z_thresh = self.excess_mass_z_threshold
        dip_p_thresh = self.dip_test_p_threshold
        dip_boot = self.dip_test_bootstrap_samples
        dip_seed = self.dip_test_random_seed
        if config:
            em_z_thresh = config.get("excess_mass_z_threshold", em_z_thresh)
            dip_p_thresh = config.get("dip_test_p_threshold", dip_p_thresh)
            dip_boot = config.get("dip_test_bootstrap_samples", dip_boot)
            dip_seed = config.get("dip_test_random_seed", dip_seed)

        available_metrics = self._discover_metrics(windows)

        if not available_metrics:
            detector_outputs[self.detector_id] = self._empty_output()
            return DetectorResult(detector_outputs=detector_outputs)

        window_ids = [w.window_id for w in windows]

        compression_events: List[Dict[str, Any]] = []
        compression_diagnostics: List[Dict[str, Any]] = []
        thresholds_used: Dict[str, List[float]] = {}
        excess_mass_z_scores: Dict[str, float] = {}
        dip_test_statistics: Dict[str, float] = {}
        dip_test_p_values: Dict[str, float] = {}

        processed_windows: set[str] = set()

        for metric in available_metrics:
            # Extract all values for this metric across windows
            all_vals = self._extract_all_values(windows, metric)
            metric_thresholds = auto_thresholds(
                all_vals,
                self.auto_threshold_candidates,
                self.auto_threshold_percentiles,
            )
            thresholds_used[metric] = metric_thresholds

            if not metric_thresholds:
                continue

            # Extract per-window values
            window_values = self._extract_metric_values(windows, metric)

            for threshold in metric_thresholds:
                for wid in window_ids:
                    vals = window_values.get(wid, [])

                    if len(vals) < 20:
                        continue

                    processed_windows.add(wid)

                    # Excess mass test using shared statistics
                    eps = compute_epsilon(vals, threshold)
                    z_score = excess_mass_test(vals, threshold, eps)
                    excess_mass_z_scores[f"{metric}_{threshold}_{wid}"] = float(z_score)

                    # Dip test using shared statistics
                    dip_stat, dip_p = dip_test(vals, bootstrap_samples=dip_boot, random_seed=dip_seed)
                    dip_test_statistics[f"{metric}_{threshold}_{wid}"] = float(dip_stat)
                    dip_test_p_values[f"{metric}_{threshold}_{wid}"] = float(dip_p)

                    excess_mass_flag = z_score > em_z_thresh
                    multimodal_flag = dip_p < dip_p_thresh

                    in_band = int(np.sum(np.abs(np.array(vals) - threshold) <= eps))
                    p_hat = in_band / len(vals) if len(vals) > 0 else 0.0

                    if excess_mass_flag and (multimodal_flag or p_hat > 0.5):
                        compression_events.append(
                            {
                                "metric": metric,
                                "threshold": threshold,
                                "window": wid,
                                "compression_detected": True,
                                "compression_index": float(p_hat),
                                "excess_mass_z_score": float(z_score),
                                "dip_test_statistic": float(dip_stat),
                                "dip_test_p_value": float(dip_p),
                                "epsilon": float(eps),
                                "sample_size": len(vals),
                                "hypothesized_cause": self._infer_cause(metric, threshold),
                            }
                        )

                        # PR-16B: Diagnostics
                        d_diag = d03_diagnostics(
                            vals=vals,
                            threshold=threshold,
                            eps=float(eps),
                            z_score=float(z_score),
                            dip_stat=float(dip_stat),
                            dip_p=float(dip_p),
                            alpha=dip_p_thresh,
                        )
                        d_diag["metric"] = metric
                        d_diag["window"] = wid
                        d_diag["threshold"] = threshold
                        compression_diagnostics.append(d_diag)

        compression_detected = len(compression_events) > 0
        compression_index = 0.0
        if compression_events:
            compression_index = float(np.mean([e["compression_index"] for e in compression_events]))

        # ------------------------------------------------------------------
        # PR-16A: Multiple-testing correction (Bonferroni per window)
        # ------------------------------------------------------------------
        inference_families: List[Dict[str, Any]] = []
        for wid in window_ids:
            fam_p: List[float] = []
            fam_ids: List[str] = []
            for metric in available_metrics:
                thresholds = thresholds_used.get(metric, [])
                for threshold in thresholds:
                    key = f"{metric}_{threshold}_{wid}"
                    dip_p = dip_test_p_values.get(key)
                    if dip_p is not None:
                        fam_p.append(dip_p)
                        fam_ids.append(key)

            if fam_p:
                result = StatisticalInferenceEngine.holm(
                    fam_p,
                    alpha=dip_p_thresh,
                    family_id=f"DIP_{wid}",
                )
                inference_families.append(StatisticalInferenceEngine.result_to_dict(result))

        total_dip_tests = sum(f["num_tests"] for f in inference_families)
        total_dip_rejections = sum(f["num_rejections"] for f in inference_families)

        detector_outputs[self.detector_id] = {
            "compression_detected": compression_detected,
            "compression_index": compression_index,
            "metrics_analyzed": available_metrics,
            "compression_events": compression_events,
            "thresholds_used": thresholds_used,
            "excess_mass_z_scores": excess_mass_z_scores,
            "dip_test_statistics": dip_test_statistics,
            "dip_test_p_values": dip_test_p_values,
            "windows_analyzed": sorted(list(processed_windows)),
            "diagnostics": {
                "enabled": True,
                "per_event": compression_diagnostics,
            },
            "inference": {
                "method": "holm",
                "alpha": dip_p_thresh,
                "families": inference_families,
                "summary": {
                    "total_dip_tests": total_dip_tests,
                    "total_dip_rejections": total_dip_rejections,
                },
            },
        }

        return DetectorResult(detector_outputs=detector_outputs)

    # ------------------------------------------------------------------
    # Legacy MetricDataFrame Path (unchanged for backward compatibility)
    # ------------------------------------------------------------------

    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool:
        """
        Validate that at least one metric is present for threshold compression analysis.

        Args:
            metric_dataframe: Input metrics to validate

        Returns:
            bool: True if at least one supported metric is present
        """
        available_metrics = set(metric_dataframe.metrics.keys())
        required_metrics = set(self.supported_metrics)
        return len(available_metrics.intersection(required_metrics)) >= 1

    def execute(self, metric_dataframe: MetricDataFrame) -> DetectorResult:
        """
        Execute threshold compression detection (legacy path).

        Args:
            metric_dataframe: Input metrics for detection

        Returns:
            DetectorResult: Detection outputs with compression analysis
        """
        detector_outputs: Dict[str, Any] = {}

        available_metrics = [
            m
            for m in self.supported_metrics
            if m in metric_dataframe.metrics and metric_dataframe.metrics[m] is not None
        ]

        if not available_metrics:
            detector_outputs[self.detector_id] = self._empty_output()
            return DetectorResult(detector_outputs=detector_outputs)

        window_sets = [set(metric_dataframe.metrics[m].keys()) for m in available_metrics]
        window_ids = sorted(set.union(*window_sets)) if window_sets else []

        compression_events: List[Dict[str, Any]] = []
        compression_diagnostics_legacy: List[Dict[str, Any]] = []
        thresholds_used: Dict[str, List[float]] = {}
        excess_mass_z_scores: Dict[str, float] = {}
        dip_test_statistics: Dict[str, float] = {}
        dip_test_p_values: Dict[str, float] = {}

        processed_windows: set[str] = set()

        for metric in available_metrics:
            # Get thresholds using shared statistics
            all_vals = []
            for window_id, vals in metric_dataframe.metrics[metric].items():
                all_vals.extend(vals)

            if not all_vals:
                continue

            metric_thresholds = auto_thresholds(
                all_vals,
                self.auto_threshold_candidates,
                self.auto_threshold_percentiles,
            )
            thresholds_used[metric] = metric_thresholds

            if not metric_thresholds:
                continue

            metric_windows = sorted(set(metric_dataframe.metrics[metric].keys()))

            for threshold in metric_thresholds:
                for window_id in metric_windows:
                    vals = metric_dataframe.metrics[metric].get(window_id, [])

                    if len(vals) < 20:
                        continue

                    processed_windows.add(window_id)

                    # Use shared statistics module
                    eps = compute_epsilon(vals, threshold)
                    z_score = excess_mass_test(vals, threshold, eps)
                    excess_mass_z_scores[f"{metric}_{threshold}_{window_id}"] = float(z_score)

                    dip_stat, dip_p = dip_test(
                        vals,
                        bootstrap_samples=self.dip_test_bootstrap_samples,
                        random_seed=self.dip_test_random_seed,
                    )
                    dip_test_statistics[f"{metric}_{threshold}_{window_id}"] = float(dip_stat)
                    dip_test_p_values[f"{metric}_{threshold}_{window_id}"] = float(dip_p)

                    excess_mass_flag = z_score > self.excess_mass_z_threshold
                    multimodal_flag = dip_p < self.dip_test_p_threshold

                    in_band = int(np.sum(np.abs(np.array(vals) - threshold) <= eps))
                    p_hat = in_band / len(vals) if len(vals) > 0 else 0.0

                    if excess_mass_flag and (multimodal_flag or p_hat > 0.5):
                        compression_events.append(
                            {
                                "metric": metric,
                                "threshold": threshold,
                                "window": window_id,
                                "compression_detected": True,
                                "compression_index": float(p_hat),
                                "excess_mass_z_score": float(z_score),
                                "dip_test_statistic": float(dip_stat),
                                "dip_test_p_value": float(dip_p),
                                "epsilon": float(eps),
                                "sample_size": len(vals),
                                "hypothesized_cause": self._infer_cause(metric, threshold),
                            }
                        )

                        # PR-16B: Diagnostics
                        d_diag = d03_diagnostics(
                            vals=vals,
                            threshold=threshold,
                            eps=float(eps),
                            z_score=float(z_score),
                            dip_stat=float(dip_stat),
                            dip_p=float(dip_p),
                            alpha=self.dip_test_p_threshold,
                        )
                        d_diag["metric"] = metric
                        d_diag["window"] = window_id
                        d_diag["threshold"] = threshold
                        compression_diagnostics_legacy.append(d_diag)

        compression_detected = len(compression_events) > 0
        compression_index = 0.0
        if compression_events:
            compression_index = float(np.mean([e["compression_index"] for e in compression_events]))

        # ------------------------------------------------------------------
        # PR-16A: Multiple-testing correction (Bonferroni per window)
        # ------------------------------------------------------------------
        inference_families: List[Dict[str, Any]] = []
        for wid in window_ids:
            fam_p: List[float] = []
            fam_ids: List[str] = []
            for metric in available_metrics:
                thresholds = thresholds_used.get(metric, [])
                for threshold in thresholds:
                    key = f"{metric}_{threshold}_{wid}"
                    dip_p = dip_test_p_values.get(key)
                    if dip_p is not None:
                        fam_p.append(dip_p)
                        fam_ids.append(key)

            if fam_p:
                result = StatisticalInferenceEngine.holm(
                    fam_p,
                    alpha=self.dip_test_p_threshold,
                    family_id=f"DIP_{wid}",
                )
                inference_families.append(StatisticalInferenceEngine.result_to_dict(result))

        total_dip_tests = sum(f["num_tests"] for f in inference_families)
        total_dip_rejections = sum(f["num_rejections"] for f in inference_families)

        detector_outputs[self.detector_id] = {
            "compression_detected": compression_detected,
            "compression_index": compression_index,
            "metrics_analyzed": available_metrics,
            "compression_events": compression_events,
            "thresholds_used": {m: t for m, t in thresholds_used.items()},
            "excess_mass_z_scores": excess_mass_z_scores,
            "dip_test_statistics": dip_test_statistics,
            "dip_test_p_values": dip_test_p_values,
            "windows_analyzed": sorted(list(processed_windows)),
            "diagnostics": {
                "enabled": True,
                "per_event": compression_diagnostics_legacy,
            },
            "inference": {
                "method": "holm",
                "alpha": self.dip_test_p_threshold,
                "families": inference_families,
                "summary": {
                    "total_dip_tests": total_dip_tests,
                    "total_dip_rejections": total_dip_rejections,
                },
            },
        }

        return DetectorResult(detector_outputs=detector_outputs)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _discover_metrics(self, windows: List[Any]) -> List[str]:
        """Find all supported metric IDs present in any window."""
        found: set[str] = set()
        for w in windows:
            for obs in w.observations:
                if obs.metric_id in self.supported_metrics:
                    found.add(obs.metric_id)
        return sorted(found)

    def _extract_metric_values(self, windows: List[Any], metric_id: str) -> Dict[str, List[float]]:
        """Extract per-window value lists for a metric."""
        result: Dict[str, List[float]] = {}
        for w in windows:
            values = [obs.value for obs in w.observations if obs.metric_id == metric_id]
            if values:
                result[w.window_id] = values
        return result

    def _extract_all_values(self, windows: List[Any], metric_id: str) -> List[float]:
        """Extract all values for a metric across all windows."""
        result: List[float] = []
        for w in windows:
            result.extend(obs.value for obs in w.observations if obs.metric_id == metric_id)
        return result

    def _infer_cause(self, metric: str, threshold: float) -> str:
        """Rule-based cause inference for threshold compression.

        Classification Tiers:
        - POLICY_MANDATE: External policy requires threshold
        - SLA_COMPLIANCE: Service level agreement constraints
        - THRESHOLD_GAMING: Deliberate threshold manipulation
        - UNKNOWN: Unable to determine cause
        """
        if self._has_policy_marker(metric):
            return "POLICY_MANDATE"

        if self._has_sla_marker(metric):
            return "SLA_COMPLIANCE"

        if self._detect_gaming_pattern(metric, threshold):
            return "THRESHOLD_GAMING"

        return "UNKNOWN"

    def _has_policy_marker(self, metric: str) -> bool:
        """Check if metric has policy mandate markers."""
        policy_indicators = ["POLICY", "COMPLIANCE", "GOVERNANCE", "REGULATORY"]
        return any(indicator in metric.upper() for indicator in policy_indicators)

    def _has_sla_marker(self, metric: str) -> bool:
        """Check if metric has SLA compliance markers."""
        sla_indicators = ["SLA", "UPTIME", "LATENCY", "AVAILABILITY"]
        return any(indicator in metric.upper() for indicator in sla_indicators)

    def _detect_gaming_pattern(self, metric: str, threshold: float) -> bool:
        """Detect statistical patterns indicating threshold gaming."""
        return False

    def _empty_output(self) -> Dict[str, Any]:
        """Return the empty (no-compression) output structure."""
        return {
            "compression_detected": False,
            "compression_index": 0.0,
            "metrics_analyzed": [],
            "compression_events": [],
            "thresholds_used": {},
            "excess_mass_z_scores": {},
            "dip_test_statistics": {},
            "dip_test_p_values": {},
            "windows_analyzed": [],
        }
