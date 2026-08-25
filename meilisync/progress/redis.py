from typing import Any

import redis.asyncio as redis

from meilisync.enums import ProgressType
from meilisync.progress import Progress


class Redis(Progress):
    type = ProgressType.redis

    def __init__(
        self,
        dsn: str = "redis://localhost:6379/0",
        key: str = "meilisync:progress",
    ):
        super().__init__(dsn=dsn, key=key)
        self.key = key
        self.redis: Any = redis.from_url(dsn, decode_responses=True)

    async def set(self, **kwargs):
        mapping = {str(key): str(value) for key, value in kwargs.items()}
        await self.redis.hset(self.key, mapping=mapping)

    async def get(self):
        return await self.redis.hgetall(self.key)
