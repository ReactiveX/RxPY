import unittest
from datetime import datetime, timedelta
import pytest

from rx.concurrency.mainloopscheduler import EventLetEventScheduler

eventlet = pytest.importorskip("eventlet")


class TestEventLetEventScheduler(unittest.TestCase):

    def test_eventlet_schedule_now(self):
        scheduler = EventLetEventScheduler()
        res = scheduler.now - datetime.now()
        assert res < timedelta(seconds=1)

    def test_eventlet_schedule_action(self):
        scheduler = EventLetEventScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        eventlet.sleep(0.1)
        assert ran[0] is True

    def test_eventlet_schedule_action_due(self):
        scheduler = EventLetEventScheduler()
        starttime = datetime.now()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.now()

        scheduler.schedule_relative(0.2, action)

        eventlet.sleep(0.3)
        diff = endtime[0] - starttime
        assert diff > timedelta(seconds=0.18)

    def test_eventlet_schedule_action_cancel(self):
        scheduler = EventLetEventScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(1.0, action)
        d.dispose()

        eventlet.sleep(0.01)
        assert not ran[0]

    def test_eventlet_schedule_action_periodic(self):
        scheduler = EventLetEventScheduler()
        period = 0.05
        counter = [3]

        def action(state):
            if counter[0]:
                counter[0] -= 1

        scheduler.schedule_periodic(period, action)
        eventlet.sleep(0.3)
        assert counter[0] == 0

    def test_eventlet_schedule_action_periodic_now(self):
        scheduler = EventLetEventScheduler()
        period = 0
        num_times = [3]

        def action(state):
            num_times[0] -= 1

        scheduler.schedule_periodic(period, action)
        eventlet.sleep(0.3)
        assert num_times[0] == 2
