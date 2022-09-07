from typing import List

from pydantic import BaseModel
from lib.symbols import Symbols
from lib.exchanges import Exchanges


class Token(BaseModel):
    price: float
    symbol: Symbols


class TokenExchange(BaseModel):
    input: Token
    output: Token
    count: float
    exchange: Exchanges


class TokenExchanges(BaseModel):
    token_exchanges: List[TokenExchange]

