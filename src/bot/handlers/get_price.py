from typing import List
from aiogram import types

from lib.symbols import Symbols
from lib.exchanges import Exchanges
from bot.services.utils import get_current_price


async def _get_symbols_by_name(raw_symbols: List[str]) -> List[Symbols]:
    symbols = []
    for raw_symbol in raw_symbols:
        symbol = Symbols.get_symbol_by_value(raw_symbol)
        if symbol is None:
            raise ValueError(f"Symbol: '{raw_symbol}' does not exist")
        symbols.append(symbol)
    return symbols


async def format_price_for_symbol(price: float, symbol: Symbols):
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
            price=await get_current_price(Exchanges.binance, input=symbol, output=Symbols.USDT),
            symbol=symbol
        ) for symbol in symbols
    ])
    await message.reply(formatted_prices)

