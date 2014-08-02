import asyncio
import unittest

from datetime import datetime, timedelta
from time import sleep
from rx.concurrency import MainloopScheduler

# def test_timeout_now():
#     res = MainloopScheduler.now() - datetime.utcnow()
#     assert res < timedelta(microseconds=1000)

class TestMainloopScheduler(unittest.TestCase):

    def test_mainloop_schedule_action(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = MainloopScheduler(loop)
            ran = False

            def action(scheduler, state):
                nonlocal ran
                ran = True
            scheduler.schedule(action)

            yield from asyncio.sleep(0.1, loop=loop)
            assert(ran == True)

        loop.run_until_complete(go())
        #loop.close()

    def test_timeout_schedule_action_due(self):
        loop = asyncio.get_event_loop()

        @asyncio.coroutine
        def go():
            scheduler = MainloopScheduler(loop)
            starttime = loop.time()
            endtime = None

            def action(scheduler, state):
                nonlocal endtime
                endtime = loop.time()

            scheduler.schedule_relative(0.2, action)

            yield from asyncio.sleep(0.3, loop=loop)
            diff = endtime-starttime
            assert(diff > 0.18)

        loop.run_until_complete(go())
        loop.close()


    def test_timeout_schedule_action_cancel(self):
        ran = False
        scheduler = TimeoutScheduler()

        def action(scheduler, state):
            nonlocal ran
            ran = True
        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        yield from asyncio.sleep(0.1, loop=loop)
        assert (not ran)
