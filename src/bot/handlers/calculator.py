from aiogram import types


async def _calc(enter: float, stop: float, risk: float) -> float:
    loss = abs(stop - enter)
    loss_percent = loss / enter
    return risk / loss_percent


async def handle_calculate(message: types.Message):
    try:
        args = map(lambda a: float(a), message.get_args())
        enter, stop, risk = args
        margin = await _calc(enter, stop, risk / 100)
        return await message.bot.send_message(
            text=f"You need to use: x{margin} margin",
            chat_id=message.from_id
        )
    except ValueError:
        return await message.bot.send_message(
            text="You need to specify <start> <stop> <risk>",
            chat_id=message.from_id
        )
