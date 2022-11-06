from typing import Callable, Coroutine, Any

from lib.database import Database
from lib.database.key_manager import create_key_for_profit_chain_pubsub
from layers.analyzer.chain import ExchangeChain


database = Database()


async def subscribe(key: str, callback: Callable[[Any], Coroutine]):
    return await database.subscribe(key, callback)


async def send_profitable_chain(chain: ExchangeChain):
    key = await create_key_for_profit_chain_pubsub(chain.get_chain_symbols())
    await database.publish(key, chain.json())

