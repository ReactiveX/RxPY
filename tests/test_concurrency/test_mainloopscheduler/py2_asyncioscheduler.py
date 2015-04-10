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
from time import sleep
from rx.concurrency import AsyncIOScheduler

class TestAsyncIOScheduler(unittest.TestCase):

    def test_asyncio_schedule_now(self):
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOScheduler(loop)
        res = scheduler.now() - datetime.now()
        assert(res < timedelta(seconds=1))

    def test_asyncio_schedule_action(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop)

            class Nonlocal:
                ran = False

            def action(scheduler, state):
                Nonlocal.ran = True

            scheduler.schedule(action)

            yield From(asyncio.sleep(0.1, loop=loop))
            assert(Nonlocal.ran == True)

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_due(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop)
            starttime = loop.time()

            class Nonlocal:
               endtime = None

            def action(scheduler, state):
                Nonlocal.endtime = loop.time()

            scheduler.schedule_relative(0.2, action)

            yield From(asyncio.sleep(0.3, loop=loop))
            diff = Nonlocal.endtime-starttime
            assert(diff > 0.18)

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_cancel(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            class Nonlocal:
                ran = False
            scheduler = AsyncIOScheduler(loop)

            def action(scheduler, state):
                Nonlocal.ran = True
            d = scheduler.schedule_relative(0.01, action)
            d.dispose()

            yield From(asyncio.sleep(0.1, loop=loop))
            assert(not Nonlocal.ran)

        loop.run_until_complete(go())
