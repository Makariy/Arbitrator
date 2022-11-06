import logging
from typing import Dict
import time
import asyncio
from websockets import WebSocketClientProtocol
from layers.tracker.services.websocket_services import send_json


PING_PERIOD = 3  # Seconds


logger = logging.getLogger(__package__)


class KuCoinPinger:
    _last_ping: float
    _connection: WebSocketClientProtocol
    _subscription_id: str

    def __init__(self, connection: WebSocketClientProtocol, subscription_id: str):
        self._connection = connection
        self._subscription_id = subscription_id
        self._last_ping = time.time()

    async def _is_time_to_ping(self) -> bool:
        now = time.time()
        if now - self._last_ping > PING_PERIOD:
            return True
        return False

    async def _reset_time_to_ping(self):
        self._last_ping = time.time()

    async def handle_pong(self, pong: Dict):
        pass

    async def ping(self):
        await send_json(self._connection, {"type": "ping", "id": self._subscription_id})

    async def start_pinging(self):
        while True:
            if await self._is_time_to_ping():
                await self.ping()
                await self._reset_time_to_ping()
            await asyncio.sleep(PING_PERIOD / 10)
