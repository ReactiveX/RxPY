import threading
import unittest
from datetime import timedelta
from time import sleep

from reactivex.internal.basic import default_now
from reactivex.scheduler import ThreadPoolScheduler

thread_pool_scheduler = ThreadPoolScheduler()


class TestThreadPoolScheduler(unittest.TestCase):
    def test_threadpool_now(self):
        scheduler = ThreadPoolScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=5)

    def test_threadpool_now_units(self):
        scheduler = ThreadPoolScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_schedule_action(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert ident != threading.current_thread().ident
            evt.set()

        nt.schedule(action)
        evt.wait()

    def test_schedule_action_due_relative(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert ident != threading.current_thread().ident
            evt.set()

        nt.schedule_relative(timedelta(milliseconds=200), action)
        evt.wait()

    def test_schedule_action_due_0(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert ident != threading.current_thread().ident
            evt.set()

        nt.schedule_relative(0.1, action)
        evt.wait()

    def test_schedule_action_absolute(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert ident != threading.current_thread().ident
            evt.set()

        nt.schedule_absolute(default_now() + timedelta(milliseconds=100), action)
        evt.wait()

    def test_schedule_action_cancel(self):
        nt = thread_pool_scheduler
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = nt.schedule_relative(0.05, action)
        d.dispose()

        sleep(0.1)
        assert ran is False
