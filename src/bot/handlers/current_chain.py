import logging
from aiogram import types

from lib.symbol import Symbol

from layers.analyzer.chain_services import get_current_chain
from layers.analyzer.logger import format_chain


logger = logging.getLogger(__package__)


async def handle_current_chain(message: types.Message):
    args = message.get_args().split()
    if len(args) < 3:
        await message.reply("You need to specify: {symbol} {symbol} {symbol} ...")
        return

    symbols = []
    for symbol_name in args:
        try:
            symbols.append(Symbol(symbol_name))
        except ValueError:
            await message.reply(f"No such symbol: {symbol_name}")
            return

    chain = await get_current_chain(symbols)
    if chain is None:
        await message.reply(f"No such chain")
        return

    logger.info(f"Sending current chain for {[symbol.value for symbol in symbols]}")

    await message.reply(await format_chain(chain))

