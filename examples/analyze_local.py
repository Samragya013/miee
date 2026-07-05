#!/usr/bin/env python3
"""Analyze a local repository with MIIE."""

import sys
from pathlib import Path

from miie.orchestration.pipeline import AnalysisPipeline
from miie.config.loader import load_config


def main():
    # Get repository path from argument or use current directory
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Validate path
    if not Path(repo_path).exists():
        print(f"Error: Repository not found: {repo_path}")
        sys.exit(1)

    # Load configuration
    config = load_config()

    # Create and run pipeline
    pipeline = AnalysisPipeline(config)
    results = pipeline.run(repo_path)

    # Display results
    print(f"\nRepository: {repo_path}")
    print(f"Integrity Score: {results['integrity_score']:.3f}")
    print(f"Confidence Score: {results['confidence_score']:.3f}")

    # Display detector results
    for detector_id, output in results.get("detector_outputs", {}).items():
        detected = output.get("drift_detected") or output.get("breakdown_detected") or output.get("compression_detected")
        status = "DETECTED" if detected else "CLEAR"
        print(f"  {detector_id}: {status}")


if __name__ == "__main__":
    main()
