import unittest
from unittest import SkipTest

from datetime import datetime, timedelta
from time import sleep
import threading
from rx.concurrency import EventLoopScheduler


class TestEventLoopScheduler(unittest.TestCase):
    def test_event_loop_now(self):
        scheduler = EventLoopScheduler()
        res = scheduler.now - datetime.utcnow()
        assert res < timedelta(microseconds=1000)

    def test_event_loop_schedule_action(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        ran = [False]
        gate = threading.Semaphore(0)

        def action(scheduler, state):
            gate.release()
            ran[0] = True

        scheduler.schedule(action)
        gate.acquire()
        assert (ran[0] is True)

    def test_event_loop_different_thread(self):
        thread_id = [None]
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)

        def action(scheduler, state):
            gate.release()
            thread_id[0] = threading.current_thread().ident

        scheduler.schedule(action)
        gate.acquire()
        assert (thread_id[0] != threading.current_thread().ident)

    def test_event_loop_schedule_ordered_actions(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)
        result = []

        scheduler.schedule(lambda s, t: result.append(1))

        def action(scheduler, state):
            gate.release()
            result.append(2)

        scheduler.schedule(action)
        gate.acquire()
        assert (result == [1, 2])

    def test_event_loop_schedule_action_due(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)
        starttime = datetime.utcnow()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.utcnow()
            print("release")
            gate.release()

        scheduler.schedule_relative(timedelta(milliseconds=200), action)

        gate.acquire()
        diff = endtime[0]-starttime
        assert(diff > timedelta(milliseconds=180))

    def test_eventloop_schedule_action_periodic(self):
        scheduler = EventLoopScheduler()
        gate = threading.Semaphore(0)
        period = 50
        counter = [3]

        def action(state):
            if state:
                counter[0] -= 1
                return state - 1
            if counter[0] == 0:
                gate.release()

        scheduler.schedule_periodic(period, action, counter[0])

        def done():
            assert counter[0] == 0

        gate.acquire()
