"""MIIE Branding -- Premium visual identity for the CLI.

Provides ASCII art logos, splash screens, and branded visual elements.
All characters are cp1252/ASCII compatible for Windows terminal support.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ── Logo Variants ───────────────────────────────────────────────────────

LOGO_FULL = r"""
     __  __ _____ _____ ___  __  __
    |  \/  |_   _|  __ \__ \|  \/  |
    | \  / | | | | |__) | ) | |\/| |
    | |\/| | | | |  ___/ / /| |  | |
    |_|  |_| |_|_|_|  /____/|_|  |_|  v1.6.0
"""

LOGO_FULL_TALL = LOGO_FULL

LOGO_FULL_DOUBLE = LOGO_FULL

LOGO_BLOCK = r"""
    +=====================================================================+
    |                                                                     |
    |   ################  ################  ################  ################  |
    |   ##          ##  ################  ################  ################  |
    |   ##      ####    ####          ####  ####          ####  ################  |
    |   ##    ####      ####          ####  ####          ####  ####          ##  |
    |   ##  ####        ####          ####  ####          ####  ####          ##  |
    |   ####            ####          ####  ####          ####  ####          ##  |
    |   ################  ################  ################  ################  |
    |                                                                     |
    |   Measurement Integrity Intelligence Engine                         |
    |                                                                     |
    +=====================================================================+"""

LOGO_COMPACT = r"""
    [MIIE] v{ver} - Measurement Integrity Intelligence Engine"""

LOGO_MINIMAL = r"""
    MIIE v{ver}"""

# ── Color Palettes ──────────────────────────────────────────────────────

PALETTE_PREMIUM = {
    "logo": "bold cyan",
    "logo_accent": "bold bright_cyan",
    "version": "bold white",
    "tagline": "dim white",
    "border": "bright_cyan",
    "glow": "bright_blue",
}

PALETTE_DARK = {
    "logo": "bold bright_blue",
    "logo_accent": "bold bright_magenta",
    "version": "bold white",
    "tagline": "dim white",
    "border": "blue",
    "glow": "bright_cyan",
}

PALETTE_MINIMAL = {
    "logo": "bold white",
    "logo_accent": "bold cyan",
    "version": "bold white",
    "tagline": "dim",
    "border": "white",
    "glow": "cyan",
}


# ── Logo Rendering ──────────────────────────────────────────────────────


def render_logo(
    variant: Literal["full", "tall", "double", "compact", "minimal", "block"] = "full",
    palette: dict | None = None,
) -> Text:
    """Render the MIIE logo as a Rich Text object."""
    pal = palette or PALETTE_PREMIUM
    logos = {
        "full": LOGO_FULL,
        "tall": LOGO_FULL_TALL,
        "double": LOGO_FULL_DOUBLE,
        "compact": LOGO_COMPACT,
        "minimal": LOGO_MINIMAL,
        "block": LOGO_BLOCK,
    }
    logo_str = logos.get(variant, LOGO_FULL)

    text = Text()
    text.append(logo_str, style=pal["logo"])
    return text


def print_banner(
    version: str,
    subtitle: str = "Measurement Integrity Intelligence Engine",
    variant: Literal["full", "tall", "double", "compact", "minimal", "block"] = "full",
    palette: dict | None = None,
    show_tagline: bool = True,
) -> None:
    """Print the premium MIIE banner with ASCII art logo."""
    pal = palette or PALETTE_PREMIUM
    console = Console()

    banner = Text()
    # Logo
    logo = render_logo(variant, pal)
    banner.append_text(logo)
    banner.append("\n")

    # Version line
    banner.append(f"  v{version}", style=pal["version"])

    # Tagline
    if show_tagline:
        banner.append(f"  - {subtitle}", style=pal["tagline"])

    console.print(
        Panel(
            banner,
            border_style=pal["border"],
            padding=(1, 2),
            expand=False,
        )
    )


def print_splash(
    version: str,
    palette: dict | None = None,
    delay: float = 0.0,
) -> None:
    """Print an animated splash screen with logo reveal."""
    pal = palette or PALETTE_PREMIUM
    console = Console()

    # Clear screen on supported terminals
    if sys.stdout.isatty():
        console.clear()

    # Logo with glow effect — line by line reveal
    logo_lines = LOGO_FULL_TALL.strip().split("\n")
    for i, line in enumerate(logo_lines):
        text = Text()
        style = pal["logo"] if i % 2 == 0 else pal["logo_accent"]
        text.append(f"  {line}", style=style)
        console.print(text)
        if delay > 0:
            time.sleep(delay / len(logo_lines))

    # Version + tagline
    console.print()
    version_text = Text()
    version_text.append(f"  v{version}", style=pal["version"])
    version_text.append(f"  - Measurement Integrity Intelligence Engine", style=pal["tagline"])
    console.print(version_text)

    # Separator
    console.print()
    sep = Text()
    sep.append("  " + "=" * 56, style=pal["border"])
    console.print(sep)
    console.print()


def print_compact_banner(version: str) -> None:
    """Print a compact single-line banner."""
    console = Console()
    text = Text()
    text.append(" MIIE ", style="bold white on bright_cyan")
    text.append(f" v{version} ", style="bold")
    text.append(" Measurement Integrity Intelligence Engine", style="dim")
    console.print(text)


def print_footer(message: str = "Analysis Complete", success: bool = True) -> None:
    """Print the MIIE footer with premium styling."""
    style = "bold green" if success else "bold red"
    border = "green" if success else "red"
    icon = "V" if success else "!"

    console = Console()

    # Build footer content
    footer = Text()
    footer.append(f"\n  {icon}  ", style=style)
    footer.append(message, style=style)
    footer.append("\n")

    console.print(
        Panel(
            footer,
            border_style=border,
            padding=(0, 2),
            expand=False,
        )
    )


def print_section_header(title: str, width: int = 60) -> None:
    """Print a styled section header."""
    console = Console()
    text = Text()
    text.append(f"\n  {'-' * 3}{title.upper()}{'-' * (width - len(title) - 5)}", style="bold cyan")
    console.print(text)


# ── Decorations ─────────────────────────────────────────────────────────

DIVIDER_DOUBLE = "=" * 60
DIVIDER_SINGLE = "-" * 60
DIVIDER_DOTS = "." * 60


def print_startup_screen(version: str) -> None:
    """Print the full startup screen with branding."""
    console = Console()
    console.print()
    print_banner(variant="full", version=version)
    console.print()
