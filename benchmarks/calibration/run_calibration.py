"""PR-16C Statistical Calibration & Certification Campaign.

Main orchestrator that runs all 12 calibration phases and produces
the 12 required deliverables.

Usage:
    python -m benchmarks.calibration.run_calibration --seed 42
    python benchmarks/calibration/run_calibration.py --seed 42
"""

from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""

    def default(self, obj):
        import numpy as np

        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


from typing import Any, Dict, List, Optional

import numpy as np

# Ensure repo root is on path
_REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from benchmarks.calibration.synthetic_data import (
    SyntheticDataset,
    generate_all_datasets,
    generate_d01_medium_drift,
    generate_d02_medium_weakening,
    generate_d03_moderate_compression,
)
from miie.processing.detection.effect_size import (
    cliffs_delta,
    cohens_d,
    correlation_effect_size,
    interpret_effect_size,
    jensen_shannon_divergence,
    ks_effect_size,
)
from miie.processing.detection.inference import (
    StatisticalInferenceEngine,
)
from miie.processing.detection.power import (
    ci_width_correlation,
    ci_width_proportion,
    mde_ks,
    observed_power,
    power_correlation_test,
    power_ks_test,
    power_proportion_test,
    power_t_test,
    sample_size_ks,
    sample_size_t_test,
)
from miie.processing.detection.statistics import (
    dip_test,
    excess_mass_test,
    fisher_z,
    ks_2samp,
    pearson_r,
    z_to_p,
)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results" / "pr16c_calibration"

# ---------------------------------------------------------------------------
# Phase 3: Detector Calibration
# ---------------------------------------------------------------------------


@dataclass
class DetectorCalibrationResult:
    """Result of calibrating one detector on one dataset."""

    dataset_id: str
    detector_id: str
    expected_detected: bool
    observed_detected: bool
    tp: bool = False
    fp: bool = False
    fn: bool = False
    tn: bool = False
    raw_p_value: float = 1.0
    adjusted_p_value: float = 1.0
    correction_method: str = ""
    ks_statistic: float = 0.0
    effect_size: float = 0.0
    power: float = 0.0
    sample_size: int = 0
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0


def calibrate_d01(dataset: SyntheticDataset, alpha: float = 0.05) -> DetectorCalibrationResult:
    """Calibrate D-01 (Distribution Drift) on a single dataset."""
    t0 = time.perf_counter()
    values = dataset.values
    n_windows = len(values)

    # Run KS tests on consecutive window pairs
    p_values = []
    ks_stats = []
    for i in range(n_windows - 1):
        stat, p = ks_2samp(values[i], values[i + 1])
        ks_stats.append(stat)
        p_values.append(p)

    # Apply Bonferroni correction (D-01 spec)
    if p_values:
        inf_result = StatisticalInferenceEngine.bonferroni(p_values, alpha=alpha, family_id="D-01_KS")
        adjusted = list(inf_result.adjusted_p_values)
        decisions = list(inf_result.reject)
    else:
        adjusted = p_values
        decisions = [False] * len(p_values)

    detected = any(decisions)
    expected = dataset.anomaly_present and dataset.anomaly_type == "metric-drift"

    tp = detected and expected
    fp = detected and not expected
    fn = not detected and expected
    tn = not detected and not expected

    # Compute effect size (max KS across pairs)
    max_ks = max(ks_stats) if ks_stats else 0.0
    if len(values) >= 2 and values[0] and values[1]:
        es = ks_effect_size(np.array(values[0]), np.array(values[1]))
        effect_val = es.value
    else:
        effect_val = max_ks

    # Compute power
    n_min = min(len(v) for v in values) if values else 0
    pow_val = power_ks_test(n_min, n_min, max_ks, alpha) if n_min > 4 else 0.0

    elapsed = (time.perf_counter() - t0) * 1000.0

    return DetectorCalibrationResult(
        dataset_id=dataset.dataset_id,
        detector_id="D-01",
        expected_detected=expected,
        observed_detected=detected,
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        raw_p_value=min(p_values) if p_values else 1.0,
        adjusted_p_value=min(adjusted) if adjusted else 1.0,
        correction_method="bonferroni",
        ks_statistic=max_ks,
        effect_size=effect_val,
        power=pow_val,
        sample_size=n_min,
        execution_time_ms=elapsed,
    )


