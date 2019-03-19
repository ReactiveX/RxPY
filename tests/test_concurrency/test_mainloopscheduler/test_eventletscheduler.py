import pytest
import unittest

from datetime import datetime, timedelta

from rx.concurrency.mainloopscheduler import EventLetEventScheduler


eventlet = pytest.importorskip("eventlet")
if eventlet:
    import eventlet.hubs


class TestEventLetEventScheduler(unittest.TestCase):

    def test_eventlet_schedule_now(self):
        scheduler = EventLetEventScheduler()
        hub = eventlet.hubs.get_hub()
        diff = scheduler.now - datetime.utcfromtimestamp(hub.clock())
        assert abs(diff) < timedelta(milliseconds=1)

    def test_eventlet_schedule_action(self):
        scheduler = EventLetEventScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        eventlet.sleep(0.1)
        assert ran is True

    def test_eventlet_schedule_action_due(self):
        scheduler = EventLetEventScheduler()
        starttime = datetime.now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = datetime.now()

        scheduler.schedule_relative(0.2, action)

        eventlet.sleep(0.3)
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(seconds=0.18)

    def test_eventlet_schedule_action_cancel(self):
        scheduler = EventLetEventScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(1.0, action)
        d.dispose()

        eventlet.sleep(0.01)
        assert ran is False

    def test_eventlet_schedule_action_periodic(self):
        scheduler = EventLetEventScheduler()
        period = 0.05
        counter = 3

        def action(state):
            nonlocal counter
            if counter:
                counter -= 1

        scheduler.schedule_periodic(period, action)
        eventlet.sleep(0.3)
        assert counter == 0

    def test_eventlet_schedule_action_periodic_now(self):
        scheduler = EventLetEventScheduler()
        period = 0
        counter = 3

        def action(state):
            nonlocal counter
            counter -= 1

        scheduler.schedule_periodic(period, action)
        eventlet.sleep(0.3)
        assert counter == 2
