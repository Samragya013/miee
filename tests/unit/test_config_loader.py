"""Tests for M-12: ConfigLoader and Config dataclass."""

import json
import textwrap
from pathlib import Path

import pytest

from miie.config.loader import (
    Config,
    ConfigError,
    ConfigLoader,
    _canonical_json,
    _compute_config_hash,
    DEFAULT_DETECTOR_WEIGHTS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_yaml(path: Path, content: str) -> Path:
    """Write a YAML string to *path* and return it."""
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


def _write_json(path: Path, data: dict) -> Path:
    """Write a JSON dict to *path* and return it."""
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def loader():
    return ConfigLoader()


@pytest.fixture
def yaml_config(tmp_path):
    return _write_yaml(
        tmp_path / "miie.yaml",
        """\
        repo: /path/to/repo
        metrics:
          - M-01
          - M-07
        window_strategy: commit
        window_size: 50
        detectors:
          - D-01
          - D-03
        output_formats:
          - json
        exclude_bots: true
        seed: 99
        verbose: true
        keep_cache: true
        shallow_depth: 5
        """,
    )


@pytest.fixture
def json_config(tmp_path):
    return _write_json(
        tmp_path / "miie.json",
        {
            "repo": "/json/repo",
            "metrics": ["M-03"],
            "window_strategy": "release",
            "window_size": 30,
            "detectors": ["D-02"],
            "output_formats": ["md"],
            "exclude_bots": False,
            "seed": 123,
        },
    )


# ---------------------------------------------------------------------------
# 1. Load from YAML file
# ---------------------------------------------------------------------------

class TestLoadYAML:
    def test_loads_yaml_file(self, loader, yaml_config):
        config = loader.load(config_path=yaml_config)
        assert isinstance(config, Config)
        assert config.repo == "/path/to/repo"
        assert config.metrics == ["M-01", "M-07"]
        assert config.window_strategy == "commit"
        assert config.window_size == 50
        assert config.detectors == ["D-01", "D-03"]
        assert config.output_formats == ["json"]
        assert config.exclude_bots is True
        assert config.seed == 99
        assert config.verbose is True
        assert config.keep_cache is True
        assert config.shallow_depth == 5

    def test_config_hash_is_set(self, loader, yaml_config):
        config = loader.load(config_path=yaml_config)
        assert config.config_hash
        assert len(config.config_hash) == 64  # SHA-256 hex digest


# ---------------------------------------------------------------------------
# 2. Load from JSON file
# ---------------------------------------------------------------------------

class TestLoadJSON:
    def test_loads_json_file(self, loader, json_config):
        config = loader.load(config_path=json_config)
        assert isinstance(config, Config)
        assert config.repo == "/json/repo"
        assert config.metrics == ["M-03"]
        assert config.window_strategy == "release"
        assert config.window_size == 30
        assert config.detectors == ["D-02"]
        assert config.output_formats == ["md"]
        assert config.exclude_bots is False
        assert config.seed == 123


# ---------------------------------------------------------------------------
# 3. CLI overrides merge correctly
# ---------------------------------------------------------------------------

class TestCLIOverrideMerge:
    def test_overrides_take_precedence(self, loader, yaml_config):
        config = loader.load(
            config_path=yaml_config,
            overrides={"seed": 7, "verbose": False, "repo": "/override"},
        )
        assert config.repo == "/override"
        assert config.seed == 7
        assert config.verbose is False
        # Non-overridden values preserved
        assert config.metrics == ["M-01", "M-07"]
        assert config.window_strategy == "commit"

    def test_none_overrides_ignored(self, loader, yaml_config):
        config = loader.load(
            config_path=yaml_config,
            overrides={"seed": None, "verbose": None},
        )
        # Original file values preserved
        assert config.seed == 99
        assert config.verbose is True

    def test_overrides_without_file(self, loader):
        config = loader.load(overrides={"repo": "/cli/only"})
        assert config.repo == "/cli/only"
        assert config.seed == 42  # default
        assert config.metrics == ["M-02", "M-06"]  # default


# ---------------------------------------------------------------------------
# 4. Invalid config raises ConfigError
# ---------------------------------------------------------------------------

class TestInvalidConfig:
    def test_invalid_metric_id(self, loader):
        with pytest.raises(ConfigError, match="Invalid metric ID"):
            loader.load(overrides={"repo": "/r", "metrics": ["M-99"]})

    def test_invalid_window_strategy(self, loader):
        with pytest.raises(ConfigError, match="Invalid window_strategy"):
            loader.load(
                overrides={"repo": "/r", "window_strategy": "invalid"}
            )

    def test_invalid_detector_id(self, loader):
        with pytest.raises(ConfigError, match="Invalid detector ID"):
            loader.load(overrides={"repo": "/r", "detectors": ["D-99"]})

    def test_invalid_output_format(self, loader):
        with pytest.raises(ConfigError, match="Invalid output format"):
            loader.load(
                overrides={"repo": "/r", "output_formats": ["pdf"]}
            )

    def test_invalid_detector_weight_key(self, loader):
        with pytest.raises(ConfigError, match="Invalid detector_weights"):
            loader.load(
                overrides={"repo": "/r", "detector_weights": {"D-99": 0.5}}
            )

    def test_invalid_window_size(self, loader):
        with pytest.raises(ConfigError, match="positive integer"):
            loader.load(overrides={"repo": "/r", "window_size": -1})

    def test_invalid_seed_type(self, loader):
        with pytest.raises(ConfigError, match="'seed' must be an integer"):
            loader.load(overrides={"repo": "/r", "seed": "not-int"})

    def test_nonexistent_config_file(self, loader, tmp_path):
        with pytest.raises(ConfigError, match="not found"):
            loader.load(config_path=tmp_path / "nope.yaml")

    def test_unsupported_file_extension(self, loader, tmp_path):
        cfg = tmp_path / "cfg.toml"
        cfg.write_text("repo = '/r'", encoding="utf-8")
        with pytest.raises(ConfigError, match="Unsupported config file"):
            loader.load(config_path=cfg)

    def test_invalid_yaml_content(self, loader, tmp_path):
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("- item1\n- item2\n", encoding="utf-8")
        with pytest.raises(ConfigError, match="YAML mapping"):
            loader.load(config_path=cfg)

    def test_invalid_json_content(self, loader, tmp_path):
        cfg = tmp_path / "bad.json"
        cfg.write_text('["not", "a", "dict"]', encoding="utf-8")
        with pytest.raises(ConfigError, match="JSON object"):
            loader.load(config_path=cfg)


# ---------------------------------------------------------------------------
# 5. Config hash is deterministic
# ---------------------------------------------------------------------------

class TestDeterministicHash:
    def test_same_input_same_hash(self, loader):
        overrides = {"repo": "/r", "seed": 42, "metrics": ["M-02", "M-06"]}
        c1 = loader.load(overrides=overrides)
        c2 = loader.load(overrides=overrides)
        assert c1.config_hash == c2.config_hash

    def test_different_input_different_hash(self, loader):
        c1 = loader.load(overrides={"repo": "/r", "seed": 42})
        c2 = loader.load(overrides={"repo": "/r", "seed": 99})
        assert c1.config_hash != c2.config_hash

    def test_hash_matches_manual_computation(self, loader):
        data = {"repo": "/r", "seed": 42}
        c = loader.load(overrides=data)
        expected = _compute_config_hash(data)
        assert c.config_hash == expected

    def test_canonical_json_is_sorted(self):
        data = {"z": 1, "a": 2}
        result = _canonical_json(data)
        assert result.index('"a"') < result.index('"z"')


# ---------------------------------------------------------------------------
# 6. Missing required field raises error
# ---------------------------------------------------------------------------

class TestMissingRequiredField:
    def test_missing_repo_raises(self, loader):
        with pytest.raises(ConfigError, match="Required field 'repo'"):
            loader.load(overrides={})

    def test_empty_repo_raises(self, loader):
        with pytest.raises(ConfigError, match="non-empty string"):
            loader.load(overrides={"repo": "   "})

    def test_repo_none_raises(self, loader):
        with pytest.raises(ConfigError, match="Required field 'repo'"):
            loader.load(overrides={"repo": None})


# ---------------------------------------------------------------------------
# 7. Default values applied correctly
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_defaults_when_no_file_or_overrides(self, loader):
        config = loader.load(overrides={"repo": "/r"})
        assert config.repo == "/r"
        assert config.since is None
        assert config.until is None
        assert config.metrics == ["M-02", "M-06"]
        assert config.window_strategy == "time"
        assert config.window_size == 90
        assert config.detectors == ["D-01", "D-02", "D-03"]
        assert config.output_formats == ["json", "md"]
        assert config.exclude_bots is False
        assert config.thresholds == {}
        assert config.detector_weights == dict(DEFAULT_DETECTOR_WEIGHTS)
        assert config.seed == 42
        assert config.output_dir == "./output"
        assert config.verbose is False
        assert config.keep_cache is False
        assert config.shallow_depth == 1

    def test_partial_overrides_preserve_defaults(self, loader):
        config = loader.load(overrides={"repo": "/r", "seed": 77})
        assert config.seed == 77
        # All other defaults intact
        assert config.window_size == 90
        assert config.detector_weights == dict(DEFAULT_DETECTOR_WEIGHTS)


# ---------------------------------------------------------------------------
# 8. Config is frozen (immutable)
# ---------------------------------------------------------------------------

class TestFrozenConfig:
    def test_cannot_mutate_fields(self, loader):
        config = loader.load(overrides={"repo": "/r"})
        with pytest.raises(AttributeError):
            config.repo = "/new"  # type: ignore[misc]

    def test_cannot_mutate_list_fields(self, loader):
        config = loader.load(overrides={"repo": "/r"})
        with pytest.raises(AttributeError):
            config.metrics = ["M-01"]  # type: ignore[misc]

    def test_cannot_mutate_dict_fields(self, loader):
        config = loader.load(overrides={"repo": "/r"})
        with pytest.raises(AttributeError):
            config.detector_weights = {}  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 9. "all" keyword accepted for metrics and detectors
# ---------------------------------------------------------------------------

class TestAllKeyword:
    def test_metrics_all_accepted(self, loader):
        config = loader.load(overrides={"repo": "/r", "metrics": ["all"]})
        assert config.metrics == ["all"]

    def test_invalid_keyword_rejected(self, loader):
        with pytest.raises(ConfigError, match="Invalid metric ID"):
            loader.load(
                overrides={"repo": "/r", "metrics": ["M-08"]}
            )
