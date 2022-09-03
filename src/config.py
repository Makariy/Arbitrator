import logging
import sys


REDIS_URL = "redis://0.0.0.0"

LOG_LEVEL = logging.DEBUG

KUCOIN_BASE_HTTP_URL = "https://api.kucoin.com"
KUCOIN_BASE_WEBSOCKET_URL = ""


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
            "handlers": ["file", "stdout"]
        }
    }
}

