from typing import List
from aiogram import types

from lib.symbol import Symbol
from bot.services.utils import get_current_price

from config import NOTIFICATION_EXCHANGE


async def _get_symbols_by_name(raw_symbols: List[str]) -> List[Symbol]:
    symbols = []
    for raw_symbol in raw_symbols:
        try:
            symbols.append(Symbol(raw_symbol))
        except ValueError:
            raise ValueError(f"Symbol: '{raw_symbol}' does not exist")
    return symbols


async def format_price_for_symbol(price: float, symbol: Symbol):
    return f"{symbol.value} - {price if price is not None else 'not found'}"


async def handle_get_price(message: types.Message):
    try:
        args = message.get_args().split()
        if len(args) < 1:
            raise ValueError("Arguments count was less than 1")
        symbols = await _get_symbols_by_name(args)
    except ValueError as e:
        return await message.reply(str(e))

    formatted_prices = "\n".join([
        await format_price_for_symbol(
            price=await get_current_price(NOTIFICATION_EXCHANGE, input=symbol, output=Symbol.USDT),
            symbol=symbol
        ) for symbol in symbols
    ])
    await message.reply(formatted_prices)

