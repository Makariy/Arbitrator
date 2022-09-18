from typing import List
from abc import ABC, abstractmethod
from websockets import WebSocketClientProtocol
from lib.token import TokenExchanges

from lib.database import Database
from lib.database.key_manager import create_key

from lib.symbols import Symbols
from lib.exchanges import Exchanges, ToTrack


database = Database()


class BaseDispatcher(ABC):
    EXCHANGE: Exchanges
    input: Symbols
    output: Symbols
    channel: str

    def __init__(self, input: Symbols, output: Symbols):
        self.input = input
        self.output = output

    async def save_token_exchanges_to_database(self, token_exchanges: TokenExchanges):
        key = create_key(self.EXCHANGE, self.input, self.output)
        await database.set(key, token_exchanges.json())

    async def init(self, *args, **kwargs):
        pass

    @abstractmethod
    async def subscribe(self, connection: WebSocketClientProtocol):
        pass

    @abstractmethod
    async def handle_message(self, message):
        pass


class BaseTracker(ABC):
    EXCHANGE: Exchanges
    connection: WebSocketClientProtocol = None
    dispatchers: List[BaseDispatcher]

    def __init__(self):
        self.dispatchers = []

    @abstractmethod
    async def init(self, to_track_list: List[ToTrack]):
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def start_tracking(self):
        pass
