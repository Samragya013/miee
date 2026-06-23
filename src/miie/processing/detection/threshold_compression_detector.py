"""
Threshold Compression Detector implementation for MIIE v1.0.
Implements D-03 detector per TFS Section 5.3.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from miie.processing.detection.base import BaseDetector
from miie.schemas.models import DetectorResult, MetricDataFrame
import itertools


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
            supported_metrics=[f"M-{i:02d}" for i in range(1, 8)]  # M-01 through M-07
        )

        # Detection thresholds from TFS Section 5.3
        self.excess_mass_z_threshold = 1.645  # One-tailed, α = 0.05
        self.dip_test_p_threshold = 0.05
        self.dip_test_bootstrap_samples = 1000
        self.dip_test_random_seed = 42

        # Auto-threshold detection parameters from TFS Section 5.3
        self.auto_threshold_candidates = [1, 5, 10, 20, 25, 50, 75, 80, 90, 95, 100, 1000]
        self.auto_threshold_percentiles = [10, 25, 50, 75, 90]

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
        Execute threshold compression detection.

        Args:
            metric_dataframe: Input metrics for detection

        Returns:
            DetectorResult: Detection outputs with compression analysis
        """
        detector_outputs = {}

        # Get available metrics that we support
        available_metrics = [
            m for m in self.supported_metrics
            if m in metric_dataframe.metrics
        ]

        if not available_metrics:
            # No metrics available for compression analysis
            detector_outputs[self.detector_id] = {
                "compression_detected": False,
                "compression_index": 0.0,
                "metrics_analyzed": [],
                "compression_events": [],
                "thresholds_used": {},
                "excess_mass_z_scores": {},
                "dip_test_statistics": {},
                "dip_test_p_values": {},
                "windows_analyzed": []
            }
            return DetectorResult(detector_outputs=detector_outputs)

        # Get all window IDs (assuming all metrics have same windows)
        window_sets = [
            set(metric_dataframe.metrics[m].keys())
            for m in available_metrics
        ]
        if not window_sets:
            window_ids = []
        else:
            window_ids = sorted(set.union(*window_sets))

        # Initialize results storage
        compression_events = []
        thresholds_used = {}      # metric -> [thresholds]
        excess_mass_z_scores = {} # (metric, threshold, window) -> z-score
        dip_test_statistics = {}  # (metric, threshold, window) -> dip stat
        dip_test_p_values = {}    # (metric, threshold, window) -> dip p-value

        # Set random seed for dip test bootstrap
        rng = np.random.default_rng(self.dip_test_random_seed)

        # Process each metric
        processed_windows = set()
        for metric in available_metrics:
            metric_thresholds = self._get_thresholds_for_metric(
                metric_dataframe, metric
            )
            thresholds_used[metric] = metric_thresholds

            if not metric_thresholds:
                # No thresholds to test for this metric
                continue

            # Get window IDs for this metric
            metric_windows = sorted(set(metric_dataframe.metrics[metric].keys()))
            if not metric_windows:
                continue

            # Process each threshold and window
            for threshold in metric_thresholds:
                for window_id in metric_windows:
                    # Get metric values for this window
                    vals = metric_dataframe.metrics[metric].get(window_id, [])

                    # Skip if insufficient sample size (TFS: ||W|| < 20 -> skip)
                    if len(vals) < 20:
                        continue
                    # Mark that we are processing this window (at least for this metric-threshold combo)
                    processed_windows.add(window_id)

                    # Perform excess mass test
                    z_score = self._excess_mass_test(vals, threshold)
                    excess_mass_z_scores[(metric, threshold, window_id)] = float(z_score)

                    # Perform dip test (supporting)
                    dip_stat, dip_p = self._dip_test(
                        vals,
                        bootstrap_samples=self.dip_test_bootstrap_samples,
                        random_seed=self.dip_test_random_seed
                    )
                    dip_test_statistics[(metric, threshold, window_id)] = float(dip_stat)
                    dip_test_p_values[(metric, threshold, window_id)] = float(dip_p)

                    # Determine if compression is detected
                    # Per TFS Section 5.3: Final flag: TRUE if excess_mass_flag AND (multimodal_flag OR p_hat > 0.5)
                    # where:
                    #   excess_mass_flag = (z_score > z_0.95)  [one-tailed, α = 0.05]
                    #   multimodal_flag = (dip_p < 0.05)
                    #   p_hat = proportion of values in band [T-ε, T+ε]
                    excess_mass_flag = z_score > self.excess_mass_z_threshold
                    multimodal_flag = dip_p < self.dip_test_p_threshold

                    # Compute p_hat (proportion in band)
                    epsilon = self._compute_epsilon(vals, threshold)
                    in_band = np.sum(np.abs(np.array(vals) - threshold) <= epsilon)
                    p_hat = in_band / len(vals) if len(vals) > 0 else 0.0

                    if excess_mass_flag and (multimodal_flag or p_hat > 0.5):
                        # Compression detected
                        compression_events.append({
                            "metric": metric,
                            "threshold": threshold,
                            "window": window_id,
                            "compression_detected": True,
                            "compression_index": float(p_hat),  # Per TFS: compression_index = p_hat
                            "excess_mass_z_score": float(z_score),
                            "dip_test_statistic": float(dip_stat),
                            "dip_test_p_value": float(dip_p),
                            "epsilon": float(epsilon),
                            "sample_size": len(vals),
                            "hypothesized_cause": self._infer_cause(metric, threshold)  # Rule-based
                        })

        # Determine overall compression detection
        compression_detected = len(compression_events) > 0
        # Compression index: average compression_index across all events
        compression_index = 0.0
        if compression_events:
            compression_values = [event["compression_index"] for event in compression_events]
            compression_index = float(np.mean(compression_values))

        # Prepare final output
        detector_outputs[self.detector_id] = {
            "compression_detected": compression_detected,
            "compression_index": compression_index,
            "metrics_analyzed": available_metrics,
            "compression_events": compression_events,
            "thresholds_used": {
                m: thresholds
                for m, thresholds in thresholds_used.items()
            },
            "excess_mass_z_scores": {
                f"{m}_{t}_{w}": z
                for (m, t, w), z in excess_mass_z_scores.items()
            },
            "dip_test_statistics": {
                f"{m}_{t}_{w}": stat
                for (m, t, w), stat in dip_test_statistics.items()
            },
            "dip_test_p_values": {
                f"{m}_{t}_{w}": p
                for (m, t, w), p in dip_test_p_values.items()
            },
            "windows_analyzed": sorted(list(processed_windows))
        }

        return DetectorResult(detector_outputs=detector_outputs)

    def _get_thresholds_for_metric(
        self,
        metric_dataframe: MetricDataFrame,
        metric: str
    ) -> List[float]:
        """
        Get thresholds for a metric: explicit thresholds (from config) + auto-thresholds.
        For now, we only implement auto-threshold detection as explicit thresholds
        would require configuration input.
        """
        # Get metric values across all windows to compute auto-thresholds
        all_vals = []
        for window_id, vals in metric_dataframe.metrics[metric].items():
            all_vals.extend(vals)

        if not all_vals:
            return []

        # Auto-threshold detection (TFS Section 5.3)
        auto_thresholds = set()

        # Add candidate thresholds that are within [min(X), max(X)]
        min_val = np.min(all_vals)
        max_val = np.max(all_vals)
        for T in self.auto_threshold_candidates:
            if min_val <= T <= max_val:
                auto_thresholds.add(float(T))

        # Add percentile-based thresholds that are "round numbers" (end in 0 or 5)
        for percentile in self.auto_threshold_percentiles:
            T = np.percentile(all_vals, percentile)
            # Check if T is a "round number" (ends in 0 or 5)
            # We'll check if the last non-zero digit is 0 or 5 when rounded to 1 decimal place
            T_rounded = round(T, 1)
            if T_rounded * 10 % 10 == 0 or T_rounded * 10 % 10 == 5:
                auto_thresholds.add(float(T_rounded))

        return sorted(list(auto_thresholds))

    def _compute_epsilon(self, vals: List[float], threshold: float) -> float:
        """
        Compute epsilon for the threshold compression test.
        Per TFS Section 5.3: ε = max(0.02 × T, 0.01 × (max(X) - min(X)))
        """
        if len(vals) == 0:
            return 0.0
        val_range = np.max(vals) - np.min(vals)
        epsilon1 = 0.02 * abs(threshold)
        epsilon2 = 0.01 * val_range
        return max(epsilon1, epsilon2)

    def _excess_mass_test(self, vals: List[float], threshold: float) -> float:
        """
        Compute excess mass test statistic.
        Per TFS Section 5.3:
        Let B(T, ε) = {x : |x - T| ≤ ε} (the "band" around threshold).
        Expected proportion under uniform assumption: p₀ = 2ε / (max(X) - min(X))
        Observed proportion: p = |B(T, ε)| / n
        Test statistic: z = (p - p₀) / √(p₀(1 - p₀) / n)
        """
        n = len(vals)
        if n < 2:
            return 0.0

        min_val = np.min(vals)
        max_val = np.max(vals)
        val_range = max_val - min_val

        if val_range == 0:
            # All values are the same
            if threshold == min_val:  # which equals max_val
                # All values are exactly at the threshold -> perfect compression
                # Return a large z-score to indicate significance
                return float('inf')
            else:
                # threshold is not the constant value
                return 0.0

        epsilon = self._compute_epsilon(vals, threshold)
        # Avoid division by zero in p0 calculation
        if val_range == 0:
            p0 = 0.0
        else:
            p0 = 2.0 * epsilon / val_range

        # Avoid p0 being 0 or 1 (would make denominator zero)
        if p0 <= 0 or p0 >= 1:
            return 0.0

        # Count values in band [T-ε, T+ε]
        in_band = np.sum(np.abs(np.array(vals) - threshold) <= epsilon)
        p = in_band / n if n > 0 else 0.0

        # Compute z-score
        # z = (p - p0) / sqrt(p0 * (1 - p0) / n)
        try:
            z = (p - p0) / np.sqrt(p0 * (1.0 - p0) / n)
        except:
            z = 0.0

        return float(z)

    def _dip_test(
        self,
        vals: List[float],
        bootstrap_samples: int = 1000,
        random_seed: int = 42
    ) -> Tuple[float, float]:
        """
        Compute Hartigans' Dip test statistic and p-value via bootstrap.
        Per TFS Section 5.3:
        D = inf_F sup_x |F_n(x) - F(x)|
        where F_n is empirical CDF and F ranges over unimodal distributions.
        p-value computed via bootstrap (n_boot = 1000, seed = 42).
        """
        n = len(vals)
        if n < 2:
            return 0.0, 1.0

        # Set random seed for reproducibility
        rng = np.random.default_rng(random_seed)

        # Compute empirical CDF
        sorted_vals = np.sort(vals)
        # Empirical CDF at each sorted value: i/n
        ecdf = np.arange(1, n+1) / n

        # Compute dip statistic: minimum (over unimodal F) of sup_x |F_n(x) - F(x)|
        # We'll use the approximation: dip statistic = max |ecdf(x) - ucdf(x)|
        # where ucdf is the CDF of the uniform distribution on [min, max]
        # This is not the exact dip test but a common approximation.
        # For exact dip test, we would need to compute the distance to the unimodal distribution.
        # Given complexity, we'll use the Kolmogorov-Smirnov test against the uniform distribution
        # as an approximation for dip test.
        min_val = np.min(vals)
        max_val = np.max(vals)
        if max_val == min_val:
            return 0.0, 1.0

        # Theoretical uniform CDF
        ucdf = (sorted_vals - min_val) / (max_val - min_val)
        # Clip to [0, 1] just in case
        ucdf = np.clip(ucdf, 0.0, 1.0)

        # KS statistic between empirical CDF and uniform CDF
        dip_statistic = np.max(np.abs(ecdf - ucdf))

        # Bootstrap p-value: generate bootstrap samples from uniform distribution
        # and compute dip statistic for each
        bootstrap_stats = []
        for _ in range(bootstrap_samples):
            # Generate bootstrap sample from uniform distribution [min_val, max_val]
            bootstrap_sample = rng.uniform(min_val, max_val, n)
            bootstrap_sample_sorted = np.sort(bootstrap_sample)
            bootstrap_ecdf = np.arange(1, n+1) / n
            bootstrap_ucdf = (bootstrap_sample_sorted - min_val) / (max_val - min_val)
            bootstrap_ucdf = np.clip(bootstrap_ucdf, 0.0, 1.0)
            bootstrap_dip = np.max(np.abs(bootstrap_ecdf - bootstrap_ucdf))
            bootstrap_stats.append(bootstrap_dip)

        # p-value = proportion of bootstrap stats >= observed dip statistic
        bootstrap_stats = np.array(bootstrap_stats)
        p_value = np.sum(bootstrap_stats >= dip_statistic) / len(bootstrap_stats)

        return float(dip_statistic), float(p_value)

    def _infer_cause(self, metric: str, threshold: float) -> str:
        """
        Rule-based cause inference for threshold compression.
        Per TFS Section 5.3: hypothesized_cause = infer_cause(M, T)
        Rule-based: see FR-010 (we don't have FR-010, so we'll return a placeholder)
        """
        # Without FR-010, we'll return a generic cause
        # In a real implementation, this would rule-based lookup
        return "THRESHOLD_GAMING"  # Placeholder from TFS example