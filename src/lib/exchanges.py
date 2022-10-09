from enum import Enum
from dataclasses import dataclass
from .symbols import Symbols


class Exchanges(Enum):
    kucoin = "KuCoin"
    huobi = "Huobi"
    binance = "Binance"


@dataclass
class ToTrack:
    exchange: Exchanges
    input: Symbols
    output: Symbols

