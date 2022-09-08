from typing import Optional
import json

from lib.database import Database
from lib.symbols import Symbols
from lib.exchanges import Exchanges
from lib.database.key_manager import create_key
from layers.tracker.models import TokenExchanges


database = Database()


async def get_token_exchanges(exchange: Exchanges, input: Symbols, output: Symbols) -> Optional[TokenExchanges]:
    raw_token_exchanges = await database.get(create_key(exchange, input, output))
    if raw_token_exchanges is None:
        return None
    return TokenExchanges(**json.loads(raw_token_exchanges))
