import asyncio
import json
import select
import threading
from asyncio import Queue
from typing import Any, List, Optional

try:
    import psycopg2
    import psycopg2.errors
    from psycopg2._psycopg import ReplicationMessage
    from psycopg2.extras import LogicalReplicationConnection
except ImportError as e:
    raise ImportError("psycopg2 is not installed to use PostgreSQL source") from e

from loguru import logger

from meilisync.enums import EventType, SourceType
from meilisync.schemas import Event, ProgressEvent
from meilisync.settings import Sync
from meilisync.source import Source

# Seconds to wait for a replication message before sending a keepalive to the
# server, so dead connections are detected instead of hanging forever.
REPLICATION_IDLE_TIMEOUT = 5
# Delay before the first reconnect attempt and the maximum delay between
# attempts (exponential backoff).
RECONNECT_MIN_DELAY = 1
RECONNECT_MAX_DELAY = 30


class CustomDictRow(psycopg2.extras.RealDictRow):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError as exc:
            if isinstance(key, int):
                return super().__getitem__(list(self.keys())[key])
            raise exc


class CustomDictCursor(psycopg2.extras.RealDictCursor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs["row_factory"] = CustomDictRow
        self.row_factory = CustomDictRow


class Postgres(Source):
    type = SourceType.postgres
    slot = "meilisync"

    # Populated by _connect() / __aiter__(); typed loosely because the
    # psycopg2 API is dynamic.
    conn: Any
    cursor: Any
    conn_dict: Any
    queue: Any
    _loop: Any

    def __init__(
        self,
        progress: dict,
        tables: List[str],
        **kwargs,
    ):
        super().__init__(progress, tables, **kwargs)
        self._stop_event = threading.Event()
        self.start_lsn: Optional[str] = (
            self.progress["start_lsn"] if self.progress else None
        )
        self._connect()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------
    def _connect(self):
        """Create a fresh pair of connections (replication + regular)."""
        self.conn = psycopg2.connect(
            **self.kwargs, connection_factory=LogicalReplicationConnection
        )
        self.cursor = self.conn.cursor()
        if self.start_lsn is None:
            self.cursor.execute("SELECT pg_current_wal_lsn()")
            row = self.cursor.fetchone()
            self.start_lsn = row[0] if row else "0/0"
        self.conn_dict = psycopg2.connect(**self.kwargs, cursor_factory=CustomDictCursor)

    @staticmethod
    def _close_quietly(obj):
        try:
            if obj is not None:
                obj.close()
        except Exception:
            pass

    def reconnect(self):
        """Close all existing connections and establish new ones."""
        logger.info('Reconnecting to PostgreSQL host "{}"...', self.kwargs.get("host"))
        self._close_quietly(self.cursor)
        self._close_quietly(self.conn)
        self._close_quietly(self.conn_dict)
        self._connect()
        logger.info("Reconnected to PostgreSQL")

    # ------------------------------------------------------------------
    # Data helpers (with reconnect on failure)
    # ------------------------------------------------------------------
    async def get_current_progress(self):
        sql = "SELECT pg_current_wal_lsn()"

        def _():
            try:
                with self.conn.cursor() as cur:
                    cur.execute(sql)
                    return cur.fetchone()[0]
            except psycopg2.Error:
                self.reconnect()
                with self.conn.cursor() as cur:
                    cur.execute(sql)
                    return cur.fetchone()[0]

        start_lsn = await asyncio.get_event_loop().run_in_executor(None, _)
        return {"start_lsn": start_lsn}

    async def get_full_data(self, sync: Sync, size: int):
        if sync.fields:
            fields = ", ".join(f"{field} as {sync.fields[field] or field}" for field in sync.fields)
        else:
            fields = "*"
        offset = 0

        while True:
            ret = await asyncio.get_event_loop().run_in_executor(
                None, self._fetch_full_data_page, sync.table, sync.pk, fields, size, offset
            )
            if not ret:
                break
            offset += size
            yield ret

    def _fetch_full_data_page(self, table: str, pk: str, fields: str, size: int, offset: int):
        sql = f"SELECT {fields} FROM {table} ORDER BY {pk} LIMIT {size} OFFSET {offset}"
        try:
            return self._execute_dict(sql)
        except psycopg2.Error:
            self.reconnect()
            return self._execute_dict(sql)

    def _execute_dict(self, sql: str):
        with self.conn_dict.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    # ------------------------------------------------------------------
    # Replication stream
    # ------------------------------------------------------------------
    @staticmethod
    def _lsn_to_str(lsn: int) -> str:
        """Convert a numeric WAL LSN to the PostgreSQL text form (e.g. ``0/16B3748``)."""
        return f"{lsn >> 32:X}/{lsn & 0xFFFFFFFF:X}"

    @staticmethod
    def _columns_to_dict(columns: list[dict[str, Any]] | None) -> dict[str, Any]:
        if not columns:
            return {}
        values: dict[str, Any] = {}
        for col in columns:
            name = col["name"]
            value = col.get("value")
            # Format 2 usually embeds json/jsonb as native JSON; fall back to
            # parsing when the plugin still emits a string.
            if col.get("type") in ("json", "jsonb") and isinstance(value, str):
                value = json.loads(value)
            values[name] = value
        return values

    def _consumer(self, msg: ReplicationMessage):
        """
        Handle one wal2json format-version 2 message.

        Format 2 emits one JSON object per change (instead of buffering a whole
        transaction into a single string). That avoids PostgreSQL's ~1GB
        MaxAllocSize failure on large transactions:
        ``string buffer exceeds maximum allowed length``.
        """
        payload = json.loads(msg.payload)
        next_lsn = payload.get("nextlsn") or self._lsn_to_str(msg.data_start)
        action = payload.get("action")

        # Begin / commit / logical messages: advance the slot only.
        if action in ("B", "C", "M", "T"):
            pass
        elif action in ("I", "U", "D"):
            self.__handle_change(payload, next_lsn)

        # Always report success to the server to avoid a “disk full” condition.
        # https://www.psycopg.org/docs/extras.html#psycopg2.extras.ReplicationCursor.consume_stream
        msg.cursor.send_feedback(flush_lsn=msg.data_start)
        # Remember the position so replication can resume from here after a
        # reconnect without losing or replaying events.
        self.start_lsn = next_lsn

    def __handle_change(self, change: dict[str, Any], next_lsn: str):
        table = change.get("table")
        if table not in self.tables:
            return

        action = change.get("action")
        if action == "U":
            values = self._columns_to_dict(change.get("columns"))
            event_type = EventType.update
        elif action == "D":
            values = self._columns_to_dict(
                change.get("columns") or change.get("identity")
            )
            event_type = EventType.delete
        elif action == "I":
            values = self._columns_to_dict(change.get("columns"))
            event_type = EventType.create
        else:
            return

        if not values:
            return

        asyncio.run_coroutine_threadsafe(
            self.queue.put(
                Event(
                    type=event_type,
                    table=table,
                    data=values,
                    progress={"start_lsn": next_lsn},
                )
            ),
            self._loop,
        ).result()

    def _start_replication(self):
        # Restrict decoding to synced tables and use format 2 so each change is
        # a standalone JSON object. Format 1 builds one giant JSON string per
        # transaction and hits PostgreSQL's ~1GB string-buffer limit on bulk
        # writes (``string buffer exceeds maximum allowed length``).
        add_tables = ",".join(f"*.{table}" for table in self.tables)
        self.cursor.start_replication(
            slot_name=self.slot,
            decode=True,
            status_interval=1,
            # psycopg2 accepts both str and int LSNs at runtime.
            start_lsn=self.start_lsn,  # type: ignore[arg-type]
            options={
                "format-version": "2",
                "include-lsn": "true",
                "include-transaction": "false",
                "add-tables": add_tables,
            },
        )

    def _stream_once(self):
        """Consume the replication stream until the connection breaks."""
        conn = self.conn
        while not self._stop_event.is_set():
            msg = self.cursor.read_message()
            if msg is not None:
                self._consumer(msg)
                continue
            # Nothing to read right now: wait for data or until the idle
            # timeout expires, then send a keepalive to detect dead
            # connections early instead of blocking forever.
            ready, _, _ = select.select([conn], [], [], REPLICATION_IDLE_TIMEOUT)
            if not ready:
                self.cursor.send_feedback(reply=True)

    def _consume_stream(self):
        """
        Blocking replication loop executed in a worker thread.

        Keeps the stream alive forever: whenever the connection breaks
        (network failure, PostgreSQL restart, ...) it transparently
        reconnects with exponential backoff and resumes replication from
        the last known LSN.
        """
        delay = RECONNECT_MIN_DELAY
        while not self._stop_event.is_set():
            try:
                self._stream_once()
                if not self._stop_event.is_set():
                    logger.warning("Replication stream ended, reconnecting...")
            except Exception as e:
                if self._stop_event.is_set():
                    break
                logger.warning(f'Replication stream interrupted: "{e}", reconnecting...')
            if self._stop_event.is_set():
                break
            while not self._stop_event.is_set():
                if self._stop_event.wait(delay):
                    return
                try:
                    self.reconnect()
                    self._start_replication()
                    delay = RECONNECT_MIN_DELAY
                    break
                except Exception as e:
                    logger.error(
                        f'Failed to reconnect to PostgreSQL: "{e}", '
                        f"retrying in {delay} seconds..."
                    )
                    delay = min(delay * 2, RECONNECT_MAX_DELAY)

    async def __aiter__(self):
        self.queue = Queue()
        self._loop = asyncio.get_event_loop()
        self._stop_event.clear()
        try:
            self.cursor.create_replication_slot(self.slot, output_plugin="wal2json")
        except psycopg2.errors.DuplicateObject:  # type: ignore
            pass
        self._start_replication()
        asyncio.ensure_future(
            self._loop.run_in_executor(None, self._consume_stream)
        )
        yield ProgressEvent(
            progress={"start_lsn": self.start_lsn},
        )
        while True:
            yield await self.queue.get()

    # ------------------------------------------------------------------
    # Health check & cleanup
    # ------------------------------------------------------------------
    def _ping(self):
        try:
            with self.conn_dict.cursor() as cur:
                cur.execute("SELECT 1")
        except psycopg2.Error:
            self.reconnect()
            with self.conn_dict.cursor() as cur:
                cur.execute("SELECT 1")

    async def ping(self):
        await asyncio.get_event_loop().run_in_executor(None, self._ping)

    async def get_count(self, sync: Sync):
        sql = f"SELECT COUNT(*) FROM {sync.table}"

        def _():
            try:
                with self.conn_dict.cursor() as cur:
                    cur.execute(sql)
                    return cur.fetchone()[0]
            except psycopg2.Error:
                self.reconnect()
                with self.conn_dict.cursor() as cur:
                    cur.execute(sql)
                    return cur.fetchone()[0]

        return await asyncio.get_event_loop().run_in_executor(None, _)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._stop_event.set()
        self._close_quietly(self.cursor)
        self._close_quietly(self.conn)
        self._close_quietly(self.conn_dict)