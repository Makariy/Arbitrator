from aiogram import types


async def _calc(enter: float, stop: float, risk: float) -> float:
    loss = abs(stop - enter)
    loss_percent = loss / enter
    return risk / loss_percent


async def _calc_profit(enter, target, balance, margin) -> float:
    return abs(enter - target) / enter * balance * margin


async def _calc_profit_percent(balance, profit) -> float:
    return profit / balance * 100


async def handle_calculate(message: types.Message):
    try:
        args = map(lambda a: float(a), message.get_args().split())
        enter, stop, risk, *extra = args
        margin = await _calc(enter, stop, risk / 100)
        response = f"You need to use: x{margin:.3f} margin"

        if extra:
            target, balance = extra
            profit = await _calc_profit(enter, target, balance, margin)
            profit_percent = await _calc_profit_percent(balance, profit)
            response = f"{response}\n" \
                       f"And your profit will be {profit:.3f} USDT ({profit_percent:.3f}%)"

        return await message.bot.send_message(
            text=response,
            chat_id=message.from_id
        )
    except ValueError:
        return await message.bot.send_message(
            text="You need to specify: \n<start> <stop> <risk> and <target> <balance> (optional)",
            chat_id=message.from_id
        )
