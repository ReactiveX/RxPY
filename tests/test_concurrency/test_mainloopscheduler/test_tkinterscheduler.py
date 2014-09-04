import unittest
from datetime import datetime, timedelta

from nose import SkipTest
try:
    import tkinter
except ImportError:
    raise SkipTest("Tkinter not installed")

from rx.concurrency import TkinterScheduler

class TkinterScheduler(unittest.TestCase):

    def test_tkinter_schedule_now(self):
        root = tkinter.Tk()

        scheduler = TkinterScheduler(root)
        res = datetime.fromtimestamp(scheduler.now()) - datetime.utcnow()
        assert(res < timedelta(seconds=1))

    # def test_tkinter_schedule_action(self):
    #     loop = ioloop.IOLoop.instance()

    #     scheduler = TkinterScheduler(loop)
    #     ran = [False]

    #     def action(scheduler, state):
    #         ran[0] = True
    #     scheduler.schedule(action)

    #     def done():
    #         assert(ran[0] == True)
    #         loop.stop()
    #     loop.call_later(0.1, done)

    #     loop.start()

    # def test_tkinter_schedule_action_due(self):
    #     loop = ioloop.IOLoop.instance()

    #     scheduler = TkinterScheduler(loop)
    #     starttime = loop.time()
    #     endtime = [None]

    #     def action(scheduler, state):
    #         endtime[0] = loop.time()

    #     scheduler.schedule_relative(0.2, action)

    #     def done():
    #         diff = endtime[0]-starttime
    #         assert(diff > 0.18)
    #         loop.stop()
    #     loop.call_later(0.3, done)

    #     loop.start()

    # def test_tkinter_schedule_action_cancel(self):
    #     loop = ioloop.IOLoop.instance()

    #     ran = [False]
    #     scheduler = TkinterScheduler(loop)

    #     def action(scheduler, state):
    #         ran[0] = True
    #     d = scheduler.schedule_relative(0.01, action)
    #     d.dispose()

    #     def done():
    #         assert(not ran[0])
    #         loop.stop()
    #     loop.call_later(0.1, done)

    #     loop.start()