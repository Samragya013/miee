"""Assumption validation framework.

Checks statistical assumptions for each detector without modifying detector code.
Consumes existing detector outputs and metric data.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from miie.assurance.models import (
    AssumptionCheck,
    AssumptionReport,
    AssumptionStatus,
)


def _hash_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _check_sample_size(n: int, min_required: int) -> AssumptionCheck:
    """Check minimum sample size assumption."""
    if n >= min_required:
        status = AssumptionStatus.SATISFIED
        evidence = f"n={n} >= {min_required}"
    elif n >= min_required * 0.7:
        status = AssumptionStatus.LIKELY_SATISFIED
        evidence = f"n={n} near threshold {min_required}"
    elif n >= 3:
        status = AssumptionStatus.UNCERTAIN
        evidence = f"n={n} below threshold {min_required}"
    else:
        status = AssumptionStatus.VIOLATED
        evidence = f"n={n} critically low"

    return AssumptionCheck(
        assumption_id=_hash_id(f"sample_size_{n}"),
        name="minimum_sample_size",
        statistical_method="sample_size",
        status=status,
        test_statistic=float(n),
        threshold=float(min_required),
        evidence=evidence,
        impact_if_violated="Results may be unreliable due to insufficient data",
        recommendation="Increase observation count or reduce window granularity",
    )


def _check_ks_assumptions(data_w1: List[float], data_w2: List[float]) -> List[AssumptionCheck]:
    """Check KS test assumptions."""
    checks: List[AssumptionCheck] = []

    # Sample size
    n1, n2 = len(data_w1), len(data_w2)
    checks.append(_check_sample_size(min(n1, n2), 20))

    # Independence (runs test approximation)
    combined = data_w1 + data_w2
    if len(combined) >= 10:
        median = sorted(combined)[len(combined) // 2]
        signs = [1 if x >= median else -1 for x in combined]
        runs = 1 + sum(1 for i in range(1, len(signs)) if signs[i] != signs[i - 1])
        expected_runs = 1 + len(combined) / 2
        var_runs = max((len(combined) - 1) / 4, 1)
        z_runs = (runs - expected_runs) / var_runs**0.5
        p_runs = 2 * (1 - _approx_normal_cdf(abs(z_runs)))

        if p_runs > 0.05:
            status = AssumptionStatus.SATISFIED
            evidence = f"Runs test z={z_runs:.3f}, p={p_runs:.3f} -> independent"
        elif p_runs > 0.01:
            status = AssumptionStatus.LIKELY_SATISFIED
            evidence = f"Runs test z={z_runs:.3f}, p={p_runs:.3f} -> likely independent"
        else:
            status = AssumptionStatus.LIKELY_VIOLATED
            evidence = f"Runs test z={z_runs:.3f}, p={p_runs:.3f} -> possible dependence"

        checks.append(
            AssumptionCheck(
                assumption_id=_hash_id("independence_ks"),
                name="independence",
                statistical_method="Kolmogorov-Smirnov two-sample test",
                status=status,
                test_statistic=z_runs,
                p_value=p_runs,
                evidence=evidence,
                impact_if_violated="KS p-values may be anti-conservative",
                recommendation="Consider paired test or block design",
            )
        )
    else:
        checks.append(
            AssumptionCheck(
                assumption_id=_hash_id("independence_ks_na"),
                name="independence",
                statistical_method="Kolmogorov-Smirnov two-sample test",
                status=AssumptionStatus.NOT_CHECKABLE,
                evidence="Too few observations for runs test",
            )
        )

    return checks


def _check_pearson_assumptions(data_x: List[float], data_y: List[float]) -> List[AssumptionCheck]:
    """Check Pearson correlation assumptions."""
    checks: List[AssumptionCheck] = []

    n = min(len(data_x), len(data_y))
    checks.append(_check_sample_size(n, 10))

    # Linearity check (approximate via squared correlation)
    if n >= 5:
        mean_x = sum(data_x) / n
        mean_y = sum(data_y) / n
        var_x = sum((x - mean_x) ** 2 for x in data_x) / max(n - 1, 1)
        var_y = sum((y - mean_y) ** 2 for y in data_y) / max(n - 1, 1)
        if var_x > 0 and var_y > 0:
            cov = sum((data_x[i] - mean_x) * (data_y[i] - mean_y) for i in range(n)) / max(n - 1, 1)
            r = cov / (var_x**0.5 * var_y**0.5)
            r_sq = r**2

            if r_sq > 0.3:
                status = AssumptionStatus.LIKELY_SATISFIED
                evidence = f"R^2={r_sq:.3f} -> linear relationship present"
            elif r_sq > 0.1:
                status = AssumptionStatus.UNCERTAIN
                evidence = f"R^2={r_sq:.3f} -> weak linear relationship"
            else:
                status = AssumptionStatus.LIKELY_VIOLATED
                evidence = f"R^2={r_sq:.3f} -> no linear relationship"

            checks.append(
                AssumptionCheck(
                    assumption_id=_hash_id("linearity_pearson"),
                    name="linearity",
                    statistical_method="Pearson correlation",
                    status=status,
                    test_statistic=r_sq,
                    evidence=evidence,
                    impact_if_violated="Pearson r underestimates true association",
                    recommendation="Consider Spearman correlation for monotonic relationships",
                )
            )

    return checks


def _check_excess_mass_assumptions(data: List[float], threshold: float) -> List[AssumptionCheck]:
    """Check excess mass test assumptions."""
    checks: List[AssumptionCheck] = []

    n = len(data)
    checks.append(_check_sample_size(n, 20))

    # Distribution shape (approximate skewness)
    if n >= 10:
        mean = sum(data) / n
        var = sum((x - mean) ** 2 for x in data) / max(n - 1, 1)
        if var > 0:
            skew = sum((x - mean) ** 3 for x in data) / (n * var**1.5)
            if abs(skew) < 2:
                status = AssumptionStatus.LIKELY_SATISFIED
                evidence = f"Skewness={skew:.3f} -> approximately symmetric"
            else:
                status = AssumptionStatus.UNCERTAIN
                evidence = f"Skewness={skew:.3f} -> skewed distribution"

            checks.append(
                AssumptionCheck(
                    assumption_id=_hash_id("symmetry_excess"),
                    name="distribution_symmetry",
                    statistical_method="Excess mass test",
                    status=status,
                    test_statistic=skew,
                    evidence=evidence,
                    impact_if_violated="Excess mass test may be anti-conservative",
                    recommendation="Consider non-parametric alternatives",
                )
            )

    return checks


def check_detector_assumptions(
    detector_id: str,
    metric: str,
    detector_output: Dict[str, Any],
    metric_data: Dict[str, Any],
) -> AssumptionReport:
    """Check assumptions for a specific detector finding."""
    checks: List[AssumptionCheck] = []

    if detector_id == "D-01":
        w1_data = metric_data.get("w1", [])
        w2_data = metric_data.get("w2", [])
        if w1_data and w2_data:
            checks.extend(_check_ks_assumptions(w1_data, w2_data))

    elif detector_id == "D-02":
        x_data = metric_data.get("x", [])
        y_data = metric_data.get("y", [])
        if x_data and y_data:
            checks.extend(_check_pearson_assumptions(x_data, y_data))

    elif detector_id == "D-03":
        data = metric_data.get("values", [])
        threshold = metric_data.get("threshold", 0.0)
        if data:
            checks.extend(_check_excess_mass_assumptions(data, threshold))

    if not checks:
        checks.append(
            AssumptionCheck(
                assumption_id=_hash_id(f"no_data_{detector_id}_{metric}"),
                name="data_availability",
                statistical_method=detector_id,
                status=AssumptionStatus.NOT_CHECKABLE,
                evidence="No metric data provided for assumption checking",
            )
        )

    satisfied = sum(1 for c in checks if c.status == AssumptionStatus.SATISFIED)
    total = len(checks)

    worst = AssumptionStatus.SATISFIED
    for c in checks:
        order = list(AssumptionStatus)
        if order.index(c.status) > order.index(worst):
            worst = c.status

    impact_map = {
        AssumptionStatus.SATISFIED: 1.0,
        AssumptionStatus.LIKELY_SATISFIED: 0.95,
        AssumptionStatus.UNCERTAIN: 0.8,
        AssumptionStatus.LIKELY_VIOLATED: 0.6,
        AssumptionStatus.VIOLATED: 0.4,
        AssumptionStatus.NOT_CHECKABLE: 0.9,
    }

    return AssumptionReport(
        report_id=_hash_id(f"assumption_{detector_id}_{metric}"),
        detector_id=detector_id,
        metric=metric,
        assumptions=checks,
        overall_status=worst,
        satisfied_count=satisfied,
        total_count=total,
        confidence_impact=impact_map.get(worst, 0.8),
    )


def _approx_normal_cdf(x: float) -> float:
    """Approximate standard normal CDF."""
    return 0.5 * (1 + _erf(x / 2**0.5))


def _erf(x: float) -> float:
    """Approximate error function."""
    t = 1.0 / (1.0 + 0.327_591_1 * abs(x))
    poly = t * (0.254_829_592 + t * (-0.284_496_736 + t * (1.421_413_741 + t * (-1.453_152_027 + t * 1.061_405_429))))
    result = 1.0 - poly * 2.718_281_828 ** (-(x**2))
    return -result if x < 0 else result
