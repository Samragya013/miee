#!/usr/bin/env python3
"""Batch analysis of multiple repositories."""

import json
import sys
from pathlib import Path

from miie.orchestration.pipeline import AnalysisPipeline
from miie.config.loader import load_config


def main():
    # Get list of repositories
    if len(sys.argv) > 1:
        repos_file = sys.argv[1]
        repos = Path(repos_file).read_text().strip().split("\n")
    else:
        repos = ["."]
        print("Usage: python batch_analysis.py repos.txt")
        print("repos.txt should contain one repository path per line")
        print("Analyzing current directory as default...")

    # Load configuration
    config = load_config()
    pipeline = AnalysisPipeline(config)

    results = []
    for repo in repos:
        repo = repo.strip()
        if not repo or repo.startswith("#"):
            continue

        print(f"\nAnalyzing {repo}...")
        try:
            result = pipeline.run(repo)
            result["repository"] = repo
            results.append(result)
            print(f"  Integrity: {result['integrity_score']:.3f}")
            print(f"  Confidence: {result['confidence_score']:.3f}")
        except Exception as e:
            print(f"  Error: {e}")
            results.append({"repository": repo, "error": str(e)})

    # Write summary
    output_file = "batch_results.json"
    Path(output_file).write_text(
        json.dumps(results, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\nBatch results written to {output_file}")
    print(f"Analyzed {len(results)} repositories")


if __name__ == "__main__":
    main()
