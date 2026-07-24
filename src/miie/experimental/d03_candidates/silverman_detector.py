"""
Silverman's Critical Bandwidth Test for Bimodality

Implements Silverman's test for multimodality using critical bandwidth analysis.
Complements GMM approach with non-parametric bimodality testing.

Mathematical Foundation:
- Critical bandwidth: h_crit = min{h : KDE(·, h) has ≤ k modes}
- Test statistic: T = h_crit / h₀ (ratio to default bandwidth)
- Bootstrap calibration for p-value computation

Reference:
- Silverman (1981) "Using kernel density estimates to investigate multimodality"
- Ameijeiras-Alonso et al. (2024) "critband: Critical Bandwidth Analysis"

Author: MIIE Research Team
Date: 2026-07-05
Status: EXPERIMENTAL - Not production-certified
"""

from typing import Any, Dict, Optional

import numpy as np
from scipy.stats import gaussian_kde


def _count_modes(density: np.ndarray) -> int:
    """
    Count local maxima (modes) in a density array.

    Args:
        density: Density values on a grid

    Returns:
        Number of modes
    """
    modes = 0
    for i in range(1, len(density) - 1):
        if density[i] > density[i - 1] and density[i] > density[i + 1]:
            modes += 1
    return modes


def _find_critical_bandwidth(data: np.ndarray, n_grid: int = 1000, n_iterations: int = 50) -> float:
    """
    Find critical bandwidth for bimodality using binary search.

    The critical bandwidth is the smallest bandwidth at which the KDE
    transitions from bimodal to unimodal.

    Args:
        data: Input data
        n_grid: Number of grid points for KDE evaluation
        n_iterations: Number of binary search iterations

    Returns:
        Critical bandwidth value
    """
    # Compute default bandwidth (Silverman's rule)
    sigma = np.std(data)
    iqr = np.percentile(data, 75) - np.percentile(data, 25)
    h_0 = 1.06 * min(sigma, iqr / 1.34) * len(data) ** (-0.2)

    # Grid for KDE evaluation
    x_grid = np.linspace(data.min() - 0.5, data.max() + 0.5, n_grid)

    def count_modes_at_bandwidth(h):
        """Count modes in KDE at given bandwidth."""
        # Convert bandwidth to bandwidth_factor for gaussian_kde
        bandwidth_factor = h / sigma
        kde = gaussian_kde(data, bw_method=bandwidth_factor)
        density = kde(x_grid)
        return _count_modes(density)

    # Binary search for critical bandwidth
    h_low, h_high = h_0 / 20, 10 * h_0

    for _ in range(n_iterations):
        h_mid = (h_low + h_high) / 2
        if count_modes_at_bandwidth(h_mid) <= 1:
            h_high = h_mid
        else:
            h_low = h_mid

    return h_high


