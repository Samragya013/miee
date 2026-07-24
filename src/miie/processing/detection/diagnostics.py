"""
Detector Diagnostics Integration for MIIE v1.6.

Provides a shared helper to compute power, effect-size, and CI diagnostics
for each detector. Called from detector outputs to augment with statistical
diagnostics without changing detector mathematics.

Reference: SDV2 G-01, PR-16B
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np

from miie.processing.detection.effect_size import (
    cohens_d,
    ks_effect_size,
    rank_biserial,
)
from miie.processing.detection.power import (
    ci_width_correlation,
    ci_width_mean,
    ci_width_proportion,
    mde_correlation,
    mde_ks,
    power_correlation_test,
    power_ks_test,
    power_proportion_test,
    sample_size_correlation,
    sample_size_ks,
    sample_size_proportion,
)

# ---------------------------------------------------------------------------
# D-01: Distribution Drift Diagnostics
# ---------------------------------------------------------------------------


def d01_diagnostics(
    vals_start: List[float],
    vals_end: List[float],
    ks_stat: float,
    ks_p: float,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Compute diagnostics for a single D-01 KS test (one window pair).

    Args:
        vals_start: Values from the earlier window.
        vals_end: Values from the later window.
        ks_stat: Observed KS statistic.
        ks_p: Observed p-value.
        alpha: Significance level.

    Returns:
        Dict with effect_size, power, sample_adequacy, ci_diagnostic.
    """
    n1, n2 = len(vals_start), len(vals_end)
    n_total = n1 + n2

    # Effect sizes
    es_ks = ks_effect_size(np.array(vals_start), np.array(vals_end))
    es_d = cohens_d(np.array(vals_start), np.array(vals_end))

    # Power analysis
    observed_pow = power_ks_test(n1, n2, ks_stat, alpha)
    mde_at_n = mde_ks(min(n1, n2), alpha, 0.80)

    # Sample adequacy (Doc 09 §8.6: minimum 20 per window)
    min_per_window = 20
    adequate = n1 >= min_per_window and n2 >= min_per_window
    shortfall = 0
    if not adequate:
        shortfall = max(0, min_per_window - n1) + max(0, min_per_window - n2)

    # Required n for observed effect at 80% power
    if ks_stat > 0:
        required = sample_size_ks(ks_stat, alpha, 0.80)
    else:
        required = sample_size_ks(0.1, alpha, 0.80)

    # CI on mean difference
    mean_diff = float(np.mean(vals_end) - np.mean(vals_start))
    pooled_std = math.sqrt((np.var(vals_start, ddof=1) + np.var(vals_end, ddof=1)) / 2.0) if n1 > 1 and n2 > 1 else 1.0
    ci = ci_width_mean(mean_diff, pooled_std, n_total, 0.95)

    return {
        "effect_sizes": {
            "ks_d": es_ks.value,
            "ks_label": es_ks.label.value,
            "cohens_d": es_d.value,
            "cohens_d_label": es_d.label.value,
            "cohens_d_ci": [es_d.ci_lower, es_d.ci_upper] if es_d.ci_lower is not None else None,
        },
        "power_analysis": {
            "observed_power": round(observed_pow, 4),
            "observed_power_interpretation": (
                "Adequate"
                if observed_pow >= 0.80
                else "Moderate" if observed_pow >= 0.50 else "Low — high risk of Type II error"
            ),
            "mde_at_current_n": round(mde_at_n, 4),
            "mde_interpretation": (
                f"At n={min(n1, n2)}/group, can detect KS D ≥ {mde_at_n:.3f} " f"with 80% power at α={alpha}"
            ),
        },
        "sample_adequacy": {
            "n_group1": n1,
            "n_group2": n2,
            "min_required_per_window": min_per_window,
            "adequate": adequate,
            "shortfall": shortfall,
            "required_n_per_group_for_observed_effect": required.required_n,
            "recommendation": (
                "Sample is adequate" if adequate else f"Need {shortfall} more observations to meet minimum"
            ),
        },
        "ci_diagnostic": {
            "estimator": "mean_difference",
            "estimate": round(mean_diff, 4),
            "ci_lower": round(ci.ci_lower, 4),
            "ci_upper": round(ci.ci_upper, 4),
            "ci_width": round(ci.ci_width, 4),
            "precision": round(ci.precision, 4),
            "interpretation": ci.interpretation,
        },
        "summary": (
            f"KS D={es_ks.value:.3f} ({es_ks.label.value}), "
            f"power={observed_pow:.2f}, "
            f"{'adequate' if adequate else 'inadequate'} sample (n1={n1}, n2={n2})"
        ),
    }


# ---------------------------------------------------------------------------
# D-02: Correlation Breakdown Diagnostics
# ---------------------------------------------------------------------------


