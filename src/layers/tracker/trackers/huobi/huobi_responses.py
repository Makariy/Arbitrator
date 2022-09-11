from typing import Optional, List
from pydantic import BaseModel, validator


class HuobiAcknowledgment(BaseModel):
    id: str
    status: str
    subbed: Optional[str]
    ts: int


class HuobiMarketDepthTickBid(BaseModel):
    price: float
    count: float


class HuobiMarketDepthTick(BaseModel):
    bids: List[HuobiMarketDepthTickBid]
    version: int
    timestamp: int

    @validator("bids", pre=True)
    def set_bids(value):
        bids = []
        for bid in value:
            bids.append(HuobiMarketDepthTickBid(price=bid[0], count=bid[1]))
        return bids

    class Config:
        fields = {
            "timestamp": "ts"
        }


class HuobiMarketDepthResponse(BaseModel):
    channel: str
    timestamp: int
    tick: HuobiMarketDepthTick

    class Config:
        fields = {
            "channel": "ch",
            "timestamp": "ts"
        }
