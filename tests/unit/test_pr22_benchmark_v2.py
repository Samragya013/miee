"""
PR-22 Phase 9: Benchmark V2 Validation Tests

Unit tests, integration tests, and regression tests for the
benchmark V2 framework.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from miie.experimental.benchmark.generator import BenchmarkV2Generator
from miie.experimental.benchmark.scenarios import (
    CorrelationScenario,
    DifficultyLevel,
    DriftPattern,
    DriftScenario,
    MultivariateScenario,
    ScenarioType,
    StressScenario,
    ThresholdScenario,
)


class TestScenarioBase(unittest.TestCase):
    """Tests for scenario base classes."""

    def test_difficulty_levels(self):
        """All 5 difficulty levels are defined."""
        levels = list(DifficultyLevel)
        self.assertEqual(len(levels), 5)
        self.assertEqual(levels[0].value, 1)
        self.assertEqual(levels[4].value, 5)

    def test_scenario_types(self):
        """All 5 scenario types are defined."""
        types = list(ScenarioType)
        self.assertEqual(len(types), 5)
        expected = {"drift", "correlation", "threshold", "stress", "multivariate"}
        actual = {t.value for t in types}
        self.assertEqual(actual, expected)

    def test_drift_patterns(self):
        """All drift patterns are defined."""
        patterns = list(DriftPattern)
        self.assertGreaterEqual(len(patterns), 5)


class TestDriftScenario(unittest.TestCase):
    """Tests for DriftScenario."""

    def test_abrupt_drift_generation(self):
        """Abrupt drift generates correct data structure."""
        scenario = DriftScenario(
            scenario_id="TEST-DRIFT-ABRUPT",
            name="Test Abrupt Drift",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_1,
            expected_f1_range=(0.85, 1.0),
            drift_pattern=DriftPattern.ABRUPT,
            effect_size=0.5,
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertEqual(len(data["values"]), 200)
        self.assertIn("anomaly_present", data)
        self.assertTrue(data["anomaly_present"])

    def test_gradual_drift_generation(self):
        """Gradual drift generates correct data structure."""
        scenario = DriftScenario(
            scenario_id="TEST-DRIFT-GRADUAL",
            name="Test Gradual Drift",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_2,
            expected_f1_range=(0.60, 0.85),
            drift_pattern=DriftPattern.GRADUAL,
            effect_size=0.5,
            duration_windows=4,
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertEqual(len(data["values"]), 200)

    def test_seasonal_drift_generation(self):
        """Seasonal drift generates correct data structure."""
        scenario = DriftScenario(
            scenario_id="TEST-DRIFT-SEASONAL",
            name="Test Seasonal Drift",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_3,
            expected_f1_range=(0.50, 0.70),
            drift_pattern=DriftPattern.SEASONAL,
            effect_size=0.3,
            parameters={"period": 4},
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertEqual(len(data["values"]), 200)

    def test_drift_metadata(self):
        """Metadata is correctly populated."""
        scenario = DriftScenario(
            scenario_id="TEST-DRIFT",
            name="Test Drift",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_1,
            expected_f1_range=(0.85, 1.0),
            drift_pattern=DriftPattern.ABRUPT,
            effect_size=0.5,
        )
        metadata = scenario.get_metadata()
        self.assertEqual(metadata["scenario_id"], "TEST-DRIFT")
        self.assertEqual(metadata["scenario_type"], "drift")
        self.assertEqual(metadata["difficulty"], 1)


class TestCorrelationScenario(unittest.TestCase):
    """Tests for CorrelationScenario."""

    def test_weakening_generation(self):
        """Weakening correlation generates correct data structure."""
        scenario = CorrelationScenario(
            scenario_id="TEST-CORR-WEAK",
            name="Test Weakening",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_1,
            expected_f1_range=(0.80, 0.95),
            correlation_strength=0.7,
            correlation_change=0.4,
            breakdown_type="weakening",
        )
        data = scenario.generate(seed=42)
        self.assertIn("metric_a", data)
        self.assertIn("metric_b", data)
        self.assertEqual(len(data["metric_a"]), 200)
        self.assertEqual(len(data["metric_b"]), 200)

    def test_reversal_generation(self):
        """Reversal correlation generates correct data structure."""
        scenario = CorrelationScenario(
            scenario_id="TEST-CORR-REV",
            name="Test Reversal",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_2,
            expected_f1_range=(0.75, 0.90),
            correlation_strength=0.7,
            correlation_change=0.5,
            breakdown_type="reversal",
        )
        data = scenario.generate(seed=42)
        self.assertIn("metric_a", data)
        self.assertIn("metric_b", data)


class TestThresholdScenario(unittest.TestCase):
    """Tests for ThresholdScenario."""

    def test_normal_distribution(self):
        """Normal distribution generates correct data."""
        scenario = ThresholdScenario(
            scenario_id="TEST-THRESH-NORM",
            name="Test Normal",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_1,
            expected_f1_range=(0.80, 0.95),
            compression_strength=0.3,
            distribution_type="normal",
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertEqual(len(data["values"]), 200)

    def test_bimodal_distribution(self):
        """Bimodal distribution generates correct data."""
        scenario = ThresholdScenario(
            scenario_id="TEST-THRESH-BIMODAL",
            name="Test Bimodal",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_2,
            expected_f1_range=(0.75, 0.90),
            compression_strength=0.0,
            distribution_type="bimodal",
            bimodal_separation=2.0,
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertEqual(len(data["values"]), 200)

    def test_heavy_tailed_distribution(self):
        """Heavy-tailed distribution generates correct data."""
        scenario = ThresholdScenario(
            scenario_id="TEST-THRESH-HEAVY",
            name="Test Heavy",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_3,
            expected_f1_range=(0.50, 0.70),
            compression_strength=0.0,
            distribution_type="heavy_tailed",
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertEqual(len(data["values"]), 200)


class TestStressScenario(unittest.TestCase):
    """Tests for StressScenario."""

    def test_small_sample(self):
        """Small sample scenario generates reduced dataset."""
        scenario = StressScenario(
            scenario_id="TEST-STRESS-SMALL",
            name="Test Small",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_3,
            expected_f1_range=(0.40, 0.65),
            stress_type="small_sample",
            stress_level=0.5,
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertLess(len(data["values"]), 200)
        self.assertGreater(len(data["values"]), 10)

    def test_noise_scenario(self):
        """Noise scenario generates noisy data."""
        scenario = StressScenario(
            scenario_id="TEST-STRESS-NOISE",
            name="Test Noise",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_3,
            expected_f1_range=(0.30, 0.55),
            stress_type="noise",
            stress_level=1.0,
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertEqual(len(data["values"]), 200)

    def test_missing_scenario(self):
        """Missing data scenario generates data with NaN values."""
        scenario = StressScenario(
            scenario_id="TEST-STRESS-MISSING",
            name="Test Missing",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_3,
            expected_f1_range=(0.35, 0.55),
            stress_type="missing",
            stress_level=0.25,
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertTrue(data["has_missing"])

    def test_outlier_scenario(self):
        """Outlier scenario generates data with outliers."""
        scenario = StressScenario(
            scenario_id="TEST-STRESS-OUTLIERS",
            name="Test Outliers",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_3,
            expected_f1_range=(0.40, 0.60),
            stress_type="outliers",
            stress_level=0.10,
        )
        data = scenario.generate(seed=42)
        self.assertIn("values", data)
        self.assertTrue(data["has_outliers"])


class TestMultivariateScenario(unittest.TestCase):
    """Tests for MultivariateScenario."""

    def test_bivariate_independent(self):
        """Bivariate independent scenario generates correct data."""
        scenario = MultivariateScenario(
            scenario_id="TEST-MULTI-BI-IND",
            name="Test Bivariate",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_3,
            expected_f1_range=(0.55, 0.75),
            n_metrics=2,
            drift_metrics=["M-01", "M-03"],
            drift_pattern="independent",
            effect_sizes={"M-01": 0.5, "M-03": 0.3},
        )
        data = scenario.generate(seed=42)
        self.assertIn("metrics", data)
        self.assertEqual(len(data["metrics"]), 2)

    def test_trivariate(self):
        """Trivariate scenario generates correct data."""
        scenario = MultivariateScenario(
            scenario_id="TEST-MULTI-TRI",
            name="Test Trivariate",
            description="Test",
            difficulty=DifficultyLevel.LEVEL_4,
            expected_f1_range=(0.40, 0.60),
            n_metrics=3,
            drift_metrics=["M-01", "M-02", "M-03"],
            drift_pattern="independent",
            effect_sizes={"M-01": 0.5, "M-02": 0.3, "M-03": 0.4},
        )
        data = scenario.generate(seed=42)
        self.assertIn("metrics", data)
        self.assertEqual(len(data["metrics"]), 3)


class TestBenchmarkV2Generator(unittest.TestCase):
    """Tests for BenchmarkV2Generator."""

    def test_initialization(self):
        """Generator initializes with all scenarios."""
        gen = BenchmarkV2Generator()
        self.assertGreater(len(gen.scenarios), 0)

    def test_scenario_counts(self):
        """Generator has correct scenario counts."""
        gen = BenchmarkV2Generator()
        summary = gen.get_summary()
        self.assertEqual(summary["total_scenarios"], 40)
        self.assertIn("drift", summary["scenario_counts"])
        self.assertIn("correlation", summary["scenario_counts"])
        self.assertIn("threshold", summary["scenario_counts"])
        self.assertIn("stress", summary["scenario_counts"])
        self.assertIn("multivariate", summary["scenario_counts"])

    def test_generation_determinism(self):
        """Same seed produces identical datasets."""
        gen1 = BenchmarkV2Generator()
        gen2 = BenchmarkV2Generator()

        datasets1 = gen1.generate_all(seed=42)
        datasets2 = gen2.generate_all(seed=42)

        self.assertEqual(len(datasets1), len(datasets2))
        for d1, d2 in zip(datasets1, datasets2):
            self.assertEqual(d1["hash"], d2["hash"])
            self.assertEqual(d1["scenario_id"], d2["scenario_id"])

    def test_different_seeds_differ(self):
        """Different seeds produce different datasets."""
        gen1 = BenchmarkV2Generator()
        gen2 = BenchmarkV2Generator()

        datasets1 = gen1.generate_all(seed=42)
        datasets2 = gen2.generate_all(seed=123)

        # At least some datasets should differ
        different = sum(1 for d1, d2 in zip(datasets1, datasets2) if d1["hash"] != d2["hash"])
        self.assertGreater(different, 0)

    def test_save_and_load(self):
        """Datasets can be saved and loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = BenchmarkV2Generator(output_dir=tmpdir)
            datasets = gen.generate_all(seed=42)
            gen.save_datasets(datasets)

            # Verify index exists
            index_path = os.path.join(tmpdir, "index.json")
            self.assertTrue(os.path.exists(index_path))

            with open(index_path) as f:
                index = json.load(f)
            self.assertEqual(index["total_datasets"], len(datasets))

            # Verify individual datasets exist
            for ds in datasets:
                ds_path = os.path.join(tmpdir, ds["scenario_id"], "dataset.json")
                self.assertTrue(os.path.exists(ds_path))

    def test_metadata_completeness(self):
        """All datasets have complete metadata."""
        gen = BenchmarkV2Generator()
        datasets = gen.generate_all(seed=42)

        for dataset in datasets:
            self.assertIn("scenario_id", dataset)
            self.assertIn("metadata", dataset)
            self.assertIn("hash", dataset)
            self.assertIn("seed", dataset)
            self.assertIn("generated_at", dataset)

            metadata = dataset["metadata"]
            self.assertIn("scenario_id", metadata)
            self.assertIn("name", metadata)
            self.assertIn("scenario_type", metadata)
            self.assertIn("difficulty", metadata)
            self.assertIn("expected_f1_range", metadata)


