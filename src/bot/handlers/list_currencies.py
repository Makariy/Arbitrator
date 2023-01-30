from aiogram import types

from config import TO_TRACK


async def handle_list_currencies(message: types.Message):
    to_track_symbols = set(map(lambda to_track: to_track.input, TO_TRACK))
    response = f"I am tracking:\n" + "\n".join(map(lambda symbol: symbol.value, to_track_symbols))
    return await message.bot.send_message(
        text=response,
        chat_id=message.from_id
    )

