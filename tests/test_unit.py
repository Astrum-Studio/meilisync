from datetime import date, datetime, timezone
from decimal import Decimal

from meilisync.enums import EventType, SourceType
from meilisync.schemas import Event
from meilisync.settings import Settings
from meilisync.source.postgres import Postgres
from meilisync.version import __VERSION__, __version__


def test_version_is_pep440_like():
    assert __version__
    assert __VERSION__ == __version__
    assert __version__[0].isdigit()


def test_settings_tables_and_index_name():
    settings = Settings.model_validate(
        {
            "progress": {"type": "file", "path": "progress.json"},
            "source": {
                "type": "postgres",
                "host": "localhost",
                "database": "app",
            },
            "meilisearch": {"api_url": "http://localhost:7700"},
            "sync": [
                {"table": "products", "full": True},
                {"table": "users", "index": "people", "pk": "uid"},
            ],
            "sentry": None,
        }
    )
    assert settings.source.type == SourceType.postgres
    assert settings.tables == ["products", "users"]
    products = settings.get_sync("products")
    users = settings.get_sync("users")
    assert products is not None
    assert users is not None
    assert products.index_name == "products"
    assert users.index_name == "people"
    assert settings.get_sync("missing") is None


def test_event_mapping_types_and_fields():
    event = Event(
        type=EventType.create,
        table="products",
        data={
            "id": 1,
            "title": "Widget",
            "created": datetime(1970, 1, 1, tzinfo=timezone.utc),
            "day": date(2026, 1, 2),
            "price": Decimal("9.50"),
            "skip_me": True,
        },
    )
    mapped = event.mapping_data(
        {"id": None, "title": "name", "created": None, "day": None, "price": None}
    )
    assert mapped["id"] == 1
    assert mapped["name"] == "Widget"
    assert mapped["created"] == 0
    assert mapped["day"] == "2026-01-02"
    assert mapped["price"] == 9.5
    assert "skip_me" not in mapped


def test_postgres_lsn_and_columns():
    assert Postgres._lsn_to_str(0) == "0/0"
    assert Postgres._lsn_to_str((0x33 << 32) | 0xE6BF38C8) == "33/E6BF38C8"
    assert Postgres._columns_to_dict(None) == {}
    payload = Postgres._columns_to_dict(
        [
            {"name": "id", "value": 1, "type": "int4"},
            {"name": "meta", "value": '{"a": 1}', "type": "jsonb"},
        ]
    )
    assert payload == {"id": 1, "meta": {"a": 1}}
