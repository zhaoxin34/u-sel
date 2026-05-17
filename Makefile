.PHONY: help install dev test lint format type-check clean fmt docs run

help:
	@echo "Available commands:"
	@echo "  make install    - Install usel (editable)"
	@echo "  make dev        - Install with dev dependencies"
	@echo "  make run        - Run usel application"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make type-check - Run mypy type checker"
	@echo "  make clean      - Clean build artifacts"

install:
	uv pip install -e .

dev:
	uv pip install -e . --group dev

run:
	uv run usel

test:
	uv run pytest

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

type-check:
	uv run mypy src/

fmt:
	uv run ruff format src/ && uv run ruff check src/ --fix

clean:
	rm -rf build/ dist/ *.egg-info/ .ruff_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Install dependencies and run dev workflow
setup: dev

# Run all checks
check: lint type-check test
