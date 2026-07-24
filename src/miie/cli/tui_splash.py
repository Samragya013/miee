"""MIIE TUI Splash -- Animated logo reveal for the TUI."""

from __future__ import annotations

import time

from rich.console import Console
from rich.text import Text

from .branding import LOGO_FULL_TALL, PALETTE_PREMIUM


def play_splash(console: Console | None = None, delay: float = 0.6) -> None:
    """Play animated splash with big MIIE logo reveal.

    Line-by-line reveal with alternating colors and subtle glow.
    """
    if console is None:
        console = Console()

    pal = PALETTE_PREMIUM
    logo_lines = LOGO_FULL_TALL.strip().split("\n")
    total = len(logo_lines)

    # Clear
    if console.is_terminal:
        console.clear()

    # Reveal logo line by line
    for i, line in enumerate(logo_lines):
        text = Text()
        # Alternate between main and accent colors
        style = pal["logo"] if i % 3 == 0 else pal["logo_accent"] if i % 3 == 1 else pal["glow"]
        text.append(f"  {line}", style=style)
        console.print(text)
        if delay > 0:
            time.sleep(delay / total)

    # Version + subtitle
    console.print()
    ver_text = Text()
    try:
        from miie import __version__
        ver = __version__
    except ImportError:
        ver = "1.6.0"
    ver_text.append(f"  v{ver}", style=pal["version"])
    ver_text.append("  Measurement Integrity Intelligence Engine", style=pal["tagline"])
    console.print(ver_text)

    # Separator
    console.print()
    sep = Text()
    sep.append("  " + "=" * 56, style=pal["border"])
    console.print(sep)
    console.print()

    # Pause before main UI
    if delay > 0:
        time.sleep(0.3)
