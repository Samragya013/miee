"""
Multi-Evidence Fusion Framework for MIIE

Implements evidence fusion strategies for combining multiple statistical
detectors into a single, scientifically superior detector.

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

from miie.experimental.fusion.fusion_detector import MultiEvidenceFusionDetector
from miie.experimental.fusion.strategies import (
    BayesianFusion,
    ConfidenceFusion,
    LikelihoodRatioFusion,
    MajorityVote,
    WeightedVote,
)

__all__ = [
    "MultiEvidenceFusionDetector",
    "MajorityVote",
    "WeightedVote",
    "ConfidenceFusion",
    "BayesianFusion",
    "LikelihoodRatioFusion",
]
