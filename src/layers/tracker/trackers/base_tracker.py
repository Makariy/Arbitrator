from abc import ABC, abstractmethod
from websockets import WebSocketClientProtocol
from lib.symbols import Symbols


class BaseTracker(ABC):
    connection: WebSocketClientProtocol = None
    input: Symbols
    output: Symbols

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def start_tracking(self):
        pass
