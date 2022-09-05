from typing import List

from pydantic import BaseModel


class BidAsk(BaseModel):
    price: float
    count: float


class Bid(BaseModel):
    input: str
    output: str
    bids: List[BidAsk]




