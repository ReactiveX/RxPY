from nose import SkipTest

import rx
asyncio = rx.config['asyncio']
if asyncio is None:
    raise SkipTest("asyncio not available")

import unittest

from datetime import datetime, timedelta
from rx.concurrency import AsyncIOScheduler


class TestAsyncIOScheduler(unittest.TestCase):

    def test_asyncio_schedule_now(self):
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOScheduler(loop)
        res = scheduler.now - datetime.now()
        assert(res < timedelta(seconds=1))

    def test_asyncio_schedule_action(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop)
            ran = False

            def action(scheduler, state):
                nonlocal ran
                ran = True
            scheduler.schedule(action)

            yield from asyncio.sleep(0.1)
            assert(ran is True)

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_due(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop)
            starttime = loop.time()
            endtime = None

            def action(scheduler, state):
                nonlocal endtime
                endtime = loop.time()

            scheduler.schedule_relative(200, action)

            yield from asyncio.sleep(0.3)
            diff = endtime-starttime
            assert(diff > 0.18)

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_cancel(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            ran = False
            scheduler = AsyncIOScheduler(loop)

            def action(scheduler, state):
                nonlocal ran
                ran = True
            d = scheduler.schedule_relative(10, action)
            d.dispose()

            yield from asyncio.sleep(0.1)
            assert(not ran)

        loop.run_until_complete(go())
