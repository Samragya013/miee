"""
Wasserstein Distance Two-Sample Test

Implements the Wasserstein-1 distance (Earth Mover's Distance) for distribution
drift detection with permutation-based p-value computation.

Mathematical Foundation:
- Wasserstein-1 distance: W₁(P, Q) = inf_{γ ∈ Γ(P,Q)} ∫∫ |x - y| dγ(x, y)
- For 1D samples: W₁(Pₙ, Qₙ) = (1/n) Σᵢ |Fₙ⁻¹(i/n) - Gₙ⁻¹(i/n)|
- Permutation test provides exact Type I error control

Reference:
- Ramdas et al. (2017) "Wasserstein Statistical Testing"
- Hu & Lin (2025) "Two-sample distribution tests via max-sliced Wasserstein distance"

Author: MIIE Research Team
Date: 2026-07-05
Status: EXPERIMENTAL - Not production-certified
"""

from typing import Optional, Tuple

import numpy as np
from scipy.stats import wasserstein_distance


def wasserstein_two_sample_test(
    sample1: np.ndarray, sample2: np.ndarray, n_permutations: int = 1000, random_state: Optional[int] = None
) -> Tuple[float, float]:
    """
    Two-sample test using Wasserstein distance with permutation p-value.

    This test determines whether two samples come from the same distribution
    by comparing the observed Wasserstein distance to its null distribution
    estimated via permutation testing.

    Args:
        sample1: First sample (window 1 values)
        sample2: Second sample (window 2 values)
        n_permutations: Number of permutations for p-value computation
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (wasserstein_distance, p_value)
        - wasserstein_distance: Observed Wasserstein-1 distance between samples
        - p_value: Permutation-based p-value (H₀: samples from same distribution)

    Example:
        >>> # Two windows from same distribution
        >>> np.random.seed(42)
        >>> w1 = np.random.normal(50, 10, 30)
        >>> w2 = np.random.normal(50, 10, 30)
        >>> dist, p = wasserstein_two_sample_test(w1, w2)
        >>> print(f"Distance: {dist:.4f}, p-value: {p:.4f}")

        >>> # Two windows from different distributions
        >>> w3 = np.random.normal(60, 10, 30)  # Shifted mean
        >>> dist, p = wasserstein_two_sample_test(w1, w3)
        >>> print(f"Distance: {dist:.4f}, p-value: {p:.4f}")
    """
    # Validate inputs
    sample1 = np.asarray(sample1).flatten()
    sample2 = np.asarray(sample2).flatten()

    if len(sample1) == 0 or len(sample2) == 0:
        raise ValueError("Samples cannot be empty")

    # Set random state for reproducibility
    rng = np.random.RandomState(random_state)

    # Compute observed Wasserstein distance
    observed_distance = wasserstein_distance(sample1, sample2)

    # Permutation test
    pooled = np.concatenate([sample1, sample2])
    n1 = len(sample1)

    perm_distances = np.zeros(n_permutations)
    for i in range(n_permutations):
        perm = rng.permutation(pooled)
        perm_distances[i] = wasserstein_distance(perm[:n1], perm[n1:])

    # p-value: proportion of permuted distances >= observed
    p_value = np.mean(perm_distances >= observed_distance)

    return observed_distance, p_value


def wasserstein_drift_detector(
    windows: list, alpha: float = 0.05, n_permutations: int = 1000, random_state: Optional[int] = None
) -> dict:
    """
    Complete drift detector using Wasserstein distance.

    Compares each window to the first (reference) window and returns
    drift detection results.

    Args:
        windows: List of numpy arrays (each window's values)
        alpha: Significance level for drift detection
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
        "n_permutations": n_permutations,
        "drift_detected": False,
        "window_results": [],
    }

    for i, window in enumerate(windows[1:], start=1):
        dist, p_value = wasserstein_two_sample_test(reference_window, window, n_permutations, random_state)

        drift_detected = p_value < alpha

        window_result = {
            "window_idx": i,
            "wasserstein_distance": dist,
            "p_value": p_value,
            "drift_detected": drift_detected,
        }
        results["window_results"].append(window_result)  # type: ignore

        if drift_detected:
            results["drift_detected"] = True

    return results


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    # Same distribution
    w1 = np.random.normal(50, 10, 30)
    w2 = np.random.normal(50, 10, 30)
    dist, p = wasserstein_two_sample_test(w1, w2)
    print(f"Same distribution: Distance={dist:.4f}, p={p:.4f}")

    # Different distributions
    w3 = np.random.normal(60, 10, 30)
    dist, p = wasserstein_two_sample_test(w1, w3)
    print(f"Different distributions: Distance={dist:.4f}, p={p:.4f}")
