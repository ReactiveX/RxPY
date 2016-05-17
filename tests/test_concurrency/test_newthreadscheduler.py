import unittest

from datetime import datetime, timedelta
from time import sleep
from rx.concurrency import NewThreadScheduler


class TestNewThreadScheduler(unittest.TestCase):
    def test_new_thread_now(self):
        scheduler = NewThreadScheduler()
        res = scheduler.now - datetime.utcnow()
        assert res < timedelta(microseconds=1000)

    def test_new_thread_schedule_action(self):
        scheduler = NewThreadScheduler()
        ran = [False]

        def action(scheduler, state):
            ran[0] = True

        scheduler.schedule(action)

        sleep(0.1)
        assert (ran[0] is True)

    def test_new_thread_schedule_action_due(self):
        scheduler = NewThreadScheduler()
        starttime = datetime.utcnow()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.utcnow()

        scheduler.schedule_relative(timedelta(milliseconds=200), action)

        sleep(0.3)
        diff = endtime[0]-starttime
        assert(diff > timedelta(milliseconds=180))

    def test_new_thread_schedule_action_cancel(self):
        ran = [False]
        scheduler = NewThreadScheduler()

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(timedelta(milliseconds=1), action)
        d.dispose()

        sleep(0.1)
        assert (not ran[0])
