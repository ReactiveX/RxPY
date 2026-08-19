import os
import threading
import unittest
from datetime import timedelta
from time import sleep

import pytest

import reactivex
from reactivex import operators as ops
from reactivex.internal.basic import default_now
from reactivex.scheduler import TimeoutScheduler

CI = os.getenv("CI") is not None


class TestTimeoutScheduler(unittest.TestCase):
    def test_timeout_singleton(self):
        scheduler = [TimeoutScheduler(), TimeoutScheduler.singleton()]
        assert scheduler[0] is scheduler[1]

        gate = [threading.Semaphore(0), threading.Semaphore(0)]
        scheduler = [None, None]

        def run(idx):
            scheduler[idx] = TimeoutScheduler()
            gate[idx].release()

        for idx in (0, 1):
            threading.Thread(target=run, args=(idx,)).start()
            gate[idx].acquire()

        assert scheduler[0] is not None
        assert scheduler[1] is not None
        assert scheduler[0] is scheduler[1]

    def test_timeout_extend(self):
        class MyScheduler(TimeoutScheduler):
            pass

        scheduler = [
            MyScheduler(),
            MyScheduler.singleton(),
            TimeoutScheduler.singleton(),
        ]
        assert scheduler[0] is scheduler[1]
        assert scheduler[0] is not scheduler[2]

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_timeout_now(self):
        scheduler = TimeoutScheduler()
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_timeout_now_units(self):
        scheduler = TimeoutScheduler()
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_timeout_schedule_action(self):
        scheduler = TimeoutScheduler()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        sleep(0.1)
        assert ran is True

    def test_timeout_schedule_action_due(self):
        scheduler = TimeoutScheduler()
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(timedelta(milliseconds=200), action)

        sleep(0.4)
        assert endtime is not None
        diff = endtime - starttime
        assert diff > timedelta(milliseconds=180)

    def test_timeout_schedule_action_cancel(self):
        ran = False
        scheduler = TimeoutScheduler()

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(timedelta(milliseconds=300), action)
        d.dispose()

        sleep(0.1)
        assert ran is False

    def test_timeout_cancel_evicts_queue(self):
        scheduler = TimeoutScheduler()
        disposables = []

        def action(scheduler, state):
            pass

        for _ in range(200):
            disposables.append(
                scheduler.schedule_relative(timedelta(seconds=60), action)
            )

        assert len(scheduler._queue) == 200

        for d in disposables:
            d.dispose()

        assert len(scheduler._queue) == 0

    def test_timeout_nested_blocking_handler_does_not_deadlock(self):
        """User/fallback work runs on the pool, not the timer thread."""
        sched = TimeoutScheduler.singleton()
        done = threading.Event()
        nested_error = []

        def on_err(e):
            try:
                reactivex.never().pipe(ops.timeout(0.2, scheduler=sched)).run()
            except Exception as ex:
                nested_error.append(ex)
            done.set()

        reactivex.never().pipe(ops.timeout(0.2, scheduler=sched)).subscribe(
            on_error=on_err
        )

        assert done.wait(5) is True
        assert nested_error
        assert "Timeout" in str(nested_error[0])

    def test_timeout_short_timer_not_blocked_by_long(self):
        scheduler = TimeoutScheduler()
        fired_at = {}
        start = default_now()
        done = threading.Event()

        def make_action(name):
            def action(scheduler, state):
                fired_at[name] = default_now()
                if len(fired_at) == 3:
                    done.set()

            return action

        scheduler.schedule_relative(timedelta(milliseconds=500), make_action("long-a"))
        scheduler.schedule_relative(timedelta(milliseconds=500), make_action("long-b"))
        scheduler.schedule_relative(timedelta(milliseconds=100), make_action("short"))

        assert done.wait(2) is True
        assert "short" in fired_at
        short_delay = (fired_at["short"] - start).total_seconds()
        assert short_delay < 0.4

    def test_timeout_many_pending_does_not_spawn_thread_per_timer(self):
        scheduler = TimeoutScheduler()
        before = threading.active_count()
        disposables = []

        def action(scheduler, state):
            pass

        for _ in range(200):
            disposables.append(
                scheduler.schedule_relative(timedelta(seconds=30), action)
            )

        sleep(0.05)
        after = threading.active_count()
        growth = after - before

        for d in disposables:
            d.dispose()

        # One timer thread plus a small pool — not one thread per pending item.
        assert growth < 50
        assert len(scheduler._queue) == 0