def calibrate_d02(dataset: SyntheticDataset, alpha: float = 0.05) -> DetectorCalibrationResult:
    """Calibrate D-02 (Correlation Breakdown) on a single dataset."""
    t0 = time.perf_counter()
    values = dataset.values
    if len(values) < 2 or not dataset.metric_pairs:
        return DetectorCalibrationResult(
            dataset_id=dataset.dataset_id,
            detector_id="D-02",
            expected_detected=False,
            observed_detected=False,
            tn=True,
        )

    values_x = values[0]
    values_y = values[1]
    n_windows = len(values_x)

    # Compute Pearson r per window
    correlations = []
    for i in range(n_windows):
        min_len = min(len(values_x[i]), len(values_y[i]))
        if min_len >= 4:
            r = pearson_r(values_x[i][:min_len], values_y[i][:min_len])
            correlations.append(r)
        else:
            correlations.append(0.0)

    # Test for correlation breakdown: compare first half vs second half
    half = len(correlations) // 2
    if half < 1:
        half = 1
    r_first = np.mean(correlations[:half])
    r_second = np.mean(correlations[half:])
    delta_r = abs(r_first - r_second)

    # Fisher z-test for difference
    if len(correlations) >= 2:
        z_first = fisher_z(float(r_first))
        z_second = fisher_z(float(r_second))
        n_avg = min(len(v) for v in values_x[:1] + values_y[:1]) if values_x and values_y else 30
        se = math.sqrt(1.0 / max(n_avg - 3, 1) + 1.0 / max(n_avg - 3, 1))
        z_diff = abs(z_first - z_second) / se if se > 0 else 0.0
        p_diff = z_to_p(z_diff, "two-sided")
    else:
        p_diff = 1.0
        z_diff = 0.0

    detected = p_diff < alpha and delta_r > 0.1
    expected = dataset.anomaly_present and dataset.anomaly_type == "correlation-breakdown"

    tp = detected and expected
    fp = detected and not expected
    fn = not detected and expected
    tn = not detected and not expected

    # Effect size (clamp delta_r to avoid Fisher z singularity at ±1)
    n_total = sum(min(len(x), len(y)) for x, y in zip(values_x, values_y))
    delta_r_clamped = max(-0.999, min(0.999, float(r_second - r_first)))
    es = correlation_effect_size(delta_r_clamped, n_total) if n_total > 4 else None
    effect_val = es.value if es else delta_r

    # Power
    pow_val = power_correlation_test(n_total, delta_r, alpha) if n_total > 4 else 0.0

    elapsed = (time.perf_counter() - t0) * 1000.0

    return DetectorCalibrationResult(
        dataset_id=dataset.dataset_id,
        detector_id="D-02",
        expected_detected=expected,
        observed_detected=detected,
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        raw_p_value=p_diff,
        adjusted_p_value=p_diff,
        correction_method="fisher_z",
        ks_statistic=delta_r,
        effect_size=effect_val,
        power=pow_val,
        sample_size=n_total,
        execution_time_ms=elapsed,
    )


def calibrate_d03(dataset: SyntheticDataset, alpha: float = 0.05) -> DetectorCalibrationResult:
    """Calibrate D-03 (Threshold Compression) on a single dataset."""
    t0 = time.perf_counter()
    values = dataset.values
    n_windows = len(values)

    threshold = 0.5
    z_scores = []
    dip_stats = []
    dip_ps = []

    for i in range(n_windows):
        if len(values[i]) < 5:
            z_scores.append(0.0)
            dip_stats.append(0.0)
            dip_ps.append(1.0)
            continue
        eps = max(0.02 * abs(threshold), 0.01 * (max(values[i]) - min(values[i])))
        z = excess_mass_test(values[i], threshold, eps)
        dip_stat, dip_p = dip_test(values[i], bootstrap_samples=200)
        z_scores.append(z)
        dip_stats.append(dip_stat)
        dip_ps.append(dip_p)

    # Apply Bonferroni correction
    if dip_ps:
        inf_result = StatisticalInferenceEngine.bonferroni(dip_ps, alpha=alpha, family_id="D-03_dip")
        adjusted = list(inf_result.adjusted_p_values)
        decisions = list(inf_result.reject)
    else:
        adjusted = dip_ps
        decisions = [False] * len(dip_ps)

    # Detection: any z > 1.645 OR any adjusted dip test significant
    detected_z = any(z > 1.645 for z in z_scores)
    detected_dip = any(decisions)
    detected = detected_z or detected_dip

    expected = dataset.anomaly_present and dataset.anomaly_type == "threshold-compression"

    tp = detected and expected
    fp = detected and not expected
    fn = not detected and expected
    tn = not detected and not expected

    # Effect size: compression index
    all_vals = [v for window in values for v in window]
    if all_vals:
        in_band = sum(1 for v in all_vals if abs(v - threshold) <= 0.1)
        compression_index = in_band / len(all_vals)
    else:
        compression_index = 0.0

    # Power
    n_total = len(all_vals)
    pow_val = power_proportion_test(n_total, compression_index, 0.5, alpha) if n_total > 5 else 0.0

    elapsed = (time.perf_counter() - t0) * 1000.0

    return DetectorCalibrationResult(
        dataset_id=dataset.dataset_id,
        detector_id="D-03",
        expected_detected=expected,
        observed_detected=detected,
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        raw_p_value=min(dip_ps) if dip_ps else 1.0,
        adjusted_p_value=min(adjusted) if adjusted else 1.0,
        correction_method="bonferroni",
        ks_statistic=max(z_scores) if z_scores else 0.0,
        effect_size=compression_index,
        power=pow_val,
        sample_size=n_total,
        execution_time_ms=elapsed,
    )


