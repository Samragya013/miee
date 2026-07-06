"""PR-16D: Detector Threshold Calibration & Decision Boundary Optimization.

Uses actual detector classes with config overrides to sweep threshold ranges
and find optimal values on certified Ground Truth datasets.

Reference: PR-16C calibration results, IMP 1.6 Hard Targets
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

_REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from benchmarks.calibration.synthetic_data import (
    SyntheticDataset,
    generate_all_datasets,
)
from miie.processing.detection.correlation_breakdown_detector import (
    CorrelationBreakdownDetector,
)
from miie.processing.detection.distribution_drift_detector import (
    DistributionDriftDetector,
)
from miie.processing.detection.threshold_compression_detector import (
    ThresholdCompressionDetector,
)
from miie.processing.observation.models import Observation, ObservationProvenance, ObservationWindow

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results" / "pr16d_calibration"


# ---------------------------------------------------------------------------
# Build ObservationWindows from SyntheticDataset
# ---------------------------------------------------------------------------


def _make_observation_window(
    window_id: str,
    window_index: int,
    values: List[float],
    metric_id: str = "M-01",
    source_type: str = "commit",
) -> ObservationWindow:
    """Create an ObservationWindow from raw values."""
    observations = []
    for i, v in enumerate(values):
        source_id = f"{'a' * 40}"  # dummy commit SHA
        obs = Observation(
            observation_id=f"{'b' * 16}",
            source_type=source_type,
            source_id=source_id,
            metric_id=metric_id,
            value=float(v),
            unit="ratio",
            timestamp="2025-01-01T00:00:00+00:00",
            quality="complete",
            provenance=ObservationProvenance(
                extractor_id="synthetic",
                extraction_timestamp="2025-01-01T00:00:00+00:00",
            ),
        )
        observations.append(obs)

    base = datetime(2025, 1, 1, tzinfo=timezone.utc)
    start = base
    end = base

    return ObservationWindow(
        window_id=window_id,
        window_index=window_index,
        strategy="commit_count",
        start_boundary=start.isoformat(),
        end_boundary=end.isoformat(),
        observations=observations,
        metrics_present=[metric_id],
    )


def _build_d01_windows(ds: SyntheticDataset) -> List[ObservationWindow]:
    """Build ObservationWindows for D-01 (single metric per window)."""
    windows = []
    for i, (wid, vals) in enumerate(zip(ds.window_ids, ds.values)):
        windows.append(_make_observation_window(wid, i, vals, metric_id="M-01"))
    return windows


def _build_d02_windows(ds: SyntheticDataset) -> List[ObservationWindow]:
    """Build ObservationWindows for D-02 (two metrics per window for correlation).
    
    D-02 datasets store values as [values_x, values_y] where each is a list
    of per-window lists.
    """
    windows = []
    # D-02 values structure: [list_of_windows_for_metric_x, list_of_windows_for_metric_y]
    values_x = ds.values[0]  # list of per-window lists
    values_y = ds.values[1]  # list of per-window lists

    for i, wid in enumerate(ds.window_ids):
        vals_a = values_x[i]
        vals_b = values_y[i]
        obs_list = []
        for j, v in enumerate(vals_a):
            obs_list.append(
                Observation(
                    observation_id=f"{'b' * 16}",
                    source_type="commit",
                    source_id=f"{j:040d}",
                    metric_id="M-01",
                    value=float(v),
                    unit="ratio",
                    timestamp="2025-01-01T00:00:00+00:00",
                    quality="complete",
                    provenance=ObservationProvenance(
                        extractor_id="synthetic",
                        extraction_timestamp="2025-01-01T00:00:00+00:00",
                    ),
                )
            )
        for j, v in enumerate(vals_b):
            obs_list.append(
                Observation(
                    observation_id=f"{'c' * 16}",
                    source_type="commit",
                    source_id=f"{j:040d}",
                    metric_id="M-02",
                    value=float(v),
                    unit="count",
                    timestamp="2025-01-01T00:00:00+00:00",
                    quality="complete",
                    provenance=ObservationProvenance(
                        extractor_id="synthetic",
                        extraction_timestamp="2025-01-01T00:00:00+00:00",
                    ),
                )
            )

        base = datetime(2025, 1, 1, tzinfo=timezone.utc)
        windows.append(
            ObservationWindow(
                window_id=wid,
                window_index=i,
                strategy="commit_count",
                start_boundary=base.isoformat(),
                end_boundary=base.isoformat(),
                observations=obs_list,
                metrics_present=["M-01", "M-02"],
            )
        )
    return windows


def _build_d03_windows(ds: SyntheticDataset) -> List[ObservationWindow]:
    """Build ObservationWindows for D-03 (single metric per window)."""
    return _build_d01_windows(ds)


# ---------------------------------------------------------------------------
# Confusion matrix evaluation
# ---------------------------------------------------------------------------


def _evaluate_detector(
    ds_list: List[SyntheticDataset],
    detector_class,
    config: Dict[str, Any],
    build_windows_fn,
    expected_type: str,
) -> Dict[str, Any]:
    """Evaluate a detector across datasets with a given config."""
    tp = fp = fn = tn = 0
    per_dataset = []

    for ds in ds_list:
        windows = build_windows_fn(ds)
        detector = detector_class()
        result = detector.detect_observations(windows, config=config)

        detected = False
        # Extract detection flag from output
        output = result.detector_outputs.get(detector.detector_id, {})
        if expected_type == "drift":
            detected = output.get("drift_detected", False)
            expected = ds.anomaly_present and ds.anomaly_type == "metric-drift"
        elif expected_type == "correlation":
            detected = output.get("breakdown_detected", False)
            expected = ds.anomaly_present and ds.anomaly_type == "correlation-breakdown"
        elif expected_type == "compression":
            detected = output.get("compression_detected", False)
            expected = ds.anomaly_present and ds.anomaly_type == "threshold-compression"
        else:
            expected = False

        is_tp = detected and expected
        is_fp = detected and not expected
        is_fn = not detected and expected
        is_tn = not detected and not expected

        tp += int(is_tp)
        fp += int(is_fp)
        fn += int(is_fn)
        tn += int(is_tn)

        per_dataset.append({
            "dataset_id": ds.dataset_id,
            "expected": expected,
            "detected": detected,
            "correct": (is_tp or is_tn),
        })

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    balanced_accuracy = (recall + specificity) / 2.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "specificity": round(specificity, 4),
        "balanced_accuracy": round(balanced_accuracy, 4),
        "per_dataset": per_dataset,
    }


# ---------------------------------------------------------------------------
# D-01: Sweep ks_p_value_threshold
# ---------------------------------------------------------------------------


def sweep_d01(
    datasets: Dict[str, SyntheticDataset],
    alpha_range: List[float],
) -> List[Dict[str, Any]]:
    """Sweep D-01's KS alpha threshold using the actual detector."""
    d01_datasets = [v for v in datasets.values() if v.detector_target in ("D-01", "all")]
    results = []

    for alpha in alpha_range:
        config = {"ks_p_value_threshold": alpha}
        r = _evaluate_detector(
            d01_datasets,
            DistributionDriftDetector,
            config,
            _build_d01_windows,
            "drift",
        )
        r["threshold"] = alpha
        results.append(r)

    return results


