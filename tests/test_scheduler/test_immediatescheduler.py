import os
import threading
import unittest
from datetime import timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.disposable import Disposable
from reactivex.internal.basic import default_now
from reactivex.internal.constants import DELTA_ZERO
from reactivex.internal.exceptions import WouldBlockException
from reactivex.scheduler import ImmediateScheduler

CI = os.getenv("CI") is not None


class TestImmediateScheduler(unittest.TestCase):
    def test_immediate_singleton(self) -> None:
        scheduler = [ImmediateScheduler(), ImmediateScheduler.singleton()]
        assert scheduler[0] is scheduler[1]

        gate = [threading.Semaphore(0), threading.Semaphore(0)]
        scheduler: list[ImmediateScheduler | None] = [None, None]

        def run(idx: int) -> None:
            scheduler[idx] = ImmediateScheduler()
            gate[idx].release()

        for idx in (0, 1):
            threading.Thread(target=run, args=(idx,)).start()
            gate[idx].acquire()

        assert scheduler[0] is not None
        assert scheduler[1] is not None
        assert scheduler[0] is scheduler[1]

    def test_immediate_extend(self) -> None:
        class MyScheduler(ImmediateScheduler):
            pass

        scheduler = [
            MyScheduler(),
            MyScheduler.singleton(),
            ImmediateScheduler.singleton(),
        ]
        assert scheduler[0] is scheduler[1]
        assert scheduler[0] is not scheduler[2]

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_immediate_now(self) -> None:
        scheduler = ImmediateScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) <= timedelta(milliseconds=1)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_immediate_now_units(self) -> None:
        scheduler = ImmediateScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_immediate_scheduleaction(self) -> None:
        scheduler = ImmediateScheduler()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        scheduler.schedule(action)
        assert ran

    def test_immediate_schedule_action_error(self) -> None:
        scheduler = ImmediateScheduler()

        class MyException(Exception):
            pass

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            raise MyException()

        with pytest.raises(MyException):
            return scheduler.schedule(action)

    def test_immediate_schedule_action_due_error(self) -> None:
        scheduler = ImmediateScheduler()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        with pytest.raises(WouldBlockException):
            scheduler.schedule_relative(0.1, action)

        assert ran is False

    def test_immediate_simple1(self) -> None:
        scheduler = ImmediateScheduler()
        xx = 0

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal xx
            xx = state
            return Disposable()

        scheduler.schedule(action, 42)
        assert xx == 42

    def test_immediate_simple2(self) -> None:
        scheduler = ImmediateScheduler()
        xx = 0

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal xx
            xx = state
            return Disposable()

        scheduler.schedule_absolute(default_now(), action, 42)
        assert xx == 42

    def test_immediate_simple3(self) -> None:
        scheduler = ImmediateScheduler()
        xx = 0

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal xx
            xx = state
            return Disposable()

        scheduler.schedule_relative(DELTA_ZERO, action, 42)
        assert xx == 42

    def test_immediate_recursive1(self) -> None:
        scheduler = ImmediateScheduler()
        xx = 0
        yy = 0

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal xx
            xx = state

            def inner_action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
                nonlocal yy
                yy = state
                return Disposable()

            return scheduler.schedule(inner_action, 43)

        scheduler.schedule(action, 42)
        assert xx == 42
        assert yy == 43

    def test_immediate_recursive2(self) -> None:
        scheduler = ImmediateScheduler()
        xx = 0
        yy = 0

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal xx
            xx = state

            def inner_action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
                nonlocal yy
                yy = state
                return Disposable()

            return scheduler.schedule_absolute(default_now(), inner_action, 43)

        scheduler.schedule_absolute(default_now(), action, 42)

        assert xx == 42
        assert yy == 43

    def test_immediate_recursive3(self) -> None:
        scheduler = ImmediateScheduler()
        xx = 0
        yy = 0

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            nonlocal xx
            xx = state

            def inner_action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
                nonlocal yy
                yy = state
                return Disposable()

            return scheduler.schedule_relative(DELTA_ZERO, inner_action, 43)

        scheduler.schedule_relative(DELTA_ZERO, action, 42)

        assert xx == 42
        assert yy == 43
