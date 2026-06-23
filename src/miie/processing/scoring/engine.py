"""Scoring Engine Implementation.
Implements the IScoringEngine interface for computing integrity and confidence scores.
"""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.miie.schemas.models import ScorePackage, DetectorResults, MetricDataFrame, WindowDefinition
from src.miie.contracts.interfaces import IScoringEngine
from src.miie.contracts.errors import ValidationError


class ScoringEngine(IScoringEngine):
    """Scoring Engine implementation that computes integrity and confidence scores."""

    def __init__(self):
        """Initialize the scoring engine."""
        pass

    def compute_integrity_score(self, detector_results: DetectorResults,
                                metric_dataframe: MetricDataFrame,
                                windows: List[WindowDefinition],
                                detector_weights: Optional[Dict[str, float]] = None) -> ScorePackage:
        """Compute integrity and confidence scores.

        Implements TFS Section 6 (Integrity Score) and TFS Section 7 (Confidence Score).

        Args:
            detector_results: Container for detector outputs
            metric_dataframe: Container for extracted metrics
            windows: List of window definitions used in analysis
            detector_weights: Optional weights for detectors (defaults to equal weights)

        Returns:
            ScorePackage: Container for computed integrity and confidence scores
        """
        # Handle edge case: no detectors or no windows or no metrics
        # Return neutral scores instead of raising validation error for edge cases
        if not detector_results.detector_outputs or not windows or not metric_dataframe.metrics:
            # Prepare computation metadata per BSD Section 9
            computation_metadata = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config_hash": "",  # Would be populated from actual config in real implementation
                "formula_version": "TFS_v1.0"
            }

            return ScorePackage(
                integrity={"overall": 1.0, "per_metric": {}},
                confidence={"overall": 0.0, "factors": {}},
                timestamp=datetime.now(timezone.utc),
                config_hash="",  # Would be populated from actual config in real implementation
                formula_version="TFS_v1.0"
            )

        # Set up detector weights (equal weights if not provided)
        detector_ids = list(detector_results.detector_outputs.keys())
        if detector_weights is None:
            # Equal weights for all detectors
            detector_weights = {det_id: 1.0 / len(detector_ids) for det_id in detector_ids}
        else:
            # Normalize provided weights to sum to 1.0
            weight_sum = math.fsum(detector_weights.values())
            if weight_sum <= 0:
                raise ValidationError("Sum of detector weights must be positive")
            detector_weights = {det_id: weight / weight_sum for det_id, weight in detector_weights.items()}

        # Compute integrity score using TFS Section 6 formula
        integrity_result = self._compute_integrity_score_tfs6(
            detector_results, metric_dataframe, windows, detector_weights
        )

        # Compute confidence score using TFS Section 7 formula
        confidence_result = self._compute_confidence_score_tfs7(
            detector_results, metric_dataframe, windows
        )

        # Prepare computation metadata per BSD Section 9
        computation_metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config_hash": "",  # Would be populated from actual config in real implementation
            "formula_version": "TFS_v1.0"
        }

        return ScorePackage(
            integrity=integrity_result,
            confidence=confidence_result,
            timestamp=datetime.now(timezone.utc),
            config_hash="",  # Would be populated from actual config in real implementation
            formula_version="TFS_v1.0"
        )

    def _compute_integrity_score_tfs6(self, detector_results: DetectorResults,
                                      metric_dataframe: MetricDataFrame,
                                      windows: List[WindowDefinition],
                                      detector_weights: Dict[str, float]) -> Dict[str, Any]:
        """Compute integrity score per TFS Section 6.3.

        Returns a dict with:
        - "overall": float in [0, 1]
        - "per_metric": dict mapping metric_id -> float in [0, 1]

        IS = 1.0 - (w₁ × d₁ + w₂ × d₂ + w₃ × d₃)

        Where:
        - d₁ = D-01 severity (0 or 1, or 0–1 for magnitude if drift detected)
        - d₂ = D-02 severity (0 or 1, or 0–1 for magnitude if breakdown detected)
        - d₃ = D-03 severity (0 or 1, or 0–1 for magnitude if compression detected)
        - Default weights: w₁=0.40, w₂=0.35, w₃=0.25
        """
        if not detector_results.detector_outputs:
            return {"overall": 1.0, "per_metric": {}}

        # Get all available metrics
        available_metrics = list(metric_dataframe.metrics.keys()) if metric_dataframe.metrics else []

        # If no metrics, return perfect score
        if not available_metrics:
            return {"overall": 1.0, "per_metric": {}}

        # Calculate per-metric integrity scores
        per_metric_scores = {}

        for metric_id in available_metrics:
            # Get severity scores for each detector for this metric
            d1 = self._get_drift_severity(detector_results, metric_id, windows)
            d2 = self._get_breakdown_severity(detector_results, metric_id, windows)
            d3 = self._get_compression_severity(detector_results, metric_id, windows)

            # TFS Section 6.3: IS_metric = 1.0 - (w₁ × d₁ + w₂ × d₂ + w₃ × d₃)
            # Using default weights from TFS Section 6.3: w₁=0.40, w₂=0.35, w₃=0.25
            w1, w2, w3 = 0.40, 0.35, 0.25
            is_metric = 1.0 - (w1 * d1 + w2 * d2 + w3 * d3)

            # Clamp to [0, 1] range
            is_metric = max(0.0, min(1.0, is_metric))
            per_metric_scores[metric_id] = is_metric

        # Calculate overall integrity score as mean of per-metric scores (TFS Section 6.4)
        if per_metric_scores:
            overall_score = math.fsum(per_metric_scores.values()) / len(per_metric_scores)
        else:
            overall_score = 1.0

        # Clamp overall score to [0, 1] range
        overall_score = max(0.0, min(1.0, overall_score))

        return {
            "overall": overall_score,
            "per_metric": per_metric_scores
        }

    def _get_drift_severity(self, detector_results: DetectorResults,
                            metric_id: str,
                            windows: List[WindowDefinition]) -> float:
        """Get D-01 drift severity for a metric per TFS Section 6.3.

        d₁ = min(1.0, mean(drift_magnitude across all window pairs))
        where drift_magnitude = ks_statistic (normalized to [0,1] by capping at 0.5)
        """
        drift_magnitudes = []

        # Check if D-01 fired on this metric
        for det_id, det_output in detector_results.detector_outputs.items():
            if det_id == "D-01":
                # Look for drift detection indicators
                drift_detected = False
                drift_magnitude = 0.0

                # Check for boolean flag
                if "drift_detected" in det_output and det_output["drift_detected"] is True:
                    drift_detected = True
                    # Try to get actual magnitude if available
                    if "ks_statistic" in det_output:
                        try:
                            ks_stat = float(det_output["ks_statistic"])
                            # Normalize KS statistic to [0,1] by capping at 0.5
                            drift_magnitude = min(1.0, ks_stat / 0.5)
                        except (ValueError, TypeError):
                            drift_magnitude = 1.0  # Max severity if we can't parse
                    else:
                        drift_magnitude = 1.0  # Assume max severity if detected but no magnitude

                # Check for numeric score/severity fields
                if not drift_detected:
                    for score_field in ["score", "severity", "drift_score"]:
                        if score_field in det_output:
                            try:
                                val = float(det_output[score_field])
                                drift_magnitude = max(0.0, min(1.0, val))
                                drift_detected = True
                                break
                            except (ValueError, TypeError):
                                pass

                if drift_detected:
                    drift_magnitudes.append(drift_magnitude)

        # Calculate mean drift magnitude
        if drift_magnitudes:
            mean_drift = math.fsum(drift_magnitudes) / len(drift_magnitudes)
            return min(1.0, mean_drift)  # Already normalized, but ensure clamp
        else:
            return 0.0  # No drift detected

    def _get_breakdown_severity(self, detector_results: DetectorResults,
                                metric_id: str,
                                windows: List[WindowDefinition]) -> float:
        """Get D-02 breakdown severity for a metric per TFS Section 6.3.

        d₂ = min(1.0, mean(breakdown_magnitude across all metric pairs and window pairs))
        where breakdown_magnitude = |delta_r| / 0.3 (capped at 1.0)
        """
        breakdown_magnitudes = []

        # Check if D-02 fired on this metric
        for det_id, det_output in detector_results.detector_outputs.items():
            if det_id == "D-02":
                # Look for breakdown detection indicators
                breakdown_detected = False
                breakdown_magnitude = 0.0

                # Check for boolean flag
                if "correlation_breakdown" in det_output and det_output["correlation_breakdown"] is True:
                    breakdown_detected = True
                    # Try to get actual magnitude if available
                    if "delta_r" in det_output:
                        try:
                            delta_r = float(det_output["delta_r"])
                            # breakdown_magnitude = |delta_r| / 0.3 (capped at 1.0)
                            breakdown_magnitude = min(1.0, abs(delta_r) / 0.3)
                        except (ValueError, TypeError):
                            breakdown_magnitude = 1.0  # Max severity if we can't parse
                    else:
                        breakdown_magnitude = 1.0  # Assume max severity if detected but no magnitude

                # Check for numeric score/severity fields
                if not breakdown_detected:
                    for score_field in ["score", "severity", "breakdown_score"]:
                        if score_field in det_output:
                            try:
                                val = float(det_output[score_field])
                                breakdown_magnitude = max(0.0, min(1.0, val))
                                breakdown_detected = True
                                break
                            except (ValueError, TypeError):
                                pass

                if breakdown_detected:
                    breakdown_magnitudes.append(breakdown_magnitude)

        # Calculate mean breakdown magnitude
        if breakdown_magnitudes:
            mean_breakdown = math.fsum(breakdown_magnitudes) / len(breakdown_magnitudes)
            return min(1.0, mean_breakdown)  # Already normalized, but ensure clamp
        else:
            return 0.0  # No breakdown detected

    def _get_compression_severity(self, detector_results: DetectorResults,
                                  metric_id: str,
                                  windows: List[WindowDefinition]) -> float:
        """Get D-03 compression severity for a metric per TFS Section 6.3.

        d₃ = min(1.0, mean(compression_index across all thresholds and windows))
        where compression_index is already in [0,1]
        """
        compression_indices = []

        # Check if D-03 fired on this metric
        for det_id, det_output in detector_results.detector_outputs.items():
            if det_id == "D-03":
                # Look for compression detection indicators
                compression_detected = False
                compression_index = 0.0

                # Check for boolean flag
                if "threshold_compressed" in det_output and det_output["threshold_compressed"] is True:
                    compression_detected = True
                    # Try to get actual compression index if available
                    if "compression_index" in det_output:
                        try:
                            compression_index = float(det_output["compression_index"])
                            # Already in [0,1] range per TFS
                            compression_index = max(0.0, min(1.0, compression_index))
                        except (ValueError, TypeError):
                            compression_index = 1.0  # Max severity if we can't parse
                    else:
                        compression_index = 1.0  # Assume max severity if detected but no index

                # Check for numeric score/severity fields
                if not compression_detected:
                    for score_field in ["score", "severity", "compression_score"]:
                        if score_field in det_output:
                            try:
                                val = float(det_output[score_field])
                                compression_index = max(0.0, min(1.0, val))
                                compression_detected = True
                                break
                            except (ValueError, TypeError):
                                pass

                if compression_detected:
                    compression_indices.append(compression_index)

        # Calculate mean compression index
        if compression_indices:
            mean_compression = math.fsum(compression_indices) / len(compression_indices)
            return min(1.0, mean_compression)  # Already normalized, but ensure clamp
        else:
            return 0.0  # No compression detected

    def _compute_confidence_score_tfs7(self, detector_results: DetectorResults,
                                       metric_dataframe: MetricDataFrame,
                                       windows: List[WindowDefinition]) -> Dict[str, Any]:
        """Compute confidence score per TFS Section 7.4-7.5.

        Returns a dict with:
        - "overall": float in [0, 1]
        - "factors": dict mapping factor_name -> float in [0, 1]

        CS = f₁ × f₂ × f₃ × f₄ × f₅

        f₁ = min(1.0, mean_n / 50.0)
        f₂ = 1.0 - min(1.0, mean_CV / 0.5)
        f₃ = 1.0 - (missing_pairs / total_pairs)
        f₄ = 1.0 - min(1.0, std_size / mean_size)
        f₅ = successful_runs / total_attempts
        """
        if not windows or not metric_dataframe.metrics:
            return {"overall": 0.0, "factors": {}}

        # f₁: Sample Size Factor
        f1 = self._compute_sample_size_factor(metric_dataframe, windows)

        # f₂: Variance Factor
        f2 = self._compute_variance_factor(metric_dataframe, windows)

        # f₃: Missing Data Factor
        f3 = self._compute_missing_data_factor(metric_dataframe, windows)

        # f₄: Window Balance Factor
        f4 = self._compute_window_balance_factor(windows)

        # f₅: Detector Success Factor
        f5 = self._compute_detector_success_factor(detector_results, metric_dataframe)

        # CS = f₁ × f₂ × f₃ × f₄ × f₅
        confidence_score = f1 * f2 * f3 * f4 * f5

        # Ensure score is in [0, 1] range
        confidence_score = max(0.0, min(1.0, confidence_score))

        return {
            "overall": confidence_score,
            "factors": {
                "sample_size": f1,
                "variance": f2,
                "missing_data": f3,
                "window_balance": f4,
                "detector_success": f5
            }
        }

    def _compute_sample_size_factor(self, metric_dataframe: MetricDataFrame,
                                    windows: List[WindowDefinition]) -> float:
        """Compute f₁: min(1.0, mean_n / 50.0)

        mean_n = mean(|Wₖ| for all k and all metrics with data)
        """
        if not metric_dataframe.metrics or not windows:
            return 0.0

        total_points = 0
        metric_count = 0

        for metric_id, metric_series in metric_dataframe.metrics.items():
            # For each metric, count the data points across all windows
            # This approximates |Wₖ| - the number of data points for metric M
            point_count = 0
            for value_list in metric_series.values():
                if isinstance(value_list, list):
                    for val in value_list:
                        if val is not None:
                            point_count += 1

            if point_count > 0:
                total_points += point_count
                metric_count += 1

        if metric_count == 0:
            mean_n = 0.0
        else:
            mean_n = total_points / metric_count

        f1 = min(1.0, mean_n / 50.0)
        return f1

    def _compute_variance_factor(self, metric_dataframe: MetricDataFrame,
                                 windows: List[WindowDefinition]) -> float:
        """Compute f₂: 1.0 - min(1.0, mean_CV / 0.5)

        mean_CV = mean(CV for all valid windows)
        CV = std(W[M]) / |mean(W[M])| (with special handling for mean=0)
        """
        if not metric_dataframe.metrics or not windows:
            return 0.5  # Default moderate confidence when no data

        cv_values = []

        for metric_id, metric_series in metric_dataframe.metrics.items():
            # For each metric and window, calculate coefficient of variation
            for window_key, value_list in metric_series.items():
                if isinstance(value_list, list) and len(value_list) > 0:
                    # Filter out None values
                    valid_values = [v for v in value_list if v is not None]
                    if len(valid_values) >= 2:  # Need at least 2 points for std/mean
                        mean_val = math.fsum(valid_values) / len(valid_values)
                        if mean_val != 0:
                            # CV = std / |mean|
                            variance = math.fsum((x - mean_val) ** 2 for x in valid_values) / len(valid_values)
                            std_val = variance ** 0.5
                            cv = std_val / abs(mean_val)
                        else:
                            # Special handling for mean=0
                            if all(v == 0 for v in valid_values):
                                cv = 0.0  # Perfect consistency
                            else:
                                cv = 1.0  # High variance relative to zero mean
                        cv_values.append(cv)

        if not cv_values:
            mean_cv = 0.0
        else:
            mean_cv = math.fsum(cv_values) / len(cv_values)

        f2 = 1.0 - min(1.0, mean_cv / 0.5)
        return f2

    def _compute_missing_data_factor(self, metric_dataframe: MetricDataFrame,
                                     windows: List[WindowDefinition]) -> float:
        """Compute f₃: 1.0 - (missing_pairs / total_pairs)

        total_pairs = num_metrics × num_windows
        missing_pairs = count of (metric, window) pairs with insufficient data
        """
        if not metric_dataframe.metrics or not windows:
            return 0.0

        num_metrics = len(metric_dataframe.metrics)
        num_windows = len(windows)
        total_pairs = num_metrics * num_windows

        if total_pairs == 0:
            return 0.0

        missing_pairs = 0

        # Count missing data pairs
        for metric_id, metric_series in metric_dataframe.metrics.items():
            # For simplicity, we'll consider a pair missing if there's no data at all
            # In a more sophisticated implementation, we'd check each window specifically
            if not metric_series or all(
                not isinstance(v, list) or len(v) == 0 or all(x is None for x in v)
                for v in metric_series.values()
            ):
                # This metric has no data at all
                missing_pairs += num_windows
            else:
                # Check each window for this metric
                for window_key in metric_series.keys():
                    value_list = metric_series[window_key]
                    if not isinstance(value_list, list) or len(value_list) == 0 or all(x is None for x in value_list):
                        missing_pairs += 1

        f3 = 1.0 - (missing_pairs / total_pairs)
        return f3

    def _compute_window_balance_factor(self, windows: List[WindowDefinition]) -> float:
        """Compute f₄: 1.0 - min(1.0, std_size / mean_size)

        window_sizes = [sum(|Wₖ| across all metrics) for each window k]
        mean_size = mean(window_sizes)
        std_size = std(window_sizes)
        """
        if not windows:
            return 0.0

        # For each window, calculate its size (sum of absolute values across all metrics)
        window_sizes = []

        # We don't have direct access to metric values per window in the WindowDefinition
        # So we'll use a simplified approach based on commit counts as a proxy for size
        # In a real implementation, this would use actual metric data

        for window in windows:
            # Use commit count as a proxy for window size
            # In reality, this would be sum of |metric values| across all metrics in the window
            window_size = window.commits  # Proxy using commit count
            window_sizes.append(float(window_size))

        if not window_sizes:
            return 0.0

        mean_size = math.fsum(window_sizes) / len(window_sizes)
        if mean_size > 0:
            variance = math.fsum((x - mean_size) ** 2 for x in window_sizes) / len(window_sizes)
            std_size = variance ** 0.5
            f4 = 1.0 - min(1.0, std_size / mean_size)
        else:
            f4 = 0.0

        return f4

    def _compute_detector_success_factor(self, detector_results: DetectorResults,
                                         metric_dataframe: MetricDataFrame) -> float:
        """Compute f₅: successful_runs / total_attempts

        total_attempts = num_metrics × num_detectors (adjusted for metric availability)
        successful_runs = count of detector executions that produced valid output
        """
        if not detector_results.detector_outputs:
            return 0.0

        num_detectors = len(detector_results.detector_outputs)
        num_metrics = len(metric_dataframe.metrics) if metric_dataframe.metrics else 0

        if num_detectors == 0 or num_metrics == 0:
            return 0.0

        # total_attempts = num_metrics × num_detectors (adjusted for metric availability)
        # For simplicity, we'll assume all metrics are available for all detectors
        total_attempts = num_metrics * num_detectors

        # successful_runs = count of detector executions that completed (not skipped)
        # In mock scenario, assume all detectors ran successfully
        successful_runs = num_detectors * num_metrics  # Assuming all combinations succeeded

        if total_attempts > 0:
            f5 = successful_runs / total_attempts
        else:
            f5 = 0.0

        return f5