# ---------------------------------------------------------------------------
# Phase 4: Statistical Calibration
# ---------------------------------------------------------------------------


def calibrate_correction_methods(alpha: float = 0.05) -> Dict[str, Any]:
    """Compare Bonferroni, Holm, BH on reference p-value sets."""
    # Reference sets with known expected outcomes
    test_sets = {
        "all_significant": [0.001, 0.002, 0.003, 0.004, 0.005],
        "some_significant": [0.001, 0.01, 0.03, 0.06, 0.10],
        "none_significant": [0.10, 0.20, 0.30, 0.40, 0.50],
        "borderline": [0.045, 0.048, 0.052, 0.055, 0.060],
        "single_test": [0.03],
        "many_tests": [0.001, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10],
    }

    results = {}
    for name, p_vals in test_sets.items():
        bonf = StatisticalInferenceEngine.bonferroni(p_vals, alpha=alpha, family_id=f"cal_{name}")
        holm = StatisticalInferenceEngine.holm(p_vals, alpha=alpha, family_id=f"cal_{name}")
        bh = StatisticalInferenceEngine.benjamini_hochberg(p_vals, alpha=alpha, family_id=f"cal_{name}")

        results[name] = {
            "raw_p_values": p_vals,
            "num_tests": len(p_vals),
            "bonferroni": {
                "adjusted_p_values": list(bonf.adjusted_p_values),
                "num_rejections": bonf.num_rejections,
                "reject": list(bonf.reject),
            },
            "holm": {
                "adjusted_p_values": list(holm.adjusted_p_values),
                "num_rejections": holm.num_rejections,
                "reject": list(holm.reject),
            },
            "benjamini_hochberg": {
                "adjusted_p_values": list(bh.adjusted_p_values),
                "num_rejections": bh.num_rejections,
                "reject": list(bh.reject),
            },
            "conservative_order": (bonf.num_rejections <= holm.num_rejections <= bh.num_rejections),
        }

    # Key property: Bonferroni is most conservative, BH is least
    monotonicity_check = all(results[n]["conservative_order"] for n in results)

    return {
        "test_sets": results,
        "monotonicity_preserved": monotonicity_check,
        "alpha": alpha,
        "summary": (
            f"Tested {len(test_sets)} p-value sets. "
            f"Conservative ordering (Bonferroni <= Holm <= BH) "
            f"{'preserved' if monotonicity_check else 'VIOLATED'} "
            f"across all sets."
        ),
    }


# ---------------------------------------------------------------------------
# Phase 5: Effect Size Validation
# ---------------------------------------------------------------------------


