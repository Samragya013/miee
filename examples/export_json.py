#!/usr/bin/env python3
"""Export MIIE results as JSON."""

import json
import sys
from pathlib import Path

from miie.orchestration.pipeline import AnalysisPipeline
from miie.config.loader import load_config


def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else "report.json"

    # Load configuration and run pipeline
    config = load_config()
    pipeline = AnalysisPipeline(config)
    results = pipeline.run(repo_path)

    # Write JSON report
    Path(output_file).write_text(
        json.dumps(results, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"JSON report written to {output_file}")


if __name__ == "__main__":
    main()
