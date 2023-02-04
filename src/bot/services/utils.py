from typing import Optional, Callable, Coroutine

from aiogram import types

from lib.platform import Platform
from lib.symbol import Symbol
from layers.analyzer.token_exchanges_fetcher import get_token_exchanges

from .user.models import User
from .user.db_services import get_user_from_db_by_telegram_id


async def get_current_price(exchange: Platform, input: Symbol, output: Symbol) -> Optional[float]:
    exchanges = await get_token_exchanges(exchange, input, output)
    if exchanges:
        current_exchange = exchanges.token_exchanges[0]
        return current_exchange.output.price / current_exchange.input.price
    return None


def auth_required(func: Callable[[types.Message, User], Coroutine]):
    async def wrapper(message: types.Message):
        user = await get_user_from_db_by_telegram_id(message.from_id)
        if user is not None:
            return await func(message, user)

        return await message.reply(f"You are not authorized. Write /start to create a session.")

    return wrapper

