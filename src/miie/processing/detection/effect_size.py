"""
Effect Size Computation and Interpretation Framework for MIIE v1.6.

Provides reusable effect-size measures with structured interpretation bands.
Each measure follows the Doc 01 §6.9 conventions: interpretation bands are
[0, 0.2] small, [0.2, 0.5] medium, [0.5, 0.8] large, > 0.8 very large.

All functions are pure computations with no detector-specific state.

Reference: Doc 01 §6.9, Cohen 1988, SDV2 G-01, PR-16B
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np
from scipy import stats as sp_stats

# ---------------------------------------------------------------------------
# Interpretation bands (Doc 01 §6.9)
# ---------------------------------------------------------------------------


class EffectSizeLabel(Enum):
    """Standard interpretation labels for effect sizes."""

    NEGLIGIBLE = "negligible"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very large"


def interpret_effect_size(d: float, kind: str = "general") -> EffectSizeLabel:
    """Classify an absolute effect size into standard interpretation bands.

    Bands per Doc 01 §6.9:
        [0, 0.2]    -> small
        [0.2, 0.5]  -> medium
        [0.5, 0.8]  -> large
        > 0.8       -> very large

    For "general" kind, values < 0.01 are negligible.
    For "correlation" kind, thresholds are halved (r ≈ 0.1 small, 0.3 medium, 0.5 large).

    Args:
        d: Absolute effect size value (must be >= 0).
        kind: "general", "correlation", "ks", "cohens_d".

    Returns:
        EffectSizeLabel enum value.
    """
    d = abs(d)

    if kind == "correlation":
        if d < 0.1:
            return EffectSizeLabel.NEGLIGIBLE
        elif d < 0.3:
            return EffectSizeLabel.SMALL
        elif d < 0.5:
            return EffectSizeLabel.MEDIUM
        else:
            return EffectSizeLabel.LARGE
    else:
        if d < 0.01:
            return EffectSizeLabel.NEGLIGIBLE
        elif d <= 0.2:
            return EffectSizeLabel.SMALL
        elif d <= 0.5:
            return EffectSizeLabel.MEDIUM
        elif d <= 0.8:
            return EffectSizeLabel.LARGE
        else:
            return EffectSizeLabel.VERY_LARGE


# ---------------------------------------------------------------------------
# Dataclasses for structured results
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EffectSizeResult:
    """Structured effect size computation result.

    Attributes:
        name: Name of the effect size measure.
        value: Computed effect size.
        label: Interpretation label.
        ci_lower: Lower bound of 95% CI (if available).
        ci_upper: Upper bound of 95% CI (if available).
        interpretation: Human-readable interpretation sentence.
    """

    name: str
    value: float
    label: EffectSizeLabel
    ci_lower: Optional[float]
    ci_upper: Optional[float]
    interpretation: str


# ---------------------------------------------------------------------------
# Effect size functions
# ---------------------------------------------------------------------------


def cohens_d(x: np.ndarray, y: np.ndarray) -> EffectSizeResult:
    """Cohen's d for two independent samples (pooled standard deviation).

    d = (mean_x - mean_y) / s_pooled

    Reference: Cohen 1988, Doc 01 §6.9

    Args:
        x: Sample 1.
        y: Sample 2.

    Returns:
        EffectSizeResult with d and interpretation.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        return EffectSizeResult(
            name="Cohen's d",
            value=0.0,
            label=EffectSizeLabel.NEGLIGIBLE,
            ci_lower=None,
            ci_upper=None,
            interpretation="Insufficient data (n < 2 per group)",
        )

    m1, m2 = np.mean(x), np.mean(y)
    s1, s2 = np.var(x, ddof=1), np.var(y, ddof=1)

    # Pooled standard deviation
    s_pooled = math.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if s_pooled == 0:
        d_val = 0.0
    else:
        d_val = (m1 - m2) / s_pooled

    label = interpret_effect_size(d_val, kind="cohens_d")

    # Approximate 95% CI for d (Hedges & Olkin 1985)
    se_d = math.sqrt((n1 + n2) / (n1 * n2) + d_val**2 / (2 * (n1 + n2)))
    ci_lower = d_val - 1.96 * se_d
    ci_upper = d_val + 1.96 * se_d

    return EffectSizeResult(
        name="Cohen's d",
        value=d_val,
        label=label,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        interpretation=(
            f"Cohen's d = {d_val:.3f} ({label.value} effect). " f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]"
        ),
    )


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> EffectSizeResult:
    """Cliff's delta — non-parametric effect size for ordinal/continuous data.

    δ = (# times x > y - # times x < y) / (n1 * n2)

    Interpretation: |δ| < 0.147 small, < 0.33 medium, < 0.474 large, >= 0.474 very large
    (Vargha & Delaney 2000)

    Reference: Cliff 1993, Vargha & Delaney 2000, Doc 01 §6.9

    Args:
        x: Sample 1.
        y: Sample 2.

    Returns:
        EffectSizeResult with δ and interpretation.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    n1, n2 = len(x), len(y)
    if n1 < 1 or n2 < 1:
        return EffectSizeResult(
            name="Cliff's delta",
            value=0.0,
            label=EffectSizeLabel.NEGLIGIBLE,
            ci_lower=None,
            ci_upper=None,
            interpretation="Insufficient data",
        )

    # Count pairwise comparisons
    greater = 0.0
    less = 0.0
    for xi in x:
        greater += np.sum(xi > y)
        less += np.sum(xi < y)

    delta_val = (greater - less) / (n1 * n2)

    # Vargha & Delaney thresholds
    abs_d = abs(delta_val)
    if abs_d < 0.147:
        label = EffectSizeLabel.SMALL
    elif abs_d < 0.33:
        label = EffectSizeLabel.MEDIUM
    elif abs_d < 0.474:
        label = EffectSizeLabel.LARGE
    else:
        label = EffectSizeLabel.VERY_LARGE

    # Approximate 95% CI (bootstrap-like normal approximation)
    se = math.sqrt((n1 + n2 + 1) / (3 * n1 * n2))
    ci_lower = delta_val - 1.96 * se
    ci_upper = delta_val + 1.96 * se

    return EffectSizeResult(
        name="Cliff's delta",
        value=delta_val,
        label=label,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        interpretation=(
            f"Cliff's δ = {delta_val:.3f} ({label.value} effect). " f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]"
        ),
    )


def rank_biserial(x: np.ndarray, y: np.ndarray) -> EffectSizeResult:
    """Rank-biserial correlation — non-parametric association measure.

    r = 2 * δ / (1 + |δ|)  where δ is Cliff's delta.

    Reference: Kerby 2014, Doc 01 §6.9

    Args:
        x: Sample 1.
        y: Sample 2.

    Returns:
        EffectSizeResult with r and interpretation.
    """
    cliff = cliffs_delta(x, y)
    d_val = cliff.value
    r_val = 2.0 * d_val / (1.0 + abs(d_val)) if (1.0 + abs(d_val)) > 0 else 0.0

    label = interpret_effect_size(r_val, kind="correlation")

    return EffectSizeResult(
        name="Rank-biserial correlation",
        value=r_val,
        label=label,
        ci_lower=None,
        ci_upper=None,
        interpretation=(
            f"Rank-biserial r = {r_val:.3f} ({label.value} effect). " f"Derived from Cliff's δ = {d_val:.3f}"
        ),
    )


def ks_effect_size(
    x: np.ndarray,
    y: np.ndarray,
) -> EffectSizeResult:
    """KS statistic as an effect size measure.

    The KS D statistic directly measures the maximum difference between
    empirical CDFs. Doc 01 §6.9 interpretation bands:
    [0, 0.2] small, [0.2, 0.5] medium, [0.5, 0.8] large, > 0.8 very large.

    Reference: Doc 01 §6.9, Massey 1951

    Args:
        x: Sample 1.
        y: Sample 2.

    Returns:
        EffectSizeResult with D and interpretation.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if len(x) < 2 or len(y) < 2:
        return EffectSizeResult(
            name="KS effect size (D)",
            value=0.0,
            label=EffectSizeLabel.NEGLIGIBLE,
            ci_lower=None,
            ci_upper=None,
            interpretation="Insufficient data (n < 2 per group)",
        )

    d_stat, _ = sp_stats.ks_2samp(x, y)
    label = interpret_effect_size(d_stat, kind="ks")

    return EffectSizeResult(
        name="KS effect size (D)",
        value=d_stat,
        label=label,
        ci_lower=None,
        ci_upper=None,
        interpretation=(f"KS D = {d_stat:.3f} ({label.value} effect). " f"Maximum CDF divergence between groups"),
    )


