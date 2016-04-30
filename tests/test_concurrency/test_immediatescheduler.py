import unittest
from datetime import datetime, timedelta

from rx.core import Disposable
from rx.concurrency import ImmediateScheduler


class TestImmediateScheduler(unittest.TestCase):
    def test_immediate_now(self):
        scheduler = ImmediateScheduler()
        res = scheduler.now - datetime.utcnow()
        assert res < timedelta(milliseconds=1000)

    def test_immediate_scheduleaction(self):
        scheduler = ImmediateScheduler()
        ran = [False]

        def action(scheduler, state=None):
            ran[0] = True

        scheduler.schedule(action)
        assert ran[0]

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
        xx = [0]

        def action(scheduler, state=None):
            xx[0] = state
            return Disposable.empty()

        scheduler.schedule(action, 42)
        assert xx[0] == 42

    def test_immediate_simple2(self):
        scheduler = ImmediateScheduler()
        xx = [0]

        def action(scheduler, state=None):
             xx[0] = state
             return Disposable.empty()

        scheduler.schedule_absolute(datetime.utcnow(), action, 42)
        assert xx[0] == 42

    def test_immediate_simple3(self):
        scheduler = ImmediateScheduler()
        xx = [0]

        def action(scheduler, state=None):
             xx[0] = state
             return Disposable.empty()

        scheduler.schedule_relative(timedelta(0), action, 42)
        assert xx[0] == 42

    def test_immediate_recursive1(self):
        scheduler = ImmediateScheduler()
        xx = [0]
        yy = [0]

        def action(scheduler, x=None):
            xx[0] = x

            def inner_action(scheduler, y):
                yy[0] = y
                return Disposable.empty()

            return scheduler.schedule(inner_action, 43)

        scheduler.schedule(action, 42)
        assert xx[0] == 42
        assert yy[0] == 43

    def test_immediate_recursive2(self):
        scheduler = ImmediateScheduler()
        xx = [0]
        yy = [0]

        def action(scheduler, state=None):
            xx[0] = state

            def inner_action(scheduler, state=None):
                yy[0] = state
                return Disposable.empty()

            return scheduler.schedule_absolute(datetime.utcnow(), inner_action, 43)

        scheduler.schedule_absolute(datetime.utcnow(), action, 42)

        assert xx[0] == 42
        assert yy[0] == 43

    def test_immediate_recursive3(self):
        scheduler = ImmediateScheduler()
        xx = [0]
        yy = [0]

        def action(scheduler, state=None):
            xx[0] = state

            def inner_action(scheduler, state):
                yy[0] = state
                return Disposable.empty()

            return scheduler.schedule_relative(timedelta(0), inner_action, 43)

        scheduler.schedule_relative(timedelta(0), action, 42)

        assert xx[0] == 42
        assert yy[0] == 43
