from lib.symbols import Symbols
from lib.exchanges import Exchanges


def create_key(exchange: Exchanges, input: Symbols, output: Symbols) -> str:
    return f"{exchange.value}_{input.value}-{output.value}"

