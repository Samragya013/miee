"""Tests for MIIE CLI configuration module."""

import json

from miie.cli.config import (
    DEFAULT_CONFIG,
    display_config,
    get_config_value,
    load_config,
    save_config,
    set_config_value,
    validate_config,
)


class TestDefaultConfig:
    def test_default_config_has_required_keys(self):
        required_keys = [
            "github_token",
            "output_dir",
            "parallelism",
            "theme",
            "default_metrics",
            "default_detectors",
        ]
        for key in required_keys:
            assert key in DEFAULT_CONFIG


class TestLoadConfig:
    def test_load_config_returns_dict(self):
        config = load_config()
        assert isinstance(config, dict)

    def test_load_config_has_defaults(self):
        config = load_config()
        assert "output_dir" in config
        assert "parallelism" in config


class TestSaveConfig:
    def test_save_config(self, tmp_path, monkeypatch):
        monkeypatch.setattr("miie.cli.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("miie.cli.config.CONFIG_FILE", tmp_path / "config.json")

        test_config = {"test_key": "test_value"}
        save_config(test_config)

        saved = json.loads((tmp_path / "config.json").read_text())
        assert saved == test_config


class TestGetConfigValue:
    def test_get_config_value_default(self, monkeypatch):
        monkeypatch.setattr("miie.cli.config.load_config", lambda: {})
        value = get_config_value("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_get_config_value_from_config(self, monkeypatch):
        monkeypatch.setattr("miie.cli.config.load_config", lambda: {"test_key": "test_value"})
        value = get_config_value("test_key")
        assert value == "test_value"


class TestSetConfigValue:
    def test_set_config_value(self, tmp_path, monkeypatch):
        monkeypatch.setattr("miie.cli.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("miie.cli.config.CONFIG_FILE", tmp_path / "config.json")

        # Create initial config
        save_config({})

        # Set value
        set_config_value("new_key", "new_value")

        # Verify
        config = load_config()
        assert config["new_key"] == "new_value"


class TestValidateConfig:
    def test_valid_config(self):
        errors = validate_config(DEFAULT_CONFIG)
        assert len(errors) == 0

    def test_invalid_parallelism(self):
        config = {"parallelism": -1}
        errors = validate_config(config)
        assert len(errors) > 0
        assert "parallelism" in errors[0]

    def test_invalid_theme(self):
        config = {"theme": "invalid"}
        errors = validate_config(config)
        assert len(errors) > 0
        assert "theme" in errors[0]


class TestDisplayConfig:
    def test_display_config(self, capsys):
        display_config()
        captured = capsys.readouterr()
        assert "output_dir" in captured.out
