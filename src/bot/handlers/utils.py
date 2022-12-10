from typing import Optional

from lib.exchanges import Exchanges
from lib.symbols import Symbols
from layers.analyzer.token_exchanges_fetcher import get_token_exchanges


async def get_current_price(exchange: Exchanges, input: Symbols, output: Symbols) -> Optional[float]:
    exchanges = await get_token_exchanges(exchange, input, output)
    if exchanges:
        current_exchange = exchanges.token_exchanges[0]
        return current_exchange.output.price / current_exchange.input.price
    return None