def correlation_effect_size(r: float, n: int) -> EffectSizeResult:
    """Correlation effect size with R² and interpretation.

    Converts Pearson r to R² (coefficient of determination) and provides
    interpretation using Doc 01 §6.9 correlation bands:
    [0, 0.1] negligible, [0.1, 0.3] small, [0.3, 0.5] medium, > 0.5 large.

    Reference: Cohen 1988, Doc 01 §6.9

    Args:
        r: Pearson correlation coefficient.
        n: Sample size.

    Returns:
        EffectSizeResult with r and R².
    """
    r = max(-1.0, min(1.0, r))
    r2 = r**2
    abs_r = abs(r)

    label = interpret_effect_size(abs_r, kind="correlation")

    # Fisher z CI
    if n >= 4:
        z_r = 0.5 * math.log((1 + r) / (1 - r))
        se = 1.0 / math.sqrt(n - 3)
        ci_lower = math.tanh(z_r - 1.96 * se)
        ci_upper = math.tanh(z_r + 1.96 * se)
    else:
        ci_lower = None
        ci_upper = None

    return EffectSizeResult(
        name="Correlation effect size",
        value=r,
        label=label,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        interpretation=(
            f"r = {r:.3f}, R² = {r2:.3f} ({label.value} effect). "
            f"Explains {r2*100:.1f}% of variance"
            + (f". 95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]" if ci_lower is not None else "")
        ),
    )


