#!/usr/bin/env python3
"""Python API usage demonstration."""

import sys
from pathlib import Path

from miie.orchestration.pipeline import AnalysisPipeline
from miie.config.loader import ConfigLoader
from miie.cli.formatting import generate_markdown_report, generate_html_report


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Load configuration
    loader = ConfigLoader()
    config = loader.load(overrides={"repo": repo_path})
    print(f"Configuration loaded: {config.config_hash}")

    # Create pipeline
    pipeline = AnalysisPipeline(config)
    print("Pipeline created")

    # Run analysis
    print(f"Analyzing {repo_path}...")
    results = pipeline.run(repo_path)

    # Access individual components
    print(f"\nResults:")
    print(f"  Integrity Score: {results['integrity_score']:.3f}")
    print(f"  Confidence Score: {results['confidence_score']:.3f}")

    # Access detector outputs
    for detector_id, output in results.get("detector_outputs", {}).items():
        print(f"  {detector_id}: {output}")

    # Generate reports
    report_md = generate_markdown_report(
        repo_name=str(Path(repo_path).name),
        integrity_score=results["integrity_score"],
        confidence_score=results["confidence_score"],
        detector_outputs=results.get("detector_outputs", {}),
        metric_names=list(results.get("metric_results", {}).keys()),
        window_count=len(results.get("windows", [])),
        total_commits=results.get("total_commits", 0),
        contributor_count=results.get("contributor_count", 0),
    )
    print(f"\nMarkdown report: {len(report_md)} characters")

    report_html = generate_html_report(
        repo_name=str(Path(repo_path).name),
        integrity_score=results["integrity_score"],
        confidence_score=results["confidence_score"],
        detector_outputs=results.get("detector_outputs", {}),
        metric_names=list(results.get("metric_results", {}).keys()),
        window_count=len(results.get("windows", [])),
    )
    print(f"HTML report: {len(report_html)} characters")


if __name__ == "__main__":
    main()
