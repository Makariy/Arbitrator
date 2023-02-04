from enum import Enum
from typing import List


class Symbol(Enum):
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



async def join_symbols(symbols: List[Symbol]) -> str:
    return "-".join(map(lambda a: a.value, symbols))

