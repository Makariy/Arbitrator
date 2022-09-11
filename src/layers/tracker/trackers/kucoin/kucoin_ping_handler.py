from typing import Dict
import time
from websockets import WebSocketClientProtocol
from layers.tracker.services.websocket_services import send_json


PING_PERIOD = 3  # Seconds


class KuCoinPingHandler:
    last_ping: float = time.time()
    connection: WebSocketClientProtocol = None

    async def set_connection(self, connection: WebSocketClientProtocol):
        self.connection = connection

    async def is_time_to_ping(self) -> bool:
        now = time.time()
        if now - self.last_ping > PING_PERIOD:
            self.last_ping = now
            return True
        return False

    async def handle_pong(self, pong: Dict):
        pass

    async def ping(self, subscription_id: str):
        await send_json(self.connection, {"type": "ping", "id": subscription_id})
