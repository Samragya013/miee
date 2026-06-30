"""Scoring Utilities Module.

Shared utility functions for scoring computations, extracted from ScoringEngine
to reduce duplication and improve testability.

IMS Phase 5 (Scoring Utilities Extraction).
"""

import math
from typing import Sequence


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    """Safe division that returns default when denominator is zero or near-zero.

    Args:
        numerator: Value to divide
        denominator: Value to divide by
        default: Value to return if denominator is zero

    Returns:
        numerator / denominator if denominator != 0, else default
    """
    if abs(denominator) < 1e-15:
        return default
    return numerator / denominator


def compute_mean(values: Sequence[float]) -> float:
    """Compute the arithmetic mean of a sequence of values.

    Args:
        values: Sequence of numeric values

    Returns:
        Arithmetic mean, or 0.0 if the sequence is empty
    """
    if not values:
        return 0.0
    return math.fsum(values) / len(values)


def compute_std(values: Sequence[float]) -> float:
    """Compute the population standard deviation of a sequence of values.

    Args:
        values: Sequence of numeric values (need at least 1 element)

    Returns:
        Population standard deviation, or 0.0 if empty
    """
    if len(values) < 2:
        return 0.0
    mean_val = compute_mean(values)
    variance = math.fsum((x - mean_val) ** 2 for x in values) / len(values)
    return variance**0.5


def compute_cv(values: Sequence[float]) -> float:
    """Compute the coefficient of variation (CV = std / |mean|).

    Special handling for mean=0:
    - If all values are 0 (perfect consistency), CV = 0.0
    - If mean is 0 but values vary, CV = 1.0

    Args:
        values: Sequence of numeric values (need at least 2 elements for meaningful CV)

    Returns:
        Coefficient of variation, or 0.0 if insufficient data
    """
    if len(values) < 2:
        return 0.0

    mean_val = compute_mean(values)
    if mean_val != 0:
        return safe_divide(compute_std(values), abs(mean_val))

    # Special handling for mean=0
    if all(v == 0 for v in values):
        return 0.0  # Perfect consistency
    return 1.0  # High variance relative to zero mean


def compute_clamped(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a value to [low, high] range.

    Args:
        value: Value to clamp
        low: Lower bound (inclusive)
        high: Upper bound (inclusive)

    Returns:
        Clamped value
    """
    return max(low, min(high, value))


def compute_coverage_ratio(present: int, total: int) -> float:
    """Compute the ratio of present items to total items.

    Args:
        present: Number of items with data present
        total: Total number of items expected

    Returns:
        Coverage ratio in [0, 1], or 0.0 if total is 0
    """
    if total <= 0:
        return 0.0
    return safe_divide(float(present), float(total), default=0.0)


def compute_balance_factor(sizes: Sequence[float]) -> float:
    """Compute the balance factor: 1 - min(1, std/mean).

    Measures how evenly distributed window sizes are.
    A perfect balance (all sizes equal) gives 1.0.
    Highly uneven sizes approach 0.0.

    Args:
        sizes: Sequence of window sizes (observations per window)

    Returns:
        Balance factor in [0, 1]
    """
    if not sizes:
        return 0.0

    if len(sizes) == 1:
        return 1.0

    mean_size = compute_mean(sizes)
    if mean_size <= 0:
        return 0.0

    std_size = compute_std(sizes)
    return compute_clamped(1.0 - min(1.0, std_size / mean_size))


def compute_sample_size_factor(mean_n: float, target: float = 50.0) -> float:
    """Compute the sample size factor: min(1.0, mean_n / target).

    Args:
        mean_n: Average number of observations per metric
        target: Target observation count for full confidence (default 50)

    Returns:
        Sample size factor in [0, 1]
    """
    return compute_clamped(safe_divide(mean_n, target))


def compute_variance_factor(mean_cv: float, threshold: float = 0.5) -> float:
    """Compute the variance factor: 1 - min(1, mean_cv / threshold).

    Args:
        mean_cv: Average coefficient of variation across windows
        threshold: CV threshold above which factor is 0 (default 0.5)

    Returns:
        Variance factor in [0, 1]
    """
    return compute_clamped(1.0 - min(1.0, safe_divide(mean_cv, threshold)))


def compute_missing_data_factor(missing_pairs: int, total_pairs: int) -> float:
    """Compute the missing data factor: 1 - (missing / total).

    Args:
        missing_pairs: Number of missing metric-window pairs
        total_pairs: Total number of metric-window pairs

    Returns:
        Missing data factor in [0, 1]
    """
    return compute_clamped(1.0 - safe_divide(float(missing_pairs), float(total_pairs)))


def compute_detector_success_factor(successful_runs: int, total_attempts: int) -> float:
    """Compute the detector success factor: successful_runs / total_attempts.

    Args:
        successful_runs: Number of successful detector executions
        total_attempts: Total number of detector execution attempts

    Returns:
        Detector success factor in [0, 1]
    """
    return safe_divide(float(successful_runs), float(total_attempts))


def compute_observation_quality_factor(complete: int, partial: int, estimated: int) -> float:
    """Compute observation quality factor from quality counts.

    Quality factor = (complete + 0.5*partial) / (complete + partial + estimated)

    Args:
        complete: Number of observations with complete data
        partial: Number of observations with partial data
        estimated: Number of estimated observations

    Returns:
        Quality factor in [0, 1]
    """
    total = complete + partial + estimated
    if total <= 0:
        return 0.0
    return safe_divide(complete + 0.5 * partial, total)
