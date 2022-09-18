from typing import List
import logging
import asyncio
from itertools import product

from lib.token import TokenExchanges, TokenExchange

from .chain import ExchangeChain, InvalidChain
from .token_exchanges_fetcher import get_token_exchanges
from .logger.logger import log_best_chains

from config import TO_TRACK, MAX_EXCHANGE_DEPTH, INPUT_TOKEN


logger = logging.getLogger(__package__)


async def _reverse_token_exchange(token_exchange: TokenExchange) -> TokenExchange:
    return TokenExchange(
        input=token_exchange.output,
        output=token_exchange.input,
        count=token_exchange.count,
        exchange=token_exchange.exchange,
        commission=token_exchange.commission
    )


async def _reverse_token_exchanges(token_exchanges: TokenExchanges) -> TokenExchanges:
    return TokenExchanges(token_exchanges=[
        await _reverse_token_exchange(token_exchange) for token_exchange in token_exchanges.token_exchanges
    ])


async def get_all_token_exchanges() -> List[TokenExchanges]:
    """Gets the current value of all the token exchanges that are configured to run from the database"""
    token_exchanges = []
    for to_track in TO_TRACK:
        token_exchange = await get_token_exchanges(to_track.exchange, to_track.input, to_track.output)
        token_exchanges.append(token_exchange)
        token_exchanges.append(await _reverse_token_exchanges(token_exchange))

    return token_exchanges


async def check_if_can_exchange(token_exchange: TokenExchange) -> bool:
    return True


async def get_best_token_exchange_from_list(token_exchanges: TokenExchanges) -> TokenExchange:
    for token_exchange in token_exchanges.token_exchanges:
        if await check_if_can_exchange(token_exchange):
            return token_exchange


async def _get_all_combinations_by_depth(arr: List, min_depth=2, max_depth=MAX_EXCHANGE_DEPTH):
    combinations = []
    for i in range(min_depth, max_depth + 1):
        combinations += product(*([arr] * i))
    return combinations


async def get_all_chains(token_exchanges_list: List[TokenExchanges]) -> List[ExchangeChain]:
    token_exchange_list = []
    for token_exchanges in token_exchanges_list:
        token_exchange_list.append(await get_best_token_exchange_from_list(token_exchanges))

    combinations = await _get_all_combinations_by_depth(token_exchange_list)
    chains = []
    for combination in combinations:
        try:
            chain = ExchangeChain(cells=combination)
            chain.validate_chain()
            chains.append(chain)
        except InvalidChain:
            pass
    return chains


async def filter_possible_chains(chains: List[ExchangeChain]) -> List[ExchangeChain]:
    possible_chains = []
    for chain in chains:
        try:
            if INPUT_TOKEN in [None, chain.cells[0].input.symbol]:
                chain.validate_chain()
                possible_chains.append(chain)
        except InvalidChain:
            pass

    return possible_chains


async def _run_analyzer():
    print("===" * 10)
    while True:
        all_token_exchanges = await get_all_token_exchanges()
        chains = await get_all_chains(all_token_exchanges)
        possible_chains = await filter_possible_chains(chains)
        sorted_chains = sorted(possible_chains, key=lambda a: a.get_profit_percent(), reverse=True)
        best_chains = list(filter(lambda a: a.get_profit_percent() > 0, sorted_chains))

        print("Current best chains: ")
        for chain in best_chains[:8]:
            print("Profit: ", chain.get_profit_percent(), " - ", chain)
        print("===" * 10)
        await log_best_chains(best_chains)
        await asyncio.sleep(2)


def run_analyzer():
    asyncio.run(_run_analyzer())
