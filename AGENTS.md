# Project Agent

**Workspace Path:** `/Volumes/data/working/ai/u-sel`
_(Note to Pi: Your file write/edit tools run in a different directory by default. You MUST use absolute paths starting with the Workspace Path above for ALL file operations!)_

**Generated:** 2025-05-17

## Stack

- **Language:** Python 3.10+
- **TUI Framework:** Textual >= 0.50.0
- **CLI Framework:** Click >= 8.0
- **Config Format:** PyYAML >= 6.0
- **Build System:** Hatchling (uv managed)

## Structure

```
u-sel/
├── src/usel/           # Main package
│   ├── __init__.py     # Package init
│   ├── cli.py          # CLI entry point (click)
│   ├── app.py          # Textual TUI application
│   ├── config.py       # YAML config loader
│   └── models.py       # Data models (Selection, Config)
├── tests/              # Test suite
│   ├── test_config.py  # Config loader tests
│   └── test_models.py  # Model tests
├── hooks/              # Git hooks (pre-commit)
├── pyproject.toml      # Project metadata & tool config
├── Makefile            # Development commands
└── README.md           # Project documentation
```

## Commands

| Action      | Command               |
| ----------- | --------------------- |
| Install     | `make install`        |
| Dev Install | `make dev`            |
| Build       | `uv pip install -e .` |
| Test        | `make test`           |
| Run         | `make run`            |
| Lint        | `make lint`           |
| Format      | `make format`         |
| Type Check  | `make type-check`     |
| All Checks  | `make check`          |

## Conventions

- **Code Style:** Ruff with `py310` target, 100 char line length
- **Linter Rules:** E, F, W, I, N, UP, B, C4 (ignore E501)
- **Type Checking:** MyPy strict=false, ignore missing imports for yaml/click
- **Testing:** pytest with asyncio mode, test path: `tests/`
- **Python Version:** 3.10+ (uses `list[T]` syntax)

## Key Files

| File                 | Purpose                                                     |
| -------------------- | ----------------------------------------------------------- |
| `src/usel/app.py`    | Textual TUI - search, select, output command                |
| `src/usel/cli.py`    | Click CLI entry, config loading, list mode                  |
| `src/usel/config.py` | YAML loader, default path `~/.config/u-sel/sels.yml`        |
| `src/usel/models.py` | `Selection` dataclass, `Config` factory                     |
| `pyproject.toml`     | Dependencies, scripts (`usel = usel.cli:main`), tool config |

## What to Avoid

- Don't change `usel.cli:main` entry point without updating pyproject.toml
- Don't modify config path without updating DEFAULT_CONFIG_PATH in config.py
- Don't add new imports without type stubs if strict type checking needed
- Avoid editing venv or cache directories - they are auto-generated

## Notes

### Config File Format (sels.yml)

```yaml
- title: pi -c
  group: pi
  description: 启动PI，继续上次会话
  output: pi -c
- title: pi -r
  group: pi
  description: 启动PI，选择一个会话
  output: pi -r
```

- Default location: `~/.config/u-sel/sels.yml`
- Structure: List of items with `title`, `group`, `description`, `output`
- `output` field is what gets printed to stdout on selection

### Zellij Integration

Run via zellij floating pane:

```bash
zellij action new-pane --floating --width 60% --height 60% --x 20% --y %20 -c -- bash -c "$(usel)"
```

The selected command is output to stdout, which zellij then executes in the original pane after the floating pane closes.

### Git Hooks

This project uses git hooks (configured via `hooks/` directory). Set with:

```bash
git config core.hooksPath hooks
```

### Development Environment

- Uses `.venv` virtual environment
- Managed by `uv` (see uv.lock)
- MyPy and Ruff caches in `.ruff_cache/`, `.mypy_cache/`

### Testing Notes

- Mock `~/.config/u-sel/sels.yml` in tests using `tmp_path` fixture
- Config must be a list (not dict or None)
- Invalid YAML raises `yaml.YAMLError`
