from typing import List, Optional, Dict

from dataclasses import dataclass

from lib.exchange import Exchange

from lib.symbol import Symbol
from lib.platform import Platform

from bot.services.utils import get_current_price


@dataclass
class ExchangeStats:
    price: float


class DispatcherCacheManager:
    _exchange_stats: Dict[str, ExchangeStats] = {}

    def __init__(self, tracking_exchanges: List[Exchange]):
        self.tracking_exchanges = tracking_exchanges

    async def _create_key_for_to_track_item(self, to_track: Exchange) -> str:
        return f"{to_track.platform.name}_{to_track.input.name}-{to_track.output.name}"

    async def _update_to_track_item_cache(self, to_track: Exchange):
        price = await get_current_price(
            exchange=to_track.platform,
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
            input: Symbol,
            output: Symbol,
            exchange: Platform
    ) -> Optional[ExchangeStats]:
        stats = self._exchange_stats.get(
            await self._create_key_for_to_track_item(Exchange(platform=exchange, input=input, output=output))
        )
        if not stats:
            ...

        return stats


