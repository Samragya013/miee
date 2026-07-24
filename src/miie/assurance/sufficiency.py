"""Evidence sufficiency framework.

Evaluates whether evidence meets minimum requirements for valid inference.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from miie.assurance.models import (
    EvidenceSufficiencyReport,
    SufficiencyCriterion,
    SufficiencyStatus,
)


def _hash_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _check_observation_coverage(
    observations_total: int,
    observations_valid: int,
    min_coverage: float = 0.8,
) -> SufficiencyCriterion:
    """Check observation coverage ratio."""
    if observations_total == 0:
        return SufficiencyCriterion(
            criterion_id=_hash_id("obs_cov_zero"),
            name="observation_coverage",
            description="Ratio of valid to total observations",
            threshold=min_coverage,
            actual=0.0,
            met=False,
            evidence="No observations available",
        )

    coverage = observations_valid / observations_total
    return SufficiencyCriterion(
        criterion_id=_hash_id(f"obs_cov_{observations_valid}_{observations_total}"),
        name="observation_coverage",
        description="Ratio of valid to total observations",
        threshold=min_coverage,
        actual=coverage,
        met=coverage >= min_coverage,
        evidence=f"{observations_valid}/{observations_total} valid = {coverage:.3f}",
    )


def _check_detector_agreement(
    detector_results: Dict[str, bool],
    min_agreement: float = 0.5,
) -> SufficiencyCriterion:
    """Check agreement across detectors."""
    if not detector_results:
        return SufficiencyCriterion(
            criterion_id=_hash_id("det_agree_none"),
            name="detector_agreement",
            description="Fraction of detectors agreeing on finding",
            threshold=min_agreement,
            actual=0.0,
            met=False,
            evidence="No detector results available",
        )

    agreeing = sum(1 for v in detector_results.values() if v)
    total = len(detector_results)
    agreement = agreeing / total

    return SufficiencyCriterion(
        criterion_id=_hash_id(f"det_agree_{agreeing}_{total}"),
        name="detector_agreement",
        description="Fraction of detectors agreeing on finding",
        threshold=min_agreement,
        actual=agreement,
        met=agreement >= min_agreement,
        evidence=f"{agreeing}/{total} detectors agree = {agreement:.3f}",
    )


def _check_statistical_power(
    power: float,
    min_power: float = 0.8,
) -> SufficiencyCriterion:
    """Check statistical power adequacy."""
    return SufficiencyCriterion(
        criterion_id=_hash_id(f"power_{power:.3f}"),
        name="statistical_power",
        description="Post-hoc statistical power",
        threshold=min_power,
        actual=power,
        met=power >= min_power,
        evidence=f"Power = {power:.3f} (threshold = {min_power})",
    )


def _check_effect_size(
    effect_size: float,
    min_effect: float = 0.2,
) -> SufficiencyCriterion:
    """Check minimum effect size."""
    abs_es = abs(effect_size)
    return SufficiencyCriterion(
        criterion_id=_hash_id(f"es_{effect_size:.3f}"),
        name="effect_size",
        description="Absolute effect size magnitude",
        threshold=min_effect,
        actual=abs_es,
        met=abs_es >= min_effect,
        evidence=f"|d| = {abs_es:.3f} (threshold = {min_effect})",
    )


def _check_confidence_interval(
    ci_lower: float,
    ci_upper: float,
    max_width: float = 1.0,
) -> SufficiencyCriterion:
    """Check confidence interval width."""
    width = abs(ci_upper - ci_lower)
    return SufficiencyCriterion(
        criterion_id=_hash_id(f"ci_{ci_lower:.3f}_{ci_upper:.3f}"),
        name="confidence_interval_width",
        description="Width of confidence interval",
        threshold=max_width,
        actual=width,
        met=width <= max_width,
        evidence=f"CI width = {width:.3f} (max = {max_width})",
    )


def _check_sample_size_adequacy(
    n: int,
    min_n: int = 30,
) -> SufficiencyCriterion:
    """Check sample size adequacy."""
    return SufficiencyCriterion(
        criterion_id=_hash_id(f"n_adeq_{n}"),
        name="sample_size_adequacy",
        description="Minimum sample size for reliable inference",
        threshold=float(min_n),
        actual=float(n),
        met=n >= min_n,
        evidence=f"n = {n} (min = {min_n})",
    )


def assess_evidence_sufficiency(
    detector_id: str,
    metric: str,
    analysis_data: Dict[str, Any],
) -> EvidenceSufficiencyReport:
    """Assess whether evidence is sufficient for a detector finding."""
    criteria: List[SufficiencyCriterion] = []

    # Observation coverage
    obs_total = analysis_data.get("observations_total", 0)
    obs_valid = analysis_data.get("observations_valid", 0)
    criteria.append(_check_observation_coverage(obs_total, obs_valid))

    # Detector agreement
    det_results = analysis_data.get("detector_results", {})
    if det_results:
        criteria.append(_check_detector_agreement(det_results))

    # Statistical power
    power = analysis_data.get("power", 0.0)
    if power > 0:
        criteria.append(_check_statistical_power(power))

    # Effect size
    effect_size = analysis_data.get("effect_size", 0.0)
    if effect_size != 0.0:
        criteria.append(_check_effect_size(effect_size))

    # Confidence interval
    ci_lower = analysis_data.get("ci_lower")
    ci_upper = analysis_data.get("ci_upper")
    if ci_lower is not None and ci_upper is not None:
        criteria.append(_check_confidence_interval(ci_lower, ci_upper))

    # Sample size
    n = analysis_data.get("sample_size", 0)
    if n > 0:
        criteria.append(_check_sample_size_adequacy(n))

    if not criteria:
        criteria.append(
            SufficiencyCriterion(
                criterion_id=_hash_id(f"no_data_{detector_id}_{metric}"),
                name="data_availability",
                description="Basic data availability check",
                threshold=1.0,
                actual=0.0,
                met=False,
                evidence="No analysis data provided",
            )
        )

    met = sum(1 for c in criteria if c.met)
    total = len(criteria)

    has_real_data = any(c.name != "data_availability" for c in criteria)

    if met == total:
        status = SufficiencyStatus.SUFFICIENT
    elif met >= total * 0.7:
        status = SufficiencyStatus.CONDITIONALLY_SUFFICIENT
    elif met > 0:
        status = SufficiencyStatus.INSUFFICIENT
    elif has_real_data:
        status = SufficiencyStatus.INSUFFICIENT
    else:
        status = SufficiencyStatus.NOT_ASSESSABLE

    gaps = [c.name for c in criteria if not c.met]

    impact_map = {
        SufficiencyStatus.SUFFICIENT: 1.0,
        SufficiencyStatus.CONDITIONALLY_SUFFICIENT: 0.85,
        SufficiencyStatus.INSUFFICIENT: 0.6,
        SufficiencyStatus.NOT_ASSESSABLE: 0.3,
    }

    return EvidenceSufficiencyReport(
        report_id=_hash_id(f"suff_{detector_id}_{metric}"),
        detector_id=detector_id,
        metric=metric,
        criteria=criteria,
        status=status,
        met_count=met,
        total_count=total,
        gaps=gaps,
        confidence_impact=impact_map.get(status, 0.5),
    )