def silverman_bimodality_test(
    data: np.ndarray, n_bootstrap: int = 1000, alpha: float = 0.05, random_state: Optional[int] = None
) -> Dict[str, Any]:
    """
    Test for bimodality using Silverman's critical bandwidth.

    Computes the critical bandwidth (smallest bandwidth for unimodal KDE)
    and compares to bootstrap calibration under unimodal null.

    Args:
        data: Input data (1D array)
        n_bootstrap: Number of bootstrap samples for calibration
        alpha: Significance level
        random_state: Random seed for reproducibility

    Returns:
        Dictionary with test results:
        - is_bimodal: bool
        - critical_bandwidth: h_crit (observed)
        - default_bandwidth: h_0 (Silverman's rule)
        - ratio: h_crit / h_0 (larger = more bimodal)
        - p_value: Bootstrap p-value

    Example:
        >>> # Bimodal data
        >>> np.random.seed(42)
        >>> data = np.concatenate([np.random.normal(0.3, 0.05, 100),
        ...                       np.random.normal(0.7, 0.05, 100)])
        >>> result = silverman_bimodality_test(data)
        >>> print(f"Bimodal: {result['is_bimodal']}, Ratio: {result['ratio']:.2f}")

        >>> # Unimodal data
        >>> data_uni = np.random.normal(0.5, 0.1, 200)
        >>> result = silverman_bimodality_test(data_uni)
        >>> print(f"Bimodal: {result['is_bimodal']}, Ratio: {result['ratio']:.2f}")
    """
    # Validate input
    data = np.asarray(data).flatten()
    if len(data) < 10:
        raise ValueError("Need at least 10 data points for Silverman's test")

    # Set random state for reproducibility
    rng = np.random.RandomState(random_state)

    # Compute default bandwidth (Silverman's rule)
    sigma = np.std(data)
    iqr = np.percentile(data, 75) - np.percentile(data, 25)
    h_0 = 1.06 * min(sigma, iqr / 1.34) * len(data) ** (-0.2)

    # Compute observed critical bandwidth
    h_crit = _find_critical_bandwidth(data)
    ratio = h_crit / h_0

    # Bootstrap calibration
    bootstrap_ratios = np.zeros(n_bootstrap)
    mean_data, std_data = np.mean(data), np.std(data)

    for i in range(n_bootstrap):
        # Generate from unimodal null (Gaussian)
        bootstrap_sample = rng.normal(mean_data, std_data, len(data))
        h_crit_b = _find_critical_bandwidth(bootstrap_sample)
        bootstrap_ratios[i] = h_crit_b / h_0

    # p-value
    p_value = np.mean(bootstrap_ratios >= ratio)
    is_bimodal = p_value < alpha

    return {
        "is_bimodal": is_bimodal,
        "critical_bandwidth": h_crit,
        "default_bandwidth": h_0,
        "ratio": ratio,
        "p_value": p_value,
        "bootstrap_mean_ratio": np.mean(bootstrap_ratios),
        "bootstrap_std_ratio": np.std(bootstrap_ratios),
    }


def silverman_compression_detector(
    windows: list, alpha: float = 0.05, n_bootstrap: int = 1000, random_state: Optional[int] = None
) -> dict:
    """
    Complete compression detector using Silverman's bimodality test.

    Tests each window for bimodality using Silverman's critical bandwidth.

    Args:
        windows: List of numpy arrays (each window's values)
        alpha: Significance level for compression detection
        n_bootstrap: Number of bootstrap samples
        random_state: Random seed for reproducibility

    Returns:
        Dictionary with compression detection results
    """
    if len(windows) < 2:
        raise ValueError("Need at least 2 windows for compression detection")

    results = {
        "n_windows": len(windows),
        "alpha": alpha,
        "n_bootstrap": n_bootstrap,
        "compression_detected": False,
        "window_results": [],
    }

    for i, window in enumerate(windows):
        test_result = silverman_bimodality_test(window, n_bootstrap, alpha, random_state)

        compression_detected = test_result["is_bimodal"]

        window_result = {
            "window_idx": i,
            "compression_detected": compression_detected,
            "ratio": test_result["ratio"],
            "p_value": test_result["p_value"],
        }
        results["window_results"].append(window_result)  # type: ignore

        if compression_detected:
            results["compression_detected"] = True

    return results


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    # Bimodal data
    data_bimodal = np.concatenate([np.random.normal(0.3, 0.05, 100), np.random.normal(0.7, 0.05, 100)])
    result = silverman_bimodality_test(data_bimodal, n_bootstrap=100)
    print(
        f"Bimodal data: is_bimodal={result['is_bimodal']}, " f"Ratio={result['ratio']:.2f}, p={result['p_value']:.4f}"
    )

    # Unimodal data
    data_unimodal = np.random.normal(0.5, 0.1, 200)
    result = silverman_bimodality_test(data_unimodal, n_bootstrap=100)
    print(
        f"\nUnimodal data: is_bimodal={result['is_bimodal']}, "
        f"Ratio={result['ratio']:.2f}, p={result['p_value']:.4f}"
    )