def sweep_d01_psi(
    datasets: Dict[str, SyntheticDataset],
    psi_range: List[float],
    ks_alpha: float = 0.05,
) -> List[Dict[str, Any]]:
    """Sweep D-01's PSI threshold (with fixed KS alpha)."""
    d01_datasets = [v for v in datasets.values() if v.detector_target in ("D-01", "all")]
    results = []

    for psi_thresh in psi_range:
        config = {"ks_p_value_threshold": ks_alpha, "psi_threshold": psi_thresh}
        r = _evaluate_detector(
            d01_datasets,
            DistributionDriftDetector,
            config,
            _build_d01_windows,
            "drift",
        )
        r["threshold"] = psi_thresh
        results.append(r)

    return results


# ---------------------------------------------------------------------------
# D-02: Sweep sudden_drop_threshold
# ---------------------------------------------------------------------------


def sweep_d02(
    datasets: Dict[str, SyntheticDataset],
    threshold_range: List[float],
) -> List[Dict[str, Any]]:
    """Sweep D-02's sudden drop threshold using the actual detector."""
    d02_datasets = [v for v in datasets.values() if v.detector_target == "D-02"]
    results = []

    for thresh in threshold_range:
        config = {"sudden_drop_threshold": thresh}
        r = _evaluate_detector(
            d02_datasets,
            CorrelationBreakdownDetector,
            config,
            _build_d02_windows,
            "correlation",
        )
        r["threshold"] = thresh
        results.append(r)

    return results


# ---------------------------------------------------------------------------
# D-03: Sweep excess_mass_z_threshold
# ---------------------------------------------------------------------------


def sweep_d03(
    datasets: Dict[str, SyntheticDataset],
    z_range: List[float],
) -> List[Dict[str, Any]]:
    """Sweep D-03's excess mass z threshold using the actual detector."""
    d03_datasets = [v for v in datasets.values() if v.detector_target in ("D-03", "all")]
    results = []

    for z_thresh in z_range:
        config = {"excess_mass_z_threshold": z_thresh}
        r = _evaluate_detector(
            d03_datasets,
            ThresholdCompressionDetector,
            config,
            _build_d03_windows,
            "compression",
        )
        r["threshold"] = z_thresh
        results.append(r)

    return results