def d02_diagnostics(
    r: float,
    n: int,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Compute diagnostics for a single D-02 correlation test.

    Args:
        r: Observed Pearson correlation.
        n: Sample size.
        alpha: Significance level.

    Returns:
        Dict with effect_size, power, sample_adequacy, ci_diagnostic.
    """
    # Effect size
    _es_corr = rank_biserial(np.array([r]), np.array([0.0]))  # Placeholder; use correlation_effect_size for r
    abs_r = abs(r)

    # Power analysis
    observed_pow = power_correlation_test(n, abs_r, alpha)
    mde_at_n = mde_correlation(n, alpha, 0.80)

    # Sample adequacy (Doc 09 §8.6: minimum 10 per window)
    min_required = 10
    adequate = n >= min_required

    # Required n for observed effect at 80% power
    if abs_r > 0:
        required = sample_size_correlation(abs_r, alpha, 0.80)
    else:
        required = sample_size_correlation(0.1, alpha, 0.80)

    # CI diagnostic
    ci = ci_width_correlation(r, n, 0.95)

    # Interpretation of r (Cohen 1988, Doc 01 §6.9)
    if abs_r < 0.1:
        strength = "negligible"
    elif abs_r < 0.3:
        strength = "small"
    elif abs_r < 0.5:
        strength = "medium"
    else:
        strength = "large"

    return {
        "effect_sizes": {
            "pearson_r": round(r, 4),
            "r_squared": round(r**2, 4),
            "strength": strength,
            "variance_explained_pct": round(r**2 * 100, 1),
            "ci_lower": round(ci.ci_lower, 4) if ci.ci_lower is not None else None,
            "ci_upper": round(ci.ci_upper, 4) if ci.ci_upper is not None else None,
        },
        "power_analysis": {
            "observed_power": round(observed_pow, 4),
            "observed_power_interpretation": (
                "Adequate"
                if observed_pow >= 0.80
                else "Moderate" if observed_pow >= 0.50 else "Low — high risk of Type II error"
            ),
            "mde_at_current_n": round(mde_at_n, 4),
            "mde_interpretation": (f"At n={n}, can detect r ≥ {mde_at_n:.3f} " f"with 80% power at α={alpha}"),
        },
        "sample_adequacy": {
            "n": n,
            "min_required": min_required,
            "adequate": adequate,
            "required_n_for_observed_effect": required.required_n,
            "recommendation": ("Sample is adequate" if adequate else f"Need at least {min_required} observations"),
        },
        "ci_diagnostic": {
            "estimator": "correlation (Fisher z)",
            "estimate": round(r, 4),
            "ci_lower": round(ci.ci_lower, 4) if ci.ci_lower is not None else None,
            "ci_upper": round(ci.ci_upper, 4) if ci.ci_upper is not None else None,
            "ci_width": round(ci.ci_width, 4),
            "precision": round(ci.precision, 4),
            "interpretation": ci.interpretation,
        },
        "summary": (f"r={r:.3f} ({strength}), R²={r**2:.3f}, " f"power={observed_pow:.2f}, n={n}"),
    }


# ---------------------------------------------------------------------------
# D-03: Threshold Compression Diagnostics
# ---------------------------------------------------------------------------


def d03_diagnostics(
    vals: List[float],
    threshold: float,
    eps: float,
    z_score: float,
    dip_stat: float,
    dip_p: float,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Compute diagnostics for a single D-03 threshold test.

    Args:
        vals: Observation values.
        threshold: Hypothesized threshold.
        eps: Bandwidth epsilon.
        z_score: Observed excess mass z-score.
        dip_stat: Dip test statistic.
        dip_p: Dip test p-value.
        alpha: Significance level.

    Returns:
        Dict with effect_size, power, sample_adequacy, ci_diagnostic.
    """
    n = len(vals)
    arr = np.array(vals)

    # Compression index (effect size for D-03)
    in_band = int(np.sum(np.abs(arr - threshold) <= eps))
    p_hat = in_band / n if n > 0 else 0.0

    # Proportion test: H0: p=0.5, H1: p>0.5
    observed_pow = power_proportion_test(n, p_hat, 0.5, alpha)

    # MDE for proportion test
    se_null = math.sqrt(0.5 * 0.5 / n)
    mde = (1.645 + 0.84) * se_null  # z_alpha + z_beta approximation
    mde = min(mde, 1.0)

    # Sample adequacy (Doc 09 §8.6: minimum 20 per window)
    min_required = 20
    adequate = n >= min_required

    # Required n
    delta = abs(p_hat - 0.5)
    if delta > 0:
        required = sample_size_proportion(p_hat, 0.5, delta, alpha, 0.80)
    else:
        required = sample_size_proportion(0.6, 0.5, 0.1, alpha, 0.80)

    # CI on proportion
    ci = ci_width_proportion(n, p_hat, 0.95, "wilson")

    # Effect size interpretation
    if p_hat > 0.7:
        compression_label = "very large"
    elif p_hat > 0.5:
        compression_label = "large"
    elif p_hat > 0.3:
        compression_label = "medium"
    else:
        compression_label = "small"

    return {
        "effect_sizes": {
            "compression_index": round(p_hat, 4),
            "compression_label": compression_label,
            "bandwidth": round(eps, 4),
            "values_in_band": in_band,
            "values_total": n,
            "proportion_in_band": round(p_hat, 4),
        },
        "power_analysis": {
            "observed_power": round(observed_pow, 4),
            "observed_power_interpretation": (
                "Adequate"
                if observed_pow >= 0.80
                else "Moderate" if observed_pow >= 0.50 else "Low — high risk of Type II error"
            ),
            "mde_at_current_n": round(mde, 4),
            "mde_interpretation": (f"At n={n}, can detect |p - 0.5| ≥ {mde:.3f} " f"with 80% power at α={alpha}"),
        },
        "sample_adequacy": {
            "n": n,
            "min_required": min_required,
            "adequate": adequate,
            "required_n_for_observed_effect": required.required_n,
            "recommendation": ("Sample is adequate" if adequate else f"Need at least {min_required} observations"),
        },
        "ci_diagnostic": {
            "estimator": "proportion (Wilson)",
            "estimate": round(p_hat, 4),
            "ci_lower": round(ci.ci_lower, 4),
            "ci_upper": round(ci.ci_upper, 4),
            "ci_width": round(ci.ci_width, 4),
            "precision": round(ci.precision, 4),
            "interpretation": ci.interpretation,
        },
        "summary": (
            f"Compression index={p_hat:.3f} ({compression_label}), "
            f"z={z_score:.2f}, dip={dip_stat:.3f} (p={dip_p:.3f}), "
            f"power={observed_pow:.2f}, n={n}"
        ),
    }
