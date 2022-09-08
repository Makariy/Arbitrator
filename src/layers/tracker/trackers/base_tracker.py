from abc import ABC, abstractmethod
from websockets import WebSocketClientProtocol
from lib.symbols import Symbols
from lib.exchanges import Exchanges


class BaseTracker(ABC):
    connection: WebSocketClientProtocol = None
    input: Symbols
    output: Symbols
    EXCHANGE: Exchanges

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def start_tracking(self):
        pass
