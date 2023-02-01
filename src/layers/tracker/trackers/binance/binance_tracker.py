import asyncio
from typing import List, Dict

from websockets import WebSocketClientProtocol

from lib.symbols import Symbols
from lib.exchanges import Exchanges, ToTrack
from lib.models import TokenExchanges, TokenExchange, Token
from layers.tracker.services.websocket_services import create_connection, send_json, recv_json

from .binance_responses import BinanceBidResponse

from ..base import BaseTracker, BaseDispatcher
from ..exceptions import UnknownResponseException, ErrorResponseException, NoSuchDispatcherException

import logging
import config


logger = logging.getLogger(__package__)


BINANCE_SYMBOLS = {
    Symbols.BTC: "btc",
    Symbols.ETH: "eth",
    Symbols.DOGE: "doge",
    Symbols.SOL: "sol",
    Symbols.ATOM: "atom",
    Symbols.XRP: "xrp",
    Symbols.APT: "apt",
    Symbols.MAGIC: "magic",
    Symbols.MINA: "mina",
    Symbols.KAVA: "kava",
    Symbols.NEAR: "near",

    Symbols.USDT: "usdt",
    Symbols.LUNA: "luna",
    Symbols.MIR: "mir",
    Symbols.SHIB: "shib",
    Symbols.AVAX: "avax",
    Symbols.EOS: "eos",
    Symbols.WAVES: "waves",

    Symbols.EUR: "eur",
    Symbols.RUB: "rub",
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
        await send_json(connection, {
            "method": "SUBSCRIBE",
            "params": [
                f"{await self.get_symbol()}@depth"
            ],
            "id": self.ID
        })

    async def get_channel_name(self) -> str:
        return self.channel

    async def _convert_binance_response_to_token_exchanges(self, response: BinanceBidResponse) -> TokenExchanges:
        token_exchanges = []
        for bid in filter(lambda a: not a.count <= 0, response.bids):
            token_exchange = TokenExchange(
                input=Token(price=1, symbol=self.input, exchange=self.EXCHANGE),
                output=Token(price=bid.price, symbol=self.output, exchange=self.EXCHANGE),
                count=bid.count,
                exchange=self.EXCHANGE,
                timestamp=response.event_time / 1000
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
            await dispatcher.init(_id=i)
            self.dispatchers.append(dispatcher)

    async def connect(self):
        self.connection = await create_connection(config.BINANCE_BASE_WEBSOCKETS_URL)

        for dispatcher in self.dispatchers:
            await dispatcher.subscribe(self.connection)
            await asyncio.sleep(0.5)

    async def _get_dispatcher_by_id(self, _id) -> BinanceDispatcher:
        for dispatcher in self.dispatchers:
            if dispatcher.ID == _id:
                return dispatcher

        raise NoSuchDispatcherException("There is no such dispatcher with this ID")

    async def _get_dispatcher_by_symbol(self, symbol: str) -> BinanceDispatcher:
        for dispatcher in self.dispatchers:
            if await dispatcher.get_symbol() == symbol.lower():
                return dispatcher

        raise NoSuchDispatcherException("There is no such dispatcher for this symbol")

    async def _dispatch_error(self, error: Dict):
        logger.error(f"Got an error from server: {error}")
        raise ErrorResponseException(error)

    async def _dispatch_message(self, message: Dict):
        if message.get("result") is not None:
            return self._dispatch_error(message)

        if message.get("id") is not None:
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



