"""
Detector Framework package for MIIE v1.0.
Exports detector framework components.

Extended in v1.6 with StatisticalInferenceEngine (PR-16A).
"""

from miie.processing.detection.base import BaseDetector
from miie.processing.detection.dispatcher import DetectorDispatcherEngine
from miie.processing.detection.inference import (
    HypothesisTest,
    InferenceResult,
    StatisticalInferenceEngine,
)
from miie.processing.detection.mock_detectors import (
    MockCorrelationBreakdownDetector,
    MockDistributionDriftDetector,
    MockThresholdCompressionDetector,
)
from miie.processing.detection.registry import DetectorRegistry
from miie.processing.detection.runner import DetectorRunner
from miie.processing.detection.statistics import (
    compute_psi,
    dip_test,
    excess_mass_test,
    fisher_z,
    fisher_z_ci,
    fisher_z_inverse,
    fisher_z_test,
    ks_2samp,
    pearson_r,
    spearman_rho,
    z_to_p,
)

__all__ = [
    "BaseDetector",
    "DetectorRegistry",
    "DetectorDispatcherEngine",
    "DetectorRunner",
    "MockDistributionDriftDetector",
    "MockCorrelationBreakdownDetector",
    "MockThresholdCompressionDetector",
    # Shared statistics (DES v2.0 §25)
    "ks_2samp",
    "compute_psi",
    "pearson_r",
    "spearman_rho",
    "fisher_z",
    "fisher_z_inverse",
    "fisher_z_ci",
    "fisher_z_test",
    "excess_mass_test",
    "dip_test",
    "z_to_p",
    # Statistical inference (PR-16A)
    "HypothesisTest",
    "InferenceResult",
    "StatisticalInferenceEngine",
]
