"""Tests for usel config."""

from pathlib import Path

import yaml

from usel.config import load_config


def test_load_config(tmp_path):
    """Test loading configuration from a YAML file."""
    config_file = tmp_path / "test.yml"
    data = [
        {"title": "cmd1", "group": "g1", "description": "desc1", "output": "out1"},
        {"title": "cmd2", "group": "g2", "description": "desc2", "output": "out2"},
    ]
    config_file.write_text(yaml.dump(data))

    config = load_config(config_file)
    assert len(config.items) == 2
    assert config.items[0].output == "out1"


def test_load_config_file_not_found():
    """Test FileNotFoundError for missing config."""
    fake_path = Path("/nonexistent/config.yml")
    try:
        load_config(fake_path)
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        pass


def test_load_config_invalid_yaml(tmp_path):
    """Test ValueError for invalid YAML."""
    config_file = tmp_path / "invalid.yml"
    config_file.write_text("invalid: [yaml")

    try:
        load_config(config_file)
        assert False, "Should raise YAMLError"
    except yaml.YAMLError:
        pass


def test_load_config_not_a_list(tmp_path):
    """Test ValueError when config is not a list."""
    config_file = tmp_path / "notalist.yml"
    config_file.write_text("key: value")

    try:
        load_config(config_file)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "must be a list" in str(e)


def test_load_config_empty_file(tmp_path):
    """Test empty config file is treated as empty list."""
    config_file = tmp_path / "empty.yml"
    config_file.write_text("")

    config = load_config(config_file)
    assert len(config.items) == 0
