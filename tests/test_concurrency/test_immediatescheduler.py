import unittest

from datetime import timedelta

from rx.disposable import Disposable
from rx.concurrency import ImmediateScheduler
from rx.internal.basic import default_now
from rx.internal.constants import DELTA_ZERO


class TestImmediateScheduler(unittest.TestCase):

    def test_immediate_now(self):
        scheduler = ImmediateScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_immediate_scheduleaction(self):
        scheduler = ImmediateScheduler()
        ran = False

        def action(scheduler, state=None):
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        assert ran

    def test_immediate_schedule_action_error(self):
        scheduler = ImmediateScheduler()

        class MyException(Exception):
            pass

        def action(scheduler, state=None):
            raise MyException()

        try:
            return scheduler.schedule(action)
        except MyException:
            assert True

    def test_immediate_simple1(self):
        scheduler = ImmediateScheduler()
        xx = 0

        def action(scheduler, state=None):
            nonlocal xx
            xx = state
            return Disposable()

        scheduler.schedule(action, 42)
        assert xx == 42

    def test_immediate_simple2(self):
        scheduler = ImmediateScheduler()
        xx = 0

        def action(scheduler, state=None):
            nonlocal xx
            xx = state
            return Disposable()

        scheduler.schedule_absolute(default_now(), action, 42)
        assert xx == 42

    def test_immediate_simple3(self):
        scheduler = ImmediateScheduler()
        xx = 0

        def action(scheduler, state=None):
            nonlocal xx
            xx = state
            return Disposable()

        scheduler.schedule_relative(DELTA_ZERO, action, 42)
        assert xx == 42

    def test_immediate_recursive1(self):
        scheduler = ImmediateScheduler()
        xx = 0
        yy = 0

        def action(scheduler, state=None):
            nonlocal xx
            xx = state

            def inner_action(scheduler, state=None):
                nonlocal yy
                yy = state
                return Disposable()

            return scheduler.schedule(inner_action, 43)

        scheduler.schedule(action, 42)
        assert xx == 42
        assert yy == 43

    def test_immediate_recursive2(self):
        scheduler = ImmediateScheduler()
        xx = 0
        yy = 0

        def action(scheduler, state=None):
            nonlocal xx
            xx = state

            def inner_action(scheduler, state=None):
                nonlocal yy
                yy = state
                return Disposable()

            return scheduler.schedule_absolute(default_now(), inner_action, 43)

        scheduler.schedule_absolute(default_now(), action, 42)

        assert xx == 42
        assert yy == 43

    def test_immediate_recursive3(self):
        scheduler = ImmediateScheduler()
        xx = 0
        yy = 0

        def action(scheduler, state=None):
            nonlocal xx
            xx = state

            def inner_action(scheduler, state):
                nonlocal yy
                yy = state
                return Disposable()

            return scheduler.schedule_relative(DELTA_ZERO, inner_action, 43)

        scheduler.schedule_relative(DELTA_ZERO, action, 42)

        assert xx == 42
        assert yy == 43
