# PostgreSQL

meilisync uses logical replication with the [`wal2json`](https://github.com/eulerto/wal2json) output plugin.

This fork is tuned for production WAL traffic:

- **format-version 2** — one JSON object per change, so a huge transaction is not buffered as a single ~1 GB string
- **`add-tables`** — only configured tables are decoded
- **Reconnect** — dropped connections resume from the last LSN with exponential backoff (1s → 30s)
- **Keepalives** every 5 seconds while idle, so a dead TCP session is noticed

## Server settings

```ini
wal_level = logical
max_replication_slots = 4
max_wal_senders = 4
```

Reload or restart PostgreSQL after changing `wal_level`.

Install `wal2json` (package name varies):

```bash
# Debian / Ubuntu
apt install postgresql-16-wal2json

# Check
psql -c "SELECT * FROM pg_available_extensions WHERE name = 'wal2json';"
```

The role used by meilisync needs `REPLICATION` and `LOGIN`, plus `SELECT` on the synced tables:

```sql
CREATE ROLE meilisync WITH LOGIN REPLICATION PASSWORD 'secret';
GRANT CONNECT ON DATABASE app TO meilisync;
GRANT USAGE ON SCHEMA public TO meilisync;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO meilisync;
```

## Config

```yaml
source:
  type: postgres
  host: 127.0.0.1
  port: 5432
  user: meilisync
  password: secret
  database: app
```

Any extra keys are passed to `psycopg2.connect`.

## Replication slot

The slot name is **`meilisync`** (hardcoded). It is created on first start if it does not exist:

```sql
SELECT slot_name, plugin, active, restart_lsn
FROM pg_replication_slots
WHERE slot_name = 'meilisync';
```

!!! warning "One consumer per slot"
    Do not run two meilisync processes against the same slot. PostgreSQL allows only one active reader. Use a different database, or fork the code / run a second slot, if you need two consumers.

!!! danger "Do not drop a live slot carelessly"
    Dropping `meilisync` forces a new slot from the current WAL position and **skips** changes that happened in between. Prefer `refresh` after a slot rebuild.

## JSON / JSONB

`json` and `jsonb` columns are parsed into Python objects (and then JSON for Meilisearch) instead of being left as strings.

## Large transactions

Upstream format version 1 assembled a whole transaction into one JSON document. PostgreSQL then failed with:

```text
string buffer exceeds maximum allowed length (1073741823 bytes)
```

and the client sat on the same LSN reconnecting forever. Format version 2 streams one change at a time, which is what this fork uses.
