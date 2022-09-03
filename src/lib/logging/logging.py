import logging

import config
from .configurator import Configurator


def configure_logging():
    logging.basicConfig(level=config.LOG_LEVEL)

    if not hasattr(config, "LOGGING"):
        raise NotImplementedError("Need to specify the 'LOGGING' configuration in the config file")

    configurator = Configurator()
    configurator.init_loggers(config.LOGGING)

