import os
import sys
import logging

from lib.symbols import Symbols
from lib.exchanges import Exchanges, ToTrack


LOG_LEVEL = logging.INFO


REDIS_URL = "redis://0.0.0.0:6379/"

KUCOIN_BASE_HTTP_URL = "https://api.kucoin.com"

HUOBI_BASE_WEBSOCKETS_URL = "wss://api.huobi.pro/ws"
HUOBI_ACCESS_KEY = os.environ.get('HUOBI_ACCESS_KEY')


LOGGING = {
    "formatters": {
        "default": {
            "instance": logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        }
    },

    "handlers": {
        "file": {
            "level": logging.DEBUG,
            "instance": logging.FileHandler(filename="log.log", mode="w"),
            "formatter": "default"
        },
        "stdout": {
            "level": logging.DEBUG,
            "instance": logging.StreamHandler(stream=sys.stdout),
            "formatter": "default"
        }
    },

    "modules": {
        "layers.tracker": {
            "level": logging.DEBUG,
            "handlers": ["stdout"]
        }
    }
}

MAX_EXCHANGE_DEPTH = 2

TO_TRACK = [
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.BTC, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.BTC, output=Symbols.USDT)
]

