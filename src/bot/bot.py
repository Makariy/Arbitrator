import asyncio
import logging
from aiogram import Bot, Dispatcher, executor

from .handlers.best_chains import handle_best_chains
from .handlers.current_chain import handle_current_chain

from .handlers.help import handle_help
from .handlers.sessions import handle_create_session
from .handlers.notify_price import (
    handle_list_notifications,
    handle_remove_notification,
    handle_create_price_limit_notification
)
from .handlers.get_price import handle_get_price
from .handlers.list_currencies import handle_list_currencies

from .handlers.calculator import handle_calculate

from bot.services.notificaions.dispatcher.dispatcher import run_dispatcher
import config


logger = logging.getLogger(__package__)


def create_bot() -> Bot:
    return Bot(token=config.TELEGRAM_API_TOKEN)


def _create_dispatcher(bot: Bot) -> Dispatcher:
    dispatcher = Dispatcher(bot, loop=asyncio.get_event_loop())
    dispatcher.message_handler(commands=["chain"])(handle_current_chain)
    dispatcher.message_handler(commands=["best_chains"])(handle_best_chains)

    dispatcher.message_handler(commands=["start"])(handle_create_session)
    dispatcher.message_handler(commands=["help"])(handle_help)

    dispatcher.message_handler(commands=["price"])(handle_get_price)
    dispatcher.message_handler(commands=["currencies"])(handle_list_currencies)

    dispatcher.message_handler(commands=["calc"])(handle_calculate)

    dispatcher.message_handler(commands=["notify"])(handle_create_price_limit_notification)
    dispatcher.message_handler(commands=["notifications"])(handle_list_notifications)
    dispatcher.message_handler(commands=["remove"])(handle_remove_notification)
    return dispatcher


def _run_bot(bot: Bot):
    dispatcher = _create_dispatcher(bot)
    dispatcher.loop.create_task(run_dispatcher(bot))
    executor.start_polling(dispatcher, skip_updates=True)


def run_bot():
    bot = create_bot()
    logger.info(f"Starting the bot")
    _run_bot(bot)
