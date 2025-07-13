.PHONY: help install install-dev test test-unit test-integration lint format type-check clean

help:
	@echo "Available commands:"
	@echo "  make install        Install the package"
	@echo "  make install-dev    Install with development dependencies"
	@echo "  make test          Run all tests"
	@echo "  make test-unit     Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black"
	@echo "  make type-check    Run mypy type checking"
	@echo "  make clean         Clean up temporary files"

install:
	pip install -e .

install-dev:
	pip install -e .[dev]
	pre-commit install

test:
	pytest

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

lint:
	ruff check .

format:
	black .
	ruff check . --fix

type-check:
	mypy unified/

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache