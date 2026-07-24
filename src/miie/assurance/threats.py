"""Threats-to-validity framework.

Identifies and classifies threats across all validity dimensions.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from miie.assurance.models import (
    ThreatAssessment,
    ThreatCategory,
    ThreatSeverity,
    ThreatToValidity,
)


def _hash_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _detect_threats(
    detector_id: str,
    metric: str,
    analysis_data: Dict[str, Any],
) -> List[ThreatToValidity]:
    """Detect threats based on analysis data."""
    threats: List[ThreatToValidity] = []

    # Construct validity: are we measuring what we think?
    threats.append(
        ThreatToValidity(
            threat_id=_hash_id(f"construct_{detector_id}_{metric}"),
            category=ThreatCategory.CONSTRUCT,
            name="construct_validity",
            description=f"Whether {metric} accurately measures the intended construct for {detector_id}",
            impact="Findings may not reflect true measurement integrity",
            severity=ThreatSeverity.MEDIUM,
            evidence="Construct mapping defined in metric specification",
            mitigation="Validate metric against known ground truth",
            residual_risk="Low if metric specification is rigorous",
            detector_ids=[detector_id],
            metric_ids=[metric],
        )
    )

    # Statistical conclusion validity
    n = analysis_data.get("sample_size", 0)
    if n < 30:
        threats.append(
            ThreatToValidity(
                threat_id=_hash_id(f"stat_power_{detector_id}"),
                category=ThreatCategory.STATISTICAL,
                name="low_statistical_power",
                description=f"Sample size n={n} may be insufficient for reliable inference",
                impact="Type II error rate elevated; may miss real effects",
                severity=ThreatSeverity.HIGH if n < 15 else ThreatSeverity.MEDIUM,
                evidence=f"n={n}, recommended minimum 30",
                mitigation="Increase observation window or reduce granularity",
                residual_risk="Depends on effect size and variance",
                detector_ids=[detector_id],
                metric_ids=[metric],
            )
        )

    power = analysis_data.get("power", 0.0)
    if 0 < power < 0.8:
        threats.append(
            ThreatToValidity(
                threat_id=_hash_id(f"low_power_{detector_id}"),
                category=ThreatCategory.STATISTICAL,
                name="inadequate_power",
                description=f"Post-hoc power={power:.3f} below 0.8 threshold",
                impact="Results may be false negatives",
                severity=ThreatSeverity.HIGH if power < 0.5 else ThreatSeverity.MEDIUM,
                evidence=f"Power={power:.3f}",
                mitigation="Collect more data or increase effect size threshold",
                residual_risk="Cannot quantify without prospective power analysis",
                detector_ids=[detector_id],
                metric_ids=[metric],
            )
        )

    # Internal validity: confounds
    threats.append(
        ThreatToValidity(
            threat_id=_hash_id(f"confound_{detector_id}"),
            category=ThreatCategory.INTERNAL,
            name="confounding_variables",
            description="External factors may influence metric values independently of actual drift",
            impact="False positive drift detection",
            severity=ThreatSeverity.MEDIUM,
            evidence="Temporal correlation does not imply causation",
            mitigation="Control for known confounds (repository size, language, team size)",
            residual_risk="Unknown confounds may remain",
            detector_ids=[detector_id],
            metric_ids=[metric],
        )
    )

    # External validity: generalizability
    threats.append(
        ThreatToValidity(
            threat_id=_hash_id(f"external_{detector_id}"),
            category=ThreatCategory.EXTERNAL,
            name="generalizability",
            description="Findings from analyzed repositories may not generalize to other contexts",
            impact="Limited applicability of conclusions",
            severity=ThreatSeverity.LOW,
            evidence="Repository-specific characteristics affect results",
            mitigation="Validate across multiple repositories and contexts",
            residual_risk="Context dependency inherent in VCS analysis",
            detector_ids=[detector_id],
            metric_ids=[metric],
        )
    )

    # Conclusion validity: multiple comparisons
    num_tests = analysis_data.get("num_tests_conducted", 1)
    if num_tests > 1:
        threats.append(
            ThreatToValidity(
                threat_id=_hash_id(f"multcomp_{detector_id}"),
                category=ThreatCategory.CONCLUSION,
                name="multiple_comparisons",
                description=f"{num_tests} statistical tests conducted without correction",
                impact="Inflated false positive rate",
                severity=ThreatSeverity.HIGH if num_tests > 5 else ThreatSeverity.MEDIUM,
                evidence=f"num_tests={num_tests}",
                mitigation="Apply BH or Bonferroni correction",
                residual_risk="Corrected tests have reduced power",
                detector_ids=[detector_id],
                metric_ids=[metric],
            )
        )

    return threats


def assess_threats(
    detector_id: str,
    metric: str,
    analysis_data: Dict[str, Any],
) -> ThreatAssessment:
    """Assess threats to validity for a detector finding."""
    threats = _detect_threats(detector_id, metric, analysis_data)

    active = [t for t in threats if t.severity in (ThreatSeverity.MEDIUM, ThreatSeverity.HIGH, ThreatSeverity.CRITICAL)]
    high_sev = [t for t in threats if t.severity in (ThreatSeverity.HIGH, ThreatSeverity.CRITICAL)]

    if high_sev:
        risk = "high"
    elif active:
        risk = "medium"
    else:
        risk = "low"

    return ThreatAssessment(
        assessment_id=_hash_id(f"threats_{detector_id}_{metric}"),
        threats=threats,
        active_count=len(active),
        total_count=len(threats),
        high_severity_count=len(high_sev),
        overall_risk=risk,
    )
