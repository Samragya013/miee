"""
Benchmark V2 Scenario Definitions

Defines all scenario types for the next-generation benchmark.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ScenarioType(Enum):
    """Scenario type enumeration."""

    DRIFT = "drift"
    CORRELATION = "correlation"
    THRESHOLD = "threshold"
    STRESS = "stress"
    MULTIVARIATE = "multivariate"


class DriftPattern(Enum):
    """Drift pattern enumeration."""

    ABRUPT = "abrupt"
    GRADUAL = "gradual"
    SUDDEN = "sudden"
    INTERMITTENT = "intermittent"
    SEASONAL = "seasonal"
    INCREMENTAL = "incremental"
    CUMULATIVE = "cumulative"


class DifficultyLevel(Enum):
    """Difficulty level enumeration."""

    LEVEL_1 = 1  # Simple
    LEVEL_2 = 2  # Medium
    LEVEL_3 = 3  # Complex
    LEVEL_4 = 4  # Adversarial
    LEVEL_5 = 5  # Extreme


@dataclass
class BaseScenario(ABC):
    """Abstract base class for all scenarios."""

    scenario_id: str
    name: str
    description: str
    difficulty: DifficultyLevel
    expected_f1_range: tuple  # (min, max)
    scenario_type: ScenarioType = ScenarioType.DRIFT
    parameters: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def generate(self, seed: int) -> Dict[str, Any]:
        """Generate scenario data.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Dictionary containing scenario data
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get scenario metadata.

        Returns:
            Dictionary containing metadata
        """
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "scenario_type": self.scenario_type.value,
            "difficulty": self.difficulty.value,
            "expected_f1_range": self.expected_f1_range,
            "parameters": self.parameters,
        }


@dataclass
class DriftScenario(BaseScenario):
    """Drift scenario definition."""

    drift_pattern: DriftPattern = DriftPattern.ABRUPT
    effect_size: float = 0.5
    onset_window: int = 5
    duration_windows: int = 1
    metric_id: str = "M-03"

    def __post_init__(self):
        self.scenario_type = ScenarioType.DRIFT
        self.parameters = {
            "drift_pattern": self.drift_pattern.value,
            "effect_size": self.effect_size,
            "onset_window": self.onset_window,
            "duration_windows": self.duration_windows,
            "metric_id": self.metric_id,
        }

    def generate(self, seed: int) -> Dict[str, Any]:
        """Generate drift scenario data.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Dictionary containing drift scenario data
        """
        import numpy as np

        rng = np.random.RandomState(seed)

        n_observations = 200
        values = rng.normal(0, 1, n_observations)

        if self.drift_pattern == DriftPattern.ABRUPT:
            onset_idx = self.onset_window * (n_observations // 10)
            values[onset_idx:] += self.effect_size

        elif self.drift_pattern == DriftPattern.GRADUAL:
            onset_idx = self.onset_window * (n_observations // 10)
            end_idx = onset_idx + self.duration_windows * (n_observations // 10)
            gradual_effect = np.linspace(0, self.effect_size, end_idx - onset_idx)
            values[onset_idx:end_idx] += gradual_effect
            values[end_idx:] += self.effect_size

        elif self.drift_pattern == DriftPattern.SUDDEN:
            onset_idx = self.onset_window * (n_observations // 10)
            values[onset_idx:] += self.effect_size * 1.5

        elif self.drift_pattern == DriftPattern.INTERMITTENT:
            for w in range(self.onset_window, 10, 3):
                start = w * (n_observations // 10)
                end = min(start + n_observations // 10, n_observations)
                values[start:end] += self.effect_size

        elif self.drift_pattern == DriftPattern.SEASONAL:
            period = self.parameters.get("period", 4)
            for i in range(n_observations):
                values[i] += self.effect_size * np.sin(2 * np.pi * i / (period * 20))

        elif self.drift_pattern == DriftPattern.INCREMENTAL:
            for w in range(self.onset_window, 10):
                start = w * (n_observations // 10)
                end = min(start + n_observations // 10, n_observations)
                values[start:end] += self.effect_size * 0.1 * (w - self.onset_window + 1)

        elif self.drift_pattern == DriftPattern.CUMULATIVE:
            for i in range(self.onset_window * 20, n_observations):
                values[i:] += self.effect_size * 0.01

        return {
            "scenario_id": self.scenario_id,
            "values": values.tolist(),
            "metric_id": self.metric_id,
            "drift_pattern": self.drift_pattern.value,
            "effect_size": self.effect_size,
            "onset_window": self.onset_window,
            "anomaly_present": self.effect_size > 0.2,
            "anomaly_windows": list(range(self.onset_window, 10)) if self.effect_size > 0.2 else [],
        }


@dataclass
class CorrelationScenario(BaseScenario):
    """Correlation scenario definition."""

    correlation_strength: float = 0.7
    correlation_change: float = 0.0
    breakdown_type: str = "weakening"
    metric_a: str = "M-01"
    metric_b: str = "M-03"

    def __post_init__(self):
        self.scenario_type = ScenarioType.CORRELATION
        self.parameters = {
            "correlation_strength": self.correlation_strength,
            "correlation_change": self.correlation_change,
            "breakdown_type": self.breakdown_type,
            "metric_a": self.metric_a,
            "metric_b": self.metric_b,
        }

    def generate(self, seed: int) -> Dict[str, Any]:
        """Generate correlation scenario data.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Dictionary containing correlation scenario data
        """
        import numpy as np

        rng = np.random.RandomState(seed)

        n_observations = 200

        # Generate correlated metrics
        mean = [0, 0]
        cov = [[1, self.correlation_strength], [self.correlation_strength, 1]]
        data = rng.multivariate_normal(mean, cov, n_observations)

        # Apply correlation breakdown
        if self.correlation_change > 0:
            breakdown_start = 100  # Middle of dataset
            if self.breakdown_type == "weakening":
                data[breakdown_start:, 1] = data[breakdown_start:, 0] * (
                    self.correlation_strength - self.correlation_change
                ) + rng.normal(0, 0.5, n_observations - breakdown_start)
            elif self.breakdown_type == "reversal":
                data[breakdown_start:, 1] = -data[breakdown_start:, 0] * self.correlation_change + rng.normal(
                    0, 0.3, n_observations - breakdown_start
                )
            elif self.breakdown_type == "emergence":
                data[breakdown_start:, 1] = data[breakdown_start:, 0] * self.correlation_change + rng.normal(
                    0, 0.5, n_observations - breakdown_start
                )

        return {
            "scenario_id": self.scenario_id,
            "metric_a": data[:, 0].tolist(),
            "metric_b": data[:, 1].tolist(),
            "correlation_strength": self.correlation_strength,
            "correlation_change": self.correlation_change,
            "breakdown_type": self.breakdown_type,
            "anomaly_present": self.correlation_change > 0.3,
        }


@dataclass
class ThresholdScenario(BaseScenario):
    """Threshold scenario definition."""

    compression_strength: float = 0.0
    distribution_type: str = "normal"
    bimodal_separation: float = 2.0
    metric_id: str = "M-03"

    def __post_init__(self):
        self.scenario_type = ScenarioType.THRESHOLD
        self.parameters = {
            "compression_strength": self.compression_strength,
            "distribution_type": self.distribution_type,
            "bimodal_separation": self.bimodal_separation,
            "metric_id": self.metric_id,
        }

    def generate(self, seed: int) -> Dict[str, Any]:
        """Generate threshold scenario data.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Dictionary containing threshold scenario data
        """
        import numpy as np

        rng = np.random.RandomState(seed)

        n_observations = 200

        if self.distribution_type == "normal":
            values = rng.normal(0, 1, n_observations)
            if self.compression_strength > 0:
                values = values * (1 - self.compression_strength * 0.5)

        elif self.distribution_type == "bimodal":
            values1 = rng.normal(-self.bimodal_separation / 2, 0.5, n_observations // 2)
            values2 = rng.normal(self.bimodal_separation / 2, 0.5, n_observations // 2)
            values = np.concatenate([values1, values2])

        elif self.distribution_type == "heavy_tailed":
            values = rng.standard_t(3, n_observations)

        elif self.distribution_type == "skewed":
            values = rng.exponential(1, n_observations) - 1

        else:
            values = rng.normal(0, 1, n_observations)

        return {
            "scenario_id": self.scenario_id,
            "values": values.tolist(),
            "metric_id": self.metric_id,
            "compression_strength": self.compression_strength,
            "distribution_type": self.distribution_type,
            "anomaly_present": self.compression_strength > 0.3 or self.distribution_type in ["bimodal", "heavy_tailed"],
        }


@dataclass
class StressScenario(BaseScenario):
    """Stress scenario definition."""

    stress_type: str = "small_sample"
    stress_level: float = 0.5
    base_scenario: Optional[BaseScenario] = None

    def __post_init__(self):
        self.scenario_type = ScenarioType.STRESS
        self.parameters = {
            "stress_type": self.stress_type,
            "stress_level": self.stress_level,
        }

    def generate(self, seed: int) -> Dict[str, Any]:
        """Generate stress scenario data.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Dictionary containing stress scenario data
        """
        import numpy as np

        rng = np.random.RandomState(seed)

        if self.base_scenario:
            base_data = self.base_scenario.generate(seed)
            values = np.array(base_data.get("values", base_data.get("metric_a", [0] * 200)))
        else:
            values = rng.normal(0, 1, 200)

        if self.stress_type == "small_sample":
            sample_size = int(200 * (1 - self.stress_level))
            sample_size = max(10, sample_size)
            indices = rng.choice(len(values), sample_size, replace=False)
            values = values[indices]

        elif self.stress_type == "noise":
            noise = rng.normal(0, self.stress_level, len(values))
            values = values + noise

        elif self.stress_type == "missing":
            n_missing = int(len(values) * self.stress_level)
            missing_indices = rng.choice(len(values), n_missing, replace=False)
            values[missing_indices] = np.nan

        elif self.stress_type == "outliers":
            n_outliers = int(len(values) * self.stress_level)
            outlier_indices = rng.choice(len(values), n_outliers, replace=False)
            values[outlier_indices] = values[outlier_indices] * 5

        return {
            "scenario_id": self.scenario_id,
            "values": values.tolist(),
            "stress_type": self.stress_type,
            "stress_level": self.stress_level,
            "original_length": 200,
            "actual_length": len(values),
            "has_missing": self.stress_type == "missing",
            "has_outliers": self.stress_type == "outliers",
        }


@dataclass
class MultivariateScenario(BaseScenario):
    """Multivariate scenario definition."""

    n_metrics: int = 3
    drift_metrics: List[str] = field(default_factory=lambda: ["M-01", "M-02", "M-03"])
    drift_pattern: str = "independent"
    effect_sizes: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        self.scenario_type = ScenarioType.MULTIVARIATE
        self.parameters = {
            "n_metrics": self.n_metrics,
            "drift_metrics": self.drift_metrics,
            "drift_pattern": self.drift_pattern,
            "effect_sizes": self.effect_sizes,
        }

    def generate(self, seed: int) -> Dict[str, Any]:
        """Generate multivariate scenario data.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Dictionary containing multivariate scenario data
        """
        import numpy as np

        rng = np.random.RandomState(seed)

        n_observations = 200
        n_metrics = self.n_metrics

        # Generate base correlated metrics
        mean = np.zeros(n_metrics)
        cov = np.eye(n_metrics)
        for i in range(n_metrics):
            for j in range(i + 1, n_metrics):
                cov[i, j] = 0.3
                cov[j, i] = 0.3

        data = rng.multivariate_normal(mean, cov, n_observations)

        # Apply drift to specific metrics
        for metric_id in self.drift_metrics:
            if metric_id in self.effect_sizes:
                effect = self.effect_sizes[metric_id]
                metric_idx = self.drift_metrics.index(metric_id)
                data[100:, metric_idx] += effect

        return {
            "scenario_id": self.scenario_id,
            "metrics": {f"M-{i+1:02d}": data[:, i].tolist() for i in range(n_metrics)},
            "n_metrics": n_metrics,
            "drift_metrics": self.drift_metrics,
            "drift_pattern": self.drift_pattern,
            "effect_sizes": self.effect_sizes,
            "anomaly_present": any(v > 0.2 for v in self.effect_sizes.values()),
        }
