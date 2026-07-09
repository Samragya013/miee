"""
PR-22 Phase 6: Scientific Stress Testing

Evaluates D-01, D-02, D-03 against V1 and V2 datasets to measure
the benchmark's discriminatory power.
"""
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np

from miie.processing.detection.distribution_drift_detector import DistributionDriftDetector
from miie.processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
from miie.processing.detection.threshold_compression_detector import ThresholdCompressionDetector
from miie.schemas.models import MetricDataFrame


# Constants
OBSERVATIONS_PER_WINDOW = 20
N_WINDOWS = 10
WINDOW_IDS = [f"w{i}" for i in range(N_WINDOWS)]


def dataset_to_metric_dataframe(dataset: Dict[str, Any], window_size: int = 20) -> MetricDataFrame:
    """Convert a V2 dataset into MetricDataFrame for detector consumption.

    Args:
        dataset: V2 generated dataset
        window_size: Number of observations per window

    Returns:
        MetricDataFrame suitable for detector input
    """
    # Determine which metric values to use
    if "values" in dataset:
        values = dataset["values"]
        metric_id = dataset.get("metric_id", "M-03")
        metrics_data = {metric_id: values}
    elif "metric_a" in dataset:
        # Correlation scenario: use both metrics
        metric_a_id = dataset.get("metric_a", {}).get("metric_id", "M-01") if isinstance(dataset.get("metric_a"), dict) else "M-01"
        metric_b_id = "M-03"
        metrics_data = {
            metric_a_id: dataset["metric_a"],
            metric_b_id: dataset["metric_b"],
        }
    elif "metrics" in dataset:
        # Multivariate scenario
        metrics_data = dataset["metrics"]
    else:
        raise ValueError(f"Unknown dataset format: {list(dataset.keys())}")

    # Convert to windowed format
    windowed_metrics = {}
    for metric_id, values in metrics_data.items():
        windowed = {}
        for i in range(0, len(values), window_size):
            window_values = values[i:i + window_size]
            window_id = f"w{i // window_size}"
            if len(window_values) > 0:
                windowed[window_id] = window_values
        windowed_metrics[metric_id] = windowed

    return MetricDataFrame(
        repo_id=dataset.get("scenario_id", "unknown"),
        run_id="benchmark_v2",
        timestamp=datetime.now(),
        metrics=windowed_metrics,
    )


def evaluate_detector(
    detector,
    detector_id: str,
    metric_df: MetricDataFrame,
    ground_truth_anomaly: bool,
) -> Dict[str, Any]:
    """Run a detector and compare against ground truth.

    Args:
        detector: Detector instance
        detector_id: Detector ID string
        metric_df: MetricDataFrame input
        ground_truth_anomaly: Whether anomaly is present in ground truth

    Returns:
        Dictionary with evaluation results
    """
    try:
        start_time = time.time()
        result = detector.execute(metric_df)
        elapsed = time.time() - start_time

        detector_outputs = result.detector_outputs
        detector_data = detector_outputs.get(detector_id, {})

        # Determine if detector flagged anomaly
        if detector_id == "D-01":
            predicted_anomaly = detector_data.get("drift_detected", False)
        elif detector_id == "D-02":
            predicted_anomaly = detector_data.get("breakdown_detected", False)
        elif detector_id == "D-03":
            predicted_anomaly = detector_data.get("compression_detected", False)
        else:
            predicted_anomaly = False

        # Confusion matrix entry
        tp = predicted_anomaly and ground_truth_anomaly
        fp = predicted_anomaly and not ground_truth_anomaly
        fn = not predicted_anomaly and ground_truth_anomaly
        tn = not predicted_anomaly and not ground_truth_anomaly

        # Severity score
        if detector_id == "D-01":
            severity = detector_data.get("drift_magnitude", 0.0)
        elif detector_id == "D-02":
            severity = detector_data.get("breakdown_magnitude", 0.0)
        elif detector_id == "D-03":
            severity = detector_data.get("compression_index", 0.0)
        else:
            severity = 0.0

        return {
            "correct": predicted_anomaly == ground_truth_anomaly,
            "predicted": int(predicted_anomaly),
            "ground_truth": int(ground_truth_anomaly),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "severity": severity,
            "elapsed_seconds": elapsed,
            "error": None,
        }

    except Exception as e:
        return {
            "correct": False,
            "predicted": 0,
            "ground_truth": int(ground_truth_anomaly),
            "tp": False,
            "fp": False,
            "fn": not ground_truth_anomaly,
            "tn": ground_truth_anomaly,
            "severity": 0.0,
            "elapsed_seconds": 0.0,
            "error": str(e),
        }


