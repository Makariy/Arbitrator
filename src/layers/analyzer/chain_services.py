from typing import Optional, List

from lib.database import Database
from lib.symbol import Symbol
from lib.database.key_manager import create_key_for_best_chain, \
    create_key_for_current_chain, \
    BEST_CHAIN_KEY, \
    CURRENT_CHAIN_KEY
from .chain import ExchangeChain


database = Database()


async def get_current_chain(symbols: List[Symbol]) -> Optional[ExchangeChain]:
    raw_chain = await database.get(await create_key_for_current_chain(symbols))
    if raw_chain is None:
        return None
    return ExchangeChain.parse_raw(raw_chain)


async def save_current_chains(best_chains: List[ExchangeChain]):
    for chain in best_chains:
        symbols = chain.get_chain_symbols()
        await database.set(await create_key_for_current_chain(symbols), chain.json())


async def get_all_chains() -> List[ExchangeChain]:
    keys = await database.keys(CURRENT_CHAIN_KEY + "*")
    chains = []
    for key in keys:
        raw_chain = await database.get(key)
        chains.append(ExchangeChain.parse_raw(raw_chain))
    return chains


async def get_best_chain(symbols: List[Symbol]) -> Optional[ExchangeChain]:
    key = await create_key_for_best_chain(symbols)
    raw_best_chain = await database.get(key)
    if raw_best_chain is not None:
        return ExchangeChain.parse_raw(raw_best_chain)

    return None


async def set_best_chain(chain: ExchangeChain):
    symbols = chain.get_chain_symbols()
    key = await create_key_for_best_chain(symbols)
    await database.set(key, chain.json())


async def get_all_best_chains() -> List[ExchangeChain]:
    keys = await database.keys(BEST_CHAIN_KEY + "*")
    chains = []
    for key in keys:
        raw_chain = await database.get(key)
        chains.append(ExchangeChain.parse_raw(raw_chain))
    return sorted(chains, key=lambda a: a.get_profit_percent(), reverse=True)



