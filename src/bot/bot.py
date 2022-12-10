import logging
from aiogram import Bot, Dispatcher, executor
from .handlers.best_chains import handle_best_chains
from .handlers.current_chain import handle_current_chain
from .handlers.notify_price import handle_notify_price
from .handlers.get_price import handle_get_price
import config


logger = logging.getLogger(__package__)


def create_bot() -> Bot:
    return Bot(token=config.TELEGRAM_API_TOKEN)


def _create_dispatcher(bot: Bot) -> Dispatcher:
    dispatcher = Dispatcher(bot)
    dispatcher.message_handler(commands=["chain"])(handle_current_chain)
    dispatcher.message_handler(commands=["best_chains"])(handle_best_chains)
    dispatcher.message_handler(commands=["notify"])(handle_notify_price)
    dispatcher.message_handler(commands=["price"])(handle_get_price)
    return dispatcher


def _run_bot(bot: Bot):
    dispatcher = _create_dispatcher(bot)
    executor.start_polling(dispatcher, skip_updates=True)


def run_bot():
    bot = create_bot()
    logger.info(f"Starting the bot")
    _run_bot(bot)