def validate_effect_sizes() -> Dict[str, Any]:
    """Validate effect size computation against analytical expectations."""
    rng = np.random.default_rng(42)
    results = {}

    # Test 1: Identical distributions -> d ≈ 0
    x_same = rng.normal(50, 10, 200)
    y_same = rng.normal(50, 10, 200)
    d_same = cohens_d(x_same, y_same)
    results["identical_distributions"] = {
        "cohens_d": d_same.value,
        "expected": "~0.0",
        "label": d_same.label.value,
        "within_tolerance": abs(d_same.value) < 0.15,
    }

    # Test 2: Known shift d=0.5
    x_shift = rng.normal(50, 10, 200)
    y_shift = rng.normal(55, 10, 200)  # d ≈ 0.5
    d_shift = cohens_d(x_shift, y_shift)
    results["known_shift_d05"] = {
        "cohens_d": d_shift.value,
        "expected": "~0.5",
        "label": d_shift.label.value,
        "within_tolerance": 0.3 < d_shift.value < 0.7,
    }

    # Test 3: Large shift d=0.8
    x_large = rng.normal(50, 10, 200)
    y_large = rng.normal(58, 10, 200)  # d ≈ 0.8
    d_large = cohens_d(x_large, y_large)
    results["large_shift_d08"] = {
        "cohens_d": d_large.value,
        "expected": "~0.8",
        "label": d_large.label.value,
        "within_tolerance": 0.5 < d_large.value < 1.1,
    }

    # Test 4: KS effect size
    ks_es = ks_effect_size(x_shift, y_shift)
    results["ks_effect_size"] = {
        "value": ks_es.value,
        "label": ks_es.label.value,
        "in_range": 0.0 <= ks_es.value <= 1.0,
    }

    # Test 5: Cliff's delta
    cliff = cliffs_delta(x_shift, y_shift)
    results["cliffs_delta"] = {
        "value": cliff.value,
        "label": cliff.label.value,
        "in_range": -1.0 <= cliff.value <= 1.0,
    }

    # Test 6: Jensen-Shannon divergence
    jsd = jensen_shannon_divergence(x_same, y_shift)
    results["jensen_shannon"] = {
        "value": jsd.value,
        "label": jsd.label.value,
        "non_negative": jsd.value >= 0.0,
    }

    # Test 7: Correlation effect size
    r_es = correlation_effect_size(0.7, 100)
    results["correlation_effect_size"] = {
        "value": r_es.value,
        "label": r_es.label.value,
        "r_squared": r_es.value**2,
    }

    # Test 8: Effect size interpretation bands
    band_tests = [
        (0.0, "general", "negligible"),
        (0.15, "general", "small"),
        (0.35, "general", "medium"),
        (0.65, "general", "large"),
        (0.9, "general", "very large"),
    ]
    band_results = {}
    for d_val, kind, expected_label in band_tests:
        label = interpret_effect_size(d_val, kind)
        band_results[f"d={d_val}"] = {
            "observed": label.value,
            "expected": expected_label,
            "correct": label.value == expected_label,
        }
    results["interpretation_bands"] = band_results

    # Test 9: Boundary values
    boundary_tests = {
        "zero_effect": cohens_d(x_same, x_same),
        "max_effect": cohens_d(x_same, x_same + 1000),
    }
    results["boundary_values"] = {
        "zero_effect_d": boundary_tests["zero_effect"].value,
        "zero_effect_label": boundary_tests["zero_effect"].label.value,
        "max_effect_d": boundary_tests["max_effect"].value,
        "max_effect_label": boundary_tests["max_effect"].label.value,
    }

    # Summary
    all_pass = (
        results["identical_distributions"]["within_tolerance"]
        and results["ks_effect_size"]["in_range"]
        and results["cliffs_delta"]["in_range"]
        and results["jensen_shannon"]["non_negative"]
        and all(v["correct"] for v in band_results.values())
    )
    results["overall_pass"] = all_pass

    return results


# ---------------------------------------------------------------------------
# Phase 6: Power Validation
# ---------------------------------------------------------------------------


def validate_power() -> Dict[str, Any]:
    """Validate power analysis against analytical expectations."""
    results = {}

    # Test 1: Power increases with sample size
    powers = [power_ks_test(n, n, 0.5, 0.05) for n in [10, 20, 30, 50, 100]]
    results["power_increases_with_n"] = {
        "powers": powers,
        "monotonic": all(powers[i] <= powers[i + 1] for i in range(len(powers) - 1)),
    }

    # Test 2: Power increases with effect size
    powers_d = [power_ks_test(30, 30, d, 0.05) for d in [0.1, 0.3, 0.5, 0.7, 0.9]]
    results["power_increases_with_effect"] = {
        "powers": powers_d,
        "monotonic": all(powers_d[i] <= powers_d[i + 1] for i in range(len(powers_d) - 1)),
    }

    # Test 3: MDE decreases with sample size
    mdes = [mde_ks(n, 0.05, 0.80) for n in [10, 20, 30, 50, 100]]
    results["mde_decreases_with_n"] = {
        "mdes": mdes,
        "monotonic": all(mdes[i] >= mdes[i + 1] for i in range(len(mdes) - 1)),
    }

    # Test 4: Sample size increases with power target
    ns = [sample_size_ks(0.5, 0.05, p).required_n for p in [0.60, 0.70, 0.80, 0.90, 0.95]]
    results["sample_size_increases_with_power"] = {
        "sample_sizes": ns,
        "monotonic": all(ns[i] <= ns[i + 1] for i in range(len(ns) - 1)),
    }

    # Test 5: CI width decreases with n
    ci_widths = [ci_width_correlation(0.5, n, 0.95).ci_width for n in [10, 20, 50, 100, 200]]
    results["ci_width_decreases_with_n"] = {
        "widths": ci_widths,
        "monotonic": all(ci_widths[i] >= ci_widths[i + 1] for i in range(len(ci_widths) - 1)),
    }

    # Test 6: Expected sample size for r=0.5, alpha=0.05, power=0.80 ≈ 29
    ss_r = sample_size_correlation(0.5, 0.05, 0.80)
    results["expected_sample_size_r05"] = {
        "required_n": ss_r.required_n,
        "expected_approx": 29,
        "within_range": 20 <= ss_r.required_n <= 40,
    }

    # Test 7: Expected sample size for d=0.5, alpha=0.05, power=0.80 ≈ 64
    ss_d = sample_size_t_test(0.5, 0.05, 0.80, two_sample=True)
    results["expected_sample_size_d05"] = {
        "required_n": ss_d.required_n,
        "expected_approx": 64,
        "within_range": 40 <= ss_d.required_n <= 90,
    }

    # Test 8: Observed power from known p-value
    op = observed_power(0.01, 50, 0.05)
    results["observed_power_from_p01"] = {
        "power": op,
        "in_range": 0.0 <= op <= 1.0,
    }

    # Test 9: Proportion CI
    ci_prop = ci_width_proportion(100, 0.7, 0.95, "wilson")
    results["proportion_ci"] = {
        "ci_lower": ci_prop.ci_lower,
        "ci_upper": ci_prop.ci_upper,
        "width": ci_prop.ci_width,
        "contains_p05": ci_prop.ci_lower <= 0.7 <= ci_prop.ci_upper,
    }

    all_pass = (
        results["power_increases_with_n"]["monotonic"]
        and results["power_increases_with_effect"]["monotonic"]
        and results["mde_decreases_with_n"]["monotonic"]
        and results["sample_size_increases_with_power"]["monotonic"]
        and results["ci_width_decreases_with_n"]["monotonic"]
        and results["expected_sample_size_r05"]["within_range"]
        and results["expected_sample_size_d05"]["within_range"]
    )
    results["overall_pass"] = all_pass

    return results


