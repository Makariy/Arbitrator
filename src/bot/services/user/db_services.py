from typing import Optional, List

from lib.database import Database
from lib.database.key_manager import USER_KEY
from lib.database.key_manager import create_key_for_user_by_telegram_id

from bot.services.user.models import User
from .models import User, NOTIFICATION_TYPES

import logging


logger = logging.getLogger(__package__)


database = Database()


class UserAlreadyExistsError(Exception):
    pass


async def get_user_from_db_by_telegram_id(telegram_id: int) -> Optional[User]:
    key = await create_key_for_user_by_telegram_id(telegram_id)
    raw_user = await database.get(key)
    if raw_user is None:
        return None

    user = User.parse_raw(raw_user)
    return user


async def _get_all_users_telegram_ids() -> List[int]:
    keys = await database.keys(f"{USER_KEY}_*")
    try:
        telegram_ids = [int(key[key.index("_") + 1:]) for key in keys]
        return telegram_ids
    except ValueError:
        logger.fatal(f"Could not parse telegram_ids for users")
        return []


async def get_all_users() -> List[User]:
    telegram_ids = await _get_all_users_telegram_ids()
    return [await get_user_from_db_by_telegram_id(telegram_id) for telegram_id in telegram_ids]


async def save_user_to_db(user: User):
    key = await create_key_for_user_by_telegram_id(user.telegram_id)
    await database.set(key, user.json())


async def create_user(telegram_id: int, username: str):
    if await get_user_from_db_by_telegram_id(telegram_id) is not None:
        raise UserAlreadyExistsError()

    user = User(
        telegram_id=telegram_id,
        username=username,
        notifications=[]
    )
    await save_user_to_db(user)
    return user


async def add_notification_to_user(user: User, notification: NOTIFICATION_TYPES):
    user.notifications.append(notification)


async def remove_notification_for_user(user: User, notification: NOTIFICATION_TYPES):
    user.notifications.remove(notification)
