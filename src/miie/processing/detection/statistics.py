"""
Shared statistical utilities for MIIE v1.5 detectors.

Implements the reusable statistical functions defined in DES v2.0 §25.
Each function is a pure computation with no detector-specific state.

Extended in v1.6 with z_to_p() and fisher_z_test() for PR-16A
multiple-testing correction support.

Reference: DES-v2.0 §25, DSVP-v1.0, PR-16A
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

import numpy as np
from scipy.stats import rankdata

# ---------------------------------------------------------------------------
# Distribution comparison (D-01)
# ---------------------------------------------------------------------------


def ks_2samp(data1: List[float], data2: List[float]) -> Tuple[float, float]:
    """Kolmogorov-Smirnov two-sample test statistic and asymptotic p-value.

    Computes the maximum absolute difference between the empirical CDFs
    of two samples, and approximates the p-value using the asymptotic
    formula: p = 2 * exp(-2 * ks^2 * n_eff).

    Args:
        data1: First sample.
        data2: Second sample.

    Returns:
        Tuple of (ks_statistic, ks_p_value), both in [0, 1].
    """
    n1 = len(data1)
    n2 = len(data2)
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0

    from scipy.stats import ks_2samp as scipy_ks_2samp

    if n1 < 30 or n2 < 30:
        result = scipy_ks_2samp(data1, data2)
        return float(result.statistic), float(result.pvalue)

    data1_sorted = np.sort(data1)
    data2_sorted = np.sort(data2)

    all_values = np.unique(np.concatenate([data1_sorted, data2_sorted]))

    cdf1 = np.searchsorted(data1_sorted, all_values, side="right") / n1
    cdf2 = np.searchsorted(data2_sorted, all_values, side="right") / n2

    ks_statistic = float(np.max(np.abs(cdf1 - cdf2)))

    n_eff = (n1 * n2) / (n1 + n2)
    if n_eff > 0:
        ks_p_value = 2 * math.exp(-2 * ks_statistic**2 * n_eff)
        ks_p_value = max(0.0, min(1.0, ks_p_value))
    else:
        ks_p_value = 1.0

    return ks_statistic, ks_p_value


def compute_psi(expected: List[float], actual: List[float], n_bins: int = 10) -> float:
    """Population Stability Index between two distributions.

    Uses n_bins equal-width bins over the combined range of both samples.
    PSI = sum((actual_prop - expected_prop) * ln(actual_prop / expected_prop)).

    Args:
        expected: Expected (reference) distribution.
        actual: Actual (test) distribution.
        n_bins: Number of bins (default 10 per DES §21.2).

    Returns:
        PSI value. Values > 0.25 indicate significant drift (DES §21.2).
    """
    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    combined = np.concatenate([expected, actual])
    min_val = float(np.min(combined))
    max_val = float(np.max(combined))

    if min_val == max_val:
        return 0.0

    bins = np.linspace(min_val, max_val, n_bins + 1)

    expected_hist, _ = np.histogram(expected, bins=bins, density=False)
    actual_hist, _ = np.histogram(actual, bins=bins, density=False)

    expected_prop = expected_hist / len(expected)
    actual_prop = actual_hist / len(actual)

    epsilon = 1e-10
    expected_prop = np.where(expected_prop == 0, epsilon, expected_prop)
    actual_prop = np.where(actual_prop == 0, epsilon, actual_prop)

    psi = float(np.sum((actual_prop - expected_prop) * np.log(actual_prop / expected_prop)))
    return psi


# ---------------------------------------------------------------------------
# Correlation (D-02)
# ---------------------------------------------------------------------------


def pearson_r(x: List[float], y: List[float]) -> float:
    """Pearson product-moment correlation coefficient.

    Args:
        x: First variable.
        y: Second variable (same length as x).

    Returns:
        Correlation coefficient in [-1, 1]. Returns 0.0 if undefined.
    """
    n = min(len(x), len(y))
    if n < 2:
        return 0.0

    x_arr = np.array(x[:n], dtype=float)
    y_arr = np.array(y[:n], dtype=float)

    r = float(np.corrcoef(x_arr, y_arr)[0, 1])
    return 0.0 if math.isnan(r) else r


def spearman_rho(x: List[float], y: List[float]) -> float:
    """Spearman rank-order correlation coefficient.

    Computes Pearson correlation on rank-transformed data using
    average ranks for ties.

    Args:
        x: First variable.
        y: Second variable (same length as x).

    Returns:
        Rank correlation coefficient in [-1, 1]. Returns 0.0 if undefined.
    """
    n = min(len(x), len(y))
    if n < 2:
        return 0.0

    try:
        x_ranked = rankdata(x[:n], method="average")
        y_ranked = rankdata(y[:n], method="average")
        rho = float(np.corrcoef(x_ranked, y_ranked)[0, 1])
        return 0.0 if math.isnan(rho) else rho
    except Exception:
        return 0.0


def fisher_z(r: float) -> float:
    """Fisher z-transform: z = 0.5 * ln((1+r)/(1-r)).

    Args:
        r: Correlation coefficient in (-1, 1).

    Returns:
        Transformed value on the real line.
    """
    clamped = max(-1.0 + 1e-10, min(1.0 - 1e-10, r))
    return 0.5 * math.log((1 + clamped) / (1 - clamped))


def fisher_z_inverse(z: float) -> float:
    """Inverse Fisher z-transform: r = tanh(z).

    Args:
        z: z-transformed value.

    Returns:
        Correlation coefficient in (-1, 1).
    """
    return math.tanh(z)


def fisher_z_ci(r: float, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Fisher z-based confidence interval for a correlation coefficient.

    Args:
        r: Observed correlation.
        n: Sample size.
        confidence: Confidence level (default 0.95 for 95% CI).

    Returns:
        Tuple of (lower, upper) bounds on the r scale.
    """
    if n < 4:
        return (0.0, 0.0)

    from scipy.stats import norm

    z_r = fisher_z(r)
    se = 1.0 / math.sqrt(n - 3)
    z_crit = norm.ppf(1 - (1 - confidence) / 2)
    z_lower = z_r - z_crit * se
    z_upper = z_r + z_crit * se
    return (fisher_z_inverse(z_lower), fisher_z_inverse(z_upper))