# ---------------------------------------------------------------------------
# Phase 8: Determinism Verification
# ---------------------------------------------------------------------------


def verify_determinism(n_runs: int = 10) -> Dict[str, Any]:
    """Run identical analyses multiple times and verify identical results."""
    results = {}
    seed = 42

    # Generate a reference dataset
    rng_ref = np.random.default_rng(seed)
    ref_data = rng_ref.normal(50, 10, 100).tolist()

    # Run KS test n_runs times
    ks_results = []
    for _ in range(n_runs):
        stat, p = ks_2samp(ref_data, ref_data)
        ks_results.append((round(stat, 15), round(p, 15)))

    results["ks_deterministic"] = {
        "all_identical": len(set(ks_results)) == 1,
        "n_runs": n_runs,
        "unique_results": len(set(ks_results)),
    }

    # Run Pearson r n_runs times
    rng2 = np.random.default_rng(seed)
    x = rng2.normal(50, 10, 50).tolist()
    y = [xi * 0.7 + rng2.normal(0, 3) for xi in x]

    pearson_results = []
    for _ in range(n_runs):
        r = pearson_r(x, y)
        pearson_results.append(round(r, 15))

    results["pearson_deterministic"] = {
        "all_identical": len(set(pearson_results)) == 1,
        "n_runs": n_runs,
    }

    # Run Fisher z n_runs times
    fisher_results = []
    for _ in range(n_runs):
        z = fisher_z(0.7)
        fisher_results.append(round(z, 15))

    results["fisher_z_deterministic"] = {
        "all_identical": len(set(fisher_results)) == 1,
        "n_runs": n_runs,
    }

    # Run Bonferroni n_runs times
    p_vals = [0.001, 0.01, 0.05, 0.10]
    bonf_results = []
    for _ in range(n_runs):
        res = StatisticalInferenceEngine.bonferroni(p_vals, alpha=0.05, family_id="det_test")
        bonf_results.append((tuple(round(p, 15) for p in res.adjusted_p_values), tuple(res.reject)))

    results["bonferroni_deterministic"] = {
        "all_identical": len(set(bonf_results)) == 1,
        "n_runs": n_runs,
    }

    # Run effect size computation n_runs times
    rng3 = np.random.default_rng(seed)
    a = rng3.normal(50, 10, 100)
    b = rng3.normal(55, 10, 100)

    es_results = []
    for _ in range(n_runs):
        d = cohens_d(a, b)
        es_results.append(round(d.value, 15))

    results["effect_size_deterministic"] = {
        "all_identical": len(set(es_results)) == 1,
        "n_runs": n_runs,
    }

    # Run power analysis n_runs times
    pow_results = []
    for _ in range(n_runs):
        p = power_ks_test(30, 30, 0.5, 0.05)
        pow_results.append(round(p, 15))

    results["power_deterministic"] = {
        "all_identical": len(set(pow_results)) == 1,
        "n_runs": n_runs,
    }

    # Full pipeline determinism: generate + detect + diagnose
    pipeline_results = []
    for _ in range(n_runs):
        ds = generate_d01_medium_drift(seed=seed)
        cal = calibrate_d01(ds)
        pipeline_results.append(
            (
                round(cal.ks_statistic, 15),
                round(cal.raw_p_value, 15),
                round(cal.effect_size, 15),
                cal.observed_detected,
            )
        )

    results["full_pipeline_deterministic"] = {
        "all_identical": len(set(pipeline_results)) == 1,
        "n_runs": n_runs,
    }

    all_deterministic = all(v["all_identical"] for v in results.values())
    results["overall_deterministic"] = all_deterministic

    return results


