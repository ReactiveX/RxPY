import pytest
import unittest

import threading
from datetime import timedelta

from rx.concurrency import CurrentThreadScheduler
from rx.internal.basic import default_now


class TestCurrentThreadScheduler(unittest.TestCase):

    def test_currentthread_singleton(self):
        scheduler = [CurrentThreadScheduler(), CurrentThreadScheduler()]
        assert scheduler[0] is scheduler[1]

        gate = [threading.Semaphore(0), threading.Semaphore(0)]
        scheduler = [None, None]

        def run(idx):
            scheduler[idx] = CurrentThreadScheduler()
            gate[idx].release()

        for idx in (0, 1):
            threading.Thread(target=run, args=(idx,)).start()
            gate[idx].acquire()

        assert scheduler[0] is not None
        assert scheduler[1] is not None
        assert scheduler[0] is not scheduler[1]

    def test_currentthread_now(self):
        scheduler = CurrentThreadScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_currentthread_schedule(self):
        scheduler = CurrentThreadScheduler()
        ran = False

        def action(scheduler, state=None):
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        assert ran is True

    def test_currentthread_schedule_block(self):
        scheduler = CurrentThreadScheduler()
        ran = False

        def action(scheduler, state=None):
            nonlocal ran
            ran = True

        t = scheduler.now
        scheduler.schedule_relative(0.2, action)
        t = scheduler.now - t
        assert ran is True
        assert t >= timedelta(seconds=0.2)

    def test_currentthread_schedule_error(self):
        scheduler = CurrentThreadScheduler()

        class MyException(Exception):
            pass

        def action(scheduler, state=None):
            raise MyException()

        with pytest.raises(MyException):
            scheduler.schedule(action)

    def test_currentthread_schedule_nested(self):
        scheduler = CurrentThreadScheduler()
        ran = False

        def action(scheduler, state=None):
            def inner_action(scheduler, state=None):
                nonlocal ran
                ran = True

            return scheduler.schedule(inner_action)
        scheduler.schedule(action)

        assert ran is True

    def test_currentthread_ensuretrampoline(self):
        scheduler = CurrentThreadScheduler()
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

    def test_currentthread_ensuretrampoline_nested(self):
        scheduler = CurrentThreadScheduler()
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

    def test_currentthread_ensuretrampoline_and_cancel(self):
        scheduler = CurrentThreadScheduler()
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

    def test_currentthread_ensuretrampoline_and_canceltimed(self):
        scheduler = CurrentThreadScheduler()
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
