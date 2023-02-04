import asyncio
from typing import List, Dict

from websockets import WebSocketClientProtocol

from lib.symbol import Symbol
from lib.platform import Platform
from lib.exchange import Exchange
from lib.models import TokenExchanges, TokenExchange, Token
from layers.tracker.services.websocket_services import create_connection, send_json, recv_json

from .binance_responses import BinanceBidResponse

from ..base import BaseTracker, BaseDispatcher
from ..exceptions import UnknownResponseException, ErrorResponseException, NoSuchDispatcherException

import logging
import config


logger = logging.getLogger(__package__)


BINANCE_SYMBOLS = {
    Symbol.BTC: "btc",
    Symbol.ETH: "eth",
    Symbol.DOGE: "doge",
    Symbol.SOL: "sol",
    Symbol.ATOM: "atom",
    Symbol.XRP: "xrp",
    Symbol.APT: "apt",
    Symbol.MAGIC: "magic",
    Symbol.MINA: "mina",
    Symbol.KAVA: "kava",
    Symbol.NEAR: "near",

    Symbol.USDT: "usdt",
    Symbol.LUNA: "luna",
    Symbol.MIR: "mir",
    Symbol.SHIB: "shib",
    Symbol.AVAX: "avax",
    Symbol.EOS: "eos",
    Symbol.WAVES: "waves",

    Symbol.EUR: "eur",
    Symbol.RUB: "rub",
}


class BinanceDispatcher(BaseDispatcher):
    ID: int
    PLATFORM = Platform.binance

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
                input=Token(price=1, symbol=self.input, platform=self.PLATFORM),
                output=Token(price=bid.price, symbol=self.output, platform=self.PLATFORM),
                count=bid.count,
                platform=self.PLATFORM,
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
    PLATFORM = Platform.binance
    dispatchers: List[BinanceDispatcher] = []

    async def init(self, exchanges_to_track: List[Exchange]):
        for index, exchange in enumerate(exchanges_to_track):
            dispatcher = BinanceDispatcher(exchange.input, exchange.output)
            await dispatcher.init(_id=index)
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
        logger.info(f"Starting tracking on {self.PLATFORM}")

        while True:
            message = await recv_json(self.connection)
            await self._dispatch_message(message)



