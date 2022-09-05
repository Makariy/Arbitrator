from abc import ABC, abstractmethod
from websockets import WebSocketClientProtocol


class BaseTracker(ABC):
    connection: WebSocketClientProtocol = None

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def start_tracking(self):
        pass
