from aiogram import types


HELP_TEXT = """
/help - display this message
/start <name> - register in this bot with name <name>

/best_chains - list the best chains for arbitration 
/chain <symbol 1> <symbol 2> <symbol 3> ... - print current profit percent from arbitration over symbols 1,2,3,...

/price <symbol> - get current <symbol> price
/currencies - list tracking currencies

/notify <symbol> <price> <direction> - receive a notification when <symbol>'s price goes above or below the <price>
/notifications - list pending notifications 
/remove <index> <index> ... - delete notifications on indexes <index> <index> ... 
"""


async def handle_help(message: types.Message):
    await message.bot.send_message(
        text=HELP_TEXT,
        chat_id=message.from_id
    )

