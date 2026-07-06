"""Deterministic Synthetic Data Generators for PR-16C Calibration.

Generates synthetic datasets with known statistical properties for calibrating
each detector. All generators use fixed seeds for reproducibility.

Reference: Doc 04 §6-8, Ground Truth Dataset Framework, PR-16C
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np


@dataclass(frozen=True)
class SyntheticDataset:
    """A synthetic dataset with known ground truth properties."""

    dataset_id: str
    detector_target: str
    anomaly_present: bool
    anomaly_type: str
    values: List[List[float]]
    window_ids: List[str]
    metric_pairs: List[Tuple[str, str]] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


def _normal(loc: float, scale: float, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.normal(loc, scale, n)


def _uniform(low: float, high: float, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(low, high, n)


# ---------------------------------------------------------------------------
# D-01: Distribution Drift Synthetic Datasets
# ---------------------------------------------------------------------------


def generate_d01_no_drift(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-DRIFT-001: No drift baseline. Identical distributions."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        vals = _normal(50.0, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-DRIFT-001",
        detector_target="D-01",
        anomaly_present=False,
        anomaly_type="none",
        values=values,
        window_ids=window_ids,
        metadata={"description": "No drift baseline"},
    )


def generate_d01_small_drift(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-DRIFT-002: Small drift below detection threshold (d=0.15)."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        shift = 0.15 * 10.0 if i >= 3 else 0.0  # small shift in later windows
        vals = _normal(50.0 + shift, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-DRIFT-002",
        detector_target="D-01",
        anomaly_present=True,
        anomaly_type="metric-drift",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Small drift below threshold", "drift_magnitude": 0.15},
    )


def generate_d01_medium_drift(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-DRIFT-003: Medium drift detected (d=0.5)."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        shift = 0.5 * 10.0 if i >= 3 else 0.0
        vals = _normal(50.0 + shift, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-DRIFT-003",
        detector_target="D-01",
        anomaly_present=True,
        anomaly_type="metric-drift",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Medium drift detected", "drift_magnitude": 0.5},
    )


def generate_d01_large_drift(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-DRIFT-004: Large drift detected (d=0.8)."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        shift = 0.8 * 10.0 if i >= 3 else 0.0
        vals = _normal(50.0 + shift, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-DRIFT-004",
        detector_target="D-01",
        anomaly_present=True,
        anomaly_type="metric-drift",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Large drift detected", "drift_magnitude": 0.8},
    )


def generate_d01_gradual_drift(n_windows: int = 8, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-DRIFT-005: Gradual drift detected."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        shift = 0.05 * i * 10.0  # gradual increase
        vals = _normal(50.0 + shift, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-DRIFT-005",
        detector_target="D-01",
        anomaly_present=True,
        anomaly_type="metric-drift",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Gradual drift detected"},
    )


def generate_d01_sudden_drift(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-DRIFT-006: Sudden drift detected."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        shift = 1.0 * 10.0 if i >= 4 else 0.0
        vals = _normal(50.0 + shift, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-DRIFT-006",
        detector_target="D-01",
        anomaly_present=True,
        anomaly_type="metric-drift",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Sudden drift detected", "drift_magnitude": 1.0},
    )


def generate_d01_intermittent_drift(n_windows: int = 8, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-DRIFT-007: Intermittent drift detected."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        shift = 0.5 * 10.0 if i % 3 == 0 else 0.0
        vals = _normal(50.0 + shift, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-DRIFT-007",
        detector_target="D-01",
        anomaly_present=True,
        anomaly_type="metric-drift",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Intermittent drift detected"},
    )


# ---------------------------------------------------------------------------
# D-02: Correlation Breakdown Synthetic Datasets
# ---------------------------------------------------------------------------


def generate_d02_no_breakdown(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-CORR-001: No correlation breakdown baseline."""
    rng = np.random.default_rng(seed)
    values_x = []
    values_y = []
    window_ids = []
    for i in range(n_windows):
        x = _normal(50.0, 10.0, obs_per_window, rng)
        y = 0.7 * x + _normal(0, 5.0, obs_per_window, rng)
        values_x.append(x.tolist())
        values_y.append(y.tolist())
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-CORR-001",
        detector_target="D-02",
        anomaly_present=False,
        anomaly_type="none",
        values=[values_x, values_y],
        window_ids=window_ids,
        metric_pairs=[("metric_x", "metric_y")],
        metadata={"description": "No correlation breakdown", "base_r": 0.7},
    )


