from typing import Coroutine, Callable, List, Any

import aioredis
import asyncio
import async_timeout
from utils.decorators import singleton

import config


async def try_wait(function: Coroutine, _timeout: float = 0.5):
    try:
        return await asyncio.wait_for(function, timeout=_timeout)

    except asyncio.TimeoutError:
        return None

@singleton
class Database:
    def __init__(self):
        self._redis = aioredis.from_url(config.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> str:
        return await self._redis.get(key)

    async def mget(self, keys: List[str]):
        return await self._redis.mget(keys)

    async def set(self, key: str, value: str):
        return await self._redis.set(key, value)

    async def keys(self, pattern: str) -> List[str]:
        return await self._redis.keys(pattern)

    async def _handle_publish(self, receiver: aioredis.client.PubSub, callback: Callable[[Any], Coroutine]):
        while True:
            message = await receiver.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message is None:
                continue
            await callback(message)

    async def subscribe(self, pattern: str, callback: Callable[[Any], Coroutine]):
        subscription = self._redis.pubsub()
        await subscription.subscribe(pattern)
        await self._handle_publish(subscription, callback)
        return subscription

    async def publish(self, pattern: str, data: Any):
        await self._redis.publish(pattern, data)


