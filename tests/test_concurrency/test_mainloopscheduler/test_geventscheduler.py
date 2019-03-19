import pytest
import unittest

from datetime import datetime, timedelta

from rx.concurrency.mainloopscheduler import GEventScheduler


gevent = pytest.importorskip("gevent")


class TestGEventScheduler(unittest.TestCase):

    def test_gevent_schedule_now(self):
        scheduler = GEventScheduler()
        hub = gevent.get_hub()
        diff = scheduler.now - datetime.utcfromtimestamp(hub.loop.now())
        assert abs(diff) < timedelta(milliseconds=1)

    def test_gevent_schedule_action(self):
        scheduler = GEventScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        gevent.sleep(0.1)
        assert ran is True

    def test_gevent_schedule_action_due(self):
        scheduler = GEventScheduler()
        starttime = datetime.now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = datetime.now()

        scheduler.schedule_relative(0.2, action)

        gevent.sleep(0.3)
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(seconds=0.18)

    def test_gevent_schedule_action_cancel(self):
        scheduler = GEventScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        gevent.sleep(0.1)
        assert ran is False
