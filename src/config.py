import logging
import sys


LOG_LEVEL = logging.DEBUG

KUCOIN_BASE_URL = "https://api.kucoin.com"


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

