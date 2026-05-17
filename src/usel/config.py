"""Configuration loader for usel."""

from pathlib import Path

import yaml

from .models import Config

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "u-sel" / "sels.yml"


def load_config(path: Path | None = None) -> Config:
    """Load configuration from YAML file.

    Args:
        path: Path to config file. Defaults to ~/.config/u-sel/sels.yml

    Returns:
        Config object with selection items.

    Raises:
        FileNotFoundError: If config file does not exist.
        yaml.YAMLError: If config file is invalid YAML.
    """
    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        data = []

    if not isinstance(data, list):
        raise ValueError(f"Config must be a list, got {type(data).__name__}")

    return Config.from_list(data)


def get_config_path() -> Path:
    """Get the default configuration path."""
    return DEFAULT_CONFIG_PATH


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
