"""
Distribution Drift Detector implementation for MIIE v1.0.
Implements D-01 detector per TFS Section 5.1.
"""

from typing import List, Optional, Tuple

import numpy as np

from miie.processing.detection.base import BaseDetector
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
        Execute distribution drift detection.

        Args:
            metric_dataframe: Input metrics for detection

        Returns:
            DetectorResult: Detection outputs with drift analysis
        """
        detector_outputs = {}

        # Get available metrics that we support
        available_metrics = [m for m in self.supported_metrics if m in metric_dataframe.metrics]

        if not available_metrics:
            # No metrics available for drift analysis
            detector_outputs[self.detector_id] = {
                "drift_detected": False,
                "drift_magnitude": 0.0,
                "metrics_analyzed": [],
                "drift_events": [],
                "ks_statistics": {},
                "psi_values": {},
                "drift_directions": {},
                "window_pairs_analyzed": [],
            }
            return DetectorResult(detector_outputs=detector_outputs)

        # Get all window IDs (assuming all metrics have same windows)
        # We'll take the union of all window IDs across metrics
        window_sets = [set(metric_dataframe.metrics[m].keys()) for m in available_metrics]
        if not window_sets:
            window_ids = []
        else:
            window_ids = sorted(set.union(*window_sets))

        # Initialize results storage
        drift_events = []
        ks_statistics = {}  # (metric, window_pair) -> KS statistic
        psi_values = {}  # (metric, window_pair) -> PSI value
        drift_directions = {}  # (metric, window_pair) -> direction string

        # Process each metric
        for metric in available_metrics:
            metric_ks = {}
            metric_psi = {}
            metric_directions = {}

            # Get window IDs for this metric (should be same as all, but be safe)
            metric_windows = sorted(set(metric_dataframe.metrics[metric].keys()))
            if len(metric_windows) < 2:
                # Need at least 2 windows for drift detection
                continue

            # Process consecutive window pairs (W_i, W_{i+1})
            for i in range(len(metric_windows) - 1):
                window_start = metric_windows[i]
                window_end = metric_windows[i + 1]

                # Get metric values for the two windows
                vals_start = metric_dataframe.metrics[metric].get(window_start, [])
                vals_end = metric_dataframe.metrics[metric].get(window_end, [])

                # Check for sufficient sample size (TFS: ||W_i|| < 10 or ||W_{i+1}|| < 10 -> skip)
                if len(vals_start) < 10 or len(vals_end) < 10:
                    # Insufficient sample size - skip with warning (we'll just not detect drift)
                    continue

                # Kolmogorov-Smirnov Test
                ks_statistic, ks_p_value = self._ks_2samp(vals_start, vals_end)
                metric_ks[f"{window_start}_{window_end}"] = float(ks_statistic)

                # Population Stability Index (PSI)
                psi_value = self._compute_psi(vals_start, vals_end)
                metric_psi[f"{window_start}_{window_end}"] = float(psi_value)

                # Determine drift direction
                drift_detected = (ks_p_value < self.ks_p_value_threshold) or (psi_value > self.psi_threshold)
                direction = None
                if drift_detected:
                    direction = self._classify_drift_direction(vals_start, vals_end, ks_statistic, psi_value)
                    metric_directions[f"{window_start}_{window_end}"] = direction

                    # Add drift event
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

            ks_statistics[metric] = metric_ks
            psi_values[metric] = metric_psi
            drift_directions[metric] = metric_directions

        # Determine overall drift detection
        drift_detected = len(drift_events) > 0
        # Drift magnitude: average KS statistic normalized to [0,1] (capped at 0.5 -> 1.0)
        # Per TFS Section 6.3: drift_magnitude = ks_statistic (normalized to [0,1] by capping at 0.5)
        drift_magnitude = 0.0
        if drift_events:
            ks_vals = [event["ks_statistic"] for event in drift_events]
            # Normalize: KS statistic is in [0,1], but TFS says to normalize by capping at 0.5
            # So: if KS <= 0.5, magnitude = KS/0.5; if KS > 0.5, magnitude = 1.0
            normalized_ks = [min(1.0, ks / 0.5) for ks in ks_vals]
            drift_magnitude = float(np.mean(normalized_ks))

        # Prepare final output
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
        }

        return DetectorResult(detector_outputs=detector_outputs)

    def _ks_2samp(self, data1: List[float], data2: List[float]) -> Tuple[float, float]:
        """
        Compute Kolmogorov-Smirnov statistic and p-value for two samples.
        Uses the asymptotic approximation for the p-value.
        """
        n1 = len(data1)
        n2 = len(data2)
        if n1 == 0 or n2 == 0:
            return 0.0, 1.0

        # Sort the data
        data1_sorted = np.sort(data1)
        data2_sorted = np.sort(data2)

        # Get all unique values from both datasets
        all_values = np.concatenate([data1_sorted, data2_sorted])
        all_values = np.unique(all_values)

        # Compute empirical CDFs
        cdf1 = np.searchsorted(data1_sorted, all_values, side="right") / n1
        cdf2 = np.searchsorted(data2_sorted, all_values, side="right") / n2

        # KS statistic is the maximum absolute difference
        ks_statistic = np.max(np.abs(cdf1 - cdf2))

        # Asymptotic p-value approximation
        # Formula: p-value = 2 * exp(-2 * ks^2 * n_eff)
        # where n_eff = n1 * n2 / (n1 + n2)
        n_eff = (n1 * n2) / (n1 + n2)
        if n_eff > 0:
            ks_p_value = 2 * np.exp(-2 * ks_statistic**2 * n_eff)
            # Cap at [0, 1]
            ks_p_value = max(0.0, min(1.0, ks_p_value))
        else:
            ks_p_value = 1.0

        return ks_statistic, ks_p_value

    def _compute_psi(self, expected: List[float], actual: List[float]) -> float:
        """
        Compute Population Stability Index (PSI) between expected and actual distributions.
        Uses 10 equal-width bins over the range [min(expected ∪ actual), max(expected ∪ actual)].
        """
        if len(expected) == 0 or len(actual) == 0:
            return 0.0

        # Combine data to determine bin range
        combined = np.concatenate([expected, actual])
        min_val = np.min(combined)
        max_val = np.max(combined)

        # Avoid division by zero if all values are the same
        if min_val == max_val:
            return 0.0

        # Create 10 equal-width bins
        bins = np.linspace(min_val, max_val, 11)  # 11 edges for 10 bins

        # Compute histograms
        expected_hist, _ = np.histogram(expected, bins=bins, density=False)
        actual_hist, _ = np.histogram(actual, bins=bins, density=False)

        # Convert to proportions
        expected_prop = expected_hist / len(expected)
        actual_prop = actual_hist / len(actual)

        # Avoid zeros in expected proportion (add small epsilon)
        epsilon = 1e-10
        expected_prop = np.where(expected_prop == 0, epsilon, expected_prop)
        actual_prop = np.where(actual_prop == 0, epsilon, actual_prop)

        # Compute PSI: sum((actual - expected) * ln(actual / expected))
        psi = np.sum((actual_prop - expected_prop) * np.log(actual_prop / expected_prop))

        return float(psi)

    def _classify_drift_direction(
        self,
        vals_start: List[float],
        vals_end: List[float],
        ks_statistic: float,
        psi_value: float,
    ) -> Optional[str]:
        """
        Classify drift direction based on TFS Section 5.1 logic.
        Returns one of: "mean_shift", "variance_collapse", "shape_change", or None.
        """
        if len(vals_start) < 2 or len(vals_end) < 2:
            return None

        # Compute basic statistics
        mean_start = np.mean(vals_start)
        mean_end = np.mean(vals_end)
        var_start = np.var(vals_start)
        var_end = np.var(vals_end)

        # Mean shift detection
        mean_diff = mean_end - mean_start
        std_start = np.std(vals_start) if var_start > 0 else 0.0
        if std_start > 0 and abs(mean_diff) > 0.5 * std_start:
            return "mean_shift"

        # Variance collapse detection
        if var_start > 0:
            var_ratio = var_end / var_start
            if var_ratio < 0.5:
                return "variance_collapse"

        # Shape change (default if drift detected but not mean_shift or variance_collapse)
        # Per TFS: IF drift_detected AND NOT (mean_shift OR variance_collapse): direction = "shape_change"
        # We assume drift_detected is True when this function is called
        return "shape_change"
