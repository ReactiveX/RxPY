import os
import threading
import unittest
from datetime import timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler import TimeoutScheduler

CI = os.getenv("CI") is not None


class TestTimeoutScheduler(unittest.TestCase):
    def test_timeout_singleton(self) -> None:
        scheduler = [TimeoutScheduler(), TimeoutScheduler.singleton()]
        assert scheduler[0] is scheduler[1]

        gate = [threading.Semaphore(0), threading.Semaphore(0)]
        scheduler: list[TimeoutScheduler | None] = [None, None]

        def run(idx: int) -> None:
            scheduler[idx] = TimeoutScheduler()
            gate[idx].release()

        for idx in (0, 1):
            threading.Thread(target=run, args=(idx,)).start()
            gate[idx].acquire()

        assert scheduler[0] is not None
        assert scheduler[1] is not None
        assert scheduler[0] is scheduler[1]

    def test_timeout_extend(self) -> None:
        class MyScheduler(TimeoutScheduler):
            pass

        scheduler = [
            MyScheduler(),
            MyScheduler.singleton(),
            TimeoutScheduler.singleton(),
        ]
        assert scheduler[0] is scheduler[1]
        assert scheduler[0] is not scheduler[2]

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_timeout_now(self) -> None:
        scheduler = TimeoutScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_timeout_now_units(self) -> None:
        scheduler = TimeoutScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_timeout_schedule_action(self) -> None:
        scheduler = TimeoutScheduler()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        scheduler.schedule(action)

        sleep(0.1)
        assert ran is True

    def test_timeout_schedule_action_due(self) -> None:
        scheduler = TimeoutScheduler()
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

    def test_timeout_schedule_action_cancel(self) -> None:
        ran = False
        scheduler = TimeoutScheduler()

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        d = scheduler.schedule_relative(timedelta(milliseconds=300), action)
        d.dispose()

        sleep(0.1)
        assert ran is False
