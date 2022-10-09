from typing import Dict, List
import logging
import gzip
from websockets import WebSocketClientProtocol

from lib.symbols import Symbols
from lib.exchanges import Exchanges, ToTrack
from lib.token import TokenExchanges, TokenExchange, Token
from layers.tracker.services.websocket_services import create_connection, recv_json, send_json

from ..base import BaseTracker, BaseDispatcher

from .huobi_responses import HuobiMarketDepthResponse, HuobiAcknowledgment
import config


logger = logging.getLogger(__package__)


HUOBI_SYMBOLS = {
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


class HuobiDispatcher(BaseDispatcher):
    EXCHANGE = Exchanges.huobi
    ack: HuobiAcknowledgment = None

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

    async def _dispatch_depth_response(self, response: HuobiMarketDepthResponse):
        token_exchanges = await self._convert_huobi_response_to_token_exchanges(response)
        logger.info(f"Got bid for {self.input} to {self.output}: {token_exchanges.token_exchanges[0]}")
        return await self.save_token_exchanges_to_database(token_exchanges)

    async def subscribe(self, connection: WebSocketClientProtocol):
        symbol = f"{HUOBI_SYMBOLS[self.input]}{HUOBI_SYMBOLS[self.output]}"
        self.channel = f"market.{symbol}.depth.step0"
        await send_json(connection, {
            "sub": self.channel,
            "id": self.channel
        })

    async def handle_acknowledgment(self, ack: Dict):
        self.ack = HuobiAcknowledgment(**ack)

    async def handle_message(self, message: Dict):
        if self.ack is None:
            raise ConnectionError(f"The server had not sent the acknowledgment")
        market_depth_response = HuobiMarketDepthResponse(**message)
        return await self._dispatch_depth_response(market_depth_response)


class HuobiTracker(BaseTracker):
    EXCHANGE = Exchanges.huobi

    async def _recv_data(self):
        return await recv_json(self.connection, decompress_function=gzip.decompress)

    async def _send_pong(self, ping: str):
        return await send_json(self.connection, {"pong": ping})

    async def _get_dispatcher_by_channel(self, channel: str) -> HuobiDispatcher:
        for dispatcher in self.dispatchers:
            if dispatcher.channel == channel:
                return dispatcher

        raise ValueError("There is no such dispatcher for the received channel")

    async def init(self, to_track_list: List[ToTrack]):
        for to_track in to_track_list:
            self.dispatchers.append(HuobiDispatcher(to_track.input, to_track.output))

    async def connect(self):
        self.connection = await create_connection(config.HUOBI_BASE_WEBSOCKETS_URL)
        for dispatcher in self.dispatchers:
            await dispatcher.subscribe(self.connection)

    async def _dispatch_message(self, message: Dict):
        channel = message.get("ch")
        if channel:
            dispatcher = await self._get_dispatcher_by_channel(channel)
            await dispatcher.handle_message(message)
            return

        subbed = message.get("subbed")
        if subbed:
            dispatcher = await self._get_dispatcher_by_channel(subbed)
            await dispatcher.handle_acknowledgment(message)
            return

        ping = message.get("ping")
        if ping:
            await self._send_pong(ping)
            return

        raise ValueError(f"Received an unknown message from server: {message}")

    async def start_tracking(self):
        logger.info(f"Starting tracking on {self.EXCHANGE}")
        while True:
            message = await self._recv_data()
            await self._dispatch_message(message)

