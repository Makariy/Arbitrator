from typing import List, Optional, Dict

from dataclasses import dataclass

from lib.exchanges import ToTrack

from lib.symbols import Symbols
from lib.exchanges import Exchanges

from bot.services.utils import get_current_price


@dataclass
class ExchangeStats:
    price: float


class DispatcherCacheManager:
    _exchange_stats: Dict[str, ExchangeStats] = {}

    def __init__(self, tracking_exchanges: List[ToTrack]):
        self.tracking_exchanges = tracking_exchanges

    async def _create_key_for_to_track_item(self, to_track: ToTrack) -> str:
        return f"{to_track.exchange.name}_{to_track.input.name}-{to_track.output.name}"

    async def _update_to_track_item_cache(self, to_track: ToTrack):
        price = await get_current_price(
            exchange=to_track.exchange,
            input=to_track.input,
            output=to_track.output
        )
        self._exchange_stats[await self._create_key_for_to_track_item(to_track)] = ExchangeStats(
            price=price
        )

    async def update_cache(self):
        for to_track in self.tracking_exchanges:
            await self._update_to_track_item_cache(to_track)

    async def get_stats_for_token_exchange(
            self,
            input: Symbols,
            output: Symbols,
            exchange: Exchanges
    ) -> Optional[ExchangeStats]:
        stats = self._exchange_stats.get(
            await self._create_key_for_to_track_item(ToTrack(exchange=exchange, input=input, output=output))
        )
        if not stats:
            ...

        return stats


