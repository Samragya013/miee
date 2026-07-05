#!/usr/bin/env python3
"""Analyze a GitHub repository with MIIE."""

import os
import sys

from miie.orchestration.pipeline import AnalysisPipeline
from miie.config.loader import load_config


def main():
    # Get repository URL
    if len(sys.argv) > 1:
        repo_url = sys.argv[1]
    else:
        repo_url = input("Enter GitHub repository URL: ")

    # Get auth token
    auth_token = os.environ.get("GITHUB_TOKEN")
    if len(sys.argv) > 2:
        auth_token = sys.argv[2]

    if not auth_token:
        print("Warning: No GitHub token provided. Rate limits may apply.")
        print("Set GITHUB_TOKEN environment variable or pass as second argument.")

    # Load configuration
    config = load_config()
    if auth_token:
        config["auth_token"] = auth_token

    # Create and run pipeline
    pipeline = AnalysisPipeline(config)
    results = pipeline.run(repo_url)

    # Display results
    print(f"\nRepository: {repo_url}")
    print(f"Integrity Score: {results['integrity_score']:.3f}")
    print(f"Confidence Score: {results['confidence_score']:.3f}")


if __name__ == "__main__":
    main()
