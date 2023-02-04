import config
from utils.timer import Timer

from bot.services.user.models import User
from bot.services.user.db_services import (
    get_all_users,
    remove_notification_for_user,
    save_user_to_db
)

from config import NOTIFICATION_CHECK_PERIOD

from aiogram import Bot

from .notification_status_checker import is_notification_completed
from .notification_completed_notifier import notify_notification_completed

from .cache import DispatcherCacheManager

import logging


logger = logging.getLogger(__name__)


async def dispatch_notifications_for_user(bot: Bot, user: User, cache_manager: DispatcherCacheManager):
    notifications = user.notifications
    for notification in notifications:
        exchange_stats = await cache_manager.get_stats_for_token_exchange(
            exchange=notification.exchange,
            input=notification.input,
            output=notification.output
        )
        if not exchange_stats:
            logger.error(f"Could not get exchange stats for {notification.dict()} ")
            return

        if await is_notification_completed(notification, exchange_stats):
            await notify_notification_completed(bot, user, notification)
            await remove_notification_for_user(user, notification)
            await save_user_to_db(user)


async def dispatch_notifications(bot: Bot, cache_manager: DispatcherCacheManager):
    users = await get_all_users()

    for user in users:
        await dispatch_notifications_for_user(bot, user, cache_manager)


async def run_dispatcher(bot: Bot):
    cache_manager = DispatcherCacheManager(config.TO_TRACK)

    timer = Timer(NOTIFICATION_CHECK_PERIOD)
    while True:
        await timer.start()
        await cache_manager.update_cache()
        await dispatch_notifications(bot, cache_manager)
        await timer.wait_for_next_iteration()
