from typing import List

from pydantic import BaseModel
from lib.symbols import Symbols
from lib.exchanges import Exchanges


class Token(BaseModel):
    price: float
    symbol: Symbols
    exchange: Exchanges
    is_fiat = False

    def is_the_same(self, other) -> bool:
        return self.symbol == other.symbol and (self.exchange == other.exchange or not self.is_fiat)


class TokenExchange(BaseModel):
    input: Token
    output: Token
    count: float
    exchange: Exchanges
    commission: float = 0


class TokenExchanges(BaseModel):
    token_exchanges: List[TokenExchange]

