"""
Base Classes for Observation Representations

Defines the abstract interface and data structures for all
observation representations.

Author: MIIE Research Team
Date: 2026-07-07
Status: EXPERIMENTAL - Not production-certified
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from miie.processing.observation.models import Observation, ObservationWindow


@dataclass
class EnhancedObservation:
    """Enhanced observation with additional contextual features.

    Extends the base Observation with additional features computed
    by the representation transformation.
    """

    # Original observation data
    observation_id: str
    source_type: str
    source_id: str
    metric_id: str
    value: float
    unit: str
    timestamp: str
    quality: str

    # Enhanced features
    features: Dict[str, float] = field(default_factory=dict)
    feature_names: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_observation(cls, obs: Observation, features: Optional[Dict[str, float]] = None) -> "EnhancedObservation":
        """Create EnhancedObservation from base Observation.

        Args:
            obs: Base observation
            features: Additional features to include

        Returns:
            EnhancedObservation with original data and features
        """
        return cls(
            observation_id=obs.observation_id,
            source_type=obs.source_type,
            source_id=obs.source_id,
            metric_id=obs.metric_id,
            value=obs.value,
            unit=obs.unit,
            timestamp=obs.timestamp,
            quality=obs.quality,
            features=features or {},
            feature_names=list(features.keys()) if features else [],
            metadata=obs.metadata.copy(),
        )

    def get_value_vector(self) -> List[float]:
        """Get all values as a feature vector.

        Returns:
            List of floats: [original_value, feature_1, feature_2, ...]
        """
        vector = [self.value]
        for feature_name in sorted(self.features.keys()):
            vector.append(self.features[feature_name])
        return vector

    def get_feature_vector(self) -> List[float]:
        """Get only the enhanced features as a vector.

        Returns:
            List of floats: [feature_1, feature_2, ...]
        """
        return [self.features[name] for name in sorted(self.features.keys())]


@dataclass
class EnhancedWindow:
    """Enhanced observation window with additional contextual features.

    Contains the original observations plus enhanced representations
    for all observations in the window.
    """

    # Original window data
    window_id: str
    window_index: int
    strategy: str
    start_boundary: str
    end_boundary: str

    # Enhanced observations
    enhanced_observations: List[EnhancedObservation] = field(default_factory=list)

    # Window-level features
    window_features: Dict[str, float] = field(default_factory=dict)
    feature_names: List[str] = field(default_factory=list)

    # Metadata
    representation_name: str = ""
    transformation_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def observations(self) -> List[EnhancedObservation]:
        """Get enhanced observations."""
        return self.enhanced_observations

    def get_metric_values(self, metric_id: str) -> List[float]:
        """Get all values for a specific metric.

        Args:
            metric_id: Metric identifier (e.g., "M-01")

        Returns:
            List of float values for the metric
        """
        return [obs.value for obs in self.enhanced_observations if obs.metric_id == metric_id]

    def get_metric_features(self, metric_id: str) -> List[Dict[str, float]]:
        """Get all features for observations of a specific metric.

        Args:
            metric_id: Metric identifier (e.g., "M-01")

        Returns:
            List of feature dictionaries
        """
        return [obs.features for obs in self.enhanced_observations if obs.metric_id == metric_id]

    def get_value_matrix(self, metric_id: str) -> List[List[float]]:
        """Get value matrix for a metric (observations x features).

        Args:
            metric_id: Metric identifier (e.g., "M-01")

        Returns:
            2D list where each row is an observation's feature vector
        """
        return [obs.get_value_vector() for obs in self.enhanced_observations if obs.metric_id == metric_id]


class BaseRepresentation(ABC):
    """Abstract base class for observation representations.

    All representations must implement the transform method to
    convert ObservationWindows into EnhancedWindows.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the representation."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable description of the representation."""
        pass

    @property
    @abstractmethod
    def feature_names(self) -> List[str]:
        """Return the names of all features added by this representation."""
        pass

    @abstractmethod
    def transform(self, windows: List[ObservationWindow]) -> List[EnhancedWindow]:
        """Transform observation windows into enhanced representation.

        Args:
            windows: List of observation windows to transform

        Returns:
            List of enhanced windows with additional features
        """
        pass

    def transform_single(self, window: ObservationWindow) -> EnhancedWindow:
        """Transform a single observation window.

        Args:
            window: Observation window to transform

        Returns:
            Enhanced window with additional features
        """
        result = self.transform([window])
        return result[0] if result else None

    def get_description(self) -> str:
        """Return a detailed description of the representation.

        Returns:
            Multi-line description including name, purpose, and features
        """
        return f"""
Representation: {self.name}
Description: {self.description}
Features Added: {len(self.feature_names)}
Feature Names: {', '.join(self.feature_names)}
"""
