#!/usr/bin/env python3
"""Interactive CLI usage demonstration."""

import subprocess
import sys


def main():
    commands = [
        ("Show version", ["miie", "--version"]),
        ("Show help", ["miie", "--help"]),
        ("Show status", ["miie", "status"]),
        ("Dry run analysis", ["miie", "analyze", ".", "--dry-run"]),
    ]

    print("MIIE Interactive CLI Demo\n")

    for desc, cmd in commands:
        print(f"\n--- {desc} ---")
        print(f"$ {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except FileNotFoundError:
            print("MIIE not installed. Run: pip install -e .")
            break


if __name__ == "__main__":
    main()
