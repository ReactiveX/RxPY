import pytest
import unittest

import threading
from datetime import timedelta
from time import sleep

from rx.disposable import Disposable
from rx.scheduler import ImmediateScheduler
from rx.internal.basic import default_now
from rx.internal.constants import DELTA_ZERO
from rx.internal.exceptions import WouldBlockException


class TestImmediateScheduler(unittest.TestCase):

    def test_immediate_singleton(self):
        scheduler = [
            ImmediateScheduler(),
            ImmediateScheduler.singleton()
        ]
        assert scheduler[0] is scheduler[1]

        gate = [threading.Semaphore(0), threading.Semaphore(0)]
        scheduler = [None, None]

        def run(idx):
            scheduler[idx] = ImmediateScheduler()
            gate[idx].release()

        for idx in (0, 1):
            threading.Thread(target=run, args=(idx,)).start()
            gate[idx].acquire()

        assert scheduler[0] is not None
        assert scheduler[1] is not None
        assert scheduler[0] is scheduler[1]

    def test_immediate_extend(self):
        class MyScheduler(ImmediateScheduler):
            pass

        scheduler = [
            MyScheduler(),
            MyScheduler.singleton(),
            ImmediateScheduler.singleton(),
        ]
        assert scheduler[0] is scheduler[1]
        assert scheduler[0] is not scheduler[2]

    def test_immediate_now(self):
        scheduler = ImmediateScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_immediate_now_units(self):
        scheduler = ImmediateScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

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

        with pytest.raises(MyException):
            return scheduler.schedule(action)

    def test_immediate_schedule_action_due_error(self):
        scheduler = ImmediateScheduler()
        ran = False

        def action(scheduler, state=None):
            nonlocal ran
            ran = True

        with pytest.raises(WouldBlockException):
            scheduler.schedule_relative(0.1, action)

        assert ran is False

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
