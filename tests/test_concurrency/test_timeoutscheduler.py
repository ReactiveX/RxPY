import unittest

from datetime import timedelta
from time import sleep

from rx.concurrency import TimeoutScheduler
from rx.internal.basic import default_now


class TestTimeoutScheduler(unittest.TestCase):

    def test_timeout_now(self):
        scheduler = TimeoutScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_timeout_schedule_action(self):
        scheduler = TimeoutScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        sleep(0.1)
        assert ran is True

    def test_timeout_schedule_action_due(self):
        scheduler = TimeoutScheduler()
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(timedelta(milliseconds=200), action)

        sleep(0.3)
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_timeout_schedule_action_cancel(self):
        ran = False
        scheduler = TimeoutScheduler()

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(timedelta(milliseconds=1), action)
        d.dispose()

        sleep(0.1)
        assert ran is False
