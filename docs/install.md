# Installation

meilisync is a Python package. Database drivers are extras so you only pull what you need.

## Python package

Requires Python 3.10 or newer.

=== "uv"

    ```bash
    uv pip install "meilisync[postgres]"
    uv pip install "meilisync[mysql]"
    uv pip install "meilisync[mongodb]"
    uv pip install "meilisync[all]"
    ```

=== "pip"

    ```bash
    pip install "meilisync[postgres]"
    pip install "meilisync[mysql]"
    pip install "meilisync[mongodb]"
    pip install "meilisync[all]"
    ```

=== "pipx"

    ```bash
    pipx install "meilisync[all]"
    ```

| Extra | Installs | Needed for |
| --- | --- | --- |
| `postgres` | `psycopg2-binary` | PostgreSQL source (also a core dependency today) |
| `mysql` | `asyncmy` | MySQL binlog source |
| `mongodb` / `mongo` | `motor` | MongoDB change streams |
| `redis` | `redis` | Redis progress backend (also a core dependency today) |
| `sentry` | `sentry-sdk` | Sentry error reporting |
| `all` | everything above | One image / one install |

`postgres` and `redis` are currently included in the base install as well, so `pip install meilisync` is enough for PostgreSQL + file or Redis progress.

## Docker

Images are published to GitHub Container Registry on every `dev`/`main` push and on version tags:

```bash
docker pull ghcr.io/astrum-studio/meilisync:latest
```

See [Docker](docker.md) for compose files, tags, and volume layout.

## From source

```bash
git clone https://github.com/Astrum-Studio/meilisync.git
cd meilisync
uv sync --all-extras --group dev
uv run meilisync --help
```

The project is built with [uv](https://docs.astral.sh/uv/) and [hatchling](https://hatch.pypa.io/).
