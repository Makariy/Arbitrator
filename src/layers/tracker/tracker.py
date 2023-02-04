from typing import List
import logging
import asyncio
from websockets.exceptions import WebSocketException

from lib.database import Database
from lib.platform import Platform
from lib.exchange import Exchange
from layers.tracker.trackers.base import BaseTracker


logger = logging.getLogger(__package__)
database = Database()


def get_all_trackers() -> List[BaseTracker.__class__]:
    from .trackers.kucoin.kucoin_tracker import KuCoinTracker
    from .trackers.huobi.huobi_tracker import HuobiTracker
    from .trackers.binance.binance_tracker import BinanceTracker

    return [
        KuCoinTracker,
        HuobiTracker,
        BinanceTracker
    ]


async def get_tracker_by_platform(platform: Platform) -> BaseTracker.__class__:
    for tracker in get_all_trackers():
        if tracker.PLATFORM == platform:
            return tracker

    raise ValueError(f"No such tracker for {platform}")


async def create_tracker_for_platform(platform: Platform, exchanges: List[Exchange]) -> BaseTracker:
    exchanges_to_track_list = list(filter(lambda a: a.platform == platform, exchanges))
    tracker_cls = await get_tracker_by_platform(platform)
    tracker = tracker_cls()
    await tracker.init(exchanges_to_track_list)
    return tracker


async def create_trackers_for_exchanges(exchanges: List[Exchange]) -> List[BaseTracker]:
    platforms = set(map(lambda a: a.platform, exchanges))
    trackers = []
    for platform in platforms:
        trackers.append(await create_tracker_for_platform(platform, exchanges))
    return trackers


async def start_tracker(tracker: BaseTracker):
    while True:
        try:
            logger.info(f"Starting tracker: {tracker}")
            await tracker.connect()
            await tracker.start_tracking()
        except (ConnectionError, WebSocketException) as error:
            logger.warning(f"Connection error occurred on tracker '{tracker.PLATFORM}': {error}")


async def _run_trackers(tracking_exchanges: List[Exchange]):
    trackers = await create_trackers_for_exchanges(tracking_exchanges)
    tasks = []
    for tracker in trackers:
        tasks.append(asyncio.create_task(start_tracker(tracker)))
    await asyncio.gather(*tasks)


def _run_multiprocessing_tracker(tracker: BaseTracker):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(start_tracker(tracker))
    logger.error(f"Running tracker {tracker} stopped")


def _run_multiprocessing_trackers(exchanges_to_track: List[Exchange]):
    from multiprocessing import Pool
    pool = Pool()
    trackers = asyncio.run(create_trackers_for_exchanges(exchanges_to_track))
    pool.map(_run_multiprocessing_tracker, trackers)


def run_trackers(exchanges_to_track: List[Exchange]):
    asyncio.run(_run_trackers(exchanges_to_track))
    # _run_multiprocessing_trackers(to_track_list)
