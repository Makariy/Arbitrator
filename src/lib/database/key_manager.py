from lib.symbols import Symbols


def create_key(exchange_name: str, input: Symbols, output: Symbols) -> str:
    return f"{exchange_name}_{input.value}-{output.value}"

