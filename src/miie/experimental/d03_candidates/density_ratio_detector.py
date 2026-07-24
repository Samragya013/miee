"""
Density Ratio Estimation for Threshold Compression

Implements density ratio estimation for detecting threshold compression.
Measures concentration of probability mass near a threshold.

Mathematical Foundation:
- Density ratio: r(x) = p(x)/q(x) where p is data distribution, q is reference
- Compression detected if r(x) > 1 near threshold
- Bootstrap calibration for significance testing

Reference:
- Sugiyama et al. (2012) "Density Ratio Estimation: A New Machine Learning Tool"

Author: MIIE Research Team
Date: 2026-07-05
Status: EXPERIMENTAL - Not production-certified
"""

from typing import Any, Dict, Optional, Tuple

import numpy as np
from scipy.stats import gaussian_kde


def _estimate_density_ratio(
    data: np.ndarray, threshold: float, bandwidth: Optional[float] = None
) -> Tuple[float, float]:
    """
    Estimate density ratio at threshold.

    Args:
        data: Input data
        threshold: Point at which to estimate density ratio
        bandwidth: KDE bandwidth (if None, uses Silverman's rule)

    Returns:
        Tuple of (density_ratio, data_density)
    """
    # Compute bandwidth
    sigma = np.std(data)
    if bandwidth is None:
        iqr = np.percentile(data, 75) - np.percentile(data, 25)
        bandwidth = 1.06 * min(sigma, iqr / 1.34) * len(data) ** (-0.2)

    # Fit KDE to data
    kde = gaussian_kde(data, bw_method=bandwidth / sigma)

    # Estimate density at threshold
    data_density = float(kde(threshold))

    # Reference: uniform distribution over data range
    uniform_density = 1 / (data.max() - data.min())

    # Density ratio
    density_ratio = data_density / uniform_density

    return density_ratio, data_density


def density_ratio_test(
    data: np.ndarray,
    threshold: Optional[float] = None,
    bandwidth: Optional[float] = None,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    random_state: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Test for threshold compression using density ratio estimation.

    Estimates the density ratio at the threshold and compares to bootstrap
    calibration under uniform null.

    Args:
        data: Input data (1D array)
        threshold: Threshold value (if None, uses median)
        bandwidth: KDE bandwidth (if None, uses Silverman's rule)
        n_bootstrap: Number of bootstrap samples for calibration
        alpha: Significance level
        random_state: Random seed for reproducibility

    Returns:
        Dictionary with test results:
        - is_compressed: bool
        - density_ratio: Observed ratio at threshold
        - data_density: Data density at threshold
        - threshold: Threshold value used
        - p_value: Bootstrap p-value

    Example:
        >>> # Compressed data (concentrated near threshold)
        >>> np.random.seed(42)
        >>> data = np.concatenate([np.random.uniform(0, 0.4, 100),
        ...                       np.random.normal(0.5, 0.05, 50)])
        >>> result = density_ratio_test(data, threshold=0.5)
        >>> print(f"Compressed: {result['is_compressed']}, Ratio: {result['density_ratio']:.2f}")

        >>> # Uniform data
        >>> data_uni = np.random.uniform(0, 1, 150)
        >>> result = density_ratio_test(data_uni, threshold=0.5)
        >>> print(f"Compressed: {result['is_compressed']}, Ratio: {result['density_ratio']:.2f}")
    """
    # Validate input
    data = np.asarray(data).flatten()
    if len(data) < 10:
        raise ValueError("Need at least 10 data points for density ratio test")

    # Set random state for reproducibility
    rng = np.random.RandomState(random_state)

    # Default threshold: median
    if threshold is None:
        threshold = np.median(data)

    # Compute observed density ratio
    density_ratio, data_density = _estimate_density_ratio(data, threshold, bandwidth)

    # Bootstrap calibration
    bootstrap_ratios = np.zeros(n_bootstrap)
    data_min, data_max = data.min(), data.max()

    for i in range(n_bootstrap):
        # Generate from uniform null
        bootstrap_sample = rng.uniform(data_min, data_max, len(data))
        ratio_b, _ = _estimate_density_ratio(bootstrap_sample, threshold, bandwidth)
        bootstrap_ratios[i] = ratio_b

    # p-value
    p_value = np.mean(bootstrap_ratios >= density_ratio)
    is_compressed = p_value < alpha

    return {
        "is_compressed": is_compressed,
        "density_ratio": density_ratio,
        "data_density": data_density,
        "threshold": threshold,
        "p_value": p_value,
        "bootstrap_mean_ratio": np.mean(bootstrap_ratios),
        "bootstrap_std_ratio": np.std(bootstrap_ratios),
    }


def density_ratio_compression_detector(
    windows: list,
    threshold: Optional[float] = None,
    bandwidth: Optional[float] = None,
    alpha: float = 0.05,
    n_bootstrap: int = 1000,
    random_state: Optional[int] = None,
) -> dict:
    """
    Complete compression detector using density ratio estimation.

    Tests each window for threshold compression using density ratio.

    Args:
        windows: List of numpy arrays (each window's values)
        threshold: Threshold value (if None, uses median of each window)
        bandwidth: KDE bandwidth (if None, uses Silverman's rule)
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
        # Use provided threshold or median of this window
        window_threshold = threshold if threshold is not None else np.median(window)

        test_result = density_ratio_test(window, window_threshold, bandwidth, n_bootstrap, alpha, random_state)

        compression_detected = test_result["is_compressed"]

        window_result = {
            "window_idx": i,
            "compression_detected": compression_detected,
            "density_ratio": test_result["density_ratio"],
            "threshold": test_result["threshold"],
            "p_value": test_result["p_value"],
        }
        results["window_results"].append(window_result)  # type: ignore

        if compression_detected:
            results["compression_detected"] = True

    return results


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    # Compressed data
    data_compressed = np.concatenate([np.random.uniform(0, 0.4, 100), np.random.normal(0.5, 0.05, 50)])
    result = density_ratio_test(data_compressed, threshold=0.5, n_bootstrap=100)
    print(
        f"Compressed data: is_compressed={result['is_compressed']}, "
        f"Ratio={result['density_ratio']:.2f}, p={result['p_value']:.4f}"
    )

    # Uniform data
    data_uniform = np.random.uniform(0, 1, 150)
    result = density_ratio_test(data_uniform, threshold=0.5, n_bootstrap=100)
    print(
        f"\nUniform data: is_compressed={result['is_compressed']}, "
        f"Ratio={result['density_ratio']:.2f}, p={result['p_value']:.4f}"
    )
