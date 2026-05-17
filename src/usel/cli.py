"""CLI entry point for usel."""

import sys
from pathlib import Path
from typing import Any

import click

from .app import run_app
from .config import DEFAULT_CONFIG_PATH, load_config


@click.command()
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True),
    default=None,
    help="Path to config file (default: ~/.config/u-sel/sels.yml)",
)
@click.option(
    "-l",
    "--list",
    "list_items",
    is_flag=True,
    help="List all available selections and exit",
)
def main(config: Any, list_items: bool) -> None:
    """Search and select command picker for zellij.

    Reads configuration from ~/.config/u-sel/sels.yml by default,
    or from the specified config file.
    """
    if config:
        config_path = Path(config)
    else:
        config_path = DEFAULT_CONFIG_PATH

    try:
        cfg = load_config(config_path)
    except FileNotFoundError:
        click.echo(f"Error: Config file not found: {config_path}", err=True)
        click.echo(f"Create one at: {config_path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        sys.exit(1)

    if list_items:
        for item in cfg.items:
            click.echo(f"{item.title} ({item.group}): {item.output}")
        return

    if not cfg.items:
        click.echo("No selections found in config.", err=True)
        sys.exit(1)

    result = run_app(cfg.items)

    if result:
        click.echo(result)


if __name__ == "__main__":
    main()
