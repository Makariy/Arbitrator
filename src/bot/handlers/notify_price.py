from typing import Callable, Awaitable

from enum import Enum
import logging
import asyncio
from aiogram import types

from lib.symbols import Symbols
from lib.exchanges import Exchanges

from .utils import get_current_price


logger = logging.getLogger(__package__)


async def _wait_for_assertion(assertion: Callable[[], Awaitable]):
    while True:
        if await assertion():
            return
        await asyncio.sleep(1)


class Directions(Enum):
    UP = "UP"
    DOWN = "DOWN"

    @staticmethod
    def get_direction_by_value(value: str):
        for item in list(Directions):
            if item.value == value:
                return item


async def _wait_for_price_to_overcome_limit(
        get_price_func: Callable[[], Awaitable],
        limit: float,
        direction: Directions,
        message: types.Message
):
    async def _assert_price_got_to_limit():
        _current_price = await get_price_func()
        if direction == Directions.UP and _current_price >= limit:
            return True
        elif direction == Directions.DOWN and _current_price <= limit:
            return True

    await _wait_for_assertion(_assert_price_got_to_limit)
    current_price = await get_price_func()
    await message.reply(f"Current price overcame the limit: {current_price}")


async def handle_notify_price(message: types.Message):
    try:
        args = message.get_args().split()
        if len(args) != 3:
            raise ValueError(f"Arguments count is not 3: len(args) == {len(args)}")

        symbol = Symbols.get_symbol_by_value(args[0])
        limit = float(args[1])
        direction = Directions.get_direction_by_value(args[2].upper())
        if direction is None:
            raise ValueError("You specified a wrong direction")
    except ValueError:
        await message.reply(f"You need to specify <symbol> <limit> <UP or DOWN>")
        return

    await message.reply(
        f"Started waiting for {symbol.value} to go {'above' if direction == Directions.UP else 'below'} " + str(limit)
    )
    asyncio.create_task(
        _wait_for_price_to_overcome_limit(
            lambda: get_current_price(Exchanges.binance, symbol, Symbols.USDT),
            limit,
            direction,
            message
        )
    )



