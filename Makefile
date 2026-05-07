# Makefile for Tracify project
# Convenience commands for common development tasks

.PHONY: help install test lint format typecheck security clean run build all

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --all-groups

test:  ## Run tests with coverage
	uv run pytest --cov=src/tracify --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests without coverage
	uv run pytest -v

lint:  ## Run ruff linter
	uv run ruff check src/ tests/

lint-fix:  ## Run ruff linter with auto-fix
	uv run ruff check --fix src/ tests/

format:  ## Format code with ruff
	uv run ruff format src/ tests/

format-check:  ## Check code formatting
	uv run ruff format --check src/ tests/

typecheck:  ## Run mypy type checker
	uv run mypy src/

security:  ## Run security scanners
	uv run bandit -r src/
	uv pip install pip-audit 2>/dev/null || true
	uv run pip-audit --desc || true

clean:  ## Clean build artifacts and cache
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run:  ## Run the application
	uv run tracify

build:  ## Build the package
	uv build

all: lint format-check typecheck test  ## Run all quality checks

pre-commit:  ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	uv run pre-commit run --all-files

ci:  ## Run CI-like checks locally
	@echo "Running CI checks..."
	@$(MAKE) lint
	@$(MAKE) format-check
	@$(MAKE) typecheck
	@$(MAKE) security
	@$(MAKE) test
	@echo "✅ All CI checks passed!"
