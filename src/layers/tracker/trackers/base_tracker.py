from abc import ABC, abstractmethod
from websockets import WebSocketClientProtocol
from layers.tracker.models import TokenExchanges

from lib.database import Database
from lib.database.key_manager import create_key

from lib.symbols import Symbols
from lib.exchanges import Exchanges


database = Database()


class BaseTracker(ABC):
    connection: WebSocketClientProtocol = None
    input: Symbols
    output: Symbols
    EXCHANGE: Exchanges

    def __init__(self, input: Symbols, output: Symbols):
        self.input = input
        self.output = output

    async def save_token_exchanges_to_database(self, token_exchanges: TokenExchanges):
        key = create_key(self.EXCHANGE, self.input, self.output)
        await database.set(key, token_exchanges.json())

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def start_tracking(self):
        pass
