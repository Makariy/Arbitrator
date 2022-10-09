from typing import List, Dict

from websockets import WebSocketClientProtocol
from pydantic import BaseModel, validator

from lib.symbols import Symbols
from lib.exchanges import Exchanges, ToTrack
from lib.token import TokenExchanges, TokenExchange, Token
from layers.tracker.services.websocket_services import create_connection, send_json, recv_json
from layers.tracker.trackers.base import BaseTracker, BaseDispatcher

import logging
import config


logger = logging.getLogger(__package__)


BINANCE_SYMBOLS = {
    Symbols.USDT: "usdt",
    Symbols.LUNA: "luna",
    Symbols.MIR: "mir",
    Symbols.SOL: "sol",
    Symbols.SHIB: "shib",
    Symbols.AVAX: "avax",
    Symbols.ATOM: "atom",
    Symbols.EOS: "eos",
    Symbols.XRP: "xrp",
    Symbols.WAVES: "waves",

    Symbols.DOGE: "doge",
    Symbols.BTC: "btc",
    Symbols.ETH: "eth",
    Symbols.EUR: "eur",
    Symbols.RUB: "rub",
}


class BinanceBid(BaseModel):
    price: float
    count: float


class BinanceBidResponse(BaseModel):
    event_type: str
    event_time: int
    symbol: str
    first_update_id: int
    final_update_id: int
    bids: List[BinanceBid]
    asks: List[BinanceBid]

    @staticmethod
    def _parse_bids(value: List[List[int]]):
        result = []
        for bid in value:
            result.append(BinanceBid(price=bid[0], count=bid[1]))
        return result

    @validator("bids", pre=True)
    def set_bids(value: List[List[int]]):
        return BinanceBidResponse._parse_bids(value)

    @validator("asks", pre=True)
    def set_asks(value: List[List[int]]):
        return BinanceBidResponse._parse_bids(value)

    class Config:
        fields = {
            "event_type": "e",
            "event_time": "E",
            "symbol": "s",
            "first_update_id": "U",
            "final_update_id": "u",
            "bids": "b",
            "asks": "a"
        }


class BinanceDispatcher(BaseDispatcher):
    ID: int
    EXCHANGE = Exchanges.binance

    async def init(self, _id: int):
        self.ID = _id

    async def get_symbol(self) -> str:
        input = BINANCE_SYMBOLS[self.input]
        output = BINANCE_SYMBOLS[self.output]
        return f"{input}{output}"

    async def subscribe(self, connection: WebSocketClientProtocol):
        symbol = await self.get_symbol()
        self.channel = f"{symbol}@depth"

    async def get_channel_name(self) -> str:
        return self.channel

    async def _convert_binance_response_to_token_exchanges(self, response: BinanceBidResponse) -> TokenExchanges:
        token_exchanges = []
        for bid in filter(lambda a: not a.count <= 0, response.bids):
            token_exchange = TokenExchange(
                input=Token(price=1, symbol=self.input, exchange=self.EXCHANGE),
                output=Token(price=bid.price, symbol=self.output, exchange=self.EXCHANGE),
                count=bid.count,
                exchange=self.EXCHANGE
            )
            token_exchanges.append(token_exchange)
        return TokenExchanges(token_exchanges=token_exchanges)

    async def handle_ack(self, message: Dict):
        pass

    async def handle_message(self, message):
        binance_response = BinanceBidResponse(**message)
        token_exchanges = await self._convert_binance_response_to_token_exchanges(binance_response)
        if token_exchanges.token_exchanges:
            logger.info(f"Got bid for {self.input} to {self.output}: {token_exchanges.token_exchanges[0]}")
        await self.save_token_exchanges_to_database(token_exchanges)


class BinanceTracker(BaseTracker):
    EXCHANGE = Exchanges.binance
    dispatchers: List[BinanceDispatcher] = []

    async def init(self, to_track_list: List[ToTrack]):
        for i in range(len(to_track_list)):
            to_track = to_track_list[i]
            dispatcher = BinanceDispatcher(to_track.input, to_track.output)
            await dispatcher.init(i + 1)
            self.dispatchers.append(dispatcher)

    async def connect(self):
        self.connection = await create_connection(config.BINANCE_BASE_WEBSOCKETS_URL)

        channels = []
        for dispatcher in self.dispatchers:
            await dispatcher.subscribe(self.connection)
            channels.append(await dispatcher.get_channel_name())

        await send_json(self.connection, {
            "method": "SUBSCRIBE",
            "params": channels,
            "id": 1
        })

    async def _get_dispatcher_by_id(self, _id) -> BinanceDispatcher:
        for dispatcher in self.dispatchers:
            if dispatcher.ID == _id:
                return dispatcher

        raise ValueError("There is no such dispatcher with this ID")

    async def _get_dispatcher_by_symbol(self, symbol: str) -> BinanceDispatcher:
        for dispatcher in self.dispatchers:
            if await dispatcher.get_symbol() == symbol.lower():
                return dispatcher

        raise ValueError("There is no such dispatcher for this symbol")

    async def _dispatch_message(self, message: Dict):
        _id = message.get("id")
        if _id is not None:
            dispatcher = await self._get_dispatcher_by_id(message.get("id"))
            await dispatcher.handle_ack(message)
            return

        dispatcher = await self._get_dispatcher_by_symbol(message.get("s"))
        await dispatcher.handle_message(message)

    async def start_tracking(self):
        logger.info(f"Starting tracking on {self.EXCHANGE}")

        while True:
            message = await recv_json(self.connection)
            await self._dispatch_message(message)



