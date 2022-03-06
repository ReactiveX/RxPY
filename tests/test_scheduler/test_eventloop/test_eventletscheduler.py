import os
import unittest
from datetime import datetime, timedelta
from time import sleep

import pytest

from reactivex.scheduler.eventloop import EventletScheduler

eventlet = pytest.importorskip("eventlet")
CI = os.getenv("CI") is not None


class TestEventletScheduler(unittest.TestCase):
    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_eventlet_schedule_now(self):
        scheduler = EventletScheduler(eventlet)
        hub = eventlet.hubs.get_hub()
        diff = scheduler.now - datetime.utcfromtimestamp(hub.clock())
        assert abs(diff) < timedelta(milliseconds=1)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_eventlet_schedule_now_units(self):
        scheduler = EventletScheduler(eventlet)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_eventlet_schedule_action(self):
        scheduler = EventletScheduler(eventlet)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        eventlet.sleep(0.1)
        assert ran is True

    def test_eventlet_schedule_action_due(self):
        scheduler = EventletScheduler(eventlet)
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
        scheduler = EventletScheduler(eventlet)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(1.0, action)
        d.dispose()

        eventlet.sleep(0.01)
        assert ran is False

    def test_eventlet_schedule_action_periodic(self):
        scheduler = EventletScheduler(eventlet)
        period = 0.05
        counter = 3

        def action(state):
            nonlocal counter
            if counter:
                counter -= 1

        scheduler.schedule_periodic(period, action)
        eventlet.sleep(0.3)
        assert counter == 0
