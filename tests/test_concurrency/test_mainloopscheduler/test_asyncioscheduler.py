import unittest

import asyncio
import threading
from datetime import datetime, timedelta

from rx.concurrency.mainloopscheduler import AsyncIOScheduler


class TestAsyncIOScheduler(unittest.TestCase):

    def test_asyncio_schedule_now(self):
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOScheduler(loop)
        diff = scheduler.now - datetime.utcfromtimestamp(loop.time())
        assert abs(diff) < timedelta(milliseconds=1)

    def test_asyncio_schedule_now_units(self):
        loop = asyncio.get_event_loop()
        scheduler = AsyncIOScheduler(loop)
        diff = scheduler.now
        yield from asyncio.sleep(0.1, loop=loop)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

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

            yield from asyncio.sleep(0.1, loop=loop)
            assert ran is True

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_threadsafe(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop, threadsafe=True)
            ran = False

            def action(scheduler, state):
                nonlocal ran
                ran = True

            def schedule():
                scheduler.schedule(action)

            threading.Thread(target=schedule).start()

            yield from asyncio.sleep(0.1, loop=loop)
            assert ran is True

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

            scheduler.schedule_relative(0.2, action)

            yield from asyncio.sleep(0.3, loop=loop)
            assert endtime is not None
            diff = endtime - starttime
            assert diff > 0.18

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_due_threadsafe(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = AsyncIOScheduler(loop, threadsafe=True)
            starttime = loop.time()
            endtime = None

            def action(scheduler, state):
                nonlocal endtime
                endtime = loop.time()

            def schedule():
                scheduler.schedule_relative(0.2, action)

            threading.Thread(target=schedule).start()

            yield from asyncio.sleep(0.3, loop=loop)
            assert endtime is not None
            diff = endtime - starttime
            assert diff > 0.18

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

            d = scheduler.schedule_relative(0.05, action)
            d.dispose()

            yield from asyncio.sleep(0.3, loop=loop)
            assert ran is False

        loop.run_until_complete(go())

    def test_asyncio_schedule_action_cancel_threadsafe(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            ran = False
            scheduler = AsyncIOScheduler(loop, threadsafe=True)

            def action(scheduler, state):
                nonlocal ran
                ran = True

            def schedule():
                d = scheduler.schedule_relative(0.05, action)
                d.dispose()

            threading.Thread(target=schedule).start()

            yield from asyncio.sleep(0.3, loop=loop)
            assert ran is False

        loop.run_until_complete(go())
