import os
import unittest
from datetime import timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler import TrampolineScheduler

CI = os.getenv("CI") is not None


class TestTrampolineScheduler(unittest.TestCase):
    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_trampoline_now(self) -> None:
        scheduler = TrampolineScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_trampoline_now_units(self) -> None:
        scheduler = TrampolineScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_trampoline_schedule(self) -> None:
        scheduler = TrampolineScheduler()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        assert ran is True

    def test_trampoline_schedule_block(self) -> None:
        scheduler = TrampolineScheduler()
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            nonlocal ran
            ran = True

        t = scheduler.now
        scheduler.schedule_relative(0.2, action)
        t = scheduler.now - t
        assert ran is True
        assert t >= timedelta(seconds=0.2)

    def test_trampoline_schedule_error(self) -> None:
        scheduler = TrampolineScheduler()

        class MyException(Exception):
            pass

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            raise MyException()

        with pytest.raises(MyException):
            scheduler.schedule(action)

    def test_trampoline_schedule_nested(self) -> None:
        scheduler = TrampolineScheduler()
        ran = False

        def action(
            scheduler: abc.SchedulerBase, state: Any = None
        ) -> abc.DisposableBase:
            def inner_action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                nonlocal ran
                ran = True

            return scheduler.schedule(inner_action)

        scheduler.schedule(action)

        assert ran is True

    def test_trampoline_schedule_nested_order(self) -> None:
        scheduler = TrampolineScheduler()
        tests: list[int] = []

        def outer(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            def action1(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                tests.append(1)

                def action2(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                    tests.append(2)

                TrampolineScheduler().schedule(action2)

            TrampolineScheduler().schedule(action1)

            def action3(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                tests.append(3)

            scheduler3 = TrampolineScheduler()
            scheduler3.schedule(action3)

        scheduler.ensure_trampoline(outer)

        assert tests == [1, 2, 3]

    def test_trampoline_ensuretrampoline(self) -> None:
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(
            scheduer: abc.SchedulerBase, state: Any = None
        ) -> abc.DisposableBase:
            def action1(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                nonlocal ran1
                ran1 = True

            scheduler.schedule(action1)

            def action2(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                nonlocal ran2
                ran2 = True

            return scheduler.schedule(action2)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is True

    def test_trampoline_ensuretrampoline_nested(self) -> None:
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(
            scheduler: abc.SchedulerBase, state: Any
        ) -> abc.DisposableBase | None:
            assert isinstance(scheduler, TrampolineScheduler)

            def inner_action1(scheduler: abc.SchedulerBase, state: Any) -> None:
                nonlocal ran1
                ran1 = True

            scheduler.ensure_trampoline(inner_action1)

            def inner_action2(scheduler: abc.SchedulerBase, state: Any) -> None:
                nonlocal ran2
                ran2 = True

            return scheduler.ensure_trampoline(inner_action2)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is True

    def test_trampoline_ensuretrampoline_and_cancel(self) -> None:
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(
            scheduler: abc.SchedulerBase, state: Any
        ) -> abc.DisposableBase:
            def inner_action1(scheduler: abc.SchedulerBase, state: Any) -> None:
                nonlocal ran1
                ran1 = True

                def inner_action2(scheduler: abc.SchedulerBase, state: Any) -> None:
                    nonlocal ran2
                    ran2 = True

                d = scheduler.schedule(inner_action2)
                d.dispose()

            return scheduler.schedule(inner_action1)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is False

    def test_trampoline_ensuretrampoline_and_canceltimed(self) -> None:
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(
            scheduler: abc.SchedulerBase, state: Any
        ) -> abc.DisposableBase:
            def inner_action1(scheduler: abc.SchedulerBase, state: Any) -> None:
                nonlocal ran1
                ran1 = True

                def inner_action2(scheduler: abc.SchedulerBase, state: Any) -> None:
                    nonlocal ran2
                    ran2 = True

                t = scheduler.now + timedelta(seconds=0.5)
                d = scheduler.schedule_absolute(t, inner_action2)
                d.dispose()

            return scheduler.schedule(inner_action1)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is False
