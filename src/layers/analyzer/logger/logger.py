from typing import List
from ..chain import ExchangeChain
from ..chain_services import save_current_chains, \
    get_best_chain, \
    set_best_chain


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

