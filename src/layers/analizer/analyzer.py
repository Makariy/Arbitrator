from typing import List
import logging

from lib.symbols import Symbols
from lib.exchanges import Exchanges

from layers.tracker.models import TokenExchanges, TokenExchange, Token
from token_exchanges_fetcher import get_token_exchanges

from config import ALL_EXCHANGES


logger = logging.getLogger(__package__)


class GraphConstructor:
    pass

class Analyzer:
    pass