# ---------------------------------------------------------------------------
# Phase 9: Performance Assessment
# ---------------------------------------------------------------------------


def assess_performance() -> Dict[str, Any]:
    """Measure runtime, memory, and throughput of statistical operations."""
    results = {}

    # D-01 calibration timing
    ds = generate_d01_medium_drift()
    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        calibrate_d01(ds)
        times.append((time.perf_counter() - t0) * 1000.0)
    results["d01_calibration"] = {
        "mean_ms": round(np.mean(times), 3),
        "median_ms": round(np.median(times), 3),
        "p95_ms": round(np.percentile(times, 95), 3),
        "min_ms": round(np.min(times), 3),
        "max_ms": round(np.max(times), 3),
    }

    # D-02 calibration timing
    ds_corr = generate_d02_medium_weakening()
    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        calibrate_d02(ds_corr)
        times.append((time.perf_counter() - t0) * 1000.0)
    results["d02_calibration"] = {
        "mean_ms": round(np.mean(times), 3),
        "median_ms": round(np.median(times), 3),
        "p95_ms": round(np.percentile(times, 95), 3),
    }

    # D-03 calibration timing (slower due to bootstrap)
    ds_thresh = generate_d03_moderate_compression()
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        calibrate_d03(ds_thresh)
        times.append((time.perf_counter() - t0) * 1000.0)
    results["d03_calibration"] = {
        "mean_ms": round(np.mean(times), 3),
        "median_ms": round(np.median(times), 3),
        "p95_ms": round(np.percentile(times, 95), 3),
    }

    # Effect size computation timing
    rng = np.random.default_rng(42)
    x = rng.normal(50, 10, 200)
    y = rng.normal(55, 10, 200)
    times = []
    for _ in range(50):
        t0 = time.perf_counter()
        cohens_d(x, y)
        cliffs_delta(x, y)
        ks_effect_size(x, y)
        times.append((time.perf_counter() - t0) * 1000.0)
    results["effect_sizes_batch"] = {
        "mean_ms": round(np.mean(times), 3),
        "p95_ms": round(np.percentile(times, 95), 3),
    }

    # Power analysis timing
    times = []
    for _ in range(50):
        t0 = time.perf_counter()
        power_ks_test(30, 30, 0.5, 0.05)
        power_t_test(30, 0.5, 0.05)
        power_correlation_test(30, 0.5, 0.05)
        times.append((time.perf_counter() - t0) * 1000.0)
    results["power_analysis_batch"] = {
        "mean_ms": round(np.mean(times), 3),
        "p95_ms": round(np.percentile(times, 95), 3),
    }

    # Correction method timing
    p_vals = list(np.random.default_rng(42).uniform(0, 1, 20))
    times = []
    for _ in range(50):
        t0 = time.perf_counter()
        StatisticalInferenceEngine.bonferroni(p_vals, alpha=0.05)
        StatisticalInferenceEngine.holm(p_vals, alpha=0.05)
        StatisticalInferenceEngine.benjamini_hochberg(p_vals, alpha=0.05)
        times.append((time.perf_counter() - t0) * 1000.0)
    results["correction_methods_batch"] = {
        "mean_ms": round(np.mean(times), 3),
        "p95_ms": round(np.percentile(times, 95), 3),
    }

    # Full campaign timing
    t0 = time.perf_counter()
    all_datasets = generate_all_datasets()
    for ds_id, ds in all_datasets.items():
        if ds.detector_target in ("D-01", "all"):
            calibrate_d01(ds)
        if ds.detector_target in ("D-02", "all"):
            calibrate_d02(ds)
        if ds.detector_target in ("D-03", "all"):
            calibrate_d03(ds)
    campaign_time = (time.perf_counter() - t0) * 1000.0
    results["full_campaign"] = {
        "total_ms": round(campaign_time, 3),
        "total_sec": round(campaign_time / 1000, 3),
        "datasets_processed": len(all_datasets),
    }

    return results


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------


