# Progress

Progress is the CDC cursor: PostgreSQL LSN, MySQL binlog coordinates, or a MongoDB resume token. Without it, a restart would either replay events or skip them.

## File

```yaml
progress:
  type: file
  path: progress.json
```

Default path is `progress.json` in the working directory.

In Docker, put this on a volume:

```yaml
progress:
  type: file
  path: /app/data/progress.json
```

The file is overwritten as a JSON object, for example:

```json
{ "start_lsn": "33/E6BF38C8" }
```

## Redis

```yaml
progress:
  type: redis
  dsn: redis://localhost:6379/0
  key: meilisync:progress
```

Values are stored as a Redis hash at `key`. Use this when the process filesystem is ephemeral (Kubernetes without a PVC, Fargate, and so on).
