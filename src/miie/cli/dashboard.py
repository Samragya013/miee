"""Scientific dashboard for MIIE CLI.

Displays integrity score, confidence score, metric coverage,
detector status, observation counts, and repository health.
"""

from __future__ import annotations

from typing import Any, Optional

from rich.console import Console
from rich.table import Table

from .display import console, print_section, print_score, print_kv


# ── Dashboard ──────────────────────────────────────────────────────────
def display_dashboard(
    integrity_score: float,
    confidence_score: float,
    detector_outputs: dict[str, Any],
    metric_names: list[str],
    window_count: int,
    total_commits: Any,
    contributor_count: Any,
    timings: dict[str, float] | None = None,
    verbose: bool = False,
) -> None:
    """Display the full scientific dashboard."""
    print_section("Scientific Dashboard")

    # ── Scores ──
    console.print()
    print_score("Integrity Score", integrity_score)
    print_score("Confidence Score", confidence_score, thresholds=(0.9, 0.7, 0.5))
    console.print()

    # ── Metric Coverage ──
    table = Table(title="Metric Coverage", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="bold", width=6)
    table.add_column("Status", width=10)
    table.add_column("Provider", style="dim")

    for metric_id in metric_names:
        table.add_row(metric_id, "[green]● Available[/green]", "GitObservationProvider")

    console.print(table)

    # ── Detector Status ──
    det_table = Table(title="Detector Status", show_header=True, header_style="bold cyan")
    det_table.add_column("ID", style="bold", width=6)
    det_table.add_column("Name", width=25)
    det_table.add_column("Status", width=12)
    det_table.add_column("Result", width=12)

    _det_names = {
        "D-01": "Distribution Drift",
        "D-02": "Correlation Breakdown",
        "D-03": "Threshold Compression",
    }

    for det_id in sorted(detector_outputs.keys()):
        det_data = detector_outputs[det_id]
        name = _det_names.get(det_id, det_id)

        if not isinstance(det_data, dict):
            status = "[yellow]ERROR[/yellow]"
            result = "[dim]N/A[/dim]"
        elif det_data.get("status") in ("error", "skipped"):
            status = "[yellow]ERROR[/yellow]"
            result = det_data.get("reason", "unknown")[:20]
        else:
            status = "[green]OK[/green]"
            triggered = (
                det_data.get("drift_detected")
                or det_data.get("breakdown_detected")
                or det_data.get("compression_detected", False)
            )
            result = "[red]DETECTED[/red]" if triggered else "[green]CLEAR[/green]"

        det_table.add_row(det_id, name, status, result)

    console.print(det_table)

    # ── Repository Info ──
    console.print()
    print_kv("Commits", total_commits)
    print_kv("Contributors", contributor_count)
    print_kv("Windows", window_count)

    # ── Performance ──
    if timings:
        console.print()
        console.print("  [bold]Performance:[/bold]")
        for stage, elapsed in timings.items():
            console.print(f"    {stage}: {elapsed:.2f}s")
        console.print(f"    [bold]Total: {sum(timings.values()):.2f}s[/bold]")

    console.print()


# ── Compact Dashboard ──────────────────────────────────────────────────
def display_compact_dashboard(
    integrity_score: float,
    confidence_score: float,
    detector_outputs: dict[str, Any],
    window_count: int,
) -> None:
    """Display a compact single-line dashboard."""
    # Determine overall status
    any_triggered = False
    any_failed = False
    for det_data in detector_outputs.values():
        if isinstance(det_data, dict):
            if det_data.get("status") in ("error", "skipped"):
                any_failed = True
            elif (
                det_data.get("drift_detected")
                or det_data.get("breakdown_detected")
                or det_data.get("compression_detected", False)
            ):
                any_triggered = True

    if any_triggered:
        status_color = "red"
        status_text = "ANOMALIES DETECTED"
    elif any_failed:
        status_color = "yellow"
        status_text = "PARTIAL"
    else:
        status_color = "green"
        status_text = "ALL CLEAR"

    console.print(
        f"  [{status_color}]{status_text}[/{status_color}] │ "
        f"IS: [bold]{integrity_score:.3f}[/bold] │ "
        f"CS: [bold]{confidence_score:.3f}[/bold] │ "
        f"Windows: {window_count}"
    )


# ── Verdict Display ────────────────────────────────────────────────────
def display_verdict(
    integrity_score: float,
    confidence_score: float,
    triggered_count: int,
    failed_detectors: list[str],
) -> None:
    """Display the overall verdict."""
    print_section("Overall Verdict")

    # Labels
    integrity_label = _score_label(integrity_score)
    confidence_label = _score_label(confidence_score)

    if triggered_count == 0:
        risk = "Very Low"
    elif triggered_count == 1:
        risk = "Low"
    elif triggered_count == 2:
        risk = "Moderate"
    else:
        risk = "High"

    table = Table(show_header=False, border_style="cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Metric Integrity", f"[bold]{integrity_label}[/bold] ({integrity_score:.3f})")
    table.add_row("Confidence", f"[bold]{confidence_label}[/bold] ({confidence_score:.3f})")
    table.add_row("Risk Level", f"[bold]{risk}[/bold]")
    if failed_detectors:
        table.add_row("Failed Detectors", ", ".join(failed_detectors))

    console.print(table)

    # Summary sentence
    console.print()
    if triggered_count == 0 and integrity_score >= 0.9:
        console.print(
            "  [green]No evidence was found that repository metrics have become "
            "distorted, unstable, or misleading.[/green]"
        )
    elif triggered_count == 0:
        console.print(
            "  [yellow]Repository metrics appear generally stable with minor variations "
            "that are within expected ranges.[/yellow]"
        )
    elif triggered_count == 1:
        console.print(
            "  [yellow]One metric anomaly was detected, but overall measurement "
            "integrity remains acceptable.[/yellow]"
        )
    else:
        console.print(
            "  [red]Multiple metric anomalies were detected. Manual investigation "
            "of repository measurement integrity is recommended.[/red]"
        )

    # Recommended action
    console.print()
    print_section("Recommended Action")
    if triggered_count == 0 and integrity_score >= 0.9:
        console.print("  No action required. Repository metrics appear trustworthy.")
    elif triggered_count == 0:
        console.print("  No immediate action. Consider analyzing a longer time range for higher confidence.")
    elif triggered_count == 1:
        console.print("  Review the flagged metric for context. Monitor for continued anomalies.")
    else:
        console.print("  Investigate flagged metrics. Review contributor activity and development patterns.")


def _score_label(value: float) -> str:
    """Convert a score to a human-readable label."""
    if value >= 0.9:
        return "Very High"
    elif value >= 0.7:
        return "High"
    elif value >= 0.5:
        return "Moderate"
    else:
        return "Low"
