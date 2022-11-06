from typing import List

import asyncio
from asyncio import Lock

from lib.symbols import Symbols, join_symbols
from lib.database.key_manager import create_key_for_profit_chain_pubsub

from .receiver import subscribe

from layers.analyzer.chain import ExchangeChain
from layers.analyzer.chain_services import get_all_chains
from layers.analyzer.chain_services import get_current_chain
import config


class Acquirer:
    symbols: List[Symbols]
    lock: Lock

    async def _track_chain(self, chain: ExchangeChain):
        print("Going to track the exchange for symbols: ",
              await join_symbols(self.symbols),
              " current profit: ",
              chain.get_profit_percent(), "%")
        for i in range(20):
            chain = await get_current_chain(self.symbols)
            if chain is None:
                print("No current exchange for chain: ", self.symbols)
                continue
            print("Current profit: ", chain.get_profit_percent(), "%")
            await asyncio.sleep(0.5)

    async def handle_message(self, message):
        data = message.get('data')
        if self.lock.locked():
            return

        async with self.lock:
            chain = ExchangeChain.parse_raw(data)
            await self._track_chain(chain)

    async def init(self, symbols: List[Symbols]):
        self.symbols = symbols
        self.lock = Lock()
        await subscribe(await create_key_for_profit_chain_pubsub(self.symbols), self.handle_message)


async def _create_acquirers() -> List[Acquirer]:
    all_chains = await get_all_chains()

    acquirers = []
    for chain in all_chains:
        acquirer = Acquirer()
        await acquirer.init(chain.get_chain_symbols())
        acquirers.append(acquirer)

    return acquirers


async def _run_acquirer():
    acquirers = await _create_acquirers()
    asyncio.get_running_loop().run_forever()


def run_acquirer():
    asyncio.run(_run_acquirer())
