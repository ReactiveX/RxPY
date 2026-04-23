import unittest
from datetime import timedelta
from typing import Any

from reactivex import abc
from reactivex import typing as rx_typing
from reactivex.scheduler import CatchScheduler, VirtualTimeScheduler


class MyException(Exception):
    pass


class CatchSchedulerTestScheduler(VirtualTimeScheduler):
    def __init__(self, initial_clock: float = 0.0) -> None:
        super().__init__(initial_clock)
        self.exc: Exception | None = None

    @classmethod
    def add(
        cls, absolute: rx_typing.AbsoluteTime, relative: rx_typing.RelativeTime
    ) -> rx_typing.AbsoluteTime:
        return absolute + relative  # type: ignore[operator]

    def _wrap(self, action: abc.ScheduledAction[Any]) -> abc.ScheduledAction[Any]:
        def _action(scheduler: abc.SchedulerBase, state: Any = None) -> abc.DisposableBase | None:
            ret: abc.DisposableBase | None = None
            try:
                ret = action(scheduler, state)
            except MyException as e:
                self.exc = e
            return ret

        return _action

    def schedule_absolute(
        self,
        duetime: rx_typing.AbsoluteTime,
        action: abc.ScheduledAction[Any],
        state: Any = None,
    ) -> abc.DisposableBase:
        action = self._wrap(action)
        return super().schedule_absolute(duetime, action, state=state)


class TestCatchScheduler(unittest.TestCase):
    def test_catch_now(self) -> None:
        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, lambda ex: True)
        diff = scheduler.now - wrapped.now
        assert abs(diff) < timedelta(milliseconds=1)

    def test_catch_now_units(self) -> None:
        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, lambda ex: True)
        diff = scheduler.now
        wrapped.sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_catch_schedule(self) -> None:
        ran = False
        handled = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule(action)
        wrapped.start()
        assert ran is True
        assert handled is False
        assert wrapped.exc is None

    def test_catch_schedule_relative(self) -> None:
        ran = False
        handled = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule_relative(0.1, action)
        wrapped.start()
        assert ran is True
        assert handled is False
        assert wrapped.exc is None

    def test_catch_schedule_absolute(self) -> None:
        ran = False
        handled = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule_absolute(0.1, action)
        wrapped.start()
        assert ran is True
        assert handled is False
        assert wrapped.exc is None

    def test_catch_schedule_error_handled(self) -> None:
        ran = False
        handled = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            raise MyException()

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule(action)
        wrapped.start()
        assert ran is True
        assert handled is True
        assert wrapped.exc is None

    def test_catch_schedule_error_unhandled(self) -> None:
        ran = False
        handled = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            raise MyException()

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return False

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule(action)
        wrapped.start()
        assert ran is True
        assert handled is True
        assert isinstance(wrapped.exc, MyException)

    def test_catch_schedule_nested(self) -> None:
        ran = False
        handled = False

        def inner(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            return None

        def outer(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            return scheduler.schedule(inner)

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule(outer)
        wrapped.start()

        assert ran is True
        assert handled is False
        assert wrapped.exc is None

    def test_catch_schedule_nested_error_handled(self) -> None:
        ran = False
        handled = False

        def inner(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            raise MyException()

        def outer(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            return scheduler.schedule(inner)

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule(outer)
        wrapped.start()
        assert ran is True
        assert handled is True
        assert wrapped.exc is None

    def test_catch_schedule_nested_error_unhandled(self) -> None:
        ran = False
        handled = False

        def inner(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            nonlocal ran
            ran = True
            raise MyException()

        def outer(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase | None:
            return scheduler.schedule(inner)

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return False

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        scheduler.schedule(outer)
        wrapped.start()
        assert ran is True
        assert handled is True
        assert isinstance(wrapped.exc, MyException)

    def test_catch_schedule_periodic(self) -> None:
        period = 0.05
        counter = 3
        handled = False

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                disp.dispose()
            return None

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        disp = scheduler.schedule_periodic(period, action, counter)
        wrapped.start()
        assert counter == 0
        assert handled is False
        assert wrapped.exc is None

    def test_catch_schedule_periodic_error_handled(self) -> None:
        period = 0.05
        counter = 3
        handled = False

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                raise MyException()
            return None

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            disp.dispose()
            return True

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        disp = scheduler.schedule_periodic(period, action, counter)
        wrapped.start()
        assert counter == 0
        assert handled is True
        assert wrapped.exc is None

    def test_catch_schedule_periodic_error_unhandled(self) -> None:
        period = 0.05
        counter = 3
        handled = False

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                raise MyException()
            return None

        def handler(_: Exception) -> bool:
            nonlocal handled
            handled = True
            disp.dispose()
            return False

        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, handler)

        disp = scheduler.schedule_periodic(period, action, counter)
        wrapped.start()
        assert counter == 0
        assert handled is True
        assert isinstance(wrapped.exc, MyException)
