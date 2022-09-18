from typing import List
from lib.exchanges import ToTrack
from layers.tracker.trackers.base import BaseTracker, BaseDispatcher


class ByBitTracker(BaseTracker):
    async def init(self, to_track_list: List[ToTrack]):
        pass

    async def connect(self):
        pass

    async def start_tracking(self):
        pass



