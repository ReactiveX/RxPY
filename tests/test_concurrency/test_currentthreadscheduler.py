import unittest
from datetime import datetime, timedelta

from rx.concurrency import CurrentThreadScheduler


class TestCurrentThreadScheduler(unittest.TestCase):

    def test_currentthread_now(self):
        scheduler = CurrentThreadScheduler()
        res = scheduler.now - datetime.utcnow()
        assert res < timedelta(milliseconds=1000)

    def test_currentthread_scheduleaction(self):
        scheduler = CurrentThreadScheduler()
        ran = [False]

        def action(scheduler, state=None):
            ran[0] = True

        scheduler.schedule(action)
        assert ran[0] is True

    def test_currentthread_scheduleactionerror(self):
        scheduler = CurrentThreadScheduler()

        class MyException(Exception):
            pass

        def action(scheduler, state=None):
            raise MyException()

        try:
            return scheduler.schedule(action)
        except MyException:
            assert True

    def test_currentthread_scheduleactionnested(self):
        scheduler = CurrentThreadScheduler()
        ran = [False]

        def action(scheduler, state=None):
            def inner_action(scheduler, state=None):
                ran[0] = True

            return scheduler.schedule(inner_action)
        scheduler.schedule(action)

        assert ran[0] == True

    def test_currentthread_ensuretrampoline(self):
        scheduler = CurrentThreadScheduler()
        ran1, ran2 = [False], [False]

        def outer_action(scheduer, state=None):
            def action1(scheduler, state=None):
                ran1[0] = True

            scheduler.schedule(action1)

            def action2(scheduler, state=None):
                ran2[0] = True

            return scheduler.schedule(action2)

        scheduler.ensure_trampoline(outer_action)
        assert ran1[0] == True
        assert ran2[0] == True

    def test_currentthread_ensuretrampoline_nested(self):
        scheduler = CurrentThreadScheduler()
        ran1, ran2 = [False], [False]

        def outer_action(scheduler, state):
            def inner_action1(scheduler, state):
                ran1[0] = True

            scheduler.ensure_trampoline(inner_action1)

            def inner_action2(scheduler, state):
                ran2[0] = True

            return scheduler.ensure_trampoline(inner_action2)

        scheduler.ensure_trampoline(outer_action)
        assert ran1[0] == True
        assert ran2[0] == True

    def test_currentthread_ensuretrampoline_and_cancel(self):
        scheduler = CurrentThreadScheduler()
        ran1, ran2 = [False], [False]

        def outer_action(scheduler, state):
            def inner_action1(scheduler, state):
                ran1[0] = True

                def inner_action2(scheduler, state):
                    ran2[0] = True

                d = scheduler.schedule(inner_action2)
                d.dispose()

            return scheduler.schedule(inner_action1)

        scheduler.ensure_trampoline(outer_action)
        assert ran1[0] == True
        assert ran2[0] == False

    def test_currentthread_ensuretrampoline_and_canceltimed(self):
        scheduler = CurrentThreadScheduler()
        ran1, ran2 = [False], [False]

        def outer_action(scheduler, state):
            def inner_action1(scheduler, state):
                ran1[0] = True

                def inner_action2(scheduler, state):
                    ran2[0] = True

                d = scheduler.schedule_relative(timedelta(milliseconds=500), inner_action2)
                d.dispose()

            return scheduler.schedule(inner_action1)

        scheduler.ensure_trampoline(outer_action)
        assert ran1[0] == True
        assert ran2[0] == False
