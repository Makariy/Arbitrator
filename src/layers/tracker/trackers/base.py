from typing import List
from abc import ABC, abstractmethod
from websockets import WebSocketClientProtocol
from lib.models import TokenExchanges

from lib.database import Database
from lib.database.key_manager import create_key_for_current_exchange

from lib.symbol import Symbol
from lib.platform import Platform
from lib.exchange import Exchange

database = Database()


class BaseDispatcher(ABC):
    PLATFORM: Platform
    input: Symbol
    output: Symbol
    channel: str

    def __init__(self, input: Symbol, output: Symbol):
        self.input = input
        self.output = output

    async def save_token_exchanges_to_database(self, token_exchanges: TokenExchanges):
        key = await create_key_for_current_exchange(self.PLATFORM, self.input, self.output)
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
    PLATFORM: Platform
    connection: WebSocketClientProtocol = None
    dispatchers: List[BaseDispatcher]

    def __init__(self):
        self.dispatchers = []

    @abstractmethod
    async def init(self, to_track_list: List[Exchange]):
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def start_tracking(self):
        pass
