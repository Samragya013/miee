"""Rich display components for MIIE CLI.

Provides panels, tables, progress bars, spinners, and formatted output
for the MIIE scientific analysis pipeline.
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ── Theme ──────────────────────────────────────────────────────────────
MIIE_THEME = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "metric": "bold blue",
        "score": "bold magenta",
        "dim": "dim white",
        "header": "bold white on dark_blue",
        "stage": "bold cyan",
        "pass": "bold green",
        "fail": "bold red",
        "skip": "bold yellow",
    }
)

# Configure console with Windows encoding support
import os
_force_terminal = os.environ.get("MIIE_FORCE_TERMINAL", "0") == "1" or not os.environ.get("PYTHONDONTWRITEBYTECODE")
console = Console(
    theme=MIIE_THEME,
    force_terminal=_force_terminal,
    width=min(120, os.get_terminal_size().columns if os.isatty(1) else 120),
)


# ── Banner ─────────────────────────────────────────────────────────────
def print_banner(version: str, subtitle: str = "Measurement Integrity Analysis") -> None:
    """Print the MIIE header banner."""
    banner = Text()
    banner.append(f"  MIIE v{version}\n", style="bold white")
    banner.append(f"  {subtitle}", style="dim")
    console.print(
        Panel(banner, border_style="blue", padding=(0, 2), expand=False)
    )


def print_footer(message: str = "Analysis Complete") -> None:
    """Print the MIIE footer."""
    console.print(
        Panel(
            Text(f"  {message}", style="bold green"),
            border_style="blue",
            padding=(0, 2),
            expand=False,
        )
    )


# ── Sections ───────────────────────────────────────────────────────────
def print_section(title: str) -> None:
    """Print a section header."""
    console.print()
    console.print(f"  [bold]{title}[/bold]")
    console.print(f"  {'-' * 40}")


def print_kv(key: str, value: Any, indent: int = 2) -> None:
    """Print a key-value pair."""
    console.print(f"{' ' * indent}{key}: [bold]{value}[/bold]")


# ── Tables ─────────────────────────────────────────────────────────────
def make_table(title: str | None = None, **kwargs) -> Table:
    """Create a styled Rich table."""
    return Table(title=title, show_header=True, header_style="bold cyan", **kwargs)


def add_metric_row(
    table: Table,
    metric_id: str,
    name: str,
    value: Any,
    status: str = "ok",
) -> None:
    """Add a metric row to a table."""
    status_style = {
        "ok": "[green]●[/green]",
        "warn": "[yellow]●[/yellow]",
        "error": "[red]●[/red]",
        "skip": "[dim]○[/dim]",
    }.get(status, "[dim]?[/dim]")
    table.add_row(status_style, metric_id, name, str(value))


def add_detector_row(
    table: Table,
    detector_id: str,
    name: str,
    triggered: bool | None,
    detail: str = "",
) -> None:
    """Add a detector row to a table."""
    if triggered is None:
        status = "[yellow]SKIP[/yellow]"
    elif triggered:
        status = "[red]DETECTED[/red]"
    else:
        status = "[green]CLEAR[/green]"
    table.add_row(detector_id, name, status, detail)


# ── Panels ─────────────────────────────────────────────────────────────
def info_panel(title: str, content: str, style: str = "cyan") -> None:
    """Display an informational panel."""
    console.print(Panel(content, title=f"[bold]{title}[/bold]", border_style=style))


def success_panel(title: str, content: str) -> None:
    """Display a success panel."""
    console.print(Panel(content, title=f"[bold green]{title}[/bold green]", border_style="green"))


def error_panel(title: str, content: str) -> None:
    """Display an error panel."""
    console.print(Panel(content, title=f"[bold red]{title}[/bold red]", border_style="red"))


def warning_panel(title: str, content: str) -> None:
    """Display a warning panel."""
    console.print(Panel(content, title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow"))


# ── Score Display ──────────────────────────────────────────────────────
def print_score(
    label: str,
    value: float,
    width: int = 30,
    thresholds: tuple[float, float, float] = (0.9, 0.7, 0.5),
) -> None:
    """Print a score with visual bar."""
    high, mid, low = thresholds
    if value >= high:
        color = "green"
        rating = "Very High"
    elif value >= mid:
        color = "cyan"
        rating = "High"
    elif value >= low:
        color = "yellow"
        rating = "Moderate"
    else:
        color = "red"
        rating = "Low"

    filled = int(value * width)
    bar = "#" * filled + "-" * (width - filled)
    console.print(
        f"  {label:<20s} [{color}]{bar}[/{color}] "
        f"[bold {color}]{value:.3f}[/bold {color}] ({rating})"
    )


# ── Pipeline Stage Display ─────────────────────────────────────────────
def print_pipeline_stage(
    stage_num: int,
    total: int,
    name: str,
    status: str = "running",
    detail: str = "",
    elapsed: float | None = None,
) -> None:
    """Print a pipeline stage with status icon."""
    icons = {
        "running": "[cyan]*[/cyan]",
        "done": "[green]OK[/green]",
        "error": "[red]ERR[/red]",
        "skip": "[yellow]-[/yellow]",
    }
    icon = icons.get(status, "[dim]?[/dim]")
    elapsed_str = f" ({elapsed:.1f}s)" if elapsed is not None else ""
    detail_str = f" -- {detail}" if detail else ""
    console.print(
        f"  {icon} [{stage_num}/{total}] [bold]{name}[/bold]{elapsed_str}{detail_str}"
    )


# ── Detection Summary ──────────────────────────────────────────────────
def print_detection_summary(
    detector_outputs: dict[str, Any],
    verbose: bool = False,
) -> None:
    """Print detector results with status icons."""
    _detector_names = {
        "D-01": "Distribution Drift",
        "D-02": "Correlation Breakdown",
        "D-03": "Threshold Compression",
    }
    for det_id in sorted(detector_outputs.keys()):
        det_data = detector_outputs[det_id]
        name = _detector_names.get(det_id, det_id)

        if not isinstance(det_data, dict):
            triggered = False
            failed = True
        elif det_data.get("status") in ("error", "skipped"):
            triggered = False
            failed = True
        else:
            failed = False
            triggered = (
                det_data.get("drift_detected")
                or det_data.get("breakdown_detected")
                or det_data.get("compression_detected", False)
            )

        if failed:
            reason = det_data.get("reason", "unknown") if isinstance(det_data, dict) else "unknown"
            console.print(f"  [yellow]![/yellow] [{det_id}] {name}: [red]{reason[:60]}[/red]")
        elif triggered:
            console.print(f"  [red]X[/red] [{det_id}] {name}: [red]DETECTED[/red]")
        else:
            console.print(f"  [green]OK[/green] [{det_id}] {name}: [green]CLEAR[/green]")


# ── Timestamp ──────────────────────────────────────────────────────────
def timestamp() -> str:
    """Return a formatted timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
