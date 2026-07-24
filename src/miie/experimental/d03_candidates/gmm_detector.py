"""
Gaussian Mixture Model (GMM) Bimodality Test

Implements GMM-based bimodality detection using BIC for model selection.
Directly addresses the GT-SYN-THRESH-005 (bimodal) failure mode identified in PR-17.

Mathematical Foundation:
- GMM: p(x) = Σₖ πₖ · N(x | μₖ, σₖ²)
- BIC: BIC = -2 ln(L) + k ln(n)
- Decision: Bimodal if BIC(K=1) - BIC(K=2) > threshold

Reference:
- McLachlan & Peel (2000) "Finite Mixture Models"
- Tu et al. (2024) "Change point detection via Gaussian mixture model"

Author: MIIE Research Team
Date: 2026-07-05
Status: EXPERIMENTAL - Not production-certified
"""

from typing import Any, Dict, Optional

import numpy as np
from sklearn.mixture import GaussianMixture


def gmm_bimodality_test(
    data: np.ndarray, threshold_bic_diff: float = 10.0, n_restarts: int = 5, random_state: Optional[int] = None
) -> Dict[str, Any]:
    """
    Test for bimodality using Gaussian Mixture Models with BIC.

    Fits GMMs with K=1 (unimodal) and K=2 (bimodal) and compares BIC values.
    If BIC difference exceeds threshold, data is classified as bimodal.

    Args:
        data: Input data (1D array)
        threshold_bic_diff: Minimum BIC difference to classify as bimodal
                           (BIC_1 - BIC_2 > threshold → bimodal)
        n_restarts: Number of EM restarts for GMM fitting
        random_state: Random seed for reproducibility

    Returns:
        Dictionary with test results:
        - is_bimodal: bool
        - bic_unimodal: BIC for K=1 model
        - bic_bimodal: BIC for K=2 model
        - bic_diff: bic_unimodal - bic_bimodal (positive favors bimodal)
        - components: GMM parameters if bimodal (means, variances, weights)
        - log_likelihood_unimodal: Log-likelihood for K=1
        - log_likelihood_bimodal: Log-likelihood for K=2

    Example:
        >>> # Bimodal data
        >>> np.random.seed(42)
        >>> data = np.concatenate([np.random.normal(0.3, 0.05, 100),
        ...                       np.random.normal(0.7, 0.05, 100)])
        >>> result = gmm_bimodality_test(data)
        >>> print(f"Bimodal: {result['is_bimodal']}, BIC diff: {result['bic_diff']:.2f}")

        >>> # Unimodal data
        >>> data_uni = np.random.normal(0.5, 0.1, 200)
        >>> result = gmm_bimodality_test(data_uni)
        >>> print(f"Bimodal: {result['is_bimodal']}, BIC diff: {result['bic_diff']:.2f}")
    """
    # Validate input
    data = np.asarray(data).flatten()
    if len(data) < 10:
        raise ValueError("Need at least 10 data points for GMM fitting")

    # Reshape for sklearn
    X = data.reshape(-1, 1)

    # Fit GMM with K=1 (unimodal)
    gmm1 = GaussianMixture(n_components=1, n_init=n_restarts, random_state=random_state)
    gmm1.fit(X)
    bic1 = gmm1.bic(X)
    ll1 = gmm1.score(X) * len(data)  # Log-likelihood

    # Fit GMM with K=2 (bimodal)
    gmm2 = GaussianMixture(n_components=2, n_init=n_restarts, random_state=random_state)
    gmm2.fit(X)
    bic2 = gmm2.bic(X)
    ll2 = gmm2.score(X) * len(data)  # Log-likelihood

    # BIC comparison
    bic_diff = bic1 - bic2  # Positive favors bimodal
    is_bimodal = bic_diff > threshold_bic_diff

    # Extract components if bimodal
    components = None
    if is_bimodal:
        # Sort components by weight (descending)
        sort_idx = np.argsort(gmm2.weights_)[::-1]
        components = {
            "means": gmm2.means_.flatten()[sort_idx],
            "variances": gmm2.covariances_.flatten()[sort_idx],
            "weights": gmm2.weights_[sort_idx],
        }

    return {
        "is_bimodal": is_bimodal,
        "bic_unimodal": bic1,
        "bic_bimodal": bic2,
        "bic_diff": bic_diff,
        "components": components,
        "log_likelihood_unimodal": ll1,
        "log_likelihood_bimodal": ll2,
    }


def gmm_compression_detector(
    windows: list,
    alpha: float = 0.05,
    threshold_bic_diff: float = 10.0,
    n_restarts: int = 5,
    random_state: Optional[int] = None,
) -> dict:
    """
    Complete compression detector using GMM bimodality test.

    Tests each window for bimodality and detects threshold compression
    when bimodal components are near the threshold.

    Args:
        windows: List of numpy arrays (each window's values)
        alpha: Significance level for compression detection
        threshold_bic_diff: Minimum BIC difference for bimodality
        n_restarts: Number of EM restarts
        random_state: Random seed for reproducibility

    Returns:
        Dictionary with compression detection results
    """
    if len(windows) < 2:
        raise ValueError("Need at least 2 windows for compression detection")

    results = {
        "n_windows": len(windows),
        "alpha": alpha,
        "threshold_bic_diff": threshold_bic_diff,
        "compression_detected": False,
        "window_results": [],
    }

    for i, window in enumerate(windows):
        test_result = gmm_bimodality_test(window, threshold_bic_diff, n_restarts, random_state)

        compression_detected = test_result["is_bimodal"]

        window_result = {
            "window_idx": i,
            "compression_detected": compression_detected,
            "bic_diff": test_result["bic_diff"],
            "components": test_result["components"],
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
    result = gmm_bimodality_test(data_bimodal)
    print(f"Bimodal data: is_bimodal={result['is_bimodal']}, " f"BIC diff={result['bic_diff']:.2f}")
    if result["components"]:
        print(f"  Means: {result['components']['means']}")
        print(f"  Weights: {result['components']['weights']}")

    # Unimodal data
    data_unimodal = np.random.normal(0.5, 0.1, 200)
    result = gmm_bimodality_test(data_unimodal)
    print(f"\nUnimodal data: is_bimodal={result['is_bimodal']}, " f"BIC diff={result['bic_diff']:.2f}")
