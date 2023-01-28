from aiogram import Bot

from bot.services.user.models import (
    User,
    NOTIFICATION_TYPES,
    PriceLimitNotification,
    NotificationType
)


async def _notify_price_limit_notification_completed(bot: Bot, user: User, notification: PriceLimitNotification):
    await bot.send_message(
        text=f"{notification.input.value} price overcame the limit {notification.limit}",
        chat_id=user.telegram_id
    )


NOTIFICATION_TYPE_TO_NOTIFY_FUNCTION_MAP = {
    NotificationType.price_limit: _notify_price_limit_notification_completed
}


async def notify_notification_completed(bot: Bot, user: User, notification: NOTIFICATION_TYPES):
    notify_function = NOTIFICATION_TYPE_TO_NOTIFY_FUNCTION_MAP.get(notification.type)
    if notify_function is None:
        raise ValueError(f"There is no such notify function for notification type {notification.type}")

    await notify_function(bot, user, notification)

