"""
MIIE v1.5 Statistical Sampling & Detector Readiness Framework.

Provides repository profiling, strategy evaluation, adaptive windowing,
detector readiness analysis, and execution tracing for deterministic
detector dispatch.

Reference: PR-7B, OEAS SS21, DES v2.0
"""

from miie.sampling.adaptive_window import AdaptiveWindowBuilder
from miie.sampling.diagnostics import DiagnosticsEngine
from miie.sampling.models import (
    DetectorReadiness,
    ExecutionTrace,
    ReadinessReport,
    RepositoryProfile,
    SamplingPlan,
    StrategyCandidate,
)
from miie.sampling.planner import SamplingPlanner
from miie.sampling.readiness import DetectorReadinessAnalyzer
from miie.sampling.strategy import StrategyEngine
from miie.sampling.trace import ExecutionTracer

__all__ = [
    "SamplingPlanner",
    "StrategyEngine",
    "AdaptiveWindowBuilder",
    "DetectorReadinessAnalyzer",
    "ExecutionTracer",
    "DiagnosticsEngine",
    "RepositoryProfile",
    "SamplingPlan",
    "StrategyCandidate",
    "ReadinessReport",
    "DetectorReadiness",
    "ExecutionTrace",
]
