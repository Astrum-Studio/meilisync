# Changelog

## 0.1.5

### PostgreSQL: fix wal2json 1GB string-buffer crash on large transactions

- Switched the replication stream to wal2json **format-version 2** (one JSON
  object per change) so bulk transactions no longer hit PostgreSQL's
  `string buffer exceeds maximum allowed length (~1GB)` error and get stuck
  reconnecting on the same LSN.
- Pass `add-tables` so only configured sync tables are decoded, cutting
  unrelated WAL noise and payload size.

## 0.1.4

### PostgreSQL: automatic reconnect on connection loss

- The replication stream now survives PostgreSQL restarts and network
  interruptions. When the connection breaks, meilisync transparently
  reconnects with exponential backoff (1s → 30s) and resumes replication from
  the last acknowledged LSN, so no events are lost or replayed.
- Idle keepalives are sent every 5 seconds while waiting for replication
  messages, so dead connections are detected quickly instead of hanging.
- All regular queries (`get_full_data`, `get_count`, `ping`,
  `get_current_progress`) retry once on a fresh connection if the existing one
  has dropped.

## 0.1.3

- Initial fork release.