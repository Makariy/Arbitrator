import logging
from aiogram import types
from lib.symbols import Symbols
from layers.analyzer.chain_services import get_all_best_chains, get_current_chain
from layers.analyzer.logger import format_chains, format_chain


logger = logging.getLogger(__package__)


async def handle_current_chain(message: types.Message):
    args = message.get_args().split()
    if len(args) < 3:
        await message.reply("You need to specify: {symbol} {symbol} {symbol} ...")
        return

    symbols = [Symbols.get_symbol_by_value(arg) for arg in args]

    if None in [symbols]:
        bad_symbol_index = symbols.index(None)
        await message.reply(f"No such symbol: {args[bad_symbol_index]}")
        return

    chain = await get_current_chain(symbols)
    if chain is None:
        await message.reply(f"No such chain")
        return

    logger.info(f"Sending current chain for {[symbol.value for symbol in symbols]}")

    await message.reply(await format_chain(chain))


async def handle_best_chains(message: types.Message):
    best_chains = await get_all_best_chains()
    formatted_chains = await format_chains(best_chains)
    logger.info(f"Sending best chains")
    await message.reply(formatted_chains)
