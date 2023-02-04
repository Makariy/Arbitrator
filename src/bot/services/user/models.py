from typing import List, Union
from enum import Enum
from pydantic import BaseModel
from lib.symbol import Symbol
from lib.platform import Platform


class Directions(Enum):
    UP = "UP"
    DOWN = "DOWN"


class NotificationType(Enum):
    price_limit = "price_limit"


class NotificationBase(BaseModel):
    type: NotificationType
    input: Symbol
    output: Symbol
    exchange: Platform


class PriceLimitNotification(NotificationBase):
    type = NotificationType.price_limit
    limit: float
    direction: Directions


NOTIFICATION_TYPES = Union[PriceLimitNotification]


class User(BaseModel):
    telegram_id: int
    username: str
    notifications: List[NOTIFICATION_TYPES]

