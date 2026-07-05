import subprocess
import sys

from miie import __version__


def test_version_constant():
    """Test that the version constant is correctly set."""
    assert __version__ == "1.6.0"


def test_cli_version_output():
    """Test that the CLI outputs the correct version."""
    result = subprocess.run(
        [sys.executable, "-m", "miie", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert f"miie, version {__version__}" in result.stdout
