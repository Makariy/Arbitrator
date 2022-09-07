from typing import Optional
import json

from lib.database import Database
from lib.symbols import Symbols
from lib.database.key_manager import create_key
from layers.tracker.models import Bid


database = Database()


async def get_bid(exchange_name: str, input: Symbols, output: Symbols) -> Optional[Bid]:
    raw_bid = await database.get(create_key(exchange_name, input, output))
    if raw_bid is None:
        return None
    return Bid(**json.loads(raw_bid))
