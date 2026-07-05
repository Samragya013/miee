#!/usr/bin/env python3
"""
PR-7C-4: Scientific Readiness Validation Campaign.

Runs the ScientificReadinessEngine on all analyzed repos, produces
per-repo execution reports and aggregate certification.

Outputs:
  validation/scientific/
    00_aggregate_summary.md
    01_per_repo_certification.md
    02_detector_readiness_matrix.md
    03_strategy_distribution.md
    04_calibration_analysis.md
    05_window_merge_analysis.md
    06_confidence_distribution.md
    07_readiness_by_detector.md
    08_prediction_error_analysis.md
    09_final_certification.md
    aggregate_certification.json
    per_repo_results.csv
    detector_matrix.csv
    strategy_distribution.csv
    calibration_results.csv
    confidence_distribution.csv
    prediction_errors.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from miie.scientific.engine import ScientificReadinessEngine
from miie.scientific.models import AggregateCertification, ScientificExecutionReport


# ---------------------------------------------------------------------------
# Repository list
# ---------------------------------------------------------------------------

REPOS = [
    ("A-02", "git/git"),
    ("A-03", "golang/go"),
    ("A-04", "rust-lang/rust"),
    ("A-05", "golang/go"),
    ("B-01", "kubernetes/kubernetes"),
    ("B-02", "ansible/ansible"),
    ("B-03", "docker/cli"),
    ("B-04", "hashicorp/terraform"),
    ("B-05", "grafana/grafana"),
    ("C-01", "django/django"),
    ("C-02", "facebookresearch/ParlAI"),
    ("C-03", "pallets/flask"),
    ("C-04", "pallets/jinja"),
    ("C-05", "encode/httpx"),
    ("D-01", "spring-projects/spring-boot"),
    ("D-02", "oracle/node"),
    ("D-03", "phpmyadmin/phpmyadmin"),
    ("D-04", "Homebrew/brew"),
    ("E-01", "vuejs/vue"),
    ("E-02", "angular/angular"),
    ("E-03", "sveltejs/svelte"),
    ("E-04", "emberjs/ember.js"),
    ("E-05", "preactjs/preact"),
    ("F-01", "microsoft/vscode"),
    ("F-02", "atom/atom"),
    ("F-03", "torvalds/linux"),
    ("F-04", "torvalds/linux"),
]


def main() -> None:
    """Run the validation campaign."""
    output_dir = ROOT_DIR / "validation" / "scientific"
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = ScientificReadinessEngine()

    # Load diagnostics from existing campaign results
    results: Dict[str, Any] = {}
    reports: List[ScientificExecutionReport] = []

    for repo_id, repo_name in REPOS:
        # Look for existing analysis report
        report_dir = ROOT_DIR / "validation" / "sampling" / f"cli_output_{repo_id}"
        if not report_dir.exists():
            print(f"  [SKIP] {repo_id}: no analysis report found")
            continue

        # Find the analysis report JSON
        json_files = list(report_dir.glob("analysis_report_*.json"))
        if not json_files:
            print(f"  [SKIP] {repo_id}: no analysis_report_*.json")
            continue

        json_path = json_files[0]
        diagnostics = engine.load_diagnostics_from_json(json_path)
        if diagnostics is None:
            print(f"  [SKIP] {repo_id}: could not load diagnostics")
            continue

        # Certify
        report = engine.certify_repository(repo_id, diagnostics)
        reports.append(report)
        results[repo_id] = {
            "repo_name": repo_name,
            "report": report,
            "diagnostics": diagnostics,
        }
        print(f"  [OK] {repo_id}: {report.certification.verdict} "
              f"(confidence={report.certification.overall_confidence:.2f})")

    # Batch certification
    repo_diag_map = {rid: r["diagnostics"] for rid, r in results.items()}
    aggregate = engine.certify_batch(repo_diag_map)

    # Generate outputs
    print(f"\nGenerating reports for {len(reports)} repos...")
    _write_aggregate_summary(aggregate, output_dir)
    _write_per_repo_certification(reports, output_dir)
    _write_detector_readiness_matrix(reports, output_dir)
    _write_strategy_distribution(reports, output_dir)
    _write_calibration_analysis(reports, output_dir)
    _write_window_merge_analysis(reports, output_dir)
    _write_confidence_distribution(reports, output_dir)
    _write_readiness_by_detector(reports, output_dir)
    _write_prediction_error_analysis(reports, output_dir)
    _write_final_certification(aggregate, output_dir)

    # Machine-readable outputs
    _write_aggregate_json(aggregate, output_dir)
    _write_per_repo_csv(reports, output_dir)
    _write_detector_matrix_csv(reports, output_dir)
    _write_strategy_csv(reports, output_dir)
    _write_calibration_csv(reports, output_dir)
    _write_confidence_csv(reports, output_dir)
    _write_prediction_csv(reports, output_dir)

    print(f"\nAll outputs written to {output_dir}")


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------


def _write_aggregate_summary(
    agg: AggregateCertification,
    output_dir: Path,
) -> None:
    """Write 00_aggregate_summary.md."""
    lines = [
        "# PR-7C Scientific Readiness — Aggregate Summary",
        "",
        f"**Total Repos Analyzed:** {agg.total_repos}",
        f"**READY:** {agg.ready_count}",
        f"**PARTIAL:** {agg.partial_count}",
        f"**SKIPPED:** {agg.skipped_count}",
        f"**FAILED:** {agg.failed_count}",
        f"**Overall Verdict:** {agg.overall_verdict}",
        f"**Overall Confidence:** {agg.overall_confidence:.4f}",
        "",
    ]
    if agg.warnings:
        lines.append("## Warnings")
        for w in agg.warnings:
            lines.append(f"- {w}")
        lines.append("")

    (output_dir / "00_aggregate_summary.md").write_text("\n".join(lines))


def _write_per_repo_certification(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 01_per_repo_certification.md."""
    lines = ["# Per-Repository Certification", ""]
    for r in reports:
        c = r.certification
        lines.append(f"## {r.repo_id}: {r.repo_name}")
        lines.append(f"- **Verdict:** {c.verdict}")
        lines.append(f"- **Confidence:** {c.overall_confidence:.4f}")
        lines.append(f"- **Strategy:** {c.strategy_used}")
        lines.append(f"- **Windows:** {c.window_count}")
        lines.append(f"- **Observations:** {c.observation_count}")
        lines.append(f"- **Prediction Error:** {c.prediction_error:.2%}")
        if c.warnings:
            for w in c.warnings:
                lines.append(f"- **Warning:** {w}")
        lines.append("")
    (output_dir / "01_per_repo_certification.md").write_text("\n".join(lines))


