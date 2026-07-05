"""
Distribution Drift Detector implementation for MIIE v1.0.
Implements D-01 detector per TFS Section 5.1.

Extended in v1.5 with detect_observations() that consumes ObservationWindow
data directly, using true per-commit observation samples instead of
aggregated single values.

Reference: DES-v2.0 §16.3, §21, IMS-v1.0 Phase 5
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from miie.processing.detection.base import BaseDetector
from miie.processing.detection.diagnostics import d01_diagnostics
from miie.processing.detection.inference import StatisticalInferenceEngine
from miie.processing.detection.statistics import compute_psi, ks_2samp
from miie.schemas.models import DetectorResult, MetricDataFrame


class DistributionDriftDetector(BaseDetector):
    """
    D-01: Distributional Drift Detector

    Detects significant changes in distribution between consecutive windows
    using Kolmogorov-Smirnov test and Population Stability Index (PSI).
    """

    def __init__(self):
        super().__init__(
            detector_id="D-01",
            detector_name="Distribution Drift Detector",
            supported_metrics=[f"M-{i:02d}" for i in range(1, 8)],  # M-01 through M-07
        )

        # Detection thresholds from TFS Section 5.1
        self.ks_p_value_threshold = 0.05
        self.psi_threshold = 0.25

    # ------------------------------------------------------------------
    # v1.5 Observation-Window Path
    # ------------------------------------------------------------------

    def detect_observations(
        self,
        windows: List[Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> DetectorResult:
        """Execute distribution drift detection on ObservationWindows.

        Extracts per-metric values from each window's observations and
        performs KS and PSI tests on consecutive window pairs.

        Args:
            windows: List of ObservationWindow objects.
            config: Optional overrides for ks_p_value_threshold, psi_threshold.

        Returns:
            DetectorResult with drift analysis.
        """
        detector_outputs: Dict[str, Any] = {}

        # Apply config overrides
        ks_threshold = self.ks_p_value_threshold
        psi_thresh = self.psi_threshold
        if config:
            ks_threshold = config.get("ks_p_value_threshold", ks_threshold)
            psi_thresh = config.get("psi_threshold", psi_thresh)

        # Discover available metrics across all windows
        available_metrics = self._discover_metrics(windows)

        if not available_metrics:
            detector_outputs[self.detector_id] = self._empty_output([], [])
            return DetectorResult(detector_outputs=detector_outputs)

        window_ids = [w.window_id for w in windows]

        drift_events: List[Dict[str, Any]] = []
        drift_diagnostics: List[Dict[str, Any]] = []
        ks_statistics: Dict[str, Dict[str, float]] = {}
        psi_values: Dict[str, Dict[str, float]] = {}
        drift_directions: Dict[str, Dict[str, str]] = {}

        for metric in available_metrics:
            metric_ks: Dict[str, float] = {}
            metric_psi: Dict[str, float] = {}
            metric_directions: Dict[str, str] = {}

            # Extract per-window value lists for this metric
            window_values = self._extract_metric_values(windows, metric)

            if len(window_ids) < 2:
                continue

            for i in range(len(window_ids) - 1):
                w_start = window_ids[i]
                w_end = window_ids[i + 1]
                vals_start = window_values.get(w_start, [])
                vals_end = window_values.get(w_end, [])

                if len(vals_start) < 10 or len(vals_end) < 10:
                    continue

                # KS test using shared statistics
                ks_stat, ks_p = ks_2samp(vals_start, vals_end)
                pair_key = f"{w_start}_{w_end}"
                metric_ks[pair_key] = ks_stat

                # PSI using shared statistics
                psi_val = compute_psi(vals_start, vals_end)
                metric_psi[pair_key] = psi_val

                # Drift detection
                drift_detected = (ks_p < ks_threshold) or (psi_val > psi_thresh)
                if drift_detected:
                    direction = self._classify_drift_direction(vals_start, vals_end)
                    metric_directions[pair_key] = direction

                    drift_events.append(
                        {
                            "metric": metric,
                            "window_pair": [w_start, w_end],
                            "drift_detected": True,
                            "ks_statistic": float(ks_stat),
                            "ks_p_value": float(ks_p),
                            "psi_value": float(psi_val),
                            "direction": direction,
                            "sample_sizes": [len(vals_start), len(vals_end)],
                        }
                    )

                    # PR-16B: Compute diagnostics with actual values
                    d_diag = d01_diagnostics(
                        vals_start=vals_start,
                        vals_end=vals_end,
                        ks_stat=float(ks_stat),
                        ks_p=float(ks_p),
                        alpha=ks_threshold,
                    )
                    d_diag["metric"] = metric
                    d_diag["window_pair"] = [w_start, w_end]
                    drift_diagnostics.append(d_diag)

            ks_statistics[metric] = metric_ks
            psi_values[metric] = metric_psi
            drift_directions[metric] = metric_directions

        # Flatten for output
        flat_ks = {f"{m}_{wp}": v for m, d in ks_statistics.items() for wp, v in d.items()}
        flat_psi = {f"{m}_{wp}": v for m, d in psi_values.items() for wp, v in d.items()}
        flat_dirs = {f"{m}_{wp}": v for m, d in drift_directions.items() for wp, v in d.items()}

        drift_detected = len(drift_events) > 0
        drift_magnitude = 0.0
        if drift_events:
            ks_vals = [e["ks_statistic"] for e in drift_events]
            normalized = [min(1.0, ks / 0.5) for ks in ks_vals]
            drift_magnitude = float(np.mean(normalized))

        # ------------------------------------------------------------------
        # PR-16A: Multiple-testing correction (Bonferroni per window pair)
        # ------------------------------------------------------------------
        inference_families: List[Dict[str, Any]] = []
        for i in range(len(window_ids) - 1):
            w_start = window_ids[i]
            w_end = window_ids[i + 1]
            pair_key = f"{w_start}_{w_end}"

            family_p_values: List[float] = []
            family_test_ids: List[str] = []
            for metric in available_metrics:
                kp = ks_statistics.get(metric, {}).get(pair_key)
                if kp is not None:
                    family_p_values.append(kp)
                    family_test_ids.append(f"{metric}_{pair_key}")

            if family_p_values:
                result = StatisticalInferenceEngine.bonferroni(
                    family_p_values,
                    alpha=ks_threshold,
                    family_id=f"KS_{pair_key}",
                )
                inference_families.append(StatisticalInferenceEngine.result_to_dict(result))

        total_ks_tests = sum(f["num_tests"] for f in inference_families)
        total_ks_rejections = sum(f["num_rejections"] for f in inference_families)

        # ------------------------------------------------------------------
        # PR-16B: Power / effect-size / sample-adequacy diagnostics
        # ------------------------------------------------------------------

        detector_outputs[self.detector_id] = {
            "drift_detected": drift_detected,
            "drift_magnitude": drift_magnitude,
            "metrics_analyzed": available_metrics,
            "drift_events": drift_events,
            "ks_statistics": flat_ks,
            "psi_values": flat_psi,
            "drift_directions": flat_dirs,
            "window_pairs_analyzed": [[window_ids[i], window_ids[i + 1]] for i in range(len(window_ids) - 1)],
            "inference": {
                "method": "bonferroni",
                "alpha": ks_threshold,
                "families": inference_families,
                "summary": {
                    "total_ks_tests": total_ks_tests,
                    "total_ks_rejections": total_ks_rejections,
                },
            },
            "diagnostics": {
                "enabled": True,
                "per_event": drift_diagnostics,
            },
        }

        return DetectorResult(detector_outputs=detector_outputs)

    # ------------------------------------------------------------------
    # Legacy MetricDataFrame Path (unchanged for backward compatibility)
    # ------------------------------------------------------------------

    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool:
        """
        Validate that at least one metric is present for drift analysis.

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
        Execute distribution drift detection (legacy path).

        Args:
            metric_dataframe: Input metrics for detection

        Returns:
            DetectorResult: Detection outputs with drift analysis
        """
        detector_outputs: Dict[str, Any] = {}

        available_metrics = [
            m
            for m in self.supported_metrics
            if m in metric_dataframe.metrics and metric_dataframe.metrics[m] is not None
        ]

        if not available_metrics:
            detector_outputs[self.detector_id] = self._empty_output([], [])
            return DetectorResult(detector_outputs=detector_outputs)

        window_sets = [set(metric_dataframe.metrics[m].keys()) for m in available_metrics]
        window_ids = sorted(set.union(*window_sets)) if window_sets else []

        drift_events: List[Dict[str, Any]] = []
        drift_diagnostics_legacy: List[Dict[str, Any]] = []
        ks_statistics: Dict[str, Dict[str, float]] = {}
        psi_values: Dict[str, Dict[str, float]] = {}
        drift_directions: Dict[str, Dict[str, str]] = {}

        for metric in available_metrics:
            metric_ks: Dict[str, float] = {}
            metric_psi: Dict[str, float] = {}
            metric_directions: Dict[str, str] = {}

            metric_windows = sorted(set(metric_dataframe.metrics[metric].keys()))
            if len(metric_windows) < 2:
                continue

            for i in range(len(metric_windows) - 1):
                window_start = metric_windows[i]
                window_end = metric_windows[i + 1]

                vals_start = metric_dataframe.metrics[metric].get(window_start, [])
                vals_end = metric_dataframe.metrics[metric].get(window_end, [])

                if len(vals_start) < 10 or len(vals_end) < 10:
                    continue

                # Use shared statistics module
                ks_statistic, ks_p_value = ks_2samp(vals_start, vals_end)
                pair_key = f"{window_start}_{window_end}"
                metric_ks[pair_key] = float(ks_statistic)

                psi_value = compute_psi(vals_start, vals_end)
                metric_psi[pair_key] = float(psi_value)

                drift_detected = (ks_p_value < self.ks_p_value_threshold) or (psi_value > self.psi_threshold)
                if drift_detected:
                    direction = self._classify_drift_direction(vals_start, vals_end)
                    metric_directions[pair_key] = direction

                    drift_events.append(
                        {
                            "metric": metric,
                            "window_pair": [window_start, window_end],
                            "drift_detected": True,
                            "ks_statistic": float(ks_statistic),
                            "ks_p_value": float(ks_p_value),
                            "psi_value": float(psi_value),
                            "direction": direction,
                            "sample_sizes": [len(vals_start), len(vals_end)],
                        }
                    )

                    # PR-16B: Diagnostics with actual values
                    d_diag = d01_diagnostics(
                        vals_start=vals_start,
                        vals_end=vals_end,
                        ks_stat=float(ks_statistic),
                        ks_p=float(ks_p_value),
                        alpha=self.ks_p_value_threshold,
                    )
                    d_diag["metric"] = metric
                    d_diag["window_pair"] = [window_start, window_end]
                    drift_diagnostics_legacy.append(d_diag)

            ks_statistics[metric] = metric_ks
            psi_values[metric] = metric_psi
            drift_directions[metric] = metric_directions

        drift_detected = len(drift_events) > 0
        drift_magnitude = 0.0
        if drift_events:
            ks_vals = [event["ks_statistic"] for event in drift_events]
            normalized_ks = [min(1.0, ks / 0.5) for ks in ks_vals]
            drift_magnitude = float(np.mean(normalized_ks))

        # ------------------------------------------------------------------
        # PR-16A: Multiple-testing correction (Bonferroni per window pair)
        # ------------------------------------------------------------------
        inference_families: List[Dict[str, Any]] = []
        for i in range(len(window_ids) - 1):
            ws = window_ids[i]
            we = window_ids[i + 1]
            pair_key = f"{ws}_{we}"

            fam_p: List[float] = []
            fam_ids: List[str] = []
            for metric in available_metrics:
                kp = ks_statistics.get(metric, {}).get(pair_key)
                if kp is not None:
                    fam_p.append(kp)
                    fam_ids.append(f"{metric}_{pair_key}")

            if fam_p:
                result = StatisticalInferenceEngine.bonferroni(
                    fam_p,
                    alpha=self.ks_p_value_threshold,
                    family_id=f"KS_{pair_key}",
                )
                inference_families.append(StatisticalInferenceEngine.result_to_dict(result))

        total_ks_tests = sum(f["num_tests"] for f in inference_families)
        total_ks_rejections = sum(f["num_rejections"] for f in inference_families)

        detector_outputs[self.detector_id] = {
            "drift_detected": drift_detected,
            "drift_magnitude": drift_magnitude,
            "metrics_analyzed": available_metrics,
            "drift_events": drift_events,
            "ks_statistics": {f"{m}_{wp}": ks for m, ks_dict in ks_statistics.items() for wp, ks in ks_dict.items()},
            "psi_values": {f"{m}_{wp}": psi for m, psi_dict in psi_values.items() for wp, psi in psi_dict.items()},
            "drift_directions": {
                f"{m}_{wp}": direction for m, dir_dict in drift_directions.items() for wp, direction in dir_dict.items()
            },
            "window_pairs_analyzed": [[window_ids[i], window_ids[i + 1]] for i in range(len(window_ids) - 1)],
            "inference": {
                "method": "bonferroni",
                "alpha": self.ks_p_value_threshold,
                "families": inference_families,
                "summary": {
                    "total_ks_tests": total_ks_tests,
                    "total_ks_rejections": total_ks_rejections,
                },
            },
            "diagnostics": {
                "enabled": True,
                "per_event": drift_diagnostics_legacy,
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
        """Extract per-window value lists for a metric from ObservationWindows."""
        result: Dict[str, List[float]] = {}
        for w in windows:
            values = [obs.value for obs in w.observations if obs.metric_id == metric_id]
            if values:
                result[w.window_id] = values
        return result

    def _classify_drift_direction(
        self,
        vals_start: List[float],
        vals_end: List[float],
    ) -> str:
        """Classify drift direction per DES §21.1."""
        if len(vals_start) < 2 or len(vals_end) < 2:
            return "shape_change"

        mean_start = float(np.mean(vals_start))
        mean_end = float(np.mean(vals_end))
        var_start = float(np.var(vals_start))
        var_end = float(np.var(vals_end))

        std_start = float(np.std(vals_start)) if var_start > 0 else 0.0
        if std_start > 0 and abs(mean_end - mean_start) > 0.5 * std_start:
            return "mean_shift"

        if var_start > 0 and (var_end / var_start) < 0.5:
            return "variance_collapse"

        return "shape_change"

    def _empty_output(self, drift_events: List[Any], window_pairs: List[Any]) -> Dict[str, Any]:
        """Return the empty (no-drift) output structure."""
        return {
            "drift_detected": False,
            "drift_magnitude": 0.0,
            "metrics_analyzed": [],
            "drift_events": drift_events,
            "ks_statistics": {},
            "psi_values": {},
            "drift_directions": {},
            "window_pairs_analyzed": window_pairs,
        }
