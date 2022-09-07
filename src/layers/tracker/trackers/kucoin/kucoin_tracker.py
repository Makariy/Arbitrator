from typing import List, Optional

import logging
from pydantic import BaseModel, validator

from layers.tracker.trackers.base_tracker import BaseTracker
from layers.tracker.services.websocket_services import recv_json, send_json
from layers.tracker.models import Bid, BidAsk

from lib.symbols import Symbols
from lib.exchanges import Exchanges
from lib.database import Database
from lib.database.key_manager import create_key
from .kucoin_authorizer import KuCoinAuthorizer


logger = logging.getLogger(__package__)
database = Database()


KuCoinSymbols = {
    Symbols.BTC: "BTC",
    Symbols.ETH: "ETH",
    Symbols.EUR: "EUR",
    Symbols.RUB: "RUB",
    Symbols.USDT: "USDT",
}


class KuCoinBidResponseData(BaseModel):
    """kucoin current best bid's response asks (Using this to parse the response)"""
    asks: List[BidAsk]
    timestamp: int

    @validator('asks', pre=True)
    def set_asks(value):
        asks = []
        for item in value:
            ask = BidAsk(price=item[0], count=item[1])
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
    subscription_id = None

    def __init__(self, input: Symbols, output: Symbols):
        self.input = input
        self.output = output
        self.authorizer = KuCoinAuthorizer()

    async def _get_acknowledgment(self) -> KuCoinAcknowledgment:
        response = await recv_json(self.connection)
        return KuCoinAcknowledgment(**response)

    async def _recv_bid(self) -> Bid:
        response = await recv_json(self.connection)
        bid_response = KuCoinBidResponse(**response)
        return Bid(
            input=KuCoinSymbols[self.input],
            output=KuCoinSymbols[self.output],
            bids=bid_response.data.asks
        )

    async def connect(self):
        self.connection = await self.authorizer.create_connection()
        self.subscription_id = await self.subscribe(
            f"/spotMarket/level2Depth50:{KuCoinSymbols[self.input]}-{KuCoinSymbols[self.output]}"
        )

    async def subscribe(self, url) -> str:
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

    async def save_bid_to_database(self, bid: Bid):
        key = create_key(self.EXCHANGE, self.input, self.output)
        await database.set(key, bid.json())

    async def start_tracking(self):
        try:
            while True:
                bid = await self._recv_bid()
                logger.info(f"Got bid for '{bid.input}' to '{bid.output}': '{bid.bids[0]}'")
                await self.save_bid_to_database(bid)

        except ConnectionError as error:
            logger.error(f"Server closed the connection: {error}")

        finally:
            if self.connection.open:
                await self.connection.close()
