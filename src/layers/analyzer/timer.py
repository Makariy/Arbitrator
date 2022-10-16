import asyncio
import time


class Timer:
    def __init__(self, period: float):
        self.period = period
        self.start_time = -1

    async def start(self):
        self.start_time = time.time()

    async def wait_for_next_iteration(self):
        now = time.time()
        to_sleep = self.period - (now - self.start_time)

        if to_sleep > 0:
            await asyncio.sleep(to_sleep)
