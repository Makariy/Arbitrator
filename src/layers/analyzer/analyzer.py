from typing import List, Optional
import logging
import asyncio
from itertools import product

from layers.tracker.models import TokenExchanges, TokenExchange, Token
from .token_exchanges_fetcher import get_token_exchanges

from config import TO_TRACK, MAX_EXCHANGE_DEPTH


logger = logging.getLogger(__package__)


class InvalidChain(Exception):
    pass


class ExchangeChain:
    cells: List[TokenExchange] = []

    def __init__(self, cells: Optional[List[TokenExchange]]):
        self.cells = []
        if cells:
            for cell in cells:
                self.add_cell(cell)

    def __iter__(self):
        return self.cells.__iter__()

    def __str__(self):
        return f"""ExchangeChain(cells={[
            f'{token_exchange.input.symbol.name} - {token_exchange.output.symbol.name}' 
            for token_exchange in self.cells]})"""

    def __repr__(self):
        return self.__str__()

    def _get_last_cell(self) -> TokenExchange:
        if len(self.cells) == 0:
            raise IndexError("There are no cells")
        return self.cells[len(self.cells) - 1]

    def validate_chain(self):
        if len(self.cells) < 2:
            raise InvalidChain("Chain length is less than 2")
        if not self.cells[0].input.is_the_same(self._get_last_cell().output):
            raise InvalidChain("The chain input is not the same chain output")

    def add_cell(self, cell: TokenExchange):
        if self.cells:
            if not self._get_last_cell().output.is_the_same(cell.input):
                raise InvalidChain("The previous output token is not the same as the new input token")
        self.cells.append(cell)

    def get_profit_percent(self) -> float:
        if len(self.cells) == 0:
            return 0

        first_exchange = self.cells[0]
        last_exchange = self._get_last_cell()

        if not first_exchange.input.is_the_same(last_exchange.output):
            raise ValueError("The input and the output tokens in the chain are not the same")

        current_token = Token(**first_exchange.input.dict())
        for cell in self.cells:
            price = current_token.price * cell.output.price
            current_token = Token(price=price, symbol=cell.output.symbol, exchange=cell.output.exchange)

        return 1 - (first_exchange.input.price / current_token.price)


async def get_all_token_exchanges() -> List[TokenExchanges]:
    """Gets the current value of all the token exchanges that are configured to run from the database"""
    from layers.tracker.tracker import create_trackers
    trackers = create_trackers(TO_TRACK)
    token_exchanges = []
    for tracker in trackers:
        token_exchanges.append(await get_token_exchanges(tracker.EXCHANGE, tracker.input, tracker.output))
    return token_exchanges


async def check_if_can_exchange(token_exchange: TokenExchange) -> bool:
    return True


async def get_best_token_exchange_from_list(token_exchanges: TokenExchanges) -> TokenExchange:
    for token_exchange in token_exchanges.token_exchanges:
        if await check_if_can_exchange(token_exchange):
            return token_exchange


async def get_all_chains(token_exchanges_list: List[TokenExchanges]) -> List[ExchangeChain]:
    token_exchange_list = []
    for token_exchanges in token_exchanges_list:
        token_exchange_list.append(await get_best_token_exchange_from_list(token_exchanges))
    combinations = product(*([token_exchange_list] * MAX_EXCHANGE_DEPTH))
    chains = []
    for combination in combinations:
        try:
            chains.append(ExchangeChain(combination))
        except InvalidChain:
            pass
    return chains


async def filter_possible_chains(chains: List[ExchangeChain]) -> List[ExchangeChain]:
    possible_chains = []
    for chain in chains:
        try:
            chain.validate_chain()
            possible_chains.append(chain)
        except InvalidChain:
            pass

    return possible_chains


async def _run_analyzer():
    while True:
        all_token_exchanges = await get_all_token_exchanges()
        chains = await get_all_chains(all_token_exchanges)
        possible_chains = await filter_possible_chains(chains)
        print("Possible chains: ", possible_chains)
        for possible_chain in possible_chains:
            print(f"Profit from chain {possible_chain}: {possible_chain.get_profit_percent()}%")
        return


def run_analyzer():
    asyncio.run(_run_analyzer())
