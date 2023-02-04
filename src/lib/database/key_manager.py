from typing import List
from lib.symbol import Symbol, join_symbols
from lib.platform import Platform


CURRENT_EXCHANGE_KEY = "currentexchange"
BEST_CHAIN_KEY = "bestchain"
CURRENT_CHAIN_KEY = "currentchain"
PROFIT_CHAIN_PUBSUB_KEY = "profit_pubsub"

USER_KEY = "user"


async def create_key_for_current_exchange(exchange: Platform, input: Symbol, output: Symbol) -> str:
    return f"{CURRENT_EXCHANGE_KEY}_{exchange.value}_{input.value}-{output.value}"


async def create_key_for_best_chain(symbols: List[Symbol]) -> str:
    return f"{BEST_CHAIN_KEY}_{await join_symbols(symbols)}"


async def create_key_for_current_chain(symbols: List[Symbol]) -> str:
    return f"{CURRENT_CHAIN_KEY}_{await join_symbols(symbols)}"


async def create_key_for_profit_chain_pubsub(symbols: List[Symbol]) -> str:
    return f"{PROFIT_CHAIN_PUBSUB_KEY}_{await join_symbols(symbols)}"


async def create_key_for_user_by_telegram_id(telegram_id: int) -> str:
    return f"{USER_KEY}_{telegram_id}"


