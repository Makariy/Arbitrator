from typing import Optional, Dict, List
import logging
import gzip
from pydantic import BaseModel, validator

from lib.symbols import Symbols
from lib.exchanges import Exchanges
from layers.tracker.models import TokenExchanges, TokenExchange, Token
from layers.tracker.services.websocket_services import create_connection, recv_json, send_json

from ..base_tracker import BaseTracker

import config


logger = logging.getLogger(__package__)


HUOBI_SYMBOLS = {
    Symbols.LUNA: "luna",
    Symbols.DOGE: "doge",
    Symbols.MIR: "mir",
    Symbols.USDT: "usdt",
    Symbols.BTC: "btc",
    Symbols.ETH: "eth",
    Symbols.EUR: "eur",
    Symbols.RUB: "rub",
}


class HuobiAcknowledgment(BaseModel):
    id: str
    status: str
    subbed: Optional[str]
    ts: int


class HuobiMarketDepthTickBid(BaseModel):
    price: float
    count: float


class HuobiMarketDepthTick(BaseModel):
    bids: List[HuobiMarketDepthTickBid]
    version: int
    timestamp: int

    @validator("bids", pre=True)
    def set_bids(value):
        bids = []
        for bid in value:
            bids.append(HuobiMarketDepthTickBid(price=bid[0], count=bid[1]))
        return bids

    class Config:
        fields = {
            "timestamp": "ts"
        }


class HuobiMarketDepthResponse(BaseModel):
    channel: str
    timestamp: int
    tick: HuobiMarketDepthTick

    class Config:
        fields = {
            "channel": "ch",
            "timestamp": "ts"
        }


class HuobiTracker(BaseTracker):
    EXCHANGE = Exchanges.huobi

    async def _recv_data(self):
        return await recv_json(self.connection, decompress_function=gzip.decompress)

    async def _get_acknowledgment(self) -> HuobiAcknowledgment:
        ack = await self._recv_data()
        return HuobiAcknowledgment(**ack)

    async def _convert_huobi_response_to_token_exchanges(self, response: HuobiMarketDepthResponse) -> TokenExchanges:
        token_exchanges = []
        for bid in response.tick.bids:
            token_exchange = TokenExchange(
                input=Token(price=1, symbol=self.input, exchange=self.EXCHANGE),
                output=Token(price=bid.price, symbol=self.output, exchange=self.EXCHANGE),
                count=bid.count,
                exchange=self.EXCHANGE
            )
            token_exchanges.append(token_exchange)
        return TokenExchanges(token_exchanges=token_exchanges)

    async def _dispatch_ping(self, ping: int):
        await send_json(self.connection, {'pong': ping})

    async def _dispatch_depth_response(self, response: HuobiMarketDepthResponse):
        token_exchanges = await self._convert_huobi_response_to_token_exchanges(response)
        logger.info(f"Got bid for {self.input} to {self.output}: {token_exchanges.token_exchanges[0]}")
        return await self.save_token_exchanges_to_database(token_exchanges)

    async def _handle_response(self, response: Dict):
        ping = response.get("ping")
        if ping is not None:
            return await self._dispatch_ping(ping)

        market_depth_response = HuobiMarketDepthResponse(**response)
        return await self._dispatch_depth_response(market_depth_response)

    async def connect(self):
        self.connection = await create_connection(config.HUOBI_BASE_WEBSOCKETS_URL)
        symbol = f"{HUOBI_SYMBOLS[self.input]}{HUOBI_SYMBOLS[self.output]}"
        await send_json(self.connection, {
            "sub": f"market.{symbol}.depth.step0",
            "id": "id1"
        })
        ack = await self._get_acknowledgment()
        logger.info(f"Got acknowledgment from server: {ack.id}")

    async def start_tracking(self):
        logger.info(f"Starting tracking from '{self.input}' to '{self.output}'")
        while True:
            data = await self._recv_data()
            await self._handle_response(data)
