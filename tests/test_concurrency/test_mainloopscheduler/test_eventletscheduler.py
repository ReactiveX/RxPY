import unittest
from datetime import datetime, timedelta

from nose import SkipTest
try:
    import eventlet
except ImportError:
    raise SkipTest("Eventlet not installed")

from rx.concurrency import EventLetEventScheduler

class TestEventLetEventScheduler(unittest.TestCase):

    def test_eventlet_schedule_now(self):
        scheduler = EventLetEventScheduler()
        res = scheduler.now() - datetime.now()
        assert(res < timedelta(seconds=1))

    def test_eventlet_schedule_action(self):
        scheduler = EventLetEventScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        eventlet.sleep(0.1)
        assert(ran[0] == True)

    def test_eventlet_schedule_action_due(self):
        scheduler = EventLetEventScheduler()
        starttime = datetime.now()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.now()

        scheduler.schedule_relative(0.2, action)

        eventlet.sleep(0.3)
        diff = endtime[0]-starttime
        assert(diff > timedelta(seconds=0.18))

    def test_eventlet_schedule_action_cancel(self):
        scheduler = EventLetEventScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        eventlet.sleep(0.1)
        assert(not ran[0])
