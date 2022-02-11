import pytest
import unittest

from datetime import timedelta
from time import sleep

from rx.scheduler import TrampolineScheduler
from rx.internal.basic import default_now


class TestTrampolineScheduler(unittest.TestCase):
    def test_trampoline_now(self):
        scheduler = TrampolineScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=2)  # NOTE: may take 1 ms in CI

    def test_trampoline_now_units(self):
        scheduler = TrampolineScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_trampoline_schedule(self):
        scheduler = TrampolineScheduler()
        ran = False

        def action(scheduler, state=None):
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        assert ran is True

    def test_trampoline_schedule_block(self):
        scheduler = TrampolineScheduler()
        ran = False

        def action(scheduler, state=None):
            nonlocal ran
            ran = True

        t = scheduler.now
        scheduler.schedule_relative(0.2, action)
        t = scheduler.now - t
        assert ran is True
        assert t >= timedelta(seconds=0.2)

    def test_trampoline_schedule_error(self):
        scheduler = TrampolineScheduler()

        class MyException(Exception):
            pass

        def action(scheduler, state=None):
            raise MyException()

        with pytest.raises(MyException):
            scheduler.schedule(action)

    def test_trampoline_schedule_nested(self):
        scheduler = TrampolineScheduler()
        ran = False

        def action(scheduler, state=None):
            def inner_action(scheduler, state=None):
                nonlocal ran
                ran = True

            return scheduler.schedule(inner_action)

        scheduler.schedule(action)

        assert ran is True

    def test_trampoline_schedule_nested_order(self):
        scheduler = TrampolineScheduler()
        tests = []

        def outer(scheduler, state=None):
            def action1(scheduler, state=None):
                tests.append(1)

                def action2(scheduler, state=None):
                    tests.append(2)

                TrampolineScheduler().schedule(action2)

            TrampolineScheduler().schedule(action1)

            def action3(scheduler, state=None):
                tests.append(3)

            scheduler3 = TrampolineScheduler()
            scheduler3.schedule(action3)

        scheduler.ensure_trampoline(outer)

        assert tests == [1, 2, 3]

    def test_trampoline_ensuretrampoline(self):
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(scheduer, state=None):
            def action1(scheduler, state=None):
                nonlocal ran1
                ran1 = True

            scheduler.schedule(action1)

            def action2(scheduler, state=None):
                nonlocal ran2
                ran2 = True

            return scheduler.schedule(action2)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is True

    def test_trampoline_ensuretrampoline_nested(self):
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(scheduler, state):
            def inner_action1(scheduler, state):
                nonlocal ran1
                ran1 = True

            scheduler.ensure_trampoline(inner_action1)

            def inner_action2(scheduler, state):
                nonlocal ran2
                ran2 = True

            return scheduler.ensure_trampoline(inner_action2)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is True

    def test_trampoline_ensuretrampoline_and_cancel(self):
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(scheduler, state):
            def inner_action1(scheduler, state):
                nonlocal ran1
                ran1 = True

                def inner_action2(scheduler, state):
                    nonlocal ran2
                    ran2 = True

                d = scheduler.schedule(inner_action2)
                d.dispose()

            return scheduler.schedule(inner_action1)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is False

    def test_trampoline_ensuretrampoline_and_canceltimed(self):
        scheduler = TrampolineScheduler()
        ran1, ran2 = False, False

        def outer_action(scheduler, state):
            def inner_action1(scheduler, state):
                nonlocal ran1
                ran1 = True

                def inner_action2(scheduler, state):
                    nonlocal ran2
                    ran2 = True

                t = scheduler.now + timedelta(seconds=0.5)
                d = scheduler.schedule_absolute(t, inner_action2)
                d.dispose()

            return scheduler.schedule(inner_action1)

        scheduler.ensure_trampoline(outer_action)
        assert ran1 is True
        assert ran2 is False
