"""Limitation framework.

Deterministic limitation identification and reporting.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from miie.assurance.models import (
    Limitation,
    LimitationCategory,
    LimitationReport,
)


def _hash_id(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _detect_limitations(
    detector_id: str,
    metric: str,
    analysis_data: Dict[str, Any],
) -> List[Limitation]:
    """Detect limitations based on analysis data."""
    limitations: List[Limitation] = []

    # Sample size limitations
    n = analysis_data.get("sample_size", 0)
    if n > 0 and n < 50:
        limitations.append(
            Limitation(
                limitation_id=_hash_id(f"lim_n_{detector_id}_{n}"),
                category=LimitationCategory.SAMPLE_SIZE,
                name="small_sample_size",
                description=f"n={n} limits statistical reliability",
                impact="Wide confidence intervals, reduced power",
                quantification=f"n={n}, recommended >= 50",
                mitigation="Extend observation window",
                detector_ids=[detector_id],
                metric_ids=[metric],
            )
        )

    # Power limitations
    power = analysis_data.get("power", 0.0)
    if 0 < power < 0.8:
        limitations.append(
            Limitation(
                limitation_id=_hash_id(f"lim_power_{detector_id}"),
                category=LimitationCategory.STATISTICAL_POWER,
                name="low_statistical_power",
                description=f"Power={power:.3f} below conventional 0.8",
                impact="Elevated Type II error rate",
                quantification=f"Power={power:.3f}",
                mitigation="Collect additional data",
                detector_ids=[detector_id],
                metric_ids=[metric],
            )
        )

    # Data quality limitations
    missing_pct = analysis_data.get("missing_data_pct", 0.0)
    if missing_pct > 0.1:
        limitations.append(
            Limitation(
                limitation_id=_hash_id(f"lim_missing_{detector_id}"),
                category=LimitationCategory.DATA_QUALITY,
                name="missing_data",
                description=f"{missing_pct:.1%} missing data",
                impact="Results may be biased if data not missing at random",
                quantification=f"Missing: {missing_pct:.1%}",
                mitigation="Investigate missingness mechanism; consider imputation",
                detector_ids=[detector_id],
                metric_ids=[metric],
            )
        )

    # Methodological limitations
    limitations.append(
        Limitation(
            limitation_id=_hash_id(f"lim_method_{detector_id}_{metric}"),
            category=LimitationCategory.METHODOLOGICAL,
            name="temporal_assumption",
            description="Analysis assumes stationarity within observation windows",
            impact="Non-stationary processes may produce misleading results",
            quantification="Assumption-based, not quantifiable",
            mitigation="Validate stationarity assumption per detector",
            detector_ids=[detector_id],
            metric_ids=[metric],
        )
    )

    # External limitations
    limitations.append(
        Limitation(
            limitation_id=_hash_id(f"lim_external_{detector_id}"),
            category=LimitationCategory.EXTERNAL,
            name="repository_specificity",
            description="Results specific to analyzed repositories",
            impact="Generalizability unknown",
            quantification="Depends on repository characteristics",
            mitigation="Cross-validate across repositories",
            detector_ids=[detector_id],
            metric_ids=[metric],
        )
    )

    # Temporal limitations
    limitations.append(
        Limitation(
            limitation_id=_hash_id(f"lim_temporal_{detector_id}"),
            category=LimitationCategory.TEMPORAL,
            name="snapshot_analysis",
            description="Analysis captures point-in-time, not continuous monitoring",
            impact="Inter-window changes may be missed",
            quantification="Single observation window",
            mitigation="Implement continuous monitoring",
            detector_ids=[detector_id],
            metric_ids=[metric],
        )
    )

    return limitations


def build_limitation_report(
    detector_id: str,
    metric: str,
    analysis_data: Dict[str, Any],
) -> LimitationReport:
    """Build complete limitation report."""
    limitations = _detect_limitations(detector_id, metric, analysis_data)

    by_cat: Dict[str, int] = {}
    for lim in limitations:
        cat = lim.category.value
        by_cat[cat] = by_cat.get(cat, 0) + 1

    high_impact = [
        lm
        for lm in limitations
        if "elevated" in lm.impact.lower() or "misleading" in lm.impact.lower() or "biased" in lm.impact.lower()
    ]
    if high_impact:
        overall = "Significant limitations present. Interpret with caution."
    else:
        overall = "Standard limitations for this type of analysis."

    return LimitationReport(
        report_id=_hash_id(f"lim_report_{detector_id}_{metric}"),
        limitations=limitations,
        total_count=len(limitations),
        by_category=by_cat,
        overall_impact=overall,
    )
