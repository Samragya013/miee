"""Pipeline visualization for MIIE CLI.

Provides live progress display through the MIIE analysis pipeline stages.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from .display import console, print_pipeline_stage

# ── Pipeline Stages ────────────────────────────────────────────────────
PIPELINE_STAGES = [
    ("acquisition", "Repository Acquisition"),
    ("validation", "Repository Validation"),
    ("extraction", "Metric Extraction"),
    ("segmentation", "Window Generation"),
    ("detection", "Detector Execution"),
    ("evidence", "Evidence Generation"),
    ("reporting", "Final Assessment"),
]


class PipelineProgress:
    """Manages live pipeline progress display."""

    def __init__(self, total_stages: int = 7, verbose: bool = False) -> None:
        self.total_stages = total_stages
        self.verbose = verbose
        self._timings: dict[str, float] = {}
        self._stage_start: float = 0.0
        self._current_stage: int = 0
        self._progress: Progress | None = None

    def start(self) -> None:
        """Initialize the progress display."""
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        )
        self._progress.start()

    def stop(self) -> None:
        """Stop the progress display."""
        if self._progress:
            self._progress.stop()
            self._progress = None

    def stage_start(self, stage_key: str, detail: str = "") -> None:
        """Mark the start of a pipeline stage."""
        self._current_stage += 1
        self._stage_start = time.perf_counter()
        name = dict(PIPELINE_STAGES).get(stage_key, stage_key)
        print_pipeline_stage(self._current_stage, self.total_stages, name, "running", detail)

    def stage_complete(self, stage_key: str, detail: str = "") -> None:
        """Mark the completion of a pipeline stage."""
        elapsed = time.perf_counter() - self._stage_start
        self._timings[stage_key] = elapsed
        name = dict(PIPELINE_STAGES).get(stage_key, stage_key)
        print_pipeline_stage(self._current_stage, self.total_stages, name, "done", detail, elapsed)

    def stage_error(self, stage_key: str, error: str) -> None:
        """Mark a pipeline stage as failed."""
        elapsed = time.perf_counter() - self._stage_start
        self._timings[stage_key] = elapsed
        name = dict(PIPELINE_STAGES).get(stage_key, stage_key)
        print_pipeline_stage(self._current_stage, self.total_stages, name, "error", error, elapsed)

    def action(self, message: str) -> None:
        """Print an action message within the current stage."""
        console.print(f"        [dim]{message}[/dim]")

    @property
    def timings(self) -> dict[str, float]:
        """Return collected stage timings."""
        return self._timings.copy()

    @property
    def total_time(self) -> float:
        """Return total elapsed time."""
        return sum(self._timings.values())


# ── Progress Context Manager ───────────────────────────────────────────
@contextmanager
def pipeline_progress(verbose: bool = False) -> Generator[PipelineProgress, None, None]:
    """Context manager for pipeline progress display."""
    progress = PipelineProgress(verbose=verbose)
    progress.start()
    try:
        yield progress
    finally:
        progress.stop()


# ── Dry Run Display ────────────────────────────────────────────────────
def display_dry_run(params: dict) -> None:
    """Display a formatted dry-run plan with premium styling."""
    from rich.table import Table

    table = Table(title="Dry Run Plan", show_header=False, border_style="cyan", padding=(0, 2))
    table.add_column("Parameter", style="bold cyan", width=18)
    table.add_column("Value")

    for key, value in params.items():
        table.add_row(key, str(value))

    console.print()
    console.print(table)
    console.print()

    # Pipeline stages
    console.print("  [bold cyan]Pipeline Stages:[/bold cyan]")
    for i, (_, name) in enumerate(PIPELINE_STAGES, 1):
        console.print(f"    [dim]{i}.[/dim] [bold white]{name}[/bold white]")
    console.print()

    # Validation status
    console.print("  [green]V Validation: PASSED[/green]")
    console.print("  [dim]No work performed (dry run).[/dim]")


# ── Timing Summary ─────────────────────────────────────────────────────
def display_timing_summary(timings: dict[str, float]) -> None:
    """Display a timing summary table with premium styling."""
    table = Table(title="Stage Timing", show_header=True, header_style="bold cyan")
    table.add_column("Stage", style="bold", min_width=20)
    table.add_column("Time", justify="right", style="cyan")

    for key, elapsed in timings.items():
        name = dict(PIPELINE_STAGES).get(key, key)
        table.add_row(name, f"{elapsed:.2f}s")

    table.add_row("[bold white]Total[/bold white]", f"[bold cyan]{sum(timings.values()):.2f}s[/bold cyan]")

    console.print()
    console.print(table)
