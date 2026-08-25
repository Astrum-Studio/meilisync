from typing import Type

from meilisync.enums import ProgressType, SourceType
from meilisync.progress import Progress
from meilisync.source import Source


def get_source(type_: SourceType) -> Type[Source]:
    if type_ == SourceType.mysql:
        from meilisync.source.mysql import MySQL

        return MySQL
    if type_ == SourceType.postgres:
        from meilisync.source.postgres import Postgres

        return Postgres
    if type_ == SourceType.mongo:
        from meilisync.source.mongo import Mongo

        return Mongo
    raise ValueError(f"Invalid source type: {type_}")


def get_progress(type_: ProgressType) -> Type[Progress]:
    if type_ == ProgressType.file:
        from meilisync.progress.file import File

        return File
    if type_ == ProgressType.redis:
        from meilisync.progress.redis import Redis

        return Redis
    raise ValueError(f"Invalid progress type: {type_}")
