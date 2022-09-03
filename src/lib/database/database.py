from typing import Any

import aioredis
from utils.decorators import singleton

import config


@singleton
class Database:
    def __init__(self):
        self._redis = aioredis.from_url(config.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> Any:
        return await self._redis.get(key)

    async def set(self, key: str, value: Any):
        return await self._redis.set(key, value)

