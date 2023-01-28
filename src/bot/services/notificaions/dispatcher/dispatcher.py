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


async def dispatch_user_notifications(bot: Bot, user: User):
    notifications = user.notifications
    for notification in notifications:
        if await is_notification_completed(notification):
            await notify_notification_completed(bot, user, notification)
            await remove_notification_for_user(user, notification)

    await save_user_to_db(user)


async def dispatch_notifications(bot: Bot):
    users = await get_all_users()

    for user in users:
        await dispatch_user_notifications(bot, user)


async def run_dispatcher(bot: Bot):
    timer = Timer(NOTIFICATION_CHECK_PERIOD)
    while True:
        await timer.start()
        await dispatch_notifications(bot)
        await timer.wait_for_next_iteration()
