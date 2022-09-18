import os
import sys
import logging

from lib.symbols import Symbols
from lib.exchanges import Exchanges, ToTrack


LOG_LEVEL = logging.ERROR
INPUT_TOKEN = Symbols.USDT


REDIS_URL = "redis://0.0.0.0:6379/"

KUCOIN_BASE_HTTP_URL = "https://api.kucoin.com"

HUOBI_BASE_WEBSOCKETS_URL = "wss://api.huobi.pro/ws"
HUOBI_ACCESS_KEY = os.environ.get('HUOBI_ACCESS_KEY')

TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")


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
        },
    },

    "modules": {
        "layers.tracker": {
            "level": logging.INFO,
            "handlers": ["stdout"]
        },
        "websockets.client": {
            "level": logging.INFO,
            "handlers": ["stdout"]
        }
    }
}

MAX_EXCHANGE_DEPTH = 2

TO_TRACK = [
    # KuCoin
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.MIR, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.LUNA, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.SOL, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.SHIB, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.AVAX, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.ATOM, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.XRP, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.WAVES, output=Symbols.USDT),

    ToTrack(exchange=Exchanges.kucoin, input=Symbols.BTC, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.ETH, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.kucoin, input=Symbols.DOGE, output=Symbols.USDT),

    ToTrack(exchange=Exchanges.kucoin, input=Symbols.SHIB, output=Symbols.DOGE),

    # Huobi
    ToTrack(exchange=Exchanges.huobi, input=Symbols.MIR, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.LUNA, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.SOL, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.SHIB, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.AVAX, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.ATOM, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.EOS, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.XRP, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.WAVES, output=Symbols.USDT),

    ToTrack(exchange=Exchanges.huobi, input=Symbols.DOGE, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.BTC, output=Symbols.USDT),
    ToTrack(exchange=Exchanges.huobi, input=Symbols.ETH, output=Symbols.USDT),
]

