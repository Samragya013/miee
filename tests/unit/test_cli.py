"""Tests for MIIE CLI commands."""

import os
import subprocess
import sys


def run_cli(*args):
    """Run miie CLI and return CompletedProcess."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "miie"] + list(args),
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        encoding="utf-8",
        errors="replace",
    )


class TestCLIBasic:
    def test_cli_version(self):
        result = run_cli("--version")
        assert result.returncode == 0
        assert "miie" in result.stdout.lower() or "version" in result.stdout.lower()

    def test_cli_help(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "analyze" in result.stdout
        assert "ingest" in result.stdout
        assert "status" in result.stdout
        assert "detect" in result.stdout
        assert "benchmark" in result.stdout
        assert "evaluate" in result.stdout
        assert "explain" in result.stdout
        assert "export" in result.stdout
        assert "generate" in result.stdout

    def test_analyze_help(self):
        result = run_cli("analyze", "--help")
        assert result.returncode == 0
        assert "repo" in result.stdout.lower() or "path" in result.stdout.lower()

    def test_ingest_help(self):
        result = run_cli("ingest", "--help")
        assert result.returncode == 0

    def test_detect_help(self):
        result = run_cli("detect", "--help")
        assert result.returncode == 0

    def test_benchmark_help(self):
        result = run_cli("benchmark", "--help")
        assert result.returncode == 0

    def test_evaluate_help(self):
        result = run_cli("evaluate", "--help")
        assert result.returncode == 0

    def test_explain_help(self):
        result = run_cli("explain", "--help")
        assert result.returncode == 0

    def test_export_help(self):
        result = run_cli("export", "--help")
        assert result.returncode == 0

    def test_generate_help(self):
        result = run_cli("generate", "--help")
        assert result.returncode == 0


class TestCLIDryRun:
    def test_analyze_dry_run(self):
        result = run_cli("analyze", ".", "--dry-run")
        assert result.returncode == 0
        assert "Dry Run" in result.stdout or "dry run" in result.stdout.lower()

    def test_analyze_missing_repo(self):
        result = run_cli("analyze", "/nonexistent/path")
        assert result.returncode != 0


class TestCLIStatus:
    def test_status(self):
        result = run_cli("status")
        assert result.returncode == 0
        # ASCII art logo or version string present
        assert "v1.6.0" in result.stdout or "Engine" in result.stdout
        assert "Engine" in result.stdout or "engine" in result.stdout
