import unittest
from datetime import datetime, timedelta

from nose import SkipTest
try:
    from tornado import ioloop
except ImportError:
    raise SkipTest("Tornado not installed")

from rx.concurrency import IOLoopScheduler


class TestIOLoopScheduler(unittest.TestCase):

    def test_ioloop_schedule_now(self):
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        res = scheduler.now - datetime.now()
        assert(res < timedelta(seconds=1))

    def test_ioloop_schedule_action(self):
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        def done():
            assert(ran[0] is True)
            loop.stop()
        loop.call_later(0.1, done)

        loop.start()

    def test_ioloop_schedule_action_due(self):
        loop = ioloop.IOLoop.instance()

        scheduler = IOLoopScheduler(loop)
        starttime = loop.time()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = loop.time()

        scheduler.schedule_relative(200, action)

        def done():
            diff = endtime[0]-starttime
            assert(diff > 0.18)
            loop.stop()
        loop.call_later(0.3, done)

        loop.start()

    def test_ioloop_schedule_action_cancel(self):
        loop = ioloop.IOLoop.instance()

        ran = [False]
        scheduler = IOLoopScheduler(loop)

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(10, action)
        d.dispose()

        def done():
            assert(not ran[0])
            loop.stop()
        loop.call_later(0.1, done)

        loop.start()
