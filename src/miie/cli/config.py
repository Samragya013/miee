"""Configuration management for MIIE CLI.

Handles persistent configuration, theme, defaults, and environment.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.table import Table

from .display import console, print_section, print_kv

# ── Config Paths ───────────────────────────────────────────────────────
CONFIG_DIR = Path.home() / ".miie"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "github_token": "",
    "output_dir": "./output",
    "parallelism": 1,
    "theme": "auto",
    "default_metrics": ["M-01", "M-02", "M-03", "M-04", "M-06", "M-07"],
    "default_detectors": ["D-01", "D-02", "D-03"],
    "default_window_strategy": "time",
    "default_window_size": 7,
    "auto_open_report": False,
    "verbose": False,
    "debug": False,
}


# ── Config Operations ──────────────────────────────────────────────────
def ensure_config_dir() -> None:
    """Ensure the MIIE config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load MIIE configuration from disk."""
    if CONFIG_FILE.exists():
        try:
            user_config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            # Merge with defaults
            config = {**DEFAULT_CONFIG, **user_config}
            return config
        except (json.JSONDecodeError, OSError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Save MIIE configuration to disk."""
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2, default=str), encoding="utf-8")


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value with env var fallback."""
    config = load_config()
    value = config.get(key, default)
    if value is None or value == "":
        env_key = f"MIIE_{key.upper()}"
        value = os.environ.get(env_key, default)
    return value


def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)


# ── Config Display ─────────────────────────────────────────────────────
def display_config() -> None:
    """Display current configuration."""
    config = load_config()

    print_section("Current Configuration")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="bold")
    table.add_column("Value")
    table.add_column("Source")

    for key, default_val in DEFAULT_CONFIG.items():
        value = config.get(key, default_val)
        source = "config" if key in config else "default"
        env_key = f"MIIE_{key.upper()}"
        if os.environ.get(env_key):
            value = os.environ[env_key]
            source = "env"
        # Mask sensitive values
        if "token" in key and value:
            value = value[:4] + "..." + value[-4:] if len(str(value)) > 8 else "****"
        table.add_row(key, str(value), source)

    console.print(table)


# ── Config Validation ──────────────────────────────────────────────────
def validate_config(config: dict) -> list[str]:
    """Validate configuration values. Returns list of errors."""
    errors = []

    if config.get("parallelism", 1) < 1:
        errors.append("parallelism must be >= 1")

    if config.get("default_window_size", 7) < 1:
        errors.append("default_window_size must be >= 1")

    theme = config.get("theme", "auto")
    if theme not in ("auto", "dark", "light"):
        errors.append(f"Invalid theme: {theme}")

    return errors
