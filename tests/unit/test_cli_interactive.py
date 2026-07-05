"""Tests for MIIE CLI interactive module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from miie.cli.interactive import (
    load_recent,
    save_recent,
    add_to_recent,
    prompt_repository_source,
)


class TestLoadRecent:
    def test_load_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr("miie.cli.interactive.RECENT_FILE", tmp_path / "recent.json")
        result = load_recent()
        assert result == []

    def test_load_existing(self, tmp_path, monkeypatch):
        monkeypatch.setattr("miie.cli.interactive.RECENT_FILE", tmp_path / "recent.json")
        repos = [{"url": "test.com", "name": "test"}]
        (tmp_path / "recent.json").write_text(json.dumps(repos), encoding="utf-8")
        result = load_recent()
        assert len(result) == 1
        assert result[0]["url"] == "test.com"


class TestSaveRecent:
    def test_save_new(self, tmp_path, monkeypatch):
        monkeypatch.setattr("miie.cli.interactive.RECENT_FILE", tmp_path / "recent.json")
        save_recent([{"url": "test.com", "name": "test"}])
        result = load_recent()
        assert len(result) == 1


class TestAddToRecent:
    def test_add_new(self, tmp_path, monkeypatch):
        monkeypatch.setattr("miie.cli.interactive.RECENT_FILE", tmp_path / "recent.json")
        add_to_recent({"url": "test.com", "name": "test"})
        result = load_recent()
        assert len(result) == 1

    def test_add_deduplicates(self, tmp_path, monkeypatch):
        monkeypatch.setattr("miie.cli.interactive.RECENT_FILE", tmp_path / "recent.json")
        add_to_recent({"url": "test.com", "name": "test"})
        add_to_recent({"url": "test.com", "name": "test"})
        result = load_recent()
        assert len(result) == 1


class TestPromptRepositorySource:
    def test_function_exists(self):
        assert callable(prompt_repository_source)
