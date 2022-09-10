from typing import List, Optional, Dict

import logging
from pydantic import BaseModel, validator

from layers.tracker.trackers.base_tracker import BaseTracker
from layers.tracker.services.websocket_services import recv_json, send_json
from layers.tracker.models import TokenExchanges, TokenExchange, Token

from lib.symbols import Symbols
from lib.exchanges import Exchanges
from lib.database import Database
from .kucoin_authorizer import KuCoinAuthorizer
from .kucoin_ping_handler import KuCoinPingHandler


logger = logging.getLogger(__package__)
database = Database()


KuCoinSymbols = {
    Symbols.BTC: "BTC",
    Symbols.LUNA: "LUNA",
    Symbols.DOGE: "DOGE",
    Symbols.MIR: "MIR",
    Symbols.ETH: "ETH",
    Symbols.EUR: "EUR",
    Symbols.RUB: "RUB",
    Symbols.USDT: "USDT",
}


class KuCoinBidResponseDataAsk(BaseModel):
    price: float
    count: float


class KuCoinBidResponseData(BaseModel):
    """kucoin current best bid's response asks (Using this to parse the response)"""
    asks: List[KuCoinBidResponseDataAsk]
    timestamp: int

    @validator('asks', pre=True)
    def set_asks(value):
        asks = []
        for item in value:
            ask = KuCoinBidResponseDataAsk(price=item[0], count=item[1])
            asks.append(ask)
        return asks


class KuCoinBidResponse(BaseModel):
    """kucoin current best bid's response (Using this to parse the response)"""
    type: str
    topic: str
    subject: str
    data: KuCoinBidResponseData


class KuCoinAcknowledgment(BaseModel):
    id: str
    type: str
    code: Optional[int]
    topic: Optional[str]
    data: Optional[str]
    private_channel: Optional[bool]
    response: Optional[bool]

    class Config:
        fields = {
            "private_channel": "privateChannel"
        }


class KuCoinTracker(BaseTracker):
    EXCHANGE = Exchanges.kucoin

    authorizer = KuCoinAuthorizer()
    ping_handler = KuCoinPingHandler()
    subscription_id = None

    async def _get_acknowledgment(self) -> KuCoinAcknowledgment:
        response = await recv_json(self.connection)
        return KuCoinAcknowledgment(**response)

    async def _subscribe(self, url) -> str:
        subscription = {
            "id": self.authorizer.connection_id,
            "type": "subscribe",
            "topic": url,
            "privateChannel": False,
            "response": True
        }
        await send_json(self.connection, subscription)
        logger.info(f"Subscribed to the '{url}' on server")

        ack = await self._get_acknowledgment()
        if ack.type == "error":
            raise ValueError(f"Server responded with an error: {ack.code} - {ack.data}")

        return ack.id

    async def _send_ping(self):
        await send_json(self.connection, {"ping": self.subscription_id})
        response = await recv_json(self.connection)
        logger.info("Got pong from server: ", response)

    async def _convert_bid_to_token_exchanges(self, bid: KuCoinBidResponseData) -> TokenExchanges:
        token_exchanges = []
        for ask in bid.asks:
            token_exchange = TokenExchange(
                input=Token(price=1, symbol=self.input, exchange=self.EXCHANGE),
                output=Token(price=ask.price, symbol=self.output, exchange=self.EXCHANGE),
                count=ask.count,
                exchange=self.EXCHANGE
            )
            token_exchanges.append(token_exchange)
        return TokenExchanges(token_exchanges=token_exchanges)

    async def connect(self):
        self.connection = await self.authorizer.create_connection()
        self.subscription_id = await self._subscribe(
            f"/spotMarket/level2Depth50:{KuCoinSymbols[self.input]}-{KuCoinSymbols[self.output]}"
        )
        await self.ping_handler.set_connection(self.connection)

    async def _handle_bid(self, raw_bid: Dict):
        bid = KuCoinBidResponse(**raw_bid).data
        token_exchanges = await self._convert_bid_to_token_exchanges(bid)
        logger.info(f"Got bid for '{self.input}' to '{self.output}': '{token_exchanges.token_exchanges[0]}'")
        await self.save_token_exchanges_to_database(token_exchanges)

    async def _handle_message(self, message: Dict):
        type = message.get("type")
        if type == "error":
            logger.error(f"Got error in response: {message}")

        if type == "pong":
            return await self.ping_handler.handle_pong(message.get("id"))

        if type == "message":
            return await self._handle_bid(message)

    async def start_tracking(self):
        try:
            while True:
                if await self.ping_handler.is_time_to_ping():
                    await self.ping_handler.ping(self.subscription_id)

                response = await recv_json(self.connection)
                await self._handle_message(response)

        except ConnectionError as error:
            logger.error(f"Server closed the connection: {error}")

        finally:
            if self.connection.open:
                await self.connection.close()
