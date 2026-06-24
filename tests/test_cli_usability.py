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
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo), capture_output=True)
    # Create 12 commits to meet minimum (10)
    for i in range(12):
        f = repo / f"file_{i}.txt"
        f.write_text(f"content {i}")
        subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True)
        subprocess.run(["git", "commit", "-m", f"commit {i}"], cwd=str(repo), capture_output=True)
    return repo


class TestProgressStages:
    """Verify progress stages appear in output."""

    def test_all_seven_stages_shown(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "[1/7]" in output
        assert "[2/7]" in output
        assert "[3/7]" in output
        assert "[4/7]" in output
        assert "[5/7]" in output
        assert "[6/7]" in output
        assert "[7/7]" in output

    def test_stage_names_correct(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Repository Acquisition" in output
        assert "Repository Validation" in output
        assert "Metric Extraction" in output
        assert "Window Generation" in output
        assert "Detector Execution" in output
        assert "Evidence Generation" in output
        assert "Final Assessment" in output

    def test_done_markers_present(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert output.count("[DONE]") == 7

    def test_timing_in_done_markers(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "[DONE] (0." in output or "[DONE] (1." in output


class TestHumanFriendlyOutput:
    """Default mode should show human-friendly messages."""

    def test_no_detector_ids_in_default_mode(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "[D-01]" not in output
        assert "[D-02]" not in output
        assert "[D-03]" not in output

    def test_human_friendly_check_messages(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "No significant metric drift detected" in output
        assert "Historical metric relationships remain stable" in output
        assert "No threshold compression patterns detected" in output

    def test_ok_markers_in_findings(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "[OK]" in output

    def test_assessment_labels_human(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Metric Integrity:  Very High" in output or "Metric Integrity:  High" in output

    def test_interpretation_present(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Interpretation" in output
        assert "natural development patterns" in output or "anomalies" in output

    def test_recommended_action_present(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Recommended Action" in output


class TestVerboseMode:
    """--verbose should show detector IDs and timing."""

    def test_verbose_shows_detector_ids(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["--verbose", "analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "[D-01]" in output
        assert "[D-02]" in output
        assert "[D-03]" in output

    def test_verbose_shows_timing(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["--verbose", "analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Stage Timing" in output
        assert "Acquisition:" in output
        assert "Total:" in output

    def test_verbose_no_human_friendly_messages(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["--verbose", "analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "No significant metric drift detected" not in output


class TestReportStructure:
    """Verify required report sections."""

    def test_banner_present(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "MIIE v" in output
        assert "Measurement Integrity Analysis" in output

    def test_analysis_summary_section(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Analysis Summary" in output
        assert "Repository history analyzed successfully" in output

    def test_integrity_findings_section(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Integrity Findings" in output

    def test_assessment_section(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Assessment" in output
        assert "Metric Integrity:" in output
        assert "Confidence:" in output

    def test_reports_saved_section(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Reports Saved:" in output

    def test_analysis_complete_footer(self, runner, repo_with_commits):
        result = runner.invoke(cli, ["analyze", str(repo_with_commits), "--format", "json"])
        output = result.output
        assert "Analysis Complete" in output


class TestDryRunUnchanged:
    """Dry-run mode must still work."""

    def test_dry_run_unchanged(self, runner):
        result = runner.invoke(cli, ["analyze", "https://example.com/repo.git", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry Run" in result.output
        assert "Validation : PASSED" in result.output
