import os
import threading
import unittest
from datetime import timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler import NewThreadScheduler

CI = os.getenv("CI") is not None


class TestNewThreadScheduler(unittest.TestCase):
    def test_new_thread_now(self) -> None:
        scheduler = NewThreadScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=5)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_new_thread_now_units(self) -> None:
        scheduler = NewThreadScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_new_thread_schedule_action(self) -> None:
        scheduler = NewThreadScheduler()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        scheduler.schedule(action)

        sleep(0.1)
        assert ran is True

    def test_new_thread_schedule_action_due(self) -> None:
        scheduler = NewThreadScheduler()
        starttime = default_now()
        endtime = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal endtime
            endtime = default_now()
            return None

        scheduler.schedule_relative(timedelta(milliseconds=200), action)

        sleep(0.4)
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_new_thread_schedule_action_cancel(self) -> None:
        ran = False
        scheduler = NewThreadScheduler()

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        d = scheduler.schedule_relative(timedelta(milliseconds=1), action)
        d.dispose()

        sleep(0.2)
        assert ran is False

    def test_new_thread_schedule_periodic(self) -> None:
        scheduler = NewThreadScheduler()
        gate = threading.Semaphore(0)
        period = 0.05
        counter = 3

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                gate.release()
            return None

        scheduler.schedule_periodic(period, action, counter)
        gate.acquire()
        assert counter == 0

    def test_new_thread_schedule_periodic_cancel(self) -> None:
        scheduler = NewThreadScheduler()
        period = 0.1
        counter = 4

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            return None

        disp = scheduler.schedule_periodic(period, action, counter)
        sleep(0.4)
        disp.dispose()
        assert 0 <= counter < 4
