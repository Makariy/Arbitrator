from typing import List, Optional
import json
from pydantic import BaseModel

from lib.database import Database
from ..chain import ExchangeChain


database = Database()
KEY = "best_chains"


class BestChains(BaseModel):
    chains: List[ExchangeChain]


async def get_best_chains() -> Optional[BestChains]:
    raw_previous_best_chains = await database.get(KEY)
    if raw_previous_best_chains is None:
        return None

    return BestChains(**json.loads(raw_previous_best_chains))


async def print_best_chains():
    best_chains = await get_best_chains()
    for chain in best_chains.chains:
        print(f"Profit: {chain.get_profit_percent()} - {chain}")


async def log_best_chains(chains: List[ExchangeChain]):
    previous_best_chains = await get_best_chains()
    if previous_best_chains is None:
        await database.set(KEY, BestChains(chains=chains[:20]).json())
        return

    # They would need to be sorted, but nevermind
    best_chains = sorted(previous_best_chains.chains, reverse=True, key=lambda a: a.get_profit_percent())
    new_chains = sorted(chains, reverse=True, key=lambda a: a.get_profit_percent())

    for new_chain in new_chains:
        for i in range(best_chains.__len__()):
            chain = best_chains[i]
            if chain == new_chain:
                break

            if new_chain.get_profit_percent() > chain.get_profit_percent():
                best_chains[i] = new_chain
                break

    await database.set(KEY, BestChains(chains=best_chains).json())
