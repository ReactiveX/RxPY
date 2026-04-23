import os
import threading
import unittest
from datetime import timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler import ThreadPoolScheduler

thread_pool_scheduler = ThreadPoolScheduler()

CI = os.getenv("CI") is not None


class TestThreadPoolScheduler(unittest.TestCase):
    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_threadpool_now(self) -> None:
        scheduler = ThreadPoolScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=5)

    def test_threadpool_now_units(self) -> None:
        scheduler = ThreadPoolScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_schedule_action(self) -> None:
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            assert ident != threading.current_thread().ident
            evt.set()
            return None

        nt.schedule(action)
        evt.wait()

    def test_schedule_action_due_relative(self) -> None:
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            assert ident != threading.current_thread().ident
            evt.set()
            return None

        nt.schedule_relative(timedelta(milliseconds=200), action)
        evt.wait()

    def test_schedule_action_due_0(self) -> None:
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            assert ident != threading.current_thread().ident
            evt.set()
            return None

        nt.schedule_relative(0.1, action)
        evt.wait()

    def test_schedule_action_absolute(self) -> None:
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            assert ident != threading.current_thread().ident
            evt.set()
            return None

        nt.schedule_absolute(default_now() + timedelta(milliseconds=100), action)
        evt.wait()

    def test_schedule_action_cancel(self) -> None:
        nt = thread_pool_scheduler
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        d = nt.schedule_relative(0.05, action)
        d.dispose()

        sleep(0.1)
        assert ran is False
