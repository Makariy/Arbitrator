from aiogram import types

from bot.services.user.db_services import (
    create_user,
    UserAlreadyExistsError
)


async def handle_create_session(message: types.Message):
    message_args = message.get_args()
    if not message_args:
        return await message.reply(f"You need to specify a username for your session")

    try:
        username = message_args[0]
        user = await create_user(telegram_id=message.from_id, username=username)
        return await message.reply(f"Session was created successfully")
    except UserAlreadyExistsError:
        return await message.reply(f"You are already registered")
