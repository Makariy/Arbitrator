from typing import List, Union
from enum import Enum
from pydantic import BaseModel
from lib.symbols import Symbols
from lib.exchanges import Exchanges


class Directions(Enum):
    UP = "UP"
    DOWN = "DOWN"


class NotificationType(Enum):
    price_limit = "price_limit"


class NotificationBase(BaseModel):
    type: NotificationType


class PriceLimitNotification(NotificationBase):
    type = NotificationType.price_limit
    limit: float
    input: Symbols
    output: Symbols
    exchange: Exchanges
    direction: Directions


NOTIFICATION_TYPES = Union[PriceLimitNotification]


class User(BaseModel):
    telegram_id: int
    username: str
    notifications: List[NOTIFICATION_TYPES]

