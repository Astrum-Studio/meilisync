# meilisync

**Realtime sync from PostgreSQL, MySQL, and MongoDB to [Meilisearch](https://www.meilisearch.com/).**

[![CI](https://github.com/Astrum-Studio/meilisync/actions/workflows/ci.yml/badge.svg)](https://github.com/Astrum-Studio/meilisync/actions/workflows/ci.yml)
[![Docker](https://github.com/Astrum-Studio/meilisync/actions/workflows/docker.yml/badge.svg)](https://github.com/Astrum-Studio/meilisync/actions/workflows/docker.yml)
[![Docs](https://github.com/Astrum-Studio/meilisync/actions/workflows/docs.yml/badge.svg)](https://astrum-studio.github.io/meilisync/)
[![PyPI](https://img.shields.io/pypi/v/meilisync.svg)](https://pypi.org/project/meilisync/)
[![Python](https://img.shields.io/pypi/pyversions/meilisync.svg)](https://pypi.org/project/meilisync/)
[![License](https://img.shields.io/github/license/Astrum-Studio/meilisync)](LICENSE)

A maintained fork of [long2ice/meilisync](https://github.com/long2ice/meilisync) by [Astrum Agency](https://astrum.agency). Built for production PostgreSQL: wal2json format 2 (no 1 GB string-buffer crash), table-filtered decoding, and automatic reconnect with LSN resume.

**[Documentation](https://astrum-studio.github.io/meilisync/)** · **[astrum.agency](https://astrum.agency)** · **[Changelog](CHANGELOG.md)** · **[Docker image](https://github.com/Astrum-Studio/meilisync/pkgs/container/meilisync)**

---

## Features

- **CDC, not polling** — PostgreSQL logical replication, MySQL binlog, MongoDB change streams
- **Full + incremental** — optional backfill when an index is missing, then live updates
- **Batching** — flush by document count, interval, or both
- **Index refresh** — rebuild via a tmp index and atomic swap
- **Plugins** — mutate events before/after they hit Meilisearch
- **Progress** — file or Redis, so restarts continue from the last cursor

## Install

```bash
pip install "meilisync[postgres]"   # PostgreSQL (also the default extra)
pip install "meilisync[mysql]"      # MySQL
pip install "meilisync[mongodb]"    # MongoDB
pip install "meilisync[all]"        # everything
```

Or Docker:

```bash
docker pull ghcr.io/astrum-studio/meilisync:latest
```

## Quick start

```yaml
# config.yml
progress:
  type: file
  path: progress.json
source:
  type: postgres
  host: 127.0.0.1
  port: 5432
  user: postgres
  password: postgres
  database: app
meilisearch:
  api_url: http://127.0.0.1:7700
  api_key: MASTER_KEY
  insert_size: 1000
  insert_interval: 5
sync:
  - table: products
    index: products
    pk: id
    full: true
```

```bash
meilisync start
```

```yaml
# docker-compose.yml
services:
  meilisync:
    image: ghcr.io/astrum-studio/meilisync:latest
    restart: unless-stopped
    volumes:
      - ./config.yml:/app/config.yml:ro
      - ./data:/app/data
```

Full configuration, source setup, and CLI: **[docs](https://astrum-studio.github.io/meilisync/)**.

## Commands

| Command | Purpose |
| --- | --- |
| `meilisync start` | Full sync (if needed) + incremental CDC |
| `meilisync refresh -t TABLE` | Rebuild an index via swap |
| `meilisync check -t TABLE` | Compare source count vs Meilisearch |
| `meilisync version` | Print version |

## Development

This repo uses **uv** for environments/lockfile and **hatchling** as the build backend.

```bash
uv sync --all-extras --group dev --group docs
make ci          # lint, typecheck, unit tests
make docs-serve  # MkDocs Material
uv build         # sdist + wheel
```

Releases are Git tags (`vX.Y.Z`): PyPI via trusted publishing, GHCR image, GitHub Release. See [Publishing](https://astrum-studio.github.io/meilisync/publishing/).

## License

[Apache-2.0](LICENSE). See [NOTICE](NOTICE) for attribution to the original project.
