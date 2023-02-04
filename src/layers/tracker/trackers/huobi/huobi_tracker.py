from typing import Dict, List
import logging
import gzip
from websockets import WebSocketClientProtocol

from lib.symbol import Symbol
from lib.platform import Platform
from lib.exchange import Exchange
from lib.models import TokenExchanges, TokenExchange, Token
from layers.tracker.services.websocket_services import create_connection, recv_json, send_json

from ..base import BaseTracker, BaseDispatcher
from ..exceptions import UnknownResponseException, ErrorResponseException, NoSuchDispatcherException

from .huobi_responses import HuobiMarketDepthResponse, HuobiAcknowledgment
import config


logger = logging.getLogger(__package__)


HUOBI_SYMBOLS = {
    Symbol.USDT: "usdt",

    Symbol.APT: "apt",
    Symbol.MAGIC: "magic",
    Symbol.MINA: "mina",
    Symbol.KAVA: "kava",
    Symbol.NEAR: "near",

    Symbol.LUNA: "luna",
    Symbol.MIR: "mir",
    Symbol.SOL: "sol",
    Symbol.SHIB: "shib",
    Symbol.AVAX: "avax",
    Symbol.ATOM: "atom",
    Symbol.EOS: "eos",
    Symbol.XRP: "xrp",
    Symbol.WAVES: "waves",

    Symbol.DOGE: "doge",
    Symbol.BTC: "btc",
    Symbol.ETH: "eth",
    Symbol.EUR: "eur",
    Symbol.RUB: "rub",
}


class HuobiDispatcher(BaseDispatcher):
    PLATFORM = Platform.huobi
    ack: HuobiAcknowledgment = None

    async def _convert_huobi_response_to_token_exchanges(self, response: HuobiMarketDepthResponse) -> TokenExchanges:
        token_exchanges = []
        for bid in response.tick.bids:
            token_exchange = TokenExchange(
                input=Token(price=1, symbol=self.input, platform=self.PLATFORM),
                output=Token(price=bid.price, symbol=self.output, platform=self.PLATFORM),
                count=bid.count,
                platform=self.PLATFORM,
                timestamp=response.timestamp / 1000
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
    PLATFORM = Platform.huobi

    async def _recv_data(self):
        return await recv_json(self.connection, decompress_function=gzip.decompress)

    async def _send_pong(self, ping: str):
        return await send_json(self.connection, {"pong": ping})

    async def _get_dispatcher_by_channel(self, channel: str) -> HuobiDispatcher:
        for dispatcher in self.dispatchers:
            if dispatcher.channel == channel:
                return dispatcher

        raise NoSuchDispatcherException("There is no such dispatcher for the received channel")

    async def init(self, exchanges_to_track: List[Exchange]):
        for exchange in exchanges_to_track:
            self.dispatchers.append(HuobiDispatcher(exchange.input, exchange.output))

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

        raise UnknownResponseException(f"Received an unknown message from server: {message}")

    async def start_tracking(self):
        logger.info(f"Starting tracking on {self.PLATFORM}")
        while True:
            message = await self._recv_data()
            await self._dispatch_message(message)

