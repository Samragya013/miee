"""
Experimental Observation Representation Package

Provides enhanced observation representations for improving
downstream detector performance without modifying production detectors.

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

from miie.experimental.representation.base import (
    BaseRepresentation,
    EnhancedObservation,
    EnhancedWindow,
)
from miie.experimental.representation.representations import (
    BaselineRepresentation,
    HistoricalContextRepresentation,
    MultiScaleRepresentation,
    QualityWeightedRepresentation,
    RepositoryStateRepresentation,
    TemporalContextRepresentation,
)

__all__ = [
    "BaseRepresentation",
    "EnhancedObservation",
    "EnhancedWindow",
    "BaselineRepresentation",
    "MultiScaleRepresentation",
    "TemporalContextRepresentation",
    "HistoricalContextRepresentation",
    "RepositoryStateRepresentation",
    "QualityWeightedRepresentation",
]
