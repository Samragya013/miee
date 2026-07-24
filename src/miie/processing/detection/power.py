"""
Statistical Power Analysis Framework for MIIE v1.6.

Provides reusable utilities for power estimation, sample size determination,
minimum detectable effect (MDE) calculation, and confidence interval
diagnostics. Resolves SDV2 Finding G-01 (no formal power analysis).

All functions are pure computations with no detector-specific state.
Each documents its mathematical basis, assumptions, and limitations.

Reference: Doc 01 §6.10, Doc 09 §8, SDV2 G-01, PR-16B
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.stats import norm

# ---------------------------------------------------------------------------
# Dataclasses for structured results
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PowerAnalysisResult:
    """Result of a statistical power analysis.

    Attributes:
        test_name: Name of the statistical test.
        effect_size: Assumed or observed effect size.
        sample_size: Sample size (per group for two-sample tests).
        alpha: Significance level.
        power: Statistical power (1 - beta).
        beta: Type II error rate.
        mde: Minimum detectable effect at target power.
        interpretation: Human-readable interpretation.
    """

    test_name: str
    effect_size: float
    sample_size: int
    alpha: float
    power: float
    beta: float
    mde: float
    interpretation: str


@dataclass(frozen=True)
class SampleSizeResult:
    """Result of a sample size estimation.

    Attributes:
        test_name: Name of the statistical test.
        effect_size: Target effect size.
        alpha: Significance level.
        target_power: Desired statistical power.
        required_n: Required sample size per group.
        interpretation: Human-readable interpretation.
    """

    test_name: str
    effect_size: float
    alpha: float
    target_power: float
    required_n: int
    interpretation: str


@dataclass(frozen=True)
class CIDiagnosticResult:
    """Confidence interval diagnostic result.

    Attributes:
        estimator: Name of the estimator.
        estimate: Point estimate.
        ci_lower: Lower CI bound.
        ci_upper: Upper CI bound.
        ci_width: Width of the CI.
        confidence: Confidence level.
        precision: 1 - ci_width (narrower = more precise).
        interpretation: Human-readable interpretation.
    """

    estimator: str
    estimate: float
    ci_lower: float
    ci_upper: float
    ci_width: float
    confidence: float
    precision: float
    interpretation: str


# ---------------------------------------------------------------------------
# Power functions
# ---------------------------------------------------------------------------


def power_ks_test(
    n1: int,
    n2: int,
    d: float,
    alpha: float = 0.05,
) -> float:
    """Approximate power for the Kolmogorov-Smirnov two-sample test.

    Uses the asymptotic approximation: under H1 with effect size d,
    the KS statistic is approximately N(d, d*(1-d)*(n1+n2)/(n1*n2)).
    Power is computed as P(reject H0 | H1 true).

    Reference: Doc 01 §6.6, Conover 1971, Ledoux & Rosenblatt 1997

    Args:
        n1: Sample size of group 1.
        n2: Sample size of group 2.
        d: Effect size (KS D statistic under H1). Must be in (0, 1].
        alpha: Significance level (default 0.05).

    Returns:
        Power estimate in [0, 1]. Returns 0.0 for invalid inputs.
    """
    if n1 < 2 or n2 < 2 or d <= 0 or d > 1.0 or alpha <= 0 or alpha >= 1:
        return 0.0

    n_eff = (n1 * n2) / (n1 + n2)

    # Under H0: KS ~ sqrt(-log(alpha/2) / (2*n_eff)) (approximate critical value)
    # Under H1: KS ≈ d with variance d*(1-d)/n_eff
    se_d = math.sqrt(d * (1.0 - d) / n_eff)

    if se_d == 0:
        return 1.0

    # Critical value under H0 (approximate)
    k_crit = math.sqrt(-math.log(alpha / 2.0) / (2.0 * n_eff))

    # Power = P(KS > k_crit | H1) = P(Z > (k_crit - d) / se_d)
    z_power = (k_crit - d) / se_d
    power = 1.0 - norm.cdf(z_power)
    return max(0.0, min(1.0, power))


def power_t_test(
    n: int,
    d: float,
    alpha: float = 0.05,
    two_sample: bool = True,
    alternative: str = "two-sided",
) -> float:
    """Power for a one-sample or two-sample t-test given Cohen's d.

    Uses the non-central t-distribution approximation. For two-sample tests,
    n is the sample size per group.

    Reference: Cohen 1988, Doc 09 §8.4

    Args:
        n: Sample size (per group for two_sample=True, total for False).
        d: Cohen's d effect size.
        alpha: Significance level (default 0.05).
        two_sample: True for two-sample test, False for one-sample.
        alternative: "two-sided" or "one-sided".

    Returns:
        Power estimate in [0, 1].
    """
    if n < 2 or d == 0 or alpha <= 0 or alpha >= 1:
        return 0.0

    if two_sample:
        ncp = d * math.sqrt(n / 2.0)
        df = 2 * (n - 1)
    else:
        ncp = d * math.sqrt(n)
        df = n - 1

    if df < 1:
        return 0.0

    if alternative == "two-sided":
        t_crit = norm.ppf(1 - alpha / 2.0)
    else:
        t_crit = norm.ppf(1 - alpha)

    # Power via normal approximation (accurate for df > 30)
    if df > 30:
        z_alpha = t_crit
        power = 1.0 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)
    else:
        # For small df, use non-central t approximation via simulation-free method
        # Approximate: power ≈ Φ(ncp - z_alpha) for one-sided
        if alternative == "two-sided":
            power = 1.0 - norm.cdf(t_crit - ncp) + norm.cdf(-t_crit - ncp)
        else:
            power = 1.0 - norm.cdf(t_crit - ncp)

    return max(0.0, min(1.0, power))


def power_correlation_test(
    n: int,
    rho: float,
    alpha: float = 0.05,
) -> float:
    """Power for testing H0: ρ = 0 using Fisher z-transform.

    Under H1 with true correlation ρ, the Fisher z-transformed statistic
    is approximately N(fisher_z(ρ), 1/(n-3)). Power is computed as
    P(|Z_obs| > z_crit | H1 true).

    Reference: Doc 01 §6.4, Doc 09 §8.4, Cohen 1988

    Args:
        n: Sample size (must be >= 4).
        rho: True population correlation under H1.
        alpha: Significance level (default 0.05).

    Returns:
        Power estimate in [0, 1].
    """
    if n < 4 or alpha <= 0 or alpha >= 1:
        return 0.0

    rho = max(-1.0 + 1e-10, min(1.0 - 1e-10, rho))

    z_crit = norm.ppf(1 - alpha / 2.0)
    se = 1.0 / math.sqrt(n - 3)

    # Fisher z of true rho
    z_rho = 0.5 * math.log((1 + rho) / (1 - rho))

    # Power = P(|Z| > z_crit | rho)
    # Z_obs ~ N(z_rho, se)
    power = 1.0 - norm.cdf(z_crit - z_rho / se) + norm.cdf(-z_crit - z_rho / se)
    return max(0.0, min(1.0, power))


def power_proportion_test(
    n: int,
    p: float,
    p0: float,
    alpha: float = 0.05,
) -> float:
    """Power for a one-sample proportion test (z-test).

    Tests H0: p = p0 against H1: p ≠ p0.

    Reference: Doc 09 §8.4, Fleiss 1981

    Args:
        n: Sample size.
        p: True proportion under H1.
        p0: Null hypothesis proportion.
        alpha: Significance level (default 0.05).

    Returns:
        Power estimate in [0, 1].
    """
    if n < 2 or p <= 0 or p >= 1 or p0 <= 0 or p0 >= 1 or alpha <= 0 or alpha >= 1:
        return 0.0

    se_null = math.sqrt(p0 * (1 - p0) / n)
    se_alt = math.sqrt(p * (1 - p) / n)

    if se_null == 0 or se_alt == 0:
        return 0.0

    z_crit = norm.ppf(1 - alpha / 2.0)

    # Non-centrality parameter
    _ncp = abs(p - p0) / se_null

    # Power = P(|Z| > z_crit | H1)
    # Under H1: Z ~ N(ncp, se_alt/se_null ratio)
    z_shift = (p - p0) / se_null
    power = 1.0 - norm.cdf(z_crit - z_shift) + norm.cdf(-z_crit - z_shift)
    return max(0.0, min(1.0, power))


def observed_power(
    p_value: float,
    n: int,
    alpha: float = 0.05,
    test_type: str = "z",
) -> float:
    """Post-hoc (observed) power from an observed p-value.

    WARNING: Post-hoc power is controversial and should be interpreted
    with caution. It is provided for diagnostic purposes only, following
    the convention in Doc 09 §8. Observed power = P(reject H0 | effect
    equal to the observed effect).

    Reference: Hoenig & Heisey 2001, Doc 09 §8

    Args:
        p_value: Observed p-value.
        n: Sample size used in the test.
        alpha: Significance level.
        test_type: "z" (z-test), "t" (t-test), "correlation", "ks".

    Returns:
        Observed power in [0, 1]. Labelled clearly as post-hoc.
    """
    if p_value <= 0 or p_value >= 1 or n < 2 or alpha <= 0 or alpha >= 1:
        return 0.0

    z_crit = norm.ppf(1 - alpha / 2.0)

    # Convert p-value to observed z
    z_obs = norm.ppf(1 - p_value / 2.0)

    # Power = P(|Z| > z_crit | effect = observed)
    power = 1.0 - norm.cdf(z_crit - z_obs) + norm.cdf(-z_crit - z_obs)
    return max(0.0, min(1.0, power))


# ---------------------------------------------------------------------------
# Sample size estimation
# ---------------------------------------------------------------------------


def sample_size_ks(
    d: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> SampleSizeResult:
    """Required sample size per group for KS test to detect effect d.

    Uses the asymptotic approximation: n ≈ -log(alpha/2) / (2*d²)
    adjusted for power via the non-centrality parameter.

    Reference: Conover 1971, Doc 09 §8.4

    Args:
        d: Target effect size (KS D statistic). Must be > 0.
        alpha: Significance level (default 0.05).
        power: Target power (default 0.80).

    Returns:
        SampleSizeResult with required_n per group.
    """
    if d <= 0 or alpha <= 0 or alpha >= 1 or power <= 0 or power >= 1:
        return SampleSizeResult(
            test_name="KS two-sample",
            effect_size=d,
            alpha=alpha,
            target_power=power,
            required_n=0,
            interpretation="Invalid parameters",
        )

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    # Approximate: n per group ≈ (z_alpha + z_beta)² / (2 * d²)
    n = math.ceil((z_alpha + z_beta) ** 2 / (2.0 * d * d))

    # Ensure minimum for KS asymptotic validity
    n = max(n, 10)

    return SampleSizeResult(
        test_name="KS two-sample",
        effect_size=d,
        alpha=alpha,
        target_power=power,
        required_n=n,
        interpretation=(
            f"Need {n} observations per group to detect KS D={d:.3f} " f"with {power*100:.0f}% power at α={alpha}"
        ),
    )


def sample_size_t_test(
    d: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sample: bool = True,
) -> SampleSizeResult:
    """Required sample size for t-test given Cohen's d.

    Reference: Cohen 1988, Doc 09 §8.4

    Args:
        d: Target Cohen's d. Must be > 0.
        alpha: Significance level (default 0.05).
        power: Target power (default 0.80).
        two_sample: True for two-sample, False for one-sample.

    Returns:
        SampleSizeResult with required_n.
    """
    if d <= 0 or alpha <= 0 or alpha >= 1 or power <= 0 or power >= 1:
        return SampleSizeResult(
            test_name="t-test",
            effect_size=d,
            alpha=alpha,
            target_power=power,
            required_n=0,
            interpretation="Invalid parameters",
        )

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    if two_sample:
        n = math.ceil(2.0 * ((z_alpha + z_beta) / d) ** 2)
    else:
        n = math.ceil(((z_alpha + z_beta) / d) ** 2)

    n = max(n, 5)

    label = "two-sample" if two_sample else "one-sample"
    return SampleSizeResult(
        test_name=f"t-test ({label})",
        effect_size=d,
        alpha=alpha,
        target_power=power,
        required_n=n,
        interpretation=(
            f"Need {n} observations to detect Cohen's d={d:.3f} " f"with {power*100:.0f}% power at α={alpha} ({label})"
        ),
    )


def sample_size_correlation(
    r: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> SampleSizeResult:
    """Required sample size for testing H0: ρ = 0.

    Uses Fisher z-transform approximation: n ≈ [(z_α/2 + z_β) / (0.5 * ln((1+r)/(1-r)))]² + 3

    Reference: Cohen 1988, Doc 09 §8.4

    Args:
        r: Target correlation to detect. Must be in (0, 1).
        alpha: Significance level (default 0.05).
        power: Target power (default 0.80).

    Returns:
        SampleSizeResult with required_n.
    """
    if r <= 0 or r >= 1 or alpha <= 0 or alpha >= 1 or power <= 0 or power >= 1:
        return SampleSizeResult(
            test_name="Correlation (Fisher z)",
            effect_size=r,
            alpha=alpha,
            target_power=power,
            required_n=0,
            interpretation="Invalid parameters",
        )

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    # Fisher z-transform of r
    z_r = 0.5 * math.log((1 + r) / (1 - r))

    n = math.ceil(((z_alpha + z_beta) / z_r) ** 2 + 3)
    n = max(n, 4)

    return SampleSizeResult(
        test_name="Correlation (Fisher z)",
        effect_size=r,
        alpha=alpha,
        target_power=power,
        required_n=n,
        interpretation=(f"Need {n} observations to detect r={r:.3f} " f"with {power*100:.0f}% power at α={alpha}"),
    )


def sample_size_proportion(
    p: float,
    p0: float,
    delta: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> SampleSizeResult:
    """Required sample size for proportion test.

    Reference: Fleiss 1981, Doc 09 §8.4

    Args:
        p: Expected proportion under H1.
        p0: Null hypothesis proportion.
        delta: Minimum detectable difference |p - p0|.
        alpha: Significance level (default 0.05).
        power: Target power (default 0.80).

    Returns:
        SampleSizeResult with required_n.
    """
    if delta <= 0 or p <= 0 or p >= 1 or p0 <= 0 or p0 >= 1:
        return SampleSizeResult(
            test_name="Proportion z-test",
            effect_size=delta,
            alpha=alpha,
            target_power=power,
            required_n=0,
            interpretation="Invalid parameters",
        )

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    p_bar = (p + p0) / 2.0
    n = math.ceil(
        ((z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p * (1 - p) + p0 * (1 - p0))) / delta) ** 2
    )
    n = max(n, 10)

    return SampleSizeResult(
        test_name="Proportion z-test",
        effect_size=delta,
        alpha=alpha,
        target_power=power,
        required_n=n,
        interpretation=(
            f"Need {n} observations to detect δ={delta:.3f} "
            f"(p={p:.2f} vs p0={p0:.2f}) with {power*100:.0f}% power at α={alpha}"
        ),
    )


# ---------------------------------------------------------------------------
# Minimum detectable effect
# ---------------------------------------------------------------------------


def mde_ks(
    n: int,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Minimum detectable KS effect size for given sample size.

    Inverts the power function to find the smallest d such that
    power(d, n, alpha) >= target_power.

    Args:
        n: Sample size per group.
        alpha: Significance level.
        power: Target power.

    Returns:
        Minimum detectable effect size d.
    """
    if n < 2 or alpha <= 0 or alpha >= 1 or power <= 0 or power >= 1:
        return 1.0

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    d = (z_alpha + z_beta) / math.sqrt(n / 2.0)
    return max(0.0, min(1.0, d))


