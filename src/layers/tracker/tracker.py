import logging
import asyncio

from lib.database import Database
from lib.symbols import Symbols
from layers.tracker.trackers.kucoin.kucoin_tracker import KuCoinTracker


logger = logging.getLogger(__package__)
database = Database()


async def _run_tracker(args):
    input = Symbols[args.input]
    output = Symbols[args.output]
    logger.info(f"Start tracking from {input} to {output}")
    kucoin_tracker = KuCoinTracker(input, output)
    await kucoin_tracker.connect()
    await kucoin_tracker.start_tracking()


def run_tracker(args):
    asyncio.run(_run_tracker(args))