def _write_detector_readiness_matrix(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 02_detector_readiness_matrix.md."""
    lines = ["# Detector Readiness Matrix", ""]
    header = "| Repo | D-01 | D-02 | D-03 |"
    sep = "|------|------|------|------|"
    lines.extend([header, sep])
    for r in reports:
        row = f"| {r.repo_id} |"
        for det_id in ("D-01", "D-02", "D-03"):
            state = r.detector_summary.get(det_id, "N/A")
            row += f" {state} |"
        lines.append(row)
    lines.append("")
    (output_dir / "02_detector_readiness_matrix.md").write_text("\n".join(lines))


def _write_strategy_distribution(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 03_strategy_distribution.md."""
    strategy_counts: Dict[str, int] = {}
    for r in reports:
        s = r.certification.strategy_used
        strategy_counts[s] = strategy_counts.get(s, 0) + 1

    lines = ["# Strategy Distribution", ""]
    for strat, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{strat}:** {count} repos")
    lines.append("")
    (output_dir / "03_strategy_distribution.md").write_text("\n".join(lines))


def _write_calibration_analysis(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 04_calibration_analysis.md."""
    lines = ["# Calibration Analysis", ""]
    lines.append("| Repo | Prediction Error | Window Diff | Conf Adj |")
    lines.append("|------|-----------------|-------------|----------|")
    for r in reports:
        c = r.certification
        pe = c.prediction_error
        lines.append(f"| {r.repo_id} | {pe:.2%} | {c.window_count} | 0.0 |")
    lines.append("")
    (output_dir / "04_calibration_analysis.md").write_text("\n".join(lines))


def _write_window_merge_analysis(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 05_window_merge_analysis.md."""
    lines = ["# Window Merge Analysis", ""]
    lines.append("Terminal window merges occur when the last window has < 10 observations.")
    lines.append("")
    for r in reports:
        merge_warnings = [w for w in r.certification.warnings if "merge" in w.lower()]
        if merge_warnings:
            lines.append(f"## {r.repo_id}")
            for w in merge_warnings:
                lines.append(f"- {w}")
            lines.append("")
    (output_dir / "05_window_merge_analysis.md").write_text("\n".join(lines))


def _write_confidence_distribution(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 06_confidence_distribution.md."""
    lines = ["# Confidence Distribution", ""]
    conf_bins: Dict[str, int] = {"high (>=0.8)": 0, "medium (0.5-0.8)": 0, "low (<0.5)": 0}
    for r in reports:
        c = r.certification.overall_confidence
        if c >= 0.8:
            conf_bins["high (>=0.8)"] += 1
        elif c >= 0.5:
            conf_bins["medium (0.5-0.8)"] += 1
        else:
            conf_bins["low (<0.5)"] += 1
    for label, count in conf_bins.items():
        lines.append(f"- **{label}:** {count} repos")
    lines.append("")
    (output_dir / "06_confidence_distribution.md").write_text("\n".join(lines))


def _write_readiness_by_detector(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 07_readiness_by_detector.md."""
    lines = ["# Readiness by Detector", ""]
    det_counts: Dict[str, Dict[str, int]] = {}
    for det_id in ("D-01", "D-02", "D-03"):
        det_counts[det_id] = {"READY": 0, "PARTIAL": 0, "SKIPPED": 0}
    for r in reports:
        for det_id in ("D-01", "D-02", "D-03"):
            state = r.detector_summary.get(det_id, "SKIPPED")
            if state in det_counts[det_id]:
                det_counts[det_id][state] += 1

    for det_id in ("D-01", "D-02", "D-03"):
        lines.append(f"## {det_id}")
        for state, count in det_counts[det_id].items():
            lines.append(f"- {state}: {count}")
        lines.append("")
    (output_dir / "07_readiness_by_detector.md").write_text("\n".join(lines))


def _write_prediction_error_analysis(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write 08_prediction_error_analysis.md."""
    lines = ["# Prediction Error Analysis", ""]
    errors = [r.certification.prediction_error for r in reports]
    if errors:
        avg_err = sum(errors) / len(errors)
        max_err = max(errors)
        min_err = min(errors)
        lines.append(f"- **Mean prediction error:** {avg_err:.2%}")
        lines.append(f"- **Max prediction error:** {max_err:.2%}")
        lines.append(f"- **Min prediction error:** {min_err:.2%}")
    lines.append("")
    (output_dir / "08_prediction_error_analysis.md").write_text("\n".join(lines))


def _write_final_certification(
    agg: AggregateCertification,
    output_dir: Path,
) -> None:
    """Write 09_final_certification.md."""
    lines = [
        "# Scientific Readiness — Final Certification",
        "",
        "## Verdict",
        "",
        f"**{agg.overall_verdict}**",
        "",
        "## Summary",
        "",
        f"- Repos analyzed: {agg.total_repos}",
        f"- READY: {agg.ready_count}",
        f"- PARTIAL: {agg.partial_count}",
        f"- SKIPPED: {agg.skipped_count}",
        f"- Overall confidence: {agg.overall_confidence:.4f}",
        "",
        "## Certification Statement",
        "",
        f"The MIIE v1.5 scientific readiness certification analyzed "
        f"{agg.total_repos} repositories. "
        f"{agg.ready_count} repositories achieved READY status, "
        f"{agg.partial_count} achieved PARTIAL status, and "
        f"{agg.skipped_count} were SKIPPED due to insufficient data. "
        f"The aggregate confidence level is {agg.overall_confidence:.2%}.",
        "",
    ]
    (output_dir / "09_final_certification.md").write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# Machine-readable writers
# ---------------------------------------------------------------------------


def _write_aggregate_json(
    agg: AggregateCertification,
    output_dir: Path,
) -> None:
    """Write aggregate_certification.json."""
    data = {
        "total_repos": agg.total_repos,
        "ready_count": agg.ready_count,
        "partial_count": agg.partial_count,
        "skipped_count": agg.skipped_count,
        "failed_count": agg.failed_count,
        "overall_verdict": agg.overall_verdict,
        "overall_confidence": agg.overall_confidence,
        "warnings": agg.warnings,
        "certifications": [
            {
                "repo_id": c.repo_id,
                "repo_name": c.repo_name,
                "verdict": c.verdict,
                "confidence": c.overall_confidence,
                "strategy": c.strategy_used,
                "windows": c.window_count,
                "observations": c.observation_count,
            }
            for c in agg.certifications
        ],
    }
    (output_dir / "aggregate_certification.json").write_text(
        json.dumps(data, indent=2)
    )


def _write_per_repo_csv(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write per_repo_results.csv."""
    with open(output_dir / "per_repo_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "repo_id", "repo_name", "verdict", "confidence",
            "strategy", "windows", "observations", "prediction_error",
        ])
        for r in reports:
            c = r.certification
            writer.writerow([
                r.repo_id, r.repo_name, c.verdict, c.overall_confidence,
                c.strategy_used, c.window_count, c.observation_count,
                c.prediction_error,
            ])


def _write_detector_matrix_csv(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write detector_matrix.csv."""
    with open(output_dir / "detector_matrix.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "D-01", "D-02", "D-03"])
        for r in reports:
            writer.writerow([
                r.repo_id,
                r.detector_summary.get("D-01", "N/A"),
                r.detector_summary.get("D-02", "N/A"),
                r.detector_summary.get("D-03", "N/A"),
            ])


def _write_strategy_csv(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write strategy_distribution.csv."""
    strategy_counts: Dict[str, int] = {}
    for r in reports:
        s = r.certification.strategy_used
        strategy_counts[s] = strategy_counts.get(s, 0) + 1

    with open(output_dir / "strategy_distribution.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["strategy", "count"])
        for strat, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
            writer.writerow([strat, count])


def _write_calibration_csv(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write calibration_results.csv."""
    with open(output_dir / "calibration_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "prediction_error", "window_count", "confidence_adjustment"])
        for r in reports:
            c = r.certification
            writer.writerow([r.repo_id, c.prediction_error, c.window_count, 0.0])


def _write_confidence_csv(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write confidence_distribution.csv."""
    conf_bins: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    for r in reports:
        c = r.certification.overall_confidence
        if c >= 0.8:
            conf_bins["high"] += 1
        elif c >= 0.5:
            conf_bins["medium"] += 1
        else:
            conf_bins["low"] += 1

    with open(output_dir / "confidence_distribution.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tier", "count"])
        for tier, count in conf_bins.items():
            writer.writerow([tier, count])


def _write_prediction_csv(
    reports: List[ScientificExecutionReport],
    output_dir: Path,
) -> None:
    """Write prediction_errors.csv."""
    with open(output_dir / "prediction_errors.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["repo_id", "prediction_error"])
        for r in reports:
            writer.writerow([r.repo_id, r.certification.prediction_error])


if __name__ == "__main__":
    main()
