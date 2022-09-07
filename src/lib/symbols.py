from enum import Enum


class Symbols(Enum):
    USDT = "USDT"
    ETH = "ETH"
    BTC = "BTC"
    EUR = "EUR"
    RUB = "RUB"

    @staticmethod
    def get_symbol_by_value(self, value: str):
        for item in list(Symbols):
            if item.value == value:
                return item

        return None

