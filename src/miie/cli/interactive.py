"""Interactive prompts for MIIE CLI.

Provides repository selection, GitHub URL input, local path browsing,
recent repositories, and configuration wizards.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from rich.prompt import Confirm, Prompt
from rich.table import Table

from .display import console, info_panel

# ── Configuration File ─────────────────────────────────────────────────
CONFIG_DIR = Path.home() / ".miie"
CONFIG_FILE = CONFIG_DIR / "config.json"
RECENT_FILE = CONFIG_DIR / "recent.json"


def ensure_config_dir() -> None:
    """Ensure the MIIE config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load MIIE configuration."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: dict) -> None:
    """Save MIIE configuration."""
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2, default=str), encoding="utf-8")


def load_recent() -> list[dict]:
    """Load recent repository list."""
    if RECENT_FILE.exists():
        try:
            data = json.loads(RECENT_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_recent(recent: list[dict]) -> None:
    """Save recent repository list."""
    ensure_config_dir()
    RECENT_FILE.write_text(json.dumps(recent, indent=2, default=str), encoding="utf-8")


def add_to_recent(repo_path: str, metadata: dict | None = None) -> None:
    """Add a repository to the recent list."""
    recent = load_recent()
    # Remove duplicate
    recent = [r for r in recent if r.get("path") != repo_path]
    entry = {"path": repo_path, "timestamp": str(__import__("datetime").datetime.now())}
    if metadata:
        entry.update(metadata)
    recent.insert(0, entry)
    # Keep last 20
    recent = recent[:20]
    save_recent(recent)


# ── Interactive Repository Input ───────────────────────────────────────
def prompt_repository_source() -> str:
    """Interactive prompt to choose repository source."""
    console.print()
    console.print("  [bold cyan]>>[/bold cyan] [bold white]Repository Source[/bold white]")
    console.print("  [dim]{'-' * 50}[/dim]")
    console.print("  [dim]1.[/dim] GitHub URL")
    console.print("  [dim]2.[/dim] Local path")
    console.print("  [dim]3.[/dim] Recent repository")

    choice = Prompt.ask(
        "\n  [bold cyan]Select source[/bold cyan]",
        choices=["1", "2", "3"],
        default="1",
    )

    if choice == "1":
        return prompt_github_url()
    elif choice == "2":
        return prompt_local_path()
    else:
        return prompt_recent_repo()


def prompt_github_url() -> str:
    """Prompt for a GitHub URL."""
    while True:
        url = Prompt.ask(
            "\n  [bold cyan]GitHub URL[/bold cyan]",
            default="https://github.com/",
        )
        if "github.com" in url or url.startswith("git@"):
            return url
        console.print("  [red]Invalid GitHub URL. Please try again.[/red]")


def prompt_local_path() -> str:
    """Prompt for a local repository path."""
    while True:
        path_str = Prompt.ask(
            "\n  [bold cyan]Local repository path[/bold cyan]",
            default=".",
        )
        path = Path(path_str).resolve()
        if (path / ".git").exists():
            return str(path)
        console.print(f"  [red]Not a git repository: {path}[/red]\n" "  [dim](No .git directory found)[/dim]")
        if not Confirm.ask("  [cyan]Try another path?[/cyan]", default=True):
            return str(path)


def prompt_recent_repo() -> str:
    """Prompt to select from recent repositories."""
    recent = load_recent()
    if not recent:
        console.print("  [yellow]No recent repositories found.[/yellow]")
        return prompt_local_path()

    table = Table(show_header=True, header_style="bold cyan", padding=(0, 2))
    table.add_column("#", style="dim", width=4)
    table.add_column("Repository", style="bold")
    table.add_column("Last Used", style="dim")

    for i, entry in enumerate(recent[:10], 1):
        table.add_row(
            str(i),
            entry.get("path", "?"),
            entry.get("timestamp", "?")[:19],
        )

    console.print()
    console.print(table)

    while True:
        choice = Prompt.ask(
            "\n  [bold cyan]Select repository (number)[/bold cyan]",
            default="1",
        )
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(recent):
                return recent[idx].get("path", "")
        except ValueError:
            pass
        console.print("  [red]Invalid selection. Please enter a number.[/red]")


# ── Interactive Configuration Wizard ───────────────────────────────────
def run_config_wizard() -> dict:
    """Interactive configuration setup wizard."""
    config = load_config()

    console.print()
    info_panel("Configuration Setup", "Configure MIIE settings interactively")

    # GitHub Token
    console.print("\n  [bold cyan]>>[/bold cyan] [bold white]GitHub Authentication[/bold white]")
    console.print("  [dim]" + "-" * 50 + "[/dim]")
    current_token = config.get("github_token", os.environ.get("GITHUB_TOKEN", ""))
    if current_token:
        masked = current_token[:4] + "..." + current_token[-4:] if len(current_token) > 8 else "****"
        console.print(f"  Current token: {masked}")
        if not Confirm.ask("  [cyan]Keep current token?[/cyan]", default=True):
            config["github_token"] = Prompt.ask("  [bold cyan]GitHub token[/bold cyan]", password=True)
    else:
        console.print("  [dim]No GitHub token configured.[/dim]")
        console.print("  [dim]A token is required for private repositories.[/dim]")
        if Confirm.ask("  [cyan]Configure GitHub token?[/cyan]", default=False):
            config["github_token"] = Prompt.ask("  [bold cyan]GitHub token[/bold cyan]", password=True)

    # Default directories
    console.print("\n  [bold cyan]>>[/bold cyan] [bold white]Directories[/bold white]")
    console.print("  [dim]" + "-" * 50 + "[/dim]")
    config["output_dir"] = Prompt.ask(
        "  [bold cyan]Default output directory[/bold cyan]",
        default=config.get("output_dir", "./output"),
    )

    # Parallelism
    console.print("\n  [bold cyan]>>[/bold cyan] [bold white]Performance[/bold white]")
    console.print("  [dim]" + "-" * 50 + "[/dim]")
    config["parallelism"] = int(
        Prompt.ask(
            "  [bold cyan]Parallel analysis threads[/bold cyan]",
            default=str(config.get("parallelism", 1)),
        )
    )

    # Theme
    console.print("\n  [bold cyan]>>[/bold cyan] [bold white]Appearance[/bold white]")
    console.print("  [dim]" + "-" * 50 + "[/dim]")
    config["theme"] = Prompt.ask(
        "  [bold cyan]Color theme[/bold cyan]",
        choices=["auto", "dark", "light"],
        default=config.get("theme", "auto"),
    )

    # Save
    save_config(config)
    console.print("\n  [green]Configuration saved to ~/.miie/config.json[/green]")
    return config


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value with fallback to env var."""
    config = load_config()
    value = config.get(key)
    if value is None:
        env_key = f"MIIE_{key.upper()}"
        value = os.environ.get(env_key, default)
    return value


# ── Interactive Analysis Confirmation ──────────────────────────────────
def confirm_analysis(params: dict) -> bool:
    """Show analysis plan and confirm before execution."""
    from rich.table import Table

    table = Table(title="Analysis Plan", show_header=False, border_style="cyan", padding=(0, 2))
    table.add_column("Parameter", style="bold cyan", width=18)
    table.add_column("Value")

    table.add_row("Repository", params.get("repo_path", "?"))
    table.add_row("Metrics", ", ".join(params.get("metrics", [])))
    table.add_row("Detectors", ", ".join(params.get("detectors", [])))
    table.add_row("Window Strategy", params.get("window_strategy", "time"))
    table.add_row("Window Size", str(params.get("window_size", 7)))
    if params.get("since"):
        table.add_row("Since", params["since"])
    if params.get("until"):
        table.add_row("Until", params["until"])
    table.add_row("Output Dir", params.get("output_dir", "./output"))
    table.add_row("Formats", ", ".join(params.get("formats", ["json"])))

    console.print()
    console.print(table)
    console.print()

    return Confirm.ask("  [bold cyan]Execute analysis?[/bold cyan]", default=True)
