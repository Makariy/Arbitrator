from bot.services.user.models import (
    NotificationType,
    PriceLimitNotification,
    Directions
)
from bot.services.user.models import NOTIFICATION_TYPES
from bot.services.notificaions.dispatcher.cache import ExchangeStats


async def _is_price_limit_notification_completed(notification: PriceLimitNotification, stats: ExchangeStats) -> bool:
    current_price = stats.price
    direction = notification.direction
    limit = notification.limit

    if direction == Directions.UP and current_price >= limit:
        return True
    elif direction == Directions.DOWN and current_price <= limit:
        return True
    return False


NOTIFICATION_TYPE_TO_CHECKER_MAP = {
    NotificationType.price_limit: _is_price_limit_notification_completed
}


async def is_notification_completed(notification: NOTIFICATION_TYPES, stats: ExchangeStats) -> bool:
    is_notification_completed_function = NOTIFICATION_TYPE_TO_CHECKER_MAP.get(notification.type)
    if not is_notification_completed_function:
        raise ValueError(f"There is no such notification checker for notification type {notification.type}")

    return await is_notification_completed_function(notification, stats)
