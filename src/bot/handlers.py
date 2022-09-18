from aiogram import types
from lib.symbols import Symbols
from layers.analyzer.logger.logger import get_all_best_chains, \
    get_best_chain, \
    format_best_chains, \
    format_best_chain


async def handle_best_chain(message: types.Message):
    args = message.get_args().split()
    if len(args) < 3:
        await message.reply("You need to specify: {symbol} {symbol} {symbol} ...")
        return

    symbols = [Symbols.get_symbol_by_value(arg) for arg in args]

    if None in [symbols]:
        bad_symbol_index = symbols.index(None)
        await message.reply(f"No such symbol: {args[bad_symbol_index]}")
        return

    best_chain = await get_best_chain(symbols)
    if best_chain is None:
        await message.reply(f"No such chain")
        return

    await message.reply(await format_best_chain(best_chain))


async def handle_best_chains(message: types.Message):
    best_chains = await get_all_best_chains()
    formatted_chains = await format_best_chains(best_chains)
    await message.reply(formatted_chains)
