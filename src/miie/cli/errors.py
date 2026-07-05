"""Human-readable error handling for MIIE CLI.

Replaces stack traces with explanations, root causes,
suggested remediation, and documentation links.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.traceback import Traceback

from .display import console, error_panel, warning_panel

# ── Error Catalog ──────────────────────────────────────────────────────
ERROR_CATALOG: dict[str, dict[str, str]] = {
    "repository_not_found": {
        "title": "Repository Not Found",
        "explanation": "The specified repository path or URL could not be found.",
        "remediation": "Check the path/URL and ensure the repository exists.",
        "docs": "https://github.com/user/miee/docs/troubleshooting.md#repository-not-found",
    },
    "git_clone_failed": {
        "title": "Git Clone Failed",
        "explanation": "Could not clone the repository from the remote URL.",
        "remediation": "Verify the URL is correct, the repository is public, and you have network access.",
        "docs": "https://github.com/user/miee/docs/troubleshooting.md#clone-failures",
    },
    "authentication_failed": {
        "title": "Authentication Failed",
        "explanation": "GitHub authentication failed. The token may be invalid or expired.",
        "remediation": "Generate a new personal access token at https://github.com/settings/tokens",
        "docs": "https://github.com/user/miee/docs/troubleshooting.md#authentication",
    },
    "insufficient_windows": {
        "title": "Insufficient Analysis Windows",
        "explanation": "Not enough data windows could be constructed for reliable detection.",
        "remediation": "Try a larger --window-size, a longer time range, or a repository with more commits.",
        "docs": "https://github.com/user/miee/docs/troubleshooting.md#window-requirements",
    },
    "metric_extraction_failed": {
        "title": "Metric Extraction Failed",
        "explanation": "Could not extract one or more metrics from the repository.",
        "remediation": "Check that the repository is a valid git repository with sufficient commit history.",
        "docs": "https://github.com/user/miee/docs/troubleshooting.md#metric-extraction",
    },
    "detector_error": {
        "title": "Detector Execution Error",
        "explanation": "A statistical detector encountered an error during execution.",
        "remediation": "This may indicate insufficient data. Try with more windows or different parameters.",
        "docs": "https://github.com/user/miee/docs/troubleshooting.md#detector-errors",
    },
    "config_invalid": {
        "title": "Invalid Configuration",
        "explanation": "The configuration file contains invalid values.",
        "remediation": "Run 'miie validate <config>' to check your configuration file.",
        "docs": "https://github.com/user/miee/docs/configuration.md",
    },
    "output_error": {
        "title": "Output Error",
        "explanation": "Could not write the output report.",
        "remediation": "Check that the output directory exists and you have write permissions.",
        "docs": "https://github.com/user/miee/docs/troubleshooting.md#output-errors",
    },
}


# ── Error Display ──────────────────────────────────────────────────────
def display_error(
    error: Exception,
    context: str | None = None,
    verbose: bool = False,
    debug: bool = False,
) -> None:
    """Display a human-readable error message."""
    error_type = type(error).__name__
    error_msg = str(error)

    # Try to match error to catalog
    catalog_entry = _match_error_to_catalog(error_type, error_msg)

    if catalog_entry:
        _display_catalog_error(catalog_entry, error_msg, context, verbose, debug, error)
    else:
        _display_generic_error(error_type, error_msg, context, verbose, debug, error)


def _match_error_to_catalog(error_type: str, error_msg: str) -> dict[str, str] | None:
    """Try to match an error to the catalog."""
    msg_lower = error_msg.lower()

    if "not found" in msg_lower or "no such file" in msg_lower:
        return ERROR_CATALOG["repository_not_found"]
    if "clone" in msg_lower or "could not access" in msg_lower:
        return ERROR_CATALOG["git_clone_failed"]
    if "401" in msg_lower or "403" in msg_lower or "authentication" in msg_lower:
        return ERROR_CATALOG["authentication_failed"]
    if "insufficient" in msg_lower and "window" in msg_lower:
        return ERROR_CATALOG["insufficient_windows"]
    if "extraction" in msg_lower or "metric" in msg_lower:
        return ERROR_CATALOG["metric_extraction_failed"]
    if "detector" in msg_lower:
        return ERROR_CATALOG["detector_error"]
    if "config" in msg_lower or "validation" in msg_lower:
        return ERROR_CATALOG["config_invalid"]
    if "write" in msg_lower or "permission" in msg_lower or "output" in msg_lower:
        return ERROR_CATALOG["output_error"]

    return None


def _display_catalog_error(
    entry: dict[str, str],
    error_msg: str,
    context: str | None,
    verbose: bool,
    debug: bool,
    original_error: Exception,
) -> None:
    """Display a catalog-matched error."""
    content = f"[bold]{entry['title']}[/bold]\n\n"
    content += f"[yellow]What happened:[/yellow] {entry['explanation']}\n\n"
    content += f"[cyan]How to fix:[/cyan] {entry['remediation']}\n\n"
    if error_msg:
        content += f"[dim]Error detail: {error_msg[:200]}[/dim]\n"
    if context:
        content += f"[dim]Context: {context}[/dim]\n"
    if entry.get("docs"):
        content += f"\n[dim]Documentation: {entry['docs']}[/dim]"

    console.print()
    error_panel("Error", content)

    if debug:
        console.print()
        console.print("[dim]Full stack trace:[/dim]")
        console.print(Traceback.from_exception(type(original_error), original_error, original_error.__traceback__))


def _display_generic_error(
    error_type: str,
    error_msg: str,
    context: str | None,
    verbose: bool,
    debug: bool,
    original_error: Exception,
) -> None:
    """Display a generic error."""
    content = f"[bold]{error_type}[/bold]\n\n"
    content += f"[yellow]Error:[/yellow] {error_msg[:300]}\n"
    if context:
        content += f"\n[cyan]Context:[/cyan] {context}\n"
    content += "\n[dim]Run with --debug for full stack trace.[/dim]"

    console.print()
    error_panel("System Error", content)

    if debug:
        console.print()
        console.print("[dim]Full stack trace:[/dim]")
        console.print(Traceback.from_exception(type(original_error), original_error, original_error.__traceback__))


# ── Warning Display ────────────────────────────────────────────────────
def display_warning(message: str, context: str | None = None) -> None:
    """Display a warning message."""
    content = f"[yellow]{message}[/yellow]"
    if context:
        content += f"\n[dim]{context}[/dim]"
    warning_panel("Warning", content)


# ── Partial Results ────────────────────────────────────────────────────
def save_partial_results(output_dir: str, error: Exception) -> Path | None:
    """Save partial results when pipeline fails mid-execution."""
    try:
        import json
        partial_path = Path(output_dir) / "partial_results.json"
        partial_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "error": str(error),
            "error_type": type(error).__name__,
            "partial": True,
        }
        partial_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return partial_path
    except Exception:
        return None


# ── Exception Handler ──────────────────────────────────────────────────
def handle_exception(
    error: Exception,
    output_dir: str = "./output",
    verbose: bool = False,
    debug: bool = False,
    exit_code: int = 2,
) -> None:
    """Handle an exception with user-friendly display."""
    # Save partial results
    partial = save_partial_results(output_dir, error)
    if partial:
        display_warning(f"Partial results saved to {partial}")

    # Display error
    display_error(error, verbose=verbose, debug=debug)

    sys.exit(exit_code)
