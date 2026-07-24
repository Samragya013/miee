"""Tests for MIIE CLI error handling module."""

from pathlib import Path

from miie.cli.errors import (
    ERROR_CATALOG,
    _match_error_to_catalog,
    display_warning,
    save_partial_results,
)


class TestErrorCatalog:
    def test_catalog_has_entries(self):
        assert len(ERROR_CATALOG) > 0

    def test_catalog_entries_have_required_keys(self):
        for entry in ERROR_CATALOG.values():
            assert "title" in entry
            assert "explanation" in entry
            assert "remediation" in entry


class TestMatchErrorToCatalog:
    def test_not_found(self):
        result = _match_error_to_catalog("FileNotFoundError", "No such file or directory")
        assert result is not None
        assert result["title"] == "Repository Not Found"

    def test_clone_failed(self):
        result = _match_error_to_catalog("GitCommandError", "clone failed")
        assert result is not None
        assert result["title"] == "Git Clone Failed"

    def test_auth_failed(self):
        result = _match_error_to_catalog("HTTPError", "401 Unauthorized")
        assert result is not None
        assert result["title"] == "Authentication Failed"

    def test_insufficient_windows(self):
        result = _match_error_to_catalog("ValueError", "Insufficient windows")
        assert result is not None
        assert result["title"] == "Insufficient Analysis Windows"

    def test_unknown_error(self):
        result = _match_error_to_catalog("RuntimeError", "something unknown")
        assert result is None


class TestDisplayWarning:
    def test_display_warning(self, capsys):
        display_warning("Test warning message")
        captured = capsys.readouterr()
        assert "Test warning message" in captured.out


class TestSavePartialResults:
    def test_save_partial_results(self, tmp_path):
        error = ValueError("Test error")
        result = save_partial_results(str(tmp_path), error)
        assert result is not None
        assert result.exists()

        import json

        data = json.loads(result.read_text())
        assert data["error"] == "Test error"
        assert data["partial"] is True

    def test_save_partial_results_invalid_dir(self, monkeypatch):

        def mock_mkdir(*args, **kwargs):
            raise OSError("Permission denied")

        monkeypatch.setattr(Path, "mkdir", mock_mkdir)
        error = ValueError("Test error")
        result = save_partial_results("/nonexistent/path", error)
        assert result is None
