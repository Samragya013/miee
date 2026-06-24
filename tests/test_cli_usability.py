"""Phase 8: Tests for CLI progress, human-friendly output, and verbose mode."""
import subprocess
import pytest
from click.testing import CliRunner
from miie.cli import cli


@pytest.fixture
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture
def repo_with_commits(tmp_path):
    """Create a test repo with enough commits to pass validation."""
    import os
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo), capture_output=True)
    # Create 12 commits spanning 14+ days to produce 2+ windows (AFD §Step 8)
    for i in range(12):
        f = repo / f"file_{i}.txt"
        f.write_text(f"content {i}")
        subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True)
        # Stagger commits across 21 days to ensure 2+ windows with size=7
        days_offset = i * 2  # 2 days apart = 21 days total
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = f"2024-01-{1 + days_offset:02d}T12:00:00"
        env["GIT_COMMITTER_DATE"] = f"2024-01-{1 + days_offset:02d}T12:00:00"
        subprocess.run(["git", "commit", "-m", f"commit {i}"], cwd=str(repo),
                       capture_output=True, env=env)
    return repo


class TestProgressStages:
    """Verify progress stages appear in output."""

    def test_all_seven_stages_shown(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "[1/7]" in output
        assert "[2/7]" in output
        assert "[3/7]" in output
        assert "[4/7]" in output
        assert "[5/7]" in output
        assert "[6/7]" in output
        assert "[7/7]" in output

    def test_stage_names_correct(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Repository Acquisition" in output
        assert "Repository Validation" in output
        assert "Metric Extraction" in output
        assert "Window Generation" in output
        assert "Detector Execution" in output
        assert "Evidence Generation" in output
        assert "Final Assessment" in output

    def test_done_markers_present(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert output.count("[DONE]") == 7

    def test_timing_in_done_markers(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "[DONE] (0." in output or "[DONE] (1." in output


class TestHumanFriendlyOutput:
    """Default mode should show human-friendly messages."""

    def test_no_detector_ids_in_default_mode(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "[D-01]" not in output
        assert "[D-02]" not in output
        assert "[D-03]" not in output

    def test_human_friendly_check_messages(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "No significant metric drift detected" in output
        assert "Historical metric relationships remain stable" in output
        assert "No threshold compression patterns detected" in output

    def test_ok_markers_in_findings(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "[OK]" in output

    def test_assessment_labels_human(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Metric Integrity:  Very High" in output or "Metric Integrity:  High" in output

    def test_interpretation_present(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        # Phase 8: "Interpretation" replaced with "Summary" + "Confidence" + "Risk Assessment"
        assert "Summary" in output
        assert "metric" in output.lower() or "anomal" in output.lower()

    def test_recommended_action_present(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Recommended Action" in output


class TestVerboseMode:
    """--verbose should show detector IDs and timing."""

    def test_verbose_shows_detector_ids(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["--verbose", "analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "[D-01]" in output
        assert "[D-02]" in output
        assert "[D-03]" in output

    def test_verbose_shows_timing(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["--verbose", "analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Stage Timing" in output
        assert "Acquisition:" in output
        assert "Total:" in output

    def test_verbose_no_human_friendly_messages(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["--verbose", "analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "No significant metric drift detected" not in output


class TestReportStructure:
    """Verify required report sections."""

    def test_banner_present(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "MIIE v" in output
        assert "Measurement Integrity Analysis" in output

    def test_analysis_summary_section(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        # Phase 8: "Analysis Summary" replaced with "Analysis Coverage" + "Summary"
        assert "Analysis Coverage" in output
        assert "commits" in output.lower()

    def test_integrity_findings_section(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Integrity Findings" in output

    def test_assessment_section(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Assessment" in output
        assert "Metric Integrity:" in output
        assert "Confidence:" in output

    def test_reports_saved_section(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Reports Saved:" in output

    def test_analysis_complete_footer(self, runner, repo_with_commits):
        # Use commit strategy with size=5 to produce 2+ windows from 12 commits
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "-w", "commit", "-s", "5", "--format", "json"])
        output = result.output
        assert "Analysis Complete" in output


class TestDryRunUnchanged:
    """Dry-run mode must still work."""

    def test_dry_run_unchanged(self, runner):
        result = runner.invoke(cli, ["analyze", "https://example.com/repo.git", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry Run" in result.output
        assert "Validation : PASSED" in result.output
