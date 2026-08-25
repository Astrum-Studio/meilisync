# Getting started

This guide runs meilisync against PostgreSQL and a local Meilisearch.

<div class="doc-hero" markdown="1">

# From zero to a live index

Install the package, write `config.yml`, start CDC. PostgreSQL is the example source — MySQL and MongoDB work the same way once extras are installed.

</div>

## Checklist

<ol class="doc-steps" markdown="1">
<li>Install <code>meilisync[postgres]</code> (or the extra for your source)</li>
<li>Copy <code>config.example.yml</code> to <code>config.yml</code> and fill in credentials</li>
<li>Run <code>meilisync start</code> and watch the first full sync, then CDC</li>
<li>Use <code>meilisync check</code> to compare source counts with Meilisearch</li>
</ol>

## Prerequisites

- Python 3.10+ or Docker
- A Meilisearch instance
- A source database (this example uses PostgreSQL)

PostgreSQL must have logical replication enabled and the `wal2json` plugin installed. See [PostgreSQL](sources/postgres.md).

## Install

```bash
pip install "meilisync[postgres]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install "meilisync[postgres]"
```

## Write `config.yml`

```yaml
debug: false
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
    fields:
      id:
      name:
      description:
```

Place the file in the working directory, or pass `-c /path/to/config.yml`.

## Start

```bash
meilisync start
```

On first start, tables with `full: true` are copied if the Meilisearch index does not exist. Incremental replication then follows WAL changes.

## Useful commands

| Command | What it does |
| --- | --- |
| `meilisync start` | Full sync (if needed) + incremental CDC |
| `meilisync refresh -t products` | Rebuild an index via a tmp index + swap |
| `meilisync check -t products` | Compare source row count vs Meilisearch |
| `meilisync version` | Print the installed version |

!!! warning "Stop CDC before refresh"
    Run `refresh` only while `start` is stopped, otherwise writes can race the swap.

Next: [configuration reference](configuration.md) and [CLI](cli.md).
