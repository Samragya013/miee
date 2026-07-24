"""
D-01 Experimental Candidates: Distribution Drift Detection

These are experimental implementations of advanced statistical methods for
detecting distribution drift in windowed data. They are designed to address
the limitations of the current KS+PSI approach identified in PR-17.

Candidates:
1. Wasserstein Distance (Earth Mover's Distance)
2. Energy Distance
3. Maximum Mean Discrepancy (MMD)

All candidates use permutation tests for p-value computation to ensure
exact Type I error control for small samples (n=30).
"""

from .energy_distance_detector import energy_distance_test
from .mmd_detector import mmd_two_sample_test
from .wasserstein_detector import wasserstein_two_sample_test

__all__ = [
    "wasserstein_two_sample_test",
    "energy_distance_test",
    "mmd_two_sample_test",
]