class TestRegression(unittest.TestCase):
    """Regression tests ensuring V2 doesn't regress on key properties."""

    def test_v2_has_more_scenarios_than_v1(self):
        """V2 has more scenarios than V1 (25)."""
        gen = BenchmarkV2Generator()
        self.assertGreater(len(gen.scenarios), 25)

    def test_v2_has_all_scenario_types(self):
        """V2 has all 5 scenario types."""
        gen = BenchmarkV2Generator()
        types = set(s.scenario_type.value for s in gen.scenarios)
        self.assertEqual(types, {"drift", "correlation", "threshold", "stress", "multivariate"})

    def test_v2_has_stress_scenarios(self):
        """V2 has stress scenarios (new in V2)."""
        gen = BenchmarkV2Generator()
        stress = [s for s in gen.scenarios if s.scenario_type == ScenarioType.STRESS]
        self.assertGreater(len(stress), 0)

    def test_v2_has_multivariate_scenarios(self):
        """V2 has multivariate scenarios (new in V2)."""
        gen = BenchmarkV2Generator()
        multi = [s for s in gen.scenarios if s.scenario_type == ScenarioType.MULTIVARIATE]
        self.assertGreater(len(multi), 0)

    def test_v2_effect_size_range(self):
        """V2 has effect sizes up to 1.5 (V1 was 0.8)."""
        gen = BenchmarkV2Generator()
        drift_scenarios = [s for s in gen.scenarios if s.scenario_type == ScenarioType.DRIFT]
        max_effect = max(s.effect_size for s in drift_scenarios)
        self.assertGreater(max_effect, 0.8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
