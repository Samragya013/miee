"""
Experimental Detector Research Package (PR-18)

This package contains experimental detector implementations for research purposes.
These detectors are NOT production-certified and should NOT be used in production.

All experimental code is isolated from certified production detectors in:
- src/miie/processing/detection/distribution_drift_detector.py (D-01)
- src/miie/processing/detection/threshold_compression_detector.py (D-03)

Experimental Results: benchmarks/results/pr18_research/
"""

__version__ = "0.1.0"
__author__ = "MIIE Research Team"

# Package-level imports for convenience
from .d01_candidates import (
    energy_distance_test,
    mmd_two_sample_test,
    wasserstein_two_sample_test,
)
from .d03_candidates import (
    density_ratio_test,
    gmm_bimodality_test,
    silverman_bimodality_test,
)

__all__ = [
    # D-01 candidates
    "wasserstein_two_sample_test",
    "energy_distance_test",
    "mmd_two_sample_test",
    # D-03 candidates
    "gmm_bimodality_test",
    "silverman_bimodality_test",
    "density_ratio_test",
]