def jensen_shannon_divergence(
    x: np.ndarray,
    y: np.ndarray,
    bins: int = 20,
) -> EffectSizeResult:
    """Jensen-Shannon divergence as a distribution effect size.

    JSD is a symmetric, bounded [0, 1] measure of distribution difference.
    sqrt(JSD) is a metric (Lin 1991).

    Reference: Lin 1991, Doc 01 §6.9

    Args:
        x: Sample 1.
        y: Sample 2.
        bins: Number of bins for histogram estimation.

    Returns:
        EffectSizeResult with JSD and interpretation.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if len(x) < 2 or len(y) < 2:
        return EffectSizeResult(
            name="Jensen-Shannon divergence",
            value=0.0,
            label=EffectSizeLabel.NEGLIGIBLE,
            ci_lower=None,
            ci_upper=None,
            interpretation="Insufficient data (n < 2 per group)",
        )

    # Common bin edges
    all_data = np.concatenate([x, y])
    lo, hi = np.min(all_data), np.max(all_data)
    if lo == hi:
        return EffectSizeResult(
            name="Jensen-Shannon divergence",
            value=0.0,
            label=EffectSizeLabel.NEGLIGIBLE,
            ci_lower=None,
            ci_upper=None,
            interpretation="Identical distributions (zero variance)",
        )

    edges = np.linspace(lo, hi, bins + 1)
    hist_x, _ = np.histogram(x, bins=edges, density=True)
    hist_y, _ = np.histogram(y, bins=edges, density=True)

    # Normalize to probability distributions
    dx = edges[1] - edges[0]
    px = hist_x * dx
    py = hist_y * dx

    # Avoid log(0) by adding epsilon
    eps = 1e-10
    px = px + eps
    py = py + eps

    # Renormalize
    px = px / px.sum()
    py = py / py.sum()

    # M = (P + Q) / 2
    pm = (px + py) / 2.0

    # JSD = 0.5 * D_KL(P || M) + 0.5 * D_KL(Q || M)
    jsd = 0.5 * np.sum(px * np.log(px / pm)) + 0.5 * np.sum(py * np.log(py / pm))
    jsd = float(jsd)

    # sqrt(JSD) for metric property
    jsd_metric = math.sqrt(jsd)

    label = interpret_effect_size(jsd_metric, kind="general")

    return EffectSizeResult(
        name="Jensen-Shannon divergence",
        value=jsd,
        label=label,
        ci_lower=None,
        ci_upper=None,
        interpretation=(
            f"JSD = {jsd:.4f}, √JSD = {jsd_metric:.3f} ({label.value} effect). "
            f"{'Distributions are similar' if jsd < 0.05 else 'Distributions differ'}"
        ),
    )


def effect_size_summary(
    x: np.ndarray,
    y: np.ndarray,
) -> dict:
    """Compute a comprehensive effect size summary for two samples.

    Returns all applicable measures in a single dict, suitable for
    inclusion in detector output metadata.

    Args:
        x: Sample 1.
        y: Sample 2.

    Returns:
        Dict with keys: cohens_d, cliffs_delta, rank_biserial, ks_d,
        jensen_shannon, and interpretation summary.
    """
    d = cohens_d(x, y)
    cliff = cliffs_delta(x, y)
    rb = rank_biserial(x, y)
    ks = ks_effect_size(x, y)
    jsd = jensen_shannon_divergence(x, y)

    # Overall assessment — worst-case label
    labels = [d.label, cliff.label, ks.label, jsd.label]
    priority = {
        EffectSizeLabel.NEGLIGIBLE: 0,
        EffectSizeLabel.SMALL: 1,
        EffectSizeLabel.MEDIUM: 2,
        EffectSizeLabel.LARGE: 3,
        EffectSizeLabel.VERY_LARGE: 4,
    }
    overall = max(labels, key=lambda lab: priority[lab])

    return {
        "cohens_d": d,
        "cliffs_delta": cliff,
        "rank_biserial": rb,
        "ks_effect_size": ks,
        "jensen_shannon": jsd,
        "overall_label": overall,
        "summary": (
            f"Effect sizes: d={d.value:.3f} ({d.label.value}), "
            f"δ={cliff.value:.3f} ({cliff.label.value}), "
            f"KS D={ks.value:.3f} ({ks.label.value}), "
            f"√JSD={math.sqrt(jsd.value):.3f} ({jsd.label.value}). "
            f"Overall: {overall.value}"
        ),
    }