def run_full_calibration(seed: int = 42) -> Dict[str, Any]:
    """Run the complete PR-16C calibration campaign."""
    print("=" * 72)
    print("PR-16C: Statistical Calibration & Certification Campaign")
    print("=" * 72)
    print(f"Seed: {seed}")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print()

    output = {}

    # Phase 2: Generate all datasets
    print("[Phase 2] Generating synthetic datasets...")
    all_datasets = generate_all_datasets(seed)
    output["phase2_datasets"] = {
        "total": len(all_datasets),
        "by_detector": {
            "D-01": sum(1 for d in all_datasets.values() if d.detector_target in ("D-01", "all")),
            "D-02": sum(1 for d in all_datasets.values() if d.detector_target in ("D-02", "all")),
            "D-03": sum(1 for d in all_datasets.values() if d.detector_target in ("D-03", "all")),
        },
        "dataset_ids": list(all_datasets.keys()),
    }
    print(f"  Generated {len(all_datasets)} datasets")

    # Phase 3: Detector Calibration
    print("\n[Phase 3] Detector Calibration...")
    d01_results = []
    d02_results = []
    d03_results = []

    for ds_id, ds in all_datasets.items():
        if ds.detector_target in ("D-01", "all"):
            r = calibrate_d01(ds)
            d01_results.append(r)
        if ds.detector_target in ("D-02", "all"):
            r = calibrate_d02(ds)
            d02_results.append(r)
        if ds.detector_target in ("D-03", "all"):
            r = calibrate_d03(ds)
            d03_results.append(r)

    def compute_confusion(results: List[DetectorCalibrationResult]) -> Dict[str, int]:
        tp = sum(1 for r in results if r.tp)
        fp = sum(1 for r in results if r.fp)
        fn = sum(1 for r in results if r.fn)
        tn = sum(1 for r in results if r.tn)
        return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}

    def compute_pr(cm: Dict[str, int]) -> Dict[str, float]:
        tp, fp, tn, fn = cm["tp"], cm["fp"], cm["tn"], cm["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
            "fpr": round(fpr, 4),
        }

    cm_d01 = compute_confusion(d01_results)
    cm_d02 = compute_confusion(d02_results)
    cm_d03 = compute_confusion(d03_results)

    metrics_d01 = compute_pr(cm_d01)
    metrics_d02 = compute_pr(cm_d02)
    metrics_d03 = compute_pr(cm_d03)

    # IMP 1.6 targets
    HARD_TARGETS = {
        "D-01": {"precision": 0.80, "recall": 0.75},
        "D-02": {"precision": 0.75, "recall": 0.70},
        "D-03": {"precision": 0.85, "recall": 0.80},
    }

    targets_met = {}
    for det, m in [("D-01", metrics_d01), ("D-02", metrics_d02), ("D-03", metrics_d03)]:
        t = HARD_TARGETS[det]
        targets_met[det] = {
            "precision": m["precision"] >= t["precision"],
            "recall": m["recall"] >= t["recall"],
            "overall": m["precision"] >= t["precision"] and m["recall"] >= t["recall"],
        }

    output["phase3_detector_calibration"] = {
        "D-01": {"confusion_matrix": cm_d01, "metrics": metrics_d01, "targets_met": targets_met["D-01"]},
        "D-02": {"confusion_matrix": cm_d02, "metrics": metrics_d02, "targets_met": targets_met["D-02"]},
        "D-03": {"confusion_matrix": cm_d03, "metrics": metrics_d03, "targets_met": targets_met["D-03"]},
        "all_targets_met": all(t["overall"] for t in targets_met.values()),
    }

    for det in ["D-01", "D-02", "D-03"]:
        m = output["phase3_detector_calibration"][det]["metrics"]
        tm = "PASS" if targets_met[det]["overall"] else "FAIL"
        print(f"  {det}: P={m['precision']:.3f} R={m['recall']:.3f} -> {tm}")

    # Phase 4: Statistical Calibration
    print("\n[Phase 4] Statistical Calibration (correction methods)...")
    output["phase4_statistical_calibration"] = calibrate_correction_methods()
    print(f"  Monotonicity: {output['phase4_statistical_calibration']['monotonicity_preserved']}")

    # Phase 5: Effect Size Validation
    print("\n[Phase 5] Effect Size Validation...")
    output["phase5_effect_size"] = validate_effect_sizes()
    print(f"  Overall: {'PASS' if output['phase5_effect_size']['overall_pass'] else 'FAIL'}")

    # Phase 6: Power Validation
    print("\n[Phase 6] Power Validation...")
    output["phase6_power"] = validate_power()
    print(f"  Overall: {'PASS' if output['phase6_power']['overall_pass'] else 'FAIL'}")

    # Phase 7: Ground Truth Certification
    print("\n[Phase 7] Ground Truth Certification...")
    gt_certification = {}
    for ds_id, ds in all_datasets.items():
        expected = ds.anomaly_present
        # Determine which detector should fire
        if ds.detector_target == "D-01" or ds.detector_target == "all":
            cal = calibrate_d01(ds)
        elif ds.detector_target == "D-02":
            cal = calibrate_d02(ds)
        elif ds.detector_target == "D-03":
            cal = calibrate_d03(ds)
        else:
            continue

        correct = cal.observed_detected == expected
        gt_certification[ds_id] = {
            "expected_anomaly": expected,
            "observed_detected": cal.observed_detected,
            "correct": correct,
        }

    correct_count = sum(1 for v in gt_certification.values() if v["correct"])
    total_count = len(gt_certification)
    output["phase7_ground_truth"] = {
        "results": gt_certification,
        "correct": correct_count,
        "total": total_count,
        "accuracy": round(correct_count / total_count, 4) if total_count > 0 else 0.0,
        "certified": correct_count == total_count,
    }
    print(f"  Correct: {correct_count}/{total_count} ({output['phase7_ground_truth']['accuracy']:.1%})")

    # Phase 8: Determinism Verification
    print("\n[Phase 8] Determinism Verification...")
    output["phase8_determinism"] = verify_determinism(n_runs=10)
    print(
        f"  Overall: {'DETERMINISTIC' if output['phase8_determinism']['overall_deterministic'] else 'NON-DETERMINISTIC'}"
    )

    # Phase 9: Performance Assessment
    print("\n[Phase 9] Performance Assessment...")
    output["phase9_performance"] = assess_performance()
    print(f"  Full campaign: {output['phase9_performance']['full_campaign']['total_sec']:.2f}s")

    # Phase 10: Validation summary
    print("\n[Phase 10] Validation...")
    output["phase10_validation"] = {
        "determinism": output["phase8_determinism"]["overall_deterministic"],
        "detector_targets": output["phase3_detector_calibration"]["all_targets_met"],
        "effect_sizes": output["phase5_effect_size"]["overall_pass"],
        "power": output["phase6_power"]["overall_pass"],
        "ground_truth": output["phase7_ground_truth"]["certified"],
        "correction_monotonicity": output["phase4_statistical_calibration"]["monotonicity_preserved"],
    }

    # Overall verdict
    all_pass = all(output["phase10_validation"].values())
    output["verdict"] = "IMPLEMENTATION COMPLETE" if all_pass else "IMPLEMENTATION COMPLETE WITH FINDINGS"
    output["statistical_freeze_recommended"] = all_pass

    print("\n" + "=" * 72)
    print(f"VERDICT: {output['verdict']}")
    if all_pass:
        print("RECOMMENDATION: Declare STATISTICAL FREEZE before PR-17")
    print("=" * 72)

    return output


