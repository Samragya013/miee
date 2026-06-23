#!/usr/bin/env python3
"""Script to generate all 120 benchmark candidates (40 per suite) and update manifest."""

import shutil
import os
import stat
from pathlib import Path
from miie.benchmark.generator import BenchmarkDatasetGenerator

def remove_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main():
    base_dir = Path("C:/Users/Samragya/Downloads/MIEE")
    candidates_dir = base_dir / "benchmarks" / "candidates"
    tmp_dir = base_dir / "benchmarks" / "tmp"

    # Ensure candidates directory exists
    candidates_dir.mkdir(parents=True, exist_ok=True)

    # Clean existing candidates (if any)
    if candidates_dir.exists():
        shutil.rmtree(candidates_dir, onerror=remove_readonly)
    candidates_dir.mkdir(parents=True)

    generator = BenchmarkDatasetGenerator()

    # Suites and their corresponding directory names under tmp
    suites = [
        ("metric-drift", "metric-drift"),
        ("correlation-breakdown", "correlation-breakdown"),
        ("threshold-compression", "threshold-compression")
    ]

    all_generated_paths = []
    base_seed = 42  # Fixed seed for reproducibility

    for suite_name, tmp_subdir in suites:
        suite_tmp = tmp_dir / tmp_subdir
        # Clean suite tmp directory
        if suite_tmp.exists():
            shutil.rmtree(suite_tmp, onerror=remove_readonly)
        suite_tmp.mkdir(parents=True)

        print(f"Generating 40 candidates for suite: {suite_name}")
        # Generate 40 candidates for this suite
        paths = generator.generate(
            dataset_type=suite_name,
            count=40,
            output_dir=suite_tmp,
            seed=base_seed
        )
        print(f"Generated {len(paths)} candidates in {suite_tmp}")

        # Move each candidate to the main candidates directory with appropriate index
        # The paths are in the order they were generated (candidate_001 to candidate_040)
        for i, src_path in enumerate(paths):
            # Determine global candidate index (1-based)
            # We need to know which suite we are in to compute the offset
            # We'll compute offset by keeping a running count
            pass  # We'll implement after the loop

        # Instead of moving inside the loop, we'll collect all paths and then process
        all_generated_paths.extend(paths)

    # Now we have all_generated_paths with 120 entries, but they are grouped by suite
    # and each group has directories named candidate_001 to candidate_040.
    # We need to rename them to have unique global indices.

    # We'll process by suite again, but this time we know the order.
    # Let's reset and do it properly.

    # Actually, let's redo the loop with moving.

    # Clear the list
    all_generated_paths = []

    for suite_idx, (suite_name, tmp_subdir) in enumerate(suites):
        suite_tmp = tmp_dir / tmp_subdir
        offset = suite_idx * 40  # 0, 40, 80

        print(f"Processing suite {suite_name} (offset {offset})")

        # Get the list of generated candidate directories (they are candidate_001 to candidate_040)
        # They should already exist in suite_tmp from the generation step
        # But we need to regenerate because we cleared the tmp directory above?
        # We didn't clear it after generation, so they are still there.

        # Actually, we generated them and left them in suite_tmp. Good.

        # List the directories in suite_tmp that match candidate_###
        candidate_dirs = sorted([d for d in suite_tmp.iterdir() if d.is_dir() and d.name.startswith("candidate_")])
        print(f"Found {len(candidate_dirs)} candidate directories in {suite_tmp}")

        for i, src_dir in enumerate(candidate_dirs):
            # Local index within suite (0-based)
            local_idx = i
            # Global candidate index (1-based)
            global_idx = offset + local_idx + 1
            # New directory name
            new_name = f"candidate_{global_idx:03d}"
            dst_dir = candidates_dir / new_name

            print(f"  Moving {src_dir.name} -> {new_name}")
            # Move the directory
            shutil.move(str(src_dir), str(dst_dir))
            all_generated_paths.append(dst_dir)

    print(f"Total candidates moved: {len(all_generated_paths)}")

    # Update manifest with all candidates
    print("Updating manifest...")
    generator.update_manifest(
        output_dir=candidates_dir,
        generated_paths=all_generated_paths,
        dataset_type="mixed",  # We'll pass a dummy value; the update_manifest method uses the dataset_type for anomaly determination
        base_seed=base_seed
    )
    print("Manifest updated.")

    # Clean up tmp directory
    shutil.rmtree(tmp_dir, onerror=remove_readonly)
    print("Cleaned up temporary directory.")

    print("Done!")

if __name__ == "__main__":
    main()