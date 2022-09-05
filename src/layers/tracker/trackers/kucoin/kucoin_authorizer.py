from typing import Optional, Tuple
import logging

import aiohttp
from websockets import WebSocketClientProtocol
from layers.tracker.services.websocket_services import create_connection, recv_json

import config


logger = logging.getLogger(__package__)


KUCOIN_TOKEN = str


class KuCoinAuthorizer:
    token: KUCOIN_TOKEN = None
    endpoint_url = None
    connection_id: KUCOIN_TOKEN = None

    async def _authorize_on_server(self) -> Tuple[KUCOIN_TOKEN, str]:
        """Authorizes on the server, and returns the token and the endpoint server url"""
        async with aiohttp.ClientSession() as session:
            response = await session.post(f"{config.KUCOIN_BASE_HTTP_URL}/api/v1/bullet-public")
        data = await response.json()
        token = data.get("data").get('token')
        instance_url = data.get("data").get("instanceServers")[0].get("endpoint")
        logger.info(f"Got the token from server: {token[:10]}...{token[len(token) - 10:]}")
        return token, instance_url

    async def _get_connection_id(self, connection) -> str:
        response = await recv_json(connection)
        connection_id = response.get("id")
        if connection_id is None:
            raise ConnectionError(f"Server refused to send the subscription_id")
        return connection_id

    async def _create_connection(self) -> WebSocketClientProtocol:
        connection = await create_connection(f"wss://ws-api.kucoin.com/endpoint?token={self.token}")
        if connection is None:
            raise ConnectionResetError(f"Server refused to accept the connection")
        logger.info(f"Created the connection with server: {connection}")
        self.connection_id = await self._get_connection_id(connection)
        logger.info(f"Got the connection id: {self.connection_id}")
        return connection

    async def create_connection(self) -> WebSocketClientProtocol:
        self.token, self.endpoint_url = await self._authorize_on_server()
        return await self._create_connection()