def save_results(output: Dict[str, Any], output_dir: Optional[Path] = None) -> None:
    """Save calibration results to disk."""
    out_dir = output_dir or OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # Main JSON summary
    with open(out_dir / "calibration_summary.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    # Per-phase CSVs
    # Detector calibration CSV
    if "phase3_detector_calibration" in output:
        rows = [
            "detector,precision,recall,f1,accuracy,fpr,tp,fp,fn,tn,target_precision,target_recall,precision_met,recall_met"
        ]
        for det in ["D-01", "D-02", "D-03"]:
            dc = output["phase3_detector_calibration"][det]
            m = dc["metrics"]
            cm = dc["confusion_matrix"]
            tm = dc["targets_met"]
            rows.append(
                f"{det},{m['precision']},{m['recall']},{m['f1']},{m['accuracy']},{m['fpr']},"
                f"{cm['tp']},{cm['fp']},{cm['fn']},{cm['tn']},"
                f"{HARD_TARGETS[det]['precision']},{HARD_TARGETS[det]['recall']},"
                f"{tm['precision']},{tm['recall']}"
            )
        with open(out_dir / "detector_calibration_matrix.csv", "w") as f:
            f.write("\n".join(rows))

    # Effect size validation CSV
    if "phase5_effect_size" in output:
        es = output["phase5_effect_size"]
        rows = ["test,observed,expected,tolerance,pass"]
        for key in ["identical_distributions", "known_shift_d05", "large_shift_d08"]:
            if key in es:
                r = es[key]
                rows.append(
                    f"{key},{r.get('cohens_d', 'N/A')},{r.get('expected', 'N/A')},{r.get('within_tolerance', 'N/A')},{r.get('within_tolerance', False)}"
                )
        with open(out_dir / "effect_size_validation.csv", "w") as f:
            f.write("\n".join(rows))

    # Power validation CSV
    if "phase6_power" in output:
        pw = output["phase6_power"]
        rows = ["test,pass,detail"]
        for key, val in pw.items():
            if key != "overall_pass" and isinstance(val, dict):
                rows.append(
                    f"{key},{val.get('monotonic', val.get('within_range', 'N/A'))},{json.dumps(val, cls=NumpyEncoder)}"
                )
        with open(out_dir / "power_validation.csv", "w") as f:
            f.write("\n".join(rows))

    print(f"\nResults saved to: {out_dir.resolve()}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

HARD_TARGETS = {
    "D-01": {"precision": 0.80, "recall": 0.75},
    "D-02": {"precision": 0.75, "recall": 0.70},
    "D-03": {"precision": 0.85, "recall": 0.80},
}


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="PR-16C Statistical Calibration & Certification Campaign")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_DIR),
        help="Output directory",
    )
    args = parser.parse_args()

    output = run_full_calibration(seed=args.seed)
    save_results(output, Path(args.output))

    return 0 if output.get("verdict") == "IMPLEMENTATION COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())