# ---------------------------------------------------------------------------
# Threshold detection (D-03)
# ---------------------------------------------------------------------------


def excess_mass_test(vals: List[float], threshold: float, epsilon: float) -> float:
    """Excess Mass z-test for threshold compression.

    Tests whether more observations cluster near a threshold than expected
    under a uniform distribution.

    Per DES §22.3:
        p0 = 2 * epsilon / range(X)
        p = |{x : |x - T| <= epsilon}| / n
        z = (p - p0) / sqrt(p0 * (1 - p0) / n)

    Args:
        vals: Observation values.
        threshold: Candidate threshold T.
        epsilon: Band half-width around threshold.

    Returns:
        z-score. Values > 1.645 indicate compression (one-tailed, alpha=0.05).
    """
    n = len(vals)
    if n < 2:
        return 0.0

    min_val = float(np.min(vals))
    max_val = float(np.max(vals))
    val_range = max_val - min_val

    if val_range == 0:
        if threshold == min_val:
            return float("inf")
        return 0.0

    p0 = 2.0 * epsilon / val_range
    if p0 <= 0 or p0 >= 1:
        return 0.0

    in_band = int(np.sum(np.abs(np.array(vals) - threshold) <= epsilon))
    p = in_band / n

    try:
        z = (p - p0) / math.sqrt(p0 * (1.0 - p0) / n)
    except (ZeroDivisionError, ValueError):
        z = 0.0

    return float(z)


