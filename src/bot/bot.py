import logging
from aiogram import Bot, Dispatcher, executor
from .handlers import handle_current_chain, handle_best_chains
import config


logger = logging.getLogger(__package__)


def create_bot() -> Bot:
    return Bot(token=config.TELEGRAM_API_TOKEN)


def _create_dispatcher(bot: Bot) -> Dispatcher:
    dispatcher = Dispatcher(bot)
    dispatcher.message_handler(commands=["chain"])(handle_current_chain)
    dispatcher.message_handler(commands=["best_chains"])(handle_best_chains)
    return dispatcher


def _run_bot(bot: Bot):
    dispatcher = _create_dispatcher(bot)
    executor.start_polling(dispatcher, skip_updates=True)


def run_bot():
    bot = create_bot()
    logger.info(f"Starting the bot")
    _run_bot(bot)
