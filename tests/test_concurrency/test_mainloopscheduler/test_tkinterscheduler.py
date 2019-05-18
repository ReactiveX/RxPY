import pytest
import unittest

from datetime import timedelta
from time import sleep

from rx.concurrency.mainloopscheduler import TkinterScheduler
from rx.internal.basic import default_now


tkinter = pytest.importorskip("tkinter")

try:
    root = tkinter.Tcl()
    display = True
except Exception:
    display = False


@pytest.mark.skipif("display == False")
class TestTkinterScheduler(unittest.TestCase):

    def test_tkinter_schedule_now(self):
        scheduler = TkinterScheduler(root)
        res = scheduler.now - default_now()
        assert abs(res) < timedelta(milliseconds=1)

    def test_tkinter_schedule_now_units(self):
        scheduler = TkinterScheduler(root)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_tkinter_schedule_action(self):
        scheduler = TkinterScheduler(root)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)

        def done():
            assert ran is True
            root.quit()

        root.after_idle(done)
        root.mainloop()

    def test_tkinter_schedule_action_due(self):
        scheduler = TkinterScheduler(root)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(0.2, action)

        def done():
            root.quit()
            assert endtime is not None
            diff = endtime - starttime
            assert diff > timedelta(milliseconds=180)

        root.after(300, done)
        root.mainloop()

    def test_tkinter_schedule_action_cancel(self):
        ran = False
        scheduler = TkinterScheduler(root)

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()

        def done():
            root.quit()
            assert ran is False

        root.after(300, done)
        root.mainloop()

    def test_tkinter_schedule_action_periodic(self):
        scheduler = TkinterScheduler(root)
        period = 0.050
        counter = 3

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1

        scheduler.schedule_periodic(period, action, counter)

        def done():
            root.quit()
            assert counter == 0

        root.after(300, done)
        root.mainloop()