def generate_d02_small_weakening(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-CORR-002: Small correlation weakening below threshold."""
    rng = np.random.default_rng(seed)
    values_x = []
    values_y = []
    window_ids = []
    for i in range(n_windows):
        r = 0.7 if i < 3 else 0.55  # small weakening
        x = _normal(50.0, 10.0, obs_per_window, rng)
        y = r * x + _normal(0, 10.0 * math.sqrt(1 - r**2), obs_per_window, rng)
        values_x.append(x.tolist())
        values_y.append(y.tolist())
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-CORR-002",
        detector_target="D-02",
        anomaly_present=True,
        anomaly_type="correlation-breakdown",
        values=[values_x, values_y],
        window_ids=window_ids,
        metric_pairs=[("metric_x", "metric_y")],
        metadata={"description": "Small weakening below threshold", "delta_r": 0.15},
    )


def generate_d02_medium_weakening(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-CORR-003: Medium correlation weakening detected."""
    rng = np.random.default_rng(seed)
    values_x = []
    values_y = []
    window_ids = []
    for i in range(n_windows):
        r = 0.7 if i < 3 else 0.35
        x = _normal(50.0, 10.0, obs_per_window, rng)
        y = r * x + _normal(0, 10.0 * math.sqrt(1 - r**2), obs_per_window, rng)
        values_x.append(x.tolist())
        values_y.append(y.tolist())
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-CORR-003",
        detector_target="D-02",
        anomaly_present=True,
        anomaly_type="correlation-breakdown",
        values=[values_x, values_y],
        window_ids=window_ids,
        metric_pairs=[("metric_x", "metric_y")],
        metadata={"description": "Medium correlation weakening", "delta_r": 0.35},
    )


def generate_d02_large_weakening(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-CORR-004: Large correlation weakening detected."""
    rng = np.random.default_rng(seed)
    values_x = []
    values_y = []
    window_ids = []
    for i in range(n_windows):
        r = 0.7 if i < 3 else 0.1
        x = _normal(50.0, 10.0, obs_per_window, rng)
        y = r * x + _normal(0, 10.0 * math.sqrt(1 - r**2), obs_per_window, rng)
        values_x.append(x.tolist())
        values_y.append(y.tolist())
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-CORR-004",
        detector_target="D-02",
        anomaly_present=True,
        anomaly_type="correlation-breakdown",
        values=[values_x, values_y],
        window_ids=window_ids,
        metric_pairs=[("metric_x", "metric_y")],
        metadata={"description": "Large correlation weakening", "delta_r": 0.6},
    )


def generate_d02_reversal(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-CORR-005: Correlation reversal detected."""
    rng = np.random.default_rng(seed)
    values_x = []
    values_y = []
    window_ids = []
    for i in range(n_windows):
        r = 0.7 if i < 3 else -0.5
        x = _normal(50.0, 10.0, obs_per_window, rng)
        y = r * x + _normal(0, 10.0 * math.sqrt(1 - r**2), obs_per_window, rng)
        values_x.append(x.tolist())
        values_y.append(y.tolist())
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-CORR-005",
        detector_target="D-02",
        anomaly_present=True,
        anomaly_type="correlation-breakdown",
        values=[values_x, values_y],
        window_ids=window_ids,
        metric_pairs=[("metric_x", "metric_y")],
        metadata={"description": "Correlation reversal", "sign_change": True},
    )


