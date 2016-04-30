import unittest

from datetime import datetime, timedelta
from time import sleep
from rx.concurrency import TimeoutScheduler


class TestTimeoutScheduler(unittest.TestCase):
    def test_timeout_now(self):
        scheduler = TimeoutScheduler()
        res = scheduler.now - datetime.utcnow()
        assert res < timedelta(microseconds=1000)

    def test_timeout_schedule_action(self):
        scheduler = TimeoutScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True

        scheduler.schedule(action)

        sleep(0.1)
        assert (ran[0] is True)

    def test_timeout_schedule_action_due(self):
        scheduler = TimeoutScheduler()
        starttime = datetime.utcnow()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.utcnow()

        scheduler.schedule_relative(timedelta(milliseconds=200), action)

        sleep(0.3)
        diff = endtime[0]-starttime
        assert(diff > timedelta(milliseconds=180))

    def test_timeout_schedule_action_cancel(self):
        ran = [False]
        scheduler = TimeoutScheduler()

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(timedelta(milliseconds=1), action)
        d.dispose()

        sleep(0.1)
        assert (not ran[0])
