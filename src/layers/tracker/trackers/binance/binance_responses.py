from typing import List
from pydantic import BaseModel, validator


class BinanceBid(BaseModel):
    price: float
    count: float


class BinanceBidResponse(BaseModel):
    event_type: str
    event_time: int
    symbol: str
    first_update_id: int
    final_update_id: int
    bids: List[BinanceBid]
    asks: List[BinanceBid]

    @staticmethod
    def _parse_bids(value: List[List[int]]):
        result = []
        for bid in value:
            result.append(BinanceBid(price=bid[0], count=bid[1]))
        return result

    @validator("bids", pre=True)
    def set_bids(value: List[List[int]]):
        return BinanceBidResponse._parse_bids(value)

    @validator("asks", pre=True)
    def set_asks(value: List[List[int]]):
        return BinanceBidResponse._parse_bids(value)

    class Config:
        fields = {
            "event_type": "e",
            "event_time": "E",
            "symbol": "s",
            "first_update_id": "U",
            "final_update_id": "u",
            "bids": "b",
            "asks": "a"
        }
