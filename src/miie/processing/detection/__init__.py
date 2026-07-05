"""
Detector Framework package for MIIE v1.0.
Exports detector framework components.

Extended in v1.6 with StatisticalInferenceEngine (PR-16A).
Extended in v1.6 with PowerAnalysis and EffectSize frameworks (PR-16B).
"""

from miie.processing.detection.base import BaseDetector
from miie.processing.detection.diagnostics import (
    d01_diagnostics,
    d02_diagnostics,
    d03_diagnostics,
)
from miie.processing.detection.dispatcher import DetectorDispatcherEngine
from miie.processing.detection.effect_size import (
    EffectSizeLabel,
    EffectSizeResult,
    cliffs_delta,
    cohens_d,
    correlation_effect_size,
    effect_size_summary,
    interpret_effect_size,
    jensen_shannon_divergence,
    ks_effect_size,
    rank_biserial,
)
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
from miie.processing.detection.power import (
    CIDiagnosticResult,
    PowerAnalysisResult,
    SampleSizeResult,
    ci_width_correlation,
    ci_width_mean,
    ci_width_proportion,
    mde_correlation,
    mde_ks,
    mde_proportion,
    mde_t_test,
    observed_power,
    power_correlation_test,
    power_ks_test,
    power_proportion_test,
    power_t_test,
    sample_size_correlation,
    sample_size_ks,
    sample_size_proportion,
    sample_size_t_test,
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
    # Power analysis (PR-16B)
    "PowerAnalysisResult",
    "SampleSizeResult",
    "CIDiagnosticResult",
    "power_ks_test",
    "power_t_test",
    "power_correlation_test",
    "power_proportion_test",
    "observed_power",
    "sample_size_ks",
    "sample_size_t_test",
    "sample_size_correlation",
    "sample_size_proportion",
    "mde_ks",
    "mde_t_test",
    "mde_correlation",
    "mde_proportion",
    "ci_width_correlation",
    "ci_width_mean",
    "ci_width_proportion",
    # Effect sizes (PR-16B)
    "EffectSizeLabel",
    "EffectSizeResult",
    "cohens_d",
    "cliffs_delta",
    "rank_biserial",
    "ks_effect_size",
    "correlation_effect_size",
    "jensen_shannon_divergence",
    "effect_size_summary",
    "interpret_effect_size",
    # Detector diagnostics (PR-16B)
    "d01_diagnostics",
    "d02_diagnostics",
    "d03_diagnostics",
]
