from enum import Enum
from typing import List


class Symbols(Enum):
    USDT = "USDT"

    LUNA = "LUNA"
    SOL = "SOL"
    SHIB = "SHIB"
    MIR = "MIR"
    AVAX = "AVAX"
    ATOM = "ATOM"
    EOS = "EOS"
    XRP = "XRP"
    WAVES = "WAVES"

    DOGE = "DOGE"
    ETH = "ETH"
    BTC = "BTC"
    EUR = "EUR"
    RUB = "RUB"

    @staticmethod
    def get_symbol_by_value(value: str):
        for item in list(Symbols):
            if item.value == value:
                return item

        return None


async def join_symbols(symbols: List[Symbols]) -> str:
    return "-".join(map(lambda a: a.value, symbols))