def generate_d02_emergence(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-CORR-006: Correlation emergence detected."""
    rng = np.random.default_rng(seed)
    values_x = []
    values_y = []
    window_ids = []
    for i in range(n_windows):
        r = 0.05 if i < 3 else 0.6
        x = _normal(50.0, 10.0, obs_per_window, rng)
        y = r * x + _normal(0, 10.0 * math.sqrt(1 - r**2), obs_per_window, rng)
        values_x.append(x.tolist())
        values_y.append(y.tolist())
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-CORR-006",
        detector_target="D-02",
        anomaly_present=True,
        anomaly_type="correlation-breakdown",
        values=[values_x, values_y],
        window_ids=window_ids,
        metric_pairs=[("metric_x", "metric_y")],
        metadata={"description": "Correlation emergence"},
    )


# ---------------------------------------------------------------------------
# D-03: Threshold Compression Synthetic Datasets
# ---------------------------------------------------------------------------


def generate_d03_no_compression(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-THRESH-001: No compression baseline."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        vals = _uniform(0.0, 1.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-THRESH-001",
        detector_target="D-03",
        anomaly_present=False,
        anomaly_type="none",
        values=values,
        window_ids=window_ids,
        metadata={"description": "No compression baseline", "threshold": 0.5},
    )


def generate_d03_weak_compression(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-THRESH-002: Weak compression below threshold."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        base = _uniform(0.0, 1.0, obs_per_window, rng)
        n_inject = int(obs_per_window * 0.35)
        injected = rng.normal(0.5, 0.15, n_inject)
        vals = np.concatenate([base, injected]).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-THRESH-002",
        detector_target="D-03",
        anomaly_present=False,
        anomaly_type="none",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Weak compression below threshold", "threshold": 0.5},
    )


def generate_d03_moderate_compression(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-THRESH-003: Moderate compression detected."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        base = _uniform(0.0, 1.0, obs_per_window, rng)
        n_inject = int(obs_per_window * 0.5)
        injected = rng.normal(0.5, 0.05, n_inject)
        vals = np.concatenate([base, injected]).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-THRESH-003",
        detector_target="D-03",
        anomaly_present=True,
        anomaly_type="threshold-compression",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Moderate compression detected", "threshold": 0.5},
    )


def generate_d03_strong_compression(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-THRESH-004: Strong compression detected."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        base = _uniform(0.0, 1.0, obs_per_window, rng)
        n_inject = int(obs_per_window * 0.65)
        injected = rng.normal(0.5, 0.03, n_inject)
        vals = np.concatenate([base, injected]).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-THRESH-004",
        detector_target="D-03",
        anomaly_present=True,
        anomaly_type="threshold-compression",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Strong compression detected", "threshold": 0.5},
    )


def generate_d03_bimodal(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-SYN-THRESH-005: Bimodal distribution detected."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        half = obs_per_window // 2
        v1 = rng.normal(0.3, 0.05, half)
        v2 = rng.normal(0.7, 0.05, obs_per_window - half)
        vals = np.concatenate([v1, v2]).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-SYN-THRESH-005",
        detector_target="D-03",
        anomaly_present=True,
        anomaly_type="threshold-compression",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Bimodal distribution detected", "threshold": 0.5},
    )


# ---------------------------------------------------------------------------
# Adversarial Edge Cases
# ---------------------------------------------------------------------------


def generate_adv_subtle_drift(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-ADV-DRIFT-001: Subtle drift may evade D-01."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        shift = 0.08 * 10.0 if i >= 3 else 0.0  # very small shift
        vals = _normal(50.0 + shift, 12.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-ADV-DRIFT-001",
        detector_target="D-01",
        anomaly_present=True,
        anomaly_type="metric-drift",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Subtle drift may evade D-01", "drift_magnitude": 0.08},
    )


def generate_adv_seasonal(n_windows: int = 12, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-ADV-DRIFT-002: Seasonal pattern should not trigger D-01."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        seasonal = 5.0 * math.sin(2 * math.pi * i / 12)
        vals = _normal(50.0 + seasonal, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-ADV-DRIFT-002",
        detector_target="D-01",
        anomaly_present=False,
        anomaly_type="none",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Seasonal pattern should not trigger D-01"},
    )


def generate_adv_subtle_corr_decoupling(
    n_windows: int = 6, obs_per_window: int = 30, seed: int = 42
) -> SyntheticDataset:
    """GT-ADV-CORR-001: Subtle correlation decoupling may evade D-02."""
    rng = np.random.default_rng(seed)
    values_x = []
    values_y = []
    window_ids = []
    for i in range(n_windows):
        r = 0.7 if i < 3 else 0.5  # small weakening, may not trigger
        x = _normal(50.0, 10.0, obs_per_window, rng)
        y = r * x + _normal(0, 10.0 * math.sqrt(1 - r**2), obs_per_window, rng)
        values_x.append(x.tolist())
        values_y.append(y.tolist())
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-ADV-CORR-001",
        detector_target="D-02",
        anomaly_present=True,
        anomaly_type="correlation-breakdown",
        values=[values_x, values_y],
        window_ids=window_ids,
        metric_pairs=[("metric_x", "metric_y")],
        metadata={"description": "Subtle correlation decoupling may evade D-02"},
    )


def generate_adv_near_threshold_gaming(
    n_windows: int = 6, obs_per_window: int = 30, seed: int = 42
) -> SyntheticDataset:
    """GT-ADV-THRESH-001: Near-threshold gaming may evade D-03."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        base = _uniform(0.0, 1.0, obs_per_window, rng)
        n_inject = int(obs_per_window * 0.25)  # just under threshold
        injected = rng.normal(0.5, 0.08, n_inject)
        vals = np.concatenate([base, injected]).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-ADV-THRESH-001",
        detector_target="D-03",
        anomaly_present=True,
        anomaly_type="threshold-compression",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Near-threshold gaming may evade D-03"},
    )


