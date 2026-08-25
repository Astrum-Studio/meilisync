# Contributing

Please read the [contributing guide](https://astrum-studio.github.io/meilisync/contributing/) in the docs.

Short version:

```bash
uv sync --all-extras --group dev --group docs
make ci
make docs-serve
uv run pre-commit install
```

- Default branch is `dev`
- Unit tests: `make test` (no databases required)
- Hooks (ruff format, ruff check --fix, ty, pytest) run on every commit
- User-facing changes need a `CHANGELOG.md` note
