from typing import Dict, List
from dataclasses import dataclass

import logging
import config


@dataclass
class Formatter:
    name: str
    instance: logging.Formatter


@dataclass
class Handler:
    name: str
    instance: logging.Handler


@dataclass
class Logger:
    name: str
    level: int
    instance: logging.Logger


class ConfigParser:
    @staticmethod
    def ensure_contains(dictionary: Dict, keys: List[str], error_message: str = "There is no such {key} in the dict"):
        for key in keys:
            if key not in dictionary.keys():
                raise ValueError(error_message.format({"key": key}))


class Configurator:
    formatters = {}
    handlers = {}
    loggers = {}

    def init_loggers(self, config: Dict):
        ConfigParser.ensure_contains(config, ["formatters", "handlers", "modules"],
                                     error_message="You must specify formatters, "
                                                   "handlers and modules in the logging config")

        self.formatters = self.create_formatters(config['formatters'])
        self.handlers = self.create_handlers(config['handlers'])
        self.loggers = self.create_loggers(config['modules'])

    def create_formatters(self, formatters_config: Dict) -> Dict[str, Formatter]:
        formatters = {}
        for formatter_name, formatter_config in formatters_config.items():
            ConfigParser.ensure_contains(formatter_config, ["instance"], "Every formatter must contain 'instance'")
            formatters[formatter_name] = Formatter(
                name=formatter_name,
                instance=formatter_config["instance"]
            )
        return formatters

    def create_handlers(self, handlers_config: Dict) -> Dict[str, Handler]:
        handlers = {}
        for handler_name, config_data in handlers_config.items():
            ConfigParser.ensure_contains(config_data, ["level", "instance", "formatter"],
                                         "Every handler must contain 'instance' and 'formatter'")

            instance = config_data["instance"]
            instance.setLevel(config_data["level"])
            formatter = self._get_formatter(config_data['formatter'])
            instance.setFormatter(formatter.instance)

            handlers[handler_name] = Handler(name=handler_name, instance=instance)

        return handlers

    def create_loggers(self, loggers_config: Dict) -> Dict[str, logging.Logger]:
        loggers = {}
        for package_name, logger_config in loggers_config.items():
            ConfigParser.ensure_contains(logger_config, ["level", "handlers"])

            logger = logging.getLogger(package_name)
            for handler_name in logger_config['handlers']:
                handler = self._get_handler(handler_name)
                logger.addHandler(handler.instance)
            logger.setLevel(logger_config['level'] or config.LOG_LEVEL)
            logger.propagate = logger_config.get("propagate") or False
            loggers[package_name] = logger

        return loggers

    def _get_handler(self, name: str):
        handler = self.handlers.get(name)
        if not handler:
            raise ValueError(f"There is no such handler '{name}'")
        return handler

    def _get_formatter(self, name):
        formatter = self.formatters.get(name)
        if not formatter:
            raise ValueError(f"There is no such formatter '{name}'")
        return formatter
