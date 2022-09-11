from typing import Dict
import logging
import gzip

from lib.symbols import Symbols
from lib.exchanges import Exchanges
from layers.tracker.models import TokenExchanges, TokenExchange, Token
from layers.tracker.services.websocket_services import create_connection, recv_json, send_json

from ..base_tracker import BaseTracker

from .huobi_responses import HuobiAcknowledgment, HuobiMarketDepthResponse

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


class HuobiTracker(BaseTracker):
    EXCHANGE = Exchanges.huobi

    async def _recv_data(self):
        return await recv_json(self.connection, decompress_function=gzip.decompress)

    async def _subscribe(self) -> HuobiAcknowledgment:
        symbol = f"{HUOBI_SYMBOLS[self.input]}{HUOBI_SYMBOLS[self.output]}"
        await send_json(self.connection, {
            "sub": f"market.{symbol}.depth.step0",
            "id": "id1"
        })
        return await self._get_acknowledgment()

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

    async def _handle_message(self, message: Dict):
        ping = message.get("ping")
        if ping is not None:
            return await self._dispatch_ping(ping)

        else:
            market_depth_response = HuobiMarketDepthResponse(**message)
            return await self._dispatch_depth_response(market_depth_response)

    async def connect(self):
        self.connection = await create_connection(config.HUOBI_BASE_WEBSOCKETS_URL)
        ack = await self._subscribe()
        logger.info(f"Got acknowledgment from server: {ack.id}")

    async def start_tracking(self):
        logger.info(f"Starting tracking from '{self.input}' to '{self.output}'")
        while True:
            message = await self._recv_data()
            await self._handle_message(message)
