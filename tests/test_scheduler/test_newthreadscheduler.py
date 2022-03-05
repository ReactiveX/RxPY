import os
import threading
import unittest
from datetime import timedelta
from time import sleep

import pytest

from reactivex.internal.basic import default_now
from reactivex.scheduler import NewThreadScheduler

CI = os.getenv("CI") is not None


class TestNewThreadScheduler(unittest.TestCase):
    def test_new_thread_now(self):
        scheduler = NewThreadScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=5)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_new_thread_now_units(self):
        scheduler = NewThreadScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_new_thread_schedule_action(self):
        scheduler = NewThreadScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        sleep(0.1)
        assert ran is True

    def test_new_thread_schedule_action_due(self):
        scheduler = NewThreadScheduler()
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(timedelta(milliseconds=200), action)

        sleep(0.4)
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_new_thread_schedule_action_cancel(self):
        ran = False
        scheduler = NewThreadScheduler()

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(timedelta(milliseconds=1), action)
        d.dispose()

        sleep(0.2)
        assert ran is False

    def test_new_thread_schedule_periodic(self):
        scheduler = NewThreadScheduler()
        gate = threading.Semaphore(0)
        period = 0.05
        counter = 3

        def action(state: int):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                gate.release()

        scheduler.schedule_periodic(period, action, counter)
        gate.acquire()
        assert counter == 0

    def test_new_thread_schedule_periodic_cancel(self):
        scheduler = NewThreadScheduler()
        period = 0.1
        counter = 4

        def action(state: int):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1

        disp = scheduler.schedule_periodic(period, action, counter)
        sleep(0.4)
        disp.dispose()
        assert 0 <= counter < 4
