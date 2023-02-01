from typing import List
from bot.services.user.models import (
    NotificationType,
    PriceLimitNotification,
    NOTIFICATION_TYPES
)


async def _sort_price_limit_notifications(notifications: List[PriceLimitNotification]) -> List[PriceLimitNotification]:
    return list(
        sorted(
            notifications,
            key=lambda notification: (notification.input.value, notification.limit)
        )
    )


NOTIFICATION_TYPE_TO_SORT_FUNCTION_MAP = {
    NotificationType.price_limit: _sort_price_limit_notifications
}


async def sort_notifications(notifications: List[NOTIFICATION_TYPES]) -> List[NOTIFICATION_TYPES]:
    notification_types = set(map(lambda a: a.type, notifications))

    notification_type_to_notifications_map = {
        notification_type: list(filter(lambda notification: notification.type is notification_type, notifications))
        for notification_type in notification_types
    }

    sorted_notifications = []
    for notification_type, notification_type_notifications in notification_type_to_notifications_map.items():
        sort_function = NOTIFICATION_TYPE_TO_SORT_FUNCTION_MAP[notification_type]
        sorted_notifications.extend(await sort_function(notification_type_notifications))

    return sorted_notifications

