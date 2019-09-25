import unittest
import asyncio
from rx import operators as ops
from rx.subject import Subject

from rx.scheduler.eventloop import AsyncIOScheduler


class TestFlatMapAsync(unittest.TestCase):

    def test_flat_map_async(self):
        actual_next = None
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOScheduler(loop=loop)

        def mapper(i):
            async def _mapper(i):
                return i + 1

            return asyncio.ensure_future(_mapper(i))

        def on_next(i):
            nonlocal actual_next
            actual_next = i

        async def test_flat_map():
            x = Subject()
            x.pipe(ops.flat_map(mapper)).subscribe(on_next, scheduler=scheduler)
            x.on_next(10)
            await asyncio.sleep(0.1)

        loop.run_until_complete(test_flat_map())
        assert actual_next == 11
