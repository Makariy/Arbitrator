from typing import Dict

import logging

from layers.tracker.trackers.base_tracker import BaseTracker
from layers.tracker.services.websocket_services import recv_json, send_json
from layers.tracker.models import TokenExchanges, TokenExchange, Token

from lib.symbols import Symbols
from lib.exchanges import Exchanges
from lib.database import Database
from .kucoin_authorizer import KuCoinAuthorizer
from .kucoin_ping_handler import KuCoinPingHandler
from .kucoin_exceptions import UnknownResponseException, ErrorResponseException
from .kucoin_responses import KuCoinAcknowledgment, \
    KuCoinBidResponse, \
    KuCoinBidResponseData


logger = logging.getLogger(__package__)
database = Database()


KuCoinSymbols = {
    Symbols.USDT: "USDT",
    Symbols.LUNA: "LUNA",
    Symbols.SOL: "SOL",
    Symbols.SHIB: "SHIB",
    Symbols.MIR: "MIR",
    Symbols.AVAX: "AVAX",
    Symbols.ATOM: "ATOM",
    Symbols.EOS: "EOS",
    Symbols.XRP: "XRP",
    Symbols.WAVES: "WAVES",

    Symbols.DOGE: "DOGE",
    Symbols.ETH: "ETH",
    Symbols.BTC: "BTC",
    Symbols.EUR: "EUR",
    Symbols.RUB: "RUB",
}


class KuCoinTracker(BaseTracker):
    EXCHANGE = Exchanges.kucoin

    authorizer = KuCoinAuthorizer()
    ping_handler = KuCoinPingHandler()
    subscription_id: str = None

    async def _get_acknowledgment(self) -> KuCoinAcknowledgment:
        response = await recv_json(self.connection)
        ack = KuCoinAcknowledgment(**response)
        if ack.type == "error":
            raise ValueError(f"Server responded with an error: {ack.code} - {ack.data}")
        return ack

    async def _subscribe(self, url) -> str:
        await send_json(self.connection, {
            "id": self.authorizer.connection_id,
            "type": "subscribe",
            "topic": url,
            "privateChannel": False,
            "response": True
        })
        logger.info(f"Subscribed to the '{url}' on server")

        ack = await self._get_acknowledgment()
        return ack.id

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

    async def _handle_bid(self, raw_bid: Dict):
        bid = KuCoinBidResponse(**raw_bid).data
        token_exchanges = await self._convert_bid_to_token_exchanges(bid)
        logger.info(f"Got bid for '{self.input}' to '{self.output}': '{token_exchanges.token_exchanges[0]}'")
        await self.save_token_exchanges_to_database(token_exchanges)

    async def _dispatch_message(self, message: Dict):
        type = message.get("type")
        if type == "message":
            return await self._handle_bid(message)

        elif type == "pong":
            return await self.ping_handler.handle_pong(message)

        elif type == "error":
            logger.error(f"Got error in response: {message}")
            raise ErrorResponseException(message)

        logger.error(f"Got an unknown response from server: {message}")
        raise UnknownResponseException(message)

    async def connect(self):
        self.connection = await self.authorizer.connect()
        self.subscription_id = await self._subscribe(
            f"/spotMarket/level2Depth50:{KuCoinSymbols[self.input]}-{KuCoinSymbols[self.output]}"
        )
        await self.ping_handler.set_connection(self.connection)

    async def start_tracking(self):
        try:
            while True:
                if await self.ping_handler.is_time_to_ping():
                    await self.ping_handler.ping(self.subscription_id)

                message = await recv_json(self.connection)
                await self._dispatch_message(message)

        except ConnectionError as error:
            logger.error(f"Server closed the connection: {error}")

        finally:
            if self.connection.open:
                await self.connection.close()
