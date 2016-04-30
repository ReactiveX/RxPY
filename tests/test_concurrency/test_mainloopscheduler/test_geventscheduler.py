import unittest
from datetime import datetime, timedelta

from nose import SkipTest
try:
    import gevent
except ImportError:
    raise SkipTest("GEvent not installed")

from rx.concurrency import GEventScheduler


class TestGEventScheduler(unittest.TestCase):

    def test_gevent_schedule_now(self):
        scheduler = GEventScheduler()
        res = scheduler.now - datetime.now()
        assert(res < timedelta(seconds=1))

    def test_gevent_schedule_action(self):
        scheduler = GEventScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        gevent.sleep(0.1)
        assert(ran[0] is True)

    def test_gevent_schedule_action_due(self):
        scheduler = GEventScheduler()
        starttime = datetime.now()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.now()

        scheduler.schedule_relative(200, action)

        gevent.sleep(0.3)
        diff = endtime[0]-starttime
        assert(diff > timedelta(seconds=0.18))

    def test_gevent_schedule_action_cancel(self):
        scheduler = GEventScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(10, action)
        d.dispose()

        gevent.sleep(0.1)
        assert(not ran[0])
