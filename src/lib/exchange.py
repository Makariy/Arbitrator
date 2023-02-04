from dataclasses import dataclass

from lib.platform import Platform
from lib.symbol import Symbol


@dataclass
class Exchange:
    platform: Platform
    input: Symbol
    output: Symbol
