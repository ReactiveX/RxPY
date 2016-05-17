import unittest
from datetime import datetime, timedelta

from nose import SkipTest
try:
    import tkinter
except ImportError:
    raise SkipTest("Tkinter not installed")

try:
    root = tkinter.Tk()
except Exception:
    raise SkipTest("No display, skipping")

from rx.concurrency import TkinterScheduler


class TestTkinterScheduler(unittest.TestCase):

    def test_tkinter_schedule_now(self):
        scheduler = TkinterScheduler(root)
        res = scheduler.now - datetime.utcnow()
        assert(res < timedelta(seconds=1))

    def test_tkinter_schedule_action(self):
        scheduler = TkinterScheduler(root)
        ran = [False]

        def action(scheduler, state):
            ran[0] = True
        scheduler.schedule(action)

        def done():
            assert(ran[0] == True)
            root.quit()

        root.after_idle(done)
        root.mainloop()

    def test_tkinter_schedule_action_due(self):
        scheduler = TkinterScheduler(root)
        starttime = datetime.utcnow()
        endtime = [None]

        def action(scheduler, state):
            endtime[0] = datetime.utcnow()

        scheduler.schedule_relative(200, action)

        def done():
            root.quit()
            diff = endtime[0]-starttime
            assert(diff > timedelta(milliseconds=180))

        root.after(300, done)
        root.mainloop()

    def test_tkinter_schedule_action_cancel(self):
        ran = [False]
        scheduler = TkinterScheduler(root)

        def action(scheduler, state):
            ran[0] = True
        d = scheduler.schedule_relative(100, action)
        d.dispose()

        def done():
            root.quit()
            assert(not ran[0])

        root.after(300, done)
        root.mainloop()

    def test_tkinter_schedule_action_periodic(self):
        scheduler = TkinterScheduler(root)
        period = 50
        counter = [3]

        def action(state):
            if state:
                counter[0] -= 1
                return state - 1

        scheduler.schedule_periodic(period, action, counter[0])

        def done():
            root.quit()
            assert counter[0] == 0

        root.after(300, done)
        root.mainloop()
