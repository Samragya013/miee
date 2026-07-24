"""
D-03 Experimental Candidates: Threshold Compression Detection

These are experimental implementations of advanced statistical methods for
detecting threshold compression in windowed data. They are designed to address
the limitations of the current Excess Mass + Dip Test approach identified in PR-17.

Candidates:
1. Gaussian Mixture Model (GMM) + BIC
2. Silverman's Critical Bandwidth Test
3. Density Ratio Estimation

All candidates use bootstrap/permutation tests for p-value computation to ensure
valid Type I error control for small samples (n=30).
"""

from .density_ratio_detector import density_ratio_test
from .gmm_detector import gmm_bimodality_test
from .silverman_detector import silverman_bimodality_test

__all__ = [
    "gmm_bimodality_test",
    "silverman_bimodality_test",
    "density_ratio_test",
]
