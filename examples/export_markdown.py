#!/usr/bin/env python3
"""Export MIIE results as Markdown."""

import sys
from pathlib import Path

from miie.orchestration.pipeline import AnalysisPipeline
from miie.config.loader import load_config
from miie.cli.formatting import generate_markdown_report


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else "report.md"

    # Load configuration and run pipeline
    config = load_config()
    pipeline = AnalysisPipeline(config)
    results = pipeline.run(repo_path)

    # Generate Markdown report
    report = generate_markdown_report(
        repo_name=str(Path(repo_path).name),
        integrity_score=results["integrity_score"],
        confidence_score=results["confidence_score"],
        detector_outputs=results.get("detector_outputs", {}),
        metric_names=list(results.get("metric_results", {}).keys()),
        window_count=len(results.get("windows", [])),
        total_commits=results.get("total_commits", 0),
        contributor_count=results.get("contributor_count", 0),
    )

    # Write to file
    Path(output_file).write_text(report, encoding="utf-8")
    print(f"Report written to {output_file}")


if __name__ == "__main__":
    main()
