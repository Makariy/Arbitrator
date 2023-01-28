import logging
from aiogram import types

from lib.symbols import Symbols

from bot.services.utils import auth_required
from bot.services.user.models import Directions, User
from bot.services.notificaions.db_services import (
    create_price_limit_notification_for_user,
    pop_notification_from_user_by_index,
    get_user_notifications,
    IncorrectNotificationIndexError
)

from config import NOTIFICATION_EXCHANGE


logger = logging.getLogger(__package__)


async def _render_notification(notification) -> str:
    return f"{notification.input.value} {notification.limit} {notification.direction.value}"


@auth_required
async def handle_create_price_limit_notification(message: types.Message, user: User):
    try:
        args = message.get_args().split()
        if len(args) != 3:
            raise ValueError(f"Arguments count is not 3: len(args) == {len(args)}")

        symbol = Symbols(args[0])
        limit = float(args[1])
        direction = Directions(args[2].upper())

    except ValueError:
        await message.reply(f"You need to specify <symbol> <limit> <UP or DOWN>")
        return

    await create_price_limit_notification_for_user(
        user.telegram_id,
        exchange=NOTIFICATION_EXCHANGE,
        intput_symbol=symbol,
        output_symbol=Symbols.USDT,
        limit=limit,
        direction=direction
    )
    await message.reply(
        f"Started waiting for {symbol.value} "
        f"to go {'above' if direction is Directions.UP else 'below'} "
        f"{limit}"
    )


@auth_required
async def handle_list_notifications(message: types.Message, user: User):
    notifications = await get_user_notifications(user.telegram_id)
    if not notifications:
        return await message.reply(f"You have no notifications yet")
    rendered_notifications = [
        f"{i + 1} - {await _render_notification(notification)}"
        for i, notification in enumerate(notifications)
    ]
    await message.reply("\n".join(rendered_notifications))


@auth_required
async def handle_remove_notification(message: types.Message, user: User):
    message_args = message.get_args()
    if not message_args:
        await message.reply(f"You need to specify notification index")
        return

    try:
        notification_index = int(message_args[0]) - 1
        notification = await pop_notification_from_user_by_index(user.telegram_id, notification_index)
        return await message.reply(
            f"Notification {await _render_notification(notification)} has been successfully removed"
        )

    except ValueError:
        return await message.reply(f"Notification index must be a digit")
    except IncorrectNotificationIndexError:
        return await message.reply(f"There is no such notification")

