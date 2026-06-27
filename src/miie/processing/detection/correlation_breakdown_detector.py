"""
Correlation Breakdown Detector implementation for MIIE v1.0.
Implements D-02 detector per TFS Section 5.2.
"""

import itertools
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import rankdata

from miie.processing.detection.base import BaseDetector
from miie.schemas.models import DetectorResult, MetricDataFrame


class CorrelationBreakdownDetector(BaseDetector):
    """
    D-02: Correlation Breakdown Detector

    Detects significant changes in correlation between metric pairs across windows.
    Implements Pearson correlation, Spearman rank correlation, and Fisher z-transformation
    for confidence interval-based breakdown detection.
    """

    def __init__(self):
        super().__init__(
            detector_id="D-02",
            detector_name="Correlation Breakdown Detector",
            supported_metrics=[f"M-{i:02d}" for i in range(1, 8)],  # M-01 through M-07
        )

        # Detection thresholds from TFS Section 5.2
        self.sudden_drop_threshold = 0.3
        self.sign_reversal_min_correlation = 0.2
        self.gradual_erosion_slope_threshold = -0.1
        self.gradual_erosion_window_start_min = 0.3
        self.gradual_erosion_window_end_max = 0.1

    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool:
        """
        Validate that at least two metrics are present for correlation analysis.

        Args:
            metric_dataframe: Input metrics to validate

        Returns:
            bool: True if at least two supported metrics are present
        """
        available_metrics = set(metric_dataframe.metrics.keys())
        required_metrics = set(self.supported_metrics)
        # Need at least two metrics to compute correlation
        return len(available_metrics.intersection(required_metrics)) >= 2

    def execute(self, metric_dataframe: MetricDataFrame) -> DetectorResult:
        """
        Execute correlation breakdown detection.

        Args:
            metric_dataframe: Input metrics for detection

        Returns:
            DetectorResult: Detection outputs with breakdown analysis
        """
        detector_outputs = {}

        # Get available metrics that we support
        available_metrics = [m for m in self.supported_metrics if m in metric_dataframe.metrics]

        if len(available_metrics) < 2:
            # Not enough metrics for correlation analysis
            detector_outputs[self.detector_id] = {
                "breakdown_detected": False,
                "breakdown_type": None,
                "metric_pairs_analyzed": [],
                "breakdown_events": [],
                "pearson_trajectories": {},
                "spearman_trajectories": {},
                "confidence_intervals": {},
                "window_pairs_flagged": [],
            }
            return DetectorResult(detector_outputs=detector_outputs)

        # Generate all unique metric pairs (i < j)
        metric_pairs = list(itertools.combinations(available_metrics, 2))

        # Get all window IDs (assuming all metrics have same windows)
        # We'll take the union of all window IDs across metrics
        window_sets = [set(metric_dataframe.metrics[m].keys()) for m in available_metrics]
        if not window_sets:
            window_ids = []
        else:
            window_ids = sorted(set.union(*window_sets))

        # Initialize results storage
        breakdown_events = []
        pearson_trajectories = {}  # (metric_i, metric_j) -> [r_values per window]
        spearman_trajectories = {}  # (metric_i, metric_j) -> [rho_values per window]
        confidence_intervals = {}  # (metric_i, metric_j, window_id) -> [lower, upper]

        # Process each metric pair
        for metric_i, metric_j in metric_pairs:
            pair_key = f"{metric_i}_{metric_j}"
            pearson_values = []
            spearman_values = []

            # Process each window in chronological order
            for window_id in window_ids:
                # Get metric values for this window
                vals_i = metric_dataframe.metrics[metric_i].get(window_id, [])
                vals_j = metric_dataframe.metrics[metric_j].get(window_id, [])

                # Check for paired observations (assume same length and ordered by index)
                n = min(len(vals_i), len(vals_j))
                if n < 10:
                    # Insufficient paired observations
                    pearson_values.append(None)
                    spearman_values.append(None)
                    continue

                # Truncate to paired observations
                x = np.array(vals_i[:n])
                y = np.array(vals_j[:n])

                # Compute Pearson correlation
                pearson_r = np.corrcoef(x, y)[0, 1]
                if np.isnan(pearson_r):
                    pearson_r = 0.0

                # Compute Spearman rank correlation
                # Use numpy to compute ranks, then Pearson on ranks
                try:
                    x_ranked = rankdata(x, method="average")
                    y_ranked = rankdata(y, method="average")
                    spearman_rho = np.corrcoef(x_ranked, y_ranked)[0, 1]
                    if np.isnan(spearman_rho):
                        spearman_rho = 0.0
                except:
                    spearman_rho = 0.0

                pearson_values.append(float(pearson_r))
                spearman_values.append(float(spearman_rho))

                # Compute confidence interval for Pearson r using Fisher z-transform
                if n >= 10:  # Already checked n>=10 above
                    # Fisher z-transform
                    z = 0.5 * np.log((1 + pearson_r) / (1 - pearson_r + 1e-10))  # Avoid division by zero
                    se = 1.0 / np.sqrt(n - 3)
                    z_critical = 1.96  # For 95% CI
                    z_lower = z - z_critical * se
                    z_upper = z + z_critical * se
                    # Transform back to r scale
                    r_lower = np.tanh(z_lower)
                    r_upper = np.tanh(z_upper)
                    confidence_intervals[(metric_i, metric_j, window_id)] = [
                        float(r_lower),
                        float(r_upper),
                    ]
                else:
                    confidence_intervals[(metric_i, metric_j, window_id)] = [0.0, 0.0]

            pearson_trajectories[pair_key] = pearson_values
            spearman_trajectories[pair_key] = spearman_values

            # Detect breakdowns for this metric pair
            pair_breakdowns = self._detect_breakdowns_for_pair(
                metric_i,
                metric_j,
                window_ids,
                pearson_values,
                spearman_values,
                confidence_intervals,
            )
            breakdown_events.extend(pair_breakdowns)

        # Determine overall breakdown detection
        breakdown_detected = len(breakdown_events) > 0
        breakdown_type = None
        if breakdown_detected:
            # Priority order: sign_reversal > sudden_drop > gradual_erosion > confidence_exclusion
            type_priority = {
                "sign_reversal": 0,
                "sudden_drop": 1,
                "gradual_erosion": 2,
                "confidence_exclusion": 3,
            }
            # Get the highest priority (lowest number) type
            breakdown_type = min(
                [event["breakdown_type"] for event in breakdown_events if event["breakdown_type"]],
                key=lambda t: type_priority[t],
            )

        # Prepare final output
        detector_outputs[self.detector_id] = {
            "breakdown_detected": breakdown_detected,
            "breakdown_type": breakdown_type,
            "metric_pairs_analyzed": [f"{m1}_{m2}" for m1, m2 in metric_pairs],
            "breakdown_events": breakdown_events,
            "pearson_trajectories": pearson_trajectories,
            "spearman_trajectories": spearman_trajectories,
            "confidence_intervals": {f"{m1}_{m2}_{w}": ci for (m1, m2, w), ci in confidence_intervals.items()},
            "window_pairs_flagged": [[event["window_pair"][0], event["window_pair"][1]] for event in breakdown_events],
        }

        return DetectorResult(detector_outputs=detector_outputs)

    def _detect_breakdowns_for_pair(
        self,
        metric_i: str,
        metric_j: str,
        window_ids: List[str],
        pearson_values: List[Optional[float]],
        spearman_values: List[Optional[float]],
        confidence_intervals: Dict[Tuple[str, str, str], List[float]],
    ) -> List[Dict]:
        """
        Detect breakdowns for a single metric pair across windows.

        Returns:
            List of breakdown event dictionaries
        """
        breakdown_events = []
        K = len(window_ids)

        if K < 2:
            return breakdown_events  # Need at least 2 windows for any comparison

        # Breakdown Type 1: Sudden drop
        for k in range(K - 1):
            if pearson_values[k] is None or pearson_values[k + 1] is None:
                continue
            delta = abs(pearson_values[k + 1] - pearson_values[k])
            if delta > self.sudden_drop_threshold:
                breakdown_events.append(
                    {
                        "metric_pair": [metric_i, metric_j],
                        "breakdown_type": "sudden_drop",
                        "window_pair": [window_ids[k], window_ids[k + 1]],
                        "delta_pearson": delta,
                        "pearson_values": [pearson_values[k], pearson_values[k + 1]],
                        "detection_method": "sudden_drop",
                    }
                )

        # Breakdown Type 2: Sign reversal
        for k in range(K - 1):
            if pearson_values[k] is None or pearson_values[k + 1] is None:
                continue
            if (
                np.sign(pearson_values[k]) != np.sign(pearson_values[k + 1])
                and abs(pearson_values[k]) > self.sign_reversal_min_correlation
                and abs(pearson_values[k + 1]) > self.sign_reversal_min_correlation
            ):
                breakdown_events.append(
                    {
                        "metric_pair": [metric_i, metric_j],
                        "breakdown_type": "sign_reversal",
                        "window_pair": [window_ids[k], window_ids[k + 1]],
                        "pearson_values": [pearson_values[k], pearson_values[k + 1]],
                        "detection_method": "sign_reversal",
                    }
                )

        # Breakdown Type 3: Gradual erosion (requires K >= 4)
        if K >= 4:
            # Only consider if first window correlation > threshold and last window correlation < threshold
            if (
                pearson_values[0] is not None
                and pearson_values[-1] is not None
                and pearson_values[0] > self.gradual_erosion_window_start_min
                and pearson_values[-1] < self.gradual_erosion_window_end_max
            ):
                # Compute linear regression slope of Pearson r over window indices
                valid_indices = []
                valid_values = []
                for idx, val in enumerate(pearson_values):
                    if val is not None:
                        valid_indices.append(idx)
                        valid_values.append(val)

                if len(valid_indices) >= 2:
                    # Simple linear regression: slope = sum((x - x_mean)*(y - y_mean)) / sum((x - x_mean)^2)
                    x = np.array(valid_indices, dtype=float)
                    y = np.array(valid_values, dtype=float)
                    x_mean = np.mean(x)
                    y_mean = np.mean(y)
                    numerator = np.sum((x - x_mean) * (y - y_mean))
                    denominator = np.sum((x - x_mean) ** 2)
                    if denominator != 0:
                        slope = numerator / denominator
                        if slope < self.gradual_erosion_slope_threshold:
                            breakdown_events.append(
                                {
                                    "metric_pair": [metric_i, metric_j],
                                    "breakdown_type": "gradual_erosion",
                                    "window_pair": [
                                        window_ids[0],
                                        window_ids[-1],
                                    ],  # First to last window
                                    "slope": slope,
                                    "pearson_values": pearson_values,
                                    "detection_method": "gradual_erosion",
                                }
                            )

        # Breakdown Type 4: Confidence interval exclusion
        if K >= 2:  # Need at least 2 windows to compare consecutive CIs
            for k in range(K - 1):
                ci_key_curr = (metric_i, metric_j, window_ids[k])
                ci_key_next = (metric_i, metric_j, window_ids[k + 1])
                if ci_key_curr in confidence_intervals and ci_key_next in confidence_intervals:
                    ci_curr = confidence_intervals[ci_key_curr]
                    ci_next = confidence_intervals[ci_key_next]
                    # Check if intervals do NOT overlap
                    if ci_curr[1] < ci_next[0] or ci_next[1] < ci_curr[0]:
                        breakdown_events.append(
                            {
                                "metric_pair": [metric_i, metric_j],
                                "breakdown_type": "confidence_exclusion",
                                "window_pair": [window_ids[k], window_ids[k + 1]],
                                "confidence_intervals": [ci_curr, ci_next],
                                "pearson_values": [
                                    pearson_values[k],
                                    pearson_values[k + 1],
                                ],
                                "detection_method": "confidence_exclusion",
                            }
                        )

        return breakdown_events
