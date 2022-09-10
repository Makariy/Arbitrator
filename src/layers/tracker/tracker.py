from typing import List
import logging
import asyncio

from lib.database import Database
from lib.exchanges import ToTrack
from layers.tracker.trackers.base_tracker import BaseTracker


logger = logging.getLogger(__package__)
database = Database()


def get_all_trackers() -> List[BaseTracker.__class__]:
    from .trackers.kucoin.kucoin_tracker import KuCoinTracker
    from .trackers.huobi.huobi_tracker import HuobiTracker
    return [
        KuCoinTracker,
        HuobiTracker
    ]


def create_tracker(to_track: ToTrack) -> BaseTracker:
    trackers = list(filter(lambda a: a.EXCHANGE == to_track.exchange, get_all_trackers()))
    if trackers:
        tracker = trackers[0]
        return tracker(input=to_track.input, output=to_track.output)
    raise ValueError(f"There is no such tracker to track {to_track.input}-{to_track.output} on {to_track.exchange}")


def create_trackers(to_track_list: List[ToTrack]) -> List[BaseTracker]:
    return [create_tracker(to_track) for to_track in to_track_list]


async def _run_tracker(tracker: BaseTracker):
    logger.info(f"Start tracking from {tracker.input} to {tracker.output}")
    await tracker.connect()
    await tracker.start_tracking()


def run_tracker(tracker: BaseTracker):
    asyncio.run(_run_tracker(tracker))


def run_trackers(trackers: List[BaseTracker]):
    loop = asyncio.get_event_loop()
    tasks = []
    for tracker in trackers:
        tasks.append(loop.create_task(_run_tracker(tracker)))
    loop.run_until_complete(asyncio.gather(*tasks))

