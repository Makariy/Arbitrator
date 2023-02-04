from typing import List

from pydantic import BaseModel
from lib.symbol import Symbol
from lib.platform import Platform

from config import DEBUG


class Token(BaseModel):
    price: float
    symbol: Symbol
    platform: Platform
    is_fiat = False

    def can_convert_to(self, other) -> bool:
        return self.symbol == other.symbol and (self.platform == other.platform or not self.is_fiat)

    def is_the_same(self, other) -> bool:
        return self.can_convert_to(other) and self.platform == other.platform

    class Config:
        validation = DEBUG


class TokenExchange(BaseModel):
    input: Token
    output: Token
    count: float
    platform: Platform
    commission: float = 0
    timestamp: float

    class Config:
        validation = DEBUG


class TokenExchanges(BaseModel):
    token_exchanges: List[TokenExchange]

    class Config:
        validation = DEBUG
