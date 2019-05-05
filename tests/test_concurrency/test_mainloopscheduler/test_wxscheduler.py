from datetime import timedelta
from time import sleep
import unittest
import pytest

from rx.concurrency.mainloopscheduler import WxScheduler
from rx.internal.basic import default_now
from rx.internal.constants import DELTA_ZERO

wx = pytest.importorskip('wx')


class AppExit(wx.Timer):

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app

    def Notify(self):
        self.app.ExitMainLoop()


class TestWxScheduler(unittest.TestCase):

    def test_wx_schedule_now(self):
        scheduler = WxScheduler(wx)
        diff = scheduler.now - default_now()
        assert abs(diff) < timedelta(milliseconds=1)

    def test_wx_schedule_now_units(self):
        scheduler = WxScheduler(wx)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_wx_schedule_action(self):
        app = wx.AppConsole()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        scheduler.schedule(action)
        exit.Start(100, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert ran is True

    def test_wx_schedule_action_relative(self):
        app = wx.AppConsole()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        scheduler.schedule_relative(0.1, action)
        exit.Start(200, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert endtime is not None
        diff = endtime - starttime
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_wx_schedule_action_absolute(self):
        app = wx.AppConsole()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        starttime = default_now()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = default_now()

        due = scheduler.now + timedelta(milliseconds=100)
        scheduler.schedule_absolute(due, action)
        exit.Start(200, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert endtime is not None
        diff = endtime - starttime
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    def test_wx_schedule_action_cancel(self):
        app = wx.AppConsole()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        d = scheduler.schedule_relative(0.1, action)
        d.dispose()
        exit.Start(200, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert ran is False

    def test_wx_schedule_action_periodic(self):
        app = wx.AppConsole()
        exit = AppExit(app)
        scheduler = WxScheduler(wx)
        period = 0.05
        counter = 3

        def action(state):
            nonlocal counter
            if state:
                counter -= 1
                return state - 1

        scheduler.schedule_periodic(period, action, counter)
        exit.Start(500, wx.TIMER_ONE_SHOT)
        app.MainLoop()
        scheduler.cancel_all()

        assert counter == 0
