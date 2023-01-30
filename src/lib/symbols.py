from enum import Enum
from typing import List


class Symbols(Enum):
    USDT = "USDT"

    AVAX = "AVAX"
    ATOM = "ATOM"
    DOGE = "DOGE"
    SOL = "SOL"
    APT = "APT"
    XRP = "XRP"
    MAGIC = "MAGIC"
    MINA = "MINA"
    KAVA = "KAVA"
    NEAR = "NEAR"

    LUNA = "LUNA"
    SHIB = "SHIB"
    MIR = "MIR"
    EOS = "EOS"
    WAVES = "WAVES"

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

