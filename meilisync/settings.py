from typing import List

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings

from meilisync.enums import ProgressType, SourceType
from meilisync.plugin import load_plugin


class Source(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: SourceType
    database: str


class MeiliSearch(BaseModel):
    api_url: str
    api_key: str | None = None
    insert_size: int | None = None
    insert_interval: int | None = None


class BasePlugin(BaseModel):
    plugins: List[str] = []

    def plugins_cls(self):
        plugins = []
        for plugin in self.plugins or []:
            p = load_plugin(plugin)
            if p.is_global:
                plugins.append(p())
            else:
                plugins.append(p)
        return plugins


class Sync(BasePlugin):
    """One table (or collection) mapped to a Meilisearch index."""

    table: str
    pk: str = "id"
    full: bool = False
    index: str | None = None
    fields: dict | None = None

    @property
    def index_name(self):
        return self.index or self.table

    def __hash__(self):
        return hash(self.table)


class Progress(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: ProgressType


class Sentry(BaseModel):
    dsn: str
    environment: str = "production"


class Settings(BaseSettings, BasePlugin):
    """Root YAML configuration loaded at process start."""

    progress: Progress
    debug: bool = False
    source: Source
    meilisearch: MeiliSearch
    sync: List[Sync]
    sentry: Sentry | None = Field(default_factory=Sentry)

    @property
    def tables(self):
        return [sync.table for sync in self.sync]

    def get_sync(self, table: str) -> Sync | None:
        for sync in self.sync:
            if sync.table == table:
                return sync
