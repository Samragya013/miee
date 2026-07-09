"""
Benchmark V2 Synthetic Scenario Generator

Generates controlled, deterministic, parameterized
scientifically reproducible repository evolution scenarios.
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from miie.experimental.benchmark.scenarios import (
    CorrelationScenario,
    DifficultyLevel,
    DriftPattern,
    DriftScenario,
    MultivariateScenario,
    StressScenario,
    ThresholdScenario,
)


class BenchmarkV2Generator:
    """Benchmark V2 scenario generator.

    Generates deterministic, reproducible benchmark datasets
    for evaluating detector performance.
    """

    def __init__(self, output_dir: str = "benchmarks/v2/datasets"):
        """Initialize the generator.

        Args:
            output_dir: Output directory for generated datasets
        """
        self.output_dir = output_dir
        self.scenarios = []
        self._initialize_scenarios()

    def _initialize_scenarios(self):
        """Initialize all benchmark scenarios."""
        # Drift scenarios
        self.scenarios.extend(self._create_drift_scenarios())

        # Correlation scenarios
        self.scenarios.extend(self._create_correlation_scenarios())

        # Threshold scenarios
        self.scenarios.extend(self._create_threshold_scenarios())

        # Stress scenarios
        self.scenarios.extend(self._create_stress_scenarios())

        # Multivariate scenarios
        self.scenarios.extend(self._create_multivariate_scenarios())

    def _create_drift_scenarios(self) -> List[DriftScenario]:
        """Create drift scenarios.

        Returns:
            List of drift scenarios
        """
        scenarios = []

        # Abrupt drift scenarios
        for d in [0.2, 0.5, 0.8, 1.0]:
            difficulty = DifficultyLevel.LEVEL_1 if d >= 0.5 else DifficultyLevel.LEVEL_2
            scenarios.append(
                DriftScenario(
                    scenario_id=f"V2-DRIFT-ABRUPT-{d:.1f}",
                    name=f"Abrupt Drift d={d}",
                    description=f"Abrupt drift with effect size d={d}",
                    difficulty=difficulty,
                    expected_f1_range=(0.85, 1.0) if d >= 0.5 else (0.60, 0.85),
                    drift_pattern=DriftPattern.ABRUPT,
                    effect_size=d,
                )
            )

        # Gradual drift scenarios
        for d in [0.2, 0.5, 0.8]:
            scenarios.append(
                DriftScenario(
                    scenario_id=f"V2-DRIFT-GRADUAL-{d:.1f}",
                    name=f"Gradual Drift d={d}",
                    description=f"Gradual drift with effect size d={d}",
                    difficulty=DifficultyLevel.LEVEL_2,
                    expected_f1_range=(0.60, 0.85),
                    drift_pattern=DriftPattern.GRADUAL,
                    effect_size=d,
                    duration_windows=4,
                )
            )

        # Seasonal drift scenarios
        for period in [4, 8, 12]:
            scenarios.append(
                DriftScenario(
                    scenario_id=f"V2-DRIFT-SEASONAL-P{period}",
                    name=f"Seasonal Drift period={period}",
                    description=f"Seasonal drift with period={period} windows",
                    difficulty=DifficultyLevel.LEVEL_3,
                    expected_f1_range=(0.50, 0.70),
                    drift_pattern=DriftPattern.SEASONAL,
                    effect_size=0.3,
                    parameters={"period": period},
                )
            )

        # Intermittent drift
        scenarios.append(
            DriftScenario(
                scenario_id="V2-DRIFT-INTERMITTENT",
                name="Intermittent Drift",
                description="Intermittent drift at windows 3, 6, 9",
                difficulty=DifficultyLevel.LEVEL_2,
                expected_f1_range=(0.65, 0.85),
                drift_pattern=DriftPattern.INTERMITTENT,
                effect_size=0.5,
            )
        )

        # Incremental drift
        scenarios.append(
            DriftScenario(
                scenario_id="V2-DRIFT-INCREMENTAL",
                name="Incremental Drift",
                description="Incremental drift with small step changes",
                difficulty=DifficultyLevel.LEVEL_3,
                expected_f1_range=(0.55, 0.75),
                drift_pattern=DriftPattern.INCREMENTAL,
                effect_size=0.5,
            )
        )

        return scenarios

    def _create_correlation_scenarios(self) -> List[CorrelationScenario]:
        """Create correlation scenarios.

        Returns:
            List of correlation scenarios
        """
        scenarios = []

        # Weakening scenarios
        for delta_r in [0.2, 0.4, 0.6]:
            scenarios.append(
                CorrelationScenario(
                    scenario_id=f"V2-CORR-WEAK-{delta_r:.1f}",
                    name=f"Correlation Weakening Δr={delta_r}",
                    description=f"Correlation weakening with Δr={delta_r}",
                    difficulty=DifficultyLevel.LEVEL_1,
                    expected_f1_range=(0.80, 0.95),
                    correlation_strength=0.7,
                    correlation_change=delta_r,
                    breakdown_type="weakening",
                )
            )

        # Reversal
        scenarios.append(
            CorrelationScenario(
                scenario_id="V2-CORR-REVERSAL",
                name="Correlation Reversal",
                description="Correlation reversal from positive to negative",
                difficulty=DifficultyLevel.LEVEL_2,
                expected_f1_range=(0.75, 0.90),
                correlation_strength=0.7,
                correlation_change=0.5,
                breakdown_type="reversal",
            )
        )

        # Emergence
        scenarios.append(
            CorrelationScenario(
                scenario_id="V2-CORR-EMERGENCE",
                name="Correlation Emergence",
                description="New correlation emerging mid-dataset",
                difficulty=DifficultyLevel.LEVEL_2,
                expected_f1_range=(0.75, 0.90),
                correlation_strength=0.0,
                correlation_change=0.8,
                breakdown_type="emergence",
            )
        )

        # Nonlinear
        scenarios.append(
            CorrelationScenario(
                scenario_id="V2-CORR-NONLINEAR",
                name="Nonlinear Correlation",
                description="Nonlinear relationship between metrics",
                difficulty=DifficultyLevel.LEVEL_3,
                expected_f1_range=(0.50, 0.70),
                correlation_strength=0.7,
                correlation_change=0.0,
                breakdown_type="nonlinear",
            )
        )

        return scenarios

    def _create_threshold_scenarios(self) -> List[ThresholdScenario]:
        """Create threshold scenarios.

        Returns:
            List of threshold scenarios
        """
        scenarios = []

        # Compression scenarios
        for strength in [0.3, 0.5, 0.7]:
            scenarios.append(
                ThresholdScenario(
                    scenario_id=f"V2-THRESH-COMP-{strength:.1f}",
                    name=f"Threshold Compression {strength:.0%}",
                    description=f"Threshold compression with strength={strength}",
                    difficulty=DifficultyLevel.LEVEL_1,
                    expected_f1_range=(0.80, 0.95),
                    compression_strength=strength,
                    distribution_type="normal",
                )
            )

        # Bimodal
        scenarios.append(
            ThresholdScenario(
                scenario_id="V2-THRESH-BIMODAL",
                name="Bimodal Distribution",
                description="Bimodal distribution with two distinct modes",
                difficulty=DifficultyLevel.LEVEL_2,
                expected_f1_range=(0.75, 0.90),
                compression_strength=0.0,
                distribution_type="bimodal",
                bimodal_separation=2.0,
            )
        )

        # Heavy-tailed
        scenarios.append(
            ThresholdScenario(
                scenario_id="V2-THRESH-HEAVY",
                name="Heavy-tailed Distribution",
                description="Heavy-tailed (Student-t) distribution",
                difficulty=DifficultyLevel.LEVEL_3,
                expected_f1_range=(0.50, 0.70),
                compression_strength=0.0,
                distribution_type="heavy_tailed",
            )
        )

        # Skewed
        scenarios.append(
            ThresholdScenario(
                scenario_id="V2-THRESH-SKEWED",
                name="Skewed Distribution",
                description="Asymmetric (exponential) distribution",
                difficulty=DifficultyLevel.LEVEL_3,
                expected_f1_range=(0.55, 0.75),
                compression_strength=0.0,
                distribution_type="skewed",
            )
        )

        return scenarios

    def _create_stress_scenarios(self) -> List[StressScenario]:
        """Create stress scenarios.

        Returns:
            List of stress scenarios
        """
        scenarios = []

        # Small sample scenarios
        for level in [0.5, 0.25]:
            sample_size = int(200 * (1 - level))
            scenarios.append(
                StressScenario(
                    scenario_id=f"V2-STRESS-SMALL-{sample_size}",
                    name=f"Small Sample n={sample_size}",
                    description=f"Small sample size with n={sample_size}",
                    difficulty=DifficultyLevel.LEVEL_3,
                    expected_f1_range=(0.40, 0.65),
                    stress_type="small_sample",
                    stress_level=level,
                )
            )

        # Noise scenarios
        for snr in [0.5, 1.0, 2.0]:
            scenarios.append(
                StressScenario(
                    scenario_id=f"V2-STRESS-NOISE-SNR{snr}",
                    name=f"High Noise SNR={snr}",
                    description=f"Noisy observations with SNR={snr}",
                    difficulty=DifficultyLevel.LEVEL_3 if snr < 1.5 else DifficultyLevel.LEVEL_2,
                    expected_f1_range=(0.30, 0.55) if snr < 1.5 else (0.65, 0.85),
                    stress_type="noise",
                    stress_level=1.0 / snr,
                )
            )

        # Missing data scenarios
        for pct in [0.10, 0.25, 0.50]:
            scenarios.append(
                StressScenario(
                    scenario_id=f"V2-STRESS-MISSING-{int(pct*100)}",
                    name=f"Missing Data {pct:.0%}",
                    description=f"Missing observations at rate {pct:.0%}",
                    difficulty=DifficultyLevel.LEVEL_2 if pct < 0.3 else DifficultyLevel.LEVEL_4,
                    expected_f1_range=(0.70, 0.85) if pct < 0.3 else (0.35, 0.55),
                    stress_type="missing",
                    stress_level=pct,
                )
            )

        # Outlier scenarios
        for pct in [0.05, 0.10, 0.20]:
            scenarios.append(
                StressScenario(
                    scenario_id=f"V2-STRESS-OUTLIERS-{int(pct*100)}",
                    name=f"Outliers {pct:.0%}",
                    description=f"Outlier contamination at rate {pct:.0%}",
                    difficulty=DifficultyLevel.LEVEL_2 if pct < 0.15 else DifficultyLevel.LEVEL_3,
                    expected_f1_range=(0.70, 0.85) if pct < 0.15 else (0.40, 0.60),
                    stress_type="outliers",
                    stress_level=pct,
                )
            )

        return scenarios

    def _create_multivariate_scenarios(self) -> List[MultivariateScenario]:
        """Create multivariate scenarios.

        Returns:
            List of multivariate scenarios
        """
        scenarios = []

        # Bivariate independent
        scenarios.append(
            MultivariateScenario(
                scenario_id="V2-MULTI-BIVAR-INDEP",
                name="Bivariate Independent Drift",
                description="Two metrics drift independently",
                difficulty=DifficultyLevel.LEVEL_3,
                expected_f1_range=(0.55, 0.75),
                n_metrics=2,
                drift_metrics=["M-01", "M-03"],
                drift_pattern="independent",
                effect_sizes={"M-01": 0.5, "M-03": 0.3},
            )
        )

        # Bivariate correlated
        scenarios.append(
            MultivariateScenario(
                scenario_id="V2-MULTI-BIVAR-CORR",
                name="Bivariate Correlated Drift",
                description="Two metrics drift together",
                difficulty=DifficultyLevel.LEVEL_3,
                expected_f1_range=(0.50, 0.70),
                n_metrics=2,
                drift_metrics=["M-01", "M-03"],
                drift_pattern="correlated",
                effect_sizes={"M-01": 0.5, "M-03": 0.5},
            )
        )

        # Trivariate
        scenarios.append(
            MultivariateScenario(
                scenario_id="V2-MULTI-TRIVAR",
                name="Trivariate Drift",
                description="Three metrics drift simultaneously",
                difficulty=DifficultyLevel.LEVEL_4,
                expected_f1_range=(0.40, 0.60),
                n_metrics=3,
                drift_metrics=["M-01", "M-02", "M-03"],
                drift_pattern="independent",
                effect_sizes={"M-01": 0.5, "M-02": 0.3, "M-03": 0.4},
            )
        )

        # Mixed drift
        scenarios.append(
            MultivariateScenario(
                scenario_id="V2-MULTI-MIXED",
                name="Mixed Drift Types",
                description="Different drift types per metric",
                difficulty=DifficultyLevel.LEVEL_4,
                expected_f1_range=(0.35, 0.55),
                n_metrics=3,
                drift_metrics=["M-01", "M-02", "M-03"],
                drift_pattern="mixed",
                effect_sizes={"M-01": 0.8, "M-02": 0.3, "M-03": 0.5},
            )
        )

        # Cascade
        scenarios.append(
            MultivariateScenario(
                scenario_id="V2-MULTI-CASCADE",
                name="Cascade Drift",
                description="Drift propagates across metrics",
                difficulty=DifficultyLevel.LEVEL_4,
                expected_f1_range=(0.30, 0.50),
                n_metrics=3,
                drift_metrics=["M-01", "M-02", "M-03"],
                drift_pattern="cascade",
                effect_sizes={"M-01": 0.8, "M-02": 0.6, "M-03": 0.4},
            )
        )

        return scenarios

    def generate_all(self, seed: int = 42) -> List[Dict[str, Any]]:
        """Generate all benchmark datasets.

        Args:
            seed: Random seed for reproducibility

        Returns:
            List of generated datasets
        """
        datasets = []

        for scenario in self.scenarios:
            data = scenario.generate(seed)
            data["metadata"] = scenario.get_metadata()
            data["seed"] = seed

            # Compute hash on deterministic content (before timestamp)
            data_hash = hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()
            data["hash"] = data_hash
            data["generated_at"] = datetime.now().isoformat()

            datasets.append(data)

        return datasets

    def save_datasets(self, datasets: List[Dict[str, Any]], output_dir: Optional[str] = None):
        """Save generated datasets to files.

        Args:
            datasets: List of generated datasets
            output_dir: Output directory (uses default if None)
        """
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)

        for data in datasets:
            scenario_id = data["scenario_id"]
            scenario_dir = os.path.join(output_dir, scenario_id)
            os.makedirs(scenario_dir, exist_ok=True)

            # Save dataset
            dataset_path = os.path.join(scenario_dir, "dataset.json")
            with open(dataset_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

        # Save index
        index = {
            "version": "2.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_datasets": len(datasets),
            "seed": datasets[0]["seed"] if datasets else 42,
            "datasets": [
                {
                    "id": d["scenario_id"],
                    "name": d["metadata"]["name"],
                    "type": d["metadata"]["scenario_type"],
                    "difficulty": d["metadata"]["difficulty"],
                    "hash": d["hash"],
                }
                for d in datasets
            ],
        }

        index_path = os.path.join(output_dir, "index.json")
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """Get generator summary.

        Returns:
            Dictionary containing summary statistics
        """
        scenario_counts = {}
        difficulty_counts = {}

        for scenario in self.scenarios:
            stype = scenario.scenario_type.value
            scenario_counts[stype] = scenario_counts.get(stype, 0) + 1

            diff = scenario.difficulty.value
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

        return {
            "total_scenarios": len(self.scenarios),
            "scenario_counts": scenario_counts,
            "difficulty_counts": difficulty_counts,
            "scenario_types": list(scenario_counts.keys()),
        }
