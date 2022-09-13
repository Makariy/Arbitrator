from typing import List
import logging
import asyncio

from lib.database import Database
from lib.exchanges import ToTrack, Exchanges
from layers.tracker.trackers.base import BaseTracker


logger = logging.getLogger(__package__)
database = Database()


def get_all_trackers() -> List[BaseTracker.__class__]:
    from .trackers.kucoin.kucoin_tracker import KuCoinTracker
    from .trackers.huobi.huobi_tracker import HuobiTracker
    return [
        KuCoinTracker,
        HuobiTracker
    ]


async def get_tracker_by_exchange(exchange: Exchanges) -> BaseTracker.__class__:
    for tracker in get_all_trackers():
        if tracker.EXCHANGE == exchange:
            return tracker

    raise ValueError(f"No such tracker for {exchange}")


async def create_trackers_for_exchange(exchange: Exchanges, to_track_list: List[ToTrack]) -> BaseTracker:
    exchanges_to_track_list = list(filter(lambda a: a.exchange == exchange, to_track_list))
    tracker_cls = await get_tracker_by_exchange(exchange)
    tracker = tracker_cls()
    await tracker.init(exchanges_to_track_list)
    return tracker


async def create_trackers(to_track_list: List[ToTrack]) -> List[BaseTracker]:
    exchanges = set(map(lambda a: a.exchange, to_track_list))
    trackers = []
    for exchange in exchanges:
        trackers.append(await create_trackers_for_exchange(exchange, to_track_list))
    return trackers


async def start_tracker(tracker: BaseTracker):
    while True:
        try:
            logger.info(f"Starting tracker: {tracker}")
            await tracker.connect()
            await tracker.start_tracking()
        except ConnectionError as error:
            logger.warning(f"Connection error occurred: {error}")


async def _run_trackers(to_track_list: List[ToTrack]):
    trackers = await create_trackers(to_track_list)
    tasks = []
    for tracker in trackers:
        tasks.append(asyncio.create_task(start_tracker(tracker)))
    await asyncio.gather(*tasks)


def run_trackers(to_track_list: List[ToTrack]):
    asyncio.run(_run_trackers(to_track_list))

