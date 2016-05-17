from nose import SkipTest

import rx
asyncio = rx.config['asyncio']
if asyncio is None:
    raise SkipTest("asyncio not available")

try:
    from trollius import From
except ImportError:
    raise SkipTest("trollius.From not available")

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

            ran = [False]

            def action(scheduler, state):
                ran[0] = True

            scheduler.schedule(action)

            yield From(asyncio.sleep(0.1, loop=loop))
            assert(ran[0] is True)

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_due(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop)
            starttime = loop.time()

            endtime = [None]

            def action(scheduler, state):
                endtime[0] = loop.time()

            scheduler.schedule_relative(200, action)

            yield From(asyncio.sleep(0.3, loop=loop))
            diff = endtime[0] - starttime
            assert(diff > 0.18)

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_cancel(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop)

            ran = [False]

            def action(scheduler, state):
                ran[0] = True

            d = scheduler.schedule_relative(10, action)
            d.dispose()

            yield From(asyncio.sleep(0.1, loop=loop))
            assert(not ran[0])

        loop.run_until_complete(go())