# ---------------------------------------------------------------------------
# Healthy Real Repository Baselines (simulated)
# ---------------------------------------------------------------------------


def generate_real_healthy_001(n_windows: int = 6, obs_per_window: int = 30, seed: int = 42) -> SyntheticDataset:
    """GT-REAL-HEALTHY-001: Healthy repository baseline."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        vals = _normal(50.0, 10.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-REAL-HEALTHY-001",
        detector_target="all",
        anomaly_present=False,
        anomaly_type="none",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Healthy repository baseline 1"},
    )


def generate_real_healthy_002(n_windows: int = 6, obs_per_window: int = 30, seed: int = 43) -> SyntheticDataset:
    """GT-REAL-HEALTHY-002: Healthy repository baseline."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        vals = _normal(30.0, 8.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-REAL-HEALTHY-002",
        detector_target="all",
        anomaly_present=False,
        anomaly_type="none",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Healthy repository baseline 2"},
    )


def generate_real_healthy_003(n_windows: int = 6, obs_per_window: int = 30, seed: int = 44) -> SyntheticDataset:
    """GT-REAL-HEALTHY-003: Healthy repository baseline."""
    rng = np.random.default_rng(seed)
    values = []
    window_ids = []
    for i in range(n_windows):
        vals = _uniform(20.0, 80.0, obs_per_window, rng).tolist()
        values.append(vals)
        window_ids.append(f"w{i}")
    return SyntheticDataset(
        dataset_id="GT-REAL-HEALTHY-003",
        detector_target="all",
        anomaly_present=False,
        anomaly_type="none",
        values=values,
        window_ids=window_ids,
        metadata={"description": "Healthy repository baseline 3"},
    )


# ---------------------------------------------------------------------------
# Registry: map dataset_id -> generator function
# ---------------------------------------------------------------------------

DATASET_GENERATORS = {
    "GT-SYN-DRIFT-001": generate_d01_no_drift,
    "GT-SYN-DRIFT-002": generate_d01_small_drift,
    "GT-SYN-DRIFT-003": generate_d01_medium_drift,
    "GT-SYN-DRIFT-004": generate_d01_large_drift,
    "GT-SYN-DRIFT-005": generate_d01_gradual_drift,
    "GT-SYN-DRIFT-006": generate_d01_sudden_drift,
    "GT-SYN-DRIFT-007": generate_d01_intermittent_drift,
    "GT-SYN-CORR-001": generate_d02_no_breakdown,
    "GT-SYN-CORR-002": generate_d02_small_weakening,
    "GT-SYN-CORR-003": generate_d02_medium_weakening,
    "GT-SYN-CORR-004": generate_d02_large_weakening,
    "GT-SYN-CORR-005": generate_d02_reversal,
    "GT-SYN-CORR-006": generate_d02_emergence,
    "GT-SYN-THRESH-001": generate_d03_no_compression,
    "GT-SYN-THRESH-002": generate_d03_weak_compression,
    "GT-SYN-THRESH-003": generate_d03_moderate_compression,
    "GT-SYN-THRESH-004": generate_d03_strong_compression,
    "GT-SYN-THRESH-005": generate_d03_bimodal,
    "GT-REAL-HEALTHY-001": generate_real_healthy_001,
    "GT-REAL-HEALTHY-002": generate_real_healthy_002,
    "GT-REAL-HEALTHY-003": generate_real_healthy_003,
    "GT-ADV-DRIFT-001": generate_adv_subtle_drift,
    "GT-ADV-DRIFT-002": generate_adv_seasonal,
    "GT-ADV-CORR-001": generate_adv_subtle_corr_decoupling,
    "GT-ADV-THRESH-001": generate_adv_near_threshold_gaming,
}


def generate_all_datasets(seed: int = 42) -> Dict[str, SyntheticDataset]:
    """Generate all 25 certified ground truth datasets."""
    datasets = {}
    for dataset_id, gen_func in DATASET_GENERATORS.items():
        datasets[dataset_id] = gen_func(seed=seed)
    return datasets


def get_datasets_by_detector(detector: str) -> Dict[str, SyntheticDataset]:
    """Get datasets targeting a specific detector."""
    all_ds = generate_all_datasets()
    return {k: v for k, v in all_ds.items() if v.detector_target == detector or v.detector_target == "all"}
