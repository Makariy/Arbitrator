from typing import List
from lib.symbols import Symbols, join_symbols
from lib.exchanges import Exchanges


CURRENT_EXCHANGE_KEY = "currentexchange"
BEST_CHAIN_KEY = "bestchain"
CURRENT_CHAIN_KEY = "currentchain"


async def create_key_for_current_exchange(exchange: Exchanges, input: Symbols, output: Symbols) -> str:
    return f"{CURRENT_EXCHANGE_KEY}_{exchange.value}_{input.value}-{output.value}"


async def create_key_for_best_chain(symbols: List[Symbols]) -> str:
    return f"{BEST_CHAIN_KEY}_{await join_symbols(symbols)}"


async def create_key_for_current_chain(symbols: List[Symbols]) -> str:
    return f"{CURRENT_CHAIN_KEY}_{await join_symbols(symbols)}"



