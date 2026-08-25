# CLI

```bash
meilisync [OPTIONS] COMMAND
```

## Global options

| Option | Default | Description |
| --- | --- | --- |
| `-c`, `--config` | `config.yml` | Path to the YAML config |
| `--install-completion` | | Install shell completion |
| `--show-completion` | | Print completion script |
| `--help` | | Show help |

All commands except `version` load and validate the config file first.

## `meilisync start`

Start CDC.

1. For each `sync` entry with `full: true`, if the Meilisearch index does not exist, copy the table in pages of `insert_size` (or 10 000).
2. Tail the source and apply create / update / delete events.
3. Persist progress after successful writes.

```bash
meilisync start
meilisync -c /etc/meilisync.yml start
```

## `meilisync refresh`

Rebuild indexes by filling a temporary index, swapping it with the live one, then deleting the temp index. Settings are copied from the existing index.

```bash
meilisync refresh
meilisync refresh -t products -t users
meilisync refresh -t products -s 5000
```

| Option | Default | Description |
| --- | --- | --- |
| `-t`, `--table` | all tables | Limit to these source tables |
| `-s`, `--size` | `10000` | Page size for the full copy |

!!! warning
    Stop `meilisync start` before running `refresh`, otherwise incremental writes can interleave with the swap.

## `meilisync check`

Compare `COUNT(*)` (or collection count) on the source with the number of documents in Meilisearch.

```bash
meilisync check
meilisync check -t products
```

This is a count check, not a document-by-document diff.

## `meilisync version`

Print the package version. Does not require a config file.

```bash
meilisync version
```
