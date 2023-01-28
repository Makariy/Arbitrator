from bot.services.user.models import (
    NotificationType,
    PriceLimitNotification,
    Directions
)
from bot.services.user.models import NOTIFICATION_TYPES
from bot.services.utils import get_current_price


async def _is_price_limit_notification_completed(notification: PriceLimitNotification) -> bool:
    current_price = await get_current_price(
        exchange=notification.exchange,
        input=notification.input,
        output=notification.output
    )
    if current_price is None:
        raise ValueError("There is no such chain")
    direction = notification.direction
    limit = notification.limit
    if direction == Directions.UP and current_price >= limit:
        return True
    elif direction == Directions.DOWN and current_price <= limit:
        return True


NOTIFICATION_TYPE_TO_CHECKER_MAP = {
    NotificationType.price_limit: _is_price_limit_notification_completed
}


async def is_notification_completed(notification: NOTIFICATION_TYPES) -> bool:
    notification_checker = NOTIFICATION_TYPE_TO_CHECKER_MAP.get(notification.type)
    if not notification_checker:
        raise ValueError(f"There is no such notification checker for notification type {notification.type}")

    return await notification_checker(notification)
