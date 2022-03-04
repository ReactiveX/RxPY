import os
import threading
import unittest
from datetime import timedelta
from time import sleep

import pytest

from reactivex.internal import DisposedException
from reactivex.internal.basic import default_now
from reactivex.scheduler import EventLoopScheduler

CI = os.getenv("CI") is not None


class TestEventLoopScheduler(unittest.TestCase):
    def test_event_loop_now(self):
        scheduler = EventLoopScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=5)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_event_loop_now_units(self):
        scheduler = EventLoopScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_event_loop_schedule_action(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        ran = False
        gate = threading.Semaphore(0)

        def action(scheduler, state):
            nonlocal ran
            ran = True
            gate.release()

        scheduler.schedule(action)
        gate.acquire()
        assert ran is True
        # There is no guarantee that the event-loop thread ends before the
        # test thread is re-scheduled, give it some time to always run.
        sleep(0.1)
        assert scheduler._has_thread() is False

    def test_event_loop_different_thread(self):
        thread_id = None
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)

        def action(scheduler, state):
            nonlocal thread_id
            thread_id = threading.current_thread().ident
            gate.release()

        scheduler.schedule(action)
        gate.acquire()
        # There is no guarantee that the event-loop thread ends before the
        # test thread is re-scheduled, give it some time to always run.
        sleep(0.1)
        assert thread_id != threading.current_thread().ident
        assert scheduler._has_thread() is False

    def test_event_loop_schedule_ordered_actions(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)
        result = []

        scheduler.schedule(lambda s, t: result.append(1))

        def action(scheduler, state):
            result.append(2)
            gate.release()

        scheduler.schedule(action)
        gate.acquire()
        # There is no guarantee that the event-loop thread ends before the
        # test thread is re-scheduled, give it some time to always run.
        sleep(0.1)
        assert result == [1, 2]
        assert scheduler._has_thread() is False

    def test_event_loop_schedule_ordered_actions_due(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)
        result = []

        def action(scheduler, state):
            result.append(3)
            gate.release()

        scheduler.schedule_relative(0.4, action)
        scheduler.schedule_relative(0.2, lambda s, t: result.append(2))
        scheduler.schedule(lambda s, t: result.append(1))

        gate.acquire()
        # There is no guarantee that the event-loop thread ends before the
        # test thread is re-scheduled, give it some time to always run.
        sleep(0.1)
        assert result == [1, 2, 3]
        assert scheduler._has_thread() is False

    def test_event_loop_schedule_ordered_actions_due_mixed(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)
        result = []

        def action(scheduler, state):
            result.append(1)
            scheduler.schedule_relative(0.2, action3)
            scheduler.schedule(action2)

        def action2(scheduler, state):
            result.append(2)

        def action3(scheduler, state):
            result.append(3)
            gate.release()

        scheduler.schedule(action)

        gate.acquire()
        # There is no guarantee that the event-loop thread ends before the
        # test thread is re-scheduled, give it some time to always run.
        sleep(0.1)
        assert result == [1, 2, 3]
        assert scheduler._has_thread() is False

    def test_event_loop_schedule_action_relative_due(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()
            gate.release()

        scheduler.schedule_relative(timedelta(milliseconds=200), action)
        gate.acquire()
        # There is no guarantee that the event-loop thread ends before the
        # test thread is re-scheduled, give it some time to always run.
        sleep(0.1)
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)
        assert scheduler._has_thread() is False

    def test_event_loop_schedule_action_absolute_due(self):
        scheduler = EventLoopScheduler(exit_if_empty=True)
        gate = threading.Semaphore(0)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()
            gate.release()

        scheduler.schedule_absolute(scheduler.now, action)
        gate.acquire()
        # There is no guarantee that the event-loop thread ends before the
        # test thread is re-scheduled, give it some time to always run.
        sleep(0.1)
        diff = endtime - starttime
        assert diff < timedelta(milliseconds=180)
        assert scheduler._has_thread() is False

    def test_eventloop_schedule_action_periodic(self):
        scheduler = EventLoopScheduler(exit_if_empty=False)
        gate = threading.Semaphore(0)
        period = 0.05
        counter = 3

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            if counter == 0:
                gate.release()

        disp = scheduler.schedule_periodic(period, action, counter)

        def dispose(scheduler, state):
            disp.dispose()
            gate.release()

        gate.acquire()
        assert counter == 0
        assert scheduler._has_thread() is True
        scheduler.schedule(dispose)

        gate.acquire()
        assert scheduler._has_thread() is True
        sleep(period)
        scheduler.dispose()
        sleep(period)
        assert scheduler._has_thread() is False

    def test_eventloop_schedule_dispose(self):
        scheduler = EventLoopScheduler(exit_if_empty=False)

        scheduler.dispose()

        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        with pytest.raises(DisposedException):
            scheduler.schedule(action)

        assert ran is False
        assert scheduler._has_thread() is False

    def test_eventloop_schedule_absolute_dispose(self):
        scheduler = EventLoopScheduler(exit_if_empty=False)

        scheduler.dispose()

        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        with pytest.raises(DisposedException):
            scheduler.schedule_absolute(scheduler.now, action)

        assert ran is False
        assert scheduler._has_thread() is False

    def test_eventloop_schedule_periodic_dispose_error(self):
        scheduler = EventLoopScheduler(exit_if_empty=False)

        scheduler.dispose()

        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        with pytest.raises(DisposedException):
            scheduler.schedule_periodic(0.1, action)

        assert ran is False
        assert scheduler._has_thread() is False
