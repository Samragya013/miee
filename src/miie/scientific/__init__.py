"""
MIIE v1.5 Scientific Readiness Certification (PR-7C).

Provides a unified engine for evaluating detector readiness across repositories,
producing per-repository execution reports and aggregate certification verdicts.

Reference: PR-7C-3, OEAS SS21, DES v2.0
"""

from miie.scientific.engine import ScientificReadinessEngine
from miie.scientific.interpreter import VerdictInterpreter
from miie.scientific.models import (
    DetectorVerdict,
    RepositoryCertification,
    ScientificExecutionReport,
)

__all__ = [
    "ScientificReadinessEngine",
    "VerdictInterpreter",
    "ScientificExecutionReport",
    "RepositoryCertification",
    "DetectorVerdict",
]