def mde_t_test(
    n: int,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sample: bool = True,
) -> float:
    """Minimum detectable Cohen's d for given sample size.

    Reference: Cohen 1988

    Args:
        n: Sample size (per group if two_sample).
        alpha: Significance level.
        power: Target power.
        two_sample: True for two-sample.

    Returns:
        Minimum detectable Cohen's d.
    """
    if n < 2 or alpha <= 0 or alpha >= 1 or power <= 0 or power >= 1:
        return 1.0

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    if two_sample:
        d = (z_alpha + z_beta) / math.sqrt(n / 2.0)
    else:
        d = (z_alpha + z_beta) / math.sqrt(n)

    return max(0.0, d)


def mde_correlation(
    n: int,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Minimum detectable correlation for given sample size.

    Inverts Fisher z power: MDE r = tanh((z_α/2 + z_β) / √(n-3))

    Args:
        n: Sample size.
        alpha: Significance level.
        power: Target power.

    Returns:
        Minimum detectable correlation r.
    """
    if n < 4 or alpha <= 0 or alpha >= 1 or power <= 0 or power >= 1:
        return 1.0

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    z_r = (z_alpha + z_beta) / math.sqrt(n - 3)
    r = math.tanh(z_r)
    return max(0.0, min(1.0, r))


def mde_proportion(
    n: int,
    p0: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Minimum detectable proportion difference for given sample size.

    Args:
        n: Sample size.
        p0: Null hypothesis proportion.
        alpha: Significance level.
        power: Target power.

    Returns:
        Minimum detectable |p - p0|.
    """
    if n < 2 or p0 <= 0 or p0 >= 1 or alpha <= 0 or alpha >= 1 or power <= 0 or power >= 1:
        return 1.0

    z_alpha = norm.ppf(1 - alpha / 2.0)
    z_beta = norm.ppf(power)

    se = math.sqrt(p0 * (1 - p0) / n)
    delta = (z_alpha + z_beta) * se
    return max(0.0, min(1.0, delta))


# ---------------------------------------------------------------------------
# Confidence interval diagnostics
# ---------------------------------------------------------------------------


def ci_width_proportion(
    n: int,
    p: float,
    confidence: float = 0.95,
    method: str = "wilson",
) -> CIDiagnosticResult:
    """Confidence interval width and precision for a proportion.

    Args:
        n: Sample size.
        p: Observed proportion.
        confidence: Confidence level.
        method: "wilson" (score) or "wald" (normal approximation).

    Returns:
        CIDiagnosticResult with width and precision diagnostics.
    """
    if n < 1 or p < 0 or p > 1 or confidence <= 0 or confidence >= 1:
        return CIDiagnosticResult(
            estimator="proportion",
            estimate=p,
            ci_lower=0.0,
            ci_upper=1.0,
            ci_width=1.0,
            confidence=confidence,
            precision=0.0,
            interpretation="Invalid parameters",
        )

    z_crit = norm.ppf(1 - (1 - confidence) / 2.0)

    if method == "wilson":
        denom = 1 + z_crit**2 / n
        center = (p + z_crit**2 / (2 * n)) / denom
        spread = z_crit * math.sqrt((p * (1 - p) / n + z_crit**2 / (4 * n**2))) / denom
        lower = max(0.0, center - spread)
        upper = min(1.0, center + spread)
    else:
        se = math.sqrt(p * (1 - p) / n)
        lower = max(0.0, p - z_crit * se)
        upper = min(1.0, p + z_crit * se)

    width = upper - lower
    precision = 1.0 - width

    if width < 0.05:
        interp = "High precision (narrow CI)"
    elif width < 0.15:
        interp = "Moderate precision"
    elif width < 0.30:
        interp = "Low precision (wide CI)"
    else:
        interp = "Very low precision — more data needed"

    return CIDiagnosticResult(
        estimator="proportion",
        estimate=p,
        ci_lower=lower,
        ci_upper=upper,
        ci_width=width,
        confidence=confidence,
        precision=precision,
        interpretation=interp,
    )


def ci_width_correlation(
    r: float,
    n: int,
    confidence: float = 0.95,
) -> CIDiagnosticResult:
    """Confidence interval width and precision for a correlation.

    Uses Fisher z-transform CI.

    Args:
        r: Observed correlation.
        n: Sample size.
        confidence: Confidence level.

    Returns:
        CIDiagnosticResult with width and precision diagnostics.
    """
    if n < 4:
        return CIDiagnosticResult(
            estimator="correlation",
            estimate=r,
            ci_lower=0.0,
            ci_upper=0.0,
            ci_width=0.0,
            confidence=confidence,
            precision=0.0,
            interpretation="Sample too small for CI (n < 4)",
        )

    r = max(-1.0 + 1e-10, min(1.0 - 1e-10, r))

    z_r = 0.5 * math.log((1 + r) / (1 - r))
    se = 1.0 / math.sqrt(n - 3)
    z_crit = norm.ppf(1 - (1 - confidence) / 2.0)

    z_lower = z_r - z_crit * se
    z_upper = z_r + z_crit * se

    lower = math.tanh(z_lower)
    upper = math.tanh(z_upper)
    width = upper - lower
    precision = 1.0 - width

    if width < 0.2:
        interp = "High precision (narrow CI)"
    elif width < 0.4:
        interp = "Moderate precision"
    elif width < 0.6:
        interp = "Low precision (wide CI)"
    else:
        interp = "Very low precision — more data needed"

    return CIDiagnosticResult(
        estimator="correlation (Fisher z)",
        estimate=r,
        ci_lower=lower,
        ci_upper=upper,
        ci_width=width,
        confidence=confidence,
        precision=precision,
        interpretation=interp,
    )


def ci_width_mean(
    mean: float,
    std: float,
    n: int,
    confidence: float = 0.95,
) -> CIDiagnosticResult:
    """Confidence interval width and precision for a mean.

    Uses t-based CI (normal approximation for large n).

    Args:
        mean: Sample mean.
        std: Sample standard deviation.
        n: Sample size.
        confidence: Confidence level.

    Returns:
        CIDiagnosticResult with width and precision diagnostics.
    """
    if n < 2 or std < 0:
        return CIDiagnosticResult(
            estimator="mean",
            estimate=mean,
            ci_lower=mean,
            ci_upper=mean,
            ci_width=0.0,
            confidence=confidence,
            precision=1.0,
            interpretation="Sample too small for CI",
        )

    z_crit = norm.ppf(1 - (1 - confidence) / 2.0)
    se = std / math.sqrt(n)

    lower = mean - z_crit * se
    upper = mean + z_crit * se
    width = upper - lower

    # Precision relative to estimate magnitude
    if abs(mean) > 0:
        relative_width = width / abs(mean)
    else:
        relative_width = width

    if relative_width < 0.1:
        interp = "High precision (narrow CI)"
    elif relative_width < 0.3:
        interp = "Moderate precision"
    elif relative_width < 0.6:
        interp = "Low precision (wide CI)"
    else:
        interp = "Very low precision — more data needed"

    return CIDiagnosticResult(
        estimator="mean",
        estimate=mean,
        ci_lower=lower,
        ci_upper=upper,
        ci_width=width,
        confidence=confidence,
        precision=1.0 - relative_width,
        interpretation=interp,
    )
