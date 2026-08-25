# Contributing

Thanks for helping improve meilisync.

## Setup

Install [uv](https://docs.astral.sh/uv/). Then:

```bash
git clone https://github.com/Astrum-Studio/meilisync.git
cd meilisync
uv sync --all-extras --group dev --group docs
uv run pre-commit install
```

## Checks

```bash
make format      # ruff format + fix
make ci          # lint, typecheck, unit tests
make docs-serve  # http://127.0.0.1:8000
uv run pre-commit run --all-files
```

Every `git commit` runs **ruff format**, **ruff check --fix**, **ty check**, and unit tests (`pytest -m "not integration"`).

Unit tests do **not** need live databases:

```bash
make test
```

Integration tests under `tests/test_mysql.py`, `tests/test_postgres.py`, and `tests/test_mongo.py` expect local MySQL / PostgreSQL / MongoDB and Meilisearch. Run them with:

```bash
make test-all
```

## Code style

- Python 3.10+, formatted by Ruff (line length 100)
- Type hints where they help; `ty` is the typechecker
- Keep PostgreSQL replication changes conservative: never skip LSN feedback, never drop the slot as a "fix"

## Pull requests

1. Branch from `dev`
2. Add a changelog note if the change is user-facing
3. Open a PR against `dev`

See [Publishing](publishing.md) for how releases are cut.
