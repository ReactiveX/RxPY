import unittest
from datetime import timedelta

from reactivex.scheduler import CatchScheduler, VirtualTimeScheduler


class MyException(Exception):
    pass


class CatchSchedulerTestScheduler(VirtualTimeScheduler):
    def __init__(self, initial_clock=0.0):
        super().__init__(initial_clock)
        self.exc = None

    def add(self, absolute, relative):
        return absolute + relative

    def _wrap(self, action):
        def _action(scheduler, state=None):
            ret = None
            try:
                ret = action(scheduler, state)
            except MyException as e:
                self.exc = e
            return ret

        return _action

    def schedule_absolute(self, duetime, action, state=None):
        action = self._wrap(action)
        return super().schedule_absolute(duetime, action, state=state)


class TestCatchScheduler(unittest.TestCase):
    def test_catch_now(self):
        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, lambda ex: True)
        diff = scheduler.now - wrapped.now
        assert abs(diff) < timedelta(milliseconds=1)

    def test_catch_now_units(self):
        wrapped = CatchSchedulerTestScheduler()
        scheduler = CatchScheduler(wrapped, lambda ex: True)
        diff = scheduler.now
        wrapped.sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_catch_schedule(self):
        ran = False
        handled = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        def handler(_):
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

    def test_catch_schedule_relative(self):
        ran = False
        handled = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        def handler(_):
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

    def test_catch_schedule_absolute(self):
        ran = False
        handled = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        def handler(_):
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

    def test_catch_schedule_error_handled(self):
        ran = False
        handled = False

        def action(scheduler, state):
            nonlocal ran
            ran = True
            raise MyException()

        def handler(_):
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

    def test_catch_schedule_error_unhandled(self):
        ran = False
        handled = False

        def action(scheduler, state):
            nonlocal ran
            ran = True
            raise MyException()

        def handler(_):
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

    def test_catch_schedule_nested(self):
        ran = False
        handled = False

        def inner(scheduler, state):
            nonlocal ran
            ran = True

        def outer(scheduler, state):
            scheduler.schedule(inner)

        def handler(_):
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

    def test_catch_schedule_nested_error_handled(self):
        ran = False
        handled = False

        def inner(scheduler, state):
            nonlocal ran
            ran = True
            raise MyException()

        def outer(scheduler, state):
            scheduler.schedule(inner)

        def handler(_):
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

    def test_catch_schedule_nested_error_unhandled(self):
        ran = False
        handled = False

        def inner(scheduler, state):
            nonlocal ran
            ran = True
            raise MyException()

        def outer(scheduler, state):
            scheduler.schedule(inner)

        def handler(_):
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

    def test_catch_schedule_periodic(self):
        period = 0.05
        counter = 3
        handled = False

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                disp.dispose()

        def handler(_):
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

    def test_catch_schedule_periodic_error_handled(self):
        period = 0.05
        counter = 3
        handled = False

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                raise MyException()

        def handler(_):
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

    def test_catch_schedule_periodic_error_unhandled(self):
        period = 0.05
        counter = 3
        handled = False

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                raise MyException()

        def handler(_):
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
