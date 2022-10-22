from typing import List, Optional

import json
from lib.database import Database
from lib.symbols import Symbols
from lib.database.key_manager import create_key_for_best_chain, \
    create_key_for_current_chain, \
    BEST_CHAIN_KEY
from ..chain import ExchangeChain


database = Database()


async def set_best_chain(chain: ExchangeChain):
    symbols = chain.get_chain_symbols()
    key = await create_key_for_best_chain(symbols)
    await database.set(key, chain.json())


async def get_best_chain(symbols: List[Symbols]) -> Optional[ExchangeChain]:
    key = await create_key_for_best_chain(symbols)
    raw_best_chain = await database.get(key)
    if raw_best_chain is not None:
        return ExchangeChain(**json.loads(raw_best_chain))

    return None


async def get_all_best_chains() -> List[ExchangeChain]:
    keys = await database.keys(BEST_CHAIN_KEY + "*")
    exchanges = []
    for key in keys:
        raw_exchange = await database.get(key)
        exchanges.append(ExchangeChain(**json.loads(raw_exchange)))
    return sorted(exchanges, key=lambda a: a.get_profit_percent(), reverse=True)


async def save_current_chains(best_chains: List[ExchangeChain]):
    for chain in best_chains:
        symbols = chain.get_chain_symbols()
        await database.set(await create_key_for_current_chain(symbols), chain.json())


async def get_current_chain(symbols: List[Symbols]) -> Optional[ExchangeChain]:
    raw_chain = await database.get(await create_key_for_current_chain(symbols))
    if raw_chain is None:
        return None
    return ExchangeChain(**json.loads(raw_chain))


async def log_best_chains(chains: List[ExchangeChain]):
    await save_current_chains(chains)

    for chain in chains:
        symbols = chain.get_chain_symbols()
        best_chain = await get_best_chain(symbols)

        if best_chain is not None:
            if best_chain.get_profit_percent() > chain.get_profit_percent():
                continue

        await set_best_chain(chain)


async def format_chain(chain: ExchangeChain) -> str:
    profit = "%.5f" % chain.get_profit_percent()
    symbols = chain.get_chain_symbols()
    rendered_chain = "-".join(map(lambda a: a.value, symbols))
    return f"Profit: {profit}%  {rendered_chain}"


async def format_chains(chains: List[ExchangeChain]) -> str:
    sorted_chains = sorted(chains, key=lambda a: a.get_profit_percent(), reverse=True)
    formatted_chains = [await format_chain(chain) for chain in sorted_chains]
    return "\n".join(formatted_chains)

