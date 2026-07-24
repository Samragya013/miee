"""
Benchmark Runner for Experimental Detectors

Provides utilities for running benchmarks on experimental detectors
and comparing results against PR-17 baselines.

Author: MIIE Research Team
Date: 2026-07-05
Status: EXPERIMENTAL - Not production-certified
"""

import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


def run_benchmark(
    detector_func: Callable, datasets: Dict[str, Dict[str, Any]], detector_name: str, **kwargs
) -> Dict[str, Any]:
    """
    Run benchmark on a detector across multiple datasets.

    Args:
        detector_func: Detector function to benchmark
        datasets: Dictionary of datasets with format:
                  {dataset_name: {"data": np.ndarray, "is_anomaly": bool, ...}}
        detector_name: Name of the detector for reporting
        **kwargs: Additional arguments to pass to detector_func

    Returns:
        Dictionary with benchmark results
    """
    results = {
        "detector_name": detector_name,
        "timestamp": datetime.now().isoformat(),
        "n_datasets": len(datasets),
        "datasets": {},
        "summary": {"true_positives": 0, "false_positives": 0, "true_negatives": 0, "false_negatives": 0},
    }

    for dataset_name, dataset_info in datasets.items():
        data = dataset_info["data"]
        is_anomaly = dataset_info.get("is_anomaly", False)

        # Run detector
        try:
            detection_result = detector_func(data, **kwargs)

            # Extract detection status
            if isinstance(detection_result, dict):
                detected = detection_result.get(
                    "drift_detected",
                    detection_result.get("compression_detected", detection_result.get("is_bimodal", False)),
                )
            else:
                detected = bool(detection_result)

            # Classify result
            if detected and is_anomaly:
                result_type = "TP"
                results["summary"]["true_positives"] += 1
            elif detected and not is_anomaly:
                result_type = "FP"
                results["summary"]["false_positives"] += 1
            elif not detected and not is_anomaly:
                result_type = "TN"
                results["summary"]["true_negatives"] += 1
            else:  # not detected and is_anomaly
                result_type = "FN"
                results["summary"]["false_negatives"] += 1

            results["datasets"][dataset_name] = {
                "detected": detected,
                "result_type": result_type,
                "details": detection_result,
            }

        except Exception as e:
            results["datasets"][dataset_name] = {"detected": False, "result_type": "ERROR", "error": str(e)}

    # Compute metrics
    tp = results["summary"]["true_positives"]
    fp = results["summary"]["false_positives"]
    tn = results["summary"]["true_negatives"]
    fn = results["summary"]["false_negatives"]

    results["summary"]["precision"] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    results["summary"]["recall"] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    results["summary"]["f1_score"] = (
        2
        * results["summary"]["precision"]
        * results["summary"]["recall"]
        / (results["summary"]["precision"] + results["summary"]["recall"])
        if (results["summary"]["precision"] + results["summary"]["recall"]) > 0
        else 0.0
    )
    results["summary"]["accuracy"] = (tp + tn) / (tp + fp + tn + fn)

    return results


def compare_detectors(
    benchmark_results: List[Dict[str, Any]], baseline_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compare multiple detector benchmark results.

    Args:
        benchmark_results: List of benchmark results from run_benchmark
        baseline_results: Optional baseline results from PR-17

    Returns:
        Comparison summary
    """
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "n_detectors": len(benchmark_results),
        "detectors": {},
        "ranking": [],
    }

    # Extract metrics for each detector
    for result in benchmark_results:
        detector_name = result["detector_name"]
        comparison["detectors"][detector_name] = {
            "precision": result["summary"]["precision"],
            "recall": result["summary"]["recall"],
            "f1_score": result["summary"]["f1_score"],
            "accuracy": result["summary"]["accuracy"],
            "true_positives": result["summary"]["true_positives"],
            "false_positives": result["summary"]["false_positives"],
            "true_negatives": result["summary"]["true_negatives"],
            "false_negatives": result["summary"]["false_negatives"],
        }

    # Add baseline if provided
    if baseline_results:
        comparison["detectors"]["PR-17_Baseline"] = {
            "precision": baseline_results.get("precision", 0),
            "recall": baseline_results.get("recall", 0),
            "f1_score": baseline_results.get("f1_score", 0),
            "accuracy": baseline_results.get("accuracy", 0),
        }

    # Rank by F1 score
    comparison["ranking"] = sorted(
        comparison["detectors"].keys(), key=lambda x: comparison["detectors"][x]["f1_score"], reverse=True  # type: ignore
    )

    # Check IMP targets
    comparison["imp_targets"] = {
        "D-01": {"precision": 0.80, "recall": 0.75},
        "D-03": {"precision": 0.85, "recall": 0.80},
    }

    comparison["meets_imp_targets"] = {}
    for detector_name, metrics in comparison["detectors"].items():  # type: ignore
        # Determine if D-01 or D-03 based on name
        if "D-01" in detector_name or "drift" in detector_name.lower():
            target = comparison["imp_targets"]["D-01"]
        else:
            target = comparison["imp_targets"]["D-03"]

        meets = metrics["precision"] >= target["precision"] and metrics["recall"] >= target["recall"]
        comparison["meets_imp_targets"][detector_name] = meets

    return comparison


def save_results(results: Dict[str, Any], output_path: str, format: str = "json") -> None:
    """
    Save benchmark results to file.

    Args:
        results: Results dictionary
        output_path: Path to save file
        format: Output format ('json' or 'markdown')
    """
    if format == "json":
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
    elif format == "markdown":
        _save_as_markdown(results, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")


def _save_as_markdown(results: Dict[str, Any], output_path: str) -> None:
    """Save results as markdown table."""
    with open(output_path, "w") as f:
        f.write("# Benchmark Results\n\n")
        f.write(f"**Detector**: {results.get('detector_name', 'Unknown')}\n")
        f.write(f"**Timestamp**: {results.get('timestamp', 'Unknown')}\n\n")

        # Summary
        summary = results.get("summary", {})
        f.write("## Summary\n\n")
        f.write(f"- True Positives: {summary.get('true_positives', 0)}\n")
        f.write(f"- False Positives: {summary.get('false_positives', 0)}\n")
        f.write(f"- True Negatives: {summary.get('true_negatives', 0)}\n")
        f.write(f"- False Negatives: {summary.get('false_negatives', 0)}\n")
        f.write(f"- Precision: {summary.get('precision', 0):.3f}\n")
        f.write(f"- Recall: {summary.get('recall', 0):.3f}\n")
        f.write(f"- F1 Score: {summary.get('f1_score', 0):.3f}\n\n")

        # Dataset details
        f.write("## Dataset Results\n\n")
        f.write("| Dataset | Detected | Result Type |\n")
        f.write("|---------|----------|-------------|\n")

        for dataset_name, dataset_result in results.get("datasets", {}).items():
            detected = "✓" if dataset_result.get("detected") else "✗"
            result_type = dataset_result.get("result_type", "Unknown")
            f.write(f"| {dataset_name} | {detected} | {result_type} |\n")


if __name__ == "__main__":
    # Example usage
    print("Benchmark runner utilities loaded successfully.")
    print("Use run_benchmark() to benchmark detectors.")
    print("Use compare_detectors() to compare results.")
