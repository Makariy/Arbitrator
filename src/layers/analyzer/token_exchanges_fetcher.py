from typing import Optional, List, Tuple
import json

from lib.database import Database
from lib.symbols import Symbols
from lib.exchanges import Exchanges
from lib.database.key_manager import create_key_for_current_exchange
from lib.models import TokenExchanges

database = Database()


async def get_token_exchanges(exchange: Exchanges, input: Symbols, output: Symbols) -> Optional[TokenExchanges]:
    key = await create_key_for_current_exchange(exchange, input, output)
    raw_token_exchanges = await database.get(key)
    if raw_token_exchanges is None:
        return None
    return TokenExchanges(**json.loads(raw_token_exchanges))


async def bulk_get_token_exchanges(raw_exchanges: List[Tuple[Exchanges, Symbols, Symbols]]) \
        -> List[Optional[TokenExchanges]]:
    keys = [
        await create_key_for_current_exchange(raw_exchange[0], raw_exchange[1], raw_exchange[2])
        for raw_exchange in raw_exchanges
    ]
    results = await database.mget(keys)
    return [
        TokenExchanges.parse_raw(raw_token_exchanges)
        for raw_token_exchanges in filter(lambda a: a is not None, results)
    ]
