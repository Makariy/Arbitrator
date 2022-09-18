from typing import List, Optional

import json
from lib.database import Database
from lib.symbols import Symbols
from ..chain import ExchangeChain


database = Database()

KEY = "best_chain"


async def join_symbols(symbols: List[Symbols]) -> str:
    return "-".join(map(lambda a: a.value, symbols))


async def get_chain_symbols(chain: ExchangeChain) -> List[Symbols]:
    cells = chain.cells
    return [cells[0].input.symbol, *list(map(lambda a: a.output.symbol, cells))]


async def make_key_for_symbols(symbols: List[Symbols]) -> str:
    return f"{KEY}_{await join_symbols(symbols)}"


async def make_key_for_chain(chain: ExchangeChain) -> str:
    symbols = await get_chain_symbols(chain)
    return await make_key_for_symbols(symbols)


async def set_best_chain(chain: ExchangeChain):
    key = await make_key_for_chain(chain)
    await database.set(key, chain.json())


async def get_best_chain(symbols: List[Symbols]) -> Optional[ExchangeChain]:
    key = await make_key_for_symbols(symbols)
    raw_best_chain = await database.get(key)
    if raw_best_chain is not None:
        return ExchangeChain(**json.loads(raw_best_chain))

    return None


async def get_all_best_chains() -> List[ExchangeChain]:
    keys = await database.keys(KEY + "*")
    exchanges = []
    for key in keys:
        raw_exchange = await database.get(key)
        exchanges.append(ExchangeChain(**json.loads(raw_exchange)))
    return sorted(exchanges, key=lambda a: a.get_profit_percent(), reverse=True)


async def log_best_chains(chains: List[ExchangeChain]):
    for chain in chains:
        symbols = await get_chain_symbols(chain)
        best_chain = await get_best_chain(symbols)

        if best_chain is not None:
            if best_chain.get_profit_percent() > chain.get_profit_percent():
                continue

        await set_best_chain(chain)


async def format_best_chain(chain: ExchangeChain) -> str:
    profit = "%.5f" % chain.get_profit_percent()
    symbols = await get_chain_symbols(chain)
    rendered_chain = "-".join(map(lambda a: a.value, symbols))
    return f"Profit: {profit}%  {rendered_chain}"


async def format_best_chains(chains: List[ExchangeChain]) -> str:
    sorted_chains = sorted(chains, key=lambda a: a.get_profit_percent(), reverse=True )
    formatted_chains = [await format_best_chain(chain) for chain in sorted_chains]
    return "\n".join(formatted_chains)

