# Configuration

meilisync reads a YAML file. The default path is `config.yml` in the current working directory. Override it with `-c`:

```bash
meilisync -c /etc/meilisync/config.yml start
```

A commented template lives in [`config.example.yml`](https://github.com/Astrum-Studio/meilisync/blob/dev/config.example.yml).

## Full example

```yaml
debug: false
plugins:
  - meilisync.plugin.Plugin
progress:
  type: file
  path: progress.json
source:
  type: postgres
  host: 127.0.0.1
  port: 5432
  user: postgres
  password: "postgres"
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
      title: name
      description:
sentry:
  dsn: ""
  environment: production
```

## `debug`

Optional. Default `false`. When `true`, settings and every CDC event are logged at debug level.

## `plugins`

Optional list of `module.Class` paths. Each class must implement `pre_event` / `post_event`. See [Plugins](plugins.md).

## `progress`

Where the last sync position is stored.

| Key | Description |
| --- | --- |
| `type` | `file` or `redis` |
| `path` | File backend: JSON path. Default `progress.json` |
| `dsn` | Redis backend: connection URL. Default `redis://localhost:6379/0` |
| `key` | Redis backend: hash key. Default `meilisync:progress` |

See [Progress](progress.md).

## `source`

Source database. Extra keys are passed through to the driver.

| Key | Description |
| --- | --- |
| `type` | `postgres`, `mysql`, or `mongo` |
| `database` | Database (or MongoDB database) name |
| `host`, `port`, `user`, `password`, … | Driver connection arguments |

- PostgreSQL: [psycopg2](https://www.psycopg.org/docs/usage.html) plus logical replication. Details: [PostgreSQL](sources/postgres.md).
- MySQL: [asyncmy](https://github.com/long2ice/asyncmy). `server_id` defaults to `1`. Details: [MySQL](sources/mysql.md).
- MongoDB: [motor](https://motor.readthedocs.io/en/stable/). Replica set is required. Details: [MongoDB](sources/mongodb.md).

## `meilisearch`

| Key | Description |
| --- | --- |
| `api_url` | Meilisearch URL, e.g. `http://127.0.0.1:7700` |
| `api_key` | API key, optional for an unsecured local instance |
| `insert_size` | Flush the batch when this many documents are queued |
| `insert_interval` | Flush the batch every N seconds |

If **neither** `insert_size` nor `insert_interval` is set, each event is written immediately.

If you care about throughput, set both. A flush happens when **either** threshold is hit.

## `sync`

A list of table → index mappings. You can sync many tables from one source.

| Key | Description |
| --- | --- |
| `table` | Table or collection name |
| `index` | Meilisearch index. Defaults to `table` |
| `pk` | Primary key field. Default `id` |
| `full` | If `true`, run a full copy when the index does not exist. Default `false` |
| `fields` | Optional column map. Key is the source column; value is the Meilisearch field name (or empty to keep the same name). Omit `fields` to copy every column |
| `plugins` | Optional per-table plugin list |

## `sentry`

Optional.

| Key | Description |
| --- | --- |
| `dsn` | Sentry DSN |
| `environment` | Sentry environment. Default `production` |

Requires `pip install meilisync[sentry]`.
