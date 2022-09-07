from typing import List
from dataclasses import dataclass

from lib.symbols import Symbols
from lib.exchanges import Exchanges

from layers.tracker.models import Bid

from config import ALL_EXCHANGES


@dataclass
class Token:
    symbol: Symbols
    value: float


@dataclass
class ExchangeBid:
    exchanges: List[Exchanges]
    input: Token
    output: Token
    count: float


def convert_bid_to_exchange_bid(bid: Bid) -> ExchangeBid:
    best_bid = bid.bids[0]
    input = Token(
        symbol=Symbols[bid.input],
        value=1
    )
    output = Token(
        symbol=Symbols[bid.output],
        value=best_bid.price
    )
    return ExchangeBid(
        exchanges=ALL_EXCHANGES,
        input=input,
        output=output,
        count=best_bid.count
    )


