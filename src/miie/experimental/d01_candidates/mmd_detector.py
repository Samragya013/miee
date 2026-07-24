"""
Maximum Mean Discrepancy (MMD) Two-Sample Test

Implements MMD with Gaussian RBF kernel for distribution drift detection
with permutation-based p-value computation.

Mathematical Foundation:
- MMD²(P, Q) = ‖μₚ - μᵧ‖²_H where μₚ = E[k(·, X)]
- Gaussian RBF kernel: k(x,y) = exp(-‖x-y‖²/(2σ²))
- Bandwidth selection via median heuristic
- Permutation test provides exact Type I error control

Reference:
- Gretton et al. (2012) "A kernel two-sample test"
- Jitkrittum et al. (2017) "A flexible test of two sample quality"

Author: MIIE Research Team
Date: 2026-07-05
Status: EXPERIMENTAL - Not production-certified
"""

from typing import Optional, Tuple

import numpy as np


def _rbf_kernel(x: np.ndarray, y: np.ndarray, sigma: float) -> float:
    """
    Gaussian RBF kernel.

    Args:
        x: First point
        y: Second point
        sigma: Kernel bandwidth

    Returns:
        Kernel value
    """
    return np.exp(-np.sum((x - y) ** 2) / (2 * sigma**2))


def _compute_mmd(s1: np.ndarray, s2: np.ndarray, sigma: float) -> float:
    """
    Compute MMD² statistic with Gaussian RBF kernel.

    Args:
        s1: First sample
        s2: Second sample
        sigma: Kernel bandwidth

    Returns:
        MMD² value
    """
    n, m = len(s1), len(s2)

    # Kernel matrices
    K_ss = np.array([[_rbf_kernel(s1[i], s1[j], sigma) for j in range(n)] for i in range(n)])
    K_tt = np.array([[_rbf_kernel(s2[i], s2[j], sigma) for j in range(m)] for i in range(m)])
    K_st = np.array([[_rbf_kernel(s1[i], s2[j], sigma) for j in range(m)] for i in range(n)])

    # MMD² unbiased estimator
    # Note: Due to numerical precision, the unbiased estimator can be slightly negative.
    # We clamp to 0 to ensure valid non-negative MMD² values.
    mmd2 = (
        (np.sum(K_ss) - np.trace(K_ss)) / (n * (n - 1))
        + (np.sum(K_tt) - np.trace(K_tt)) / (m * (m - 1))
        - 2 * np.mean(K_st)
    )

    return max(0.0, mmd2)


def _median_heuristic(data: np.ndarray) -> float:
    """
    Compute bandwidth using median heuristic.

    Args:
        data: Concatenated samples

    Returns:
        Bandwidth value
    """
    pairwise_dists = np.abs(np.subtract.outer(data, data))
    return np.median(pairwise_dists[pairwise_dists > 0])


def mmd_two_sample_test(
    sample1: np.ndarray,
    sample2: np.ndarray,
    sigma: Optional[float] = None,
    n_permutations: int = 1000,
    random_state: Optional[int] = None,
) -> Tuple[float, float]:
    """
    Two-sample test using Maximum Mean Discrepancy with permutation p-value.

    This test determines whether two samples come from the same distribution
    by comparing the observed MMD² to its null distribution estimated via
    permutation testing.

    Args:
        sample1: First sample (window 1 values)
        sample2: Second sample (window 2 values)
        sigma: Kernel bandwidth (if None, uses median heuristic)
        n_permutations: Number of permutations for p-value computation
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (mmd_squared, p_value)
        - mmd_squared: Observed MMD² between samples
        - p_value: Permutation-based p-value (H₀: samples from same distribution)

    Example:
        >>> # Two windows from same distribution
        >>> np.random.seed(42)
        >>> w1 = np.random.normal(50, 10, 30)
        >>> w2 = np.random.normal(50, 10, 30)
        >>> mmd2, p = mmd_two_sample_test(w1, w2)
        >>> print(f"MMD²: {mmd2:.4f}, p-value: {p:.4f}")

        >>> # Two windows from different distributions
        >>> w3 = np.random.normal(60, 10, 30)  # Shifted mean
        >>> mmd2, p = mmd_two_sample_test(w1, w3)
        >>> print(f"MMD²: {mmd2:.4f}, p-value: {p:.4f}")
    """
    # Validate inputs
    sample1 = np.asarray(sample1).flatten()
    sample2 = np.asarray(sample2).flatten()

    if len(sample1) == 0 or len(sample2) == 0:
        raise ValueError("Samples cannot be empty")

    # Set random state for reproducibility
    rng = np.random.RandomState(random_state)

    # Bandwidth selection
    if sigma is None:
        pooled = np.concatenate([sample1, sample2])
        sigma = _median_heuristic(pooled)

    # Compute observed MMD²
    observed_mmd2 = _compute_mmd(sample1, sample2, sigma)

    # Permutation test
    pooled = np.concatenate([sample1, sample2])
    n1 = len(sample1)

    perm_mmd2 = np.zeros(n_permutations)
    for i in range(n_permutations):
        perm = rng.permutation(pooled)
        perm_mmd2[i] = _compute_mmd(perm[:n1], perm[n1:], sigma)

    # p-value: proportion of permuted MMD² >= observed
    p_value = np.mean(perm_mmd2 >= observed_mmd2)

    return observed_mmd2, p_value


def mmd_drift_detector(
    windows: list,
    alpha: float = 0.05,
    sigma: Optional[float] = None,
    n_permutations: int = 1000,
    random_state: Optional[int] = None,
) -> dict:
    """
    Complete drift detector using MMD.

    Compares each window to the first (reference) window and returns
    drift detection results.

    Args:
        windows: List of numpy arrays (each window's values)
        alpha: Significance level for drift detection
        sigma: Kernel bandwidth (if None, uses median heuristic)
        n_permutations: Number of permutations for p-value
        random_state: Random seed for reproducibility

    Returns:
        Dictionary with drift detection results
    """
    if len(windows) < 2:
        raise ValueError("Need at least 2 windows for drift detection")

    reference_window = windows[0]
    results = {
        "reference_window_idx": 0,
        "n_windows": len(windows),
        "alpha": alpha,
        "sigma": sigma,
        "n_permutations": n_permutations,
        "drift_detected": False,
        "window_results": [],
    }

    for i, window in enumerate(windows[1:], start=1):
        mmd2, p_value = mmd_two_sample_test(reference_window, window, sigma, n_permutations, random_state)

        drift_detected = p_value < alpha

        window_result = {"window_idx": i, "mmd_squared": mmd2, "p_value": p_value, "drift_detected": drift_detected}
        results["window_results"].append(window_result)

        if drift_detected:
            results["drift_detected"] = True

    return results


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    # Same distribution
    w1 = np.random.normal(50, 10, 30)
    w2 = np.random.normal(50, 10, 30)
    mmd2, p = mmd_two_sample_test(w1, w2)
    print(f"Same distribution: MMD²={mmd2:.4f}, p={p:.4f}")

    # Different distributions
    w3 = np.random.normal(60, 10, 30)
    mmd2, p = mmd_two_sample_test(w1, w3)
    print(f"Different distributions: MMD²={mmd2:.4f}, p={p:.4f}")