def dip_test(
    vals: List[float],
    bootstrap_samples: int = 1000,
    random_seed: int = 42,
) -> Tuple[float, float]:
    """Hartigan's Dip test approximation via bootstrap.

    Uses KS statistic against uniform CDF as an approximation for the
    true dip statistic (documented in DSVP §15.4).

    Args:
        vals: Observation values.
        bootstrap_samples: Number of bootstrap resamples.
        random_seed: Seed for reproducibility.

    Returns:
        Tuple of (dip_statistic, p_value).
    """
    n = len(vals)
    if n < 2:
        return 0.0, 1.0

    rng = np.random.default_rng(random_seed)

    sorted_vals = np.sort(vals)
    ecdf = np.arange(1, n + 1) / n

    min_val = float(np.min(vals))
    max_val = float(np.max(vals))
    if max_val == min_val:
        return 0.0, 1.0

    ucdf = (sorted_vals - min_val) / (max_val - min_val)
    ucdf = np.clip(ucdf, 0.0, 1.0)

    dip_statistic = float(np.max(np.abs(ecdf - ucdf)))

    bootstrap_stats = np.empty(bootstrap_samples)
    for i in range(bootstrap_samples):
        bs = rng.uniform(min_val, max_val, n)
        bs_sorted = np.sort(bs)
        bs_ecdf = np.arange(1, n + 1) / n
        bs_ucdf = (bs_sorted - min_val) / (max_val - min_val)
        bs_ucdf = np.clip(bs_ucdf, 0.0, 1.0)
        bootstrap_stats[i] = np.max(np.abs(bs_ecdf - bs_ucdf))

    p_value = float(np.sum(bootstrap_stats >= dip_statistic) / bootstrap_samples)
    return dip_statistic, p_value


def compute_epsilon(vals: List[float], threshold: float) -> float:
    """Compute epsilon for threshold compression test.

    Per DES §22.3: epsilon = max(0.02 * |T|, 0.01 * (max(X) - min(X))).

    Args:
        vals: Observation values.
        threshold: Candidate threshold T.

    Returns:
        Band half-width.
    """
    if len(vals) == 0:
        return 0.0
    val_range = float(np.max(vals) - np.min(vals))
    epsilon1 = 0.02 * abs(threshold)
    epsilon2 = 0.01 * val_range
    return max(epsilon1, epsilon2)


def auto_thresholds(
    vals: List[float],
    candidates: Optional[List[float]] = None,
    percentiles: Optional[List[int]] = None,
) -> List[float]:
    """Compute candidate thresholds for D-03.

    Combines fixed candidate thresholds with percentile-based round numbers.

    Args:
        vals: Observation values.
        candidates: Fixed threshold values to test (default: DES §22.2).
        percentiles: Percentile values to test (default: DES §22.2).

    Returns:
        Sorted list of unique thresholds.
    """
    if not vals:
        return []

    if candidates is None:
        candidates = [1, 5, 10, 20, 25, 50, 75, 80, 90, 95, 100, 1000]
    if percentiles is None:
        percentiles = [10, 25, 50, 75, 90]

    min_val = float(np.min(vals))
    max_val = float(np.max(vals))

    thresholds: set[float] = set()

    for t in candidates:
        if min_val <= t <= max_val:
            thresholds.add(float(t))

    for pct in percentiles:
        t = round(float(np.percentile(vals, pct)), 1)
        if t * 10 % 10 == 0 or t * 10 % 10 == 5:
            thresholds.add(t)

    return sorted(thresholds)


# ---------------------------------------------------------------------------
# Hypothesis testing utilities (PR-16A)
# ---------------------------------------------------------------------------


def z_to_p(z: float, alternative: str = "two-sided") -> float:
    """Convert a z-score to a p-value using the standard normal distribution.

    Args:
        z: Observed z-score.
        alternative: "two-sided" (H1: μ ≠ 0), "greater" (H1: μ > 0),
            or "less" (H1: μ < 0).

    Returns:
        P-value in [0, 1].
    """
    from scipy.stats import norm

    if alternative == "two-sided":
        return 2.0 * (1.0 - norm.cdf(abs(z)))
    elif alternative == "greater":
        return 1.0 - norm.cdf(z)
    else:
        return norm.cdf(z)


def fisher_z_test(r: float, n: int) -> float:
    """Test H0: ρ = 0 using Fisher z-transform.

    Computes z_obs = fisher_z(r) * sqrt(n - 3), then returns the
    two-sided p-value from the standard normal distribution.

    Args:
        r: Observed Pearson correlation in (-1, 1).
        n: Sample size (must be >= 4).

    Returns:
        Two-sided p-value. Returns 1.0 if n < 4.
    """
    if n < 4:
        return 1.0

    from scipy.stats import norm

    z_r = fisher_z(r)
    se = 1.0 / math.sqrt(n - 3)
    z_obs = z_r / se
    return 2.0 * (1.0 - norm.cdf(abs(z_obs)))
