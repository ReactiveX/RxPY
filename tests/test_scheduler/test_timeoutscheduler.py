import os
import subprocess
import sys
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
        before = len(scheduler._queue)
        disposables = []

        def action(scheduler, state):
            pass

        for _ in range(200):
            disposables.append(
                scheduler.schedule_relative(timedelta(seconds=60), action)
            )

        assert len(scheduler._queue) - before == 200

        for d in disposables:
            d.dispose()

        assert len(scheduler._queue) <= before

    def test_timeout_cancel_out_of_order_keeps_queue_bounded(self):
        """Cancelling from the back evicts lazily, but must not pile up."""
        scheduler = TimeoutScheduler()
        before = len(scheduler._queue)
        disposables = []

        def action(scheduler, state):
            pass

        for _ in range(200):
            disposables.append(
                scheduler.schedule_relative(timedelta(seconds=60), action)
            )

        for d in reversed(disposables):
            d.dispose()

        assert len(scheduler._queue) - before <= 32

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

    def test_timeout_blocking_handlers_do_not_starve_later_timers(self):
        """The dispatch pool grows; it must not queue behind busy workers."""
        scheduler = TimeoutScheduler()
        gate = threading.Event()
        started = threading.Semaphore(0)
        blockers = 40

        def block(scheduler, state):
            started.release()
            gate.wait(30)

        try:
            for _ in range(blockers):
                scheduler.schedule_relative(timedelta(milliseconds=50), block)

            for _ in range(blockers):
                assert started.acquire(timeout=5) is True

            fired = threading.Event()
            scheduler.schedule_relative(
                timedelta(milliseconds=50), lambda sc, st: fired.set()
            )
            assert fired.wait(5) is True
        finally:
            gate.set()

    def test_timeout_reentrant_dispose_does_not_deadlock(self):
        """Disposal runs user code, which may cancel a nested timer."""
        scheduler = TimeoutScheduler()
        ran = threading.Event()

        def action(sched, state):
            ran.set()
            # Idiomatic recursive scheduling: the action hands back the
            # disposable for the next iteration.
            return sched.schedule_relative(timedelta(seconds=60), action)

        disposable = scheduler.schedule_relative(timedelta(milliseconds=50), action)
        assert ran.wait(5) is True
        sleep(0.05)

        disposed = threading.Event()
        thread = threading.Thread(
            target=lambda: (disposable.dispose(), disposed.set()), daemon=True
        )
        thread.start()
        assert disposed.wait(5) is True

        # The gate must be free afterwards, too.
        fired = threading.Event()
        scheduler.schedule_relative(
            timedelta(milliseconds=10), lambda sc, st: fired.set()
        )
        assert fired.wait(5) is True

    def test_timeout_far_future_does_not_kill_timer_thread(self):
        """A duetime beyond the platform's time_t must not stop the loop."""
        scheduler = TimeoutScheduler()
        far = scheduler.schedule_relative(timedelta(days=400000), lambda sc, st: None)
        try:
            sleep(0.1)
            fired = threading.Event()
            scheduler.schedule_relative(
                timedelta(milliseconds=50), lambda sc, st: fired.set()
            )
            assert fired.wait(5) is True
        finally:
            far.dispose()

    def test_timeout_action_exception_is_reported(self):
        """Exceptions used to reach threading.excepthook; keep them visible."""
        scheduler = TimeoutScheduler()
        raised = threading.Event()

        def action(sched, state):
            raised.set()
            raise ValueError("boom")

        with self.assertLogs("Rx", level="ERROR") as captured:
            scheduler.schedule_relative(timedelta(milliseconds=50), action)
            assert raised.wait(5) is True
            sleep(0.1)

        assert any("boom" in record for record in captured.output)

        # The worker survives and keeps serving later actions.
        fired = threading.Event()
        scheduler.schedule_relative(
            timedelta(milliseconds=10), lambda sc, st: fired.set()
        )
        assert fired.wait(5) is True

    def test_timeout_running_action_does_not_delay_exit(self):
        """Workers are daemons: a running action must not delay shutdown."""
        code = (
            "import time\n"
            "from reactivex.scheduler import TimeoutScheduler\n"
            "TimeoutScheduler.singleton().schedule_relative("
            "0.05, lambda sc, st: time.sleep(30))\n"
            "time.sleep(0.3)\n"
        )
        started = default_now()
        subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            timeout=20,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        )
        assert (default_now() - started).total_seconds() < 15

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
        before_queue = len(scheduler._queue)
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
        assert len(scheduler._queue) <= before_queue