def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate metrics from individual results.

    Args:
        results: List of per-dataset evaluation results

    Returns:
        Dictionary with precision, recall, F1, accuracy, FPR
    """
    tp = sum(1 for r in results if r["tp"])
    fp = sum(1 for r in results if r["fp"])
    fn = sum(1 for r in results if r["fn"])
    tn = sum(1 for r in results if r["tn"])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    errors = [r for r in results if r["error"] is not None]
    avg_severity = np.mean([r["severity"] for r in results if r["error"] is None])
    avg_time = np.mean([r["elapsed_seconds"] for r in results if r["error"] is None])

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "fpr": fpr,
        "fnr": fnr,
        "avg_severity": float(avg_severity),
        "avg_time_ms": float(avg_time * 1000),
        "n_errors": len(errors),
        "n_total": len(results),
    }


def compute_discriminatory_power(detector_metrics: Dict[str, Dict[str, float]]) -> float:
    """Compute benchmark discriminatory power.

    Discriminatory power = fraction of detectors that achieve DIFFERENT
    F1 scores across the benchmark. If all detectors score the same,
    discriminatory power = 0.

    Returns:
        Discriminatory power in [0, 1]
    """
    f1_scores = [m["f1"] for m in detector_metrics.values()]
    if len(f1_scores) < 2:
        return 0.0

    # Count unique F1 scores
    unique_f1 = len(set(round(f1, 3) for f1 in f1_scores))
    # Discriminatory power = (unique - 1) / (total - 1)
    return (unique_f1 - 1) / (len(f1_scores) - 1)


def main():
    """Run stress testing across V2 datasets."""
    print("=" * 70)
    print("PR-22 PHASE 6: SCIENTIFIC STRESS TESTING")
    print("=" * 70)

    # Initialize detectors
    print("\n[1/5] Initializing detectors...")
    detectors = {
        "D-01": DistributionDriftDetector(),
        "D-02": CorrelationBreakdownDetector(),
        "D-03": ThresholdCompressionDetector(),
    }
    print("  D-01: DistributionDriftDetector")
    print("  D-02: CorrelationBreakdownDetector")
    print("  D-03: ThresholdCompressionDetector")

    # Load V2 datasets
    v2_index_path = "benchmarks/v2/datasets/index.json"
    print(f"\n[2/5] Loading V2 datasets from {v2_index_path}...")
    with open(v2_index_path) as f:
        v2_index = json.load(f)

    print(f"  Loaded {v2_index['total_datasets']} V2 datasets")

    # Load V2 dataset files
    v2_datasets = []
    for ds_info in v2_index["datasets"]:
        ds_path = os.path.join("benchmarks/v2/datasets", ds_info["id"], "dataset.json")
        if os.path.exists(ds_path):
            with open(ds_path) as f:
                dataset = json.load(f)
                v2_datasets.append(dataset)

    print(f"  Successfully loaded {len(v2_datasets)} datasets")

    # Load V1 datasets for comparison
    print("\n[3/5] Loading V1 datasets...")
    v1_index_path = "benchmarks/ground_truth/index.json"
    v1_datasets = []
    if os.path.exists(v1_index_path):
        with open(v1_index_path) as f:
            v1_index = json.load(f)
        for ds_info in v1_index.get("datasets", []):
            ds_path = os.path.join("benchmarks/ground_truth", ds_info.get("id", ""), "dataset.json")
            if os.path.exists(ds_path):
                with open(ds_path) as f:
                    dataset = json.load(f)
                    v1_datasets.append(dataset)
    print(f"  Loaded {len(v1_datasets)} V1 datasets")

    # Evaluate against V2 datasets
    print("\n[4/5] Evaluating detectors against V2 datasets...")
    all_results = {}

    for detector_id, detector in detectors.items():
        print(f"\n  Evaluating {detector_id}...")
        detector_results = []

        for dataset in v2_datasets:
            ground_truth = dataset.get("anomaly_present", False)
            metric_df = dataset_to_metric_dataframe(dataset)

            result = evaluate_detector(detector, detector_id, metric_df, ground_truth)
            result["scenario_id"] = dataset["scenario_id"]
            result["scenario_type"] = dataset.get("metadata", {}).get("scenario_type", "unknown")
            result["difficulty"] = dataset.get("metadata", {}).get("difficulty", 0)
            detector_results.append(result)

        metrics = compute_metrics(detector_results)
        all_results[detector_id] = {
            "individual_results": detector_results,
            "aggregate_metrics": metrics,
        }
        print(f"    F1={metrics['f1']:.3f} P={metrics['precision']:.3f} R={metrics['recall']:.3f} "
              f"Acc={metrics['accuracy']:.3f} (TP={metrics['tp']} FP={metrics['fp']} "
              f"FN={metrics['fn']} TN={metrics['tn']})")

    # Compute discriminatory power
    print("\n[5/5] Computing discriminatory power...")
    detector_metrics = {k: v["aggregate_metrics"] for k, v in all_results.items()}
    disc_power = compute_discriminatory_power(detector_metrics)
    print(f"  Discriminatory power: {disc_power:.1%}")

    # By scenario type
    print("\n  Results by scenario type:")
    for scenario_type in ["drift", "correlation", "threshold", "stress", "multivariate"]:
        type_results = {did: [] for did in detectors}
        for dataset in v2_datasets:
            if dataset.get("metadata", {}).get("scenario_type") == scenario_type:
                for did in detectors:
                    for r in all_results[did]["individual_results"]:
                        if r["scenario_id"] == dataset["scenario_id"]:
                            type_results[did].append(r)

        if any(len(v) > 0 for v in type_results.values()):
            print(f"\n    {scenario_type.upper()}:")
            for did, results in type_results.items():
                if results:
                    m = compute_metrics(results)
                    print(f"      {did}: F1={m['f1']:.3f} P={m['precision']:.3f} R={m['recall']:.3f}")

    # By difficulty level
    print("\n  Results by difficulty level:")
    for level in [1, 2, 3, 4]:
        level_results = {did: [] for did in detectors}
        for dataset in v2_datasets:
            if dataset.get("metadata", {}).get("difficulty") == level:
                for did in detectors:
                    for r in all_results[did]["individual_results"]:
                        if r["scenario_id"] == dataset["scenario_id"]:
                            level_results[did].append(r)

        if any(len(v) > 0 for v in level_results.values()):
            print(f"\n    Level {level}:")
            for did, results in level_results.items():
                if results:
                    m = compute_metrics(results)
                    print(f"      {did}: F1={m['f1']:.3f} P={m['precision']:.3f} R={m['recall']:.3f}")

    # Write report
    report_dir = "benchmarks/results/pr22_benchmark_evolution"
    os.makedirs(report_dir, exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "v2_datasets_evaluated": len(v2_datasets),
        "v1_datasets_evaluated": len(v1_datasets),
        "discriminatory_power": disc_power,
        "detector_summary": {
            did: {
                "f1": all_results[did]["aggregate_metrics"]["f1"],
                "precision": all_results[did]["aggregate_metrics"]["precision"],
                "recall": all_results[did]["aggregate_metrics"]["recall"],
                "accuracy": all_results[did]["aggregate_metrics"]["accuracy"],
                "fpr": all_results[did]["aggregate_metrics"]["fpr"],
                "tp": all_results[did]["aggregate_metrics"]["tp"],
                "fp": all_results[did]["aggregate_metrics"]["fp"],
                "fn": all_results[did]["aggregate_metrics"]["fn"],
                "tn": all_results[did]["aggregate_metrics"]["tn"],
            }
            for did in detectors
        },
        "by_scenario_type": {},
        "by_difficulty": {},
    }

    # Populate by scenario type
    for scenario_type in ["drift", "correlation", "threshold", "stress", "multivariate"]:
        report["by_scenario_type"][scenario_type] = {}
        for did in detectors:
            type_results = [r for r in all_results[did]["individual_results"]
                           if r.get("scenario_type") == scenario_type]
            if type_results:
                report["by_scenario_type"][scenario_type][did] = compute_metrics(type_results)

    # Populate by difficulty
    for level in [1, 2, 3, 4]:
        report["by_difficulty"][str(level)] = {}
        for did in detectors:
            level_results = [r for r in all_results[did]["individual_results"]
                            if r.get("difficulty") == level]
            if level_results:
                report["by_difficulty"][str(level)][did] = compute_metrics(level_results)

    report_path = os.path.join(report_dir, "PR22_PHASE6_STRESS_TESTING.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n  Report saved: {report_path}")

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 6 SUMMARY")
    print("=" * 70)
    print(f"  V2 datasets evaluated: {len(v2_datasets)}")
    print(f"  Discriminatory power: {disc_power:.1%}")
    for did in detectors:
        m = all_results[did]["aggregate_metrics"]
        print(f"  {did}: F1={m['f1']:.3f} P={m['precision']:.3f} R={m['recall']:.3f} Acc={m['accuracy']:.3f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
