"""
Benchmark V2 Generation & Determinism Verification

Generates all V2 datasets and verifies deterministic output.
"""
import json
import os
import sys
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from miie.experimental.benchmark.generator import BenchmarkV2Generator


def main():
    """Run generation and verification."""
    output_dir = "benchmarks/v2/datasets"
    report_dir = "benchmarks/results/pr22_benchmark_evolution"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    print("=" * 70)
    print("BENCHMARK V2 GENERATION & DETERMINISM VERIFICATION")
    print("=" * 70)

    # Step 1: Generate with seed 42
    print("\n[1/4] Generating datasets with seed=42...")
    gen = BenchmarkV2Generator(output_dir=output_dir)
    datasets_run1 = gen.generate_all(seed=42)
    print(f"  Generated {len(datasets_run1)} datasets")

    # Step 2: Generate again with same seed
    print("\n[2/4] Re-generating with seed=42 (determinism check)...")
    gen2 = BenchmarkV2Generator(output_dir=output_dir)
    datasets_run2 = gen2.generate_all(seed=42)

    # Step 3: Verify determinism
    print("\n[3/4] Verifying determinism...")
    all_match = True
    mismatched = []
    for d1, d2 in zip(datasets_run1, datasets_run2):
        # Compare the stored hash (computed before timestamp)
        if d1["hash"] != d2["hash"]:
            all_match = False
            mismatched.append(d1["scenario_id"])

    if all_match:
        print("  PASS: All datasets are deterministic")
    else:
        print(f"  FAIL: {len(mismatched)} datasets differ")
        for mid in mismatched:
            print(f"    - {mid}")

    # Step 4: Generate with different seed (seed 123)
    print("\n[4/4] Generating with seed=123 (different seed check)...")
    gen3 = BenchmarkV2Generator(output_dir=output_dir)
    datasets_run3 = gen3.generate_all(seed=123)

    # Compare stored hashes (deterministic content only)
    diff_seed_match = sum(
        1 for d1, d2 in zip(datasets_run1, datasets_run3) if d1["hash"] == d2["hash"]
    )
    print(f"  {diff_seed_match}/{len(datasets_run1)} datasets match across different seeds")

    # Save datasets
    print("\nSaving datasets...")
    gen.save_datasets(datasets_run1)
    print(f"  Saved to {output_dir}")

    # Summary
    summary = gen.get_summary()
    print("\n" + "=" * 70)
    print("GENERATION SUMMARY")
    print("=" * 70)
    print(f"  Total scenarios: {summary['total_scenarios']}")
    print(f"  Scenario types: {summary['scenario_counts']}")
    print(f"  Difficulty distribution: {summary['difficulty_counts']}")
    print(f"  Determinism: {'PASS' if all_match else 'FAIL'}")

    # Difficulty breakdown
    print("\n  Difficulty breakdown:")
    for diff, count in sorted(summary['difficulty_counts'].items()):
        print(f"    Level {diff}: {count} scenarios")

    # Scenario type breakdown
    print("\n  Scenario type breakdown:")
    for stype, count in sorted(summary['scenario_counts'].items()):
        print(f"    {stype}: {count}")

    # Write generation report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_datasets": len(datasets_run1),
        "seed": 42,
        "determinism_check": {
            "match_same_seed": all_match,
            "mismatches": mismatched,
            "different_seed_match_rate": f"{diff_seed_match}/{len(datasets_run1)}",
        },
        "summary": summary,
        "datasets": [
            {
                "id": d["scenario_id"],
                "name": d["metadata"]["name"],
                "type": d["metadata"]["scenario_type"],
                "difficulty": d["metadata"]["difficulty"],
                "hash": d["hash"],
                "anomaly_present": d.get("anomaly_present", False),
            }
            for d in datasets_run1
        ],
    }

    report_path = os.path.join(report_dir, "PR22_PHASE5_GENERATION_REPORT.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  Report saved: {report_path}")

    print("\n" + "=" * 70)
    print("PHASE 5 COMPLETE")
    print("=" * 70)

    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())
