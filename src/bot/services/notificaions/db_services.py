from typing import List
from lib.platform import Platform
from lib.symbol import Symbol

from bot.services.user.models import Directions, PriceLimitNotification, NOTIFICATION_TYPES
from bot.services.user.db_services import (
    get_user_from_db_by_telegram_id,
    save_user_to_db,
    add_notification_to_user,
    remove_notification_for_user
)


class UserDoesNotExist(Exception):
    pass


class IncorrectNotificationIndexError(Exception):
    pass


async def create_price_limit_notification_for_user(
        telegram_id: int,
        exchange: Platform,
        intput_symbol: Symbol,
        output_symbol: Symbol,
        limit: float,
        direction: Directions
):
    user = await get_user_from_db_by_telegram_id(telegram_id)
    if user is None:
        raise UserDoesNotExist()

    notification = PriceLimitNotification(
        limit=limit,
        input=intput_symbol,
        output=output_symbol,
        exchange=exchange,
        direction=direction
    )

    await add_notification_to_user(user, notification)
    await save_user_to_db(user)


async def get_user_notifications(telegram_id: int) -> List[NOTIFICATION_TYPES]:
    user = await get_user_from_db_by_telegram_id(telegram_id)
    if user is None:
        raise UserDoesNotExist()

    return user.notifications

