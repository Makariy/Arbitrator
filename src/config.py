import os
import sys
import logging

from lib.symbol import Symbol
from lib.platform import Platform
from lib.exchange import Exchange

LOG_LEVEL = logging.INFO


INPUT_TOKEN = Symbol.USDT
ANALYZE_PERIOD = 1  # In seconds
MINIMAL_PROFIT_PERCENT = -1

NOTIFICATION_EXCHANGE = Platform.huobi
NOTIFICATION_CHECK_PERIOD = 1  # In Seconds


REDIS_URL = os.environ.get("REDIS_URL", "redis://0.0.0.0:6379/")

KUCOIN_BASE_HTTP_URL = "https://api.kucoin.com"
HUOBI_BASE_WEBSOCKETS_URL = "wss://api.huobi.pro/ws"
BINANCE_BASE_WEBSOCKETS_URL = "wss://stream.binance.com:9443/ws"


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
        "layers.tracker.kucoin.kucoin_pinger": {
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

TRACKING_EXCHANGES = [
    # KuCoin
    # Exchange(platform=Platform.kucoin, input=Symbol.MIR, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.LUNA, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.SHIB, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.WAVES, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.SHIB, output=Symbol.DOGE),
    #
    # Exchange(platform=Platform.kucoin, input=Symbol.BTC, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.ETH, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.DOGE, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.SOL, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.AVAX, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.ATOM, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.XRP, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.APT, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.MAGIC, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.MINA, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.KAVA, output=Symbol.USDT),
    # Exchange(platform=Platform.kucoin, input=Symbol.NEAR, output=Symbol.USDT),

    # Huobi
    # Exchange(platform=Platform.huobi, input=Symbol.MIR, output=Symbol.USDT),
    # Exchange(platform=Platform.huobi, input=Symbol.LUNA, output=Symbol.USDT),
    # Exchange(platform=Platform.huobi, input=Symbol.SHIB, output=Symbol.USDT),
    # Exchange(platform=Platform.huobi, input=Symbol.EOS, output=Symbol.USDT),
    # Exchange(platform=Platform.huobi, input=Symbol.WAVES, output=Symbol.USDT),
    # 
    Exchange(platform=Platform.huobi, input=Symbol.BTC, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.ETH, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.DOGE, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.SOL, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.AVAX, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.ATOM, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.XRP, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.APT, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.MAGIC, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.MINA, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.KAVA, output=Symbol.USDT),
    Exchange(platform=Platform.huobi, input=Symbol.NEAR, output=Symbol.USDT),


    # Binance
    # Exchange(platform=Platform.binance, input=Symbol.MIR, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.LUNA, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.SHIB, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.EOS, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.WAVES, output=Symbol.USDT),
    #
    # Exchange(platform=Platform.binance, input=Symbol.BTC, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.ETH, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.DOGE, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.SOL, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.AVAX, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.ATOM, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.XRP, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.APT, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.MAGIC, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.MINA, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.KAVA, output=Symbol.USDT),
    # Exchange(platform=Platform.binance, input=Symbol.NEAR, output=Symbol.USDT),
]

