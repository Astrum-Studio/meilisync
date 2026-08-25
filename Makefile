.PHONY: install lint format typecheck test test-all build docs docs-serve ci pre-commit

install:
	uv sync --all-extras --group dev --group docs
	uv run pre-commit install

pre-commit:
	uv run pre-commit install
	uv run pre-commit run --all-files

lint:
	uv run --all-extras ruff check meilisync tests conftest.py
	uv run --all-extras ruff format --check meilisync tests conftest.py

format:
	uv run --all-extras ruff format meilisync tests conftest.py
	uv run --all-extras ruff check meilisync tests conftest.py --fix

typecheck:
	uv run --all-extras ty check meilisync tests conftest.py

test:
	PYTHONDEVMODE=1 uv run --all-extras pytest -m "not integration"

test-all:
	PYTHONDEVMODE=1 uv run --all-extras pytest

build:
	uv build

docs:
	uv run mkdocs build --strict

docs-serve:
	uv run mkdocs serve

ci: lint typecheck test