def sweep_d03_dip(
    datasets: Dict[str, SyntheticDataset],
    dip_range: List[float],
    z_thresh: float = 1.645,
) -> List[Dict[str, Any]]:
    """Sweep D-03's dip_test_p_threshold (with fixed z threshold)."""
    d03_datasets = [v for v in datasets.values() if v.detector_target in ("D-03", "all")]
    results = []

    for dip_thresh in dip_range:
        config = {"excess_mass_z_threshold": z_thresh, "dip_test_p_threshold": dip_thresh}
        r = _evaluate_detector(
            d03_datasets,
            ThresholdCompressionDetector,
            config,
            _build_d03_windows,
            "compression",
        )
        r["threshold"] = dip_thresh
        results.append(r)

    return results


def sweep_d03_joint(
    datasets: Dict[str, SyntheticDataset],
    z_range: List[float],
    dip_range: List[float],
) -> List[Dict[str, Any]]:
    """Joint sweep of D-03's z and dip thresholds."""
    d03_datasets = [v for v in datasets.values() if v.detector_target in ("D-03", "all")]
    results = []

    for z_thresh in z_range:
        for dip_thresh in dip_range:
            config = {
                "excess_mass_z_threshold": z_thresh,
                "dip_test_p_threshold": dip_thresh,
            }
            r = _evaluate_detector(
                d03_datasets,
                ThresholdCompressionDetector,
                config,
                _build_d03_windows,
                "compression",
            )
            r["threshold"] = f"z={z_thresh},dip={dip_thresh}"
            results.append(r)

    return results


# ---------------------------------------------------------------------------
# Find optimal threshold
# ---------------------------------------------------------------------------


def find_optimal(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find the threshold with best balanced accuracy."""
    return max(results, key=lambda r: (r["balanced_accuracy"], r["f1"]))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 70)
    print("PR-16D: Threshold Sensitivity Analysis (Actual Detectors)")
    print("=" * 70)
    t_start = time.perf_counter()

    # Generate datasets
    print("\n[Phase 2] Generating synthetic datasets...")
    datasets = generate_all_datasets(seed=42)
    print(f"  Generated {len(datasets)} datasets")

    # D-01 sweep: alpha from 0.01 to 0.50
    print("\n[D-01] Sweeping ks_p_value_threshold...")
    d01_alphas = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10,
                  0.12, 0.15, 0.18, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
    d01_results = sweep_d01(datasets, d01_alphas)
    d01_optimal = find_optimal(d01_results)
    print(f"  Best: alpha={d01_optimal['threshold']}, "
          f"P={d01_optimal['precision']}, R={d01_optimal['recall']}, "
          f"F1={d01_optimal['f1']}, BA={d01_optimal['balanced_accuracy']}")

    # D-01 PSI sweep: psi from 0.05 to 2.0
    print("\n[D-01] Sweeping psi_threshold...")
    d01_psi_range = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25,
                     0.30, 0.35, 0.40, 0.50, 0.60, 0.80, 1.0, 1.5, 2.0]
    d01_psi_results = sweep_d01_psi(datasets, d01_psi_range)
    d01_psi_optimal = find_optimal(d01_psi_results)
    print(f"  Best: psi={d01_psi_optimal['threshold']}, "
          f"P={d01_psi_optimal['precision']}, R={d01_psi_optimal['recall']}, "
          f"F1={d01_psi_optimal['f1']}, BA={d01_psi_optimal['balanced_accuracy']}")

    # D-02 sweep: sudden_drop from 0.05 to 0.50
    print("\n[D-02] Sweeping sudden_drop_threshold...")
    d02_thresholds = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25,
                      0.30, 0.35, 0.40, 0.45, 0.50]
    d02_results = sweep_d02(datasets, d02_thresholds)
    d02_optimal = find_optimal(d02_results)
    print(f"  Best: threshold={d02_optimal['threshold']}, "
          f"P={d02_optimal['precision']}, R={d02_optimal['recall']}, "
          f"F1={d02_optimal['f1']}, BA={d02_optimal['balanced_accuracy']}")

    # D-03 sweep: z from 1.0 to 3.0
    print("\n[D-03] Sweeping excess_mass_z_threshold...")
    d03_z = [1.0, 1.2, 1.4, 1.5, 1.645, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0]
    d03_results = sweep_d03(datasets, d03_z)
    d03_optimal = find_optimal(d03_results)
    print(f"  Best: z={d03_optimal['threshold']}, "
          f"P={d03_optimal['precision']}, R={d03_optimal['recall']}, "
          f"F1={d03_optimal['f1']}, BA={d03_optimal['balanced_accuracy']}")

    # D-03 dip_test_p_threshold sweep
    print("\n[D-03] Sweeping dip_test_p_threshold...")
    d03_dip_range = [0.01, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    d03_dip_results = sweep_d03_dip(datasets, d03_dip_range)
    d03_dip_optimal = find_optimal(d03_dip_results)
    print(f"  Best: dip={d03_dip_optimal['threshold']}, "
          f"P={d03_dip_optimal['precision']}, R={d03_dip_optimal['recall']}, "
          f"F1={d03_dip_optimal['f1']}, BA={d03_dip_optimal['balanced_accuracy']}")

    # D-03 joint sweep: z × dip
    print("\n[D-03] Joint z × dip sweep...")
    d03_z_joint = [0.8, 1.0, 1.2, 1.4, 1.645]
    d03_dip_joint = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
    d03_joint_results = sweep_d03_joint(datasets, d03_z_joint, d03_dip_joint)
    d03_joint_optimal = find_optimal(d03_joint_results)
    print(f"  Best: {d03_joint_optimal['threshold']}, "
          f"P={d03_joint_optimal['precision']}, R={d03_joint_optimal['recall']}, "
          f"F1={d03_joint_optimal['f1']}, BA={d03_joint_optimal['balanced_accuracy']}")

    elapsed = time.perf_counter() - t_start
    print(f"\nSensitivity analysis completed in {elapsed:.2f}s")

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    # Strip per_dataset from sweep results for JSON (too verbose)
    d01_sweep = [{k: v for k, v in r.items() if k != "per_dataset"} for r in d01_results]
    d01_psi_sweep = [{k: v for k, v in r.items() if k != "per_dataset"} for r in d01_psi_results]
    d02_sweep = [{k: v for k, v in r.items() if k != "per_dataset"} for r in d02_results]
    d03_sweep = [{k: v for k, v in r.items() if k != "per_dataset"} for r in d03_results]
    d03_dip_sweep = [{k: v for k, v in r.items() if k != "per_dataset"} for r in d03_dip_results]
    d03_joint_sweep = [{k: v for k, v in r.items() if k != "per_dataset"} for r in d03_joint_results]

    output = {
        "d01_sweep": d01_sweep,
        "d01_optimal": {k: v for k, v in d01_optimal.items() if k != "per_dataset"},
        "d01_psi_sweep": d01_psi_sweep,
        "d01_psi_optimal": {k: v for k, v in d01_psi_optimal.items() if k != "per_dataset"},
        "d02_sweep": d02_sweep,
        "d02_optimal": {k: v for k, v in d02_optimal.items() if k != "per_dataset"},
        "d03_sweep": d03_sweep,
        "d03_optimal": {k: v for k, v in d03_optimal.items() if k != "per_dataset"},
        "d03_dip_sweep": d03_dip_sweep,
        "d03_dip_optimal": {k: v for k, v in d03_dip_optimal.items() if k != "per_dataset"},
        "d03_joint_sweep": d03_joint_sweep,
        "d03_joint_optimal": {k: v for k, v in d03_joint_optimal.items() if k != "per_dataset"},
    }

    with open(OUTPUT_DIR / "sensitivity_analysis.json", "w") as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\nResults saved to: {OUTPUT_DIR.resolve()}")

    # Print summary
    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("=" * 70)

    for name, opt, targets in [
        ("D-01 (KS)", d01_optimal, {"P": 0.80, "R": 0.75}),
        ("D-01 (PSI)", d01_psi_optimal, {"P": 0.80, "R": 0.75}),
        ("D-02", d02_optimal, {"P": 0.75, "R": 0.70}),
        ("D-03 (z)", d03_optimal, {"P": 0.85, "R": 0.80}),
        ("D-03 (dip)", d03_dip_optimal, {"P": 0.85, "R": 0.80}),
    ]:
        print(f"\n{name} optimal: {opt['threshold']}")
        print(f"  P={opt['precision']} R={opt['recall']} F1={opt['f1']} BA={opt['balanced_accuracy']}")
        print(f"  TP={opt['tp']} FP={opt['fp']} FN={opt['fn']} TN={opt['tn']}")
        p_met = opt["precision"] >= targets["P"]
        r_met = opt["recall"] >= targets["R"]
        print(f"  IMP 1.6: P>={targets['P']}={'PASS' if p_met else 'FAIL'}, R>={targets['R']}={'PASS' if r_met else 'FAIL'}")


if __name__ == "__main__":
    main()
