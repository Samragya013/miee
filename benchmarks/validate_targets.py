"""Validate Detector Targets Against IMP §1.6 Hard Requirements.

Reads evaluation JSONs from benchmarks/results/ and checks each detector
against its hard target. Prints PASS/FAIL per target and exits with
code 0 if all pass, 1 if any fail.

Usage:
    python benchmarks/validate_targets.py [--results-dir benchmarks/results/]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# IMP §1.6 hard targets
HARD_TARGETS = {
    "D-01": {"precision": 0.80, "recall": 0.75},
    "D-02": {"precision": 0.75, "recall": 0.70},
    "D-03": {"precision": 0.85, "recall": 0.80},
}


def load_evaluation(detector_id: str, results_dir: Path) -> Dict[str, Any]:
    """Load the evaluation JSON for a given detector."""
    eval_path = results_dir / f"{detector_id}_evaluation.json"
    if not eval_path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {eval_path}")
    with open(eval_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_targets(eval_result: Dict[str, Any]) -> Tuple[Dict[str, bool], Dict[str, float]]:
    """Check evaluation metrics against hard targets.

    Returns:
        Tuple of (status_dict, metrics_dict) where status_dict maps
        metric names to pass/fail booleans.
    """
    detector_id = eval_result["detector_id"]
    target = HARD_TARGETS[detector_id]
    metrics = eval_result["metrics"]

    precision_val = metrics.get("precision", 0.0)
    recall_val = metrics.get("recall", 0.0)

    status = {
        "precision": precision_val >= target["precision"],
        "recall": recall_val >= target["recall"],
    }
    actual = {
        "precision": precision_val,
        "recall": recall_val,
    }
    return status, actual


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate MIIE detector performance against IMP §1.6 hard targets.")
    parser.add_argument(
        "--results-dir",
        type=str,
        default="benchmarks/results/",
        help="Directory containing evaluation JSONs (default: benchmarks/results/)",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"ERROR: Results directory does not exist: {results_dir.resolve()}")
        print("Run 'python benchmarks/run_evaluation.py' first to generate results.")
        return 1

    all_pass = True

    print("=" * 60)
    print("MIIE Detector Target Validation (IMP 1.6)")
    print("=" * 60)

    for detector_id, target in HARD_TARGETS.items():
        print(f"\n{detector_id} (suite target: P>={target['precision']}, R>={target['recall']})")
        print("-" * 60)

        try:
            eval_result = load_evaluation(detector_id, results_dir)
        except FileNotFoundError as e:
            print(f"  ERROR: {e}")
            all_pass = False
            continue

        status, actual = check_targets(eval_result)

        for metric_name in ("precision", "recall"):
            target_val = target[metric_name]
            actual_val = actual[metric_name]
            passed = status[metric_name]
            marker = "PASS" if passed else "FAIL"
            print(f"  {metric_name:12s}: {actual_val:.4f}  (target: {target_val:.2f})  [{marker}]")
            if not passed:
                all_pass = False

    print("\n" + "=" * 60)
    overall = "ALL TARGETS MET" if all_pass else "TARGETS NOT MET"
    print(f"Overall: {overall}")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
