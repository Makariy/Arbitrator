from typing import List, Optional
from pydantic import BaseModel, validator


class KuCoinBidResponseDataAsk(BaseModel):
    price: float
    count: float


class KuCoinBidResponseData(BaseModel):
    """kucoin current best bid's response asks (Using this to parse the response)"""
    asks: List[KuCoinBidResponseDataAsk]
    timestamp: int

    @validator('asks', pre=True)
    def set_asks(value):
        asks = []
        for item in value:
            ask = KuCoinBidResponseDataAsk(price=item[0], count=item[1])
            asks.append(ask)
        return asks


class KuCoinBidResponse(BaseModel):
    """kucoin current best bid's response (Using this to parse the response)"""
    type: str
    topic: str
    subject: str
    data: KuCoinBidResponseData


class KuCoinAcknowledgment(BaseModel):
    id: str
    type: str
    code: Optional[int]
    topic: Optional[str]
    data: Optional[str]
    private_channel: Optional[bool]
    response: Optional[bool]

    class Config:
        fields = {
            "private_channel": "privateChannel"
        }
