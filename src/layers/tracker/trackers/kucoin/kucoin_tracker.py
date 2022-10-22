from typing import Dict, List

import logging
from websockets import WebSocketClientProtocol

from layers.tracker.trackers.base import BaseTracker, BaseDispatcher
from layers.tracker.services.websocket_services import recv_json, send_json
from lib.token import TokenExchanges, TokenExchange, Token

from lib.symbols import Symbols
from lib.exchanges import Exchanges, ToTrack
from lib.database import Database
from .kucoin_authorizer import KuCoinAuthorizer
from .kucoin_pinger import KuCoinPinger
from ..exceptions import UnknownResponseException, ErrorResponseException, NoSuchDispatcherException
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


class KuCoinDispatcher(BaseDispatcher):
    EXCHANGE = Exchanges.kucoin
    connection_id: str

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

    async def handle_acknowledgment(self, ack: Dict) -> KuCoinAcknowledgment:
        ack = KuCoinAcknowledgment(**ack)
        if ack.type == "error":
            raise ErrorResponseException(f"Server responded with an error: {ack.code} - {ack.data}")
        return ack

    async def handle_message(self, message: Dict):
        bid = KuCoinBidResponse(**message).data
        token_exchanges = await self._convert_bid_to_token_exchanges(bid)
        logger.info(f"Got bid for '{self.input}' to '{self.output}': '{token_exchanges.token_exchanges[0]}'")
        await self.save_token_exchanges_to_database(token_exchanges)

    async def subscribe(self, connection: WebSocketClientProtocol):
        self.channel = f"/spotMarket/level2Depth50:{KuCoinSymbols[self.input]}-{KuCoinSymbols[self.output]}"
        await send_json(connection, {
            "id": self.channel,
            "type": "subscribe",
            "topic": self.channel,
            "privateChannel": False,
            "response": True
        })
        logger.info(f"Subscribed to the '{self.channel}' on server")


class KuCoinTracker(BaseTracker):
    EXCHANGE = Exchanges.kucoin

    authorizer = KuCoinAuthorizer()
    pinger: KuCoinPinger

    async def _get_dispatcher_by_topic(self, topic: str) -> BaseDispatcher:
        for dispatcher in self.dispatchers:
            if dispatcher.channel == topic:
                return dispatcher

        raise NoSuchDispatcherException(f"No such dispatcher for topic: '{topic}'")

    async def _dispatch_message(self, message: Dict):
        type = message.get("type")
        if type == "message":
            dispatcher = await self._get_dispatcher_by_topic(message['topic'])
            return await dispatcher.handle_message(message)

        elif type == "pong":
            return await self.pinger.handle_pong(message)

        elif type == "error":
            logger.error(f"Got error in response: {message}")
            raise ErrorResponseException(message)

        elif type == "ack":
            return

        logger.error(f"Got an unknown response from server: {message}")
        raise UnknownResponseException(message)

    async def init(self, to_track_list: List[ToTrack]):
        for to_track in to_track_list:
            dispatcher = KuCoinDispatcher(input=to_track.input, output=to_track.output)
            await dispatcher.init()
            self.dispatchers.append(dispatcher)

    async def connect(self):
        await self.authorizer.authorize()
        self.connection = await self.authorizer.open_connection()
        self.pinger = KuCoinPinger(self.connection, self.authorizer.token)
        for dispatcher in self.dispatchers:
            await dispatcher.subscribe(self.connection)

    async def start_tracking(self):
        ping_task = await self.pinger.start_pinging()

        try:
            while True:
                message = await recv_json(self.connection)
                await self._dispatch_message(message)

        except ConnectionError as error:
            logger.error(f"Server closed the connection: {error}")
            raise

        finally:
            if not ping_task.done():
                ping_task.cancel()

            if self.connection.open:
                await self.connection.close()
