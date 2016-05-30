import time
import unittest

from datetime import datetime, timedelta
import threading
from rx.concurrency import ThreadPoolScheduler, thread_pool_scheduler


class TestThreadPoolScheduler(unittest.TestCase):
    def test_threadpool_now(self):
        scheduler = ThreadPoolScheduler()
        res = scheduler.now - datetime.utcnow()
        assert(res < timedelta(microseconds=1000))

    def test_schedule_action(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert(ident != threading.current_thread().ident)
            evt.set()

        nt.schedule(action)
        evt.wait()

    def test_schedule_action_due_relative(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert(ident != threading.current_thread().ident)
            evt.set()

        nt.schedule_relative(timedelta(milliseconds=200), action)
        evt.wait()

    def test_schedule_action_due_0(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert(ident != threading.current_thread().ident)
            evt.set()

        nt.schedule_relative(200, action)
        evt.wait()

    def test_schedule_action_absolute(self):
        ident = threading.current_thread().ident
        evt = threading.Event()
        nt = thread_pool_scheduler

        def action(scheduler, state):
            assert(ident != threading.current_thread().ident)
            evt.set()

        nt.schedule_absolute(datetime.utcnow()+timedelta(milliseconds=100), action)
        evt.wait()

    def test_schedule_action_cancel(self):
        nt = thread_pool_scheduler
        set = []

        def action(scheduler, state):
            set.append(True)
            assert(False)

        d = nt.schedule_relative(100, action)
        d.dispose()

        time.sleep(0.1)
        assert(not len(set))
