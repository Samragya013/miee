"""
Benchmark V2 Experimental Package

Provides synthetic scenario generation and evaluation
for next-generation benchmark framework.
"""

from miie.experimental.benchmark.generator import BenchmarkV2Generator
from miie.experimental.benchmark.scenarios import (
    CorrelationScenario,
    DriftScenario,
    MultivariateScenario,
    StressScenario,
    ThresholdScenario,
)

__all__ = [
    "BenchmarkV2Generator",
    "DriftScenario",
    "CorrelationScenario",
    "ThresholdScenario",
    "StressScenario",
    "MultivariateScenario",
]
