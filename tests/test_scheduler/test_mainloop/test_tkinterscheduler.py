import os
import sys
import unittest
from datetime import datetime, timedelta
from time import sleep
from typing import Any

import pytest

from reactivex import abc
from reactivex.internal.basic import default_now
from reactivex.scheduler.mainloop import TkinterScheduler

# Skip entire module on PyPy due to Tkinter interpreter/finalizer issues.
# On macOS: "Tcl_AsyncDelete: async handler deleted by the wrong thread".
# On Linux: PyPy's _tkinter app __del__ calls threading.notify_all during
# interpreter shutdown, which aborts the xdist worker and fails whichever
# test it was running.
if hasattr(sys, "pypy_version_info"):
    pytest.skip("Tkinter tests are incompatible with PyPy", allow_module_level=True)

tkinter: Any = pytest.importorskip("tkinter")

root: Any = None
try:
    root = tkinter.Tk()
    root.withdraw()  # Don't actually draw anything
    display = True
except Exception:
    display = False

CI = os.getenv("CI") is not None


@pytest.mark.skipif("display == False")
class TestTkinterScheduler(unittest.TestCase):
    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_tkinter_schedule_now(self) -> None:
        scheduler = TkinterScheduler(root)
        res = scheduler.now - default_now()
        assert abs(res) <= timedelta(milliseconds=1)

    @pytest.mark.skipif(CI, reason="Flaky test in GitHub Actions")
    def test_tkinter_schedule_now_units(self) -> None:
        scheduler = TkinterScheduler(root)
        diff = scheduler.now
        sleep(1.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=1000) < diff < timedelta(milliseconds=1300)

    def test_tkinter_schedule_action(self) -> None:
        scheduler = TkinterScheduler(root)
        ran = False

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        def done() -> None:
            assert ran is True
            root.quit()

        root.after_idle(done)
        root.mainloop()

    def test_tkinter_schedule_action_due(self) -> None:
        scheduler = TkinterScheduler(root)
        starttime = default_now()
        endtime: datetime | None = None

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(0.2, action)

        def done() -> None:
            root.quit()
            assert endtime is not None
            diff = endtime - starttime
            assert diff > timedelta(milliseconds=180)

        root.after(300, done)
        root.mainloop()

    def test_tkinter_schedule_action_cancel(self) -> None:
        ran = False
        scheduler = TkinterScheduler(root)

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        def done() -> None:
            root.quit()
            assert ran is False

        root.after(300, done)
        root.mainloop()

    def test_tkinter_schedule_action_periodic(self) -> None:
        scheduler = TkinterScheduler(root)
        period = 0.050
        counter = 3

        def action(state: int | None) -> int | None:
            nonlocal counter
            if state:
                counter -= 1
                return state - 1
            return None

        scheduler.schedule_periodic(period, action, counter)

        def done() -> None:
            root.quit()
            assert counter == 0

        root.after(300, done)
        root.mainloop()
