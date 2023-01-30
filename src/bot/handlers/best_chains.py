import logging
from aiogram import types
from layers.analyzer.chain_services import get_all_best_chains
from layers.analyzer.logger import format_chains


logger = logging.getLogger(__package__)


async def handle_best_chains(message: types.Message):
    best_chains = await get_all_best_chains()
    formatted_chains = await format_chains(best_chains)
    logger.info(f"Sending best chains")
    await message.reply(
        formatted_chains if formatted_chains else "There are no chains for now"
    )

