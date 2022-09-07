from enum import Enum
from dataclasses import dataclass
from .symbols import Symbols


class Exchanges(Enum):
    kucoin = "KuCoin"


@dataclass
class ToTrack:
    exchange: Exchanges
    input: Symbols
    output: Symbols

