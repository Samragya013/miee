"""Scoring Utilities Module.

Shared utility functions for score confidence (C_s) computations, extracted from
ScoringEngine to reduce duplication and improve testability.

Score confidence factors use β notation:
    β₁: sample_size_adequacy    (compute_sample_size_factor)
    β₂: variance_stability      (compute_variance_factor)
    β₃: data_completeness       (compute_missing_data_factor)
    β₄: window_balance          (compute_balance_factor)
    β₅: detector_coverage       (compute_detector_success_factor)
    β₆: evidence_quality        (compute_observation_quality_factor)

Formula: C_s = β₁ × β₂ × β₃ × β₄ × β₅ × β₆

Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4

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

    Filters out NaN and infinite values before computation.

    Args:
        values: Sequence of numeric values

    Returns:
        Arithmetic mean, or 0.0 if the sequence is empty or all invalid
    """
    if not values:
        return 0.0
    # Filter out NaN and infinite values to prevent propagation
    valid = [v for v in values if math.isfinite(v)]
    if not valid:
        return 0.0
    return math.fsum(valid) / len(valid)


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

    Filters out NaN and infinite values before computation.

    Args:
        values: Sequence of numeric values (need at least 2 elements for meaningful CV)

    Returns:
        Coefficient of variation, or 0.0 if insufficient data
    """
    if len(values) < 2:
        return 0.0

    # Filter out non-finite values
    valid = [v for v in values if math.isfinite(v)]
    if len(valid) < 2:
        return 0.0

    mean_val = compute_mean(valid)
    if mean_val != 0:
        return safe_divide(compute_std(valid), abs(mean_val))

    # Special handling for mean=0
    if all(v == 0 for v in valid):
        return 0.0  # Perfect consistency
    return 1.0  # High variance relative to zero mean


def compute_clamped(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a value to [low, high] range.

    Handles NaN and infinite values by returning the low bound.

    Args:
        value: Value to clamp
        low: Lower bound (inclusive)
        high: Upper bound (inclusive)

    Returns:
        Clamped value
    """
    if not math.isfinite(value):
        return low
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
    """Compute β₄ (window_balance): 1 - min(1, std/mean).

    Measures how evenly distributed window sizes are.
    A perfect balance (all sizes equal) gives 1.0.
    Highly uneven sizes approach 0.0.

    Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4

    Args:
        sizes: Sequence of window sizes (observations per window)

    Returns:
        Window balance factor in [0, 1]
    """
    if not sizes:
        return 0.0

    if len(sizes) == 1:
        return 1.0

    # Filter out non-finite values
    valid = [s for s in sizes if math.isfinite(s) and s >= 0]
    if not valid:
        return 0.0

    mean_size = compute_mean(valid)
    if mean_size <= 0:
        return 0.0

    std_size = compute_std(valid)
    return compute_clamped(1.0 - min(1.0, std_size / mean_size))


def compute_sample_size_factor(mean_n: float, target: float = 50.0) -> float:
    """Compute β₁ (sample_size_adequacy): min(1.0, mean_n / target).

    Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4

    Args:
        mean_n: Average number of observations per metric
        target: Target observation count for full confidence (default 50)

    Returns:
        Sample size factor in [0, 1]
    """
    return compute_clamped(safe_divide(mean_n, target))


def compute_variance_factor(mean_cv: float, threshold: float = 0.5) -> float:
    """Compute β₂ (variance_stability): 1 - min(1, mean_cv / threshold).

    Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4

    Args:
        mean_cv: Average coefficient of variation across windows
        threshold: CV threshold above which factor is 0 (default 0.5)

    Returns:
        Variance factor in [0, 1]
    """
    return compute_clamped(1.0 - min(1.0, safe_divide(mean_cv, threshold)))


def compute_missing_data_factor(missing_pairs: int, total_pairs: int) -> float:
    """Compute β₃ (data_completeness): 1 - (missing / total).

    Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4

    Args:
        missing_pairs: Number of missing metric-window pairs
        total_pairs: Total number of metric-window pairs

    Returns:
        Missing data factor in [0, 1]
    """
    return compute_clamped(1.0 - safe_divide(float(missing_pairs), float(total_pairs)))


def compute_detector_success_factor(successful_runs: int, total_attempts: int) -> float:
    """Compute β₅ (detector_coverage): successful_runs / total_attempts.

    Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4

    Args:
        successful_runs: Number of successful detector executions
        total_attempts: Total number of detector execution attempts

    Returns:
        Detector success factor in [0, 1]
    """
    if total_attempts <= 0:
        return 0.0
    return safe_divide(float(successful_runs), float(total_attempts))


def compute_observation_quality_factor(complete: int, partial: int, estimated: int) -> float:
    """Compute β₆ (evidence_quality) from quality counts.

    Formula: (complete + 0.5*partial) / (complete + partial + estimated)

    Reference: 01_CONFIDENCE_MODEL_UNIFICATION.md §7.4

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
